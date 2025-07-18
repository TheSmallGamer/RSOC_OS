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

import requests
import json

def generate_narrative_from_summary(summary: str, context: str = "medical") -> str:
    if context == "navex":
        prompt = (
            "You are a professional RSOC analyst generating a neutral summary of a NAVEX report. "
            "Reword the following input into 1–2 paragraphs using formal, third-person business language. "
            "Do not include any references to ownership or affiliation (e.g., 'our', 'my', 'we', 'us'). "
            "Do not recommend actions, make conclusions, or suggest outcomes. "
            "Do not add opinions, tone of urgency, or emotional language. "
            "Your job is only to neutrally describe the reported content:\n\n"
            f"{summary}"
        )
    elif context == "weather":
        prompt = (
            "You are a professional RSOC analyst generating a weather advisory. "
            "Reword the following summary into a clear and concise advisory paragraph. "
            "Use formal business language and proper grammar. "
            "Do not include phrases like 'we are monitoring' or 'our team'. "
            "Focus only on what the National Weather Service has issued or what was observed. "
            "Keep the tone neutral and factual, avoiding speculation or emotional language.\n\n"
            f"{summary}"
        )
    elif context == "general":
        prompt = (
            "You are a Regional Security Operations Center (RSOC) analyst drafting a situation report (SitRep). "
            "Use a formal, concise, and professional tone. "
            "The SitRep begins with the sentence: 'At [TIME] [TIME_ZONE], the RSOC (Regional Security Operations Center) received a report [generated content]'. "
            "You are not creating an email, but rather filling a cell in a formal incident report. "
            "Use 1-2 paragraphs. Do not speculate or include unnecessary filler. Avoid bullet points or labeling outcomes directly. "
            "Only summarize what has been reported by the user.\n\n"
            f"Structured INput:\n{summary}"
        )
    else:
        prompt = (
            "You are a professional security operations report writer. Take the following structured summary "
            "and write a single, cohesive, formal paragraph that summarizes the incident. Your writing should be "
            "clear, factual, and reflect only events that occurred onsite. Do not include any speculation or assumptions. "
            "Do not mention anything that occurred after the subject left the site. "
            "RSOC will always stand for Regional Security Operations Center. "
            "In regards to the All Clear time, the RSOC always receives this from the ERT Team, no one else. "
            "Try to make the narrative at least two paragraphs. "
            "Do not include phrases like 'admitted to hospital', 'underwent treatment', or anything implying medical diagnosis or outcomes. "
            "Start the sitrep with the following: 'At [Time] [TimeZone], the RSOC (Regional Security Operations Center) received a call...'. "
            "Use formal and professional language.\n\n"
            f"Structured Input:\n{summary}"
        )

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "mistral", "prompt": prompt},
            stream=True,
            timeout=60
        )
        response.raise_for_status()

        full_output = ""
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    full_output += data.get("response", "")
                except json.JSONDecodeError:
                    continue

        return full_output.strip()

    except Exception as e:
        return f"[ERROR generating narrative: {e}]"
