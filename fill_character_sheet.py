#!/usr/bin/env python3
"""Auto-Fill D&D 5e Character Sheet - Simple file picker interface"""

import re
import json
import sys
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from pypdf import PdfReader, PdfWriter

# Fix for PyInstaller bundled executables where stdin/stdout/stderr may be None
if getattr(sys, 'frozen', False):
    if sys.stdout is None:
        sys.stdout = open(os.devnull, "w")
    if sys.stderr is None:
        sys.stderr = open(os.devnull, "w")
    if sys.stdin is None:
        sys.stdin = open(os.devnull, "r")


def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    if getattr(sys, 'frozen', False):
        # Running in a PyInstaller bundle
        base_path = sys._MEIPASS
    else:
        # Running in normal Python environment
        base_path = Path(__file__).parent
    return Path(base_path) / relative_path


def load_field_mappings(mappings_file: Path) -> dict:
    """Load field mappings from JSON file."""
    if not mappings_file.exists():
        return {}
    with open(mappings_file, 'r', encoding='utf-8') as f:
        mappings = json.load(f)
    # Remove comment key if present
    mappings.pop('comment', None)
    return mappings


def parse_character_template(template_path: Path) -> dict:
    """
    Parse a character sheet text template into a dictionary of PDF field values.
    Supports multi-line values for large text fields.

    Args:
        template_path: Path to the text template file

    Returns:
        Dictionary mapping PDF field names to their values

    Format:
        FieldName: value
        FieldName: multi-line value
          continuation of value
          more lines
    """
    field_values = {}

    with open(template_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].rstrip()

        # Skip empty lines and comments
        if not line or line.startswith('#'):
            i += 1
            continue

        # Check if line matches "FieldName: value" pattern
        match = re.match(r'^([A-Za-z0-9_\s]+?)\s*:\s*(.*)$', line)
        if match:
            field_name = match.group(1).strip()
            value = match.group(2).strip()

            # Check for multi-line value (next lines are indented or continuations)
            i += 1
            value_lines = [value] if value else []

            while i < len(lines):
                next_line = lines[i].rstrip()

                # If next line is indented or doesn't match field pattern, it's a continuation
                if next_line and not next_line.startswith('#'):
                    # Check if it's a new field
                    if re.match(r'^([A-Za-z0-9_\s]+?)\s*:', next_line):
                        break
                    # It's a continuation line
                    value_lines.append(next_line)
                    i += 1
                else:
                    i += 1
                    break

            # Join multi-line values with newlines
            final_value = '\n'.join(value_lines).strip()

            # Skip empty values and placeholders
            if final_value and final_value != '[empty]' and not final_value.startswith('[MULTI-LINE]'):
                field_values[field_name] = final_value
        else:
            i += 1

    return field_values


def fill_pdf_form(input_pdf: Path, output_pdf: Path, field_values: dict) -> tuple[int, int]:
    """
    Fill a PDF form with the provided field values.
    Handles both text fields and checkbox fields.

    Args:
        input_pdf: Path to the blank PDF form
        output_pdf: Path where the filled PDF will be saved
        field_values: Dictionary mapping field names to values

    Returns:
        Tuple of (fields_filled, fields_not_found)
    """
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    # Get available PDF fields for validation
    pdf_fields = reader.get_fields()
    if not pdf_fields:
        raise ValueError(f"No form fields found in {input_pdf}")

    # Append all pages from reader to writer
    writer.append(reader)

    fields_filled = 0
    fields_not_found = 0

    # Update form fields page by page
    for page_num, page in enumerate(writer.pages):
        page_updates = {}

        for field_name, value in field_values.items():
            # Check if field exists in PDF
            if field_name in pdf_fields:
                # Handle checkbox fields (Check Box N)
                if field_name.startswith("Check Box"):
                    # Checkbox: "Yes" = checked, anything else = unchecked
                    if value and str(value).strip().lower() in (
                        'yes', '1', 'true', 'x', '✓'
                    ):
                        page_updates[field_name] = "/Yes"
                    else:
                        page_updates[field_name] = "/Off"
                else:
                    # Regular text field
                    page_updates[field_name] = str(value)
                fields_filled += 1
            else:
                # Check for common variations (trailing spaces, etc.)
                field_found = False
                for pdf_field in pdf_fields.keys():
                    if pdf_field.strip() == field_name.strip():
                        # Handle checkbox fields
                        if pdf_field.startswith("Check Box"):
                            if value and str(value).strip().lower() in (
                                'yes', '1', 'true', 'x', '✓'
                            ):
                                page_updates[pdf_field] = "/Yes"
                            else:
                                page_updates[pdf_field] = "/Off"
                        else:
                            page_updates[pdf_field] = str(value)
                        fields_filled += 1
                        field_found = True
                        break

                if not field_found:
                    fields_not_found += 1

        # Update fields for this page
        if page_updates:
            writer.update_page_form_field_values(
                page,
                page_updates,
                auto_regenerate=False
            )

    # Write the filled PDF
    with open(output_pdf, 'wb') as output_file:
        writer.write(output_file)

    return fields_filled, fields_not_found


