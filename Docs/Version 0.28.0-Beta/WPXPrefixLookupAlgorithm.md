# WPX Prefix Lookup Algorithm Specification

**Version: 0.28.2-Beta**
**Date: 2025-08-02**

This document describes the algorithm implemented in `cq_wpx_prefix.py` for determining an amateur radio callsign's official CQ WPX Contest prefix.

---
### --- Revision History ---
- 2025-08-02: Initial release of this specification document.
---

## 1. Core Purpose

The script's purpose is to implement the specific and complex rules of the CQ WPX Contest to derive the correct prefix from a given callsign. It relies on pre-processed information provided by the `get_cty.py` lookup script to resolve ambiguities.

## 2. Required Inputs

The algorithm requires a row of data containing three key fields:

1.  **`Call`**: The original, raw callsign string.
2.  **`DXCCPfx`**: The resolved DXCC prefix for the location of operation (e.g., "K", "VP2V"). This can be "Unknown".
3.  **`portableid`**: The part of a portable callsign identified by `get_cty.py` as the location designator (e.g., "7", "VP2V"). This is blank for non-portable calls.

## 3. The Lookup Algorithm

The algorithm follows a strict hierarchy. A successful determination at any step concludes the process for that callsign.

### Step 1: Initial Cleanup
The first step is to clean the raw `Call` string to remove common suffixes that are not part of a WPX prefix or a portable designator. This includes stripping suffixes like `/P`, `/M`, `/QRP` and any characters following a hyphen (`-`).

### Step 2: Maritime Mobile Override
The highest-priority rule is for maritime mobile stations. If the raw `Call` string ends in `/MM`, the WPX prefix is immediately determined to be **"Unknown"**.

### Step 3: Portable Call Processing
If the `portableid` field is not blank, the portable prefix rules are applied.

1.  **Prerequisite Check:** If the `DXCCPfx` is "Unknown," the program cannot safely resolve a portable call, and the WPX prefix is **"Unknown"**.
2.  **`call/digit` Rule:** If the `portableid` is a single digit (e.g., "7" from `WN5N/7`), a special transformation is applied: the last digit of the *root callsign's prefix* is replaced with the `portableid` digit. (e.g., `WN5N`'s prefix `WN5` becomes `WN7`).
3.  **Letters-Only Rule:** If the `portableid` contains only letters and no numbers (e.g., "LX" from `LX/KD4D`), a zero (`Ø`) is appended to it to form the prefix (`LXØ`).
4.  **Default Portable Rule:** In all other portable cases (e.g., the `portableid` is a full prefix like "VP2V"), the `portableid` itself becomes the WPX prefix.

### Step 4: Non-Portable Call Processing
If the `portableid` field is blank, the non-portable rules are applied to the cleaned callsign.

1.  **`DXCCPfx` Override Rule:** The program first checks if the callsign starts with the provided `DXCCPfx`. If it does, the `DXCCPfx` is the definitive WPX prefix. This handles special cases like `VP2VMM` (whose `DXCCPfx` is `VP2V`).
2.  **Default Rules:** If the override rule does not apply (either because the call doesn't match or the `DXCCPfx` is "Unknown"), the program uses the following fallback logic:
    * **No-Number Calls:** If the callsign has no numbers (e.g., `RAEM`), the prefix is the first two letters plus a zero (`RAØ`).
    * **Standard Calls:** The prefix is everything in the callsign up to and including the last digit (e.g., `S55A` becomes `S55`).