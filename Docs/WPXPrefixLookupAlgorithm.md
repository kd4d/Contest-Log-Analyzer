# WPX Prefix Lookup Algorithm Specification

**Version: 0.30.0-Beta**
**Date: 2025-08-05**

---
### --- Revision History ---
## [0.30.0-Beta] - 2025-08-05
# - Initial release of Version 0.30.0-Beta.
# - Standardized all project files to a common baseline version.
---

## 1. Core Purpose

The script's purpose is to implement the specific and complex rules of the CQ WPX Contest to derive the correct prefix from a given callsign. It relies on pre-processed information provided by the `get_cty.py` lookup script to resolve ambiguities.

---
## 2. Required Inputs

The algorithm requires a row of data containing three key fields derived from the `get_cty.py` script:

1.  **`Call`**: The original, raw callsign string.
2.  **`DXCCPfx`**: The resolved DXCC prefix for the location of operation (e.g., "K", "VP2V"). This can be "Unknown".
3.  **`portableid`**: The part of a portable callsign identified by `get_cty.py` as the location designator (e.g., "7", "VP2V"). This is blank for non-portable calls.

---
## 3. The Lookup Algorithm

The algorithm follows a strict hierarchy. A successful determination at any step concludes the process for that callsign.

### Step 1: Initial Cleanup (`_clean_callsign`)
The first step is to clean the raw `Call` string to remove common non-prefix suffixes that are not part of a WPX prefix or a portable designator. This includes stripping suffixes like `/P`, `/M`, `/QRP` and any characters following a hyphen (`-`).

### Step 2: Maritime Mobile Override
The highest-priority rule is for maritime mobile stations. If the raw `Call` string ends in `/MM`, the WPX prefix is immediately determined to be **"Unknown"**.

### Step 3: Portable Call Processing
If the `portableid` field is not blank, the portable prefix rules are applied.

1.  **Prerequisite Check:** If the `DXCCPfx` is "Unknown," the program cannot safely resolve a portable call, and the WPX prefix is set to **"Unknown"**.
2.  **`call/digit` Rule:** If the `portableid` is a single digit (e.g., "7" from `WN5N/7`), a special transformation is applied: the last digit of the *root callsign's prefix* is replaced with the `portableid` digit (e.g., `WN5N`'s prefix `WN5` becomes `WN7`).
3.  **Letters-Only Rule:** If the `portableid` contains only letters and no numbers (e.g., "LX" from `LX/KD4D`), a zero (`0`) is appended to it to form the prefix (`LX0`).
4.  **Default Portable Rule:** In all other portable cases where the `portableid` is a full prefix (e.g., "VP2V" from `VP2V/KD4D`), the `portableid` itself becomes the WPX prefix.

### Step 4: Non-Portable Call Processing
If the `portableid` field is blank, the non-portable rules are applied to the cleaned callsign.

1.  **Default Prefix Calculation:** The standard prefix is first determined by taking everything in the callsign up to and including the last digit (e.g., `S55A` becomes `S55`). For calls with no numbers (e.g., `RAEM`), the prefix is the first two letters plus a zero (`RA0`).
2.  **`DXCCPfx` Override Rule:** The program then checks if the callsign starts with the provided `DXCCPfx` and if the `DXCCPfx` is *longer* than the default prefix calculated above. If both are true, the more-specific `DXCCPfx` is used as the definitive WPX prefix. This correctly handles special cases like `VP2VMM` (default prefix `VP2`) being overridden by its `DXCCPfx` (`VP2V`).
3.  **Final Validation:** If any of the above rules result in a prefix that is only a single digit, it is invalidated and set to **"Unknown"**.