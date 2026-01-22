Set WshShell = CreateObject("WScript.Shell")
' The 0 at the end tells Windows to run the command in a hidden window
WshShell.Run "C:\Users\Anwender\AppData\Local\Python\pythoncore-3.14-64\python.exe -m streamlit run app.py --server.headless true --browser.gatherUsageStats false", 0, False