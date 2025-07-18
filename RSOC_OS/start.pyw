import os
import sys
import subprocess

from lib.update_checker import check_for_updates # type: ignore

# Get the directory where this script is located
base_dir = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(base_dir, "RSOC_OS.py")  # or your entry point

# Path to pythonw.exe — adjust this path if needed
pythonw = sys.executable.replace("python.exe", "pythonw.exe")

subprocess.Popen([pythonw, main_path], cwd=base_dir, shell=False)
check_for_updates()
