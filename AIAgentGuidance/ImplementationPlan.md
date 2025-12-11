# Implementation Plan - Remove Hourly ADIF Generation

**Goal:** Disable the automatic generation of hourly ADIF files in the `Debug/adif_files` directory, while preserving the generation of the single cumulative ADIF file.

**Safety Protocols:**
* **Constraint:** Do NOT modify the cumulative ADIF export logic (lines 231-234).
* **Constraint:** Do NOT modify the `debug_data` flag handling for text reports.

## **Execution Steps**

### **1. Modify `contest_tools/log_manager.py`**
* **Locate:** The block labeled `# --- Hourly ADIF Debug File Generation ---` inside `finalize_loading` (approx lines 225-231).
* **Action:** Delete the entire `if debug_data:` block that handles hourly ADIF generation.
    * *Specifically:* Remove lines 225 through 231 (inclusive of the loop and export call).
* **Verify:** Ensure the subsequent block `# --- ADIF Export (if enabled for this contest) ---` remains intact to generate the single N1MM-compatible file.

## **Technical Debt Register**
* **Observation:** `finalize_loading` in `log_manager.py` performs multiple distinct tasks (CSV export, WAE QTC export, ADIF export).
* **Recommendation:** Future refactoring should extract these export routines into dedicated Exporter classes (e.g., `CsvExporter`, `AdifExporter`) orchestrated by the ReportGenerator, rather than the LogManager.

## **Builder Bootstrap Context**
* **Target File:** `contest_tools/log_manager.py`
* **Logic:** The current implementation iterates through `master_time_index` and creates a `temp_log` for every hour to export an ADIF file if `debug_data` is True. This is the logic to be removed.