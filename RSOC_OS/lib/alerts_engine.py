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

import threading
import time
import datetime
import os
import json
import getpass
import winsound

from PySide6.QtWidgets import (
    QApplication, QDialog, QScrollArea, QSizePolicy, QVBoxLayout, QLabel, QPushButton
)
from PySide6.QtCore import (
    QTimer, Qt, QSize, QObject, Signal
)

# ===== User Info =====
USERNAME = getpass.getuser()
ALERTS_FILE = f'./config/alerts_{USERNAME}.json'

# ===== Qt Signal Handler =====
class AlertSignalHandler(QObject):
    show_alert_signal = Signal(dict)
    copy_clipboard_signal = Signal(str)

signal_handler = AlertSignalHandler()

# ===== Alert Trigger Logic =====
def trigger_alert(alert):
    urgency = alert.get("urgency", "Normal")
    print(f"[ALERT TRIGGERED] {alert.get('title')} - Urgency: {urgency}")
    play_sound(urgency)

    signal_handler.show_alert_signal.emit(alert)

    clipboard_entry = alert.get("linked_clipboard")
    if clipboard_entry:
        print(f"[CLIPBOARD] Attempting to copy linked entry: {clipboard_entry}")
        signal_handler.copy_clipboard_signal.emit(clipboard_entry)

def play_sound(urgency):
    if urgency == "Low":
        winsound.MessageBeep(winsound.MB_ICONASTERISK)
    elif urgency == "Normal":
        winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
    elif urgency == "High":
        winsound.MessageBeep(winsound.MB_ICONHAND)
    else:
        winsound.MessageBeep()

# ===== Background Monitoring =====
def alert_monitor_loop():
    while True:
        check_alerts()
        time.sleep(10)  # Every 10 seconds

def check_alerts():
    now = datetime.datetime.now()
    current_time_str = now.strftime("%H:%M")
    current_timestamp_str = now.strftime("%Y-%m-%d %H:%M")

    alerts = read_alerts_data()
    updated = False

    for alert in alerts:
        if not alert.get("enabled", True):
            continue

        alert_time = alert.get("time")
        repeat = alert.get("repeat_interval", 0)
        last_triggered = alert.get("last_triggered", "")

        # Skip if already triggered this minute
        if last_triggered == current_timestamp_str:
            continue

        # Fire if one-time or repeatable
        if current_time_str == alert_time or (
            repeat > 0 and should_trigger_repeat(current_time_str, alert_time, repeat)
        ):
            alert["last_triggered"] = current_timestamp_str
            trigger_alert(alert)

            if repeat == 0:
                alert["enabled"] = False

            updated = True

    if updated:
        write_alerts_data(alerts)


def should_trigger_repeat(current_time, start_time, interval):
    fmt = "%H:%M"
    ct = datetime.datetime.strptime(current_time, fmt)
    st = datetime.datetime.strptime(start_time, fmt)

    minutes_passed = int((ct - st).total_seconds() / 60)
    return minutes_passed >= 0 and minutes_passed % interval == 0

# ===== Start Alert Engine =====
def start_alert_engine(parent_widget):
    signal_handler.show_alert_signal.connect(lambda alert: show_popup(alert))
    signal_handler.copy_clipboard_signal.connect(copy_clipboard_text)

    thread = threading.Thread(target=alert_monitor_loop, daemon=True)
    thread.start()

# ===== Pop-Up Dialog =====
def show_popup(alert):
    popup = PopUpAlertWindow(alert)
    popup.exec()

class PopUpAlertWindow(QDialog):
    def __init__(self, alert):
        super().__init__()
        self.setWindowTitle("RSOC-OS Alert")
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setFixedSize(QSize(350, 250))  # Slightly larger to fit content

        urgency = alert.get("urgency", "Normal")
        color = {
            "Low": "#2980b9",
            "Normal": "#f39c12",
            "High": "#c0392b"
        }.get(urgency, "#95a5a6")

        layout = QVBoxLayout(self)

        # Title
        title = QLabel(alert.get("title", "Alert"))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"""
            font-size: 16px;
            font-weight: bold;
            color: white;
            background-color: {color};
            padding: 10px;
        """)
        layout.addWidget(title)

        # Scrollable Description
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFixedHeight(120)

        desc_label = QLabel(alert.get("description", ""))
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        desc_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        desc_label.setContentsMargins(5, 5, 5, 5)

        scroll_area.setWidget(desc_label)
        layout.addWidget(scroll_area)

        # Acknowledge Button
        ack_btn = QPushButton("Acknowledge")
        ack_btn.clicked.connect(self.accept)
        layout.addWidget(ack_btn)

        # Final window positioning
        self.adjustSize()
        self.move(QApplication.primaryScreen().availableGeometry().center() - self.rect().center())


# ===== Clipboard Integration =====
def copy_clipboard_text(title):
    app = QApplication.instance()
    if app is None:
        print("[ERROR] QApplication instance not found for clipboard!")
        return

    clipboard_file = f'./config/clipboard_{USERNAME}.json'
    if not os.path.exists(clipboard_file):
        print("[ERROR] Clipboard file not found.")
        return

    with open(clipboard_file, 'r') as file:
        clips = json.load(file).get("clips", [])

    for clip in clips:
        if clip.get("title") == title:
            content = clip.get("content", "")
            app.clipboard().setText(content)
            app.processEvents()
            print(f"[CLIPBOARD] Copied content: {content[:30]}...")
            break

# ===== JSON Read/Write =====
def read_alerts_data():
    if not os.path.exists(ALERTS_FILE):
        return []

    with open(ALERTS_FILE, 'r') as file:
        alerts = json.load(file).get("alerts", [])

    # Patch old-format timestamps
    for alert in alerts:
        lt = alert.get("last_triggered", "")
        if lt and len(lt) == 5:
            alert["last_triggered"] = ""

    return alerts

def write_alerts_data(alerts):
    with open(ALERTS_FILE, 'w') as file:
        json.dump({"alerts": alerts}, file, indent=4)
