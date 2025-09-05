# ADIF to CSV Converter
#
# Version: 1.0.0-Beta
# Date: 2025-09-05
#
# Purpose: A standalone utility to convert ADIF log files (.adi) into
#          comma-separated value (.csv) files for easier analysis in
#          spreadsheet software.
#
# Copyright (c) 2025 Mark Bailey, KD4D
#
# License: Mozilla Public License, v. 2.0
#          (https://www.mozilla.org/MPL/2.0/)
#
import sys
import os
import re
import csv
from typing import List, Dict, Set

def convert_adif_to_csv(adif_filepath: str):
    """
    Parses an ADIF file, disregarding the header, and converts it into a
    CSV file where the column headers are the ADIF tags.

    Args:
        adif_filepath (str): The path to the input ADIF file.
    """
    # --- 1. Read and Prepare ADIF Content ---
    try:
        with open(adif_filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: Input file not found at '{adif_filepath}'")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # Find the end of the header to start processing records
    header_end_match = re.search(r'<EOH>', content, re.IGNORECASE)
    if not header_end_match:
        print("Warning: <EOH> tag not found. Processing from start of file.")
        records_content = content
    else:
        records_content = content[header_end_match.end():]

    # Split the content into individual QSO records
    qso_records = re.split(r'<EOR>', records_content, flags=re.IGNORECASE)

    # --- 2. Parse Each QSO Record ---
    all_qsos_data: List[Dict[str, str]] = []
    all_field_names: Set[str] = set()
    
    # Regex to capture ADIF tags and their values
    adif_tag_pattern = re.compile(r'<([A-Z0-9_]+):\d+>([^<]*)', re.IGNORECASE)

    for record_str in qso_records:
        record_str = record_str.strip()
        if not record_str:
            continue

        qso_data: Dict[str, str] = {}
        matches = adif_tag_pattern.findall(record_str)
        
        for tag, value in matches:
            tag_upper = tag.upper()
            qso_data[tag_upper] = value
            all_field_names.add(tag_upper)
        
        if qso_data:
            all_qsos_data.append(qso_data)

    if not all_qsos_data:
        print("No valid QSO records found in the ADIF file.")
        return

    # --- 3. Write to CSV File ---
    base_name = os.path.splitext(adif_filepath)[0]
    csv_filepath = f"{base_name}.csv"
    
    # Sort the field names for a consistent column order
    sorted_field_names = sorted(list(all_field_names))

    try:
        with open(csv_filepath, 'w', newline='', encoding='utf-8') as f_out:
            writer = csv.DictWriter(f_out, fieldnames=sorted_field_names)
            
            # Write the header row (ADIF tags)
            writer.writeheader()
            
            # Write all the QSO data rows
            writer.writerows(all_qsos_data)
            
        print(f"Successfully converted ADIF file to '{csv_filepath}'")

    except IOError as e:
        print(f"Error writing to CSV file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during CSV writing: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python adif_to_csv.py <path_to_adif_file.adi>")
        sys.exit(1)
        
    input_file = sys.argv[1]
    
    if not os.path.isfile(input_file):
        print(f"Error: The provided path is not a valid file: '{input_file}'")
        sys.exit(1)
        
    convert_adif_to_csv(input_file)