def get_character_name_from_filename(template_path: Path) -> str:
    """
    Extract character name from template filename.

    Examples:
        "Aerion_Ferris_PDF_Template.txt" -> "Aerion Ferris"
        "Character_Sheet_PDF_Template.txt" -> "Character Sheet"
        "My Character Name.txt" -> "My Character Name"

    Args:
        template_path: Path to the template file

    Returns:
        Character name string
    """
    filename = template_path.stem  # Get filename without extension

    # Remove common suffixes
    suffixes_to_remove = [
        '_PDF_Template',
        '_PDF_template',
        '_Template',
        '_template',
        'Template',
        'template'
    ]

    for suffix in suffixes_to_remove:
        if filename.endswith(suffix):
            filename = filename[:-len(suffix)]
            break

    # Replace underscores with spaces
    character_name = filename.replace('_', ' ').strip()

    return character_name


def main():
    """Main function: Open file picker, fill PDF, done."""

    # Hide the root tkinter window
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)

    # Open file picker
    template_path = filedialog.askopenfilename(
        title="Select Character Template File",
        initialdir=get_resource_path("character_sheets"),
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )

    # User cancelled
    if not template_path:
        print("Cancelled.")
        return 0

    template_path = Path(template_path)
    print(f"\nSelected: {template_path.name}")

    # Extract character name
    character_name = get_character_name_from_filename(template_path)
    print(f"Character: {character_name}")

    # Define paths
    script_dir = get_resource_path("")
    blank_pdf_path = get_resource_path("character_sheets") / "dnd5e_blank_sheet.pdf"

    # Check blank PDF exists
    if not blank_pdf_path.exists():
        msg = ("Blank PDF not found.\n"
               "Please ensure 'dnd5e_blank_sheet.pdf' is in character_sheets/")
        messagebox.showerror("Error", msg)
        return 1

    # Parse template
    print("\nParsing template...")
    try:
        field_values = parse_character_template(template_path)
        print(f"Parsed {len(field_values)} fields")

        # Check if this is a standardized template (needs mapping)
        mappings_file = script_dir / "field_mappings.json"
        if mappings_file.exists():
            # Check if template uses standardized field names
            sample_fields = list(field_values.keys())[:5]
            uses_standardized = any('_' in field for field in sample_fields)

            if uses_standardized:
                print("Applying field mappings...")
                mappings = load_field_mappings(mappings_file)

                # Translate standardized field names to PDF field names
                translated_values = {}
                unmapped_count = 0
                for std_field, value in field_values.items():
                    pdf_field = mappings.get(std_field)
                    if pdf_field:
                        translated_values[pdf_field] = value
                    else:
                        # Field not in mappings, skip
                        unmapped_count += 1

                field_values = translated_values
                print(f"Mapped {len(field_values)} fields to PDF format")
                if unmapped_count > 0:
                    print(f"Warning: {unmapped_count} fields not in mapping")

    except Exception as e:
        messagebox.showerror("Error", f"Error parsing template: {e}")
        return 1

    # Open Save As dialog
    print("\nSelect where to save the filled PDF...")
    output_pdf_path = filedialog.asksaveasfilename(
        title="Save Filled Character Sheet As",
        defaultextension=".pdf",
        initialfile=f"{character_name}.pdf",
        initialdir=script_dir,
        filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
    )

    # User cancelled
    if not output_pdf_path:
        print("Cancelled.")
        return 0

    output_pdf_path = Path(output_pdf_path)

    # Fill PDF
    print(f"\nCreating: {output_pdf_path.name}")
    try:
        fields_filled, fields_not_found = fill_pdf_form(
            blank_pdf_path,
            output_pdf_path,
            field_values
        )

        print(f"\nDone! Filled {fields_filled} fields")
        print(f"Saved: {output_pdf_path.absolute()}\n")

    except Exception as e:
        messagebox.showerror("Error", f"Error filling PDF: {e}")
        if output_pdf_path.exists():
            output_pdf_path.unlink()
        return 1

    msg = f"Filled {fields_filled} fields\nSaved: {output_pdf_path.name}"
    messagebox.showinfo("Success", msg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
