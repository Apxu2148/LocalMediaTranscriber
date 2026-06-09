@echo off
setlocal EnableExtensions

cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\cleanup_dev.ps1" %*

endlocal
