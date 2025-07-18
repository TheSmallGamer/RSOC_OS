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

# === UNCHANGED IMPORTS AND JSON LOADERS ===
import json
import os
import subprocess
import time
from PySide6.QtGui import QMovie
from PySide6.QtWidgets import (
    QApplication, QDialog, QFrame, QInputDialog, QMessageBox, QWidget, QLabel, QLineEdit, QComboBox, QTimeEdit, QTextEdit,
    QVBoxLayout, QHBoxLayout, QRadioButton, QPushButton, QGridLayout,
    QSizePolicy
)
from PySide6.QtCore import Qt, QTime, QThread, Signal, QObject
from lib.sitrep_outlook_helper import send_sitrep_to_outlook # type: ignore
from lib.llm_narrative import generate_narrative_from_summary # type: ignore


class NarrativeWorker(QObject):
    finished = Signal(str)

    def __init__(self, summary):
        super().__init__()
        self.summary = summary

    def run(self):
        from lib.llm_narrative import generate_narrative_from_summary  # type: ignore # Local import to avoid thread issues
        result = generate_narrative_from_summary(self.summary)
        self.finished.emit(result)

class LoadingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Please be patient...")
        self.setModal(True)  # Proper modal behavior
        self.setFixedSize(250, 70)
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)

        layout = QVBoxLayout()
        label = QLabel("Message generating, please be patient...")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        self.setLayout(layout)

def load_company_list():
    default_companies = ["Flex", "RSOC", "VOLT", "Other"]
    filepath = "./config/companies.json"

    if not os.path.exists(filepath):
        os.makedirs("./config", exist_ok=True)
        with open(filepath, "w") as f:
            json.dump({"companies": default_companies}, f, indent=4)
        return default_companies

    with open(filepath, "r") as f:
        data = json.load(f)
        return data.get("companies", default_companies)
    
def load_recipient_list():
    filepath = "./config/recipients.json"
    if not os.path.exists(filepath):
        os.makedirs("./config", exist_ok=True)
        # Create default file if missing
        default_data = {
            "Flex": {"to": "flex.security@company.com", "cc": "rsoc@company.com"},
            "SolarEdge": {"to": "solaredge.security@company.com", "cc": "rsoc@company.com"},
            "RSOC": {"to": "rsoc@company.com", "cc": ""},
            "Default": {"to": "rsoc@company.com", "cc": ""}
        }
        with open(filepath, "w") as f:
            json.dump(default_data, f, indent=4)
        return default_data

    with open(filepath, "r") as f:
        data = json.load(f)
        return data


def load_symptom_list():
    default_symptoms = [
        "High Blood Pressure",
        "Chest Pain",
        "Shortness of Breath",
        "Allergic Reaction",
        "Fainting",
        "Other"
    ]
    filepath = "./config/symptoms.json"

    if not os.path.exists(filepath):
        os.makedirs("./config", exist_ok=True)
        with open(filepath, "w") as f:
            json.dump({"symptoms": default_symptoms}, f, indent=4)
        return default_symptoms

    with open(filepath, "r") as f:
        data = json.load(f)
        return data.get("symptoms", default_symptoms)

