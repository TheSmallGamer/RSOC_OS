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

import json
import os
import subprocess
import time
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit, QComboBox,
    QDateEdit, QTimeEdit, QTextEdit, QPushButton, QMessageBox, QCheckBox, QFileDialog
)
from PySide6.QtCore import Qt, QDate, QTime
from lib.llm_narrative import generate_narrative_from_summary # type: ignore
from lib.sitrep_outlook_helper import get_filled_html, load_navex_recipients # type: ignore
import win32com.client


def get_navex_sitrep_widget(region_name, parent=None):
    region_combo = QComboBox()
    region_combo.addItems([
        "US and Canada", "Mexico and Costa Rica", "Brazil",
        "Europe", "China", "India", "Penang / Southeast Asia"
    ])
    region_combo.setCurrentText(region_name)
    region_combo.setDisabled(True)  # Prevent user from changing it

    summary_types = [
        "Workplace Harassment", "Workplace Violence", "Nepotism", "Favoritism",
        "Retaliation", "Discrimination", "Policy Violation", "Safety Concern", "Theft", "Other"
    ]

    widget = QWidget()
    main_layout = QHBoxLayout(widget)

    # === Left Form Column ===
    form_col = QVBoxLayout()
    form_grid = QGridLayout()
    row = 0

    selected_region_label = QLabel(f"Selected Region: {region_name}")
    selected_region_label.setStyleSheet("font-weight: bold; font-size: 14px;")
    form_grid.addWidget(selected_region_label)
    row += 1

    case_input = QLineEdit()
    form_grid.addWidget(QLabel("NAVEX Case #:"), row, 0)
    form_grid.addWidget(case_input, row, 1)

    date_input = QDateEdit()
    date_input.setDate(QDate.currentDate())
    form_grid.addWidget(QLabel("Date:"), row, 2)
    form_grid.addWidget(date_input, row, 3)

    row += 1
    time_input = QTimeEdit()
    time_input.setTime(QTime.currentTime())
    form_grid.addWidget(QLabel("Time:"), row, 0)
    form_grid.addWidget(time_input, row, 1)

    timezone_input = QComboBox()
    timezone_input.addItems(["CST", "EST", "PST", "MST", "GMT", "IST", "CET", "BRT"])
    form_grid.addWidget(QLabel("Time Zone:"), row, 2)
    form_grid.addWidget(timezone_input, row, 3)

    row += 1
    reporter_input = QLineEdit()
    anonymous_checkbox = QCheckBox("Anonymous")

    def toggle_anonymous(checked):
        reporter_input.setDisabled(checked)

    anonymous_checkbox.stateChanged.connect(lambda state: reporter_input.setDisabled(state == Qt.Checked))

    form_grid.addWidget(QLabel("Reporter:"), row, 0)
    form_grid.addWidget(reporter_input, row, 1, 1, 2)
    form_grid.addWidget(anonymous_checkbox, row, 3)

    row += 1
    subject_type_combo = QComboBox()
    subject_type_combo.addItems(summary_types)
    custom_subject_input = QLineEdit()
    custom_subject_input.setPlaceholderText("Enter custom subject type...")
    custom_subject_input.setVisible(False)

    subject_type_layout = QHBoxLayout()
    subject_type_layout.addWidget(subject_type_combo)
    subject_type_layout.addWidget(custom_subject_input)

    form_grid.addWidget(QLabel("Subject Type:"), row, 0)
    form_grid.addLayout(subject_type_layout, row, 1, 1, 3)


    def handle_subject_change(text):
        custom_subject_input.setVisible(text == "Other")

    subject_type_combo.currentTextChanged.connect(handle_subject_change)

    row += 1
    subject_description_input = QLineEdit()
    subject_description_input.setPlaceholderText("(e.g. the reporting employee's manager, a team lead, or HR)")
    form_grid.addWidget(QLabel("Subject Description:"), row, 0)
    form_grid.addWidget(subject_description_input, row, 1, 1, 3)

    row += 1
    summary_input = QTextEdit()
    summary_input.setPlaceholderText("What happened, in basic terms...")
    form_grid.addWidget(QLabel("Summary Details:"), row, 0)
    form_grid.addWidget(summary_input, row, 1, 1, 3)

    row += 1
    site_input = QLineEdit()
    site_input.setPlaceholderText("(e.g. Guad North)")
    form_grid.addWidget(QLabel("Reported Site Location:"), row, 0)
    form_grid.addWidget(site_input, row, 1, 1, 3)

    # === Leadership Section ===
    form_col.addLayout(form_grid)
    form_col.addSpacing(10)
    form_col.addWidget(QLabel("Leadership Parties Involved:"))

    leader_layout = QVBoxLayout()
    form_col.addLayout(leader_layout)

    def add_leadership_row(name="", title=""):
        row_layout = QHBoxLayout()
        name_input = QLineEdit(); name_input.setText(name)
        title_input = QLineEdit(); title_input.setText(title)
        remove_btn = QPushButton("-")

        def remove():
            if leader_layout.count() > 1:
                row_item = row_layout
                while row_item.count():
                    item = row_item.takeAt(0)
                    if item.widget(): item.widget().deleteLater()
                leader_layout.removeItem(row_item)

        remove_btn.clicked.connect(remove)

        row_layout.addWidget(QLabel("Name:"))
        row_layout.addWidget(name_input)
        row_layout.addWidget(QLabel("Job Title:"))
        row_layout.addWidget(title_input)
        row_layout.addWidget(remove_btn)
        leader_layout.addLayout(row_layout)

    add_leadership_row()  # Always at least one

    add_btn = QPushButton("+")
    add_btn.setFixedWidth(30)
    add_btn.clicked.connect(lambda: add_leadership_row())
    form_col.addWidget(add_btn)

    # === Buttons ===
    button_layout = QHBoxLayout()
    generate_btn = QPushButton("Generate")
    send_btn = QPushButton("Copy to Outlook")
    button_layout.addWidget(generate_btn)
    button_layout.addWidget(send_btn)
    form_col.addLayout(button_layout)

    # === Right Output Column ===
    output = QTextEdit()
    output.setReadOnly(False)
    output.setPlaceholderText("Generated NAVEX message will appear here...")
    output.setMinimumWidth(500)

    # === Final Layout ===
    main_layout.addLayout(form_col, 3)
    main_layout.addWidget(output, 2)

    def on_generate():
        case = case_input.text().strip()
        date = date_input.date().toString("MMMM d, yyyy")
        time_str = time_input.time().toString("HH:mm")
        timezone = timezone_input.currentText()
        reporter = reporter_input.text().strip() if not anonymous_checkbox.isChecked() else "an anonymous employee"
        subject = (
            custom_subject_input.text().strip()
            if subject_type_combo.currentText() == "Other"
            else subject_type_combo.currentText()
        ).lower()
        subject_description = subject_description_input.text().strip()
        site = site_input.text().strip()

        if not all([case, subject, subject_description, site]):
            return QMessageBox.warning(widget, "Missing Info", "Fill all required fields first.")

        # Leadership entries
        leadership_lines = []
        for i in range(leader_layout.count()):
            row = leader_layout.itemAt(i)
            if isinstance(row, QHBoxLayout):
                name_input = row.itemAt(1).widget()
                title_input = row.itemAt(3).widget()
                if name_input and title_input and (name_input.text().strip() or title_input.text().strip()):
                    leadership_lines.append(f"• {name_input.text().strip()} - {title_input.text().strip()}")
        if not leadership_lines:
            leadership_lines = ["• N/A"]

        # Refined LLM prompt
        cleaned_input = subject_description.strip()
        refined_prompt = (
            f"Subject Type: {subject}\n"
            f"Reported By: {reporter}\n"
            f"Subject Description: {subject_description.strip()}\n"
            f"Summary Details: {summary_input.toPlainText().strip()}"
        )
        
        # Start Ollama
        ollama_proc = subprocess.Popen(["ollama", "serve"])
        time.sleep(2)
        generated_summary = generate_narrative_from_summary(refined_prompt, context="navex")
        ollama_proc.terminate()

        final_message = (
            f"NAVEX Case #: {case}\n\n"
            f"On {date} at {time_str} {timezone}, the Regional Security Operations Center (RSOC) received a NAVEX email "
            f"regarding a report made by {reporter} regarding {subject}. {generated_summary.strip()}\n\n"
            f"The leadership parties involved are as follows:\n\n"
            f"{chr(10).join(leadership_lines)}\n\n"
            f"The reported location is at the {site} site.\n\n"
            f"Please see the attached NAVEX report for a more in-depth approach.\n\n"
            f"NAVEX Case #: {case}"
        )

        output.setPlainText(final_message)

    def on_send():
        narrative = output.toPlainText().strip()
        if not narrative:
            return QMessageBox.warning(widget, "Missing Text", "Please generate the message first.")

        subject_type = subject_type_combo.currentText()
        recipients = load_navex_recipients(region_combo.currentText(), parent_widget=widget)

        html = get_filled_html(
            narrative,
            category=subject_type,
            company=region_combo.currentText(),
            manager_name=recipients["bps_manager"]
        )

        outlook = win32com.client.Dispatch("Outlook.Application")
        mail = outlook.CreateItem(0)
        mail.Subject = f"Navex SITREP | {subject_type}"
        mail.To = recipients["to"]
        mail.CC = recipients["cc"]
        mail.BCC = recipients["bcc"]
        mail.HTMLBody = html

        file_path, _ = QFileDialog.getOpenFileName(widget, "Attach NAVEX Report")
        if file_path:
            mail.Attachments.Add(file_path)

        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.normpath(os.path.join(current_dir, "..", "images", "image001.png"))

        if os.path.exists(image_path):
            attachment = mail.Attachments.Add(image_path)
            attachment.PropertyAccessor.SetProperty(
                "http://schemas.microsoft.com/mapi/proptag/0x3712001F", "rsoc_logo"
            )
        else:
            QMessageBox.warning(
                "Missing Logo",
                f"Logo image not found at:\n{image_path}"
            )

        mail.Display()

    generate_btn.clicked.connect(on_generate)
    send_btn.clicked.connect(on_send)

    widget.setMinimumSize(1100,620)

    return widget


