Newer WAE Plan 
# Implementation Plan: WAE Contest Integration

This implementation will be executed in two phases, followed by a final, separate migration phase to be addressed in a future task. This plan is designed for maximum safety and isolation to prevent regressions.

---
## **Stage 4 of 5: Implement Core WAE Scoring Architecture**
**Goal:** Introduce the new, pluggable scoring architecture without activating it for any contest. This ensures the existing codebase is not affected.

### **1. File 1 of 15: `contest_tools/score_calculators/calculator_interface.py` (New File)**
* **File Identification:** New file.
* **Surgical Changes:** Create a new file defining the abstract base class `TimeSeriesCalculator`. It will have one abstract method, `calculate(self, log: 'ContestLog') -> pd.DataFrame`, which establishes the contract for all score calculator modules.
* **Surgical Change Verification (`diff`):** Not applicable (new file).
* **Affected Modules Checklist:** This new interface will be implemented by `standard_calculator.py` and `wae_calculator.py`.

### **2. File 2 of 15: `contest_tools/score_calculators/standard_calculator.py` (New File)**
* **File Identification:** New file.
* **Surgical Changes:** Create the default `StandardCalculator` class which implements the `TimeSeriesCalculator` interface. Its `calculate` method will generate a DataFrame containing cumulative scores and QSO counts from the `QSOPoints` column, broken down by operating style (Run vs. S&P).
* **Surgical Change Verification (`diff`):** Not applicable (new file).
* **Affected Modules Checklist:** This will be the default calculator for non-WAE contests.

### **3. File 3 of 15: `contest_tools/score_calculators/wae_calculator.py` (New File)**
* **File Identification:** New file.
* **Surgical Changes:** Create the WAE-specific `WaeCalculator` class. Its `calculate` method will implement the WAE scoring formula: `(Total QSOs + Total QTCs) * Total Weighted Multipliers`, and apportion the final score into `run_score` and `sp_unk_score` columns.
* **Surgical Change Verification (`diff`):** Not applicable (new file).
* **Affected Modules Checklist:** This module will be called by `contest_log.py` for WAE logs.

### **4. File 4 of 15: `contest_tools/contest_definitions/__init__.py`**
* **File Identification:** `contest_tools/contest_definitions/__init__.py`, Version `0.56.29-Beta`
* **Surgical Changes:** Add three new properties to the `ContestDefinition` class to expose the new JSON keys to the application: `use_new_score_calculator`, `time_series_calculator`, and `points_header_label`.
* **Surgical Change Verification (`diff`):**
```cla-bundle
--- a/contest_tools/contest_definitions/__init__.py
+++ b/contest_tools/contest_definitions/__init__.py
@@ -131,6 +131,18 @@
     def custom_adif_exporter(self) -> Optional[str]:
         return self._data.get('custom_adif_exporter')
 
+    @property
+    def use_new_score_calculator(self) -> bool:
+        return self._data.get('use_new_score_calculator', False)
+
+    @property
+    def time_series_calculator(self) -> Optional[str]:
+        return self._data.get('time_series_calculator')
+        
+    @property
+    def points_header_label(self) -> Optional[str]:
+        return self._data.get('points_header_label')
+
     @property
     def contest_period(self) -> Optional[Dict[str, str]]:
         return self._data.get('contest_period')
```
* **Affected Modules Checklist:** This change allows `contest_log.py` to access the new configuration values.

### **5. File 5 of 15: `contest_tools/log_manager.py`**
* **File Identification:** `contest_tools/log_manager.py`, Version `0.70.2-Beta`
* **Surgical Changes:** Modify the `load_log` method to set the `_log_manager_ref` back-reference on the `ContestLog` object *before* calling `apply_annotations`.
* **Surgical Change Verification (`diff`):**
```cla-bundle
--- a/contest_tools/log_manager.py
+++ b/contest_tools/log_manager.py
@@ -81,9 +81,9 @@
             if not contest_name:
                 logging.warning(f"  - Could not determine contest name from file header. Skipping.")
                 return
 
             log = ContestLog(contest_name=contest_name, cabrillo_filepath=cabrillo_filepath, root_input_dir=root_input_dir)
             
-            log.apply_annotations()
+            # Set the back-reference BEFORE running annotations that might need it.
+            setattr(log, '_log_manager_ref', self)
+            
+            log.apply_annotations()
             
             self.logs.append(log)
             
```
* **Affected Modules Checklist:** This change corrects a bug in the interaction between `LogManager` and `ContestLog`, affecting all score calculators.

### **6. File 6 of 17: `contest_tools/contest_log.py`**
* **File Identification:** `contest_tools/contest_log.py`, Version `0.80.10-Beta`
* **Surgical Changes:** Add new attributes (`qtcs_df`, `time_series_score_df`). Modify `_ingest_cabrillo_data` to handle the WAE parser's return signature. Add a conditional block to `apply_annotations` that calls the new `_pre_calculate_time_series_score` method only if the `use_new_score_calculator` flag is true; otherwise, it executes the existing logic.
* **Affected Modules Checklist:** Core architectural change. This provides the feature flag mechanism.

---
## **Stage 5 of 5: Integrate into Reports and Finalize**
**Goal:** Activate the new architecture for WAE only, create WAE-specific reports, make existing reports WAE-aware, and update all user documentation.

