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

import os
import subprocess
import json
from threading import Thread
import time
import tkinter as tk
from tkinter import filedialog, messagebox

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QWidget, QVBoxLayout, QComboBox, QPushButton, QLabel, QMessageBox

import pygetwindow as gw  # type: ignore

CONFIG_PATH = "./config/milestone_config.json"
IP_MAP_PATH = "./config/site_ip_map.json"

def load_milestone_path():
    if not os.path.exists(CONFIG_PATH):
        return prompt_for_exe()
    try:
        with open(CONFIG_PATH, 'r') as file:
            data = json.load(file)
            path = data.get("milestone_path")
            if path and os.path.isfile(path):
                return path
            else:
                return prompt_for_exe()
    except json.JSONDecodeError:
        return prompt_for_exe()

def save_milestone_path(path):
    with open(CONFIG_PATH, 'w') as file:
        json.dump({"milestone_path": path}, file)

def prompt_for_exe():
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Milestone Executable", "Please locate the Milestone XProtect Smart Client executable.")
    exe_path = filedialog.askopenfilename(
        title="Select Milestone XProtect Smart Client",
        filetypes=[("Executable Files", "*.exe")]
    )
    if exe_path:
        save_milestone_path(exe_path)
    return exe_path if exe_path else None

def wait_for_login_window(title_keyword="Smart Client", timeout=60):
    start = time.time()
    while time.time() - start < timeout:
        windows = gw.getWindowsWithTitle(title_keyword)
        if windows:
            windows[0].activate()
            return True
        time.sleep(1)
    raise TimeoutError("Milestone window not detected within timeout.")

def wait_for_login_elements(timeout=60):
    from pywinauto import Application  # type: ignore

    start = time.time()
    while time.time() - start < timeout:
        try:
            app = Application(backend="uia").connect(title_re=".*Smart Client.*", found_index=0)
            window = app.top_window()
            if window.child_window(title="Connect", control_type="Button").exists():
                return True
        except Exception:
            pass
        time.sleep(1)
    raise TimeoutError("Milestone Connect button not found in time.")

def get_ip_for_site(site_name):
    if not os.path.exists(IP_MAP_PATH):
        raise FileNotFoundError("Site-to-IP mapping file not found.")
    with open(IP_MAP_PATH, 'r') as f:
        ip_map = json.load(f)
    return ip_map.get(site_name)

def launch_milestone_and_login(site_name):
    import pyautogui  # type: ignore

    ip_address = get_ip_for_site(site_name)

    if ip_address == "Not Milestone Server":
        QTimer.singleShot(0, lambda: QMessageBox.warning(
            None,
            "Use Different System",
            f"{site_name} is not a camera system hosted on Milestone.\nPlease use the required camera system to open."
        ))
        return

    elif ip_address == "No Camera Server":
        QTimer.singleShot(0, lambda: QMessageBox.warning(
            None,
            "No Camera Server",
            f"There is currently no set up Milestone camera server for {site_name}.\nPlease try again later."
        ))
        return

    exe_path = load_milestone_path()
    if not exe_path:
        return

    subprocess.Popen(exe_path)

    try:
        wait_for_login_window()
        wait_for_login_elements()
    except TimeoutError as e:
        QTimer.singleShot(0, lambda: QMessageBox.critical(None, "Milestone Timeout", str(e)))
        return
    except Exception as e:
        QTimer.singleShot(0, lambda: QMessageBox.critical(None, "Milestone Detection Failed", f"An unexpected error occurred:\n{e}"))
        return

    pyautogui.press('tab', presses=2, interval=0.25)
    pyautogui.write(ip_address)
    pyautogui.press('enter')

def get_milestone_launcher_widget():
    widget = QWidget()
    layout = QVBoxLayout(widget)

    title = QLabel("Select Site to Launch Milestone")
    title.setObjectName("SitrepTitle")
    layout.addWidget(title)

    site_dropdown = QComboBox()
    try:
        with open(IP_MAP_PATH, 'r') as f:
            site_map = json.load(f)
            for site in site_map.keys():
                site_dropdown.addItem(site)
    except Exception:
        site_dropdown.addItem("Error loading sites")

    layout.addWidget(site_dropdown)

    launch_button = QPushButton("Launch Milestone")
    layout.addWidget(launch_button)

    def handle_launch():
        selected_site = site_dropdown.currentText()
        ip_address = get_ip_for_site(selected_site)

        if ip_address == "Not Milestone Server":
            QMessageBox.warning(
                widget,
                "Use Different System",
                f"{selected_site} is not a camera system hosted on Milestone.\n\nPlease use the required camera system to open."
            )
            return

        elif ip_address == "No Camera Server":
            QMessageBox.warning(
                widget,
                "No Camera Server",
                f"There is currently no set up Milestone camera server for {selected_site}.\n\nPlease try again later."
            )
            return

        def safe_launch():
            try:
                launch_milestone_and_login(selected_site)
            except TimeoutError as e:
                QTimer.singleShot(0, lambda: QMessageBox.critical(widget, "Milestone Timeout", str(e)))
            except Exception as e:
                QTimer.singleShot(0, lambda: QMessageBox.critical(widget, "Milestone Crash", f"Unexpected error:\n{e}"))

        Thread(target=safe_launch, daemon=True).start()

    launch_button.clicked.connect(handle_launch)
    return widget
