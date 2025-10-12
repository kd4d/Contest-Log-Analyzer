# Contest Log Analyzer - Programmer's Guide

**Version: 0.91.1-Beta**
**Date: 2025-10-11**

---
### --- Revision History ---
## [0.91.1-Beta] - 2025-10-11
### Added
# - Added the "Python File Header Standard" section to document the
#   mandatory header format for all .py files.
## [0.91.0-Beta] - 2025-10-10
### Changed
# - Synchronized the guide with the current codebase to correct multiple
#   discrepancies, including:
#   - Added the missing `--wrtc` CLI argument.
#   - Updated the scoring module description to reflect the `scoring_module` JSON key.
#   - Corrected the custom parser function signature.
#   - Added documentation for the `inherits_from` JSON inheritance model.
#   - Added missing keys to the JSON Quick Reference (`_filename`, `_version`,
#     `_date`, `is_naqp_ruleset`, `included_reports`).
#   - Added documentation for `multiplier_rules` sub-keys.
## [0.90.17-Beta] - 2025-10-06
### Added
# - Added a new implementation contract for "Event ID Resolver Modules"
#   to document the pluggable architecture for handling contests with
#   multiple events per year.
## [0.90.14-Beta] - 2025-10-06
### Fixed
# - Added the missing `--cty` argument to the CLI documentation.
# - Corrected the return signature for Custom Parser Modules in the
#   Implementation Contracts to account for variable return tuples (e.g.,
#   for QTC data).
## [0.90.10-Beta] - 2025-09-30
### Changed
# - Updated the implementation contract for Custom Parser Modules to
#   reflect the new, four-argument function signature.
## [0.89.0-Beta] - 2025-09-29
### Added
# - Added a new "How to Add a New Contest: A Step-by-Step Guide"
#   section to provide a clear, tutorial-based workflow for developers.
### Changed
# - Clarified the implementation contract for Scoring Modules to explicitly
#   state the file naming and loading conventions.
## [0.88.2-Beta] - 2025-09-21
### Fixed
# - Corrected the function signature for Custom Multiplier Resolvers in the
#   Implementation Contracts to use `my_location_type: str`.
# - Added the missing `custom_location_resolver` key to the JSON Quick Reference.
## [0.87.0-Beta] - 2025-09-18
### Added
# - Added a "High-Level Data Annotation Workflow" section to clarify the
#   data processing pipeline for developers.
# - Expanded all module "Implementation Contracts" to include "When to Use",
#   "Input DataFrame State", and "Responsibility" clauses.
### Fixed
# - Corrected the function signature for Custom Multiplier Resolvers to
#   match the actual four-argument contract in the source code.
## [0.86.7-Beta] - 2025-09-15
### Changed
# - Updated JSON Quick Reference table to include `time_series_calculator`
#   and `points_header_label` keys.
# - Updated function signatures in the Implementation Contracts to include
#   the mandatory `root_input_dir` parameter.
## [0.57.17-Beta] - 2025-09-02
### Added
# - Documented the new `total_points` option for the `score_formula`
#   key in the JSON Quick Reference.
## [0.57.4-Beta] - 2025-09-01
### Added
# - Added a convention to the Custom ADIF Exporter contract explaining
#   the need to handle timestamp uniqueness for N1MM compatibility.
## [0.55.12-Beta] - 2025-08-31
### Changed
# - Updated the Custom Parser contract to reflect the new, mandatory
#   two-stage parsing architecture.
## [0.55.9-Beta] - 2025-08-31
### Changed
# - Deprecated the `qso_common_fields_regex` in the JSON Quick Reference
#   as this logic is now handled internally by the parser.
# - Added a note to describe the new mode normalization logic (e.g., FM -> PH).
## [0.55.8-Beta] - 2025-08-30
### Added
# - Added a new "Implementation Details and Conventions" section to the
#   Custom ADIF Exporter contract to document N1MM-specific tagging
#   requirements and the APP_CLA_ tag convention.
## [0.55.7-Beta] - 2025-08-30
### Added
# - Added a note to the Custom Parser contract clarifying the need to
#   include temporary columns in the `default_qso_columns` list.
# - Added "Custom ADIF Exporter Modules" to the implementation contracts.
# - Added the `custom_adif_exporter` key to the JSON Quick Reference table.
## [0.54.1-Beta] - 2025-08-28
### Changed
# - Clarified that the `RawQSO` column is an intermediate field that is
#   removed before the final reporting stage.
## [0.52.13-Beta] - 2025-08-26
### Changed
# - Updated the Core Data Columns list to include the new `RawQSO` column.
# - Updated the custom parser contract to require the `RawQSO` column.
# - Updated the `report_type` and `--report` argument descriptions to include 'html'.
# - Added the missing `--debug-mults` CLI argument to the documentation.
## [0.51.0-Beta] - 2025-08-26
### Added
# - Added "Advanced Report Design: Shared Logic" section to document the
#   pattern of separating data aggregation from presentation.
### Changed
# - Updated CLI arguments and ContestReport class to include the new
#   'html' report type.
## [0.40.11-Beta] - 2025-08-25
### Changed
# - Updated the JSON Quick Reference table to include the new
#   `mutually_exclusive_mults` key, reflecting its replacement of
#   the obsolete `score_report_rules` key in the codebase.
## [0.40.10-Beta] - 2025-08-24
### Added
# - Added a section explaining when and why __init__.py files need to
#   be updated, clarifying the project's dynamic vs. explicit import models.
## [0.49.1-Beta] - 2025-08-24
### Changed
# - Replaced the `score_report_rules` key with the more generic
#   `mutually_exclusive_mults` key in the JSON Quick Reference table.
## [0.49.0-Beta] - 2025-08-24
### Added
# - Documented the new `score_report_rules` key in the JSON Quick
#   Reference table.
## [0.48.0-Beta] - 2025-08-23
### Added
# - Major overhaul to create a comprehensive, standalone developer guide.
# - Added "The ContestReport Base Class" section with an annotated boilerplate.
# - Added "The Core Data Columns" section with a complete reference list.
# - Added "The Annotation and Scoring Workflow" section explaining contest_log.py.
# - Added "Utility for Complex Multipliers" section referencing _core_utils.py.
# - Added detailed implementation contracts for all custom annotation modules.
# - Added "Appendix: Key Source Code References" to list essential files.
### Changed
# - Updated all sections to be consistent with the current project state.
## [0.37.0-Beta] - 2025-08-18
### Added
# - Added a new "Regression Testing" section to describe the
#   run_regression_test.py script and its methodology.
# - Added the `enable_adif_export` key to the JSON Quick Reference table.
### Changed
# - Updated the document's version to align with other documentation.
# - Corrected the list of required data files in Section 2.
# - Updated the Command-Line Options list in Section 3 to include
#   the --debug-data flag.
## [0.36.7-Beta] - 2025-08-15
### Changed
# - Updated the CLI arguments list to be complete.
# - Updated the JSON Quick Reference table to include all supported keys.
## [0.35.23-Beta] - 2025-08-15
### Changed
# - Updated the "Available Reports" list and the `--report` argument
#   description to be consistent with the current codebase.
## [0.32.15-Beta] - 2025-08-12
### Added
# - Added documentation for the new "Custom Parser Module" plug-in pattern.
### Changed
# - Replaced nested markdown code fences with __CODE_BLOCK__ placeholder.
## [1.0.1-Beta] - 2025-08-11
### Changed
# - Updated CLI arguments, contest-specific module descriptions, and the
#   report interface to be fully consistent with the current codebase.
## [1.0.0-Beta] - 2025-08-10
### Added
# - Initial release of the Programmer's Guide.
---

