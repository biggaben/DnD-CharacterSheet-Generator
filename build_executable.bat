@echo off
REM Build script for D&D Character Sheet Auto-Fill Tool
REM Creates a standalone .exe using PyInstaller

echo =========================================
echo Building D&D Character Sheet Filler EXE
echo =========================================
echo.

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist "DnD_SpecSheet_Generator.spec" del "DnD_SpecSheet_Generator.spec"

REM Build the executable
echo.
echo Building executable...
.venv\Scripts\pyinstaller.exe --onefile --windowed ^
  --add-data "field_mappings.json;." ^
  --add-data "character_sheets;character_sheets" ^
  --name "DnD_SpecSheet_Generator" ^
  --clean ^
  fill_character_sheet.py

echo.
if exist "dist\DnD_SpecSheet_Generator.exe" (
    echo =========================================
    echo BUILD SUCCESSFUL!
    echo =========================================
    echo.
    echo Executable created at:
    echo   dist\DnD_SpecSheet_Generator.exe
    echo.
    echo File size:
    for %%A in ("dist\DnD_SpecSheet_Generator.exe") do echo   %%~zA bytes
    echo.
) else (
    echo =========================================
    echo BUILD FAILED!
    echo =========================================
    echo Check the output above for errors.
)

pause
