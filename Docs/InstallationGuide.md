# Contest Log Analyzer - Installation Guide

**Version: 0.47.2-Beta**
**Date: 2025-08-24**

---
### --- Revision History ---
## [0.47.2-Beta] - 2025-08-24
### Changed
# - Updated the description for SweepstakesSections.dat to correctly
#   include the ARRL Field Day contest.
## [0.47.1-Beta] - 2025-08-23
### Changed
# - Updated the conda install command to add `numpy` and remove `plotly`.
## [0.37.0-Beta] - 2025-08-18
### Changed
# - Aligned version with other documentation files.
# - Corrected the list of required data files in Step 6, removing the
#   obsolete reference to CQ160mults.dat and clarifying which
#   contests use each file.
## [0.35.22-Beta] - 2025-08-15
### Changed
# - Updated the list of required data files in Step 6 to be complete.
# - Removed the obsolete Kaleido dependency from the installation
#   command in Step 3.
## [0.33.1-Beta] - 2025-08-13
### Changed
# - Updated installation instructions to use a single, consolidated conda
#   command for all dependencies, including ffmpeg.
## [0.33.0-Beta] - 2025-08-13
### Added
# - Added plotly, kaleido, and imageio to the list of required libraries
#   to support the new animation reports.
## [1.1.0-Beta] - 2025-08-10
### Changed
# - Overhauled the installation process to use Git and Conda/Miniforge for
#   a more robust developer setup.
## [1.0.0-Beta] - 2025-08-10
### Added
# - Initial release of the Installation Guide.
# ---

## Introduction
This document provides instructions for setting up the Contest Log Analyzer application and its dependencies on a local computer. Following these steps will ensure that the application can find the necessary data files and has a place to write its output reports.
---
## 1. Prerequisites
Before you begin, ensure you have the following software installed on your system:
* **Git:** For cloning the source code repository.
* **Miniforge:** This is the recommended way to install Python and manage the project's libraries in an isolated environment. Miniforge is a minimal installer for the Conda package manager.
---
## 2. Installation Steps

### Step 1: Clone the Repository
Open a terminal or command prompt, navigate to the directory where you want to store the project, and clone the remote Git repository.
```
git clone [https://github.com/user/Contest-Log-Analyzer.git](https://github.com/user/Contest-Log-Analyzer.git)
cd Contest-Log-Analyzer
```
This will create the project directory (`Contest-Log-Analyzer`) on your local machine.
### Step 2: Create and Activate the Conda Environment
It is a best practice to create an isolated environment for the project's dependencies. This prevents conflicts with other Python projects on your system.
```
# Create an environment named "cla" with Python 3.11
conda create --name cla python=3.11

# Activate the new environment
conda activate cla
```

### Step 3: Install Libraries with Conda
With the `cla` environment active, use the following single command to install all required libraries from the recommended `conda-forge` channel. This includes `ffmpeg` for video creation.
```
conda install -c conda-forge pandas numpy matplotlib seaborn imageio ffmpeg
```

### Step 4: Set Up the Data and Reports Directory
The application requires a specific directory structure for its operation. You must create a main directory that will contain your log files, required data files, and the output reports. This directory can be anywhere on your system, but it is recommended to place it outside of the source code directory.
For example, create a main folder `C:\Users\devnu\Desktop\CLA_Data`. Inside this folder, you must create the following subdirectories:

```
CLA_Data/
|
+-- data/
|
+-- logs/
|
+-- reports/
```

### Step 5: Set the Environment Variable
You must set a system environment variable named **`CONTEST_LOGS_REPORTS`** that points to the main data directory you created in the previous step.
**For Windows:**
1.  Open the Start Menu and search for "Edit the system environment variables."
2.  In the System Properties window, click the "Environment Variables..." button.
3.  In the "User variables" section, click "New...".
4.  For "Variable name," enter: `CONTEST_LOGS_REPORTS`
5.  For "Variable value," enter the full path to your main directory (e.g., `C:\Users\devnu\Desktop\CLA_Data`).
6.  Click OK to close all windows. You must **restart** your terminal or command prompt for the change to take effect.
### Step 6: Obtain and Place Data Files
The analyzer relies on several external data files. Download the following files and place them inside the **`data/`** subdirectory you created in Step 4.

* `cty.dat`: Required for all contests.
* `arrl_10_mults.dat`: Required for the ARRL 10 Meter contest.
* `ARRLDXmults.dat`: Required for the ARRL DX contest.
* `NAQPmults.dat`: Required for NAQP and CQ 160-Meter contests.
* `SweepstakesSections.dat`: Required for ARRL Sweepstakes and ARRL Field Day.
---
## 3. Running the Analyzer
To verify the installation, run the program from the project's source code directory. Ensure your `cla` conda environment is active.

```
# Make sure your conda environment is active
conda activate cla

# Run the script from the main project directory
(cla) C:\Users\devnu\Desktop\Contest-Log-Analyzer>python main_cli.py --report score_report ..\CLA_Data\logs\2025\NAQP-CW\aug\k3aj.log
```

If the installation is successful, you will see an output message indicating that the report was saved, and you will find a new `.txt` file in your `CLA_Data\reports` subdirectory.