# Technical Debt Cleanup Plan

**Version: 0.30.0-Beta**
**Date: 2025-08-05**

---
### --- Revision History ---
## [0.30.0-Beta] - 2025-08-05
# - Initial release of Version 0.30.0-Beta.
# - Standardized all project files to a common baseline version.
---

### 1. Create a Shared Alias Parser
* **What:** I will create a single, generic `AliasLookup` class and move it into the shared **`_report_utils.py`** module. The multiplier resolver modules (like `cq_160_multiplier_resolver.py`) will be simplified to use this shared utility.
* **Why:** This will **eliminate duplicate code** and ensure that all contests use the same, consistent logic for parsing multiplier alias files, making the system easier to maintain.

### 2. Unify Time-Series Logic
* **What:** I will modify the plot-based reports (`plot_cumulative_difference.py`, `plot_point_rate.py`, and `plot_qso_rate.py`).
* **Why:** I will remove their old, internal time-alignment logic and update them to work with the **pre-aligned dataframes** provided by the `LogManager`. This will make all time-series reports (both text and plots) consistent, more robust, and will fix the "all zeros" bug permanently.