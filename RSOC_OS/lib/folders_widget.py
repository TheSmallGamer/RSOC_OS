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

from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QPushButton, QScrollArea,
    QStackedLayout, QMessageBox
)
from PySide6.QtCore import Qt
from functools import partial
import os

class FoldersWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.user_base = Path.home() / "Box" / "RSOC"

        self.stacked_layout = QStackedLayout(self)

        # === MAIN FOLDER VIEW ===
        self.main_widget = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        content = QWidget()
        grid = QGridLayout(content)
        grid.setAlignment(Qt.AlignTop)

        self.folder_paths = {
            "BOLO": self.user_base / "BOLO",
            "Documents": self.user_base / "Documents",
            "ELT Profiles and Site Visits": self.user_base / "ELT Profiles and Site Visits",
            "Flex HQ Files": self.user_base / "FLEX HQ Files",
            "Forms": self.user_base / "Forms",
            "Investigations": self.user_base / "Investigations",
            "Officer Files": self.user_base / "Officer Files",
            "Post Order and SOPs": self.user_base / "Post Order & SOPs",
            "Checklists and Trackers": self.user_base / "RSOC Checklists & Trackers (Save completed documents here)",
            "Templates": self.user_base / "RSOC Templates",
            "Systems": self.user_base / "Systems",
            "Training": self.user_base / "Training",
            "Weather Advisories": self.user_base / "Weather Advisories",
            "Admin Info": self.user_base / "Documents" / "Admin" / "Admin Information",
        }

        folder_labels = sorted(self.folder_paths.keys()) + ["Site Files"]

        for i, label in enumerate(folder_labels):
            btn = QPushButton(label)
            if label == "Site Files":
                btn.clicked.connect(self.show_site_files_view)
            else:
                btn.clicked.connect(partial(self.open_folder, label))
            grid.addWidget(btn, i // 3, i % 3)

        content.setLayout(grid)
        scroll.setWidget(content)

        layout = QVBoxLayout(self.main_widget)
        layout.addWidget(scroll)
        self.stacked_layout.addWidget(self.main_widget)

        # === SITE FILES VIEW ===
        self.site_files_widget = QWidget()
        site_grid = QGridLayout()
        site_grid.setAlignment(Qt.AlignTop)

        self.site_paths = {
            "Austin": self.user_base / "Site Files" / "AUR - Austin",
            "Buffalo Grove": self.user_base / "Site Files" / "BFG- Buffalo Grove",
            "West Columbia": self.user_base / "Site Files" / "CLB - West Columbia",
            "Coopersville": self.user_base / "Site Files" / "CVL - Coopersville",
            "Dallas": self.user_base / "Site Files" / "DAL-Dallas",
            "Hollis": self.user_base / "Site Files" / "HOL - Hollis",
            "Manchester": self.user_base / "Site Files" / "MCT - Manchester",
            "Memphis": self.user_base / "Site Files" / "MEM - Memphis",
            "Milpitas": self.user_base / "Site Files" / "MIL - Milpitas",
            "Northfield": self.user_base / "Site Files" / "NFLD-Northfield□",
            "Newmarket": self.user_base / "Site Files" / "NMK - Newmarket",
            "Farmington Hills": self.user_base / "Site Files" / "RHL - Farmington Hills",
            "Richmond": self.user_base / "Site Files" / "RIC - Anord Mardix Virginia",
            "Sacramento": self.user_base / "Site Files" / "SAC - Sacramento",
            "San Jose": self.user_base / "Site Files" / "SJC - San Jose",
            "Salt Lake City": self.user_base / "Site Files" / "SLC - Salt Lake City",
            "Sterling Heights": self.user_base / "Site Files" / "STH - Sterling Heights",
        }

        # Add site buttons to grid
        for i, label in enumerate(self.site_paths):
            btn = QPushButton(label)
            btn.clicked.connect(partial(self.open_site_folder, label))
            site_grid.addWidget(btn, i // 3, i % 3)

        # Add back button at bottom
        back_btn = QPushButton("← Back to Folders")
        back_btn.setObjectName("backButton")
        back_btn.setFixedWidth(200)
        back_btn.clicked.connect(self.show_main_folder_view)

        from PySide6.QtWidgets import QHBoxLayout, QSpacerItem, QSizePolicy
        back_layout = QHBoxLayout()
        back_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        back_layout.addWidget(back_btn)

        # Position the back layout under all folder buttons
        site_grid.addLayout(back_layout, (len(self.site_paths) + 2) // 3, 0, 1, 3)

        self.site_files_widget.setLayout(site_grid)
        self.stacked_layout.addWidget(self.site_files_widget)


    def open_folder(self, label):
        path = self.folder_paths.get(label)
        if path and path.exists():
            os.startfile(str(path))
        else:
            QMessageBox.warning(self, "Error", f"No path set for: {label}")

    def open_site_folder(self, label):
        path = self.site_paths.get(label)
        if path and path.exists():
            os.startfile(str(path))
        else:
            QMessageBox.warning(self, "Error", f"No site path set for: {label}")

    def show_site_files_view(self):
        self.stacked_layout.setCurrentIndex(1)

    def show_main_folder_view(self):
        self.stacked_layout.setCurrentIndex(0)

