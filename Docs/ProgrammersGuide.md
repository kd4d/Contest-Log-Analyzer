# Contest Log Analyzer - Programmer's Guide

**Version: 0.48.0-Beta**
**Date: 2025-08-23**

---
### --- Revision History ---
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
# - Replaced nested markdown code fences with ``` placeholder.
## [1.0.1-Beta] - 2025-08-11
### Changed
# - Updated CLI arguments, contest-specific module descriptions, and the
#   report interface to be fully consistent with the current codebase.
## [1.0.0-Beta] - 2025-08-10
### Added
# - Initial release of the Programmer's Guide.
# ---

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
## Core Components

### Command-Line Interface (`main_cli.py`)
This script is the main entry point for running the analyzer.
* **Argument Parsing:** It uses Python's `argparse` to handle command-line arguments.
Key arguments include:
    * `log_files`: A list of one or more log files to process.
    * `--report`: Specifies which reports to run. This can be a single `report_id`, a comma-separated list of IDs, the keyword `all`, or a category keyword (`chart`, `text`, `plot`, `animation`).
    * `--verbose`: Enables `INFO`-level debug logging.
    * `--include-dupes`: An optional flag to include duplicate QSOs in report calculations.
    * `--mult-name`: An optional argument to specify which multiplier to use for multiplier-specific reports (e.g., 'Countries').
    * `--metric`: An optional argument for difference plots, specifying whether to compare `qsos` or `points`. Defaults to `qsos`.
    * `--debug-data`: An optional flag to save the source data for visual reports to a text file.
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
## How to Add a New Report

### The Report Interface
All reports must be created as `.py` files in the `contest_tools/reports/` directory. For the program to recognize a report, it must adhere to the contract defined by the `ContestReport` base class.

### The `ContestReport` Base Class
This abstract base class, defined in `contest_tools/reports/report_interface.py`, provides the required structure for all report modules. A new report **must** inherit from this class and implement its required attributes and methods.

```python
# Excerpt from contest_tools/reports/report_interface.py

from abc import ABC, abstractmethod
from typing import List
from ..contest_log import ContestLog

class ContestReport(ABC):
    # --- Required Class Attributes ---
    report_id: str = "abstract_report"
    report_name: str = "Abstract Report"
    report_type: str = "text" # 'text', 'plot', 'chart', or 'animation'
    
    supports_single: bool = False
    supports_pairwise: bool = False
    supports_multi: bool = False

    def __init__(self, logs: List[ContestLog]):
        # ... constructor logic ...

    @abstractmethod
    def generate(self, output_path: str, **kwargs) -> str:
        # ... your report logic goes here ...
        pass
```

### Boilerplate Example
Here is a minimal "Hello World" report.

```
# contest_tools/reports/text_hello_world.py
from .report_interface import ContestReport

class Report(ContestReport):
    report_id = "hello_world"
    report_name = "Hello World Report"
    report_type = "text"
    supports_single = True

    def generate(self, output_path: str, **kwargs) -> str:
        log = self.logs[0]
        callsign = log.get_metadata().get('MyCall', 'N/A')
        report_content = f"Hello, {callsign}!"
        # In a real report, you would save this content to a file.
        print(report_content)
        
        return f"Report '{self.report_name}' generated successfully."
```

---
## How to Add a New Contest

Adding a new contest is primarily a data-definition task that involves creating a `.json` file and, if necessary, contest-specific Python modules.

### The Core Data Columns
After parsing, all log data is normalized into a standard pandas DataFrame. The available columns are defined in `contest_tools/contest_definitions/_common_cabrillo_fields.json`. When creating exchange parsing rules, the `groups` list **must** map to these column names.

**Available Columns**: `ContestName`, `CategoryOverlay`, `CategoryOperator`, `CategoryTransmitter`, `MyCall`, `Frequency`, `Mode`, `Datetime`, `SentRS`, `SentRST`, `SentZone`, `SentNR`, `Call`, `RS`, `RST`, `Zone`, `NR`, `Transmitter`, `Band`, `Date`, `Hour`, `Dupe`, `DXCCName`, `DXCCPfx`, `CQZone`, `ITUZone`, `Continent`, `WAEName`, `WAEPfx`, `Lat`, `Lon`, `Tzone`, `portableid`, `Run`, `QSOPoints`, `Mult1`, `Mult1Name`, `Mult2`, `Mult2Name`.

### JSON Quick Reference
Create a new `.json` file in `contest_tools/contest_definitions/`. The following table describes the available keys.

