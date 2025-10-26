# D&D Character Sheet Generator

Automatically fill D&D 5e character sheet PDFs from text templates.

**→ Want a standalone .exe?** Run `build_executable.bat` to create a Windows executable (no Python required to run).

## Two Template Options

### 1. Standardized Template (Recommended for LLMs)

Use `character_standardized_template.txt` with logical, semantic field names:

- Easy for LLMs to understand and fill
- Clear instructions for each section
- Automatic mapping to PDF fields
- Example: `Character_Name`, `Ability_Strength_Modifier`, `Spell_01_Name`

### 2. Direct PDF Template

Use `character_pdf_template.txt` with exact PDF field names:

- Direct mapping (no translation needed)
- All 259 PDF fields available
- Example: `CharacterName`, `STRmod`, `SpellName1`

## How to Use

### Windows

1. Double-click `run_auto_fill.bat`
2. Select your filled template file
3. Done! PDF saved as `CharacterName.pdf` in project root

### Command Line

```bash
.venv\Scripts\python fill_character_sheet.py
```

## Setup

1. Install Python 3.8+
2. Install dependencies:

   ```bash
   python -m venv .venv
   .venv\Scripts\pip install -r requirements.txt
   ```

## Creating a Character

1. Copy the template you want to use
2. Fill in your character details
3. Run the script and select your file
4. Your PDF is ready!

## Template Format

```text
Field_Name: Value
Multi_Line_Field:
Line 1 of text
Line 2 of text

Next_Field: Value
```

Blank line ends multi-line input.

## Field Mappings

The script automatically detects which template type you're using:

- **Standardized template** (has underscores): Applies `field_mappings.json` translation
- **Direct PDF template**: No translation needed

View all mappings in `field_mappings.json`.

## Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt` (pypdf, pyinstaller)
- `dnd5e_blank_sheet.pdf` in `character_sheets/` directory

## Files

- `fill_character_sheet.py` - Main script
- `run_gui.bat` - Windows launcher
- `field_mappings.json` - Translation layer (standardized → PDF fields)
- `character_sheets/` - Templates and blank PDF form
- `Examples/` - Sample filled character templates
- `build_executable.bat` - **Build standalone .exe**
- `BuildGuide.md` - Detailed build instructions
- `requirements.txt` - Python dependencies
- `validate_template.py` - Template validation tool
- `LICENSE` - MIT license
- `README.md` - This file

## Building an Executable

Want to share this tool with non-technical users? Build a standalone `.exe`:

```bash
.\build_executable.bat
```

The executable (`DnD_CharacterSheet_Generator.exe`) will be created in the `dist/` folder.

See `BuildGuide.md` for detailed instructions and troubleshooting.
