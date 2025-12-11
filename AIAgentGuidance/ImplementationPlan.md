# ImplementationPlan.md

**Version:** 1.0.0
**Target:** 0.102.1-Beta

**1. File Identification**
* **File Path:** `contest_tools/score_calculators/standard_calculator.py`
* **Baseline Version:** 0.90.4-Beta

**2. Surgical Changes**
The goal is to decouple the "Points/QSO Count" calculation from the "Multiplier Count" calculation to ensure points are not dropped when multipliers are unknown, and to enforce the `mults_from_zero_point_qsos` rule.

1.  **Enforce Zero-Point Rule:** Before processing multipliers, insert a check for `log.contest_definition.mults_from_zero_point_qsos`. If `False`, filter `df_for_mults` to exclude rows where `QSOPoints == 0`.
2.  **Decouple Scoring Data Source:** Change the source dataframe for `cum_points_ts`, `run_points_ts`, `cum_qso_ts`, and `run_qso_ts` from `hourly_groups` (derived from the filtered `df_for_mults`) to `hourly_groups_all` (derived from the full `df_original_sorted`).

**3. Surgical Change Verification (`diff`)**
**Ground Truth Declaration:** I declare that the following `diff` is being generated against the definitive baseline version of this file, **Version 0.90.4-Beta**.

--- BEGIN DIFF ---
--- contest_tools/score_calculators/standard_calculator.py
+++ contest_tools/score_calculators/standard_calculator.py
@@ -37,6 +37,10 @@
         # Create a filtered DataFrame for multiplier counting, excluding "Unknown"
         df_for_mults = df_original_sorted.copy()
+        
+        # If contest prohibits zero-point mults (e.g. ARRL DX), filter them out now
+        if not log.contest_definition.mults_from_zero_point_qsos:
+            df_for_mults = df_for_mults[df_for_mults['QSOPoints'] > 0]
+            
         for col in multiplier_columns:
             if col in df_for_mults.columns:
                 df_for_mults = df_for_mults[df_for_mults[col] != 'Unknown']
@@ -48,12 +52,12 @@
         per_band_mult_ts_dict = {}
 
-        # --- Time-series calculation (now based on the filtered df_for_mults) ---
-        hourly_groups = df_for_mults.set_index('Datetime').groupby(pd.Grouper(freq='h'))
+        # --- Time-series calculation (Points/QSOs based on FULL valid log) ---
+        hourly_groups_all = df_original_sorted.set_index('Datetime').groupby(pd.Grouper(freq='h'))
         
         
         # Cumulative QSO Points
-        cum_points_ts = hourly_groups['QSOPoints'].sum().cumsum().reindex(master_index, method='ffill').fillna(0)
-        run_points_ts = df_for_mults[df_for_mults['Run'] == 'Run'].set_index('Datetime')['QSOPoints'].resample('h').sum().cumsum().reindex(master_index, method='ffill').fillna(0)
+        cum_points_ts = hourly_groups_all['QSOPoints'].sum().cumsum().reindex(master_index, method='ffill').fillna(0)
+        run_points_ts = df_original_sorted[df_original_sorted['Run'] == 'Run'].set_index('Datetime')['QSOPoints'].resample('h').sum().cumsum().reindex(master_index, method='ffill').fillna(0)
         sp_unk_points_ts = cum_points_ts - run_points_ts
         
         # Cumulative QSO Counts
-        cum_qso_ts = hourly_groups.size().cumsum().reindex(master_index, method='ffill').fillna(0)
-        run_qso_ts = df_for_mults[df_for_mults['Run'] == 'Run'].set_index('Datetime')['Call'].resample('h').count().cumsum().reindex(master_index, method='ffill').fillna(0)
+        cum_qso_ts = hourly_groups_all.size().cumsum().reindex(master_index, method='ffill').fillna(0)
+        run_qso_ts = df_original_sorted[df_original_sorted['Run'] == 'Run'].set_index('Datetime')['Call'].resample('h').count().cumsum().reindex(master_index, method='ffill').fillna(0)
         sp_unk_qso_ts = cum_qso_ts - run_qso_ts
 
         # Determine if all rules use the simple 'sum_by_band' method.
--- END DIFF ---

**4. Affected Modules Checklist**
* `contest_tools/score_calculators/standard_calculator.py`: **Primary Target.**
* `plot_interactive_animation.py`: Indirectly affected (will now receive correct scores).
* `text_score_report.py`: No change needed (already correct).

**5. Pre-Flight Check**
* **Inputs:** `standard_calculator.py` (v0.90.4-Beta).
* **Expected Outcome:** 1. Multipliers will be calculated from a filtered subset (`df_for_mults`) that respects the zero-point rule.
    2. Points/QSOs will be calculated from the full set (`df_original_sorted`), restoring points previously lost due to missing multiplier data.
* **Backward Compatibility:** Confirmed. This aligns the calculator with the existing behavior of the text reports.
* **Refactoring Impact:** The decoupling ensures that `cum_points_ts` is mathematically identical to `df['QSOPoints'].sum()`, fixing the "slightly lower score" bug.
* **Syntax Validation:** Python syntax is valid.

**6. Post-Generation Verification**
I confirm the plan contains all mandated sections, including the Metadata Header and Surgical Change Verification.