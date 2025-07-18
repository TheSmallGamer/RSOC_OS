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
import win32com.client
from PySide6.QtWidgets import QFileDialog, QMessageBox
from datetime import datetime

CONFIG_PATH = "./config"
TEMPLATE_PATH = os.path.join(CONFIG_PATH, "SitRep Template.htm")
RECIPIENTS_PATH = os.path.join(CONFIG_PATH, "recipients.json")


def load_medical_recipients(company: str, restricted: bool = False, parent_widget=None) -> dict:
    if not os.path.exists(RECIPIENTS_PATH):
        return {"to": "", "cc": "", "bps_manager": "Unknown"}

    with open(RECIPIENTS_PATH, "r") as f:
        data = json.load(f)

    recipients = data.get("medical_recipients", {})
    agencies = data.get("agencies", {})
    roles = {k.lower(): v for k, v in data.get("roles", {}).items()}

    mode_key = "restricted" if restricted else "normal"

    # Use role expansion if values are lists (recommended structure)
    def expand_roles(raw_list):
        return "; ".join([roles.get(r.lower(), r) for r in raw_list])

    to_raw = recipients.get(mode_key, {}).get("to", "")
    cc_raw = recipients.get(mode_key, {}).get("cc", "")
    
    if isinstance(to_raw, list):
        to_field = expand_roles(to_raw)
    else:
        to_field = to_raw  # fallback for legacy strings

    if isinstance(cc_raw, list):
        cc_field = expand_roles(cc_raw)
    else:
        cc_field = cc_raw

    # Append agency contact in normal mode
    if not restricted:
        agency_email = agencies.get(company)
        if agency_email:
            to_field += f"; {agency_email}"
        else:
            QMessageBox.warning(
                parent_widget,
                "Missing Agency Contact",
                f"No agency contact found for '{company}'. Please add it manually in Outlook."
            )

    bps_key = recipients.get("bps_manager", "Unknown")
    if isinstance(bps_key, str):
        # Lookup in roles (case-insensitive), fallback to key itself
        bps_value = roles.get(bps_key.lower(), bps_key)

        # Extract name from "Name <email>" or use as-is
        if "<" in bps_value and ">" in bps_value:
            bps_manager = bps_value.split("<")[0].strip()
        else:
            bps_manager = bps_value
    else:
        bps_manager = "Unknown"


    return {"to": to_field, "cc": cc_field, "bps_manager": bps_manager}

def load_navex_recipients(region: str, parent_widget=None) -> dict:
    if not os.path.exists(RECIPIENTS_PATH):
        return {"to": "", "cc": "", "bcc": "", "bps_manager": "Unknown"}

    with open(RECIPIENTS_PATH, "r") as f:
        data = json.load(f)

    navex_data = data.get("navex_recipients", {})
    roles = {k.lower(): v for k, v in data.get("roles", {}).items()}

    region_data = navex_data.get(region)
    if not region_data:
        QMessageBox.critical(
            parent_widget,
            "Missing Region",
            f"No NAVEX recipient list found for region: {region}"
        )
        return {"to": "", "cc": "", "bcc": "", "bps_manager": "Unknown"}

    def expand(entry):
        if isinstance(entry, list):
            return "; ".join(
                roles.get(e.lower(), e) if isinstance(e, str) else str(e)
                for e in entry
            )
        elif isinstance(entry, str):
            return roles.get(entry.lower(), entry)
        return ""

    to_field = expand(region_data.get("to", []))
    cc_field = expand(region_data.get("cc", []))
    bcc_field = expand(region_data.get("bcc", []))

    # Extract display name from ManagerReplace
    bps_key = region_data.get("bps_manager", "Unknown")
    bps_val = roles.get(bps_key.lower(), bps_key) if isinstance(bps_key, str) else bps_key
    if "<" in bps_val and ">" in bps_val:
        bps_manager = bps_val.split("<")[0].strip()
    else:
        bps_manager = bps_val

    return {
        "to": to_field,
        "cc": cc_field,
        "bcc": bcc_field,
        "bps_manager": bps_manager
    }


