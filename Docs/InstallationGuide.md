Filename: "Docs/InstallationGuide.md"

# Installation Guide - Contest Log Analyzer

**Version: 0.26.7-Beta**
**Date: 2025-08-03**

This guide provides step-by-step instructions to set up the Contest Log Analyzer on your system. The process involves installing a Python distribution, setting up a dedicated environment, installing the required libraries, and configuring the necessary data files.
---

### Step 1: Clone the Repository

Before you begin, you will need to have **Git** installed on your system to download the project's source code. Open your command prompt or terminal, navigate to the directory where you want to store the project, and run the following command:

    git clone [https://github.com/kd4d/Contest-Log-Analyzer.git](https://github.com/kd4d/Contest-Log-Analyzer.git) "Cont-Log-Analyzer"
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

The program requires the `CONTEST_DATA_DIR` environment variable to be set to the location of your data directory. This tells the analyzer where to find files like `cty.dat`.

* **Windows (Temporary, for the current command prompt session):**

    set CONTEST_DATA_DIR="C:\path\to\your\Contest-Log-Analyzer\data"

* **macOS/Linux (Temporary, for the current terminal session):**

    export CONTEST_DATA_DIR="/path/to/your/Contest-Log-Analyzer/data"
---
### Step 5: Download Required Data Files

Create a `data` directory inside your `Contest-Log-Analyzer` project folder if it doesn't exist. Place the necessary data files in this directory.

* **Required for all contests:** `cty.dat` (available from [country-files.com](http://www.country-files.com/cty/cty.dat))
* **Required for ARRL DX:** `ARRLDXmults.dat`
* **Required for ARRL SS:** `SweepstakesSections.dat`