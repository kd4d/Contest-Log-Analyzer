**Version:** 1.0.0
**Target:** 0.129.1-Beta

# Implementation Plan - Fix Rate Differential Band Linking

## 1. File Identification
* [cite_start]`web_app/analyzer/views.py` (Version 0.129.0-Beta) [cite: 1596]
* [cite_start]`web_app/analyzer/templates/analyzer/qso_dashboard.html` (Existing) [cite: 1820]

## 2. Surgical Changes

### `web_app/analyzer/views.py`
* **Function:** `qso_dashboard`
* **Logic:** Update the file path construction loop for `DIFF_BANDS`.
* **Change:** Replace the use of `band_slug` in the directory path with the raw `band` variable (e.g., "160M" instead of "160") to match the Report Generator's output structure.

### `web_app/analyzer/templates/analyzer/qso_dashboard.html`
* **Block:** `script` (updateDiffContent function)
* **Logic:** Replace fragile `dataset` property access with robust `getAttribute` calls to retrieve data attributes containing hyphens or numbers (e.g., `data-diff-160`).

## 3. Surgical Change Verification (`diff`)

**File: `web_app/analyzer/views.py`**
__CODE_BLOCK__text
--- web_app/analyzer/views.py
+++ web_app/analyzer/views.py
@@ -1637,7 +1637,7 @@
                 # The view helper usually puts band files in subdirs unless it's ALL
                 if band != 'ALL':
-                    file_rel = os.path.join(base_path, f"plots/{band_slug}/{filename}")
+                    file_rel = os.path.join(base_path, f"plots/{band}/{filename}")
                 else:
                     file_rel = os.path.join(base_path, f"plots/{filename}")
__CODE_BLOCK__

**File: `web_app/analyzer/templates/analyzer/qso_dashboard.html`**
__CODE_BLOCK__text
--- web_app/analyzer/templates/analyzer/qso_dashboard.html
+++ web_app/analyzer/templates/analyzer/qso_dashboard.html
@@ -1844,9 +1844,9 @@
             if (!currentStratBtn) return;
             // Try to find specific band path, fallback to all, fallback to blank
             // Dataset properties are camelCase (data-diff-160 -> diff160)
-            let diffSrc = currentStratBtn.dataset['diff' + currentDiffBand.charAt(0).toUpperCase() + currentDiffBand.slice(1)];
-            if (!diffSrc) diffSrc = currentStratBtn.dataset['diff' + currentDiffBand]; // Try lowercase
-            if (!diffSrc) diffSrc = currentStratBtn.dataset['diffAll'];
+            // Use getAttribute for robust retrieval of numeric keys (e.g. data-diff-160)
+            let diffSrc = currentStratBtn.getAttribute('data-diff-' + currentDiffBand);
+            if (!diffSrc) diffSrc = currentStratBtn.getAttribute('data-diff-all');
             // Fallback
             
             if (diffSrc) {
__CODE_BLOCK__

## 4. Affected Modules Checklist
* `web_app/analyzer/views.py` (Direct modification)
* `web_app/analyzer/templates/analyzer/qso_dashboard.html` (Direct modification)

## 5. Pre-Flight Check
* **Inputs:** `web_app/analyzer/views.py` (0.129.0-Beta), `qso_dashboard.html`.
* **Expected Outcome:** The view will correctly locate band-specific plots in `plots/160M/` (etc.) instead of `plots/160/`. The JavaScript will reliably retrieve the correct URL for numeric bands like "160" or "80".
* **Mental Walkthrough:**
    1.  User clicks "160" button. `currentDiffBand` becomes "160".
    2.  `updateDiffContent` calls `getAttribute('data-diff-160')`.
    3.  This attribute will contain the URL found by the Python view using the corrected path logic.
    4.  Iframe source updates to the specific band plot.
* **Backward Compatibility:** No impact on other dashboards.
* **Syntax Validation:** Python and JavaScript syntax verified.

## 6. Post-Generation Verification
I confirm this plan adheres to Protocol 2.5 and addresses the root cause identified in the Error Analysis.