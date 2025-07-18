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
    QMessageBox, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QDateEdit, QTimeEdit, QComboBox,
    QTextEdit, QLineEdit, QPushButton, QSizePolicy
)
from PySide6.QtCore import QDate, QTime, Qt
from lib.llm_narrative import generate_narrative_from_summary # type: ignore
from lib.sitrep_outlook_helper import send_general_sitrep_to_outlook # type: ignore

def get_general_sitrep_widget(parent=None):
    widget = QWidget()
    main_layout = QHBoxLayout(widget)

    # === LEFT COLUMN ===
    left_layout = QVBoxLayout()

    # Date, Time, and Time Zone in one row
    datetime_row = QHBoxLayout()
    
    date_label = QLabel("Date of Incident:")
    date_input = QDateEdit()
    date_input.setDate(QDate.currentDate())
    date_input.setCalendarPopup(True)

    time_label = QLabel("Time of Incident:")
    time_input = QTimeEdit()
    time_input.setTime(QTime.currentTime())

    timezone_label = QLabel("Time Zone:")
    timezone_input = QComboBox()
    timezone_input.addItems(["CST", "EST", "PST", "MST", "UTC"])

    datetime_row.addWidget(date_label)
    datetime_row.addWidget(date_input)
    datetime_row.addWidget(time_label)
    datetime_row.addWidget(time_input)
    datetime_row.addWidget(timezone_label)
    datetime_row.addWidget(timezone_input)

    # Location
    location_label = QLabel("Location:")
    location_input = QLineEdit()

    # Incident Type + "Other" custom input
    type_row = QHBoxLayout()
    type_label = QLabel("Incident Type:")
    type_input = QComboBox()
    type_input.addItems(["Power Outage", "Suspicious Activity", "Unauthorized Entry", "Equipment Failure", "Other"])
    other_type_input = QLineEdit()
    other_type_input.setPlaceholderText("Enter custom incident type...")
    other_type_input.setVisible(False)
    type_row.addWidget(type_input)
    type_row.addWidget(other_type_input)

    def handle_type_change(index):
        if type_input.currentText() == "Other":
            other_type_input.setVisible(True)
        else:
            other_type_input.setVisible(False)

    type_input.currentIndexChanged.connect(handle_type_change)

    # Affected Areas / Departments
    affected_label = QLabel("Affected Areas / Departments:")
    affected_input = QTextEdit()
    affected_input.setFixedHeight(60)

    # Personnel Involved
    personnel_label = QLabel("Personnel Involved:")
    personnel_input = QTextEdit()
    personnel_input.setFixedHeight(60)

    # Additional Notes / Summary
    notes_label = QLabel("Additional Notes / Summary:")
    notes_input = QTextEdit()
    notes_input.setFixedHeight(80)

    # Add widgets to left layout
    left_layout.addLayout(datetime_row)
    left_layout.addWidget(location_label)
    left_layout.addWidget(location_input)
    left_layout.addWidget(type_label)
    left_layout.addLayout(type_row)
    left_layout.addWidget(affected_label)
    left_layout.addWidget(affected_input)
    left_layout.addWidget(personnel_label)
    left_layout.addWidget(personnel_input)
    left_layout.addWidget(notes_label)
    left_layout.addWidget(notes_input)

    # === RIGHT COLUMN ===
    right_layout = QVBoxLayout()

    output_label = QLabel("Generated Situation Summary:")
    output_box = QTextEdit()
    output_box.setPlaceholderText("Click 'Generate Summary' to produce a professional writeup.")
    output_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    generate_button = QPushButton("Generate Summary")
    send_button = QPushButton("Send to Outlook")

    right_layout.addWidget(output_label)
    right_layout.addWidget(output_box)
    right_layout.addWidget(generate_button)
    right_layout.addWidget(send_button)

    # === MAIN LAYOUT ===
    main_layout.addLayout(left_layout, 2)
    main_layout.addLayout(right_layout, 3)

    # Store widgets as attributes for access
    widget.date_input = date_input
    widget.time_input = time_input
    widget.timezone_input = timezone_input
    widget.location_input = location_input
    widget.type_input = type_input
    widget.other_type_input = other_type_input
    widget.affected_input = affected_input
    widget.personnel_input = personnel_input
    widget.notes_input = notes_input
    widget.output_box = output_box
    widget.generate_button = generate_button
    widget.send_button = send_button

    def on_generate():
        date = widget.date_input.date().toString("MMMM d, yyyy")
        time = widget.time_input.time().toString("h:mm AP")
        timezone = widget.timezone_input.currentText()
        location = widget.location_input.text().strip()
        incident_type = widget.type_input.currentText()
        if incident_type == "Other":
            incident_type = widget.other_type_input.text().strip() or "Unspecified Incident"

        affected = widget.affected_input.toPlainText().strip()
        personnel = widget.personnel_input.toPlainText().strip()
        notes = widget.notes_input.toPlainText().strip()

        # Build structured input
        summary = (
            f"Date: {date}\n"
            f"Time: {time} {timezone}\n"
            f"Location: {location}\n"
            f"Incident Type: {incident_type}\n"
            f"Affected Areas/Departments: {affected}\n"
            f"Personnel Involved: {personnel}\n"
            f"Additional Notes: {notes}"
        )

        generated = generate_narrative_from_summary(summary, context="general") # type: ignore
        widget.output_box.setPlainText(generated)

    widget.generate_button.clicked.connect(on_generate)

    def on_send():
        summary = widget.output_box.toPlainText().strip()
        if not summary:
            QMessageBox.warning(widget, "Error", "No summary generated.")
            return

        date_str = widget.date_input.date().toString("MMMM d, yyyy")
        incident_type = widget.type_input.currentText()
        if incident_type == "Other":
            incident_type = widget.other_type_input.text().strip() or "Unspecified"

        send_general_sitrep_to_outlook(summary, date_str, incident_type)

    widget.send_button.clicked.connect(on_send)

    return widget