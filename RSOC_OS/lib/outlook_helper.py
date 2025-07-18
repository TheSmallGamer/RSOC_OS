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
from PySide6.QtWidgets import QMessageBox
import win32com.client

def create_outlook_email(subject: str, html_body: str = "", to: list = None, cc: list = None, attachments: list = None):
    try:
        outlook = win32com.client.Dispatch("Outlook.Application")
        mail = outlook.CreateItem(0)  # 0 = Mail Item

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

        if to:
            mail.To = "; ".join(to)
        if cc:
            mail.CC = "; ".join(cc)

        mail.Subject = subject
        if html_body:
            mail.HTMLBody = html_body

        if attachments:
            for filepath in attachments:
                if os.path.exists(filepath):
                    mail.Attachments.Add(filepath)
                else:
                    print(f"Warning: Attachment file not found → {filepath}")

        mail.Display()

    except Exception as e:
        print(f"Error creating Outlook email: {e}")

def create_email_with_embedded_image(subject, html_body, to, cc, image_path, image_cid, bcc=None):
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
    mail.HTMLBody = html_body
    mail.To = "; ".join(to)
    mail.CC = "; ".join(cc)

    if bcc:
        mail.BCC = "; ".join(bcc)

    if os.path.exists(image_path):
        attachment = mail.Attachments.Add(image_path)
        attachment.PropertyAccessor.SetProperty(
            "http://schemas.microsoft.com/mapi/proptag/0x3712001F", image_cid  # PR_ATTACH_CONTENT_ID
        )
    else:
        print(f"Image not found at path: {image_path}")

    mail.Display()