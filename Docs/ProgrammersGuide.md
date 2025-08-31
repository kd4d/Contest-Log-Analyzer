# Contest Log Analyzer - Programmer's Guide

**Version: 0.55.12-Beta**
**Date: 2025-08-31**

---
### --- Revision History ---
## [0.55.12-Beta] - 2025-08-31
### Changed
# - Updated the Custom Parser contract to reflect the new, mandatory
#   two-stage parsing architecture.
## [0.55.9-Beta] - 2025-08-31
### Changed
# - Deprecated the `qso_common_fields_regex` in the JSON Quick Reference
#   [cite_start]as this logic is now handled internally by the parser. [cite: 590]
# [cite_start]- Added a note to describe the new mode normalization logic (e.g., FM -> PH). [cite: 591]
## [0.55.8-Beta] - 2025-08-30
### Added
# - Added a new "Implementation Details and Conventions" section to the
#   Custom ADIF Exporter contract to document N1MM-specific tagging
#   [cite_start]requirements and the APP_CLA_ tag convention. [cite: 592]
## [0.55.7-Beta] - 2025-08-30
### Added
# - Added a note to the Custom Parser contract clarifying the need to
#   [cite_start]include temporary columns in the `default_qso_columns` list. [cite: 593]
# [cite_start]- Added "Custom ADIF Exporter Modules" to the implementation contracts. [cite: 594]
# [cite_start]- Added the `custom_adif_exporter` key to the JSON Quick Reference table. [cite: 595]
## [0.54.1-Beta] - 2025-08-28
### Changed
# - Clarified that the `RawQSO` column is an intermediate field that is
#   [cite_start]removed before the final reporting stage. [cite: 596]
## [0.52.13-Beta] - 2025-08-26
### Changed
# [cite_start]- Updated the Core Data Columns list to include the new `RawQSO` column. [cite: 597]
# [cite_start]- Updated the custom parser contract to require the `RawQSO` column. [cite: 598]
# [cite_start]- Updated the `report_type` and `--report` argument descriptions to include 'html'. [cite: 599]
# [cite_start]- Added the missing `--debug-mults` CLI argument to the documentation. [cite: 600]
## [0.51.0-Beta] - 2025-08-26
### Added
# - Added "Advanced Report Design: Shared Logic" section to document the
#   [cite_start]pattern of separating data aggregation from presentation. [cite: 601]
### Changed
# - Updated CLI arguments and ContestReport class to include the new
#   [cite_start]'html' report type. [cite: 602]
## [0.40.11-Beta] - 2025-08-25
### Changed
# - Updated the JSON Quick Reference table to include the new
#   `mutually_exclusive_mults` key, reflecting its replacement of
#   [cite_start]the obsolete `score_report_rules` key in the codebase. [cite: 603]
## [0.40.10-Beta] - 2025-08-24
### Added
# - Added a section explaining when and why __init__.py files need to
#   [cite_start]be updated, clarifying the project's dynamic vs. explicit import models. [cite: 604]
## [0.49.1-Beta] - 2025-08-24
### Changed
# - Replaced the `score_report_rules` key with the more generic
#   [cite_start]`mutually_exclusive_mults` key in the JSON Quick Reference table. [cite: 605]
## [0.49.0-Beta] - 2025-08-24
### Added
# - Documented the new `score_report_rules` key in the JSON Quick
#   [cite_start]Reference table. [cite: 606]
## [0.48.0-Beta] - 2025-08-23
### Added
# [cite_start]- Major overhaul to create a comprehensive, standalone developer guide. [cite: 607]
# [cite_start]- Added "The ContestReport Base Class" section with an annotated boilerplate. [cite: 608]
# [cite_start]- Added "The Core Data Columns" section with a complete reference list. [cite: 609]
# [cite_start]- Added "The Annotation and Scoring Workflow" section explaining contest_log.py. [cite: 610]
# [cite_start]- Added "Utility for Complex Multipliers" section referencing _core_utils.py. [cite: 611]
# [cite_start]- Added detailed implementation contracts for all custom annotation modules. [cite: 612]
# [cite_start]- Added "Appendix: Key Source Code References" to list essential files. [cite: 613]
### Changed
# [cite_start]- Updated all sections to be consistent with the current project state. [cite: 614]
## [0.37.0-Beta] - 2025-08-18
### Added
# - Added a new "Regression Testing" section to describe the
#   [cite_start]run_regression_test.py script and its methodology. [cite: 615]
# [cite_start]- Added the `enable_adif_export` key to the JSON Quick Reference table. [cite: 616]
### Changed
# [cite_start]- Updated the document's version to align with other documentation. [cite: 617]
## [0.36.7-Beta] - 2025-08-15
### Changed
# [cite_start]- Updated the CLI arguments list to be complete. [cite: 618]
# [cite_start]- Updated the JSON Quick Reference table to include all supported keys. [cite: 619]
## [0.35.23-Beta] - 2025-08-15
### Changed
# - Updated the "Available Reports" list and the `--report` argument
#   [cite_start]description to be consistent with the current codebase. [cite: 620]
## [0.32.15-Beta] - 2025-08-12
### Added
# [cite_start]- Added documentation for the new "Custom Parser Module" plug-in pattern. [cite: 621]
### Changed
# [cite_start]- Replaced nested markdown code fences with ``` placeholder. [cite: 622]
## [1.0.1-Beta] - 2025-08-11
### Changed
# - Updated CLI arguments, contest-specific module descriptions, and the
#   [cite_start]report interface to be fully consistent with the current codebase. [cite: 623]
## [1.0.0-Beta] - 2025-08-10
### Added
# [cite_start]- Initial release of the Programmer's Guide. [cite: 624]
---

