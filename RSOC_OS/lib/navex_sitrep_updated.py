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
    QLabel, QWidget, QVBoxLayout, QGridLayout, QPushButton,
    QMessageBox, QStackedLayout
)
from lib.navex_sitrep import get_navex_sitrep_widget  # type: ignore # This is your original form generator

def get_navex_sitrep_main_widget():
    container = QWidget()
    layout = QStackedLayout()
    container.setLayout(layout)

    def on_region_selected(region_name):
        confirm = QMessageBox.question(
            container,
            "Confirm Region",
            f"Are you sure you selected the correct region?\n\nYou selected: {region_name}",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            sitrep_form = get_navex_sitrep_widget(region_name)
            layout.addWidget(sitrep_form)
            layout.setCurrentWidget(sitrep_form)

    region_selector = build_region_selector(on_region_selected)
    layout.addWidget(region_selector)

    return container

def build_region_selector(callback):
    regions = [
        "US and Canada", "Mexico and Costa Rica", "Brazil",
        "Europe", "China", "India", "Penang / Southeast Asia"
    ]

    grid = QGridLayout()
    buttons = []

    for index, region in enumerate(regions):
        button = QPushButton(region)
        button.clicked.connect(lambda _, r=region: callback(r))
        buttons.append(button)
        row, col = divmod(index, 3)
        grid.addWidget(button, row, col)

    wrapper = QWidget()
    layout = QVBoxLayout(wrapper)
    layout.addWidget(QLabel("BEFORE CONTINUING -\n\nPlease determine the region in which the NAVEX report originated from before selecting a button option. \nSelecting the incorrect region option will open the wrong Outlook format addressed to the wrong recipients."))  # Optional: disable this button or convert to QLabel
    layout.addLayout(grid)

    return wrapper
