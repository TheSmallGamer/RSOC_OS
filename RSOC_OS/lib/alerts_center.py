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
import json
import getpass
from PySide6.QtWidgets import (
    QMessageBox, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QGridLayout, QCheckBox, QSizePolicy, QDialog,
    QLineEdit, QTextEdit, QTimeEdit, QSpinBox, QComboBox
)
from PySide6.QtCore import Qt, QSize, QTime

# ===== User-specific alerts file =====
USERNAME = getpass.getuser()
ALERTS_FILE = f'./config/alerts_{USERNAME}.json'


def get_alerts_widget(parent=None):
    widget = QWidget()
    layout = QVBoxLayout()

    # ===== Top Bar =====
    top_bar = QHBoxLayout()

    title = QLabel("Alerts Center")
    title.setObjectName("AlertsTitle")
    title.setAlignment(Qt.AlignCenter)

    add_button = QPushButton("New Alert")
    add_button.clicked.connect(lambda: open_new_alert_dialog(widget))

    left_spacer = QWidget()
    left_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
    right_spacer = QWidget()
    right_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

    top_bar.addWidget(left_spacer)
    top_bar.addWidget(title)
    top_bar.addWidget(right_spacer)
    top_bar.addWidget(add_button)

    layout.addLayout(top_bar)

    # ===== Scrollable Grid =====
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)

    content_widget = QWidget()
    grid_layout = QGridLayout()
    content_widget.setLayout(grid_layout)

    scroll_area.setWidget(content_widget)
    layout.addWidget(scroll_area)

    widget.setLayout(layout)

    load_alerts(grid_layout, widget)

    return widget


# ===== Load Alerts =====
def load_alerts(grid_layout, parent_widget):
    alerts = read_alerts_data()
    alerts = sorted(alerts, key=lambda x: x.get("enabled", True), reverse=True)

    for i in reversed(range(grid_layout.count())):
        grid_layout.itemAt(i).widget().setParent(None)

    col_count = 3
    for index, alert in enumerate(alerts):
        row = index // col_count
        col = index % col_count
        grid_layout.addWidget(create_alert_card(alert, parent_widget, index), row, col)


# ===== Create Alert Card =====
def create_alert_card(alert, parent_widget, index):
    card = QWidget()
    card.setObjectName("AlertCard")
    layout = QVBoxLayout()

    urgency = alert.get("urgency", "Normal")
    title = QLabel(f"{alert.get('title', 'Untitled')} [{urgency}]")
    title.setStyleSheet("font-weight: bold;")
    layout.addWidget(title)

    layout.addWidget(QLabel(f"Next Alert: {alert.get('time', 'N/A')}"))

    toggle = QCheckBox("Enabled")
    toggle.setChecked(alert.get("enabled", True))
    toggle.stateChanged.connect(lambda state: toggle_alert(index, state, parent_widget))
    layout.addWidget(toggle)

    btn_layout = QHBoxLayout()
    edit_btn = QPushButton("Edit")
    edit_btn.clicked.connect(lambda: open_edit_alert_dialog(index, parent_widget))
    delete_btn = QPushButton("Delete")
    delete_btn.clicked.connect(lambda: delete_alert(index, parent_widget))
    btn_layout.addWidget(edit_btn)
    btn_layout.addWidget(delete_btn)
    layout.addLayout(btn_layout)

    card.setLayout(layout)
    card.setFixedSize(QSize(250, 120))
    return card


# ===== New Alert Dialog =====
def open_new_alert_dialog(parent_widget):
    dialog = QDialog(parent_widget)
    dialog.setWindowTitle("Create New Alert")
    dialog.setMinimumWidth(400)

    layout = QVBoxLayout()

    title_input = QLineEdit()
    description_input = QTextEdit()
    time_input = QTimeEdit()
    time_input.setDisplayFormat("HH:mm")
    time_input.setTime(QTime.currentTime())
    repeat_input = QSpinBox()
    repeat_input.setRange(0, 1440)
    urgency_input = QComboBox()
    urgency_input.addItems(["Low", "Normal", "High"])
    clipboard_input = QComboBox()
    clipboard_input.addItem("None")
    clipboard_input.addItems(get_clipboard_titles())
    enable_toggle = QCheckBox("Enable this alert")
    enable_toggle.setChecked(True)

    layout.addWidget(QLabel("Alert Title:")); layout.addWidget(title_input)
    layout.addWidget(QLabel("Description:")); layout.addWidget(description_input)
    layout.addWidget(QLabel("Alert Time:")); layout.addWidget(time_input)
    layout.addWidget(QLabel("Repeat Interval (minutes, 0 = No Repeat):")); layout.addWidget(repeat_input)
    layout.addWidget(QLabel("Urgency Level:")); layout.addWidget(urgency_input)
    layout.addWidget(QLabel("Link Clipboard Entry:")); layout.addWidget(clipboard_input)
    layout.addWidget(enable_toggle)

    button_layout = QHBoxLayout()
    save_btn = QPushButton("Save")
    cancel_btn = QPushButton("Cancel")
    cancel_btn.clicked.connect(dialog.close)
    button_layout.addStretch(); button_layout.addWidget(save_btn); button_layout.addWidget(cancel_btn)
    layout.addLayout(button_layout)

    dialog.setLayout(layout)

    def save_alert():
        title = title_input.text().strip() or "Untitled Alert"
        alert_entry = {
            "title": title,
            "description": description_input.toPlainText().strip(),
            "time": time_input.time().toString("HH:mm"),
            "repeat_interval": repeat_input.value(),
            "urgency": urgency_input.currentText(),
            "enabled": enable_toggle.isChecked()
        }
        if clipboard_input.currentText() != "None":
            alert_entry["linked_clipboard"] = clipboard_input.currentText()

        alerts = read_alerts_data()
        alerts.insert(0, alert_entry)
        write_alerts_data(alerts)
        load_alerts(parent_widget.findChild(QScrollArea).widget().layout(), parent_widget)
        dialog.close()

    save_btn.clicked.connect(save_alert)
    dialog.exec()


