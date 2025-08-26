# Contest Log Analyzer/test_code/html_table_prototype_generator.py
#
# Purpose: A standalone script to generate a styled HTML report from data,
#          serving as a prototype for web-based reporting.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-25
# Version: 1.0.7-Beta
#
# --- Revision History ---
# ## [1.0.7-Beta] - 2025-08-25
# - Removed the `min-w-full` class from the table's container div to
#   allow the table to dynamically size to its content.
# ## [1.0.6-Beta] - 2025-08-25
# - Removed the `w-full` class from the table to allow for dynamic,
#   content-based column sizing.
# ## [1.0.5-Beta] - 2025-08-25
# - Updated all internal "light" grid lines to a "medium" weight for
#   better visual consistency and clarity.
# ## [1.0.4-Beta] - 2025-08-25
# - Increased border contrast by using darker gray shades.
# - Added internal vertical dividers within the Unique and Common QSO groups.
# ## [1.0.3-Beta] - 2025-08-25
# - Replaced all custom CSS with Tailwind CSS utility classes to fix
#   border rendering conflicts and correctly implement the visual hierarchy.
# ## [1.0.2-Beta] - 2025-08-25
# - Refined CSS to create a hierarchical border system with "light" and
#   "dark" dividers for improved visual structure.
# ## [1.0.1-Beta] - 2025-08-25
# - Fixed a TypeError by correcting the mock data structure from a set
#   of dictionaries to a list of dictionaries.
# ## [1.0.0-Beta] - 2025-08-25
# - Initial release of the HTML generation prototype script.
#
import webbrowser
import os

def generate_html_report(report_data, output_filename="report.html"):
    """
    Generates a styled HTML report from a list of dictionaries.

    Args:
        report_data (list): A list of dictionaries, where each dictionary
                            represents a row in the table.
        output_filename (str): The name of the output HTML file.
    """

    # --- 1. Build the HTML for the table body ---
    table_rows_html = ""
    for i, row in enumerate(report_data):
        # The last row should not have a bottom border
        bottom_border_class = "" if i == len(report_data) - 1 else "border-b"
        
        table_rows_html += f"""
        <tr class="{bottom_border_class} border-gray-400">
            <td class="p-3 text-left font-medium border-r-2 border-r-gray-500 whitespace-nowrap">{row['call']}</td>
            <td class="p-3 text-right border-r border-gray-400">{row['total']:,}</td>
            <td class="p-3 text-right border-r border-gray-400">{row['unique']:,}</td>
            <td class="p-3 text-right border-r-2 border-r-gray-500">{row['common']:,}</td>
            <td class="p-3 text-right border-r border-gray-400">{row['run_unique']:,}</td>
            <td class="p-3 text-right border-r border-gray-400">{row['sp_unique']:,}</td>
            <td class="p-3 text-right border-r-2 border-r-gray-500">{row['unk_unique']:,}</td>
            <td class="p-3 text-right border-r border-gray-400">{row['run_common']:,}</td>
            <td class="p-3 text-right border-r border-gray-400">{row['sp_common']:,}</td>
            <td class="p-3 text-right">{row['unk_common']:,}</td>
        </tr>
        """

    # --- 2. Define the full HTML structure as a template ---
    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QSO Comparison Report</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Inter', sans-serif;
        }}
    </style>
</head>
<body class="bg-gray-100 p-4 sm:p-8">
    <div class="max-w-7xl mx-auto bg-white p-6 rounded-lg shadow-md">
        <h1 class="text-2xl font-bold text-gray-800 mb-2">QSO Comparison Report</h1>
        <p class="text-gray-600">--- 20M ---</p>
        
        <div class="mt-8 overflow-x-auto">
            <div class="inline-block">
                <div class="overflow-hidden rounded-lg border-2 border-gray-500">
                    <table class="text-sm">
                        <thead class="bg-gray-50">
                            <!-- Top header row with merged cells -->
                            <tr>
                                <th rowspan="2" class="p-3 font-semibold text-center border-b-2 border-gray-500 border-r-2 border-r-gray-500"></th>
                                <th rowspan="2" class="p-3 font-semibold text-center border-b-2 border-gray-500 border-r border-gray-400">Total</th>
                                <th rowspan="2" class="p-3 font-semibold text-center border-b-2 border-gray-500 border-r border-gray-400">Unique</th>
                                <th rowspan="2" class="p-3 font-semibold text-center border-b-2 border-gray-500 border-r-2 border-r-gray-500">Common</th>
                                <th colspan="3" class="p-3 font-semibold text-center border-b border-gray-400 border-r-2 border-r-gray-500 whitespace-nowrap">Unique QSOs</th>
                                <th colspan="3" class="p-3 font-semibold text-center border-b border-gray-400 whitespace-nowrap">Common QSOs</th>
                            </tr>
                            <!-- Sub-header row -->
                            <tr>
                                <th class="p-3 font-semibold text-center border-b-2 border-gray-500 border-r border-gray-400">Run</th>
                                <th class="p-3 font-semibold text-center border-b-2 border-gray-500 border-r border-gray-400">S&P</th>
                                <th class="p-3 font-semibold text-center border-b-2 border-gray-500 border-r-2 border-r-gray-500">Unk</th>
                                <th class="p-3 font-semibold text-center border-b-2 border-gray-500 border-r border-gray-400">Run</th>
                                <th class="p-3 font-semibold text-center border-b-2 border-gray-500 border-r border-gray-400">S&P</th>
                                <th class="p-3 font-semibold text-center border-b-2 border-gray-500">Unk</th>
                            </tr>
                        </thead>
                        <tbody class="bg-white">
                            {table_rows_html}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
    """

    # --- 3. Write the final HTML to a file ---
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(html_template)
        print(f"Successfully generated report: '{output_filename}'")
        
        # --- 4. Open the file in the default web browser ---
        webbrowser.open('file://' + os.path.realpath(output_filename))

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Mock data
    mock_report_data = [
        {
            "call": "K1ABC", "total": 15230, "unique": 5110, "common": 10120,
            "run_unique": 4100, "sp_unique": 900, "unk_unique": 110,
            "run_common": 6000, "sp_common": 4000, "unk_common": 120
        },
        {
            "call": "W1XYZ", "total": 14500, "unique": 4380, "common": 10120,
            "run_unique": 3800, "sp_unique": 500, "unk_unique": 80,
            "run_common": 6100, "sp_common": 3900, "unk_common": 120
        }
    ]
    
    generate_html_report(mock_report_data)