| Key | Description | Example Value |
| --- | --- | --- |
| `contest_name` | The official name from the Cabrillo `CONTEST:` tag. | `"CQ-WW-CW"` |
| `dupe_check_scope` | Determines if dupes are checked `per_band` or across `all_bands`. | `"per_band"` |
| `exchange_parsing_rules` | An object containing regex patterns to parse the exchange portion of a QSO line. | `{ "NAQP-CW": [ { "regex": "...", "groups": [...] } ] }` |
| `multiplier_rules` | A list of objects defining the contest's multipliers. | `[ { "name": "Zones", "source_column": "CQZone", "value_column": "Mult1" } ]` |
| `score_formula` | Scoring method. Can be `qsos_times_mults` or `points_times_mults`. | `"points_times_mults"` |
| `multiplier_report_scope`| Determines if mult reports run `per_band` or `per_mode`. | `"per_band"` |
| `excluded_reports`| A list of `report_id` strings to disable for this contest. | `[ "point_rate_plots" ]` |
| `operating_time_rules`| Defines on-time limits for the `score_report`. | `{ "single_op_max_hours": 30 }` |
| `mults_from_zero_point_qsos`| `True` if multipliers count from 0-point QSOs. | `true` |
| `enable_adif_export` | `True` if the log should be exported to an N1MM-compatible ADIF file. | `true` |
| `valid_bands` | A list of bands valid for the contest. | `[ "160M", "80M", "40M" ]` |
| `contest_period` | Defines the official start/end of the contest. | `{ "start_day": "Saturday" }` |
| `custom_parser_module` | *Optional.* Specifies a module to run for complex, asymmetric parsing. | `"arrl_10_parser"` |
| `custom_multiplier_resolver` | *Optional.* Specifies a module to run for complex multiplier logic (e.g., NAQP). | `"naqp_multiplier_resolver"` |
| `contest_specific_event_id_resolver` | *Optional.* Specifies a module to create a unique event ID for contests that run multiple times a year. | `"naqp_event_id_resolver"` |
| `scoring_module` | *Implied.* The system looks for a `[contest_name]_scoring.py` file with a `calculate_points` function. | N/A (Convention-based) |
| `cabrillo_version` | The Cabrillo version for the log header. | `"3.0"` |
| `header_field_map` | Maps Cabrillo tags to internal DataFrame columns. | `{"CALLSIGN": "MyCall"}` |
| `qso_common_fields_regex`| Regex to parse the non-exchange part of a QSO line. | `"QSO:\\s+(\\d+)..."` |
| `qso_common_field_names` | A list of names for the groups in the common regex. | `["FrequencyRaw", "Mode"]` |
| `default_qso_columns` | The complete, ordered list of columns for the final DataFrame. | `["MyCall", "Frequency", "Mode"]` |
| `scoring_rules` | *Legacy.* Defines contest-specific point values. | `{"points_per_qso": 2}` |

### The Annotation and Scoring Workflow (`contest_log.py`)
After initial parsing, `contest_log.py` orchestrates a sequence of data enrichment steps. This is the plug-in system for contest-specific logic. The sequence is defined in the `apply_contest_specific_annotations` method. A developer needing to add complex logic should reference this file to understand the workflow.

**Sequence of Operations:**
1.  **Universal Annotations**: Run/S&P and DXCC/Zone lookups are applied to all logs.
2.  **Custom Multiplier Resolver**: If `custom_multiplier_resolver` is defined in the JSON, the specified module is dynamically imported and its `resolve_multipliers` function is executed.
3.  **Standard Multiplier Rules**: The system processes the `multiplier_rules` from the JSON. If a rule has `"source": "calculation_module"`, it dynamically imports and runs the specified function. This is how WPX prefixes are calculated.
4.  **Scoring**: The system looks for a scoring module by convention (e.g., `cq_ww_cw_scoring.py`) and executes its `calculate_points` function.

### Advanced Guide: Extending Core Logic (Implementation Contracts)
For contests requiring logic beyond simple JSON definitions, create a Python module in `contest_tools/contest_specific_annotations/`. Each module type has a specific contract (required function and signature) it must fulfill.

* **Custom Parser Modules**:
    * **Purpose**: To parse a raw log file and return a standardized DataFrame and metadata dictionary. Called *instead of* the generic parser.
    * **Required Function Signature**: `parse_log(filepath: str, contest_definition: ContestDefinition) -> Tuple[pd.DataFrame, Dict[str, Any]]`
* **Custom Multiplier Resolvers**:
    * **Purpose**: To apply complex logic to identify multipliers and add the appropriate `Mult_` columns to the DataFrame.
    * **Required Function Signature**: `resolve_multipliers(df: pd.DataFrame, my_location_type: str) -> pd.DataFrame`
* **Scoring Modules**:
    * **Purpose**: To calculate the point value for every QSO and return the results as a pandas Series that will become the `QSOPoints` column.
    * **Required Function Signature**: `calculate_points(df: pd.DataFrame, my_call_info: Dict[str, Any]) -> pd.Series`
* **Utility for Complex Multipliers (`_core_utils.py`)**:
    * For contests with complex multiplier aliases (like NAQP or ARRL DX), developers should use the `AliasLookup` class found in `contest_tools/core_annotations/_core_utils.py`. This utility is designed to be used within a custom multiplier resolver to parse `.dat` alias files.
---
## Appendix: Key Source Code References
This appendix lists the most important files for developers to consult to understand the application's framework. The sections above provide context and instructions on how these files are used.

* **`contest_tools/contest_definitions/_common_cabrillo_fields.json`**: The definitive source for all available DataFrame column names. Essential for writing exchange parsing rules.
* **`contest_tools/reports/report_interface.py`**: Defines the `ContestReport` abstract base class that all new reports must inherit from.
* **`contest_tools/contest_log.py`**: The central orchestrator for applying contest-specific logic, including custom parsers, multiplier resolvers, and scoring modules.
* **`contest_tools/core_annotations/_core_utils.py`**: Contains shared utilities, most notably the `AliasLookup` class for handling complex multiplier aliases.