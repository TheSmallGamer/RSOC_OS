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
import getpass
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QTabWidget, QScrollArea, QGridLayout, QMessageBox,
    QStackedWidget, QComboBox, QHBoxLayout
)
from PySide6.QtCore import Qt

USERNAME = getpass.getuser()
RSOC_BASE = os.path.join("C:/Users", USERNAME, "Box", "RSOC")

def get_documents_widget():
    widget = QWidget()
    layout = QVBoxLayout(widget)

    title = QLabel("Documents & Printables")
    title.setObjectName("SitrepTitle")
    layout.addWidget(title)

    tab_widget = QTabWidget()
    tab_widget.addTab(create_documents_tab(), "Documents")
    tab_widget.addTab(create_printables_tab(), "Printables")

    layout.addWidget(tab_widget)
    return widget

def create_documents_tab():
    stacked_layout = QStackedWidget()

    # --- Main Documents View ---
    documents_main_widget = QWidget()
    grid_layout = QGridLayout(documents_main_widget)
    grid_layout.setAlignment(Qt.AlignTop)

    buttons = {
        "Badge Reader Map": os.path.join(RSOC_BASE, "Site Files", "AUR - Austin", "Reader Maps"),
        "Site CMT Contact List": os.path.join(RSOC_BASE, "Site Files", "North America Region Site CMT Contact List - June 2024.xlsx"),
        "Proxce Map": os.path.join(RSOC_BASE, "Site Files", "AUR - Austin", "Proxce Map locations"),
        "Proxce Contact List": os.path.join(RSOC_BASE, "Documents", "Proxce Contact List - 02.09.24.xlsx"),
        "Quick Reaction Cards": os.path.join(RSOC_BASE, "Documents", "Regional QRC VE APR 2019 (ARNE).pdf"),
    }

    row, col = 0, 0
    for label, path in buttons.items():
        button = QPushButton(label)
        button.setObjectName("QPushButton")
        if label == "Site Files":
            button.clicked.connect(lambda: stacked_layout.setCurrentIndex(1))
        else:
            button.clicked.connect(lambda _, p=path: open_path(p))
        grid_layout.addWidget(button, row, col)
        col += 1
        if col == 3:
            col = 0
            row += 1

    # Stack both views
    stacked_layout.addWidget(documents_main_widget)

    container = QWidget()
    container_layout = QVBoxLayout(container)
    container_layout.setContentsMargins(0, 0, 0, 0)
    container_layout.addWidget(stacked_layout)
    return container

def create_printables_tab():
    base_path = os.path.join(RSOC_BASE, "Documents")
    printable_files = {
        "Key Control Log": os.path.join(base_path, "KeyControlLogMasterTemplate.xlsx"),
        "Statement Report": os.path.join(base_path, "Statement Report - blank.pdf"),
        "Time Off Request": os.path.join(base_path, "Admin", "Admin Information", "Forms", "Time-Off Request Form.pdf"),
        "Incident Report": os.path.join(base_path, "Admin", "Admin Information", "Forms", "AUS Incident Report Form.pdf"),
        "Camera Pass Request": os.path.join(base_path, "Admin", "Admin Information", "Forms", "Camera Pass Request Form.docx"),
        "Direct Deposit Form": os.path.join(base_path, "Admin", "Admin Information", "Forms", "Direct Deposit Processing Form.xlsx"),
        "Disciplinary Notice": os.path.join(base_path, "Admin", "Admin Information", "Forms", "Disciplinary Notice Form.pdf"),
        "Hallmark Exemption ID Request": os.path.join(base_path, "Admin", "Admin Information", "Forms", "Hallmark Exemption ID Request Form.docx"),
        "Security Statement": os.path.join(base_path, "Admin", "Admin Information", "Forms", "Security Statement of Understanding.pdf"),
        "Shift Swap Request": os.path.join(base_path, "Admin", "Admin Information", "Forms", "Shift Swap Form.xlsx"),
        "Payroll Deduction Agreement": os.path.join(base_path, "Admin", "Admin Information", "Forms", "Payroll Deduction.xlsx"),
    }

    tab = QWidget()
    layout = QVBoxLayout(tab)

    label = QLabel("Select a printable form:")
    layout.addWidget(label)

    dropdown = QComboBox()
    dropdown.addItems(printable_files.keys())
    layout.addWidget(dropdown)

    go_button = QPushButton("GO")
    go_button.setObjectName("QPushButton")
    layout.addWidget(go_button)

    def open_selected_document():
        selection = dropdown.currentText()
        filepath = printable_files.get(selection)
        if filepath and os.path.exists(filepath):
            os.startfile(filepath)
        else:
            QMessageBox.warning(tab, "File Error", f"File not found:\n{filepath}")

    go_button.clicked.connect(open_selected_document)

    return tab

def open_path(path):
    if os.path.exists(path):
        os.startfile(path)
    else:
        QMessageBox.warning(None, "File Not Found", f"Cannot find:\n{path}")
