# Implementation Plan - Footer and Copyright Standardization

**Version:** 1.0.0
**Target:** 0.115.3-Beta

## 1. File Identification
* **File 1:** `contest_tools/templates/base.html` (Baseline: 0.102.0-Beta)
* **File 2:** `contest_tools/reports/_report_utils.py` (Baseline: 0.107.0-Beta)
* **File 3:** `contest_tools/reports/text_rate_sheet.py` (Baseline: 2.0.1)
* **File 4:** `contest_tools/reports/text_score_report.py` (Baseline: 0.92.0-Beta)
* **File 5:** `contest_tools/reports/text_rate_sheet_comparison.py` (Baseline: 2.1.1)
* **File 6:** `contest_tools/reports/text_comparative_score_report.py` (Baseline: 0.113.0-Beta)
* **File 7:** `contest_tools/reports/text_summary.py` (Baseline: 0.90.0-Beta)
* **File 8:** `contest_tools/reports/text_continent_breakdown.py` (Baseline: 0.90.0-Beta)
* **File 9:** `contest_tools/reports/text_continent_summary.py` (Baseline: 0.90.0-Beta)
* **File 10:** `contest_tools/reports/text_missed_multipliers.py` (Baseline: 0.113.0-Beta)
* **File 11:** `contest_tools/reports/text_wae_score_report.py` (Baseline: 0.91.4-Beta)
* **File 12:** `contest_tools/reports/text_wae_comparative_score_report.py` (Baseline: 0.113.0-Beta)
* **File 13:** `contest_tools/reports/text_qso_comparison.py` (Baseline: 0.90.1-Beta)
* **File 14:** `contest_tools/reports/text_comparative_continent_summary.py` (Baseline: 0.113.0-Beta)

## 2. Surgical Changes

### A. Web Application (`base.html`)
I will tighten the footer spacing to eliminate the "grey area above" and enforce the "one blank line" padding.
* **Change:** Replace `py-4 mt-5 border-top` with `py-3 mt-0 border-top bg-light`.
    * `mt-0`: Removes the ~3rem top margin.
    * `py-3`: Sets vertical padding to 1rem (approx one line height top/bottom).
    * `bg-light`: Ensures the pale gray background.

### B. Utility Update (`_report_utils.py`)
I will add a centralized function to generate the standard text footer.
* **Add:** `get_copyright_footer() -> str` which returns `"\n\nCopyright (c) 2025 Mark Bailey, KD4D\n"`.

### C. Text Reports (Files 3-14)
I will systematically update the `generate` method in each text report to append the copyright footer.
* **Pattern:** `report_content = ... + get_copyright_footer()`
* **Import:** Add `from ._report_utils import get_copyright_footer` (or modify existing import).

## 3. Surgical Change Verification (`diff`)

**(Excerpt showing `base.html` and representative text report changes)**

```text
--- BEGIN DIFF ---
--- contest_tools/templates/base.html
+++ contest_tools/templates/base.html
@@ -23,7 +23,7 @@
 
     {% block content %}{% endblock %}
 
-    <footer class="text-center text-muted py-4 mt-5 border-top">
+    <footer class="text-center text-muted py-3 mt-0 border-top bg-light">
         <div class="container">
             <p class="mb-0 small">Copyright &copy; 2025 by Mark Bailey, KD4D</p>
         </div>

--- contest_tools/reports/_report_utils.py
+++ contest_tools/reports/_report_utils.py
@@ -14,6 +14,8 @@
 #
 # --- Revision History ---
+# [0.115.3-Beta] - 2025-12-15
+# - Added `get_copyright_footer` to standardize text report footers.
 # [0.107.0-Beta] - 2025-12-14
 # - Updated `_sanitize_filename_part` to enforce strict lowercase conversion.
 # [0.106.0-Beta] - 2025-12-13
@@ -35,6 +37,9 @@
 from ..contest_log import ContestLog
 from ..utils.json_encoders import NpEncoder
 
+def get_copyright_footer() -> str:
+    """Returns the standardized copyright footer text (1 blank line, text, 1 blank line)."""
+    return "\n\nCopyright (c) 2025 Mark Bailey, KD4D\n"
+
 def get_valid_dataframe(log: ContestLog, include_dupes: bool = False) -> pd.DataFrame:
     """Returns a safe copy of the log's DataFrame, excluding dupes unless specified."""
     df = log.get_processed_data()

--- contest_tools/reports/text_rate_sheet.py
+++ contest_tools/reports/text_rate_sheet.py
@@ -20,13 +20,13 @@
 import pandas as pd
 import os
 from ..contest_log import ContestLog
 from .report_interface import ContestReport
-from ..data_aggregators.time_series import TimeSeriesAggregator
+from ._report_utils import get_copyright_footer
+from ..data_aggregators.time_series import TimeSeriesAggregator
 
 class Report(ContestReport):
     """
@@ -118,7 +118,7 @@
             footer = f"Gross QSOs={gross_qsos}     Dupes={dupes}     Net QSOs={display_net}"
 
             # --- Assembly ---
-            full_content = "\n\n".join(report_blocks) + "\n\n" + footer + "\n"
+            full_content = "\n\n".join(report_blocks) + "\n\n" + footer + get_copyright_footer()
             
             os.makedirs(output_path, exist_ok=True)
             filename = f"{self.report_id}_{callsign}.txt"
--- END DIFF ---