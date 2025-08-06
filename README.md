# Contest Log Analyzer

**Version: 0.30.30-Beta**
**Date: 2025-08-05**

[cite_start]A Python-based tool for in-depth analysis and comparison of amateur radio contest logs. [cite: 1021] [cite_start]This application processes standard Cabrillo files to generate detailed reports, charts, and visualizations, providing deep insights into operator strategy and performance. [cite: 1022]
---
## Key Features

* [cite_start]**Data-Driven Architecture**: Uses simple JSON files to define the rules, scoring, and exchange formats for each contest, making the tool highly extensible. [cite: 1023]
* [cite_start]**Run/S&P Heuristics**: A sophisticated, multi-pass heuristic analyzes QSO timing and frequency to classify each contact as "Run," "Search & Pounce," or "Unknown," providing a clear picture of operating strategy. [cite: 1024]
* [cite_start]**Unique vs. Common QSO Analysis**: The analyzer precisely identifies "unique" QSOs (worked by only one of two logs) and "common" QSOs (worked by both), breaking them down by Run/S&P status to reveal strategic advantages. [cite: 1025]
* [cite_start]**Cumulative Difference Plots**: Goes beyond traditional rate graphs by presenting QSO and Point rate data in "Cumulative Difference Plots," which visualize performance trends and momentum shifts much more clearly. [cite: 1026]
* [cite_start]**Annotated CSV Output**: Generates detailed, "annotated" CSV files from the processed logs, perfect for loading into Excel or other tools for custom analysis and prototyping. [cite: 1027]
* [cite_start]**Contest-Specific Scoring**: A modular system calculates QSO points based on the official rules for supported contests (ARRL-DX, ARRL-SS, CQ-WPX, CQ-WW). [cite: 1028]
* [cite_start]**Dynamic Reporting Engine**: A flexible, "plug-and-play" system for generating a wide variety of text, plot, and chart-based reports. [cite: 1029]
---
## Installation

[cite_start]This project uses `conda` for environment and package management. [cite: 1030]
#### 1. Clone the Repository

    git clone https://github.com/kd4d/Contest-Log-Analyzer.git "Contest-Log-Analyzer"
    cd "Contest-Log-Analyzer"

#### 2. Create and Activate Conda Environment

[cite_start]It is recommended to use Miniforge and create a dedicated environment. [cite: 1032]

    conda create --name contest-analyzer python=3.11 -y
    conda activate contest-analyzer

#### 3. Install Dependencies

[cite_start]Update the base packages and then install the required libraries. [cite: 1033]

    conda update --all -y
    conda install pandas matplotlib seaborn -y

#### 4. Set Up Environment Variable

[cite_start]The program requires the `CONTEST_LOGS_REPORTS` environment variable to be set to the root directory containing your `Logs`, `data`, and `reports` subdirectories. [cite: 1033]
* **Windows (Temporary):**
    
        set CONTEST_LOGS_REPORTS="C:\path\to\your\Contest-Log-Analyzer"
    
* **macOS/Linux (Temporary):**

        export CONTEST_LOGS_REPORTS="/path/to/your/Contest-Log-Analyzer"

#### 5. Download Data Files

[cite_start]Place the necessary data files in a central `data/` directory. [cite: 1035]
* [cite_start]**Required for all contests:** `cty.dat` (from [country-files.com](http://www.country-files.com/cty/cty.dat)) [cite: 1035]
* **Required for ARRL DX:** `ARRLDXmults.dat`
* **Required for ARRL SS:** `SweepstakesSections.dat`

---
## Usage

[cite_start]The analyzer is run from the command line using `main_cli.py`. [cite: 1036]
#### **Basic Syntax**

    python main_cli.py --report <ReportID|all|chart|text|plot> <LogFile1> [<LogFile2>...] [options]

#### **Examples**

* **Generate all available reports for two logs:**

        python main_cli.py --report all Logs/2025/cq-160-cw/kd4d.log Logs/2025/cq-160-cw/n0ni.log

* **Generate only the plot reports for two logs:**

        python main_cli.py --report plot Logs/2025/cq-160-cw/kd4d.log Logs/2025/cq-160-cw/n0ni.log

* **Generate a specific report (Score Summary) for a single log:**

        python main_cli.py --report score_report Logs/2025/cq-160-cw/kd4d.log

* **Generate a Missed Multipliers report for CQ WW Zones:**

        python main_cli.py --report missed_multipliers --mult-name Zones Logs/2024/cq-ww-cw/k3lr.log Logs/2024/cq-ww-cw/kc1xx.log

---
## Available Reports

[cite_start]All generated files are saved to a structured directory under `reports/YYYY/CONTEST_NAME/EVENT_ID/CALLSIGN_COMBO/`. [cite: 1148, 1162, 1165]
#### **Text Reports (`text/`)**

* [cite_start]`summary`: High-level overview of QSO counts (Run, S&P, Unknown). [cite: 1037]
* [cite_start]`score_report`: Comprehensive score breakdown by band for a single log. [cite: 1038]
* [cite_start]`rate_sheet`: Detailed hourly QSO rates per band for a single log. [cite: 1039]
* [cite_start]`rate_sheet_comparison`: Side-by-side hourly rate comparison for multiple logs. [cite: 1040]
* [cite_start]`qso_comparison`: Detailed pairwise breakdown of Total, Unique, and Common QSOs. [cite: 1040]
* [cite_start]`missed_multipliers`: Comparative report showing multipliers missed by each station. [cite: 1041]
* [cite_start]`multiplier_summary`: Detailed breakdown of QSOs per multiplier. [cite: 1041]
* [cite_start]`multipliers_by_hour`: Shows new multipliers worked each hour of the contest. [cite: 1042]
* [cite_start]`continent_summary`: Total QSOs per continent for a single log. [cite: 1043]
* [cite_start]`comparative_continent_summary`: Side-by-side comparison of QSOs per continent. [cite: 1043]
* [cite_start]`continent_breakdown`: Detailed QSOs per continent broken down by Run/S&P status. [cite: 1044]

#### **Plots (`plots/`)**

* [cite_start]`qso_rate_plots`: Cumulative QSO rate line graphs. [cite: 1045]
* [cite_start]`point_rate_plots`: Cumulative point rate line graphs. [cite: 1045]
* [cite_start]`cumulative_difference_plots`: Plot showing the running QSO or Point difference between two logs. [cite: 1045]

#### **Charts (`charts/`)**

* [cite_start]`qso_breakdown_chart`: Stacked bar chart comparing unique QSO counts for two logs. [cite: 1046]
* [cite_start]`chart_point_contribution`: Side-by-side pie charts comparing point sources. [cite: 1047]
* [cite_start]`chart_point_contribution_single`: Per-band pie charts showing point sources for one log. [cite: 1047]
---
## License

[cite_start]This project is licensed under the **Mozilla Public License, v. 2.0**. [cite: 1048]