# Contest Log Analyzer/test_code/missed_mults_formatter_prototype.py
#
# Version: 1.6.2-Beta
# Date: 2025-08-27
#
# Purpose: A standalone prototype script to validate the fixed-width
#          formatting logic. This version uses the `prettytable` library
#          and hardcoded data to ensure perfect table alignment.
#
# --- Revision History ---
## [1.6.2-Beta] - 2025-08-27
### Fixed
# - Corrected the title-centering logic by adding a dummy row to the
#   table used for the width calculation. This ensures the calculated
#   width is accurate.
## [1.6.1-Beta] - 2025-08-27
### Changed
# - Modified the create_table helper function to accept an alignment
#   parameter for the first column.
# - The summary table's row labels ("Worked:", etc.) are now
#   right-justified as requested.
## [1.6.0-Beta] - 2025-08-27
### Changed
# - Replaced the `tabulate` library with `prettytable` to allow for
#   direct, programmatic control over column widths.
# - The script now creates PrettyTable objects and explicitly sets the
#   width of each column, guaranteeing a uniform layout.
# ... previous history truncated ...

from prettytable import PrettyTable

def generate_report_prototype():
    """
    Generates a prototype of the Missed Multipliers report with fixed-width tables.
    """
    # --- 1. Hardcoded, Display-Ready Mock Data ---
    headers = ['Stprov', '8P5A', 'ZF1A']
    bands = ["160M", "80M", "40M", "20M", "15M", "10M"]

    mock_main_data = [
        ('160M', 'AZ (Arizona)', '0', '(Run) 2'), ('160M', 'CA (California)', '0', '(Run) 4'),
        ('160M', 'IA (Iowa)', '0', '(Run) 1'), ('160M', 'IL (Illinois)', '0', '(Run) 1'),
        ('160M', 'IN (Indiana)', '0', '(Run) 2'), ('160M', 'KS (Kansas)', '0', '(Run) 1'),
        ('160M', 'KY (Kentucky)', '0', '(Run) 3'), ('160M', 'LA (Louisiana)', '0', '(Run) 1'),
        ('160M', 'ME (Maine)', '0', '(Run) 1'), ('160M', 'MI (Michigan)', '0', '(Run) 5'),
        ('160M', 'MN (Minnesota)', '0', '(Run) 1'), ('160M', 'MO (Missouri)', '0', '(Run) 2'),
        ('160M', 'OH (Ohio)', '0', '(Run) 6'), ('160M', 'OK (Oklahoma)', '0', '(S&P) 1'),
        ('160M', 'ON (Ontario)', '0', '(Unk) 1'), ('160M', 'RI (Rhode Island)', '0', '(Run) 1'),
        ('160M', 'SC (South Carolina)', '0', '(Run) 3'), ('160M', 'SK (Saskatchewan)', '0', '(Run) 1'),
        ('160M', 'TN (Tennessee)', '0', '(Run) 4'), ('160M', 'UT (Utah)', '0', '(Run) 1'),
        ('160M', 'WI (Wisconsin)', '0', '(Run) 3'), ('160M', 'WV (West Virginia)', '0', '(Run) 1'),
        ('80M', 'AB (Alberta)', '(Run) 1', '0'), ('80M', 'ID (Idaho)', '0', '(Run) 1'),
        ('80M', 'MB (Manitoba)', '0', '(Run) 1'), ('80M', 'NE (Nebraska)', '(Run) 2', '0'),
        ('80M', 'OK (Oklahoma)', '0', '(Run) 1'), ('80M', 'SK (Saskatchewan)', '0', '(Run) 1'),
        ('40M', 'LB (Labrador)', '(Run) 1', '0'), ('40M', 'WY (Wyoming)', '0', '(Run) 2'),
        ('40M', 'YT (Yukon)', '0', '(Run) 1'), ('20M', 'LB (Labrador)', '(Run) 1', '0'),
        ('15M', 'LB (Labrador)', '(Run) 1', '0'), ('15M', 'NT (Northwest Territories)', '0', '(Unk) 1'),
        ('10M', 'LB (Labrador)', '(Run) 1', '0'), ('10M', 'NT (Northwest Territories)', '0', '(Run) 1'),
    ]

    mock_summary_data = [
        ('160M', 'Worked:', '0', '22'), ('160M', 'Missed:', '22', '0'), ('160M', 'Delta:', '-22', ''),
        ('80M', 'Worked:', '2', '4'), ('80M', 'Missed:', '4', '2'), ('80M', 'Delta:', '-2', ''),
        ('40M', 'Worked:', '1', '2'), ('40M', 'Missed:', '2', '1'), ('40M', 'Delta:', '-1', ''),
        ('20M', 'Worked:', '1', '0'), ('20M', 'Missed:', '0', '1'), ('20M', 'Delta:', '', '-1'),
        ('15M', 'Worked:', '1', '1'), ('15M', 'Missed:', '1', '1'), ('15M', 'Delta:', '', ''),
        ('10M', 'Worked:', '1', '1'), ('10M', 'Missed:', '1', '1'), ('10M', 'Delta:', '', ''),
    ]

    # --- 2. Pass 1: Global Sizing ---
    col_widths = {h: len(h) for h in headers}
    for row in mock_main_data:
        for i, header in enumerate(headers):
            col_widths[header] = max(col_widths[header], len(row[i + 1]))
    for row in mock_summary_data:
        for i, header in enumerate(headers):
            col_widths[header] = max(col_widths[header], len(row[i + 1]))

    # --- 3. Pass 2: Formatting and Printing ---
    def create_table(header_list, width_dict, first_col_align='l'):
        table = PrettyTable()
        table.field_names = header_list
        table.align[header_list[0]] = first_col_align
        for header in header_list[1:]:
            table.align[header] = 'r'
            # Set a fixed width for each column
            table.max_width[header] = width_dict[header]
            table.min_width[header] = width_dict[header]
        table.max_width[header_list[0]] = width_dict[header_list[0]]
        table.min_width[header_list[0]] = width_dict[header_list[0]]
        return table

    # Use a dummy table to calculate the total report width for centering the title
    dummy_table = create_table(headers, col_widths)
    dummy_table.add_row(['' for _ in headers]) # Add one row to ensure correct width calculation
    max_line_width = len(str(dummy_table).split('\n')[0])

    title1 = "--- Missed Multipliers Report: STPROV ---"
    title2 = "2025 ARRL-DX-SSB - 8P5A, ZF1A"
    print(title1.center(max_line_width))
    print(title2.center(max_line_width))

    for band in bands:
        main_data_for_band = [row[1:] for row in mock_main_data if row[0] == band]
        summary_data_for_band = [row[1:] for row in mock_summary_data if row[0] == band]

        if not main_data_for_band: continue
        
        print(f"\n{band.replace('M', '')} Meters Missed Multipliers")

        main_table = create_table(headers, col_widths)
        for row in main_data_for_band:
            main_table.add_row(row)

        summary_table = create_table(headers, col_widths, first_col_align='r')
        for row in summary_data_for_band:
            summary_table.add_row(row)

        # Get string representations and stitch them together
        main_lines = str(main_table).split('\n')
        summary_lines = str(summary_table).split('\n')
        
        # Print main table without its bottom border
        print('\n'.join(main_lines[:-1]))
        # Print summary table starting from its header separator line
        print('\n'.join(summary_lines[2:]))

if __name__ == "__main__":
    generate_report_prototype()