def prompt_region_selection(parent=None) -> str:
    from PySide6.QtWidgets import QDialog, QGridLayout, QPushButton

    dlg = QDialog()
    dlg.setWindowTitle("Select NAVEX Region")
    dlg.setModal(True)
    dlg.setMinimumSize(600, 300)

    layout = QGridLayout(dlg)
    regions = [
        "US & Canada", "Mexico & Costa Rica", "Brazil",
        "Europe", "China", "India", "Penang / Southeast Asia"
    ]

    selected = {"region": None}

    def make_btn(region_name):
        btn = QPushButton(region_name)
        btn.setMinimumSize(160, 40)
        btn.clicked.connect(lambda: confirm_region(region_name))
        return btn

    def confirm_region(region_name):
        confirm = QMessageBox.question(
            dlg,
            "Confirm Region",
            f"Are you sure you selected the correct region?\n\nRegion: {region_name}"
        )
        if confirm == QMessageBox.Yes:
            selected["region"] = region_name
            dlg.accept()
            if parent and hasattr(parent, "resize_with_animation"):
                parent.resize_with_animation(1400, 620)

    for i, region in enumerate(regions):
        layout.addWidget(make_btn(region), i // 3, i % 3)

    dlg.setLayout(layout)
    dlg.exec()
    return selected["region"]
