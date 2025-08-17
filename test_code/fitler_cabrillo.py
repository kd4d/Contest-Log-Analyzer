# filter_cabrillo.py
import sys
import os
import re

def filter_cabrillo_by_band(input_filepath: str):
    """
    Reads a Cabrillo log file and creates a new one containing only the records
    from the 40-meter band (7000-7300 kHz), preserving the header and trailer.

    Args:
        input_filepath (str): The path to the source Cabrillo log file.
    """
    try:
        with open(input_filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: Input file not found at '{input_filepath}'")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    header_lines = []
    qso_lines = []
    trailer_line = ""

    qso_pattern = re.compile(r'^QSO:\s*(\d+)', re.IGNORECASE)

    for line in lines:
        match = qso_pattern.match(line)
        if match:
            try:
                # Cabrillo frequency is in kHz
                frequency_khz = int(match.group(1))
                # Check if the frequency is within the 40m band (7000-7300 kHz)
                if 7000 <= frequency_khz <= 7300:
                    qso_lines.append(line)
            except (ValueError, IndexError):
                # Ignore lines with malformed frequencies
                continue
        elif line.strip().upper() == 'END-OF-LOG:':
            trailer_line = line
        else:
            # If it's not a QSO line or the trailer, it's a header line
            header_lines.append(line)

    if not qso_lines:
        print("No QSOs found on the 40-meter band. Output file not created.")
        return

    output_filename = f"{os.path.splitext(input_filepath)[0]}_40m.log"

    try:
        with open(output_filename, 'w', encoding='utf-8', newline='') as f_out:
            f_out.writelines(header_lines)
            f_out.writelines(qso_lines)
            if trailer_line:
                f_out.write(trailer_line)
        print(f"\nSuccessfully created filtered file: '{output_filename}'")
    except IOError as e:
        print(f"Error writing to output file: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python filter_cabrillo.py <path_to_cabrillo_file>")
        sys.exit(1)

    input_file = sys.argv[1]

    if not os.path.isfile(input_file):
        print(f"Error: The provided path is not a valid file: '{input_file}'")
        sys.exit(1)

    filter_cabrillo_by_band(input_file)