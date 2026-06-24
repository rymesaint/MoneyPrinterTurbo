@echo off
setlocal
set "CURRENT_DIR=%CD%"
echo ***** Current directory: %CURRENT_DIR% *****
set "PYTHONPATH=%CURRENT_DIR%"

if not defined MPT_WEBUI_HOST set "MPT_WEBUI_HOST=0.0.0.0"
if not defined MPT_WEBUI_PORT set "MPT_WEBUI_PORT=8080"

set "PYTHON_CMD="
if exist "%CURRENT_DIR%\.venv\Scripts\python.exe" (
    set "PYTHON_CMD=%CURRENT_DIR%\.venv\Scripts\python.exe"
) else (
    where uv >nul 2>nul
    if not errorlevel 1 set "PYTHON_CMD=uv run python"
)

if not defined PYTHON_CMD (
    where python >nul 2>nul
    if not errorlevel 1 (
        echo ***** Warning: using python from PATH. *****
        set "PYTHON_CMD=python"
    )
)

if not defined PYTHON_CMD (
    echo ***** Python not found. Please install dependencies first. *****
    pause
    exit /b 1
)

echo ***** Starting MoneyPrinterTurbo at http://%MPT_WEBUI_HOST%:%MPT_WEBUI_PORT% *****
%PYTHON_CMD% main.py
