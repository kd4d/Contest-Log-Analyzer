--- FILE: Docs/Working with Gemini.md ---
# Project Workflow Guide

**Version: 0.31.1-Beta**
**Date: 2025-08-07**

---
### --- Revision History ---
## [0.31.1-Beta] - 2025-08-07
### Changed
# - Formalized the "Explicit State-Transition Protocol" in Section 9 to
#   ensure reliable execution of multi-step tasks by making the user
#   the controller of the sequence.
## [0.31.0-Beta] - 2025-08-07
# - Initial release of Version 0.31.0-Beta.
# ---

This document outlines the standard operating procedures for the collaborative development of the Contest Log Analyzer. **The primary audience for this document is the Gemini AI agent.**

**Its core purpose is to serve as a persistent set of rules and context.** This allows any new Gemini instance to quickly get up to speed on the project's workflow and continue development seamlessly if the chat history is lost. Adhering to this workflow ensures consistency and prevents data loss.
---

### Guiding Principles

1.  **Trust the User's Diagnostics.** When the user reports a bug, their description of the symptoms (e.g., "the multipliers are too high," "the report is all zeros") should be treated as the ground truth. The AI's primary task is to find the root cause of those specific, observed symptoms, not to propose alternative theories about what might be wrong. If the AI cannot find the root cause, the AI can then ask the user questions.

2.  **Debug "A Priori" When Stuck.** If an initial bug fix fails, do not simply try to patch the failed fix. Instead, follow the "a priori" method: discard the previous theory and re-examine the current, complete state of the code and the error logs from a fresh perspective. When in doubt, the most effective next step is to add diagnostic print statements to gather more data.

3.  **Prefer Logic in Code, Not Data.** The project's design philosophy is to keep the `.json` definition files as simple, declarative maps. All complex, conditional, or contest-specific logic should be implemented in dedicated Python modules (e.g., `cq_160_multiplier_resolver.py`). This makes the system more robust and easier to maintain.

4.  **Assume Bugs are Systemic.** When a bug is identified in one module (e.g., a report or a resolver), the default assumption is that the same flaw exists in all other similar modules. The AI's primary directive is to perform a global search for that specific bug pattern across the entire project and fix all instances at once, rather than treating the initial report as an isolated incident.

5.  **No Unrequested Changes.** The AI will only implement changes explicitly requested by the user. All suggestions for refactoring, library changes, or stylistic updates must be proposed and approved by the user before implementation. Any changes not directly related to the user's request are strictly forbidden.
---

## 1. Project File Input

All project source files (`.py`, `.json`) and documentation files (`.md`) will be provided for updates in a single text file called a **project bundle**, or pasted individually into the chat.
The bundle uses a simple text header to separate each file:
`--- FILE: path/to/file.ext ---`

---

## 2. AI Output Format

When the AI provides updated files, it must follow these rules to ensure data integrity.

1.  **Single File or Bundle Per Response**: Only one file or one project bundle will be delivered in a single response.
2.  **Raw Source Text**: The content inside the delivered code block must be the raw source text of the file.
3.  **Code File Delivery**: For code files (e.g., `.py`, `.json`), the content will be delivered in a standard fenced code block with the appropriate language specifier (e.g., ` ```python ... ``` `).
4.  **Bundled File Delivery**: When delivering a bundle, the response will follow a three-part structure:
    * A status update on its own line (e.g., "Here is bundle 1 of 3.").
    * A single fenced code block using the `Plaintext` language specifier (` ```text ... ``` `) containing the bundle content.
    * A confirmation request on its own line after the code block (e.g., "Please confirm when you are ready for the next file/bundle.").

---

## 3. Versioning

1.  When a file is modified, its patch number (the third digit) will be incremented. For example, a change to a `0.28.20-Beta` file will result in version `0.28.21-Beta` for that file.
2.  Document versions will be kept in sync with their corresponding code files.
3.  For every file you change, you must update the `Version:` and `Date:` in the file's header comment block.

---

## 4. File and Checksum Verification

1.  The user's file system uses Windows CRLF (`\r\n`) line endings. The AI's output can use standard LF (`\n`). The AI must be aware of this difference when comparing checksums.
2.  When a checksum verification is requested, the AI will provide a concise report. It will either state that **all checksums agree** or it will provide a list of the **specific files that show a mismatch**. The full table of checksums will not be displayed.
3.  **File State Algorithm:** Before any file modification or checksum comparison, the AI must first establish the definitive "most recent, correct state" of all project files by executing the following algorithm:
    1.  Start with an empty list of definitive files.
    2.  Working backward from the most recent chat message, examine each turn.
    3.  If a turn contains a file or a bundle of files, iterate through them. For each file, if its path is not already in the definitive list, add the file's path and its full content from that turn to the list.
    4.  Continue this process until the initial project and documentation bundles are reached. Add any remaining, not-yet-seen files from those initial bundles to the list.
    The resulting list is the single source of truth for all subsequent operations.

