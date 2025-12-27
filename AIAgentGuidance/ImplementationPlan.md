**Version:** 1.0.0
**Target:** 0.143.0-Beta

# Implementation Plan - Enforce Fixed Height for HTML Charts

## 1. File Identification
* **File:** `contest_tools/reports/chart_qso_breakdown.py`
* **Baseline Version:** 0.142.0-Beta (As provided in latest upload)

## 2. Surgical Changes
I will modify the HTML generation logic to enforce a deterministic height for the interactive chart. This resolves the race condition in the Dashboard's "Hidden DOM" layout calculation that leads to scrollbars on non-active tabs.

1.  **Enforce Fixed Height:** Update the `fig.layout.height` assignment in the HTML export block. Instead of setting it to `None` (which triggers autosizing and the race condition), I will set it to `400 * rows`. This matches the calculation used for the PNG export and ensures the Dashboard iframe can detect the correct content size immediately upon loading.

## 3. Surgical Change Verification (`diff`)
```text
--- BEGIN DIFF ---
--- contest_tools/reports/chart_qso_breakdown.py
+++ contest_tools/reports/chart_qso_breakdown.py
@@ -19,6 +19,9 @@
 #
 # --- Revision History ---
+# [0.143.0-Beta] - 2025-12-27
+# - Enforced fixed height (400 * rows) for HTML export to prevent dashboard
+#   scrollbar race conditions in hidden tabs.
 # [0.142.0-Beta] - 2025-12-27
 # - Increased subplot vertical_spacing to 0.15 to prevent label overlap.
 # - Reduced X-axis title_standoff to 5 to tighten Band Label placement.
@@ -177,7 +180,7 @@
         html_file = os.path.join(output_path, f"{base_filename}.html")
         
         # Force removal of fixed dimensions to enable responsive sizing
-        fig.layout.height = None
+        # UPDATE: Enforce fixed height to prevent dashboard scrollbar race condition
+        fig.layout.height = 400 * rows
         fig.layout.width = None
         
         # Optimize margins for dashboard display
--- END DIFF ---