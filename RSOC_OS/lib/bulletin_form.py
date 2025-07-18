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

from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
)
from lib.bulletin_outlook_helper import send_bulletin_to_outlook  # type: ignore


def format_subject_case(text: str) -> str:
    """
    Capitalizes acronyms and proper nouns, but lowercases common subject words.
    'EMS Arrival' => 'EMS arrival'
    'Unauthorized Entry' => 'Unauthorized entry'
    """
    words = text.strip().split()
    formatted = []

    for word in words:
        if word.isupper():  # keep acronyms as-is
            formatted.append(word)
        elif word.istitle():  # proper nouns (entered intentionally)
            formatted.append(word)
        else:
            formatted.append(word.lower())

    # Capitalize only the first word if not already capitalized
    if formatted:
        if not formatted[0].isupper():
            formatted[0] = formatted[0].capitalize()

    return ' '.join(formatted)


class BulletinForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bulletin Generator")

        # Input fields
        self.name_input = QLineEdit()
        self.name_input.setObjectName("BulletinNameField")

        self.subject_input = QLineEdit()
        self.subject_input.setObjectName("BulletinSubjectField")

        self.location_input = QLineEdit()
        self.location_input.setObjectName("BulletinLocationField")

        # Layouts
        layout = QVBoxLayout()

        name_label = QLabel("Reporter Name:")
        name_label.setObjectName("SitrepTitle")
        layout.addWidget(name_label)
        layout.addWidget(self.name_input)

        subject_label = QLabel("Subject (Incident Type):")
        subject_label.setObjectName("SitrepTitle")
        layout.addWidget(subject_label)
        layout.addWidget(self.subject_input)

        location_label = QLabel("Location:")
        location_label.setObjectName("SitrepTitle")
        layout.addWidget(location_label)
        layout.addWidget(self.location_input)

        # Submit button
        button_layout = QHBoxLayout()
        submit_btn = QPushButton("Generate Bulletin")
        submit_btn.clicked.connect(self.handle_submit)
        button_layout.addStretch()
        button_layout.addWidget(submit_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def handle_submit(self):
        reporter = self.name_input.text().strip()
        subject  = format_subject_case(self.subject_input.text().strip())
        location = format_subject_case(self.location_input.text().strip())

        if not (reporter and subject and location):
            QMessageBox.warning(self, "Missing Info", "Please fill out all fields.")
            return

        try:
            send_bulletin_to_outlook(reporter, subject, location)
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"An error occurred while generating the bulletin:\n{e}"
            )


def get_bulletin_form_widget():
    return BulletinForm()
