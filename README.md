# Contest Log Analyzer

**Version 0.15.0-Beta**

A Python-based tool for in-depth analysis and comparison of amateur radio contest logs. This application processes standard Cabrillo files to generate detailed reports, charts, and visualizations, providing deep insights into operator strategy and performance.

---

## Key Features

* **Advanced Log Processing:** Ingests standard Cabrillo files and enriches the data with universal annotations (DXCC, WAE, Continent, Zones) and contest-specific data.
* **Run/S&P/Unknown Classification:** A sophisticated, multi-pass heuristic analyzes QSO patterns to classify each contact as "Run," "Search & Pounce," or "Unknown," providing a clear picture of operating strategy.
* **Contest-Specific Scoring:** A modular system calculates QSO points based on the official rules for supported contests (currently CQ WPX and CQ WW).
* **Data-Driven Reporting Engine:** A flexible, "plug-and-play" system for generating a wide variety of text, plot, and chart-based reports.
* **Comparative Analysis:** Most reports are designed for pairwise or multi-log comparison, allowing you to analyze your performance against others.

## Installation

This project uses `conda` for environment and package management.

#### 1. Clone the Repository

```bash
git clone [https://github.com/kd4d/Contest-Log-Analyzer.git](https://github.com/kd4d/Contest-Log-Analyzer.git) "Contest-Log-Analyzer"
cd "Contest-Log-Analyzer"
```

#### 2. Create and Activate Conda Environment

It is recommended to use Miniforge and create a dedicated environment.

```bash
conda create --name contest-analyzer python=3.11 -y
conda activate contest-analyzer
```

#### 3. Install Dependencies

Update the base packages and then install the required libraries.

```bash
conda update --all -y
conda install pandas matplotlib seaborn shapely -y
```

#### 4. Set Up Environment Variable

The program requires the `CTY_DAT_PATH` environment variable to be set to the location of your main `cty.dat` file.

* **Windows (Temporary):**
    ```cmd
    set CTY_DAT_PATH="C:\path\to\your\Contest-Log-Analyzer\data\cty.dat"
    ```
* **macOS/Linux (Temporary):**
    ```bash
    export CTY_DAT_PATH="/path/to/your/Contest-Log-Analyzer/data/cty.dat"
    ```

#### 5. Download Country Files

Place the necessary country files in the `data/` directory.

* **Required for all contests:** `cty.dat` (from [country-files.com](http://www.country-files.com/cty/cty.dat))
* **Required for CQ WW:** `cqww.cty` (from [country-files.com/cq/cqww.cty](http://www.country-files.com/cq/cqww.cty))

---

## Usage

The analyzer is run from the command line using `main_cli.py`.

#### **Basic Syntax**

```bash
python main_cli.py --report <ReportID|all> <LogFile1> [<LogFile2>...] [options]
```

#### **Examples**

* **Generate all available reports for two logs:**
    ```bash
    python main_cli.py --report all Logs/2025/cq-wpx-cw/k3lr.log Logs/2025/cq-wpx-cw/kc1xx.log
    ```

* **Generate a specific report (Rate Sheet) for a single log:**
    ```bash
    python main_cli.py --report rate_sheet Logs/2025/cq-wpx-cw/k3lr.log
    ```

* **Generate a Missed Multipliers report for CQ WW Zones:**
    ```bash
    python main_cli.py --report missed_multipliers --mult-name Zones Logs/2024/cq-ww-cw/k3lr.log Logs/2024/cq-ww-cw/kc1xx.log
    ```

* **Generate a Cumulative Difference plot for QSO Points:**
    ```bash
    python main_cli.py --report cumulative_difference_plots --metric points k3lr.log kc1xx.log
    ```

---

## Available Reports

All generated files are saved to a structured directory under `reports_output/YYYY/CONTEST_NAME/`.

#### **Text Reports (`text/`)**

* `summary`: High-level overview of QSO counts (Run, S&P, Unknown).
* `rate_sheet`: Detailed hourly QSO rates per band for a single log.
* `rate_sheet_comparison`: Side-by-side hourly rate comparison for multiple logs.
* `qso_comparison`: Detailed pairwise breakdown of Total, Unique, and Common QSOs by Run/S&P/Unknown.
* `missed_multipliers`: Comparative report showing multipliers missed by each station. Requires `--mult-name`.

#### **Plots (`plots/`)**

* `qso_rate_plots`: Cumulative QSO rate line graphs.
* `point_rate_plots`: Cumulative point rate line graphs.
* `cumulative_difference_plots`: Three-panel plot showing the running QSO or Point difference between two logs.

#### **Charts (`charts/`)**

* `qso_breakdown_chart`: Stacked bar chart comparing the unique Run/S&P/Unknown QSO counts for two logs.
* `venn_diagrams`: Area-proportional Venn diagrams visualizing the overlap of worked callsigns.

---

## License

This project is licensed under the **Mozilla Public License, v. 2.0**. See the `MPL2.0.htm` file for details.
