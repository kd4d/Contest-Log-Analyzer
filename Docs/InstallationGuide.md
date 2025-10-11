# Contest Log Analyzer - Installation Guide

**Version: 0.91.14-Beta**
**Date: 2025-10-10**

---
### --- Revision History ---
## [0.91.14-Beta] - 2025-10-10
### Fixed
# - Added missing `CQ160mults.dat` to the list of required data files.
## [0.90.13-Beta] - 2025-10-06
### Fixed
# - Added missing `requests` and `beautifulsoup4` libraries to the conda
#   installation command in Step 3. These are required by the cty_manager
#   for web scraping.
## [0.62.0-Beta] - 2025-09-08
### Changed
# - Overhauled directory and environment variable setup to use a separate
#   input (CONTEST_INPUT_DIR) and output (CONTEST_REPORTS_DIR) path.
## [0.56.29-Beta] - 2025-09-01
### Fixed
# - Added the missing `prettytable` and `tabulate` libraries to the
#   conda installation command.
# - Added the missing `iaru_officials.dat` file to the list of
#   required data files.
## [0.47.4-Beta] - 2025-08-28
### Changed
# - Added the mandatory `imageio-ffmpeg` package to the conda install
#   command to ensure the video animation backend is found correctly.
## [0.47.3-Beta] - 2025-08-25
### Added
# - Added the required `band_allocations.dat` file to the list of
#   required data files in Step 6.
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
```_
git clone [https://github.com/user/Contest-Log-Analyzer.git](https://github.com/user/Contest-Log-Analyzer.git)
cd Contest-Log-Analyzer
```_
This will create the project directory (`Contest-Log-Analyzer`) on your local machine.
### Step 2: Create and Activate the Conda Environment
It is a best practice to create an isolated environment for the project's dependencies. This prevents conflicts with other Python projects on your system.
```_
# Create an environment named "cla" with Python 3.11
conda create --name cla python=3.11

# Activate the new environment
conda activate cla
```_

### Step 3: Install Libraries with Conda
With the `cla` environment active, use the following single command to install all required libraries from the recommended `conda-forge` channel. This includes `ffmpeg` for video creation.
```_
conda install -c conda-forge pandas numpy matplotlib seaborn imageio imageio-ffmpeg ffmpeg prettytable tabulate requests beautifulsoup4
```_

### Step 4: Set Up the Input and Output Directories
The application requires separate directories for its input files (logs, data) and its output files (reports). This separation is critical to prevent file-locking issues with cloud sync services.

**1. Create the Input Directory:** This folder will contain your log files and required data files. It can be located anywhere, including inside a cloud-synced folder like OneDrive.
Example: `C:\Users\YourUser\OneDrive\Desktop\CLA_Inputs`
Inside this folder, you must create the following subdirectories:
```_
CLA_Inputs/
|
+-- data/
|
+-- Logs/
```_

**2. Create the Output Directory:** This folder is where the analyzer will save all generated reports. **This directory must be on a local, non-synced path.** A recommended location is in your user profile directory.
Example: `%USERPROFILE%\HamRadio\CLA` (which translates to `C:\Users\YourUser\HamRadio\CLA`)

### Step 5: Set the Environment Variables
You must set two system environment variables that point to the directories you created in the previous step.
* **`CONTEST_INPUT_DIR`**: Points to your main input directory (e.g., `C:\Users\YourUser\OneDrive\Desktop\CLA_Inputs`).
* **`CONTEST_REPORTS_DIR`**: Points to your main output directory (e.g., `C:\Users\YourUser\HamRadio\CLA`).
**For Windows:**
1.  Open the Start Menu and search for "Edit the system environment variables."
2.  In the System Properties window, click the "Environment Variables..." button.
3.  In the "User variables" section, click "New..." and create both variables.
4.  Click OK to close all windows. You must **restart** your terminal or command prompt for the changes to take effect.
### Step 6: Obtain and Place Data Files
The analyzer relies on several external data files. Download the following files and place them inside the **`data/`** subdirectory within your **Input Directory** (`CONTEST_INPUT_DIR`).
* `cty.dat`: Required for all contests.
* `CQ160mults.dat`: Required for the CQ 160-Meter contest.
* `arrl_10_mults.dat`: Required for the ARRL 10 Meter contest.
* `ARRLDXmults.dat`: Required for the ARRL DX contest.
* `NAQPmults.dat`: Required for NAQP and CQ 160-Meter contests.
* `SweepstakesSections.dat`: Required for ARRL Sweepstakes and ARRL Field Day.
* `band_allocations.dat`: Required for all contests to perform frequency validation.
* `iaru_officials.dat`: Required for the IARU HF World Championship contest.
---
## 3. Running the Analyzer
To verify the installation, run the program from the project's source code directory. Ensure your `cla` conda environment is active.

```_
# Make sure your conda environment is active
conda activate cla

# Run the script from the main project directory, providing a relative path
# to a log file inside your CONTEST_INPUT_DIR
(cla) C:\..._Analyzer>python main_cli.py --report score_report 2025/NAQP-CW/aug/k3aj.log
```_

If the installation is successful, you will see an output message indicating that the report was saved, and you will find a new `.txt` file in a `reports` subdirectory inside your `CONTEST_REPORTS_DIR`.