def get_medical_sitrep_widget(parent=None):
    widget = QWidget()
    widget.outcome_inputs = {}  # ← PRE-INIT TO AVOID MISSING KEY ERRORS

    recipient_list = load_recipient_list()

    layout = QHBoxLayout()
    form_layout = QGridLayout()
    form_layout.setSpacing(8)
    row = 0

    form_layout.addWidget(QLabel("Initial Call Time:"), row, 0)
    call_time_input = QTimeEdit()
    call_time_input.setTime(QTime.currentTime())
    form_layout.addWidget(call_time_input, row, 1)
    form_layout.addWidget(QLabel("Time Zone:"), row, 2)
    timezone_input = QComboBox()
    timezone_input.addItems(["CST", "EST", "PST", "MST"])
    form_layout.addWidget(timezone_input, row, 3)

    row += 1
    companies = load_company_list()

    company_input = QComboBox()
    company_input.addItems(companies)
    form_layout.addWidget(company_input, row, 0)
    form_layout.addWidget(QLabel("Reporting Employee:"), row, 1)
    reporting_input = QLineEdit()
    reporting_input.setPlaceholderText("e.g. John Doe (12345678)")
    form_layout.addWidget(reporting_input, row, 2, 1, 2)

    row += 1
    patient_company_input = QComboBox()
    patient_company_input.addItems(companies)
    form_layout.addWidget(patient_company_input, row, 0)
    form_layout.addWidget(QLabel("Patient Name:"), row, 1)
    patient_input = QLineEdit()
    patient_input.setPlaceholderText("e.g. Jane Doe (C1234567)")
    form_layout.addWidget(patient_input, row, 2, 1, 2)

    row += 1
    form_layout.addWidget(QLabel("Describe Symptom(s):"), row, 0)
    symptom_input = QLineEdit()
    symptom_input.setPlaceholderText("e.g. high blood pressure, chest pain, etc.")
    form_layout.addWidget(symptom_input, row, 1, 1, 3)

    row += 1
    mod_input = QComboBox()
    mod_input.addItems([chr(c) for c in range(ord('A'), ord('T'))])
    mod_input.setFixedWidth(50)
    form_layout.addWidget(QLabel("Mod:"), row, 0)
    form_layout.addWidget(mod_input, row, 1)

    column_input = QLineEdit()
    column_input.setFixedWidth(50)
    form_layout.addWidget(QLabel("Column:"), row, 2)
    form_layout.addWidget(column_input, row, 3)

    row += 1
    ert_time_input = QTimeEdit()
    ert_time_input.setTime(QTime.currentTime())
    form_layout.addWidget(QLabel("Time ERT Called:"), row, 0)
    form_layout.addWidget(ert_time_input, row, 1)

    row += 1
    responder_input = QLineEdit()
    responder_input.setPlaceholderText("e.g. Zachary Barba and Serena Burns")
    form_layout.addWidget(QLabel("Responding ERT Member(s):"), row, 0)
    form_layout.addWidget(responder_input, row, 1, 1, 3)

    row += 1
    separator = QFrame()
    separator.setFrameShape(QFrame.HLine)
    separator.setFrameShadow(QFrame.Sunken)
    form_layout.addWidget(separator, row, 0, 1, 4)

    row += 1
    staying_radio = QRadioButton("Staying at Work")
    going_radio = QRadioButton("Going Home")
    ems_radio = QRadioButton("EMS Responded")
    form_layout.addWidget(staying_radio, row, 0)
    form_layout.addWidget(going_radio, row, 1)
    form_layout.addWidget(ems_radio, row, 2)

    outcome_dynamic = QVBoxLayout()
    outcome_dynamic.setAlignment(Qt.AlignTop)
    outcome_widget = QWidget()
    outcome_widget.setLayout(outcome_dynamic)
    form_layout.addWidget(outcome_widget, row + 1, 0, 1, 4)

    row += 2
    generate_btn = QPushButton("Generate")
    copy_btn = QPushButton("Copy to Outlook")
    form_layout.addWidget(generate_btn, row, 0, 1, 2)
    form_layout.addWidget(copy_btn, row, 2, 1, 2)

    output_display = QTextEdit()
    output_display.setPlaceholderText("Generated Message Body")
    layout.addLayout(form_layout, 2)
    layout.addWidget(output_display, 3)
    widget.setLayout(layout)

    def clear_outcome_fields():
        while outcome_dynamic.count():
            item = outcome_dynamic.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                while item.layout().count():
                    child = item.layout().takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()
                item.layout().deleteLater()  # <- Add this line
        widget.outcome_inputs.clear()

    def handle_radio_selection():
        clear_outcome_fields()

        if ems_radio.isChecked():
            widget.outcome_inputs["outcome_type"] = "EMS Responded"

            top_row = QHBoxLayout()
            ems_contacted = QTimeEdit()
            ems_arrival = QTimeEdit()
            unit_number = QLineEdit()
            top_row.addWidget(QLabel("911 Contacted:")); top_row.addWidget(ems_contacted)
            top_row.addWidget(QLabel("EMS Arrival:")); top_row.addWidget(ems_arrival)
            top_row.addWidget(QLabel("Unit Number:")); top_row.addWidget(unit_number)
            outcome_dynamic.addLayout(top_row)

            widget.outcome_inputs.update({
                "ems_contacted": ems_contacted,
                "ems_arrival": ems_arrival,
                "unit_number": unit_number
            })

            amb_row = QHBoxLayout()
            amb_btn = QPushButton("Brought to Ambulance")
            amb_btn.setStyleSheet("font-size: 10pt; padding: 2px 6px;")
            amb_label = QLabel("Arrived at Ambulance:")
            amb_time = QTimeEdit()
            amb_label.hide()
            amb_time.hide()

            # Default state
            widget.outcome_inputs["Brought to Ambulance"] = "No"

            def toggle_amb():
                toggled = not amb_label.isVisible()
                amb_label.setVisible(toggled)
                amb_time.setVisible(toggled)
                widget.outcome_inputs["Brought to Ambulance"] = "Yes" if toggled else "No"

            amb_btn.clicked.connect(toggle_amb)

            amb_row.addWidget(amb_btn)
            amb_row.addWidget(amb_label)
            amb_row.addWidget(amb_time)
            amb_row.addStretch()

            widget.outcome_inputs["amb_time"] = amb_time
            outcome_dynamic.addLayout(amb_row)

            hospital_row = QHBoxLayout()
            hosp_toggle = QPushButton("Going to Hospital")
            hosp_toggle.setStyleSheet("font-size: 10pt; padding: 2px 6px;")
            hosp_name = QLineEdit(); hosp_name.hide()
            hosp_name.setPlaceholderText("e.g. Seton Northwest Hospital")
            alt_combo = QComboBox(); alt_combo.addItems(["Employee Going Home", "Employee Return to Work"]); alt_combo.hide()
            hospital_row.addWidget(hosp_toggle); hospital_row.addWidget(hosp_name); hospital_row.addWidget(alt_combo)
            outcome_dynamic.addLayout(hospital_row)
            widget.outcome_inputs.update({
                "hosp_toggle": hosp_toggle,
                "Hospital Name": hosp_name,
                "Post Eval Option": alt_combo
            })

            final_row = QHBoxLayout()
            final_left_label = QLabel("Left Site Time:")
            final_left_time = QTimeEdit()
            final_clear_label = QLabel("All Clear Time:")
            final_clear_time = QTimeEdit()
            final_row.addWidget(final_left_label); final_row.addWidget(final_left_time)
            final_row.addWidget(final_clear_label); final_row.addWidget(final_clear_time)
            outcome_dynamic.addLayout(final_row)

            widget.outcome_inputs.update({
                "final_left_label": final_left_label,
                "Final Left Time": final_left_time,
                "final_clear_time": final_clear_time
            })

            def update_final_row_visibility():
                if hosp_toggle.text() == "No Hospital Ride" and alt_combo.currentText() == "Employee Return to Work":
                    final_left_label.hide(); final_left_time.hide()
                else:
                    final_left_label.show(); final_left_time.show()
                final_clear_label.show(); final_clear_time.show()

            def toggle_hospital():
                if hosp_toggle.text() == "No Hospital Ride":
                    hosp_toggle.setText("Going to Hospital")
                    hosp_name.show(); alt_combo.hide()
                    widget.outcome_inputs["Hospital Transport"] = "Yes"
                else:
                    hosp_toggle.setText("No Hospital Ride")
                    hosp_name.hide(); alt_combo.show()
                    widget.outcome_inputs["Hospital Transport"] = "No"
                update_final_row_visibility()

            hosp_toggle.clicked.connect(toggle_hospital)
            alt_combo.currentTextChanged.connect(update_final_row_visibility)
            toggle_hospital()

        elif staying_radio.isChecked():
            clear_time = QTimeEdit()
            row = QHBoxLayout(); row.addWidget(QLabel("All Clear Time:")); row.addWidget(clear_time)
            outcome_dynamic.addLayout(row)
            widget.outcome_inputs.update({
                "outcome_type": "Staying at Work",
                "all_clear_time": clear_time
            })

        elif going_radio.isChecked():
            left_site = QTimeEdit()
            clear_time = QTimeEdit()
            r1 = QHBoxLayout(); r1.addWidget(QLabel("Left Site Time:")); r1.addWidget(left_site)
            r2 = QHBoxLayout(); r2.addWidget(QLabel("All Clear Time:")); r2.addWidget(clear_time)
            outcome_dynamic.addLayout(r1); outcome_dynamic.addLayout(r2)
            widget.outcome_inputs.update({
                "outcome_type": "Going Home",
                "left_site_time": left_site,
                "all_clear_time": clear_time
            })

    staying_radio.toggled.connect(handle_radio_selection)
    going_radio.toggled.connect(handle_radio_selection)
    ems_radio.toggled.connect(handle_radio_selection)

    def on_generate_clicked():
        if not reporting_input.text().strip():
            QMessageBox.warning(widget, "Missing Info", "Please fill in Reporting Employee name."); return
        if not patient_input.text().strip():
            QMessageBox.warning(widget, "Missing Info", "Please fill in Patient Name."); return
        if not column_input.text().strip():
            QMessageBox.warning(widget, "Missing Info", "Please fill in Column"); return
        if not responder_input.text().strip():
            QMessageBox.warning(widget, "Missing Info", "Please fill in Responding ERT Member(s)"); return
        if not any([staying_radio.isChecked(), going_radio.isChecked(), ems_radio.isChecked()]):
            QMessageBox.warning(widget, "Missing Info", "Please select an Outcome option"); return

        if ems_radio.isChecked():
            unit_input = widget.outcome_inputs.get("unit_number")
            if not unit_input or not unit_input.text().strip():
                QMessageBox.warning(widget, "Missing Info", "Please enter Unit Number")
                return
            if widget.outcome_inputs.get("hosp_toggle").text() == "Going to Hospital":
                if not widget.outcome_inputs.get("Hospital Name").text().strip():
                    QMessageBox.warning(widget, "Missing Info", "Please enter Hospital Name"); return

        summary_parts = [
            f"Initial Call Time: {call_time_input.time().toString('HH:mm')} {timezone_input.currentText()}",
            f"Reported by {reporting_input.text().strip()} from {company_input.currentText()}",
            f"Patient: {patient_input.text().strip()} ({patient_company_input.currentText()})",
            f"Mod: {mod_input.currentText()}, Column: {column_input.text().strip()}",
            f"ERT Called at: {ert_time_input.time().toString('HH:mm')}",
            f"Responding ERT Member(s): {responder_input.text().strip()}",
        ]

        symptom = symptom_input.text().strip()
        if not symptom:
            QMessageBox.warning(widget, "Missing Info", "Please enter the symptom(s) observed.")
            return
        summary_parts.append(f"Symptom: {symptom}")

        ems_details = []
        if ems_radio.isChecked():
            ems_details.append("outcome_type: EMS Responded")
            ems_details.append(f"ems_contacted: {widget.outcome_inputs['ems_contacted'].time().toString('HH:mm')}")
            ems_details.append(f"ems_arrival: {widget.outcome_inputs['ems_arrival'].time().toString('HH:mm')}")
            ems_details.append(f"unit_number: {widget.outcome_inputs['unit_number'].text().strip()}")

            bta = widget.outcome_inputs.get("Brought to Ambulance", "No")
            ems_details.append(f"Brought to Ambulance: {bta}")
            if bta == "Yes":
                amb_time = widget.outcome_inputs.get("amb_time")
                if amb_time:
                    ems_details.append(f"Arrived at Ambulance: {amb_time.time().toString('HH:mm')}")

            hospital_transport = widget.outcome_inputs.get("Hospital Transport", "No")
            ambulance_outcome = "GOING TO HOSPITAL" if hospital_transport == "Yes" else "NO HOSPITAL RIDE"
            ems_details.append(f"Ambulance Outcome: {ambulance_outcome}")

            if hospital_transport == "Yes":
                hospital_name_input = widget.outcome_inputs.get("Hospital Name")
                if hospital_name_input:
                    ems_details.append(f"Hospital Name: {hospital_name_input.text().strip()}")
                left_time = widget.outcome_inputs.get("Final Left Time")
                clear_time = widget.outcome_inputs.get("final_clear_time")
                if left_time:
                    ems_details.append(f"Left Site Time: {left_time.time().toString('HH:mm')}")
                if clear_time:
                    ems_details.append(f"All Clear Time: {clear_time.time().toString('HH:mm')}")
            else:
                post_eval_combo = widget.outcome_inputs.get("Post Eval Option")
                if post_eval_combo:
                    post_eval_value = post_eval_combo.currentText()
                    ems_details.append(f"Post Eval Outcome: {post_eval_value}")
                    if post_eval_value == "Employee Return to Work":
                        clear_time = widget.outcome_inputs.get("final_clear_time")
                        if clear_time:
                            ems_details.append(f"All Clear Time: {clear_time.time().toString('HH:mm')}")
                    elif post_eval_value == "Employee Going Home":
                        left_time = widget.outcome_inputs.get("Final Left Time")
                        clear_time = widget.outcome_inputs.get("final_clear_time")
                        if left_time:
                            ems_details.append(f"Left Site Time: {left_time.time().toString('HH:mm')}")
                        if clear_time:
                            ems_details.append(f"All Clear Time: {clear_time.time().toString('HH:mm')}")
        else:
            outcome_type = widget.outcome_inputs.get("outcome_type", "Unknown")
            ems_details.append(f"outcome_type: {outcome_type}")
            if outcome_type == "Staying at Work":
                clear_time = widget.outcome_inputs.get("all_clear_time")
                if clear_time:
                    ems_details.append(f"All Clear Time: {clear_time.time().toString('HH:mm')}")
            elif outcome_type == "Going Home":
                left_time = widget.outcome_inputs.get("left_site_time")
                clear_time = widget.outcome_inputs.get("all_clear_time")
                if left_time:
                    ems_details.append(f"Left Site Time: {left_time.time().toString('HH:mm')}")
                if clear_time:
                    ems_details.append(f"All Clear Time: {clear_time.time().toString('HH:mm')}")



        # Final output
        summary_text = "\n".join(summary_parts) + "\n\n" + "\n".join(ems_details)

        # Show blocking message box
        loading_dialog = LoadingDialog(widget)
        loading_dialog.show()
        QApplication.processEvents()  # allow the dialog to render before blocking

        # 🔄 Start Ollama process
        ollama_proc = subprocess.Popen(["ollama", "serve"])
        time.sleep(2)

        # 🧠 Generate narrative
        narrative = generate_narrative_from_summary(summary_text)

        # ✅ Stop Ollama
        ollama_proc.terminate()
        loading_dialog.close()

        # Display result
        output_display.setText(narrative)

    def on_copy_to_outlook_clicked():
        narrative = output_display.toPlainText().strip()
        if not narrative:
            QMessageBox.warning(widget, "No Message", "Generate a narrative before sending to Outlook.")
            return

        patient_company = patient_company_input.currentText()

        send_sitrep_to_outlook(
            summary_html=narrative,
            sitrep_type="Medical",
            patient_company=patient_company,
            ask_attachment=False,
            parent_widget=widget
        )

    generate_btn.clicked.connect(on_generate_clicked)
    copy_btn.clicked.connect(on_copy_to_outlook_clicked)
    return widget
