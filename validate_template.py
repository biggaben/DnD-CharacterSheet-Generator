#!/usr/bin/env python3
"""Validate that a filled template uses the standardized format."""

import re
import json
from pathlib import Path
import sys


def load_expected_fields(mappings_file: Path) -> set:
    """Load expected standardized field names from mappings file."""
    with open(mappings_file, 'r', encoding='utf-8') as f:
        mappings = json.load(f)

    # Remove non-field keys
    mappings.pop('comment', None)
    mappings.pop('NOTE_Unmapped_Fields', None)

    return set(mappings.keys())


def parse_template_fields(template_path: Path) -> dict:
    """
    Parse template and extract field names found.

    Returns:
        dict with 'found_fields' (set), 'invalid_fields' (list), 'line_numbers' (dict)
    """
    found_fields = set()
    invalid_fields = []
    line_numbers = {}

    with open(template_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        
        # Skip empty lines, comments, and section headers
        if not line or line.startswith('#') or line.startswith('=') or line.startswith('D&D'):
            continue
        
        # Check if line matches "FieldName: value" pattern
        match = re.match(r'^([A-Za-z0-9_]+)\s*:\s*(.*)$', line)
        if match:
            field_name = match.group(1)
            value = match.group(2).strip()
            
            # Check if field name uses standardized format (contains underscore)
            if '_' in field_name:
                found_fields.add(field_name)
                line_numbers[field_name] = line_num
            else:
                # Field name doesn't use standardized format
                invalid_fields.append({
                    'line': line_num,
                    'field': field_name,
                    'reason': 'Field name missing underscore (not standardized format)'
                })

    return {
        'found_fields': found_fields,
        'invalid_fields': invalid_fields,
        'line_numbers': line_numbers
    }


def validate_template(template_path: Path, mappings_file: Path) -> dict:
    """
    Validate a filled template against the standardized format.

    Returns:
        dict with validation results
    """
    expected_fields = load_expected_fields(mappings_file)
    parsed = parse_template_fields(template_path)

    found_fields = parsed['found_fields']
    invalid_fields = parsed['invalid_fields']

    # Check for missing expected fields (optional fields are okay)
    missing_critical_fields = []
    critical_fields = {
        'Character_Name', 'Character_Class_Level', 'Character_Race',
        'Ability_Strength', 'Ability_Dexterity', 'Ability_Constitution',
        'Ability_Intelligence', 'Ability_Wisdom', 'Ability_Charisma',
        'HP_Maximum', 'Combat_ArmorClass'
    }

    for field in critical_fields:
        if field not in found_fields:
            missing_critical_fields.append(field)

    # Check for unexpected fields (not in mappings)
    unexpected_fields = found_fields - expected_fields

    # Calculate validation score
    uses_standardized_format = len(invalid_fields) == 0
    has_critical_fields = len(missing_critical_fields) == 0
    minimal_unexpected = len(unexpected_fields) < 5

    is_valid = uses_standardized_format and has_critical_fields

    return {
        'is_valid': is_valid,
        'uses_standardized_format': uses_standardized_format,
        'has_critical_fields': has_critical_fields,
        'found_fields_count': len(found_fields),
        'expected_fields_count': len(expected_fields),
        'invalid_fields': invalid_fields,
        'missing_critical_fields': missing_critical_fields,
        'unexpected_fields': list(unexpected_fields),
        'line_numbers': parsed['line_numbers']
    }


def main():
    """Main function: validate template from command line."""
    if len(sys.argv) < 2:
        print("Usage: python validate_template.py <template_file>")
        print("\nValidates that a filled template uses the standardized format.")
        return 1

    template_path = Path(sys.argv[1])
    if not template_path.exists():
        print(f"Error: Template file not found: {template_path}")
        return 1

    script_dir = Path(__file__).parent
    mappings_file = script_dir / "field_mappings.json"

    if not mappings_file.exists():
        print(f"Error: Mappings file not found: {mappings_file}")
        return 1

    print(f"Validating: {template_path.name}\n")

    results = validate_template(template_path, mappings_file)

    # Print results
    if results['is_valid']:
        print("✓ Template is VALID and uses standardized format")
        print(f"  Found {results['found_fields_count']} standardized fields")
    else:
        print("✗ Template has VALIDATION ISSUES\n")

    # Show invalid fields (non-standardized format)
    if results['invalid_fields']:
        print(f"⚠ Found {len(results['invalid_fields'])} fields NOT using standardized format:")
        for item in results['invalid_fields'][:10]:  # Show first 10
            print(f"  Line {item['line']}: '{item['field']}' - {item['reason']}")
        if len(results['invalid_fields']) > 10:
            print(f"  ... and {len(results['invalid_fields']) - 10} more")
        print()

    # Show missing critical fields
    if results['missing_critical_fields']:
        print(f"✗ Missing {len(results['missing_critical_fields'])} critical fields:")
        for field in results['missing_critical_fields']:
            print(f"  - {field}")
        print()

    # Show unexpected fields (not in mappings)
    if results['unexpected_fields']:
        print(f"ℹ Found {len(results['unexpected_fields'])} fields not in mappings:")
        for field in results['unexpected_fields'][:10]:
            print(f"  - {field}")
        if len(results['unexpected_fields']) > 10:
            print(f"  ... and {len(results['unexpected_fields']) - 10} more")
        print()

    # Summary
    if not results['uses_standardized_format']:
        print("\n⚠ THIS FILE DOES NOT USE THE STANDARDIZED TEMPLATE FORMAT")
        print("   The LLM should fill the standardized template by putting values after")
        print("   each field name (FieldName: value) WITHOUT changing the field names.")
        print("\n   See character_sheets/template_semantic_fields.txt for the template.")

    return 0 if results['is_valid'] else 1


if __name__ == "__main__":
    exit(main())
