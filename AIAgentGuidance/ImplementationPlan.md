# Implementation Plan - QSO Breakdown Chart Header Fix

**Version:** 1.0.0
**Target:** 0.115.2-Beta

## 1. File Identification
* **File:** `contest_tools/reports/chart_qso_breakdown.py`
* **Baseline Version:** 0.115.1-Beta

## 2. Surgical Changes
I will modify `contest_tools/reports/chart_qso_breakdown.py` to increase the top margin of the chart layout.

1.  **Layout Configuration Update (in `generate`):**
    * Locate the `fig.update_layout` call under the "Specific Adjustments" comment.
    * Add `margin=dict(t=140)` to the arguments.
    * This reserves 140px at the top, providing sufficient clearance for the two-line title and the first row of subplot headers.

## 3. Surgical Change Verification (`diff`)

```text
--- BEGIN DIFF ---
--- contest_tools/reports/chart_qso_breakdown.py
+++ contest_tools/reports/chart_qso_breakdown.py
@@ -14,6 +14,8 @@
 # file, You can obtain one at [http://mozilla.org/MPL/2.0/](http://mozilla.org/MPL/2.0/).
 #
 # --- Revision History ---
+# [0.115.2-Beta] - 2025-12-15
+# - Increased top margin to 140px to prevent the two-line header from overlapping subplot titles.
 # [0.115.1-Beta] - 2025-12-15
 # - Standardized chart header to the two-line format (Report Name + Context).
 # - Optimized x-axis labels ("Unique Call" -> "Call", "Common (Both)" -> "Common")
@@ -134,7 +136,8 @@
         
         # Specific Adjustments
         fig.update_layout(
-            barmode='stack'
+            barmode='stack',
+            margin=dict(t=140) # Increased top margin to prevent title overlap
         )
 
         create_output_directory(output_path)
--- END DIFF ---