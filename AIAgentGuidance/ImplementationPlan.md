# Implementation Plan - Run/SP Plot Standardization

## 1. Builder Bootstrap Context
* **Target File:** `plot_comparative_run_sp.py`
* **Goal:** Refactor legacy script to meet Phase 2 Visualization Standards (Two-line titles, flexible I/O, robust styling).
* **Context:** This script analyzes the ratio of Run (calling CQ) vs. Search & Pounce (S/P) QSOs.

## 2. Technical Debt Register
* **Observed:** The current script likely uses hardcoded filenames or legacy command-line parsing.
* **Remediation:** Implement `argparse` for robust input/output handling.

## 3. Proposed Changes

### 3.1 Refactor `plot_comparative_run_sp.py`
* **Action:** Rewrite the script structure to separate data loading, processing, and visualization.
* **Standardization Requirements (Protocol 2.5.7):**
    * **CLI:** Use `argparse`. Accept `--input` (CSV/Log), `--output` (Image path), and `--title` (Optional override).
    * **Visuals:**
        * **Title:** Enforce "Two-Line Title" format (Main Title in bold/larger, Subtitle with context).
        * **Layout:** Use `constrained_layout=True` or `tight_layout`.
        * **Typography:** Ensure axis labels and legends are Left-Anchored where possible/applicable.
    * **Logic:**
        * Load data (Pandas recommended).
        * Calculate Run vs S/P intervals (if not pre-calculated).
        * Plot Stacked Bar or Line chart (preserve original logic but enhance style).
* **Output:** The script must save the figure to the specified output path without displaying the GUI (non-interactive backend).

## 4. Verification Plan
### 4.1 Automated Verification
* **Command:** `python plot_comparative_run_sp.py --help`
* **Success Criteria:** The help message must display the new arguments (`--input`, `--output`).

### 4.2 Visual Verification
* **Command:** (Builder to provide specific test command based on available data)
* **Success Criteria:** Visual inspection of the generated PNG to confirm Two-Line Title and layout.