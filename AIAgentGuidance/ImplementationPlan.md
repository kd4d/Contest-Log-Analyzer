# ImplementationPlan.md

**Version:** 1.2.0
**Target:** 0.139.2-Beta

## 1. File Identification
* **File:** `web_app/analyzer/views.py`
* **Baseline Version:** 0.139.1-Beta

## 2. Surgical Changes
The objective is to fix a logic ordering error in `multiplier_dashboard` where the parsed `mult_type` variable is overwritten with `None` immediately after being extracted, causing all reports to be grouped under a single "None" key.

### A. Variable Scope Correction (Lines ~1660-1675)
* **Action:** Move the initialization of `mult_type` and `report_key` to the *start* of the loop iteration, ensuring they are reset before processing the next artifact but *not* overwriting the result of the parsing logic.
* **Logic:**
    1.  Initialize `mult_type = None` and `report_key = None` immediately after checking `target_ids`.
    2.  Parse the filename to extract `mult_type`.
    3.  Proceed to mapping logic.

## 3. Surgical Change Verification (`diff`)

--- BEGIN DIFF ---
--- web_app/analyzer/views.py
+++ web_app/analyzer/views.py
@@ -1662,18 +1662,18 @@
         if rid not in target_ids: continue
         
+        mult_type = None
+        report_key = None
+        
         # Extract Mult Type from Filename: {report_id}_{MULT_TYPE}_{combo_id}.txt
         fname = os.path.basename(art['path'])
         # Strip extension
         base = os.path.splitext(fname)[0]
         # Strip suffix
         if base.endswith(suffix):
             base = base[:-len(suffix)]
         # Strip prefix
         if base.startswith(rid + '_'):
             mult_type_slug = base[len(rid)+1:]
             mult_type = mult_type_slug.replace('_', ' ').title()
         else:
             continue
 
-        mult_type = None
-        report_key = None
-
         # Solo Mode Mapping Logic
         if log_count == 1:
--- END DIFF ---

## 3.a. Ground Truth Declaration
I declare that the `diff` above is generated against the definitive baseline version of `web_app/analyzer/views.py` (Version 0.139.1-Beta).

## 4. Affected Modules Checklist
* `web_app/analyzer/views.py`: **Target** (Fixing `multiplier_dashboard`).

## 5. Pre-Flight Check
* **Inputs:** `session_id`.
* **Expected Outcome:** The Multiplier Dashboard will display separate cards for "Countries", "Zones", etc., instead of a single card titled "None".
* **Mental Walkthrough:**
    1.  Loop starts for artifact (e.g., `missed_multipliers_countries...`).
    2.  Variables initialized to None.
    3.  Parsing logic runs -> `mult_type` becomes "Countries".
    4.  The erroneous overwrite lines are GONE.
    5.  Mapping logic runs using `mult_type="Countries"`.
    6.  Report registered correctly.
* **Safety:** The change is purely structural (moving lines up) and corrects a blatant shadowing bug.

## 6. Post-Generation Verification
I confirm that this plan contains the Metadata Header, Surgical Changes, `diff` verification, and Pre-Flight Check required by Protocol 2.5.