## Introduction

This document provides a technical guide for developers (both human and AI) looking to extend the functionality of the Contest Log Analyzer.
The project is built on a few core principles:

* **Data-Driven:** The behavior of the analysis engine is primarily controlled by data, not code.
Contest rules, multiplier definitions, and parsing logic are defined in simple `.json` files.
This allows new contests to be added without changing the core Python scripts.
* **Extensible:** The application is designed with a "plugin" architecture.
New reports and contest-specific logic modules can be dropped into the appropriate directories, and the main engine will discover and integrate them automatically.
* **Convention over Configuration:** This extensibility relies on convention. The dynamic discovery of modules requires that files and classes be named and placed in specific, predictable locations.
---
## Python File Header Standard

All Python (`.py`) files in the project must begin with the following standard header block. This ensures consistency and proper version tracking.

__CODE_BLOCK__python
# {filename}.py
#
# Purpose: {A concise, one-sentence description of the module's primary responsibility.}
#
# Author: {Author Name}
# Date: {YYYY-MM-DD}
# Version: {x.y.z-Beta}
#
# Copyright (c) {Year} Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
#
# License: Mozilla Public License, v. 2.0
#          (https://www.mozilla.org/MPL/2.0/)
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# --- Revision History ---
# [{version}] - {YYYY-MM-DD}
# - {Description of changes}
__CODE_BLOCK__

