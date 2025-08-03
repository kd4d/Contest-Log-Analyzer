# Definitive Callsign Lookup Algorithm Specification

**Version: 1.4.0 (Based on `get_cty.py` v0.26.0-Beta with corrections)**

This document specifies the precise, ordered algorithm for determining a callsign's DXCC and WAE entity information. The process is a sequence of rules executed in a specific order. The first rule to yield a definitive result terminates that branch of the logic.

---

### **Function: `get_cty_DXCC_WAE(callsign)` (Primary Entry Point)**

This is the main function called by the application. It performs two separate lookups (DXCC-only and WAE-priority) and merges the results.

1.  **Perform DXCC-Only Lookup:**
    * Call the core `get_cty(callsign)` function with the WAE lookup feature **disabled**.
    * Store the resulting `CtyInfo` object as `dxcc_res_obj`.

2.  **Perform WAE-Priority Lookup:**
    * Call the core `get_cty(callsign)` function with the WAE lookup feature **enabled**.
    * Store the resulting `CtyInfo` object as `wae_res_obj`.

3.  **Merge Results:**
    * Initialize a `FullCtyInfo` result with all fields set to "Unknown" or empty.
    * **If** `dxcc_res_obj` is valid (not "Unknown"):
        * Populate the `DXCCName`, `DXCCPfx`, `CQZone`, `ITUZone`, `Continent`, `Lat`, `Lon`, and `Tzone` fields of the final result from `dxcc_res_obj`.
    * **If** `wae_res_obj` is valid (not "Unknown"):
        * **Overwrite** the `CQZone`, `ITUZone`, `Continent`, `Lat`, `Lon`, and `Tzone` fields of the final result with the data from `wae_res_obj`. This is the WAE **override** for geographic data.
        * **If** the WAE entity's primary prefix starts with an asterisk (`*`):
            * Populate the `WAEName` and `WAEPfx` fields of the final result from `wae_res_obj`.

4.  **Return** the final, merged `FullCtyInfo` object.

---

### **Function: `get_cty(callsign)` (Core Logic)**

This function contains the core decision tree for resolving a single callsign. It is always called with a `wae` flag (True or False) to control whether WAE prefixes are included in the lookup. *Note: Throughout this section, "the callsign" refers to the string variable as it is being processed at each sequential step.*

**Step 1: Pre-processing and Standardization**

1.  Convert the input `callsign` to uppercase.
2.  Remove any leading/trailing whitespace.
3.  Partition the callsign by the first hyphen (`-`) and keep only the part before it.
4.  Iterate through the suffix list \[`/P`, `/B`, `/M`, `/QRP`\]. If the callsign ends with one of these, strip it. Only the first one found is stripped.

**Step 2: Exact Match Lookup (Highest Priority)**

1.  **If `wae` is enabled**, check if `="<callsign>"` exists in the `waeprefixes` dictionary. If yes, **return** the corresponding entity.
2.  Check if `="<callsign>"` exists in the `dxccprefixes` dictionary. If yes, **return** the corresponding entity.

**Step 3: Hardcoded Special Cases**

1.  **Maritime Mobile:** If the callsign ends in `/MM`, **return** the "Unknown" entity.
2.  **Guantanamo Bay:** This check is performed **before** the portable callsign logic.
    * If the callsign string exactly matches the regex `^KG4[A-Z]{2}$` (e.g., "KG4XX"), **return** the entity for `KG4` (Guantanamo Bay).
    * If the callsign contains a `/` and one of its parts (split by `/`) exactly matches the regex `^KG4[A-Z]{2}$`, it is an invalid portable operation. **Return** the "Unknown" entity.
    * *Note: If a callsign starts with "KG4" but does not meet either of the conditions above (e.g., `KG4A`, `KG4ABC`), this rule takes no action, and the callsign proceeds to the next steps for normal resolution.*

**Step 4: Portable Callsign Logic (contains `/`)**
*If the callsign contains a `/`, the following ordered logic is applied:*

1.  Split the callsign into parts. The first part is `p1`, and the last part is `p2`.
2.  Determine if `p1` is a valid prefix (`p1_is_pfx`). A prefix is valid if it exists as a key in `dxccprefixes`, or if `wae` is enabled, if it exists as a key in `waeprefixes`.
3.  Determine if `p2` is a valid prefix (`p2_is_pfx`) using the same logic.
4.  **Unambiguous Prefix Rule:**
    * If `p1_is_pfx` is true and `p2_is_pfx` is false, **return** the entity for `p1`.
    * If `p2_is_pfx` is true and `p1_is_pfx` is false, **return** the entity for `p2`.
5.  **"Strip the Digit" Heuristic:**
    * If the above rule was inconclusive, create stripped versions `p1s` and `p2s` by removing a single trailing digit (if present).
    * Repeat the **Unambiguous Prefix Rule** using these stripped versions. If it produces a result, **return** it.
6.  **US/Canada Heuristic:**
    * If `p2` is a single digit (`0`-`9`) AND `p1` matches the structural pattern of a US or Canadian callsign, **return** the result of the **Longest Prefix Match** (Step 5) on `p1`.
7.  **Final Portable Fallback:**
    * Perform a **Longest Prefix Match** (Step 5) on `p1` and `p2` separately.
    * If `p1` matches the structural pattern of a US or Canadian callsign, **return** the result for `p2` (if valid), otherwise return the result for `p1`.
    * If `p1` is not a US/Canadian structure, **return** the result for `p1` (if valid), otherwise return the result for `p2`.
    * If no result is found, **return** the "Unknown" entity.

**Step 5: Longest Prefix Match (General Case)**
*If the callsign is not portable and has not been matched by a prior rule:*

1.  Start with the full callsign as the `temp` string.
2.  Loop as long as `temp` has characters:
    * **If `wae` is enabled**, check if `temp` exists as a key in the `waeprefixes` dictionary. If yes, **return** that entity.
    * Check if `temp` exists as a key in the `dxccprefixes` dictionary. If yes, **return** that entity.
    * If no match, shorten `temp` by removing the last character and repeat the loop.
3.  If the loop finishes with no match, **return** the "Unknown" entity.