# Implementation Plan - Fix Dashboard Band Sorting

**Version:** 1.2.0
**Target:** 0.135.2-Beta

### 1. File Identification
**File:** `web_app/analyzer/views.py`
**Version:** 0.135.1-Beta

### 2. Surgical Changes
The file naming convention used by the report generator creates filenames like `qso_rate_plots_160_cw...` (numeric band only), but the `BAND_SORT_ORDER` dictionary expects keys like `160M`. This mismatch causes the lookup to fail, resulting in a default sort value of 99 and incorrect ordering in the dashboard tabs.

We will inject a normalization step in both plot discovery loops (`point_plots` and `qso_band_plots`) to ensure numeric band segments are converted to the expected format (e.g., `160` -> `160M`).

**Logic Injection:**
1.  In `qso_dashboard`, locate the parsing block for `point_plots`.
2.  After extracting `band_key`, check `if band_key.isdigit(): band_key += 'M'`.
3.  Repeat this logic for the `qso_band_plots` parsing block.

### 3. Surgical Change Verification (`diff`)

```text
--- BEGIN DIFF ---
--- web_app/analyzer/views.py
+++ web_app/analyzer/views.py
@@ -2079,6 +2079,9 @@
                     
                     if parts:
                         band_key = parts[0].upper()
+                        # Normalize numeric bands to match sort keys (160 -> 160M)
+                        if band_key.isdigit():
+                            band_key += 'M'
                         label = "All Bands" if band_key == 'ALL' else band_key
                         
                         sort_val = BAND_SORT_ORDER.get(band_key, 99)
@@ -2088,6 +2091,9 @@
                     
                     if parts:
                         band_key = parts[0].upper()
+                        # Normalize numeric bands to match sort keys (160 -> 160M)
+                        if band_key.isdigit():
+                            band_key += 'M'
                         
                         # Skip "ALL" bands since it is in the top pane
                         if band_key == 'ALL':
--- END DIFF ---