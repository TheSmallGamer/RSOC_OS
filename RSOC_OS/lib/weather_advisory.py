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
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton,
    QComboBox, QDateTimeEdit, QTextEdit, QCheckBox, QScrollArea, QMessageBox
)
from PySide6.QtCore import Qt, QDateTime
import json
import os

SITE_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "site_data.json")
RECIPIENTS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "recipients.json")

def get_weather_advisory_widget(parent=None):
    widget = QWidget()
    main_layout = QHBoxLayout(widget)

    ### LEFT SIDE ###
    left_layout = QVBoxLayout()

    title_label = QLabel("Weather Advisory Generator")
    title_label.setStyleSheet("font-weight: bold; font-size: 18px;")
    left_layout.addWidget(title_label)

    advisory_label = QLabel("Advisory Type:")
    advisory_input = QComboBox()
    advisory_input.setEditable(True)
    advisory_input.addItems(["Snowstorm", "Flood", "Heat Advisory", "Severe Thunderstorm", "Hurricane", "Other"])
    left_layout.addWidget(advisory_label)
    left_layout.addWidget(advisory_input)

    time_layout = QHBoxLayout()
    from_input = QDateTimeEdit(QDateTime.currentDateTime())
    from_input.setDisplayFormat("MM/dd/yyyy HH:mm")
    to_input = QDateTimeEdit(QDateTime.currentDateTime())
    to_input.setDisplayFormat("MM/dd/yyyy HH:mm")
    time_layout.addWidget(QLabel("From:"))
    time_layout.addWidget(from_input)
    time_layout.addWidget(QLabel("To:"))
    time_layout.addWidget(to_input)
    left_layout.addLayout(time_layout)

    summary_label = QLabel("Summary Details:")
    summary_input = QTextEdit()
    summary_input.setPlaceholderText("Enter a brief summary of the situation")
    left_layout.addWidget(summary_label)
    left_layout.addWidget(summary_input)

    actions_label = QLabel("Actions Required:")
    left_layout.addWidget(actions_label)

    action_texts = [
        "Monitor local weather updates, road conditions, \nand follow community guidance.", "Plan on slippery road conditions.", "Slow down and use caution while traveling.", 
        "Materials teams double check critical shipment schedules over \nthe next 72 hrs. - if you asses a delay, alert your BPS partner", 
        "Shelter in Place", "Evacuate Area", "Notify Site Leadership", "Other"
    ]
    actions_checkboxes = []
    actions_grid = QGridLayout()
    for i, text in enumerate(action_texts):
        cb = QCheckBox(text)
        actions_checkboxes.append(cb)
        actions_grid.addWidget(cb, i // 2, i % 2)
    left_layout.addLayout(actions_grid)

    site_label = QLabel("Flex Sites Affected:")
    left_layout.addWidget(site_label)

    site_checkboxes = {}
    site_scroll = QScrollArea()
    site_scroll.setWidgetResizable(True)
    site_container = QWidget()
    site_layout = QGridLayout(site_container)

    try:
        with open(SITE_DATA_PATH, "r", encoding="utf-8") as f:
            site_data = json.load(f)

        cities = list(site_data.keys())
        for i, city in enumerate(cities):
            cb = QCheckBox(city)
            site_checkboxes[city] = cb
            site_layout.addWidget(cb, i // 3, i % 3)
    except Exception as e:
        site_layout.addWidget(QLabel(f"Failed to load site data: {e}"))

    site_scroll.setWidget(site_container)
    left_layout.addWidget(site_scroll)

    ### RIGHT SIDE ###
    right_layout = QVBoxLayout()
    output_label = QLabel("Generated Advisory:")
    output_box = QTextEdit()
    output_box.setReadOnly(False)

    right_layout.addWidget(output_label)
    right_layout.addWidget(output_box)

    btn_layout = QHBoxLayout()
    generate_btn = QPushButton("Generate Summary")
    copy_btn = QPushButton("Copy to Outlook")
    clear_btn = QPushButton("Clear")
    btn_layout.addWidget(generate_btn)
    btn_layout.addWidget(copy_btn)
    btn_layout.addWidget(clear_btn)

    right_layout.addLayout(btn_layout)

    main_layout.addLayout(left_layout)
    main_layout.addLayout(right_layout)

    ### EVENTS ###

    def on_generate():
        advisory_type = advisory_input.currentText().strip()
        from_time_val = from_input.dateTime().toString("MM/dd/yyyy HH:mm")
        to_time_val = to_input.dateTime().toString("MM/dd/yyyy HH:mm")
        summary_raw = summary_input.toPlainText().strip()
        selected_sites = [k for k, v in site_checkboxes.items() if v.isChecked()]
        selected_actions = [cb.text() for cb in actions_checkboxes if cb.isChecked()]

        if not advisory_type or not summary_raw or not selected_sites:
            QMessageBox.warning(widget, "Missing Fields", "Advisory Type, Summary, and Sites are required.")
            return

        try:
            from lib.llm_narrative import generate_narrative_from_summary # type: ignore
            refined_summary = generate_narrative_from_summary(summary_raw.strip(), context="weather")
        except Exception as e:
            QMessageBox.critical(widget, "LLM Error", str(e))
            return

        city_list = "<br>".join(selected_sites)
        from_dt = from_input.dateTime().toPython()
        to_dt = to_input.dateTime().toPython()

        from_formatted = from_dt.strftime("%A, %B %d, %Y at %#I:%M %p")
        to_formatted = to_dt.strftime("%A, %B %d, %Y at %#I:%M %p")

        # Flex Sites Summary + Details Section
        site_summary_block = "<b><u>Flex Sites near weather events are:</u></b><br>"
        details_block = ""

        for city in selected_sites:
            data = site_data.get(city, {})
            state = data.get("state", "")
            addresses = data.get("addresses", [])
            address_line = " | ".join(addresses)

            site_summary_block += f"<b><span style='color:#2F75B5'>{city}</span></b><br>"

            details_block += (
                f"{city}, {state}<br>"
                f"Location: {address_line}<br>"
                f"Time: {from_formatted} - {to_formatted}<br><br>"
            )

        actions_block = "\n".join([f"• {a}" for a in selected_actions])

        city_label = "city" if len(selected_sites) == 1 else "cities"

        final = (
            f"<b><u>Summary:</u></b><br>"
            f"The Brand Protection and Security team is monitoring a {advisory_type} in the {city_label} of {city_list} "
            f"issued by the National Weather Service on {from_time_val} to {to_time_val}.<br><br>"
            f"{refined_summary}<br><br>"
            f"<b><u>Actions:</u></b><br>{actions_block.replace('•', '•&nbsp;').replace('\n', '<br>')}<br><br>"
            f"<b><u>Flex Sites near weather events are:</u></b><br><b><span style='color:#2F75B5'>{city_list}</b><br><br>"
            f"{details_block.strip()}"
        )

        output_box.setHtml(final)

    def on_send():
        from lib.sitrep_outlook_helper import send_weather_advisory_to_outlook # type: ignore

        subject = f"DRAFT - Weather Advisory - {advisory_input.currentText().strip()}"
        body = output_box.toHtml()

        try:
            with open(RECIPIENTS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                profile = data.get("weather_advisory", {})
                roles = data.get("roles", {})

                def resolve(rlist):
                    result = []
                    for r in rlist:
                        val = roles.get(r, r)
                        result.extend(val if isinstance(val, list) else [val])
                    return result

                to_list = resolve(profile.get("to", []))
                cc_list = resolve(profile.get("cc", []))
                bcc_list = resolve(profile.get("bcc", []))

        except Exception as e:
            QMessageBox.critical(widget, "Recipient Error", str(e))
            return

        image_path = os.path.join("RSOC_OS", "resources", "images", "flexlogo.png")

        try:
            send_weather_advisory_to_outlook(
                subject=subject,
                body=body,
                to=to_list,
                cc=cc_list,
                bcc=bcc_list,
                image_path=image_path
            )
        except Exception as e:
            QMessageBox.critical(widget, "Send Failed", str(e))

    def on_clear():
        advisory_input.setCurrentIndex(0)
        from_input.setDateTime(QDateTime.currentDateTime())
        to_input.setDateTime(QDateTime.currentDateTime())
        summary_input.clear()
        output_box.clear()
        for cb in actions_checkboxes:
            cb.setChecked(False)
        for cb in site_checkboxes.values():
            cb.setChecked(False)

    generate_btn.clicked.connect(on_generate)
    clear_btn.clicked.connect(on_clear)
    copy_btn.clicked.connect(on_send)

    return widget
