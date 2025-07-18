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
import webbrowser
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QGridLayout
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl

# Optional: disable GPU to avoid rendering issues
os.environ["QTWEBENGINE_DISABLE_GPU"] = "1"
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --disable-software-rasterizer --disable-webgl"

website_map = {
    "S2 Lenel": "http://10.10.20.118/frameset/",
    "Heliaus": "https://heliaus.aus.com/index.php?t=aHR0cHM6Ly9oZWxpYXVzLmF1cy5jb20vZGFycy9kYXJzLnBocA==",
    "Navigator": "https://secure.liferaftinc.com/user/login",
    "Flex Box": "https://flex.ent.box.com/folder/0",
    "Google News": "https://news.google.com/home?hl=en-US&gl=US&ceid=US:en",
    "OpenBook Lockers": "https://aurnt525.americas.ad.flextronics.com/OpenBook/Admin.aspx",
    "Badge Access Portal": "https://aurnt525.americas.ad.flextronics.com/BadgeAccess/Home/Index",
    "Kiosk Cameras": "https://console.rhombussystems.com/login/",
    "License Plate Cameras": "http://10.159.241.202/local/fflprapp/operator.html#",
    "Weatherbug Alerts": "https://www.weatherbug.com/alerts/"
}

def get_website_selector_widget(parent=None):
    widget = QWidget()
    outer_layout = QVBoxLayout()
    grid_layout = QGridLayout()

    buttons_per_row = 3
    for index, (name, url) in enumerate(website_map.items()):
        row = index // buttons_per_row
        col = index % buttons_per_row
        btn = QPushButton(name)
        btn.setMinimumHeight(50)
        btn.setMinimumWidth(200)
        btn.clicked.connect(lambda _, u=url: parent.load_embedded_browser(u))
        grid_layout.addWidget(btn, row, col)

    outer_layout.addLayout(grid_layout)
    widget.setLayout(outer_layout)
    return widget

def get_webview_widget(url: str, back_callback, parent=None):
    widget = QWidget()
    layout = QVBoxLayout()

    browser = QWebEngineView()
    browser.load(QUrl(url))

    controls = QHBoxLayout()
    back_btn = QPushButton("Back")
    popout_btn = QPushButton("Pop Out")

    back_btn.clicked.connect(back_callback)
    popout_btn.clicked.connect(lambda: webbrowser.open(url))

    controls.addWidget(back_btn)
    controls.addStretch()
    controls.addWidget(popout_btn)

    layout.addLayout(controls)
    layout.addWidget(browser)
    widget.setLayout(layout)
    return widget
