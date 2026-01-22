@echo off
cd /d "C:\Users\%USERNAME%\secure-invoice-processor"

:: 1. Open the local redacted outputs folder
start explorer.exe "C:\Users\%USERNAME%\secure-invoice-processor\redacted_outputs"

:: 2. Run the hidden VBScript (This starts the engine with NO terminal window)
wscript.exe "launch_hidden.vbs"

:: 3. Give the engine 5 seconds to warm up
timeout /t 5 /nobreak > nul

:: 4. Launch the standalone Edge window
start "" "msedge" --app=http://localhost:XXXX
exit