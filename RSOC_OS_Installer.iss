[Setup]
AppName=RSOC_OS
AppVersion=1.0
; ⛔️ Previously used: {pf} (which requires admin)
DefaultDirName={userappdata}\Programs\RSOC_OS
DefaultGroupName=RSOC_OS
UninstallDisplayIcon={app}\images\rsoc-os logo.ico
OutputBaseFilename=RSOC_OS_Installer
Compression=lzma
SolidCompression=yes
PrivilegesRequired=lowest

[Files]
; ✅ Main program
Source: "RSOC_OS\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs
; ✅ Optional embedded Python installer
Source: "python-3.12.4-amd64.exe"; DestDir: "{tmp}"; Flags: ignoreversion

[Icons]
; ✅ Shortcut with custom icon
Name: "{group}\RSOC_OS"; Filename: "{app}\start.pyw"; WorkingDir: "{app}"; IconFilename: "{app}\images\rsoc-os logo.ico"
Name: "{userstartup}\RSOC_OS"; Filename: "{app}\start.pyw"; WorkingDir: "{app}"; IconFilename: "{app}\images\rsoc-os logo.ico"

[Run]
; ✅ Install Python silently (you may want to switch InstallAllUsers=0 to avoid admin here)
Filename: "{tmp}\python-3.12.4-amd64.exe"; Parameters: "/quiet InstallAllUsers=0 PrependPath=1 Include_pip=1"; Flags: waituntilterminated runhidden

; ✅ Install requirements
Filename: "python.exe"; Parameters: "-m pip install -r ""{app}\requirements.txt"""; WorkingDir: "{app}"; Flags: runhidden waituntilterminated

; ✅ Install Ollama if not already present
Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -NoProfile -WindowStyle Hidden -Command ""if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {{ Invoke-WebRequest -Uri 'https://ollama.com/download/OllamaSetup.exe' -OutFile $env:TEMP\OllamaSetup.exe; Start-Process $env:TEMP\OllamaSetup.exe -ArgumentList '/S' -Wait }}"""; Flags: runhidden

; ✅ Launch app post-install
Filename: "pythonw.exe"; Parameters: """{app}\start.pyw"""; WorkingDir: "{app}"; Description: "Launch RSOC_OS now"; Flags: postinstall nowait skipifsilent shellexec
