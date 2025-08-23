from sys import argv
import re

import json
from typing import List, Tuple, Optional

def parse_json_to_tuples(filename: str) -> Optional[List[Tuple[str, str]]]:
    """
    Reads a JSON file containing a list of strings and converts them to tuples.

    This function assumes the JSON file contains a standard JSON array (e.g., ["item1", "item2"]).
    Each string in the array is split by the first underscore character "_" 
    into a two-part tuple. Strings without an underscore are ignored.

    Args:
        filename: The path to the input JSON file.

    Returns:
        A list of string tuples, or None if a file or parsing error occurs.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if not isinstance(data, list):
            print(f"Error: JSON file '{filename}' does not contain a list ([...]).")
            return None

        result_list: List[Tuple[str, str]] = []
        for item in data:
            if isinstance(item, str) and '_' in item:
                # Split only on the first underscore to handle multipliers that might contain one
                parts = item.split('_', 1)
                if len(parts) == 2:
                    result_list.append((parts[0], parts[1]))
        
        return result_list

    except FileNotFoundError:
        print(f"Error: File not found at '{filename}'")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{filename}'. Please ensure it is valid.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def parse_summary_to_tuples(filename: str) -> Optional[List[Tuple[str, str]]]:
    """
    Parses a specially formatted multiplier summary text file.

    The function reads the file, identifies the band headers, and processes
    each two-line entry. For every non-zero QSO count in an entry, it
    creates a (Multiplier, Band) tuple.

    Args:
        filename: The path to the input text file.

    Returns:
        A list of (Multiplier, Band) tuples, or None if an error occurs.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File not found at '{filename}'")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while reading the file: {e}")
        return None

    band_headers = []
    # First, find the header line to determine the band names
    for line in lines:
        if line.strip().startswith("STPROV"):
            # Extract the six band names between STPROV and Total
            band_headers = [f"{b}M" for b in line.strip().split()[1:-1]]
            break

    if not band_headers:
        print("Error: Could not find the 'STPROV' header row in the file.")
        return None

    result_list: List[Tuple[str, str]] = []
    # Iterate through the lines to find the data entries
    for i, line in enumerate(lines):
        # A data line is indented and starts with "8P5A:"
        if line.strip().startswith("8P5A:"):
            # The multiplier name is on the previous line
            if i > 0:
                multiplier = lines[i-1].strip()
                # Ensure the multiplier line is a simple word (e.g., "AB", "AL")
                if re.fullmatch(r'[A-Z]+', multiplier):
                    try:
                        # Parse the numbers, ignoring the callsign label and the final "Total"
                        numbers_str = line.split(':')[1].strip().split()[:6]
                        qso_counts = [int(n) for n in numbers_str]

                        # Create a tuple for each non-zero entry
                        for j, count in enumerate(qso_counts):
                            if count > 0:
                                band_name = band_headers[j]
                                result_list.append((band_name, multiplier))
                    except (ValueError, IndexError):
                        # Skip malformed data lines
                        continue
                        
    return result_list


import re
from typing import List, Tuple, Optional

def parse_mult_file_to_tuples(filename: str) -> Optional[List[Tuple[str, str]]]:
    """
    Parses a text file of multipliers and their associated bands.

    The function reads a file where each line consists of a multiplier followed
    by a space and a comma-separated list of frequency identifiers. It maps
    these identifiers to band names and returns a list of (band, multiplier) tuples.

    Args:
        filename: The path to the input text file.

    Returns:
        A list of (band, multiplier) tuples, or None if an error occurs.
    """
    # Mapping of frequency identifiers to band names
    band_mapping = {
        '1.8': '160M',
        '3.5': '80M',
        '7': '40M',
        '14': '20M',
        '21': '15M',
        '28': '10M'
    }

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File not found at '{filename}'")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while reading the file: {e}")
        return None

    result_list: List[Tuple[str, str]] = []
    for line in lines:
        line = line.strip()
        # Skip blank lines or the header line
        if not line or line.lower().startswith('type='):
            continue

        # Split the line into the multiplier and the band numbers
        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            continue  # Skip malformed lines

        multiplier, bands_str = parts
        
        # Split the band numbers string and create tuples
        band_numbers = bands_str.split(',')
        for num in band_numbers:
            band_name = band_mapping.get(num.strip())
            if band_name:
                result_list.append((band_name, multiplier))

    return result_list



if __name__=="__main__":
    print (argv)
    
    js_tuples = parse_json_to_tuples(argv[1])
    txt_tuples = parse_summary_to_tuples(argv[2])
    
    print (argv[1] + ":")
    
    js_set = set(js_tuples)
    print (js_set)
    print (argv[2] + ":")
    txt_set = set(txt_tuples)
    print (txt_set)
    
    n1mm_tuples = parse_mult_file_to_tuples(argv[3])
    n1mm_set = set(n1mm_tuples)
    
    print ("js length:    {}".format(len(js_set)))
    print ("txt length:   {}".format(len(txt_set)))
    print ("n1mm length:  {}".format(len(n1mm_set)))

    print ("Symmetric Difference: (js vs txt)")
    print (js_set ^ txt_set)
    
    print ("Symmetric Difference: (n1mm vs txt)")
    print (n1mm_set ^ txt_set)