## Introduction

[cite_start]This document provides a technical guide for developers (both human and AI) looking to extend the functionality of the Contest Log Analyzer. [cite: 625] The project is built on a few core principles:

* [cite_start]**Data-Driven:** The behavior of the analysis engine is primarily controlled by data, not code. [cite: 626] [cite_start]Contest rules, multiplier definitions, and parsing logic are defined in simple `.json` files. [cite: 627] [cite_start]This allows new contests to be added without changing the core Python scripts. [cite: 628]
* [cite_start]**Extensible:** The application is designed with a "plugin" architecture. [cite: 629] [cite_start]New reports and contest-specific logic modules can be dropped into the appropriate directories, and the main engine will discover and integrate them automatically. [cite: 630]
* **Convention over Configuration:** This extensibility relies on convention. [cite_start]The dynamic discovery of modules requires that files and classes be named and placed in specific, predictable locations. [cite: 631]
---
## Core Components

### Command-Line Interface (`main_cli.py`)
[cite_start]This script is the main entry point for running the analyzer. [cite: 632]
* [cite_start]**Argument Parsing:** It uses Python's `argparse` to handle command-line arguments. [cite: 633] Key arguments include:
    * [cite_start]`log_files`: A list of one or more log files to process. [cite: 634]
    * `--report`: Specifies which reports to run. [cite_start]This can be a single `report_id`, a comma-separated list of IDs, the keyword `all`, or a category keyword (`chart`, `text`, `plot`, `animation`, `html`). [cite: 635]
    * [cite_start]`--verbose`: Enables `INFO`-level debug logging. [cite: 636]
    * [cite_start]`--include-dupes`: An optional flag to include duplicate QSOs in report calculations. [cite: 636]
    * [cite_start]`--mult-name`: An optional argument to specify which multiplier to use for multiplier-specific reports (e.g., 'Countries'). [cite: 637]
    * `--metric`: An optional argument for difference plots, specifying whether to compare `qsos` or `points`. [cite_start]Defaults to `qsos`. [cite: 638]
    * [cite_start]`--debug-data`: An optional flag to save the source data for visual reports to a text file. [cite: 639]
    * [cite_start]`--debug-mults`: An optional flag to save intermediate multiplier lists from text reports for debugging. [cite: 600]
