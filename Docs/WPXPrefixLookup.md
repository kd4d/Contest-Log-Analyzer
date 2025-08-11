# WPX Prefix Lookup Specification

**Version: 1.2.0-Beta**
**Date: 2025-08-11**

---
### --- Revision History ---
## [1.2.0-Beta] - 2025-08-11
### Changed
# - Updated the description of the `calculate_wpx_prefixes` function to
#   reflect the correct "once per contest" logic.
## [1.1.0-Beta] - 2025-08-11
### Changed
# - Updated the algorithm and implementation sections to match the
#   corrected, hierarchical logic in the `cq_wpx_prefix.py` module.
## [1.0.0-Beta] - 2025-08-10
### Added
# - Initial release of the WPX Prefix Lookup technical specification.
# ---

## 1. Introduction
This document provides the definitive technical specification for how WPX (Worked All Prefixes) multipliers are calculated and processed by the Contest Log Analyzer. It covers both the abstract algorithm and its concrete implementation in the Python source code.

---
## 2. The Prefix Lookup Algorithm
This section defines the formal, step-by-step logic for determining a valid WPX prefix from a single amateur radio callsign. The process is hierarchical, checking for a special case first before proceeding to the standard calculation.

### 2.1. Special Case: Prefix-Style Portables
The algorithm first checks for the special case of a prefix-style portable callsign (e.g., `PA/F6ABC`).

1.  The callsign is checked for a forward slash (`/`).
2.  If a slash is found, the portion of the callsign *before* the slash is isolated (the "prefix part").
3.  This prefix part is then checked for any numerical digits.
4.  If the prefix part contains **no digits**, a `0` is appended to it to form the final prefix (e.g., `PA` becomes `PA0`), and the algorithm terminates for this callsign.
5.  If the prefix part *does* contain a digit (e.g., `IT9` in `IT9/K3MM`), this special rule is ignored, and the algorithm proceeds to the standard calculation below.

### 2.2. Standard Prefix Calculation
If the callsign is not a special prefix-style portable, or if its prefix part contains a digit, the following standard algorithm is used:

1.  **Remove Simple Portable Indicators:** Any standard portable indicators (e.g., `/P`, `/M`, `/AM`, `/MM`) are removed from the end of the callsign string.

2.  **Extract Standard Prefix:** The code then uses a regular expression `([A-Z]+)(\d+)([A-Z]*)` to match the standard prefix structure: the initial group of letters, the first number group, and the subsequent group of letters.

3.  **Apply LDL Special Case:** A final check is performed on the standard prefix extracted in the previous step. If it matches the specific **Letter-Digit-Letter (LDL)** format (e.g., `N8S`), the final letter is dropped to produce the correct prefix (e.g., `N8`). Otherwise, the standard prefix is used as the final result.

---
## 3. The Python Implementation

This section describes how the algorithm and the higher-level "first-worked" logic are implemented in the project's source code.

### 3.1. Overview
The full process involves two stages, handled by two separate functions within the `cq_wpx_prefix.py` module:
* A low-level helper function (`_get_prefix`) that implements the hierarchical algorithm from Section 2.
* A high-level orchestrator function (`calculate_wpx_prefixes`) that uses this helper to implement the stateful "first-worked per contest" logic.

--- FILE: Docs/WPXPrefixLookup.md.part2 ---
#### `_get_prefix(call)` function
This helper function is the direct, line-by-line implementation of the hierarchical algorithm described in Section 2. It accepts a single callsign string and returns the final, calculated prefix string, correctly handling all special cases.

#### `calculate_wpx_prefixes(df)` function
This is the main function called by the log processing engine. It implements the "first-worked per contest" logic. Its process is as follows:
1.  It takes the full, unprocessed QSO DataFrame as input.
2.  It sorts the DataFrame chronologically by the `Datetime` of each QSO.
3.  It then iterates through the sorted QSOs, calling the `_get_prefix` helper for each one.
4.  It maintains a "seen" set of only the `prefix` strings. If a QSO's prefix is not yet in the set, it is considered a "first" for the entire contest. The prefix is recorded for that QSO, and the prefix is added to the "seen" set.
5.  For all subsequent QSOs with the same prefix, a null value is recorded.
6.  The function returns a sparse pandas Series, aligned to the original DataFrame's index, containing prefixes only for the QSOs that were the first in the entire contest.

### 3.3. Data Flow and Orchestration

#### `contest_log.py`
This script is the central orchestrator for all log processing. Its `apply_contest_specific_annotations` method reads the `multiplier_rules` from the relevant `.json` file. When it encounters a rule with `"source": "calculation_module"`, it uses the `module_name` and `function_name` from the rule to dynamically import and execute the correct function (e.g., `calculate_w_prefixes`). The sparse Series returned by this function is then assigned to the final multiplier column (e.g., `Mult1`) in the main DataFrame.

#### `get_cty.py`
This utility is fundamental to the overall log processing pipeline, as it provides the essential geographic data for each QSO (e.g., `DXCCName`, `Continent`). However, for the specific task of calculating a WPX prefix, its data is **not** used as a direct input. The prefix is derived solely from the callsign string itself, as defined by the algorithm in Section 2.