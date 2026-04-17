@echo off
chcp 65001 >nul
title AI Gateway

cd /d "%~dp0"

echo ========================================
echo   AI Gateway - Starting...
echo ========================================

REM 检查虚拟环境
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo [OK] Virtual environment activated
) else (
    echo [INFO] No virtual environment found, using system Python
)

REM 检查依赖
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo.
    echo [ERROR] Dependencies not installed!
    echo Please run: pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM 初始化数据库
echo.
echo [1/2] Initializing database...
python -m app.init_db

REM 启动服务
echo.
echo [2/2] Starting server...
echo.
echo Server will be available at:
echo   - API:  http://localhost:8000
echo   - Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server.
echo ========================================
echo.

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
