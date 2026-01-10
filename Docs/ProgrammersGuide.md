# Contest Log Analytics - Programmer's Guide

**Version: 0.128.0-Beta**
**Date: 2026-01-07**

---
### --- Revision History ---
## [0.128.0-Beta] - 2026-01-07
### Changed
# - Updated "Shared Utilities & Styles" section to document PlotlyStyleManager.
# - Added documentation for PlotlyStyleManager methods and capabilities.
## [0.127.0-Beta] - 2025-12-23
### Added
# - Added "The Manifest & WORM Strategy" section to Phase 3.
# - Documented `contest_tools/manifest_manager.py`.
## [0.126.0-Beta] - 2025-12-18
### Added
# - Added "Phase 3: Web Architecture" section detailing the Django stateless design.
# - Updated "The Data Abstraction Layer (DAL)" to include `ComparativeEngine`.
# - Updated "Shared Utilities & Styles" to include `pivot_utils` and `log_fetcher`.
## [0.94.1-Beta] - 2025-12-06
### Changed
# - Updated "The Data Abstraction Layer (DAL)" section to reflect
#   the formal Aggregator Class architecture.
## [0.94.0-Beta] - 2025-12-06
### Added
# - Added "The Data Abstraction Layer (DAL)" section.
# - Added "Shared Utilities & Styles" section.
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
# - Corrected the function signature for Custom Multiplier Resolvers.
## [0.87.0-Beta] - 2025-09-18
### Added
# - Added a "High-Level Data Annotation Workflow" section to clarify the
#   data processing pipeline for developers.
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

This document provides a technical guide for developers (both human and AI) looking to extend the functionality of the Contest Log Analytics.
The project is built on a few core principles:

* **Data-Driven:** The behavior of the analysis engine is primarily controlled by data, not code.
Contest rules, multiplier definitions, and parsing logic are defined in simple `.json` files.
This allows new contests to be added without changing the core Python scripts.
* **Extensible:** The application is designed with a "plugin" architecture.
New reports and contest-specific logic modules can be dropped into the appropriate directories, and the main engine will discover and integrate them automatically.
* **Convention over Configuration:** This extensibility relies on convention. The dynamic discovery of modules requires that files and classes be named and placed in specific, predictable locations.
---
## Python File Header Standard

All Python (`.py`) files in the project must begin with the following standard header block.
This ensures consistency and proper version tracking.

```
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
# License, v. 2.0.
# If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# --- Revision History ---
# [{version}] - {YYYY-MM-DD}
# - {Description of changes}
```

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

## Phase 3: Web Architecture

The project now includes a stateless, containerized web dashboard (`web_app`) built on Django.
### Core Principles (ADR-007)
* **Stateless Operation**: The Django app does not use a database for domain logic.
It relies on the file system (session directories) for data persistence.
* **Shared Presentation Layer**: The `web_app/config/settings.py` is configured to map the `TEMPLATES` setting to `contest_tools/templates`.
This ensures that the CLI (which uses Jinja2) and the Web App (which uses Django Templates) share the exact same HTML report templates.
### Key Components
* **`web_app/analyzer/views.py`**: Contains the view logic.
    * **`analyze_logs`**: Orchestrates the upload, parsing (via `LogManager`), and reporting (via `ReportGenerator`) pipeline.
It serializes the dashboard context to `dashboard_context.json`.
    * **`dashboard_view`**: Loads the serialized context to render the "Strategy Board".
* **`get_progress`**: Provides a JSON endpoint for the client-side progress bar.
* **`contest_tools/utils/log_fetcher.py`**: A utility class used by the web view to scrape public contest log archives (e.g., CQ WW) and download logs on-demand.
* **`contest_tools/manifest_manager.py`**: Manages the `session_manifest.json`, providing a decoupled way for the UI to discover generated artifacts without hardcoding paths.

### The Manifest & WORM Strategy
To ensure the dashboard remains responsive even with large datasets, the application employs a **"Write Once, Read Many" (WORM)** strategy for expensive aggregations.

1.  **Generation Phase:** During the initial analysis (`analyze_logs`), specific "Artifact Reports" (e.g., `json_multiplier_breakdown.py`) are executed. These reports do not produce human-readable text but instead serialize processed aggregation trees into JSON files.
2.  **Hydration Phase:** When the user loads a dashboard view (e.g., `multiplier_dashboard`), the view uses the `ManifestManager` to locate the JSON artifact.
3.  **Rendering:** The view hydrates its context directly from this pre-computed JSON, avoiding the need to re-parse Cabrillo logs or re-run aggregators on every page load.

---

## The Data Abstraction Layer (DAL)

The `contest_tools.data_aggregators` package is the sole authority for data summarization.
* **Design Principle:** "Pure Python Primitives".
To ensure complete decoupling between the data processing logic and the presentation layer (Reports, Web UI), all Aggregators must return standard Python types (Dictionaries, Lists, Ints, Strings).
They **must not** return Pandas DataFrames or NumPy arrays.

* **Primary Aggregators:**
    * **`CategoricalAggregator`**: Handles set operations (Unique/Common QSOs), point breakdowns, and generic categorical grouping.
* **`ComparativeEngine`**: Implements pure Set Theory logic to calculate Universe, Common, Differential, and Missed counts for any set of items.
* **`MatrixAggregator`**: Generates 2D grids (Band x Time) for heatmaps and activity status tracking.
* **`MultiplierStatsAggregator`**: Handles all multiplier summarization logic, including unique counts and "Missed Multiplier" analysis.
* **`TimeSeriesAggregator`**: Generates the standard TimeSeries Data Schema (v1.4.0), including cumulative rates, scores, and scalar metrics.
* **`WaeStatsAggregator`**: Specialized logic for WAE contests, handling QTCs and weighted multiplier calculations.
---

## Shared Utilities & Styles

* **`contest_tools.styles.MPLStyleManager`**: A centralized source for Matplotlib styles and color consistency for legacy static plots.
It provides methods like `get_point_color_map()` and `get_qso_mode_colors()` to ensure visual uniformity across different reports.
* **`contest_tools.styles.PlotlyStyleManager`**: A centralized source for Plotly styles and color consistency for interactive visualizations.
It provides methods like:
    * `get_point_color_map()` - Generates consistent color mapping for QSO point values
    * `get_qso_mode_colors()` - Returns standard color scheme for Run/S&P/Mixed modes
    * `get_standard_layout()` - Returns standard Plotly layout dictionary with support for polymorphic titles (string or list of strings for three-line titles) and footer text for branding/CTY metadata
* **`contest_tools.utils.CtyManager`**: Manages the lifecycle of the `cty.dat` country file, including downloading, version management, and local caching.
* **`contest_tools.utils.json_encoders.NpEncoder`**: A custom JSON encoder class used to serialize NumPy data types (like `int64` or `float64`) and Pandas Timestamps into standard JSON formats.
* **`contest_tools.utils.pivot_utils`**: Contains shared DataFrame pivoting logic to prevent circular imports between reports.
* **`contest_tools.utils.log_fetcher`**: Provides the `fetch_log_index` and `download_logs` functions for interacting with public log archives.
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
```
{
  "contest_name": "MY-CONTEST",
  "dupe_check_scope": "per_band",
  "score_formula": "points_times_mults",
  "valid_bands": ["80M", "40M", "20M", "15M", "10M"]
}
```