---

## 5. Development Protocol

1.  When creating or modifying any project file (e.g., `.py`, `.json`, `.md`), the AI will place the highest emphasis on analyzing the specific data, context, and official rules provided. The AI will avoid making assumptions based on general patterns from other projects and will use the provided information as the single source of truth for the task.
2.  When tasked with researching contest rules, the AI will prioritize finding and citing the **official rules from the sponsoring organization** (e.g., NCJ for NAQP, CQ Magazine for CQ contests).
3.  Each contest's ruleset is to be treated as entirely unique. Logic, scoring, or multipliers from one contest must **never** be assumed to apply to another unless explicitly stated in the provided rules.

---

## 6. Code Modification Protocol

1.  **Strictly Adhere to Requested Changes**: The AI's primary directive is to implement only the changes explicitly requested by the user. Unsolicited changes, such as updating a plotting library (e.g., from Matplotlib to Plotly) or changing a chart's visual style (e.g., from a pie chart to a donut chart), are strictly forbidden.
2.  **Modify, Don't Regenerate**: The last provided version of a file will be treated as the ground truth. Only specific, requested changes will be applied, preserving all other existing content.
3.  **Propose, Don't Impose**: If the AI identifies a potential improvement, a necessary refactor, or determines that a file requires a major rewrite, it will **not** proceed unilaterally. It will first propose the change and request permission before taking any action.

---

## 7. Canvas Interface Fallback

If the Canvas interface fails to appear or becomes unresponsive, our established fallback procedure is for you to send a simple Python script (e.g., 'Hello, world!') to the Canvas to restore its functionality.

---

## 8. Communication Protocol

All AI communication, including chat responses and generated documentation, will be treated as **technical writing**. When discussing technical concepts, variables, rules, or code, the AI must use the exact, consistent terminology used in the source code or our established protocols. Conversational synonyms and rephrasing of technical terms are to be avoided. Precision and consistency are paramount.

### 8.1. Definition of Prefixes

To ensure absolute clarity in technical discussions, we will adhere to the standard definitions for binary and decimal prefixes:
* **Kilo (k)** = 1,000; **Kibi (Ki)** = 1,024
* **Mega (M)** = 1,000,000; **Mebi (Mi)** = 1,048,576
* **Giga (G)** = 1,000,000,000; **Gibi (Gi)** = 1,073,741,824
* **Terra (T)** = 1,000,000,000,000; **Tebi (Ti)** = 1,099,511,627,776
* **Peta (P)** = 1,000,000,000,000,000; **Pebi (Pi)** = 1,125,899,906,842,624

This rule is strict and will not be altered based on conversational context. If the user is ambiguous, I will ask for clarification.

---

## 9. Explicit State-Transition Protocol for Multi-File Delivery

To ensure reliable execution of multi-step tasks, this protocol makes the user the definitive controller of the sequence. It eliminates reliance on the AI's internal state tracking, which has proven to be a point of failure.

1.  **AI Declaration:** At the beginning of a task, the AI will state its intent and declare the total number of bundles to be sent.
2.  **Bundling Strategy:** The AI will prioritize sending **fewer, larger bundles** to minimize processing overhead on the user's end. It will pack as many files as possible into each one while staying under our established **37 kilobyte** (37,000 byte) limit.
3.  **State-Driven Sequence:** The process then follows a strict, turn-by-turn sequence.
    * **User Prompt:** The user drives the process by sending a prompt that contains the last successfully completed step. The AI will provide the exact text for this prompt in its previous response.
        
            Example: "The last bundle you successfully received was Part 1 of 7. Please send the next bundle."

    * **AI Response:** The AI's response must follow a four-part structure:
        1.  **Acknowledge State:** The AI first confirms its understanding of the current state.
            
                Example: "Acknowledged. The last bundle sent was 1 of 7."

        2.  **Declare State Transition:** The AI then declares the specific action it is about to take.
            
                Example: "I will now prepare and send bundle 2 of 7."

        3.  **Execute Action:** The AI provides the fenced code block containing the bundle.
        4.  **Provide Next Prompt:** After the code block, the AI provides a pre-formatted block containing the exact text for the user's next prompt.

                Example:
                Please copy and paste the following prompt to continue:
                ```
                The last bundle you successfully received was Part 2 of 7. Please send the next bundle.
                ```

4.  **Completion:** After sending the final bundle, the AI will state that the task is complete instead of providing a "next prompt" block.
---

