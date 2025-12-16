# Contest Log Analytics

**Version: 1.1.0**
**Date: 2025-12-15**

---
### --- Revision History ---
## [1.1.0] - 2025-12-15
### Changed
# - Updated "Introduction" to use "Sports Analytics" metaphor.
# - Replaced CLI-focused "Installation and Setup" with "Web Dashboard" focus.
## [1.0.0] - 2025-12-06
### Added
# - Added `wrtc_propagation` and `wrtc_propagation_animation` to the list
#   of Available Reports.
## [0.94.0-Beta] - 2025-12-06
### Changed
# - Updated version to 0.94.0-Beta to reflect the Phase 1.5 Stabilization release.
### Removed
# - Removed `multipliers_by_hour` from the list of Available Reports.
## [0.91.1-Beta] - 2025-10-11
### Added
# - Added an introduction to explain the concept of Contest Analytics.
# - Added sections linking to the Installation, User, and Report
#   Interpretation guides.
## [0.91.0-Beta] - 2025-10-10
### Changed
# - Updated version number to align with the current session.
# - Added WRTC to the list of supported contests.
## [0.88.0-Beta] - 2025-09-21
### Fixed
# - Synchronized the "Available Reports" list with the current project
#   baseline to add one missing report and correct two report IDs.
## [0.86.5-Beta] - 2025-09-18
### Changed
# - Corrected the report ID for the comparative rate sheet to align
#   with the source code.
## [0.86.4-Beta] - 2025-09-15
### Changed
# - Synchronized the "Supported Contests" and "Available Reports"
#   sections with the current project baseline.
## [0.55.1-Beta] - 2025-09-03
### Changed
# - Synchronized the "Available Reports" list with the current codebase
#   by correcting one report ID and adding a missing report name.
## [0.55.0-Beta] - 2025-08-29
# - Initial release.
---

The Contest Log Analytics is a "Sports Analytics" engine for amateur radio contesting. Just as a sports team watches "game tape" to understand why a play failed, this tool analyzes your logs to understand *why* a score was achieved. It answers the critical questions: Was my strategy of running on 20 meters more effective than my competitor's S&P strategy? Which specific multipliers did they work that I missed?

---
## Key Features

* **Data-Driven Architecture**: Uses simple JSON files to define the rules, scoring, and exchange formats for each contest, making the tool highly extensible.
* **Run/S&P Heuristics**: A sophisticated, multi-pass heuristic analyzes QSO timing and frequency to classify each contact as "Run," "Search & Pounce," or "Unknown," providing a clear picture of operating strategy even though Cabrillo logs do not record this data explicitly.
* **Unique vs. Common QSO Analysis**: The analyzer precisely identifies "unique" QSOs (worked by only one of two logs) and "common" QSOs (worked by both), breaking them down by Run/S&P status to reveal strategic advantages.
* **Cumulative Difference Plots**: Visualizes the "Zero Line" of competition. Above zero means you are leading; the slope indicates your momentum relative to your competitor.
* **Interactive Replay**: Generates an interactive HTML dashboard that replays the contest hour-by-hour, allowing you to visualize momentum shifts.
* **Annotated CSV Output**: Generates detailed, "annotated" CSV files from the processed logs, perfect for loading into Excel or other tools for custom analysis and prototyping.
* **Contest-Specific Scoring**: A modular system calculates QSO points based on the official rules for supported contests (ARRL-DX, ARRL-SS, CQ-WPX, CQ-WW).
* **Dynamic Reporting Engine**: A flexible, "plug-and-play" system for generating a wide variety of text, plot, and chart-based reports.

---
## Installation and Setup

### Preferred Method: Web Dashboard (Docker)
The easiest way to use the analyzer is via the containerized Web Dashboard.

1.  **Install Docker Desktop.**
2.  **Clone the Repository.**
3.  **Run:** `docker-compose up --build`
4.  **Open Browser:** Navigate to `http://localhost:8000`.

