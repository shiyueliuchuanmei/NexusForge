@echo off
chcp 65001 >nul
title AI Gateway - Stop

echo Stopping AI Gateway server...
taskkill /f /im python.exe 2>nul
taskkill /f /im uvicorn.exe 2>nul
echo [OK] Server stopped
pause
