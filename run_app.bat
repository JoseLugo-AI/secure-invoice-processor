@echo off
:: TELEPORT TO PROJECT FOLDER
cd /d "C:\Users\Anwender\secure-invoice-processor"

:: 1. Open your invoices folder
start explorer.exe "C:\Users\Anwender\secure-invoice-processor\invoices"

:: 2. Start the Streamlit server SILENTLY
:: We use 'start /b' to keep it in the background
start /b "" "C:\Users\Anwender\AppData\Local\Python\pythoncore-3.14-64\python.exe" -m streamlit run app.py --server.headless true

:: 3. Wait for the engine to warm up (10 seconds)
timeout /t 10 /nobreak > nul

:: 4. Open ONLY the standalone window
start "" "msedge" --app=http://localhost:8501

exit