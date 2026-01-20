Set oShell = CreateObject("WScript.Shell")
oShell.CurrentDirectory = "C:\Users\Anwender\secure-invoice-processor"
' 0 means run the window invisibly
oShell.Run "cmd.exe /c run_app.bat", 0, False