### Advanced Method: CLI
For automated workflows or developers, the Command Line Interface is available. See `Docs/InstallationGuide.md` for detailed Python/Conda setup instructions.

---
## Usage

The analyzer is run from the command line using `main_cli.py`. The examples below show basic usage. For a complete list of all command-line options, available reports, and usage details, please refer to the `Docs/UsersGuide.md`.

#### **Basic Syntax**

    python main_cli.py --report <ReportID|all|chart|text|plot|animation|html> <LogFile1> [<LogFile2>...] [options]

#### **Examples**

* **Generate all available reports for two logs:**

```
python main_cli.py --report all Logs/2024/cq-ww-cw/k3lr.log Logs/2024/cq-ww-cw/kc1xx.log
```

* **Generate a specific report (Score Summary) for a single log:**

```
python main_cli.py --report score_report Logs/2024/cq-ww-cw/k3lr.log
```

* **Generate a Missed Multipliers report for CQ WW Zones:**

```
python main_cli.py --report missed_multipliers --mult-name Zones Logs/2024/cq-ww-cw/k3lr.log Logs/2024/cq-ww-cw/kc1xx.log
```

---
## Supported Contests

The analyzer uses the `CONTEST:` field in the Cabrillo header to apply contest-specific rules. The following contests are currently supported:

* ARRL 10 Meter
* ARRL DX (CW & SSB)
* ARRL Field Day
* ARRL Sweepstakes
* CQ 160-Meter
* CQ WPX (CW & SSB)
* CQ World Wide DX (CW & SSB)
* IARU HF World Championship
* North American QSO Party (NAQP)
* WAE (CW & SSB)
* WRTC (via IARU-HF log)

---
## Available Reports

All generated files are saved to a structured directory under `reports/YYYY/CONTEST_NAME/`. For a detailed explanation of how to interpret each report, please see the `Docs/ReportInterpretationGuide.md`.

#### **Animation Reports (`animations/`)**
* `hourly_animation`: Hourly Rate Animation
* `wrtc_propagation_animation`: WRTC Propagation Animation

#### **HTML Reports (`html/`)**
* `html_qso_comparison`: HTML QSO Comparison Report

#### **Chart Reports (`charts/`)**
* `chart_point_contribution`: Point Contribution Breakdown
* `chart_point_contribution_single`: Point Contribution Breakdown (Single Log)
* `qso_breakdown_chart`: QSO Breakdown Chart

#### **Plot Reports (`plots/`)**
* `band_activity_heatmap`: Band Activity Heatmap
* `comparative_band_activity`: Comparative Band Activity
* `comparative_band_activity_heatmap`: Comparative Band Activity Heatmap
* `comparative_run_sp_timeline`: Comparative Activity Timeline (Run/S&P)
* `cumulative_difference_plots`: Cumulative Difference Plots
* `point_rate_plots`: Point Rate Comparison Plots
* `qso_rate_plots`: QSO Rate Comparison Plots
* `wrtc_propagation`: WRTC Propagation by Continent

#### **Text Reports (`text/`)**
* `comparative_continent_summary`: Comparative Continent QSO Summary
* `rate_sheet_comparison`: Comparative Rate Sheet
* `comparative_score_report`: Comparative Score Report
* `continent_breakdown`: Continent QSO Breakdown
* `continent_summary`: Continent QSO Summary
* `missed_multipliers`: Missed Multipliers Report
* `multiplier_summary`: Multiplier Summary
* `qso_comparison`: QSO Comparison Summary
* `rate_sheet`: Hourly Rate Sheet
* `score_report`: Score Summary
* `summary`: QSO Summary
* `text_wae_comparative_score_report`: WAE Comparative Score Report
* `text_wae_score_report`: WAE Score Summary

---
## License

This project is licensed under the **Mozilla Public License, v. 2.0**.