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
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton
from PySide6.QtCore import Qt

# Path to save the notes JSON file
NOTES_FILE = './config/quick_notes.json'

def get_quick_notes_widget(parent=None):
    widget = QWidget()
    layout = QVBoxLayout()

    # Title Label
    title = QLabel("Notes")
    title.setAlignment(Qt.AlignCenter)
    title.setObjectName("QuickNotesTitle")
    layout.addWidget(title)

    # Text Area
    text_edit = QTextEdit()
    text_edit.setPlaceholderText("Start typing your notes here...")
    layout.addWidget(text_edit)

    # Clear Button
    clear_button = QPushButton("Clear Notes")
    layout.addWidget(clear_button)

    widget.setLayout(layout)

    # Load existing note if available
    if os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, 'r') as file:
            data = json.load(file)
            text_edit.setPlainText(data.get("note", ""))

    # Autosave on text change
    text_edit.textChanged.connect(lambda: autosave_notes(text_edit.toPlainText()))

    # Clear button functionality
    clear_button.clicked.connect(lambda: clear_notes(text_edit))

    return widget

def autosave_notes(content):
    data = {"note": content}
    with open(NOTES_FILE, 'w') as file:
        json.dump(data, file)

def clear_notes(text_edit):
    text_edit.clear()
    if os.path.exists(NOTES_FILE):
        os.remove(NOTES_FILE)
