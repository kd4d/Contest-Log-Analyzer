# Installation Guide - Contest Log Analyzer

**Version: 0.30.30-Beta**
**Date: 2025-08-05**

---
### --- Revision History ---
## [0.30.30-Beta] - 2025-08-05
# - Updated environment variable from CONTEST_DATA_DIR to CONTEST_LOGS_REPORTS.
## [0.30.0-Beta] - 2025-08-05
# - Initial release of Version 0.30.0-Beta.
# - Standardized all project files to a common baseline version.
---

[cite_start]This guide provides step-by-step instructions to set up the Contest Log Analyzer on your system. [cite: 2102] [cite_start]The process involves installing a Python distribution, setting up a dedicated environment, installing the required libraries, and configuring the necessary data files. [cite: 2103]
---

### Step 1: Clone the Repository

[cite_start]Before you begin, you will need to have **Git** installed on your system to download the project's source code. [cite: 2104] [cite_start]Open your command prompt or terminal, navigate to the directory where you want to store the project, and run the following command: [cite: 2105]

    git clone https://github.com/kd4d/Contest-Log-Analyzer.git "Contest-Log-Analyzer"
    cd "Contest-Log-Analyzer"
---
### Step 2: Create and Activate a Conda Environment

[cite_start]This project uses `conda` for environment and package management. [cite: 2106] [cite_start]It is highly recommended to create a dedicated environment to avoid conflicts with other Python projects. [cite: 2106]

    conda create --name contest-analyzer python=3.11 -y
    conda activate contest-analyzer
---
### Step 3: Install Dependencies

[cite_start]Once the environment is activated, install the required libraries. [cite: 2108]

    conda update --all -y
    conda install pandas matplotlib seaborn -y
---
### Step 4: Set Up the Environment Variable

[cite_start]The program requires the `CONTEST_LOGS_REPORTS` environment variable to be set to the root directory containing your `Logs`, `data`, and `reports` subdirectories. [cite: 2108]
* [cite_start]**Windows (Temporary, for the current command prompt session):** [cite: 2109]

        set CONTEST_LOGS_REPORTS="C:\path\to\your\Contest-Log-Analyzer"

* [cite_start]**macOS/Linux (Temporary, for the current terminal session):** [cite: 2109]

        export CONTEST_LOGS_REPORTS="/path/to/your/Contest-Log-Analyzer"
---
### Step 5: Download Required Data Files

[cite_start]Create a `data` directory inside your `Contest-Log-Analyzer` project folder if it doesn't exist. [cite: 2110] [cite_start]Place the necessary data files in this directory. [cite: 2110]

* [cite_start]**Required for all contests:** `cty.dat` (available from [country-files.com](http://www.country-files.com/cty/cty.dat)) [cite: 2110]
* [cite_start]**Required for ARRL DX:** `ARRLDXmults.dat` [cite: 2110]
* [cite_start]**Required for ARRL SS:** `SweepstakesSections.dat` [cite: 2110]