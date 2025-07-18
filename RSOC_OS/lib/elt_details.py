# ==============================================================================
# RSOC_OS — Operational Support Suite for the Flex Regional Security Operations Center
#
# Copyright (c) 2025 Morgan Small
# All rights reserved.
#
# Permission is granted to current Flex RSOC personnel to use this software
# solely for official operational support and task automation.
#
# Use of this suite is implicitly permitted only while Morgan Small is employed
# within the Flex RSOC organizational structure. Should he be demoted,
# terminated, or otherwise removed from the RSOC hierarchy in any way,
# this implicit permission is revoked. Continued use of RSOC_OS following such
# circumstances is prohibited unless explicitly authorized by the original author.
#
# This program is intended to assist RSOC operators and supervisors in completing
# repetitive daily tasks efficiently and consistently. It is not designed to
# replace human oversight or operator judgment. RSOC personnel are still required
# to provide appropriate input, review outputs, and confirm that all
# generated content is accurate and appropriate for operational use.
#
# Redistribution:
# Redistribution, reproduction, or reuse of this software or any of its components
# outside the Flex RSOC environment is strictly prohibited without explicit,
# written permission from the author, Morgan Small.
#
# Attribution:
# Any derivative works, extensions, or adaptations of this software must
# include clear attribution to the original author, Morgan Small.
#
# External Dependencies:
# This software relies on third-party packages. Compatibility with future versions
# of those libraries is not guaranteed. It is the user's responsibility to maintain
# a stable environment for proper functionality.
#
# Disclaimer of Warranty:
# This software is provided "as is" without warranty of any kind, express or implied.
# In no event shall the author be held liable for any damages or losses arising
# from the use, misuse, or inability to use this software.
#
# Confidentiality:
# Portions of this software may contain proprietary logic or access confidential
# systems and workflows. Users are expected to treat the internal logic, file paths,
# and associated data structures as confidential and not disclose them outside of
# authorized RSOC personnel.
#
# Version Integrity:
# Modifications to this software should be version-controlled and approved by the
# original author. Unauthorized edits or forks may compromise the tool's intended
# functionality and are strongly discouraged.
#
# Contact:
# For support, feedback, or licensing inquiries, contact:
# Morgan Small — morgan.small@flex.com OR jamiesmall0718@gmail.com
# ==============================================================================

import os, json, datetime, tempfile, shutil, traceback
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QLabel, QMessageBox, QScrollArea
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QSize

CONFIG_DIR = "config"
CFG_PATH   = os.path.join(CONFIG_DIR, "elt_details.json")
DAYS_REMIND = 60

# ---------- Path management ----------
def _load_cfg():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR, exist_ok=True)
    if os.path.exists(CFG_PATH):
        with open(CFG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"pptx_path": "", "last_confirmed": "2000-01-01"}

def _save_cfg(cfg):  # type: (dict)->None
    with open(CFG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

def _choose_pptx(parent=None):
    dlg = QFileDialog(parent)
    dlg.setWindowTitle("Locate ELT PowerPoint")
    dlg.setNameFilter("PowerPoint (*.pptx *.ppt)")
    dlg.setFileMode(QFileDialog.ExistingFile)
    return dlg.selectedFiles()[0] if dlg.exec() else None

def _ensure_pptx(parent=None) -> str | None:
    cfg  = _load_cfg()
    raw  = cfg.get("pptx_path", "")
    pptx = os.path.expandvars(raw)

    if not os.path.isfile(pptx):
        sel = _choose_pptx(parent)
        if not sel:
            return None
        home = Path.home()
        cfg["pptx_path"] = sel.replace(str(home), r"%USERPROFILE%")
        cfg["last_confirmed"] = datetime.date.today().isoformat()
        _save_cfg(cfg)
        pptx = sel

    last = datetime.date.fromisoformat(cfg.get("last_confirmed", "2000-01-01"))
    if (datetime.date.today() - last).days >= DAYS_REMIND:
        if QMessageBox.question(
            parent or QWidget(),
            "ELT file check",
            f"ELT deck last confirmed {last:%Y-%m-%d}. Still correct?",
            QMessageBox.Yes | QMessageBox.No
        ) == QMessageBox.No:
            sel = _choose_pptx(parent)
            if sel:
                home = Path.home()
                cfg["pptx_path"] = sel.replace(str(home), r"%USERPROFILE%")
                pptx = sel
        cfg["last_confirmed"] = datetime.date.today().isoformat()
        _save_cfg(cfg)

    return pptx if os.path.isfile(pptx) else None

# ---------- Export slides as PNG ----------
def export_slides_to_pngs(pptx_path: str, temp_dir: str) -> list[str]:
    """Return a list of PNG slide paths (exported as silently as possible)."""
    try:
        import win32com.client
        app = win32com.client.DispatchEx("PowerPoint.Application")
        app.WindowState = 2  # Minimized (ppWindowMinimized = 2)

        pres = app.Presentations.Open(os.path.abspath(pptx_path), WithWindow=False)
        pres.Export(temp_dir, "PNG")
        pres.Close()
        app.Quit()

        return sorted(os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if f.lower().endswith(".png"))

    except Exception as e:
        print("[!] Slide export failed:\n", traceback.format_exc())
        return []

# ---------- Build image preview ----------
def build_png_viewer(png_files: list[str]) -> QWidget:
    scroll = QScrollArea()
    inner = QWidget()
    vbox = QVBoxLayout(inner)
    for png in png_files:
        lbl = QLabel()
        lbl.setPixmap(QPixmap(png))
        lbl.setAlignment(Qt.AlignCenter)
        vbox.addWidget(lbl)
    scroll.setWidget(inner)
    scroll.setWidgetResizable(True)
    return scroll

# ---------- Fallback GUI if preview fails ----------
def _fallback_widget(pptx, msg):
    w = QWidget()
    vb = QVBoxLayout(w)
    lab = QLabel(msg + "\nClick below to open the file.")
    lab.setAlignment(Qt.AlignCenter)
    vb.addWidget(lab)
    btn = QPushButton("Open in PowerPoint")
    btn.clicked.connect(lambda: os.startfile(pptx))
    hb = QHBoxLayout()
    hb.addStretch()
    hb.addWidget(btn)
    hb.addStretch()
    vb.addLayout(hb)
    w.setMinimumSize(QSize(600, 300))
    return w

# ---------- Final widget builder ----------
def get_elt_details_widget(parent=None) -> QWidget:
    pptx = _ensure_pptx(parent)
    if not pptx:
        return QLabel("No ELT PowerPoint selected.")

    tmp_dir = tempfile.mkdtemp(prefix="elt_slides_")
    pngs = export_slides_to_pngs(pptx, tmp_dir)
    if not pngs:
        return _fallback_widget(pptx, "Couldn’t render slides. Open in PowerPoint.")

    w = QWidget()
    vbox = QVBoxLayout(w)
    vbox.addWidget(build_png_viewer(pngs))

    pop = QPushButton("Open in PowerPoint")
    pop.clicked.connect(lambda: os.startfile(pptx))
    hb = QHBoxLayout()
    hb.addStretch()
    hb.addWidget(pop)
    hb.addStretch()
    vbox.addLayout(hb)

    w.destroyed.connect(lambda: shutil.rmtree(tmp_dir, ignore_errors=True))
    w.setMinimumSize(QSize(1000, 700))
    return w
