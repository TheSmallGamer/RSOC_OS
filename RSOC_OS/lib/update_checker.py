# lib/update_checker.py
import requests
from packaging import version
from PySide6.QtWidgets import QMessageBox
import webbrowser

GITHUB_REPO = "TheSmallGamer/RSOC_OS"
CURRENT_VERSION = "1.0.1"  # Update this each time you publish a new version

def get_latest_release_info():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data["tag_name"], data["assets"][0]["browser_download_url"]
    except Exception as e:
        print(f"[Update Checker] Error: {e}")
        return None, None

def is_newer(current, latest):
    return version.parse(latest) > version.parse(current)

def check_for_updates():
    latest_version, download_url = get_latest_release_info()
    if latest_version and is_newer(CURRENT_VERSION, latest_version):
        msg = QMessageBox()
        msg.setWindowTitle("Update Available")
        msg.setText(f"A new version ({latest_version}) of RSOC_OS is available.\nWould you like to download it?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        result = msg.exec()

        if result == QMessageBox.Yes:
            webbrowser.open(download_url)