### **7. File 7 of 17: `contest_tools/contest_definitions/wae_cw.json`**
* **File Identification:** `contest_tools/contest_definitions/wae_cw.json`, Version `0.76.0-Beta`
* **Surgical Changes:** Add the keys to activate the new scoring system: `"use_new_score_calculator": true`, `"time_series_calculator": "wae_calculator"`, and `"points_header_label": "QSO+QTC Pts"`.
* **Affected Modules Checklist:** This activates the new scoring path for the WAE CW contest.

### **8. File 8 of 17: `contest_tools/contest_definitions/wae_ssb.json`**
* **File Identification:** `contest_tools/contest_definitions/wae_ssb.json`, Version `0.76.0-Beta`
* **Surgical Changes:** Add the same three keys as in the WAE CW file to activate the new scoring system.
* **Affected Modules Checklist:** This activates the new scoring path for the WAE SSB contest.

### **9. File 9 of 17: `contest_tools/reports/plot_cumulative_difference.py`**
* **File Identification:** `contest_tools/reports/plot_cumulative_difference.py`, Version `0.57.7-Beta`
* **Surgical Changes:** Refactor the report to use the new `log.time_series_score_df`. Add conditional logic to generate a simplified single-panel plot for WAE, as its non-linear scoring makes the Run/S&P breakdown misleading.
* **Affected Modules Checklist:** This change makes the report dependent on the new scoring architecture.

### **10. File 10 of 17: `contest_tools/reports/plot_point_rate.py`**
* **File Identification:** `contest_tools/reports/plot_point_rate.py`, Version `0.57.7-Beta`
* **Surgical Changes:** The report will be refactored to source its data directly from the new `log.time_series_score_df` and to use the `points_header_label` from the contest definition for its Y-axis label.
* **Affected Modules Checklist:** This change makes the report dependent on the new scoring architecture.

### **11. File 11 of 17: `contest_tools/reports/plot_hourly_animation.py`**
* **File Identification:** `contest_tools/reports/plot_hourly_animation.py`, Version `0.80.3-Beta`
* **Surgical Changes:** Refactor the report to source its cumulative score data directly from `log.time_series_score_df`, removing its internal score calculation logic.
* **Affected Modules Checklist:** This change makes the report dependent on the new scoring architecture.

### **12. File 12 of 17: `contest_tools/reports/text_wae_score_report.py` (New File)**
* **File Identification:** New file.
* **Surgical Changes:** Create a new, dedicated score report for the WAE contest with a custom table layout that includes columns for "QSO Pts", "QTC Pts", and "Weighted Mults".
* **Affected Modules Checklist:** This is a new, standalone report.

### **13. File 13 of 17: `contest_tools/reports/text_wae_comparative_score_report.py` (New File)**
* **File Identification:** New file.
* **Surgical Changes:** Create the comparative version of the WAE score report.
* **Affected Modules Checklist:** This is a new, standalone report.

### **14. File 14 of 17: `Docs/UsersGuide.md`**
* **File Identification:** `Docs/UsersGuide.md`, Version `0.62.0-Beta`
* **Surgical Changes:** Add "WAE CW" and "WAE SSB" to the list of supported contests in Section 4.
* **Affected Modules Checklist:** Updates user-facing documentation.

### **15. File 15 of 17: `Docs/ReportInterpretationGuide.md`**
* **File Identification:** `Docs/ReportInterpretationGuide.md`, Version `0.54.3-Beta`
* **Surgical Changes:** Add a new subsection to "Text Reports" explaining how to read the new WAE-specific score reports.
* **Affected Modules Checklist:** Updates user-facing documentation.

### **16. File 16 of 17: `test_code/test_wae_loader.py` (Purge)**
* **File Identification:** `test_code/test_wae_loader.py`, Version `1.0.1-Beta`
* **Surgical Changes:** This file will be removed from the project's definitive state as its purpose is now obsolete. This action will be performed using the **File Purge Protocol (3.6)**.
* **Affected Modules Checklist:** This action is a cleanup step and has no dependencies.

### **17. File 17 of 17: `test_code/test_iaru_loader.py` (Purge)**
* **File Identification:** `test_code/test_iaru_loader.py`, Version `1.0.1-Beta`
* **Surgical Changes:** This file will be removed from the project's definitive state as its purpose is now obsolete. This action will be performed using the **File Purge Protocol (3.6)**.
* **Affected Modules Checklist:** This action is a cleanup step and has no dependencies.

---
## **Future Work: Phase 3 - Migrate Existing Contests**
This phase will be handled in a **separate, future task** after the WAE integration is complete and has been fully validated. The steps will include:
1.  **Update All Other JSONs**: Add `"use_new_score_calculator": true` and `"time_series_calculator": "standard_calculator"` to all non-WAE contest definition files.
2.  **Finalize `contest_log.py`**: Remove the conditional logic and the old scoring code path from `contest_log.py`, making the new architecture the one and only system.
3.  **Final Regression Test**: Run `run_regression_test.py` to provide final verification that the new architecture is a perfect functional replacement for the old logic.

---
### **Post-Generation Verification:**
I have verified that this implementation plan contains all the sections mandated by **Protocol 2.5**.