@echo off
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python run_excel_tasks.py >> scheduler_output.log 2>&1
