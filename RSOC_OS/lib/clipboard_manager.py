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
    QLineEdit, QSizePolicy, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QDialog, QScrollArea, QGridLayout
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QClipboard, QGuiApplication, QIcon

# Define user-specific JSON path
USERNAME = getpass.getuser()
CLIPBOARD_FILE = f'./config/clipboard_{USERNAME}.json'


def get_clipboard_widget(parent=None):
    widget = QWidget()
    layout = QVBoxLayout()

    # ===== Top Bar (Centered Title + Right-Aligned Add Button) =====
    top_bar = QHBoxLayout()

    left_spacer = QWidget()
    left_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

    right_spacer = QWidget()
    right_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

    title = QLabel("Clipboard")
    title.setObjectName("ClipboardTitle")
    title.setAlignment(Qt.AlignCenter)

    add_button = QPushButton("Add New")
    add_button.clicked.connect(lambda: open_add_dialog(widget))

    top_bar.addWidget(left_spacer)
    top_bar.addWidget(title)
    top_bar.addWidget(right_spacer)
    top_bar.addWidget(add_button)

    layout.addLayout(top_bar)

    # ===== Scrollable Grid for Clipboard Entries =====
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)

    content_widget = QWidget()
    grid_layout = QGridLayout()
    content_widget.setLayout(grid_layout)

    scroll_area.setWidget(content_widget)
    layout.addWidget(scroll_area)

    widget.setLayout(layout)

    # Load and display saved clipboard entries
    load_clips(grid_layout, widget)

    return widget

# ===== Load Clipboard Data and Populate Grid =====
def load_clips(grid_layout, parent_widget):
    clips = read_clipboard_data()

    clips = sorted(clips, key=lambda x: x.get("pinned", False), reverse=True)

    # Clear existing grid
    for i in reversed(range(grid_layout.count())):
        grid_layout.itemAt(i).widget().setParent(None)

    # Display clips in 3-column grid
    col_count = 3
    for index, clip in enumerate(clips):
        row = index // col_count
        col = index % col_count
        grid_layout.addWidget(create_clip_card(clip, parent_widget), row, col)

# ===== Create Individual Clipboard Card =====
def create_clip_card(clip, parent_widget):
    card = QWidget()
    card.setObjectName("ClipboardCard")
    card_layout = QVBoxLayout()

    top_bar = QHBoxLayout()

    if "title" in clip:
        title_label = QLabel(clip["title"])
        title_label.setStyleSheet("font-weight: bold;")
    else:
        title_label = QLabel("(No Title)")

    pin_button = QPushButton()
    update_pin_icon(pin_button, clip.get("pinned", False))
    pin_button.setFixedSize(20, 20)
    pin_button.setStyleSheet("border: none;")
    pin_button.clicked.connect(lambda: toggle_pin(clip, parent_widget))

    top_bar.addWidget(title_label)
    top_bar.addStretch()
    top_bar.addWidget(pin_button)

    card_layout.addLayout(top_bar)

    # Truncate display text
    display_text = clip["content"][:125] + ("..." if len(clip["content"]) > 75 else "")
    preview_label = QLabel(display_text)
    preview_label.setWordWrap(True)
    card_layout.addWidget(preview_label)

    # Buttons: Copy, Edit, Delete
    button_layout = QHBoxLayout()

    copy_btn = QPushButton("Copy")
    copy_btn.clicked.connect(lambda: copy_to_clipboard(clip["content"]))

    edit_btn = QPushButton("Edit")
    edit_btn.clicked.connect(lambda: open_edit_dialog(parent_widget, clip))

    delete_btn = QPushButton("Delete")
    delete_btn.clicked.connect(lambda: delete_clip(parent_widget, clip))

    for btn in [copy_btn, edit_btn, delete_btn]:
        button_layout.addWidget(btn)

    card_layout.addLayout(button_layout)
    card.setLayout(card_layout)
    card.setFixedSize(QSize(250, 150))

    return card


# ===== Clipboard Functions =====
def copy_to_clipboard(text):
    clipboard = QGuiApplication.clipboard()
    clipboard.setText(text)


def open_add_dialog(parent_widget):
    dialog = QDialog(parent_widget)
    dialog.setWindowTitle("Add New Clipboard Entry")
    layout = QVBoxLayout()

    title_input = QLineEdit()
    title_input.setPlaceholderText("Enter title...")
    layout.addWidget(title_input)

    text_edit = QTextEdit()
    text_edit.setPlaceholderText("Enter clipboard content...")
    layout.addWidget(text_edit)

    save_btn = QPushButton("Save")
    save_btn.clicked.connect(lambda: save_new_clip(dialog, title_input.text(), text_edit.toPlainText(), parent_widget))
    layout.addWidget(save_btn)

    dialog.setLayout(layout)
    dialog.exec()


def open_edit_dialog(parent_widget, clip):
    dialog = QDialog(parent_widget)
    dialog.setWindowTitle("Edit Clipboard Entry")
    layout = QVBoxLayout()

    text_edit = QTextEdit()
    text_edit.setPlainText(clip["content"])
    layout.addWidget(text_edit)

    save_btn = QPushButton("Save Changes")
    save_btn.clicked.connect(lambda: save_edited_clip(dialog, clip, text_edit.toPlainText(), parent_widget))
    layout.addWidget(save_btn)

    dialog.setLayout(layout)
    dialog.exec()


def save_new_clip(dialog, title, content, parent_widget):
    if content.strip() == "":
        dialog.close()
        return

    clip_entry = {"content": content}
    if title.strip():
        clip_entry["title"] = title.strip()

    clips = read_clipboard_data()
    clips.insert(0, clip_entry)
    write_clipboard_data(clips)
    dialog.close()

    refresh_display(parent_widget)


def save_edited_clip(dialog, clip, new_content, parent_widget):
    clips = read_clipboard_data()
    for c in clips:
        if c == clip:
            c["content"] = new_content
            break
    write_clipboard_data(clips)
    dialog.close()

    refresh_display(parent_widget)


def delete_clip(parent_widget, clip):
    clips = read_clipboard_data()
    clips = [c for c in clips if c != clip]
    write_clipboard_data(clips)

    refresh_display(parent_widget)

# ===== Data Handling =====
def read_clipboard_data():
    if not os.path.exists(CLIPBOARD_FILE):
        return []
    with open(CLIPBOARD_FILE, 'r') as file:
        return json.load(file).get("clips", [])


def write_clipboard_data(clips):
    with open(CLIPBOARD_FILE, 'w') as file:
        json.dump({"clips": clips}, file, indent=4)


def refresh_display(parent_widget):
    grid_layout = parent_widget.findChild(QScrollArea).widget().layout()
    load_clips(grid_layout, parent_widget)

def update_pin_icon(button, pinned):
    if pinned:
        button.setIcon(QIcon('images/pin_filled.png'))
    else:
        button.setIcon(QIcon('images/pin_hollow.png'))

def toggle_pin(clip, parent_widget):
    clips = read_clipboard_data()
    for c in clips:
        if c == clip:
            c["pinned"] = not c.get("pinned", False)
            break
    write_clipboard_data(clips)
    refresh_display(parent_widget)