* [cite_start]**Report Discovery:** The script dynamically discovers all available reports by inspecting the `contest_tools.reports` package. [cite: 641] [cite_start]Any valid report class in this package is automatically made available as a command-line option. [cite: 642]
### Logging System (`Utils/logger_config.py`)
[cite_start]The project uses Python's built-in `logging` framework for console output. [cite: 643]
* **`logging.info()`:** Used for verbose, step-by-step diagnostic messages. [cite_start]These are only displayed when the `--verbose` flag is used. [cite: 644]
* [cite_start]**`logging.warning()`:** Used for non-critical issues the user should be aware of (e.g., ignoring an `X-QSO:` line). [cite: 645] [cite_start]These are always displayed. [cite: 646]
* [cite_start]**`logging.error()`:** Used for critical, run-terminating failures (e.g., a file not found or a fatal parsing error). [cite: 646]
### Regression Testing (`run_regression_test.py`)
[cite_start]The project includes an automated regression test script to ensure that new changes do not break existing functionality. [cite: 647]
* [cite_start]**Workflow**: The script follows a three-step process: [cite: 648]
    1.  [cite_start]**Archive**: It archives the last known-good set of reports by renaming the existing `reports/` directory with a timestamp. [cite: 648]
    2.  [cite_start]**Execute**: It runs a series of pre-defined test cases from a `regressiontest.bat` file. [cite: 649] [cite_start]Each command in this file generates a new set of reports. [cite: 650]
    3.  [cite_start]**Compare**: It performs a `diff` comparison between the newly generated text reports and the archived baseline reports. [cite: 651] [cite_start]Any differences are flagged as a regression. [cite: 652]
* [cite_start]**Methodology**: This approach focuses on **data integrity**. [cite: 652] [cite_start]Instead of comparing images or videos, which can be brittle, the regression test compares the raw text output and the debug data dumps from visual reports. [cite: 653] [cite_start]This provides a robust and reliable way to verify that the underlying data processing and calculations remain correct after code changes. [cite: 654]
---
## How to Add a New Report

### The Report Interface
[cite_start]All reports must be created as `.py` files in the `contest_tools/reports/` directory. [cite: 655] [cite_start]For the program to recognize a report, it must adhere to the contract defined by the `ContestReport` base class. [cite: 656]
### The `ContestReport` Base Class
[cite_start]This abstract base class, defined in `contest_tools/reports/report_interface.py`, provides the required structure for all report modules. [cite: 657] [cite_start]A new report **must** inherit from this class and implement its required attributes and methods. [cite: 658]
__CODE_BLOCK__python
# Excerpt from contest_tools/reports/report_interface.py

from abc import ABC, abstractmethod
from typing import List
from ..contest_log import ContestLog

class ContestReport(ABC):
    # --- Required Class Attributes ---
    report_id: str = "abstract_report"
    report_name: str = "Abstract Report"
    report_type: str = "text" # 'text', 'plot', 'chart', 'animation', or 'html'
    
    supports_single: bool = False
    supports_pairwise: bool = False
    supports_multi: bool = False

    def __init__(self, logs: List[ContestLog]):
        # ... constructor logic ...

    
    @abstractmethod
    def generate(self, output_path: str, **kwargs) -> str:
        # ... your report logic goes here ...
        pass
__CODE_BLOCK__

### Boilerplate Example
Here is a minimal "Hello World" report.
__CODE_BLOCK__python
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
__CODE_BLOCK__

---
## How to Add a New Contest

[cite_start]Adding a new contest is primarily a data-definition task that involves creating a `.json` file and, if necessary, contest-specific Python modules. [cite: 664]
### The Core Data Columns
[cite_start]After parsing, all log data is normalized into a standard pandas DataFrame. [cite: 665] The available columns are defined in `contest_tools/contest_definitions/_common_cabrillo_fields.json`. [cite_start]When creating exchange parsing rules, the `groups` list **must** map to these column names. [cite: 666]
[cite_start]**Available Columns**: `ContestName`, `CategoryOverlay`, `CategoryOperator`, `CategoryTransmitter`, `MyCall`, `Frequency`, `Mode`, `Datetime`, `SentRS`, `SentRST`, `SentZone`, `SentNR`, `Call`, `RS`, `RST`, `Zone`, `NR`, `Transmitter`, `RawQSO` (*Note: This is an intermediate column used for diagnostics during parsing and is removed before the final DataFrame is available for reporting*), `Band`, `Date`, `Hour`, `Dupe`, `DXCCName`, `DXCCPfx`, `CQZone`, `ITUZone`, `Continent`, `WAEName`, `WAEPfx`, `Lat`, `Lon`, `Tzone`, `portableid`, `Run`, `QSOPoints`, `Mult1`, `Mult1Name`, `Mult2`, `Mult2Name`. [cite: 667]
### JSON Quick Reference
Create a new `.json` file in `contest_tools/contest_definitions/`. [cite_start]The following table describes the available keys. [cite: 668]

