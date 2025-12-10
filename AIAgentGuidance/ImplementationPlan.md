# Implementation Plan - CTY Manager: Writelog Support & Hybrid Validation

**Date:** 2025-12-10
**Target Version:** 0.90.13-Beta
**Builder Bootstrap Context:**
- **Goal:** Switch the CTY data source to `wl_cty.dat`, rename files using the Zip Stem versioning (e.g., `wl_cty_3501.dat`), and implement "Lazy Validation" using the internal `=VER` date.
- **Constraint:** Do not download all files to build the index. Use web metadata for indexing and internal content for validation upon usage.

## Phase 1: Parsing Logic Update
**Target File:** `contest_tools/core_annotations/get_cty.py`

### Step 1.1: Add Date Extraction Helper
- Add a static method `extract_version_date(filepath: str) -> Optional[pd.Timestamp]` to the `CtyLookup` class.
- **Logic:** Open file -> Regex search for `r'=VER(\d{8})'` -> Parse YYYYMMDD -> Return Timestamp.
- This centralizes the parsing logic where it belongs.

## Phase 2: CTY Manager Overhaul
**Target File:** `contest_tools/utils/cty_manager.py`

### Step 2.1: Update Extraction Target
- Modify `_download_and_unzip` to specifically look for `wl_cty.dat` in the zip archive.
- Update the renaming logic: `target_dat_filename = f"wl_cty_{zip_stem.replace('cty-', '')}.dat"` (e.g., `wl_cty_3501.dat`).

### Step 2.2: Implement Validation & Fallback
- Modify `find_cty_file_by_date` to implement the Hybrid Strategy:
    1.  **Filter:** Select candidates based on the existing index (Web Date).
    2.  **Iterate:** Loop through candidates.
    3.  **Verify:** After `_download_and_unzip`, call `CtyLookup.extract_version_date`.
    4.  **Check:** Compare the *Internal Date* against `contest_date`.
        * If valid: Return file.
        * If invalid: Log warning, delete/ignore, try next candidate.
    5.  **Fallback:** If no "After" file is found (e.g., running during contest), log a warning and return the **latest available** file from the index.

## 3. Safety Protocols
- **Regex Safety:** Ensure the VER regex matches strict 8-digit format to avoid false positives.
- **File Integrity:** Ensure `wl_cty.dat` is actually found; if not, raise a clear error (do not fallback to `cty.dat`).

## 4. Verification
- **Unit Test:** Verify `extract_version_date` correctly parses `=VER20251209`.
- **Integration Test:** Verify `CtyManager` correctly identifies `wl_cty.dat`, renames it, and updates the index.