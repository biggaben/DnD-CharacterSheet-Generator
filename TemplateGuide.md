# D&D Character Sheet Auto-Fill System

## Overview

This system automates filling D&D 5e character sheets by:
1. Using a **standardized template format** with consistent field names
2. Mapping those field names to **PDF form fields** via `field_mappings.json`
3. Auto-filling the PDF with the `fill_character_sheet.py` script

---

## System Components

### 1. Standardized Template (`template_semantic_fields.txt`)

**Purpose:** Define consistent, machine-readable field names for all character data.

**Format:**
```
FieldName: value
Multi_Line_Field: Line 1 of text
Line 2 continues here
Line 3 continues here

Next_Field: value
```

**Key Rules:**
- Field names use `Underscore_Case` (e.g., `Character_Name`, `Ability_Strength`)
- Values come after the colon on the same line (or continue on following lines)
- Multi-line values continue without blank lines (blank line ends the field)
- **NEVER change field names** - they map to PDF fields via `field_mappings.json`

**Example:**
```
Character_Name: Aerion Ferris
Ability_Strength: 8
Ability_Strength_Modifier: -1
Equipment_List: Scale Mail
Shield
Dungeoneer's Pack
```

---

### 2. Field Mappings (`field_mappings.json`)

**Purpose:** Map standardized field names to actual PDF form field names.

**Format:**
```json
{
  "Standardized_Field_Name": "PDFFormFieldName",
  "Character_Name": "CharacterName",
  "Ability_Strength": "STR",
  "Ability_Strength_Modifier": "STRmod"
}
```

**Important Notes:**
- PDF field names are specific to the form (found in `dnd5e_blank_sheet.pdf`)
- Some PDF fields have trailing spaces: `"Race "` not `"Race"`
- Some standardized fields have **no PDF mapping** (see below)

#### Intentionally Unmapped Fields

These fields exist in the standardized template but **don't map to PDF fields**:

**Spell Slots** (PDF uses checkboxes instead):
- `SpellSlots_Level1_Total` through `SpellSlots_Level9_Total`
- PDF has checkbox fields, not total counts

**Spell Levels for Spells 1-7** (PDF limitation):
- `Spell_01_Level` through `Spell_07_Level`
- PDF only has level fields for spells 8-15 (`lvl18` through `lvl115`)

**Other Metadata:**
- `Spellcasting_AbilityModifier` (PDF doesn't have separate field)

**NOTE:** Proficiency checkboxes for saves and skills ARE now mapped (as of latest update).

---

### 3. Auto-Fill Script (`fill_character_sheet.py`)

**Purpose:** Parse filled template and generate filled PDF.

**How It Works:**
1. Load `field_mappings.json`
2. Parse template file using regex to extract `FieldName: value` pairs
3. Detect standardized format by checking for underscores in field names
4. If standardized format detected, apply mappings to translate field names
5. Fill PDF form fields with translated values
6. Save filled PDF

**Usage:**
```bash
python auto_fill_character_sheet.py
# Or double-click: run_auto_fill.bat
```

Opens file picker to select template, then saves filled PDF.

---

### 4. Validation Script (`validate_template.py`)

**Purpose:** Verify that a filled template uses correct standardized format.

**Usage:**
```bash
python validate_template.py "My Character.txt"
```

**Checks:**
- ✓ All fields use standardized format (contain underscores)
- ✓ Critical fields are present (name, class, abilities, HP, AC)
- ⚠ Warns about fields not in mappings (potential typos)

**Example Output:**
```
✗ Template has VALIDATION ISSUES

⚠ Found 52 fields NOT using standardized format:
  Line 2: 'Name' - Field name missing underscore
  Line 3: 'Race' - Field name missing underscore
  ...

✗ Missing 11 critical fields:
  - Character_Name
  - Ability_Strength
  ...
```

---

## Workflow

### For LLMs Filling Templates

1. **Start with the blank template:** `character_sheets/template_semantic_fields.txt`

2. **Read the instructions carefully** (at top of template)

3. **Fill in values WITHOUT changing field names:**
   ```
   ✓ CORRECT:
   Character_Name: Aerion Ferris
   Ability_Strength: 8
   Ability_Strength_Modifier: -1
   
   ✗ WRONG:
   Name: Aerion Ferris          ← Changed field name!
   Strength: 8 (−1)             ← Combined fields!
   ```

4. **Validate the filled template:**
   ```bash
   python validate_template.py "Filled Character.txt"
   ```

5. **Generate PDF:**
   ```bash
   python auto_fill_character_sheet.py
   ```

### For Developers

**To add new field mappings:**

1. Extract PDF field names from form:
   ```bash
   python OLD/extract_pdf_fields.py
   ```

2. Add mapping to `field_mappings.json`:
   ```json
   "Standardized_Field_Name": "PDFFormFieldName"
   ```

3. Update template if needed

4. Test with validation script

---

## Common Issues & Solutions

### Issue: "✗ Template has VALIDATION ISSUES"

**Cause:** LLM changed field names or didn't use standardized format

**Solution:** 
- Re-read template instructions
- Use exact field names from template
- Run validation script to identify specific problems

### Issue: "Warning: X fields not in mapping"

**Cause:** Template has fields that don't map to PDF

**Solution:**
- Check if field name has typo
- If field is intentionally unmapped (see list above), ignore warning
- If new field needed, add to `field_mappings.json`

### Issue: "Fields filled: 0"

**Cause:** Template doesn't use standardized format (no underscores in field names)

**Solution:**
- Regenerate template using standardized format
- Or add mappings for human-readable format (not recommended)

---

## File Reference

```
DnD-Specsheet-Tools/
├── auto_fill_character_sheet.py       # Main PDF filling script
├── validate_template.py               # Template validation script
├── field_mappings.json                # Field name mappings
├── TEMPLATE_SYSTEM.md                 # This documentation
└── character_sheets/
    ├── character_standardized_template.txt  # Blank template
    ├── Character Sheet 5e.pdf              # Blank PDF form
    └── [Character Name].txt                # Filled templates
```

---

## Technical Details

### Field Name Detection

The script detects standardized format by checking if field names contain underscores:

```python
sample_fields = list(field_values.keys())[:5]
uses_standardized = any('_' in field for field in sample_fields)
```

If underscores found → Apply mappings from `field_mappings.json`
If no underscores → Use field names directly (legacy format)

### Multi-Line Value Parsing

Multi-line fields are parsed by continuing until:
- A blank line is encountered
- A new field pattern is found (`FieldName:`)
- End of file

Example:
```
Equipment_List: Scale Mail
Shield
Dungeoneer's Pack

Currency_Gold: 10
```

Results in:
```python
{
  'Equipment_List': 'Scale Mail\nShield\nDungeoneer\'s Pack',
  'Currency_Gold': '10'
}
```

### PDF Field Matching

The script tries exact matches first, then checks for variations:

```python
if field_name in pdf_fields:
    # Exact match
elif pdf_field.strip() == field_name.strip():
    # Trailing space variation
```

Some PDF fields have quirks (trailing spaces, unusual names) which are handled in `field_mappings.json`.

---

## Future Enhancements

- [ ] Auto-generate filled template from character description (LLM)
- [ ] Support for multiple PDF form versions
- [ ] Web interface for template filling
- [ ] Import from D&D Beyond / Roll20
- [ ] Spell slot checkbox auto-filling
- [ ] Proficiency checkbox auto-checking

---

## Questions?

See:
- `README.md` - General project overview
- `USAGE.md` - User guide for filling sheets
- `field_mappings.json` - Current field mappings
- `validate_template.py --help` - Validation script usage