def get_filled_html(narrative: str, category: str, company: str, manager_name: str) -> str:
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError("SitRep template file not found in config directory.")

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as file:
        html = file.read()

    # Locate the first empty <td> with height:1.0in and inject the narrative
    target_string = (
        '<td width=900 style=\'width:675.35pt;border-top:none;border-left:none;\n'
        '  border-bottom:solid black 1.0pt;border-right:solid black 1.0pt;background:\n'
        '  white;padding:.75pt .75pt .75pt .75pt;height:1.0in\'>'
    )
    if target_string not in html:
        raise ValueError("Could not locate the narrative insertion cell in the HTML template.")

    narrative = narrative.replace("\n", "<br>")

    formatted_narrative = (
        "<p class=MsoNormal>"
        "<span style='font-size:12.0pt;font-family:\"Century Gothic\",sans-serif;"
        "color:#203864'>"
        f"{narrative}"
        "</span></p>"
    )

    insertion = target_string + "\n" + formatted_narrative

    html = html.replace("CategoryReplace", category)
    formatted_date = datetime.now().strftime("%B %d, %Y")
    html = html.replace("MonthReplace", formatted_date)
    html = html.replace(target_string, insertion, 1)

    html = html.replace("ManagerReplace", manager_name)

    return html

def send_weather_advisory_to_outlook(subject, body, to, cc, bcc=None, image_path=None):
    import win32com.client

    outlook = win32com.client.Dispatch("Outlook.Application")
    mail = outlook.CreateItem(0)
    
    rsoc_email = "rsoc@flex.com"
    rsoc_account = None
    for account in outlook.Session.Accounts:
        if account.SmtpAddress.lower() == rsoc_email:
            rsoc_account = account
            break

    if rsoc_account:
        mail.SendUsingAccount = rsoc_account
        mail.SentOnBehalfOfName = rsoc_email  # Optional: keeps display name consistent
    else:
        QMessageBox.critical(None, "Error", "RSOC email account (rsoc@flex.com) not found in Outlook.")
        return

    mail.Subject = subject
    mail.To = "; ".join(to)
    mail.CC = "; ".join(cc)
    if bcc:
        mail.BCC = "; ".join(bcc)

    # Plain body if you want simple text:
    mail.HTMLBody = body

    # Attach logo if it exists
    if image_path and os.path.exists(image_path):
        mail.Attachments.Add(image_path)

    mail.Display()


def send_sitrep_to_outlook(
    summary_html: str,
    sitrep_type: str,
    patient_company: str,
    ask_attachment: bool = True,
    parent_widget=None
):
    # Ask user which distribution to use
    msgbox = QMessageBox(parent_widget)
    msgbox.setWindowTitle("Send SitRep")
    msgbox.setText("Who should receive this SitRep?")
    normal_btn = msgbox.addButton("All Parties (Agency, CMT, RSOC)", QMessageBox.YesRole)
    restricted_btn = msgbox.addButton("Local BPS & RSOC Only", QMessageBox.NoRole)
    cancel_btn = msgbox.addButton("Cancel", QMessageBox.RejectRole)
    msgbox.exec()

    if msgbox.clickedButton() == cancel_btn:
        return  # Exit silently

    mode = "normal" if msgbox.clickedButton() == normal_btn else "restricted"
    recipients = load_medical_recipients(patient_company, restricted=(mode == "restricted"), parent_widget=parent_widget)

    if not recipients:
        QMessageBox.critical(
            parent_widget,
            "Missing Recipient",
            f"No recipient list found for company '{patient_company}' in {mode} mode.\n"
            f"Please manually enter recipients in Outlook."
        )
        recipients = {"to": "", "cc": ""}

    # Combine HTML with narrative inserted
    full_html = get_filled_html(
        summary_html,
        category=sitrep_type,
        company=patient_company,
        manager_name=recipients.get("bps_manager", "Unknown")
    )


    # Launch Outlook
    outlook = win32com.client.Dispatch("Outlook.Application")
    mail = outlook.CreateItem(0)
    
    rsoc_email = "rsoc@flex.com"
    rsoc_account = None
    for account in outlook.Session.Accounts:
        if account.SmtpAddress.lower() == rsoc_email:
            rsoc_account = account
            break

    if rsoc_account:
        mail.SendUsingAccount = rsoc_account
        mail.SentOnBehalfOfName = rsoc_email  # Optional: keeps display name consistent
    else:
        QMessageBox.critical(None, "Error", "RSOC email account (rsoc@flex.com) not found in Outlook.")
        return

    mail.Subject = f"SITREP | Situation Report | {sitrep_type}"
    mail.To = recipients["to"]
    mail.CC = recipients["cc"]
    mail.HTMLBody = full_html

    if sitrep_type.lower() == "navex":
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(None, "Select NAVEX Attachment")
        if file_path:
            mail.Attachments.Add(file_path)
    elif ask_attachment:
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(None, "Attach a file?")
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
            parent_widget,
            "Missing Logo",
            f"Logo image not found at:\n{image_path}"
        )

    mail.Display()

