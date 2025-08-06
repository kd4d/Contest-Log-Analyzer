# WPX Prefix Lookup Algorithm Specification

**Version: 0.30.30-Beta**
**Date: 2025-08-05**

---
### --- Revision History ---
## [0.30.30-Beta] - 2025-08-05
# - No functional changes. Synchronizing version numbers.
## [0.30.0-Beta] - 2025-08-05
# - Initial release of Version 0.30.0-Beta.
# - Standardized all project files to a common baseline version.
---

## 1. Core Purpose

[cite_start]The script's purpose is to implement the specific and complex rules of the CQ WPX Contest to derive the correct prefix from a given callsign. [cite: 2277] [cite_start]It relies on pre-processed information provided by the `get_cty.py` lookup script to resolve ambiguities. [cite: 2278]
---
## 2. Required Inputs

[cite_start]The algorithm requires a row of data containing three key fields derived from the `get_cty.py` script: [cite: 2279]

1.  [cite_start]**`Call`**: The original, raw callsign string. [cite: 2279]
2.  **`DXCCPfx`**: The resolved DXCC prefix for the location of operation (e.g., "K", "VP2V"). [cite_start]This can be "Unknown". [cite: 2280]
3.  [cite_start]**`portableid`**: The part of a portable callsign identified by `get_cty.py` as the location designator (e.g., "7", "VP2V"). [cite: 2281] [cite_start]This is blank for non-portable calls. [cite: 2282]

---
## 3. The Lookup Algorithm

[cite_start]The algorithm follows a strict hierarchy. [cite: 2282] [cite_start]A successful determination at any step concludes the process for that callsign. [cite: 2283]

### Step 1: Initial Cleanup (`_clean_callsign`)
[cite_start]The first step is to clean the raw `Call` string to remove common non-prefix suffixes that are not part of a WPX prefix or a portable designator. [cite: 2284] [cite_start]This includes stripping suffixes like `/P`, `/M`, `/QRP` and any characters following a hyphen (`-`). [cite: 2285]

### Step 2: Maritime Mobile Override
[cite_start]The highest-priority rule is for maritime mobile stations. [cite: 2286] [cite_start]If the raw `Call` string ends in `/MM`, the WPX prefix is immediately determined to be **"Unknown"**. [cite: 2287]

### Step 3: Portable Call Processing
[cite_start]If the `portableid` field is not blank, the portable prefix rules are applied. [cite: 2288]
1.  [cite_start]**Prerequisite Check:** If the `DXCCPfx` is "Unknown," the program cannot safely resolve a portable call, and the WPX prefix is set to **"Unknown"**. [cite: 2289]
2.  [cite_start]**`call/digit` Rule:** If the `portableid` is a single digit (e.g., "7" from `WN5N/7`), a special transformation is applied: the last digit of the *root callsign's prefix* is replaced with the `portableid` digit (e.g., `WN5N`'s prefix `WN5` becomes `WN7`). [cite: 2290]
3.  [cite_start]**Letters-Only Rule:** If the `portableid` contains only letters and no numbers (e.g., "LX" from `LX/KD4D`), a zero (`0`) is appended to it to form the prefix (`LX0`). [cite: 2291]
4.  [cite_start]**Default Portable Rule:** In all other portable cases where the `portableid` is a full prefix (e.g., "VP2V" from `VP2V/KD4D`), the `portableid` itself becomes the WPX prefix. [cite: 2292]

### Step 4: Non-Portable Call Processing
[cite_start]If the `portableid` field is blank, the non-portable rules are applied to the cleaned callsign. [cite: 2293]
1.  [cite_start]**Default Prefix Calculation:** The standard prefix is first determined by taking everything in the callsign up to and including the last digit (e.g., `S55A` becomes `S55`). [cite: 2294] [cite_start]For calls with no numbers (e.g., `RAEM`), the prefix is the first two letters plus a zero (`RA0`). [cite: 2295]
2.  [cite_start]**`DXCCPfx` Override Rule:** The program then checks if the callsign starts with the provided `DXCCPfx` and if the `DXCCPfx` is *longer* than the default prefix calculated above. [cite: 2296] [cite_start]If both are true, the more-specific `DXCCPfx` is used as the definitive WPX prefix. [cite: 2297] [cite_start]This correctly handles special cases like `VP2VMM` (default prefix `VP2`) being overridden by its `DXCCPfx` (`VP2V`). [cite: 2298]
3.  [cite_start]**Final Validation:** If any of the above rules result in a prefix that is only a single digit, it is invalidated and set to **"Unknown"**. [cite: 2299]