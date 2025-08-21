import re
import os
import sys

def analyze_adif_log(filename, log_type):
    """
    Analyzes an ADIF file to extract two key pieces of information:
    1. A set of (band, call, mult) for QSOs explicitly flagged as new multipliers.
    2. A dictionary mapping the first occurrence of each (band, mult) to its QSO data.
    
    :param filename: The ADIF file to parse.
    :param log_type: 'n1mm' or 'cla'.
    :return: A tuple containing (flagged_qso_set, first_mult_occurrence_dict).
    """
    flagged_qsos = set()
    first_mults = {} # {(band, mult): {qso_data_dict}, ...}
    
    if not os.path.exists(filename):
        print(f"!!! ERROR: File not found: {filename}")
        return None, None

    with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    try:
        qso_section = content.split('<EOH>')[1]
        qsos_raw = qso_section.strip().split('<EOR>')
    except IndexError:
        print(f"!!! ERROR: Could not find <EOH> header in {filename}")
        return set(), {}

    tag_regex = re.compile(r"<([A-Z0-9_]+):\d+>([^<]+)")

    for qso_str in qsos_raw:
        if not qso_str.strip():
            continue

        qso_data = dict(tag_regex.findall(qso_str.upper()))
        qso_data['__RAW_RECORD__'] = qso_str.strip() # Store the raw record

        # --- Part 1: Check for explicit "new multiplier" flags ---
        is_new_mult_flag = False
        if log_type == 'n1mm' and qso_data.get('APP_N1MM_MULT1') == '1':
            is_new_mult_flag = True
        elif log_type == 'cla' and qso_data.get('APP_CLA_STPROV_ISNEWMULT') == '1':
            is_new_mult_flag = True

        band = qso_data.get('BAND', '').strip().upper()
        call = qso_data.get('CALL', '').strip().upper()
        state = qso_data.get('STATE', '').strip()
        province = qso_data.get('VE_PROV', '').strip()
        multiplier_val = state if state else province

        if is_new_mult_flag and band and call and multiplier_val:
            flagged_qsos.add((band, call, multiplier_val))

        # --- Part 2: Track the first occurrence of any multiplier ---
        if band and multiplier_val:
            mult_key = (band, multiplier_val)
            if mult_key not in first_mults:
                first_mults[mult_key] = qso_data

    return flagged_qsos, first_mults

def main():
    if len(sys.argv) != 3:
        print("Usage: python compare_mults.py <n1mm_log_file.adi> <cla_log_file.adi>")
        sys.exit(1)

    n1mm_log_file, cla_log_file = sys.argv[1], sys.argv[2]
    
    print("--- ADIF Multiplier Comparison Script ---")
    print(f"N1MM File: {n1mm_log_file}")
    print(f"CLA File:  {cla_log_file}\n")

    n1mm_flagged_qsos, n1mm_first_mults = analyze_adif_log(n1mm_log_file, 'n1mm')
    cla_flagged_qsos, cla_first_mults = analyze_adif_log(cla_log_file, 'cla')

    if n1mm_flagged_qsos is None or cla_flagged_qsos is None:
        print("\nAnalysis aborted due to file error.")
        return

    # --- Analysis 1: Compare QSOs explicitly flagged as new multipliers ---
    print("--- Analysis 1: QSOs Flagged as New Multipliers ---")
    print(f"Found {len(n1mm_flagged_qsos)} QSOs flagged as new in N1MM log.")
    print(f"Found {len(cla_flagged_qsos)} QSOs flagged as new in CLA log.")
    
    n1mm_only_flagged = sorted(list(n1mm_flagged_qsos - cla_flagged_qsos))
    cla_only_flagged = sorted(list(cla_flagged_qsos - n1mm_flagged_qsos))

    if n1mm_only_flagged:
        print(f"\n[!] QSOs flagged as a new multiplier in N1MM ONLY ({len(n1mm_only_flagged)}):")
        print("    BAND  CALL      MULT")
        print("    ----- --------- ----")
        for band, call, mult in n1mm_only_flagged:
            print(f"    {band.ljust(5)} {call.ljust(9)} {mult}")
    
    if cla_only_flagged:
        print(f"\n[!] QSOs flagged as a new multiplier in CLA ONLY ({len(cla_only_flagged)}):")
        print("    BAND  CALL      MULT")
        print("    ----- --------- ----")
        for band, call, mult in cla_only_flagged:
            print(f"    {band.ljust(5)} {call.ljust(9)} {mult}")
    
    if not n1mm_only_flagged and not cla_only_flagged:
        print("\n[SUCCESS] The sets of flagged multiplier QSOs are identical.")

    print("\n" + "="*50 + "\n")

    # --- Analysis 2: Compare the final calculated set of multipliers ---
    print("--- Analysis 2: Final Multiplier Set Comparison ---")
    n1mm_mult_set = set(n1mm_first_mults.keys())
    cla_mult_set = set(cla_first_mults.keys())

    print(f"Final unique multiplier count for N1MM: {len(n1mm_mult_set)}")
    print(f"Final unique multiplier count for CLA:  {len(cla_mult_set)}")
    
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
                flag_val = qso_info.get('APP_N1MM_MULT1', 'NOT_SET')
                print(f"  > Call: {qso_info.get('CALL', 'N/A')}, Flag <APP_N1MM_MULT1> value: {flag_val}")
                print(f"  > Record: {qso_info.get('__RAW_RECORD__')}")
            
            if (band, mult) in cla_mult_set:
                print("  Found in CLA log. First QSO credited:")
                qso_info = cla_first_mults[(band, mult)]
                flag_val = qso_info.get('APP_CLA_STPROV_ISNEWMULT', 'NOT_SET')
                print(f"  > Call: {qso_info.get('CALL', 'N/A')}, Flag <APP_CLA_STPROV_ISNEWMULT> value: {flag_val}")
                print(f"  > Record: {qso_info.get('__RAW_RECORD__')}")

    print("\n\n--- Analysis Complete ---")

if __name__ == "__main__":
    main()