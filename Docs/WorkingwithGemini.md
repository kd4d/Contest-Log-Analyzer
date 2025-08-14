# Project Workflow Guide

**Version: 0.32.16-Beta**
**Date: 2025-08-13**

---
### --- Revision History ---
## [0.32.16-Beta] - 2025-08-13
### Added
# - Added Core Principle 8 (Surgical Modification).
# - Added Special Case Protocol 7.3 (Fragile Dependency).
# - Added Development Philosophy 5.5 (Data-Driven Scoring).
## [0.32.15-Beta] - 2025-08-12
### Changed
# - Updated Versioning Protocol (3.4) to reflect atomic versioning.
# - Added Core Principle 7 (Non-Destructive Reporting).
# - Added protocol for "Per-Mode" multiplier logic (5.4).
# - Added protocol for the Custom Parser plug-in pattern (2.4).
## [0.33.0-Beta] - 2025-08-12
### Changed
# - Overhauled the versioning protocol (3.4) to use an atomic,
#   minor-version-bump strategy. All files in a single logical
#   update now receive the same version number.
---

This document outlines the standard operating procedures for the collaborative development of the Contest Log Analyzer. **The primary audience for this document is the Gemini AI agent.**

**Its core purpose is to serve as a persistent set of rules and context.** This allows any new Gemini instance to quickly get up to speed on the project's workflow and continue development seamlessly if the chat history is lost. Adhering to this workflow ensures consistency and prevents data loss.
---
## Part I: Core Principles

These are the foundational rules that govern all interactions and analyses.

1.  **Protocol Adherence is Paramount.** All protocols must be followed with absolute precision. Failure to do so invalidates the results and undermines the development process. There is no room for deviation unless a deviation is explicitly requested by the AI and authorized by the user.

2.  **Trust the User's Diagnostics.** When the user reports a bug, their description of the symptoms should be treated as the ground truth. The AI's primary task is to find the root cause of those specific, observed symptoms, not to propose alternative theories.

3.  **No Unrequested Changes.** The AI will only implement changes explicitly requested by the user. All suggestions for refactoring, library changes, or stylistic updates must be proposed and approved by the user before implementation.

4.  **Technical Diligence Over Conversational Assumptions.** Technical tasks are not conversations. Similar-looking prompts do not imply similar answers. Each technical request must be treated as a unique, atomic operation. The AI must execute a full re-computation from the current project state for every request, ignoring any previous results or cached data.

5.  **Prefer Logic in Code, Not Data.** The project's design philosophy is to keep the `.json` definition files as simple, declarative maps. All complex, conditional, or contest-specific logic should be implemented in dedicated Python modules.

6.  **Assume Bugs are Systemic.** When a bug is identified in one module, the default assumption is that the same flaw exists in all other similar modules. The AI must perform a global search for that specific bug pattern and fix all instances at once.

7.  **Reports Must Be Non-Destructive.** Specialist report scripts must **never** modify the original `ContestLog` objects they receive. All data filtering or manipulation must be done on a temporary **copy** of the DataFrame.

8.  **Principle of Surgical Modification.** All file modifications must be treated as surgical operations. The AI must start with the last known-good version of a file as the ground truth and apply only the minimal, approved change. Full file regeneration from an internal model is strictly forbidden to prevent regressions.
---
## Part II: Standard Operating Protocols

### 1. Session Management

1.1. **Onboarding Protocol.** The first action for any AI agent upon starting a session is to read this document in its entirety, acknowledge it, and ask any clarifying questions.

1.2. **Definitive State Reconciliation Protocol.** This protocol is triggered by **any request to update a project file.** The AI must:
    1.  **Re-establish Definitive State** by working backward through the chat history to find the most recent, correct version of all project files.
    2.  **Review Every File** in the definitive state.
    3.  **Proceed with the Task**.

1.3. **Context Checkpoint Protocol.** If the AI appears to have lost context, the user can issue a **Context Checkpoint**.
    1.  The user begins with the exact phrase: **"Gemini, let's establish a Context Checkpoint."**
    2.  The user provides a brief, numbered list of critical facts.

1.4. **Definitive State Initialization Protocol.** This protocol serves as a "hard reset" of the project state.
    1.  **Initiation:** The user or AI requests a "Definitive State Initialization."
    2.  **Agreement:** The other party agrees to proceed.
    3.  **File Upload:** The user creates and uploads new, complete `project_bundle.txt` and `documentation_bundle.txt` files.
    4.  **State Purge:** The AI discards its current understanding of the project state.
    5.  **Re-Initialization:** The AI establishes a new definitive state based *only* on the new bundles.
    6.  **Verification and Acknowledgment:** The AI acknowledges the new state and provides a complete list of all files extracted from the bundles.

1.5. **Document Review and Synchronization Protocol.** This protocol is used to methodically review and update all project documentation.
    ...

### 2. Task Execution Workflow

2.1. **Decomposition of Complexity.** Complex requests must be broken down into smaller, sequential steps.

2.2. **Pre-Flight Check Protocol.** The AI will perform a "white-box" mental code review **before** delivering a modified file.

2.3. **Code Modification Protocol.**
    1.  **Strictly Adhere to Requested Changes**.
    2.  **Modify, Don't Regenerate**.
    3.  **Propose, Don't Impose**.
    4.  **Forward-Only Modification**.

2.4. **Custom Parser Protocol.** For contests with highly complex or asymmetric exchanges.
    1.  **Activation**: A new key, `"custom_parser_module": "module_name"`, is added to the contest's `.json` file.
    2.  **Hook**: The `contest_log.py` script detects this key and calls the specified module.
    3.  **Implementation**: The custom parser module is placed in the `contest_specific_annotations` directory.

### 3. File and Data Handling

3.4. **Versioning Protocol.**
    1.  **Minor Version Bumps:** Major changes will increment the minor version number (e.g., `0.31.x` -> `0.32.0`).
    2.  **Atomic Versioning:** All files modified as part of a single, logical update will receive the **same version number**.
    3.  **Patch Increments:** Subsequent logical updates will increment the patch number (e.g., `0.32.0` -> `0.32.1`).
    4.  **Header Updates:** Every changed file must have its `Version:`, `Date:`, and `Revision History` updated.

...

### 5. Development Philosophy

...

5.4. **Per-Mode Multiplier Protocol.** For contests where multipliers are counted independently for each mode.
    1.  **Activation**: The contest's `.json` file must contain `"multiplier_report_scope": "per_mode"`.
    2.  **Generator Logic**: This instructs the `report_generator.py` to run multiplier reports separately for each mode.
    3.  **Report Logic**: The specialist reports must accept a `mode_filter` argument.

5.5. **Data-Driven Scoring Protocol.** To accommodate different scoring methods, the `score_formula` key is available in the contest's `.json` definition. If set to `"qsos_times_mults"`, the final score will be `Total QSOs x Total Multipliers`. If omitted, it defaults to `Total QSO Points x Total Multipliers`.
---
## Part III: Special Case & Recovery Protocols

...

### 7. Miscellaneous Protocols

...

7.3. **Fragile Dependency Protocol.** If a third-party library proves to be unstable, a sprint will be conducted to replace it with a more robust alternative (e.g., replacing the Kaleido rendering engine with Matplotlib's native `savefig` functionality).