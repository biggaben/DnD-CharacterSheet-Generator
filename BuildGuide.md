# Building the Executable

This document explains how to build a standalone `.exe` file for the D&D Character Sheet Generator using PyInstaller.

## Prerequisites

1. Python 3.x installed
2. Virtual environment set up (`.venv` folder)
3. All dependencies installed (`pypdf`, `pyinstaller`)

## Quick Start

### Install PyInstaller

```powershell
.venv\Scripts\pip install pyinstaller
```

### Build the Executable

Simply run the build script:

```powershell
.\build_exe.bat
```

The executable will be created at: `dist\DnD_CharacterSheet_Generator.exe`

## Manual Build (Alternative)

If you prefer to build manually:

```powershell
# Activate virtual environment
.venv\Scripts\activate

# Build the executable
pyinstaller --onefile --windowed `
  --add-data "field_mappings.json;." `
  --add-data "character_sheets;character_sheets" `
  --name "DnD_CharacterSheet_Generator" `
  --clean `
  fill_character_sheet.py
```

## What Gets Included

The executable bundles:

- **Python interpreter** - No Python installation needed to run
- **fill_character_sheet.py** - The main script
- **pypdf library** - PDF manipulation
- **tkinter** - GUI file dialogs
- **field_mappings.json** - Field name mappings
- **character_sheets/** - Including the blank PDF template

## Build Options Explained

- `--onefile` - Creates a single executable file (vs. a folder with dependencies)
- `--windowed` - Hides the console window (GUI application)
- `--add-data "source;dest"` - Includes data files in the bundle
- `--name` - Sets the output executable name
- `--clean` - Removes temporary build files before building

## Testing the Executable

After building:

1. Navigate to `dist\` folder
2. Double-click `DnD_CharacterSheet_Generator.exe`
3. Test:
   - File picker opens to character_sheets folder
   - Can select a template file
   - Can save the filled PDF
   - PDF is correctly filled with character data

## Troubleshooting

### Antivirus False Positive

PyInstaller executables are sometimes flagged by antivirus software. This is a known issue with PyInstaller. You may need to:
- Add an exception for the executable
- Submit the file to your antivirus vendor as a false positive

### Import Errors

If the executable fails with import errors:

```powershell
# Add hidden imports manually
pyinstaller ... --hidden-import=pypdf._utils ...
```

### File Not Found Errors

If the executable can't find bundled files:
- Ensure `get_resource_path()` is used for all resource paths
- Check that data files are properly bundled with `--add-data`

### Debug Mode

To see what's happening:

```powershell
# Build without --windowed to see console output
pyinstaller --onefile `
  --add-data "field_mappings.json;." `
  --add-data "character_sheets;character_sheets" `
  --name "DnD_CharacterSheet_Generator" `
  fill_character_sheet.py
```

Then run the .exe from command line to see errors.

## Distribution

The final executable is completely standalone:

- **Size**: ~15-25 MB (includes Python interpreter)
- **Requirements**: None - no Python installation needed
- **Compatibility**: Windows 7+ (64-bit)

Share `DnD_CharacterSheet_Generator.exe` with others who can run it without installing anything.

## Advanced: Creating a Windows Installer

For even easier distribution, consider creating an installer:

1. Use [Inno Setup](https://jrsoftware.org/isinfo.php)
2. Package the .exe with an installer
3. Add desktop shortcut
4. Add to Start Menu

## Advanced: Adding an Icon

To add a custom icon:

1. Create or find a `.ico` file
2. Add to build command:

```powershell
pyinstaller --onefile --windowed --icon=icon.ico ...
```

## Advanced: Version Information

To add Windows version info:

1. Create `version_info.txt`:

```python
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
  ),
  kids=[
    StringFileInfo([
      StringTable('040904B0', [
        StringStruct('CompanyName', 'GenSecLabs'),
        StringStruct('FileDescription', 'D&D Character Sheet Auto-Fill'),
        StringStruct('FileVersion', '1.0.0.0'),
        StringStruct('ProductName', 'DnD Character Sheet Tools'),
        StringStruct('ProductVersion', '1.0.0.0')
      ])
    ])
  ]
)
```

2. Add to build:

```powershell
pyinstaller ... --version-file=version_info.txt ...
```

## Build Artifacts

After building, you'll see:

```
build/                      # Temporary build files (can be deleted)
dist/                       # Output folder
  └── DnD_CharacterSheet_Generator.exe   # Your executable!
DnD_CharacterSheet_Generator.spec  # PyInstaller spec file (can be reused)
```

The only file you need is `dist\DnD_CharacterSheet_Generator.exe`.
