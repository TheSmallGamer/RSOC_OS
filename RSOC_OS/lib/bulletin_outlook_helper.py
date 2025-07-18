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

import datetime
import json
import os
from PySide6.QtWidgets import QMessageBox
import win32com.client
from typing import List


# Path to recipients.json
RECIPIENTS_FILE = os.path.join("config", "recipients.json")


def _a_or_an(phrase: str) -> str:
    """Returns 'an' if the phrase starts with a vowel sound, else 'a'."""
    vowels = ("a", "e", "i", "o", "u")
    word = phrase.strip().lower().split()[0] if phrase.strip() else ""
    return "an" if word.startswith(vowels) else "a"


def _generate_body(reporter: str, subject: str, location: str) -> str:
    article = _a_or_an(subject)
    return (
        "BPS,\n\n"
        f"Be advised, report from {reporter} of {article} {subject} at {location}. "
        "Security Management has been notified via phone. "
        "RSOC is currently coordinating and gathering information. "
        "Situation Report to follow."
    )


def _expand_roles(role_list: List[str], role_map: dict) -> str:
    """
    Expands a list of roles (e.g. ['bps manager']) to a semicolon-separated list of emails.
    Falls back to the input string if the role is not found in the map.
    """
    emails = []
    for item in role_list:
        key = item.strip().lower()
        emails.append(role_map.get(key, item))  # fallback to literal email if not found
    return "; ".join(filter(None, emails))


def _load_bulletin_recipients() -> tuple[str, str]:
    """
    Loads 'bulletin_recipients' from recipients.json and expands roles.
    Returns (to, cc) as email strings.
    """
    try:
        with open(RECIPIENTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            roles = {k.lower(): v for k, v in data.get("roles", {}).items()}
            bulletin = data.get("bulletin_recipients", {})
            to = _expand_roles(bulletin.get("to", []), roles)
            cc = _expand_roles(bulletin.get("cc", []), roles)
            return to, cc
    except Exception as e:
        print(f"[ERROR] Failed to load bulletin recipients: {e}")
        return "", ""


def send_bulletin_to_outlook(reporter: str, subject: str, location: str) -> None:
    body = _generate_body(reporter, subject, location)
    today = datetime.datetime.now().strftime("%m/%d/%Y")
    subject_line = f"Bulletin: {location} | {subject} {today}"

    to_field, cc_field = _load_bulletin_recipients()

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

    mail.To = to_field
    mail.CC = cc_field
    mail.Subject = subject_line
    mail.Body = body
    mail.Display()
