# Contest Log Analyzer/test_code/compare_mult_sets.py
#
# Purpose: This utility compares the diagnostic multiplier set JSON file
#          with the generated text report to definitively identify any
#          discrepancies in the final output.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-23
# Version: 1.0.0-Beta
#
# --- Revision History ---
## [1.0.0-Beta] - 2025-08-23
# - Initial release of the multiplier set comparison utility.
import json
import os
import argparse
from collections import Counter
from typing import Set, Tuple

def load_json_set(filepath: str) -> Set[Tuple[str, str]]:
    """Loads a JSON file and parses its contents into a set of tuples."""
    if not os.path.exists(filepath):
        print(f"Error: Input file not found at '{filepath}'")
        return set()
        
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError) as e:
        print(f"Error reading or parsing {filepath}: {e}")
        return set()
    
    parsed_set = set()
    for item in data:
        try:
            band, mult = item.split('_', 1)
            parsed_set.add((band, mult))
        except ValueError:
            print(f"Warning: Skipping malformed entry '{item}' in {filepath}")
    return parsed_set

def load_text_report_set(filepath: str) -> Set[Tuple[str, str]]:
    """Parses a multiplier summary text report into a set of (band, mult) tuples."""
    if not os.path.exists(filepath):
        print(f"Error: Input file not found at '{filepath}'")
        return set()

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading text report file: {e}")
        return set()

    text_report_set = set()
    header_line = ""
    data_lines_start = 0
    for i, line in enumerate(lines):
        if line.strip().startswith('STPROV'):
            header_line = line
            data_lines_start = i + 2
            break
    
    if not header_line:
        print("Error: Could not find header row in text report.")
        return set()

    bands = [f"{b}M" if b != '160' else '160M' for b in header_line.split()[1:7]]
    current_mult = None
    
    for line in lines[data_lines_start:]:
        line = line.strip()
        if not line or line.startswith('---') or line.startswith('Total'):
            continue
        
        if line.startswith('8P5A:'):
            if current_mult:
                parts = line.split()
                qso_counts = [int(p) for p in parts[1:7]]
                for i, count in enumerate(qso_counts):
                    if count > 0:
                        text_report_set.add((bands[i], current_mult))
        else:
            current_mult = line.split()[0]
            
    return text_report_set

def main():
    """Main function to load, compare, and report on the multiplier sets."""
    parser = argparse.ArgumentParser(
        description="Compares a multiplier set JSON file with a text report."
    )
    parser.add_argument("json_file", help="Path to the ground-truth JSON file.")
    parser.add_argument("text_report", help="Path to the text report file to verify.")
    args = parser.parse_args()

    json_label = os.path.basename(args.json_file)
    text_label = os.path.basename(args.text_report)

    truth_set = load_json_set(args.json_file)
    reported_set = load_text_report_set(args.text_report)

    if not truth_set or not reported_set:
        print("\nAnalysis aborted due to file loading errors.")
        return

    # --- 1. Tabulate and print per-band counts ---
    counts_truth = Counter(band for band, mult in truth_set)
    counts_reported = Counter(band for band, mult in reported_set)
    all_bands = sorted(list(set(counts_truth.keys()) | set(counts_reported.keys())))

    print("\n--- Per-Band Multiplier Counts ---")
    header = f"{'Band':<6} {'JSON File':>15} {'Text Report':>15}"
    print(header)
    print('-' * len(header))
    for band in all_bands:
        count1 = counts_truth.get(band, 0)
        count2 = counts_reported.get(band, 0)
        print(f"{band:<6} {count1:>15} {count2:>15}")
    print('-' * len(header))
    print(f"{'Total':<6} {len(truth_set):>15} {len(reported_set):>15}\n")

    # --- 2. Calculate and print set differences ---
    missing_from_report = sorted(list(truth_set - reported_set))
    
    print("--- Set Difference Analysis ---")
    if not missing_from_report:
        print("\n[SUCCESS] The multiplier sets are identical.")
    else:
        print(f"\n[!] Multipliers found in '{json_label}' but MISSING from '{text_label}':")
        for band, mult in missing_from_report:
            print(f"  - ({band}, {mult})")

    print("\n--- Analysis Complete ---")

if __name__ == "__main__":
    main()