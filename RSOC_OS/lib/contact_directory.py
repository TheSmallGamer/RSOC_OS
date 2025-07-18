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
from PySide6.QtGui import QAction
import pandas as pd  # type: ignore
from PySide6.QtWidgets import (
    QDateEdit, QDialog, QFormLayout, QHBoxLayout, QLineEdit, QMenu, QPushButton, QWidget, QVBoxLayout, QLabel,
    QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import QDate, Qt

CONFIG_PATH = os.path.join("config", "contact_config.json")

def get_contact_file_path():
    """Retrieve or prompt for the contact Excel file path."""
    if not os.path.exists(CONFIG_PATH):
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)

    if os.path.isfile(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
            contact_path = config.get("contact_file_path")
            if contact_path and os.path.isfile(contact_path):
                return contact_path

    # Prompt user for file
    file_dialog = QFileDialog()
    file_path, _ = file_dialog.getOpenFileName(
        None, "Select Contact Directory Excel File", "", "Excel Files (*.xlsx *.xls)"
    )

    if file_path:
        # Save path to config
        with open(CONFIG_PATH, "w") as f:
            json.dump({"contact_file_path": file_path}, f, indent=4)
        return file_path
    else:
        QMessageBox.critical(None, "File Required", "You must select a contact directory file to proceed.")
        raise FileNotFoundError("Contact directory file not selected.")

class AddContactDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Contact")
        self.setMinimumSize(400, 300)

        self.layout = QVBoxLayout(self)

        self.fields = {
            "First Name": QLineEdit(),
            "Last Name": QLineEdit(),
            "Job Title": QLineEdit(),
            "Company": QLineEdit(),
            "Work Email": QLineEdit(),
            "Personal Email": QLineEdit(),
            "Work Phone": QLineEdit(),
            "Personal Phone": QLineEdit(),
            "Location/Site": QLineEdit(),
            "Birthday": QDateEdit()
        }

        self.fields["Birthday"].setCalendarPopup(True)
        self.fields["Birthday"].setDate(QDate.currentDate())

        for label, widget in self.fields.items():
            row = QHBoxLayout()
            row.addWidget(QLabel(label))
            row.addWidget(widget)
            self.layout.addLayout(row)

        self.save_button = QPushButton("Save Contact")
        self.save_button.clicked.connect(self.accept)
        self.layout.addWidget(self.save_button)

    def get_data(self):
        return {
            label: (
                widget.date().toString("yyyy-MM-dd")
                if isinstance(widget, QDateEdit)
                else widget.text().strip()
            )
            for label, widget in self.fields.items()
        }

class ContactDirectoryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 600)
        self.layout = QVBoxLayout(self)

        self.contact_path = get_contact_file_path()
        self.contacts = pd.read_excel(self.contact_path)
        self.contacts = self.contacts.astype(str).fillna("")

        # === Header Row ===
        header_layout = QHBoxLayout()

        self.title_label = QLabel("Contact Directory")
        self.title_label.setObjectName("SitrepTitle")
        header_layout.addWidget(self.title_label)

        header_layout.addStretch(1)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search contacts...")
        self.search_box.textChanged.connect(self.filter_contacts)
        self.search_box.setFixedWidth(200)
        header_layout.addWidget(self.search_box)

        self.add_button = QPushButton("Add Contact")
        self.add_button.clicked.connect(self.open_add_contact_dialog)
        header_layout.addWidget(self.add_button)

        self.layout.addLayout(header_layout)

        # === Table Widget ===
        self.table = QTableWidget()
        self.layout.addWidget(self.table)
        self.refresh_table()

        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.open_context_menu)
        self.table.setSortingEnabled(True)

    def open_context_menu(self, position):
        item = self.table.itemAt(position)
        if not item:
            return

        row = item.row()
        menu = QMenu()

        display_action = QAction("Display Contact", self)
        edit_action = QAction("Edit Contact", self)
        delete_action = QAction("Delete Contact", self)

        display_action.triggered.connect(lambda: self.display_contact(row))
        edit_action.triggered.connect(lambda: self.edit_contact(row))
        delete_action.triggered.connect(lambda: self.delete_contact(row))

        menu.addAction(display_action)
        menu.addAction(edit_action)
        menu.addAction(delete_action)

        menu.exec(self.table.viewport().mapToGlobal(position))

    def display_contact(self, row):
        contact_info = []
        for col in range(self.table.columnCount()):
            header = self.table.horizontalHeaderItem(col).text()
            value = self.table.item(row, col).text()
            contact_info.append(f"<b>{header}:</b> {value}")
        
        msg = QDialog(self)
        msg.setWindowTitle("Contact Details")
        layout = QVBoxLayout()
        for line in contact_info:
            layout.addWidget(QLabel(line))
        msg.setLayout(layout)
        msg.exec()

    def edit_contact(self, row):
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Contact")
        layout = QFormLayout(dialog)

        fields = [
            "First Name", "Last Name", "Job Title", "Company",
            "Work Email", "Personal Email", "Work Phone",
            "Personal Phone", "Location/Site", "Birthday"
        ]

        edits = []
        for col, field in enumerate(fields):
            current_value = self.table.item(row, col).text()
            edit = QLineEdit(current_value)
            layout.addRow(QLabel(field), edit)
            edits.append(edit)

        save_button = QPushButton("Save")
        layout.addWidget(save_button)

        def save_changes():
            for col, edit in enumerate(edits):
                value = edit.text()
                self.table.setItem(row, col, QTableWidgetItem(value))
                self.contacts.iat[row, col] = str(value) if value else ""
            self.contacts.to_excel(self.contact_path, index=False)
            dialog.accept()

        save_button.clicked.connect(save_changes)
        dialog.setLayout(layout)
        dialog.exec()

    def delete_contact(self, row):
        name = f"{self.table.item(row, 0).text()} {self.table.item(row, 1).text()}"
        confirm = QMessageBox.question(
            self,
            "Delete Contact",
            f"Are you sure you want to delete {name}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            # Remove from Excel DataFrame
            self.contacts.drop(self.contacts.index[row], inplace=True)
            self.contacts.reset_index(drop=True, inplace=True)
            self.contacts.to_excel(self.contact_path, index=False)

            # Remove from GUI
            self.table.removeRow(row)

            QMessageBox.information(self, "Deleted", f"{name} has been removed.")

    def refresh_table(self, filter_text=""):
        
        filtered = self.contacts.copy()
        if filter_text:
            mask = filtered.apply(lambda row: filter_text.lower() in row.astype(str).str.lower().to_string(), axis=1)
            filtered = filtered[mask]

        self.table.clear()
        self.table.setColumnCount(len(filtered.columns))
        self.table.setRowCount(len(filtered))
        headers = [
            "First Name", "Last Name", "Job Title", "Company",
            "Work Email", "Personal Email", "Work Phone", "Personal Phone",
            "Location/Site", "Birthday"
        ]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)

        for row_idx, (_, row) in enumerate(filtered.iterrows()):
            for col_idx, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                self.table.setItem(row_idx, col_idx, item)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def filter_contacts(self, text):
        text = text.strip().lower()
        self.table.setSortingEnabled(False)  # Disable sorting while updating rows
        self.table.setRowCount(0)

        for index, row in self.contacts.iterrows():
            full_name = f"{str(row['First Name'])} {str(row['Last Name'])}".lower()
            if (
                text in str(row['First Name']).lower()
                or text in str(row['Last Name']).lower()
                or text in full_name
            ):
                row_position = self.table.rowCount()
                self.table.insertRow(row_position)
                self.table.setVerticalHeaderItem(row_position, QTableWidgetItem(str(index + 1)))
                for col_index, col in enumerate(self.contacts.columns):
                    value = str(row[col]) if not pd.isna(row[col]) else ""
                    self.table.setItem(row_position, col_index, QTableWidgetItem(value))

        self.table.setSortingEnabled(True)  # Re-enable sorting after rows are added


    def open_add_contact_dialog(self):
        dialog = AddContactDialog(self)
        if dialog.exec():
            new_data = dialog.get_data()

            if not new_data["First Name"] or not new_data["Last Name"]:
                QMessageBox.warning(self, "Missing Info", "First and Last Name are required.")
                return

            self.contacts = pd.concat([self.contacts, pd.DataFrame([new_data])], ignore_index=True)
            self.contacts.to_excel(self.contact_path, index=False)
            self.refresh_table()

def get_contact_directory_widget():
    return ContactDirectoryWidget()
