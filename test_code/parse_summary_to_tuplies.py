import re
from typing import List, Tuple, Optional

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

# --- Example Usage ---
if __name__ == '__main__':
    # Create a dummy text file for demonstration
    dummy_filename = "example_summary.txt"
    dummy_data = """--- Multiplier Summary: STPROV ---
                 2024 ARRL-DX-CW - 8P5A                

STPROV    160     80     40     20     15     10  Total
-------------------------------------------------------
AB    
  8P5A:      3      6      9     12     13     13     56
AL    
  8P5A:      3      9     13     13     18     20     76
YT    
  8P5A:      0      1      1      1      0      0      3
-------------------------------------------------------
Total 
  8P5A:    308    739   1135   1340   1684   1925   7131
"""
    with open(dummy_filename, 'w') as f:
        f.write(dummy_data)

    print(f"--- Analyzing dummy file: '{dummy_filename}' ---")
    
    # Call the function with the dummy filename
    list_of_tuples = parse_summary_to_tuples(dummy_filename)

    if list_of_tuples is not None:
        print("Successfully parsed the file. Result:")
        for tpl in list_of_tuples:
            print(tpl)
    else:
        print("Function failed to return data due to an error.")

    # Clean up the dummy file
    import os
    os.remove(dummy_filename)