## 10. Context Checkpoint Protocol

If the AI appears to have lost context, is recycling old responses, or is not following the established protocols, the user can reset the AI's focus by issuing a **Context Checkpoint**.

1.  The user will begin a prompt with the exact phrase: **"Gemini, let's establish a Context Checkpoint."**
2.  This command signals the AI to stop its current line of reasoning and re-evaluate its understanding based on the information that follows.
3.  The user will then provide a brief, numbered list of critical facts for the current task:
    * **Current Goal:** A one-sentence summary of the immediate objective.
    * **Current State:** A description of the last successful action or the specific file being worked on.
    * **Key Rule:** The most important rule, bug, or constraint for the current task.
---

## 11. Technical Debt Cleanup Protocol

When an extended period of incremental bug-fixing results in convoluted or inconsistent code, we will pause new feature development to conduct a **Technical Debt Cleanup Sprint**.

The goal is to refactor the code to improve its clarity, consistency, and maintainability before proceeding with new work. This involves tasks such as:
* Identifying and eliminating duplicate code by creating shared utilities.
* Unifying inconsistent logic (e.g., standardizing how all time-series reports handle data).
* Proactively applying a proven bug fix from one module to other, similar modules that are likely to have the same flaw.
---

## 12. Pre-Flight Check Protocol

The term "Unit Test" has a specific meaning in software development that involves automated code execution. Since the AI cannot execute code, we will use the term **Pre-Flight Check** to describe our verification process.

This protocol is a structured, "white-box" mental code review that the AI performs **before** delivering a modified file. Its purpose is to make the development process more rigorous and to catch logic errors before they are delivered to the user.

1.  **Stating the Plan:** Before delivering a file, the AI will state its Pre-Flight Check plan:
    * **Inputs:** The specific conditions being tested (e.g., "I will test this with the KD4D log for the CQ-160 contest").
    * **Expected Outcome:** The specific, verifiable result that proves the change is working correctly (e.g., "The output `_processed.csv` file should now contain a `STPROV_Mult` column, and the `DXCC_Mult` column should be empty for a QSO with W1AW").
2.  **Mental Walkthrough:** The AI will mentally trace the execution path of the specified inputs through the modified code, confirming that the logic produces the expected outcome.
3.  **User Verification:** The user performs the final verification by running the code in the live environment and confirming the result.

---

## 13. File Naming Convention Protocol

All generated report files must adhere to a standardized naming convention to ensure clarity and consistency.

1.  **Template Structure:** Filenames will be constructed from the following components, separated by underscores:
    `<report_id>_<details>_<callsigns>.<ext>`
2.  **Component Definitions:**
    * `<report_id>`: The machine-readable ID of the report (e.g., `qso_rate_plots`, `score_report`).
    * `<details>`: (Optional) Any specific parameters used by the report, such as the metric (`qsos`, `points`) or multiplier type (`dxcc`, `stprov`).
    * `<callsigns>`:
        * **Single Log:** The callsign of the log being analyzed (e.g., `KD4D`).
        * **Pairwise Comparison:** The two callsigns, separated by `_vs_` (e.g., `KD4D_vs_N0NI`).
        * **Multi-Log:** All callsigns, sorted alphabetically and separated by underscores (e.g., `K1LZ_K3LR_KC1XX`).
    * `<ext>`: The file extension (`.txt`, `.png`).
3.  **Examples:**
    * `score_report_KD4D.txt`
    * `missed_multipliers_dxcc_KD4D_vs_N0NI.txt`
    * `cumulative_difference_plots_points_all_K1LZ_vs_K3LR.png`
    * `qso_rate_plots_K1LZ_K3LR_KC1XX.png`

---

## 14. Definitive State Reconciliation Protocol

Certain user commands are designated as **Reconciliation Triggers**. These commands signal that the project's state may be uncertain and require a mandatory, full review of all files before any other action is taken.

1.  **Trigger Commands**: This protocol must be executed whenever the user requests a:
    * `checksum comparison`
    * `consolidated update` or `full project bundle`
    * `diff` on any file

2.  **Mandatory Reconciliation Process**: Upon receiving a trigger command, the AI must perform the following steps in sequence before generating a response:
    1.  **Re-establish Definitive State**: Execute the **File State Algorithm** (as defined in Section 4.3) from scratch, using only the content of the current chat history to build the definitive list of all project files. All previously cached or remembered file states must be discarded.
    2.  **Full File Review**: Once the definitive state is established, the AI must review the content of **every single file** in that state to ensure its response is based on the complete and correct context of the entire project.
    3.  **Proceed with Task**: Only after completing the reconciliation may the AI proceed with the original user request (e.g., performing the checksum comparison or generating the bundle).