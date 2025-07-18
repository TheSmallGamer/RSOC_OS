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
    QLineEdit, QMessageBox, QWidget, QVBoxLayout, QPushButton, QLabel,
    QStackedLayout, QHBoxLayout, QFileDialog, QComboBox,
    QTimeEdit, QCheckBox, QGroupBox, QFormLayout
)
from PySide6.QtCore import QDate, Qt, QTime
from lib.outlook_helper import create_outlook_email, create_email_with_embedded_image #type: ignore
import json
import os
from datetime import datetime, timedelta

def load_recipients():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "..", "config", "recipients.json")
    with open(os.path.normpath(config_path), "r") as f:
        return json.load(f)

def get_email_formats_widget():
    return EmailFormatsWidget()

class EmailFormatsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.recipients = load_recipients()
        self.layout = QVBoxLayout(self)
        self.stack = QStackedLayout()
        self.layout.addLayout(self.stack)

        self.init_main_menu()

    def clear_stack(self):
        while self.stack.count():
            widget = self.stack.widget(0)
            self.stack.removeWidget(widget)
            widget.deleteLater()

    def init_main_menu(self):
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)

        title = QLabel ("Email Formats")
        title.setObjectName("SitrepTitle")
        layout.addWidget(title)

        buttons = {
            "Post Trackers": self.show_post_tracker_shifts,
            "Gate Communication": self.show_gate_options,
            "Passdown Formats": self.show_passdown_shifts
        }

        for label, func in buttons.items():
            btn = QPushButton(label)
            btn.clicked.connect(func)
            layout.addWidget(btn)

        self.stack.addWidget(main_widget)

    def go_back_to_main_menu(self):
        self.clear_stack()
        self.init_main_menu()

    def show_post_tracker_shifts(self):
        self._shift_selector("Select Shift for Post Tracker", self.send_post_tracker_email)

    def show_passdown_shifts(self):
        self._shift_selector("Select Shift for Passdown Format", self.send_passdown_email)

    def _shift_selector(self, title, callback):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        label = QLabel(title)
        label.setObjectName("SitrepTitle")
        layout.addWidget(label)

        for shift in ["First Shift", "Second Shift", "Third Shift"]:
            btn = QPushButton(shift)
            btn.clicked.connect(lambda _, s=shift: callback(s))
            layout.addWidget(btn)

        back = QPushButton("Back")
        back.clicked.connect(self.go_back_to_main_menu)
        layout.addWidget(back)

        self.clear_stack()
        self.stack.addWidget(widget)

    def show_gate_options(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        label = QLabel("Gate Communication Type")
        label.setObjectName("SitrepTitle")
        layout.addWidget(label)
        for label in ["Gates Opened", "Gates Closed"]:
            btn = QPushButton(label)
            btn.clicked.connect(lambda _, l=label: self.show_gate_form(l))
            layout.addWidget(btn)

        back = QPushButton("Back")
        back.clicked.connect(self.go_back_to_main_menu)
        layout.addWidget(back)

        self.clear_stack()
        self.stack.addWidget(widget)

    def show_gate_form(self, gate_status):
        widget = QWidget()
        layout = QFormLayout(widget)

        title_box = QComboBox()
        title_box.addItems([
            "Security Professional",
            "Vehicle Patrol Officer",
            "Floor Supervisor"
        ])
        name_input = QLineEdit()

        time_box = QTimeEdit()
        time_box.setTime(QTime.currentTime())

        gates_group = QGroupBox("Broken/Malfunctioning Gates")
        gates_layout = QVBoxLayout()
        gate_checks = []
        for gate in ["D Dock", "G Dock", "J Dock", "Q Dock"]:
            cb = QCheckBox(gate)
            gates_layout.addWidget(cb)
            gate_checks.append(cb)
        gates_group.setLayout(gates_layout)

        send = QPushButton("Generate Email")
        send.clicked.connect(lambda: self.generate_gate_email(
            gate_status, title_box, name_input, time_box, gate_checks
        ))

        back = QPushButton("Back")
        back.clicked.connect(self.show_gate_options)

        layout.addRow("Officer Title:", title_box)
        layout.addRow("Officer Name:", name_input)
        layout.addRow("Time:", time_box)
        layout.addRow(gates_group)
        layout.addRow(send)
        layout.addRow(back)

        self.clear_stack()
        self.stack.addWidget(widget)

    def send_post_tracker_email(self, shift):
        shift_key = shift.lower().split()[0]  # "first", "second", or "third"

        if shift_key in ["first", "second"]:
            template_filename = "post_tracker_firstandsecond.html"
        else:
            template_filename = "post_tracker_third.html"

        path = os.path.normpath(os.path.join("config", template_filename))

        if not os.path.exists(path):
            QMessageBox.warning(self, "Missing Template", f"Template not found:\n{path}")
            return

        with open(path, "r", encoding="cp1252") as f:
            html_body = f.read().replace("cid:LOGO_CID", "cid:flexlogo")

        # Modify shift-specific content if needed
        if shift_key == "second":
            html_body = html_body.replace("0600-1400", "1400-2200")

        # Resolve recipients
        def resolve_roles(role_list, roles_dict):
            emails = []
            for role in role_list:
                entry = roles_dict.get(role, role)
                if isinstance(entry, list):
                    emails.extend(entry)
                else:
                    emails.append(entry)
            return emails

        roles = self.recipients.get("roles", {})
        post_config = self.recipients.get("post_trackers", {})
        to_emails = resolve_roles(post_config.get("to", []), roles)
        cc_emails = resolve_roles(post_config.get("cc", []), roles)
        bcc_emails = resolve_roles(post_config.get("bcc", []), roles)

        logo_path = os.path.abspath("images/flexlogo.png")
        create_email_with_embedded_image(
            subject=f"{shift} Post Tracker - {datetime.now().strftime('%m/%d/%Y')}",
            html_body=html_body,
            to=to_emails,
            cc=cc_emails,
            bcc=bcc_emails,
            image_path=logo_path,
            image_cid="flexlogo"
        )

    def generate_gate_email(self, gate_status, title_box, name_input, time_input, dock_buttons):
        officer_title = title_box.currentText()
        officer_name = name_input.text().strip()
        selected_time = time_input.time().toString("hh:mm AP")
        malfunctioning = [cb.text() for cb in dock_buttons if cb.isChecked()]

        if not officer_name:
            QMessageBox.warning(self, "Missing Info", "Please enter the officer's name.")
            return

        from datetime import datetime

        now_hour = datetime.now().hour
        if now_hour < 12:
            current_greeting = "Good morning"
        elif now_hour < 17:
            current_greeting = "Good afternoon"
        else:
            current_greeting = "Good evening"

        selected_hour = time_input.time().hour()
        if selected_hour < 12:
            selected_time_of_day = "morning"
        elif selected_hour < 17:
            selected_time_of_day = "afternoon"
        else:
            selected_time_of_day = "evening"

        date_str = QDate.currentDate().toString("MM/dd/yyyy")
        subject = f"Truck Gate Communication - {date_str}"

        # Format gate list with Oxford comma
        if len(malfunctioning) > 1:
            gate_list = ", ".join(malfunctioning[:-1]) + f", and {malfunctioning[-1]}"
        else:
            gate_list = malfunctioning[0] if malfunctioning else ""

        # Determine the message body content
        if len(malfunctioning) == 4:
            status_line = (
                f"that none of the truck gates were closed and locked successfully "
                f"due to preexisting damage or malfunctions. RSOC personnel will continue to monitor "
                f"these entrances throughout the malfunction period and report any unusual activity or attempted access."
            )
        elif malfunctioning:
            status_line = (
                f"that the truck gates were closed and locked successfully, with the exception of {gate_list} "
                f"due to preexisting damage or a malfunction. RSOC personnel will continue to monitor these entrances "
                f"during the malfunction period and report any unusual activity or attempted access."
            )
        else:
            status_line = (
                "that the truck gates were closed and locked successfully."
            )

        html_body = f"""
        <p>{current_greeting},</p>
        <p>At {selected_time} CT this {selected_time_of_day}, the RSOC received confirmation from {officer_title} {officer_name} {status_line}</p>
        <p>If you have any questions, or require any further information, feel free to reach out to the RSOC with any inquiries you may have.</p>
        """

        def resolve_roles(role_list, roles_dict):
            emails = []
            for role in role_list:
                entry = roles_dict.get(role, role)
                if isinstance(entry, list):
                    emails.extend(entry)
                else:
                    emails.append(entry)
            return emails

        roles = self.recipients.get("roles", {})
        gc = self.recipients.get("gate_communication", {})
        to_emails = resolve_roles(gc.get("to", []), roles)
        cc_emails = resolve_roles(gc.get("cc", []), roles)

        create_outlook_email(subject=subject, html_body=html_body, to=to_emails, cc=cc_emails)

    def send_passdown_email(self, shift):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Documents (*.pdf *.docx *.doc)")
        file_dialog.setFileMode(QFileDialog.ExistingFile)

        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if not selected_files:
                return

            filepath = selected_files[0]

            # Greeting logic
            now_hour = datetime.now().hour
            if now_hour < 12:
                greeting = "Good morning,"
            elif now_hour < 17:
                greeting = "Good afternoon,"
            else:
                greeting = "Good evening,"

            html_body = f"""
            <p>{greeting}</p>
            <p>Attached is the most recently updated pass-down document. If you have any questions, or require any further information, feel free to reach out to me with any inquiries you may have.</p>
            """

            # Resolve recipients
            def resolve_roles(role_list, roles_dict):
                emails = []
                for role in role_list:
                    entry = roles_dict.get(role, role)
                    if isinstance(entry, list):
                        emails.extend(entry)
                    else:
                        emails.append(entry)
                return emails
            
            now = datetime.now()

            if shift.lower().startswith("third"):
                date_for_subject = (now - timedelta(days=1)).strftime("%m/%d/%Y")
            else:
                date_for_subject = now.strftime("%m/%d/%Y")
            
            shift_proper = shift.title() if shift else "Shift"
            subject = f"{shift_proper} Pass-Down - {date_for_subject}"

            roles = self.recipients.get("roles", {})
            config = self.recipients.get("passdown", {})
            to_emails = resolve_roles(config.get("to", []), roles)
            cc_emails = resolve_roles(config.get("cc", []), roles)

            create_outlook_email(
                subject=subject,
                html_body=html_body,
                to=to_emails,
                cc=cc_emails,
                attachments=[filepath]
            )