---
## Core Components

### Command-Line Interface (`main_cli.py`)
This script is the main entry point for running the analyzer.
* **Argument Parsing:** It uses Python's `argparse` to handle command-line arguments.
Key arguments include:
    * `log_files`: A list of one or more log files to process.
    * `--report`: Specifies which reports to run. This can be a single `report_id`, a comma-separated list of IDs, the keyword `all`, or a category keyword (`chart`, `text`, `plot`, `animation`, `html`).
    * `--verbose`: Enables `INFO`-level debug logging.
    * `--include-dupes`: An optional flag to include duplicate QSOs in report calculations.
    * `--mult-name`: An optional argument to specify which multiplier to use for multiplier-specific reports (e.g., 'Countries').
    * `--metric`: An optional argument for difference plots, specifying whether to compare `qsos` or `points`. Defaults to `qsos`.
    * `--debug-data`: An optional flag to save the source data for visual reports to a text file.
    * `--cty <specifier>`: An optional argument to specify the CTY file: 'before', 'after' (default), or a specific filename (e.g., 'cty-3401.dat').
    * `--wrtc <year>`: An optional argument to score IARU-HF logs using the rules for a specific WRTC year.
    * `--debug-mults`: An optional flag to save intermediate multiplier lists from text reports for debugging.
* **Report Discovery:** The script dynamically discovers all available reports by inspecting the `contest_tools.reports` package.
Any valid report class in this package is automatically made available as a command-line option.
### Logging System (`Utils/logger_config.py`)
The project uses Python's built-in `logging` framework for console output.
* **`logging.info()`:** Used for verbose, step-by-step diagnostic messages. These are only displayed when the `--verbose` flag is used.
* **`logging.warning()`:** Used for non-critical issues the user should be aware of (e.g., ignoring an `X-QSO:` line).
These are always displayed.
* **`logging.error()`:** Used for critical, run-terminating failures (e.g., a file not found or a fatal parsing error).
### Regression Testing (`run_regression_test.py`)
The project includes an automated regression test script to ensure that new changes do not break existing functionality.
* **Workflow**: The script follows a three-step process:
    1.  **Archive**: It archives the last known-good set of reports by renaming the existing `reports/` directory with a timestamp.
    2.  **Execute**: It runs a series of pre-defined test cases from a `regressiontest.bat` file.
    Each command in this file generates a new set of reports.
    3.  **Compare**: It performs a `diff` comparison between the newly generated text reports and the archived baseline reports.
    Any differences are flagged as a regression.
* **Methodology**: This approach focuses on **data integrity**.
Instead of comparing images or videos, which can be brittle, the regression test compares the raw text output and the debug data dumps from visual reports.
This provides a robust and reliable way to verify that the underlying data processing and calculations remain correct after code changes.
---
## How to Add a New Contest: A Step-by-Step Guide

This guide walks you through the process of adding a new, simple contest called "My Contest".
This contest will have a simple exchange (RST + Serial Number) and one multiplier (US States).
### Step 1: Create the JSON Definition File
Navigate to the `contest_tools/contest_definitions/` directory and create a new file named `my_contest.json`.
The filename (minus the extension) is the ID used to find the contest's rules.
### Step 2: Define Basic Metadata
Open `my_contest.json` and add the basic information.
The `contest_name` must exactly match the `CONTEST:` tag in the Cabrillo log files for this contest.
__CODE_BLOCK__json
{
  "contest_name": "MY-CONTEST",
  "dupe_check_scope": "per_band",
  "score_formula": "points_times_mults",
  "valid_bands": ["80M", "40M", "20M", "15M", "10M"]
}
__CODE_BLOCK__