| Key | Description | Example Value |
| --- | --- | --- |
| `contest_name` | [cite_start]The official name from the Cabrillo `CONTEST:` tag. [cite: 670] | `"CQ-WW-CW"` |
| `dupe_check_scope` | [cite_start]Determines if dupes are checked `per_band` or across `all_bands`. [cite: 671] | `"per_band"` |
| `exchange_parsing_rules` | [cite_start]An object containing regex patterns to parse the exchange portion of a QSO line. [cite: 672] | `{ "NAQP-CW": [ { "regex": "...", "groups": [...] } ] }` |
| `multiplier_rules` | [cite_start]A list of objects defining the contest's multipliers. [cite: 674] | `[ { "name": "Zones", "source_column": "CQZone", "value_column": "Mult1" } ]` |
| `mutually_exclusive_mults` | [cite_start]*Optional.* Defines groups of multiplier columns that are mutually exclusive for a single QSO, used for diagnostic reporting. [cite: 675] | `[["Mult1", "Mult2"]]` |
| `score_formula` | Scoring method. [cite_start]Can be `qsos_times_mults` or `points_times_mults`. [cite: 676] | `"points_times_mults"` |
| `multiplier_report_scope`| [cite_start]Determines if mult reports run `per_band` or `per_mode`. [cite: 677] | `"per_band"` |
| `excluded_reports`| [cite_start]A list of `report_id` strings to disable for this contest. [cite: 678] | `[ "point_rate_plots" ]` |
| `operating_time_rules`| [cite_start]Defines on-time limits for the `score_report`. [cite: 679] | `{ "single_op_max_hours": 30 }` |
| `mults_from_zero_point_qsos`| [cite_start]`True` if multipliers count from 0-point QSOs. [cite: 680] | `true` |
| `enable_adif_export` | [cite_start]`True` if the log should be exported to an N1MM-compatible ADIF file. [cite: 681] | `true` |
| `valid_bands` | [cite_start]A list of bands valid for the contest. [cite: 682] | `[ "160M", "80M", "40M" ]` |
| `contest_period` | [cite_start]Defines the official start/end of the contest. [cite: 683] | `{ "start_day": "Saturday" }` |
| `custom_parser_module` | [cite_start]*Optional.* Specifies a module to run for complex, asymmetric parsing. [cite: 684] | `"arrl_10_parser"` |
| `custom_multiplier_resolver` | [cite_start]*Optional.* Specifies a module to run for complex multiplier logic (e.g., NAQP). [cite: 685] | `"naqp_multiplier_resolver"` |
| `custom_adif_exporter` | [cite_start]*Optional.* Specifies a module to generate a contest-specific ADIF file. [cite: 686] | `"iaru_hf_adif"` |
| `contest_specific_event_id_resolver` | [cite_start]*Optional.* Specifies a module to create a unique event ID for contests that run multiple times a year. [cite: 687] | `"naqp_event_id_resolver"` |
| `scoring_module` | [cite_start]*Implied.* The system looks for a `[contest_name]_scoring.py` file with a `calculate_points` function. [cite: 688] | N/A (Convention-based) |
| `cabrillo_version` | [cite_start]The Cabrillo version for the log header. [cite: 689] | `"3.0"` |
| `qso_common_fields_regex`| *Deprecated.* Regex to parse the non-exchange part of a QSO line. [cite_start]This is now handled internally by the parser. [cite: 691] | `"QSO:\\s+(\\d+)..."` |
| `qso_common_field_names` | [cite_start]A list of names for the groups in the common regex. [cite: 692] | `["FrequencyRaw", "Mode"]` |
| `default_qso_columns` | [cite_start]The complete, ordered list of columns for the final DataFrame. [cite: 693] | `["MyCall", "Frequency", "Mode"]` |
| `scoring_rules` | [cite_start]*Legacy.* Defines contest-specific point values. [cite: 694] | `{"points_per_qso": 2}` |
### The Annotation and Scoring Workflow (`contest_log.py`)
[cite_start]After initial parsing, `contest_log.py` orchestrates a sequence of data enrichment steps. [cite: 695] This is the plug-in system for contest-specific logic. [cite_start]The sequence is defined in the `apply_contest_specific_annotations` method. [cite: 696] [cite_start]A developer needing to add complex logic should reference this file to understand the workflow. [cite: 697]
**Sequence of Operations:**
1.  [cite_start]**Universal Annotations**: Run/S&P and DXCC/Zone lookups are applied to all logs. [cite: 698]
2.  [cite_start]**Mode Normalization**: The `Mode` column is standardized (e.g., `FM` is mapped to `PH`, `RY` to `DG`). [cite: 699]
3.  [cite_start]**Custom Multiplier Resolver**: If `custom_multiplier_resolver` is defined in the JSON, the specified module is dynamically imported and its `resolve_multipliers` function is executed. [cite: 700]
4.  [cite_start]**Standard Multiplier Rules**: The system processes the `multiplier_rules` from the JSON. [cite: 701] [cite_start]If a rule has `"source": "calculation_module"`, it dynamically imports and runs the specified function. [cite: 702] [cite_start]This is how WPX prefixes are calculated. [cite: 703]
5.  [cite_start]**Scoring**: The system looks for a scoring module by convention (e.g., `cq_ww_cw_scoring.py`) and executes its `calculate_points` function. [cite: 703]
### A Note on `__init__.py` Files
[cite_start]The need to update an `__init__.py` file depends on whether a package uses dynamic or explicit importing. [cite: 704]
* [cite_start]**Dynamic Importing (No Update Needed):** Directories like `contest_tools/contest_specific_annotations` and `contest_tools/reports` are designed as "plug-in" folders. [cite: 705] [cite_start]The application uses dynamic importing (`importlib.import_module`) to load these modules by name from the JSON definitions or by discovery. [cite: 706] [cite_start]Therefore, the `__init__.py` files in these directories are intentionally left empty and **do not need to be updated** when a new module is added. [cite: 707]
* [cite_start]**Explicit Importing (Update Required):** When a new parameter is added to a `.json` file, the `ContestDefinition` class in `contest_tools/contest_definitions/__init__.py` **must be updated**. [cite: 708] [cite_start]A new `@property` must be added to the class to expose the new data from the JSON file to the rest of the application. [cite: 709] [cite_start]This is a critical maintenance step for extending the data model. [cite: 710] [cite_start]Similarly, packages like `contest_tools/core_annotations` use their `__init__.py` to explicitly expose functions and classes, and would need to be updated if a new core utility were added. [cite: 711]
### Advanced Guide: Extending Core Logic (Implementation Contracts)
[cite_start]For contests requiring logic beyond simple JSON definitions, create a Python module in `contest_tools/contest_specific_annotations/`. [cite: 712] [cite_start]Each module type has a specific contract (required function and signature) it must fulfill. [cite: 713]
* **Custom Parser Modules**:
    * **Purpose**: To parse the contest-specific *exchange* portion of a QSO line. The custom parser is now part of a **mandatory two-stage process**: it must first call the shared `parse_qso_common_fields` helper from the main `cabrillo_parser.py` module to handle the fixed fields (frequency, mode, date, etc.). The custom parser's only remaining job is to parse the `ExchangeRest` string that the helper returns.
    * **Required Function Signature**: `parse_log(filepath: str, contest_definition: ContestDefinition) -> Tuple[pd.DataFrame, Dict[str, Any]]`
    * [cite_start]**Note on Temporary Columns**: Any temporary columns created by the parser that are needed by a downstream module (like a custom resolver) **must** be included in the `default_qso_columns` list in the contest's JSON definition. [cite: 715] [cite_start]Failure to do so will cause the column to be discarded after parsing. [cite: 716]
