import re
import os
import sys
import argparse
from collections import Counter

def analyze_adif_log(filename, suppress_zeros=False):
    """
    Analyzes an ADIF file to extract a dictionary mapping the first 
    occurrence of each (band, mult) to its QSO data.
    :param filename: The ADIF file to parse.
    :param suppress_zeros: If True, QSOs with 0 points are ignored.
    :return: A dictionary mapping (band, mult) to its first QSO data.
    """
    first_mults = {} # {(band, mult): {qso_data_dict}, ...}
    
    if not os.path.exists(filename):
        print(f"!!! ERROR: File not found: {filename}")
        return None

    with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    try:
        qso_section = content.split('<EOH>')[1]
        qsos_raw = qso_section.strip().split('<EOR>')
    except IndexError:
        print(f"!!! ERROR: Could not find <EOH> header in {filename}")
        return {}

    tag_regex = re.compile(r"<([A-Z0-9_]+):\d+>([^<]+)")

    for qso_str in qsos_raw:
        if not qso_str.strip():
            continue

        qso_data = dict(tag_regex.findall(qso_str.upper()))
        qso_data['__RAW_RECORD__'] = qso_str.strip()

        if suppress_zeros:
            n1mm_points = qso_data.get('APP_N1MM_POINTS')
            cla_points = qso_data.get('APP_CLA_QSO_POINTS')
            
            if (n1mm_points is not None and int(n1mm_points) == 0) or \
               (cla_points is not None and int(cla_points) == 0):
                continue

        band = qso_data.get('BAND', '').strip().upper()
        state = qso_data.get('STATE', '').strip()
        province = qso_data.get('VE_PROV', '').strip()
        multiplier_val = state if state else province

        if band and multiplier_val:
            mult_key = (band, multiplier_val)
            if mult_key not in first_mults:
                first_mults[mult_key] = qso_data

    return first_mults

def main():
    parser = argparse.ArgumentParser(description="Compare multipliers in two ADIF log files for ARRL DX.")
    parser.add_argument("n1mm_log_file", help="The file path for the N1MM ADIF log.")
    parser.add_argument("cla_log_file", help="The file path for the CLA-generated ADIF log.")
    parser.add_argument("--nozero", action="store_true", help="Suppress QSOs with zero points from multiplier counts.")
    args = parser.parse_args()
    
    print("--- ADIF Multiplier Comparison Script ---")
    print(f"N1MM File: {args.n1mm_log_file}")
    print(f"CLA File:  {args.cla_log_file}")
    if args.nozero:
        print("Mode:      Ignoring zero-point QSOs")
    print("")

    n1mm_first_mults = analyze_adif_log(args.n1mm_log_file, args.nozero)
    cla_first_mults = analyze_adif_log(args.cla_log_file, args.nozero)

    if n1mm_first_mults is None or cla_first_mults is None:
        print("\nAnalysis aborted due to file error.")
        return

    n1mm_mult_set = set(n1mm_first_mults.keys())
    cla_mult_set = set(cla_first_mults.keys())

    # --- New: Per-Band Count Logic ---
    n1mm_band_counts = Counter(band for band, mult in n1mm_mult_set)
    cla_band_counts = Counter(band for band, mult in cla_mult_set)
    all_bands = sorted(list(set(n1mm_band_counts.keys()) | set(cla_band_counts.keys())))

    print("--- Per-Band Unique Multiplier Counts ---")
    header = f"{'Band':<6} {'N1MM ADIF':>10} {'CLA ADIF':>10}"
    print(header)
    print('-' * len(header))
    for band in all_bands:
        n1mm_count = n1mm_band_counts.get(band, 0)
        cla_count = cla_band_counts.get(band, 0)
        print(f"{band:<6} {n1mm_count:>10} {cla_count:>10}")
    print('-' * len(header))
    print(f"{'Total':<6} {len(n1mm_mult_set):>10} {len(cla_mult_set):>10}\n")


    # --- Analysis: Compare the final calculated set of multipliers ---
    print("--- Detailed Multiplier Set Comparison ---")
    
    discrepancies = n1mm_mult_set.symmetric_difference(cla_mult_set)

    if not discrepancies:
        print("\n[SUCCESS] The final multiplier sets are identical.")
    else:
        print(f"\n[!] Found {len(discrepancies)} discrepancies in the final multiplier sets.")
        for band, mult in sorted(list(discrepancies)):
            print("\n" + "-"*25)
            print(f"Discrepancy: {mult} on {band}")
            print("-" * 25)
            
            if (band, mult) in n1mm_mult_set:
                print("  Found in N1MM log. First QSO credited:")
                qso_info = n1mm_first_mults[(band, mult)]
                print(f"  > Call: {qso_info.get('CALL', 'N/A')}")
                print(f"  > Record: {qso_info.get('__RAW_RECORD__')}")
            
            if (band, mult) in cla_mult_set:
                print("  Found in CLA log. First QSO credited:")
                qso_info = cla_first_mults[(band, mult)]
                print(f"  > Call: {qso_info.get('CALL', 'N/A')}")
                print(f"  > Record: {qso_info.get('__RAW_RECORD__')}")

    print("\n\n--- Analysis Complete ---")

if __name__ == "__main__":
    main()