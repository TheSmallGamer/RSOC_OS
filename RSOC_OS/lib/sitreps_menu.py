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
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QSizePolicy
)
from PySide6.QtCore import Qt
from lib import medical_sitrep # type: ignore
from lib.navex_sitrep_updated import get_navex_sitrep_main_widget # type: ignore
from lib.weather_advisory import get_weather_advisory_widget # type: ignore
from lib.general_sitrep import get_general_sitrep_widget # type: ignore

def get_sitreps_menu_widget(parent=None):
    widget = QWidget()
    layout = QVBoxLayout()

    # ===== Title Bar =====
    title_bar = QHBoxLayout()

    title_label = QLabel("Select SitRep Type")
    title_label.setAlignment(Qt.AlignCenter)
    title_label.setObjectName("SitrepTitle")
    title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    title_bar.addStretch()
    title_bar.addWidget(title_label)
    title_bar.addStretch()

    layout.addLayout(title_bar)

    # ===== Sitrep Buttons =====
    button_names = [
        ("Medical SitRep", "Medical"),
        ("NAVEX SitRep", "NAVEX"),
        ("Weather Advisory", "Weather"),
        ("General SitRep", "General")
    ]

    for label, action in button_names:
        btn = QPushButton(label)
        btn.setObjectName(f"SitrepButton_{action}")
        btn.setMinimumHeight(40)
        btn.clicked.connect(lambda _, a=action: handle_sitrep_selection(a, parent))
        layout.addWidget(btn)

    widget.setLayout(layout)
    return widget


def handle_sitrep_selection(action_type, parent):
    if action_type == "Medical":
        parent.clear_content_area()
        parent.dynamic_layout.addWidget(medical_sitrep.get_medical_sitrep_widget())
        parent.resize_with_animation(1050, 620)
    elif action_type == "NAVEX":
        from lib import navex_sitrep_updated
        # Clear previous widgets
        while parent.dynamic_layout.count():
            item = parent.dynamic_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        # Add the full interactive region selector view
        parent.dynamic_layout.addWidget(navex_sitrep_updated.get_navex_sitrep_main_widget())
        parent.resize_with_animation(500, 400)
    elif action_type == "Weather":
        parent.clear_content_area()
        parent.dynamic_layout.addWidget(get_weather_advisory_widget()) # type: ignore
        parent.resize_with_animation(1050, 720)
    elif action_type == "General":
        parent.clear_content_area()
        parent.dynamic_layout.addWidget(get_general_sitrep_widget())
        parent.resize_with_animation(1050, 520)
    else:
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(parent, "SitRep Selected", f"You selected: {action_type} SitRep")