* **Custom Multiplier Resolvers**:
    * [cite_start]**Purpose**: To apply complex logic to identify multipliers and add the appropriate `Mult_` columns to the DataFrame. [cite: 717]
    * [cite_start]**Required Function Signature**: `resolve_multipliers(df: pd.DataFrame, my_location_type: str) -> pd.DataFrame` [cite: 718]
* **Scoring Modules**:
    * [cite_start]**Purpose**: To calculate the point value for every QSO and return the results as a pandas Series that will become the `QSOPoints` column. [cite: 718]
    * [cite_start]**Required Function Signature**: `calculate_points(df: pd.DataFrame, my_call_info: Dict[str, Any]) -> pd.Series` [cite: 719]
* **Custom ADIF Exporter Modules**:
    * [cite_start]**Purpose**: To generate a highly customized ADIF file for compatibility with specific external programs (e.g., N1MM Logger+). [cite: 719]
    * [cite_start]**Required Function Signature**: `export_log(log: ContestLog, output_filepath: str)` [cite: 720]
    * [cite_start]**Location**: `contest_tools/adif_exporters/` [cite: 720]
    * **Implementation Details and Conventions**:
        * [cite_start]**External Tool Compatibility**: Custom exporters must be aware of the specific tags required by external programs. [cite: 720] [cite_start]For example, N1MM Logger+ uses `<APP_N1MM_HQ>` for IARU HQ/Official multipliers. [cite: 721]
        * [cite_start]**Conditional Tag Omission**: A critical function of a custom exporter is to conditionally *omit* standard ADIF tags when required by a contest's rules to ensure correct scoring by external tools. [cite: 722] [cite_start]For the IARU contest, the standard `<ITUZ>` tag must be omitted for any QSO that provides an HQ or Official multiplier. [cite: 723]
        * [cite_start]**Redundant `APP_CLA_` Tags**: To ensure our own ADIF files are self-descriptive for future use (e.g., log ingestion by CLA), it is a project convention to include redundant, parallel `APP_CLA_` tags for all contest-specific data. [cite: 724] [cite_start]For example, an IARU HQ QSO should contain both `<APP_N1MM_HQ:4>DARC` for N1MM and a corresponding `<APP_CLA_MULT_HQ:4>DARC` for our own tools. [cite: 725]
