--- FILE: Docs/InstallationGuide.md ---
# Installation Guide - Contest Log Analyzer

**Version: 0.30.31-Beta**
**Date: 2025-08-06**

---
### --- Revision History ---
## [0.30.31-Beta] - 2025-08-06
### Changed
# - Updated documentation to refer to the primary branch as "Master".
## [0.30.30-Beta] - 2025-08-05
# - Updated environment variable from CONTEST_DATA_DIR to CONTEST_LOGS_REPORTS.
## [0.30.0-Beta] - 2025-08-05
# - Initial release of Version 0.30.0-Beta.
# - Standardized all project files to a common baseline version.
---

This guide provides step-by-step instructions to set up the Contest Log Analyzer on your system. The process involves installing a Python distribution, setting up a dedicated environment, installing the required libraries, and configuring the necessary data files.
---

### Step 1: Clone the Repository

Before you begin, you will need to have **Git** installed on your system to download the project's source code. Open your command prompt or terminal, navigate to the directory where you want to store the project, and run the following command to clone the **Master** branch:

    git clone https://github.com/kd4d/Contest-Log-Analyzer.git "Contest-Log-Analyzer"
    cd "Contest-Log-Analyzer"
---
### Step 2: Create and Activate a Conda Environment

This project uses `conda` for environment and package management. It is highly recommended to create a dedicated environment to avoid conflicts with other Python projects.

    conda create --name contest-analyzer python=3.11 -y
    conda activate contest-analyzer
---
### Step 3: Install Dependencies

Once the environment is activated, install the required libraries.

    conda update --all -y
    conda install pandas matplotlib seaborn -y
---
### Step 4: Set Up the Environment Variable

The program requires the `CONTEST_LOGS_REPORTS` environment variable to be set to the root directory containing your `Logs`, `data`, and `reports` subdirectories.
* **Windows (Temporary, for the current command prompt session):**

        set CONTEST_LOGS_REPORTS="C:\path\to\your\Contest-Log-Analyzer"

* **macOS/Linux (Temporary, for the current terminal session):**

        export CONTEST_LOGS_REPORTS="/path/to/your/Contest-Log-Analyzer"
---
### Step 5: Download Required Data Files

Create a `data` directory inside your `Contest-Log-Analyzer` project folder if it doesn't exist. Place the necessary data files in this directory.

* **Required for all contests:** `cty.dat` (available from [country-files.com](http://www.country-files.com/cty/cty.dat))
* **Required for ARRL DX:** `ARRLDXmults.dat`
* **Required for ARRL SS:** `SweepstakesSections.dat`