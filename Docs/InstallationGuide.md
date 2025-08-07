# Installation Guide - Contest Log Analyzer

**Version: 0.30.42-Beta**
**Date: 2025-08-07**

---
### --- Revision History ---
## [0.30.42-Beta] - 2025-08-07
# - Removed the Developer Guide section to create a separate, dedicated
#   document for developers.
## [0.30.30-Beta] - 2025-08-07
# - Synchronized documentation with the current code base.
# - Added Git workflow instructions for developers and beta testers.
## [0.30.0-Beta] - 2025-08-05
# - Initial release of Version 0.30.0-Beta.
---

This guide will help you install the latest stable beta release of the Contest Log Analyzer.

### Step 1: Clone the Repository

Before you begin, you will need to have **Git** installed on your system to download the project's source code. Open your command prompt or terminal, navigate to the directory where you want to store the project, and run the following command to download the software:

    git clone https://github.com/kd4d/Contest-Log-Analyzer.git "Contest-Log-Analyzer"
    cd "Contest-Log-Analyzer"

### Step 2: Create and Activate a Conda Environment

This project uses `conda` for environment and package management. It is highly recommended to create a dedicated environment to avoid conflicts with other Python projects.

    conda create --name contest-analyzer python=3.11 -y
    conda activate contest-analyzer

### Step 3: Install Dependencies

Once the environment is activated, install the required libraries using the following commands.

    conda update --all -y
    conda install pandas matplotlib seaborn -y

### Step 4: Set Up the Environment Variable

The program requires the `CONTEST_LOGS_REPORTS` environment variable to be set to the root directory containing your `Logs`, `data`, and `reports` subdirectories.

* **Windows (Temporary, for the current command prompt session):**

        set CONTEST_LOGS_REPORTS="C:\path\to\your\Contest-Log-Analyzer"

* **macOS/Linux (Temporary, for the current terminal session):**

        export CONTEST_LOGS_REPORTS="/path/to/your/Contest-Log-Analyzer"

### Step 5: Download Required Data Files

Create a `data` directory inside your `Contest-Log-Analyzer` project folder if it doesn't exist. Place the necessary data files in this directory.

* **Required for all contests:** `cty.dat` (available from [country-files.com](http://www.country-files.com/cty/cty.dat))
* **Required for ARRL DX:** `ARRLDXmults.dat`
* **Required for ARRL SS:** `SweepstakesSections.dat`

### Step 6: Updating to a New Version

When a new stable version is announced, navigate to your project directory in your terminal or command prompt and run this single command:

    git pull

This will download and apply all the updates for the latest beta release.