* **Utility for Complex Multipliers (`_core_utils.py`)**:
    * [cite_start]For contests with complex multiplier aliases (like NAQP or ARRL DX), developers should use the `AliasLookup` class found in `contest_tools/core_annotations/_core_utils.py`. [cite: 726] [cite_start]This utility is designed to be used within a custom multiplier resolver to parse `.dat` alias files. [cite: 727]
---
## Advanced Report Design: Shared Logic
[cite_start]A key architectural principle for creating maintainable and consistent reports is the **separation of data aggregation from presentation**. [cite: 728] [cite_start]When multiple reports need to display the same underlying data in different formats (e.g., HTML and plain text), the data aggregation logic should not be duplicated. [cite: 729]
### The Shared Aggregator Pattern
[cite_start]The preferred method is to create a dedicated, non-report helper module within the `contest_tools/reports/` directory. [cite: 730] [cite_start]This module's sole responsibility is to perform the complex data calculations and return a clean, structured data object (like a dictionary or pandas DataFrame). [cite: 731]
#### Example: `_qso_comparison_aggregator.py`
To generate both `html_qso_comparison` and `text_qso_comparison` reports, we can create a shared helper:
1.  [cite_start]**Create the Aggregator**: A new file, `_qso_comparison_aggregator.py`, would contain a function like `aggregate_qso_comparison_data(logs)`. [cite: 732] [cite_start]This function would perform all the necessary calculations (Unique QSOs, Common QSOs, Run/S&P breakdowns, etc.) and return a final dictionary. [cite: 733]
2.  **Update the Report Modules**:
    * [cite_start]`html_qso_comparison.py` would import and call this function. [cite: 734] [cite_start]Its only remaining job would be to take the returned data and render it into the final HTML string. [cite: 735]
    * [cite_start]`text_qso_comparison.py` would also import and call the *same* function. [cite: 736] [cite_start]Its job would be to take the data and render it into a fixed-width text table using a tool like pandas' `to_string()` method. [cite: 737]
[cite_start]This pattern ensures that both reports are always based on the exact same data, eliminating the risk of inconsistencies and reducing code duplication. [cite: 738]
---
## Appendix: Key Source Code References
[cite_start]This appendix lists the most important files for developers to consult to understand the application's framework. [cite: 739] [cite_start]The sections above provide context and instructions on how these files are used. [cite: 740]
* **`contest_tools/contest_definitions/_common_cabrillo_fields.json`**: The definitive source for all available DataFrame column names. [cite_start]Essential for writing exchange parsing rules. [cite: 741]
* [cite_start]**`contest_tools/reports/report_interface.py`**: Defines the `ContestReport` abstract base class that all new reports must inherit from. [cite: 742]
* [cite_start]**`contest_tools/contest_log.py`**: The central orchestrator for applying contest-specific logic, including custom parsers, multiplier resolvers, and scoring modules. [cite: 743]
* [cite_start]**`contest_tools/core_annotations/_core_utils.py`**: Contains shared utilities, most notably the `AliasLookup` class for handling complex multiplier aliases. [cite: 744]