# ===== Edit Alert Dialog =====
def open_edit_alert_dialog(alert_index, parent_widget):
    alerts = read_alerts_data()
    alert = alerts[alert_index]

    dialog = QDialog(parent_widget)
    dialog.setWindowTitle(f"Edit Alert: {alert.get('title', 'Untitled')}")
    dialog.setMinimumWidth(400)

    layout = QVBoxLayout()

    title_input = QLineEdit(alert.get("title", ""))
    description_input = QTextEdit(); description_input.setPlainText(alert.get("description", ""))
    time_input = QTimeEdit(); time_input.setDisplayFormat("HH:mm")
    hours, minutes = map(int, alert.get("time", "00:00").split(":"))
    time_input.setTime(QTime(hours, minutes))
    repeat_input = QSpinBox(); repeat_input.setRange(0, 1440); repeat_input.setValue(alert.get("repeat_interval", 0))
    urgency_input = QComboBox(); urgency_input.addItems(["Low", "Normal", "High"])
    urgency_input.setCurrentIndex(urgency_input.findText(alert.get("urgency", "Normal")))
    clipboard_input = QComboBox(); clipboard_input.addItem("None"); clipboard_input.addItems(get_clipboard_titles())
    clip_index = clipboard_input.findText(alert.get("linked_clipboard", "None"))
    clipboard_input.setCurrentIndex(clip_index if clip_index >= 0 else 0)
    enable_toggle = QCheckBox("Enable this alert"); enable_toggle.setChecked(alert.get("enabled", True))

    layout.addWidget(QLabel("Alert Title:")); layout.addWidget(title_input)
    layout.addWidget(QLabel("Description:")); layout.addWidget(description_input)
    layout.addWidget(QLabel("Alert Time:")); layout.addWidget(time_input)
    layout.addWidget(QLabel("Repeat Interval (minutes, 0 = No Repeat):")); layout.addWidget(repeat_input)
    layout.addWidget(QLabel("Urgency Level:")); layout.addWidget(urgency_input)
    layout.addWidget(QLabel("Link Clipboard Entry:")); layout.addWidget(clipboard_input)
    layout.addWidget(enable_toggle)

    button_layout = QHBoxLayout()
    save_btn = QPushButton("Save Changes")
    cancel_btn = QPushButton("Cancel")
    cancel_btn.clicked.connect(dialog.close)
    button_layout.addStretch(); button_layout.addWidget(save_btn); button_layout.addWidget(cancel_btn)
    layout.addLayout(button_layout)

    dialog.setLayout(layout)

    def save_edited_alert():
        alert["title"] = title_input.text().strip() or "Untitled Alert"
        alert["description"] = description_input.toPlainText().strip()
        alert["time"] = time_input.time().toString("HH:mm")
        alert["repeat_interval"] = repeat_input.value()
        alert["urgency"] = urgency_input.currentText()
        alert["enabled"] = enable_toggle.isChecked()
        selected_clip = clipboard_input.currentText()
        if selected_clip != "None":
            alert["linked_clipboard"] = selected_clip
        else:
            alert.pop("linked_clipboard", None)

        write_alerts_data(alerts)
        load_alerts(parent_widget.findChild(QScrollArea).widget().layout(), parent_widget)
        dialog.close()

    save_btn.clicked.connect(save_edited_alert)
    dialog.exec()


# ===== Toggle Enable/Disable =====
def toggle_alert(alert_index, state, parent_widget):
    alerts = read_alerts_data()
    alerts[alert_index]["enabled"] = bool(state)
    write_alerts_data(alerts)
    load_alerts(parent_widget.findChild(QScrollArea).widget().layout(), parent_widget)


# ===== Data Handling =====
def read_alerts_data():
    if not os.path.exists(ALERTS_FILE):
        return []
    with open(ALERTS_FILE, 'r') as file:
        return json.load(file).get("alerts", [])


def write_alerts_data(alerts):
    with open(ALERTS_FILE, 'w') as file:
        json.dump({"alerts": alerts}, file, indent=4)


# ===== Clipboard Helper =====
def get_clipboard_titles():
    clipboard_file = f'./config/clipboard_{USERNAME}.json'
    if not os.path.exists(clipboard_file):
        return []

    with open(clipboard_file, 'r') as file:
        data = json.load(file).get("clips", [])

    titles = []
    for clip in data:
        if "title" in clip:
            titles.append(clip["title"])
        else:
            preview = clip["content"][:30] + ("..." if len(clip["content"]) > 30 else "")
            titles.append(preview)
    return titles

def delete_alert(alert_index, parent_widget):
    alerts = read_alerts_data()

    confirm = QMessageBox.question(
        parent_widget,
        "Delete Alert",
        f"Are you sure you want to delete '{alerts[alert_index]['title']}'?",
        QMessageBox.Yes | QMessageBox.No
    )

    if confirm == QMessageBox.Yes:
        if 0 <= alert_index < len(alerts):
            alerts.pop(alert_index)
            write_alerts_data(alerts)
            load_alerts(parent_widget.findChild(QScrollArea).widget().layout(), parent_widget)