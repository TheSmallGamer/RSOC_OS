# RSOC_OS

**RSOC_OS** (Regional Security Operations Center Operating System) is a custom-built desktop application designed to streamline, automate, and modernize the daily tasks and responsibilities of RSOC teams.

Developed by [Morgan Small], RSOC_OS provides powerful, easy-to-use tools for shift supervisors and operators, all in one cohesive, secure interface.

---

## 🚀 Features

- 📋 **SitRep Generators**  
  - Medical
  - NAVEX
  - Weather Advisory
  - General/Unclassified

- 📂 **Document Creation & Automation**  
  - BOLO Generator (with templated document editing)
  - Pass-Down Email Generator (auto-date, shift-aware subject lines)
  - Contact Directory with real-time Excel syncing

- 📧 **Outlook Integration**  
  - Automatically drafts fully formatted emails
  - Loads recipients dynamically from `recipients.json`
  - Sets From: as `rsoc@flex.com`

- 🌐 **Web View Tools**  
  - Embedded RSOC-relevant websites
  - Secure credential saving and auto-login features
  - “Pop out” to external browser option

- 🧠 **LLM-Powered Narrative Writing**  
  - Generates professional summaries for SitReps using local LLMs (via Ollama)

- 🛠️ **Installer & Auto-Startup Support**  
  - Installs to `Program Files`
  - Shortcut placed in `shell:startup`
  - Includes Python and all dependencies

---

## 🖥️ Installation

1. Download the latest release `.zip` or `.exe` from [Releases](#).
2. Unzip and run `RSOC_OS_Installer.exe`.
3. The app will be installed to your `Local App Data` directory.
4. After installation, press `F7` to launch the RSOC_OS interface.
5. If RSOC_OS does not launch after initial installation, go to your `shell:startup` folder, and run the shortcut from there.

> RSOC_OS will auto-launch at login and run in the background. You can toggle visibility using the F7 key.

---

## 🧱 Requirements

- Windows 10/11
- Internet access (for update checking & LLM)
- Microsoft Outlook (for email generation)
- Python 3.12+ (bundled with installer)

---

## 🔐 License

> **Custom License — Not Open Source**

RSOC_OS is proprietary software developed by Morgan Small.

- **Use of this software is prohibited if the author is removed, demoted, or terminated from RSOC operations.**
- **Modification, redistribution, or use outside Flex RSOC is strictly forbidden without explicit written permission.**
- **All rights reserved.**

See [LICENSE](LICENSE) for full terms.

---

## 📫 Contact

For licensing inquiries, bug reports, or feature requests, please contact:

**Morgan Small**  
📧 `jamiesmall0718@gmail.com`

---

## 🧠 Developer Notes

This tool was built from the ground up to address real-world inefficiencies and pain points within RSOC environments. RSOC_OS is a passion project designed to protect operational integrity, streamline workflows, and centralize essential tasks under one secure, user-friendly system.

**Important Disclaimer:**

RSOC_OS was developed voluntarily and independently by the author. It is not intended to be used as a basis for requesting increased pay, bonuses, promotions, or any form of financial compensation. This software is offered as a contribution to operational excellence, not as leverage for personal gain.

Please do not distribute or showcase without permission — it’s still in private release and subject to modification.

---