def send_general_sitrep_to_outlook(summary_text: str, date: str, incident_type: str):
    from_path = os.path.join("config", "SitRep Template.htm")
    with open(from_path, "r", encoding="cp1252") as f:
        html_body = f.read()

    # Replace placeholders
    html_body = html_body.replace("MonthReplace", date)
    html_body = html_body.replace("CategoryReplace", incident_type)
    
    # Inject the summary into the Situation cell
    html_body = html_body.replace('<td width=900 style=\'width:675.35pt;border-top:none;border-left:none;\n  border-bottom:solid black 1.0pt;border-right:solid black 1.0pt;background:\n  white;padding:.75pt .75pt .75pt .75pt;height:1.0in\'>',
                                  f'<td width=900 style="width:675.35pt;border-top:none;border-left:none; border-bottom:solid black 1.0pt;border-right:solid black 1.0pt;background: white;padding:.75pt .75pt .75pt .75pt;height:1.0in"><p class=MsoNormal style="font-family:\'Century Gothic\',sans-serif;color:#203864;font-size:12pt">{summary_text}</p>')

    outlook = win32com.client.Dispatch("Outlook.Application")
    mail = outlook.CreateItem(0)

    # Attempt to use RSOC account
    rsoc_email = "rsoc@flex.com"
    rsoc_account = None
    for account in outlook.Session.Accounts:
        if account.SmtpAddress.lower() == rsoc_email:
            rsoc_account = account
            break
    if rsoc_account:
        mail.SendUsingAccount = rsoc_account
        mail.SentOnBehalfOfName = rsoc_email
    else:
        QMessageBox.critical(None, "Error", "RSOC email account (rsoc@flex.com) not found in Outlook.")
        return

    # Load recipient roles from JSON and expand based on general_sitrep role names
    with open(os.path.join("config", "recipients.json"), "r", encoding="utf-8") as f:
        data = json.load(f)

    roles = {k.lower(): v for k, v in data.get("roles", {}).items()}
    general_cfg = data.get("general_sitrep", {})

    bps_key = general_cfg.get("bps_manager", "Unknown")
    bps_value = roles.get(bps_key.lower(), bps_key) if isinstance(bps_key, str) else bps_key

    if "<" in bps_value and ">" in bps_value:
        bps_manager_name = bps_value.split("<")[0].strip()
    else:
        bps_manager_name = bps_value

    html_body = html_body.replace("ManagerReplace", bps_manager_name)

    def expand_roles(role_list):
        return [roles.get(role.lower(), role) for role in role_list]

    to_recipients = expand_roles(general_cfg.get("to", []))
    cc_recipients = expand_roles(general_cfg.get("cc", []))

    mail.To = "; ".join(to_recipients)
    mail.CC = "; ".join(cc_recipients)

    mail.Subject = f"SITREP | Situation Report | {incident_type}"
    mail.HTMLBody = html_body

    # Attach logo image with content ID for inline use
    current_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.normpath(os.path.join(current_dir, "..", "images", "image001.png"))

    attachment = mail.Attachments.Add(image_path)

    # Use PropertyAccessor to set content ID (for use in HTML as cid:rsoc_logo)
    property_accessor = attachment.PropertyAccessor
    property_accessor.SetProperty("http://schemas.microsoft.com/mapi/proptag/0x3712001F", "rsoc_logo")


    mail.Display()
