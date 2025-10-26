# DnD Character Sheet Auto-Fill

Automatically fill D&D 5e character sheet PDFs from text templates.

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
.venv\Scripts\python auto_fill_character_sheet.py
```

## Setup

1. Install Python 3.8+
2. Install dependencies:

   ```bash
   python -m venv .venv
   .venv\Scripts\pip install pypdf
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
- pypdf library
- `Character Sheet 5e.pdf` in `character_sheets/` directory

## Files

- `auto_fill_character_sheet.py` - Main script
- `run_auto_fill.bat` - Windows launcher
- `character_standardized_template.txt` - LLM-friendly template with logical names
- `Character_Sheet_PDF_Template.txt` - Direct PDF field template
- `field_mappings.json` - Translation layer (standardized → PDF fields)
- `character_sheets/Character Sheet 5e.pdf` - Blank PDF form

---

**Simple. Fast. No fluff.**

