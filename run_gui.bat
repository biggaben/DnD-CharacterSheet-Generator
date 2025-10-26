@echo off
REM Batch file to run the auto-fill character sheet script
REM Uses the virtual environment Python with pypdf installed

cd /d "%~dp0"
.venv\Scripts\python.exe fill_character_sheet.py
pause
