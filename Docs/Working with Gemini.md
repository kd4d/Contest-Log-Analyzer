--- FILE: Docs/Working with Gemini.md ---
# Project Workflow Guide

**Version: 0.30.30-Beta**
**Date: 2025-08-07**

---
### --- Revision History ---
## [0.30.30-Beta] - 2025-08-07
# - Synchronized documentation with the current code base and our
#   established protocols.
## [0.30.11-Beta] - 2025-08-05
# - Updated protocol to use 'Plaintext' as the code block specifier for
#   all documentation and bundle files, per user feedback.
# - Clarified the multi-part delivery protocol to distinguish between
#   sending a sequence of single files versus a sequence of bundles.
## [0.30.10-Beta] - 2025-08-05
# - Added Section 4.3 to formally define the "File State Algorithm" for
#   determining the definitive version of all project files.
# - Amended Section 8 to clarify that all AI communication is to be
#   treated as "technical writing," prioritizing precision over conversational style.
---

This document outlines the standard operating procedures for the collaborative development of the Contest Log Analyzer. **The primary audience for this document is the Gemini AI agent.**

**Its core purpose is to serve as a persistent set of rules and context.** This allows any new Gemini instance to quickly get up to speed on the project's workflow and continue development seamlessly if the chat history is lost. Adhering to this workflow ensures consistency and prevents data loss.
---

### Guiding Principles

1.  **Trust the User's Diagnostics.** When the user reports a bug, their description of the symptoms (e.g., "the multipliers are too high," "the report is all zeros") should be treated as the ground truth. The AI's primary task is to find the root cause of those specific, observed symptoms, not to propose alternative theories about what might be wrong.

2.  **Debug "A Priori" When Stuck.** If an initial bug fix fails, do not simply try to patch the failed fix. Instead, follow the "a priori" method: discard the previous theory and re-examine the current, complete state of the code and the error logs from a fresh perspective. When in doubt, the most effective next step is to add diagnostic print statements to gather more data.

3.  **Prefer Logic in Code, Not Data.** The project's design philosophy is to keep the `.json` definition files as simple, declarative maps. All complex, conditional, or contest-specific logic should be implemented in dedicated Python modules (e.g., `cq_160_multiplier_resolver.py`). This makes the system more robust and easier to maintain.
---

## 1. Project File Input

All project source files (`.py`, `.json`) and documentation files (`.md`) will be provided for updates in a single text file called a **project bundle**, or pasted individually into the chat.
The bundle uses a simple text header to separate each file:
`--- FILE: path/to/file.ext ---`

---

## 2. AI Output Format

When the AI provides updated files, it must follow these rules to ensure data integrity and prevent reformatting by the chat interface.

1.  **Single File or Bundle Per Response**: Only one file or one project bundle will be delivered in a single response.
2.  **Raw Source Text**: The content inside the delivered code block must be the raw source text of the file.
3.  **Code File Delivery**: For code files (e.g., `.py`, `.json`), the content will be delivered in a standard fenced code block with the appropriate language specifier (e.g., ` ```python ... ``` `).
4.  **Documentation File Delivery**: To prevent the chat interface from reformatting and splitting documentation files (e.g., `.md`) or bundles, a specific protocol is required:
    * The AI's **entire response** will consist of a single fenced code block using the `Plaintext` language specifier (e.g., ` ```text ... ``` `). No conversational text will precede or follow this block.
    * Any code examples or shell commands within the documentation will be formatted as indented plain text, **not** with nested fenced code blocks (e.g., ` ```bash`). This is critical to ensure the file is delivered as one unbroken block.

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

1.  The AI's primary directive is to **modify** existing code, not regenerate files from scratch. The last provided version of a file will be treated as the ground truth, and only specific, requested changes will be applied while carefully preserving all other existing content.
2.  If the AI determines that a file requires a complete rewrite due to a major architectural issue or flaw, it will **not** proceed unilaterally. It will first propose the rewrite and request permission to proceed.

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

## 9. Protocol for Multi-File and Bundled Delivery

When a single logical task requires modifying multiple files, this protocol ensures changes are delivered sequentially and clearly.

1.  **Declaration:** At the beginning of the chat, the AI will first state its intent to modify multiple items, list all the files that will be affected, and state the **total number of files or bundles** that will be sent (e.g., "This is file 1 of 3" or "This is bundle 1 of 2").
2.  **Bundling Strategy:** The AI will prioritize sending **fewer, larger bundles**, packing as many files as possible into each one while staying under our established **37 kilobyte** (37,000 byte) limit.
3.  **Sequential Delivery:** At the beginning of each subsequent response, the AI will provide a status update (e.g., "This is file 2 of 3."). The AI will then provide the file or bundle. The response will end with a clear statement, such as: "Please confirm when you are ready for the next file/bundle."
4.  **Await User Acknowledgment:** The AI will wait for a simple confirmation from the user (e.g., 'OK', 'Ready', 'next') before sending the next file or bundle.
5.  **Iteration:** The AI will then provide the next item in the sequence, repeating this turn-by-turn process until all declared files have been delivered.
6.  **AI Completion Signal:** After sending the final file or bundle, the AI will state that the multi-file update is complete.
7.  **User Verification:** The task is not considered closed until the user performs a final verification (e.g., running a test or a checksum comparison) and confirms success.
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