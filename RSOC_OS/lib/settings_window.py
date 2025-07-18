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

import getpass
import configparser
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QCheckBox

def open_settings(main_window):
    current_user = getpass.getuser()
    config = configparser.ConfigParser()
    config.read('./config/settings.ini')

    dialog = QDialog(main_window)
    dialog.setWindowTitle("Settings")

    layout = QVBoxLayout()

    # Get current theme or default to dark
    theme = config.get(current_user, 'theme', fallback='dark')
    is_dark = theme == "dark"
    
    theme_toggle = QCheckBox("Enable Dark Mode")
    theme_toggle.setChecked(is_dark)
    theme_toggle.stateChanged.connect(lambda: toggle_theme(config, current_user, theme_toggle.isChecked(), main_window))

    layout.addWidget(QLabel(f"User: {current_user}"))
    layout.addWidget(theme_toggle)

    dialog.setLayout(layout)
    dialog.exec()

def toggle_theme(config, user, dark_mode_enabled, main_window):
    theme = "dark" if dark_mode_enabled else "light"

    if user not in config:
        config[user] = {}

    config[user]['theme'] = theme

    with open('./config/settings.ini', 'w') as configfile:
        config.write(configfile)

    main_window.config.read('./config/settings.ini')
    main_window.setStyleSheet("")
    main_window.load_theme()
    main_window.refresh_icons()