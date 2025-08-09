--- FILE: Docs/Working with Gemini.md ---
# Project Workflow Guide

**Version: 0.31.11-Beta**
**Date: 2025-08-09**

---
### --- Revision History ---
## [0.31.11-Beta] - 2025-08-09
### Added
# - Added "Forward-Only Modification" principle to the Code Modification Protocol (Section 6).
## [0.31.10-Beta] - 2025-08-08
### Added
# - Added new Guiding Principles for AI onboarding and state verification.
# - Added Section 15 to formalize the Error Analysis Protocol.
### Changed
# - Streamlined Sections 2 and 9 to remove redundancy and improve clarity.
## [0.31.4-Beta] - 2025-08-08
### Added
# - Added a new Guiding Principle and the "Complex Task Decomposition
#   Protocol" (Section 15) to formalize how complex tasks are broken
#   down to ensure reliability and prevent errors.
### Changed
# - Reviewed and reinforced the principles of error prevention,
#   demonstrated understanding, and improved reliability throughout the
#   document.
## [0.31.3-Beta] - 2025-08-07
### Changed
# - Added a new Guiding Principle and updated the Checksum Protocol to
#   mandate a full, uncached re-computation for every technical request
#   to prevent errors from conversational assumptions.
## [0.31.2-Beta] - 2025-08-07
### Added
# - Added a new Guiding Principle to enforce strict adherence to all
#   technical protocols.
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

1.  **Onboarding Protocol.** The first action for any AI agent upon starting a session is to read this document in its entirety, acknowledge it, and ask any clarifying questions. This ensures full alignment with the established workflow from the outset.

2.  **Decomposition of Complexity.** Complex or multi-faceted requests must be broken down into smaller, sequential steps. If the user provides a task that is not atomic, the AI's first action is to propose a step-by-step plan. This process ensures **demonstrated understanding** of the full scope of the request, improves **reliability** by focusing on one discrete action at a time, and is the primary mechanism for **error prevention**.

3.  **Technical Diligence Over Conversational Assumptions.** Technical tasks, particularly checksum comparisons, are not conversations. Similar-looking prompts do not imply similar answers. Each technical request must be treated as a unique, atomic operation. The AI must execute a full re-computation from the current project state for every request, ignoring any previous results or cached data.

4.  **Protocol Adherence is Paramount.** All protocols must be followed with absolute precision. Failure to do so invalidates the results and undermines the development process. There is no room for deviation unless a deviation is explicitly requested by the AI and authorized by the user.

5.  **Mutual State Verification.** Both the user and the AI can lose context. If an instruction from the user appears to contradict the established state or our immediate goals, the AI should pause and ask for clarification before proceeding.

6.  **Trust the User's Diagnostics.** When the user reports a bug, their description of the symptoms should be treated as the ground truth. The AI's primary task is to find the root cause of those specific, observed symptoms, not to propose alternative theories.

7.  **Debug "A Priori" When Stuck.** If an initial bug fix fails, do not simply patch the failed fix. Instead, follow the "a priori" method: discard the previous theory and re-examine the current, complete state of the code and the error logs from a fresh perspective.

8.  **Prefer Logic in Code, Not Data.** The project's design philosophy is to keep the `.json` definition files as simple, declarative maps. All complex, conditional, or contest-specific logic should be implemented in dedicated Python modules.

9.  **Assume Bugs are Systemic.** When a bug is identified in one module, the default assumption is that the same flaw exists in all other similar modules. The AI must perform a global search for that specific bug pattern and fix all instances at once.

10. **No Unrequested Changes.** The AI will only implement changes explicitly requested by the user. All suggestions for refactoring, library changes, or stylistic updates must be proposed and approved by the user before implementation.
---

## 1. Project File Input

All project source files and documentation will be provided for updates in a single text file called a **project bundle**, or pasted individually into the chat. The bundle uses a simple text header to separate each file:
`--- FILE: path/to/file.ext ---`

---

## 2. AI Output Format

When the AI provides updated files, it must follow these rules to ensure data integrity.

1.  **Single File or Bundle Per Response**: Only one file or one project bundle will be delivered in a single response.
2.  **Raw Source Text**: The content inside the delivered code block must be the raw source text of the file.
3.  **Code File Delivery**: For code files (e.g., `.py`, `.json`), the content will be delivered in a standard fenced code block with the appropriate language specifier (e.g., ` ```python ... ``` `).
4.  **Bundled File Delivery**: Bundles containing documentation or multiple files must be delivered in a single fenced code block using the `Plaintext` language specifier (` ```text ... ``` `). For the conversational workflow of delivering bundles, see **Protocol 9**.

---

## 3. Versioning

1.  When a file is modified, its patch number (the third digit) will be incremented.
2.  Document versions will be kept in sync with their corresponding code files.
3.  For every file changed, the AI must update the `Version:` and `Date:` in the file's header.

---

## 4. File and Checksum Verification

1.  **Line Endings:** The user's file system uses Windows CRLF (`\r\n`). The AI must correctly handle this conversion when calculating checksums.
2.  **Concise Reporting:** The AI will either state that **all checksums agree** or will list the **specific files that show a mismatch**.
3.  **File State Algorithm:** Before any modification, the AI must establish the definitive "most recent, correct state" of all project files by working backward through the chat history.
4.  **Mandatory Re-computation Protocol:** Every request for a checksum comparison is a **cache-invalidation event**. The AI must:
    * Discard all previously calculated checksums.
    * Re-establish the definitive state of all files from scratch.
    * Re-compute the SHA-256 hash for every single file in the current state.
    * Perform a literal, digit-for-digit comparison against only the checksum values provided in the user's current prompt.

---

## 5. Development Protocol

1.  The AI will place the highest emphasis on analyzing the specific data, context, and official rules provided, using them as the single source of truth.
2.  When researching contest rules, the AI will prioritize finding and citing the **official rules from the sponsoring organization**.
3.  Each contest's ruleset is to be treated as entirely unique. Logic from one contest must **never** be assumed to apply to another.

---

## 6. Code Modification Protocol

1.  **Strictly Adhere to Requested Changes**: The AI will implement only the changes explicitly requested by the user.
2.  **Modify, Don't Regenerate**: The last provided version of a file is the ground truth. Only requested changes will be applied.
3.  **Propose, Don't Impose**: If the AI identifies a potential improvement, it will first propose the change and request permission before taking any action.
4.  **Forward-Only Modification**: The most recently provided version of a file is the definitive state. All subsequent changes must be applied as modifications to this version. Do not revert to a prior version of a file unless explicitly instructed to do so. This ensures a sequential and predictable workflow.

---

## 7. Canvas Interface Fallback

If the Canvas interface fails, the AI will send a simple Python script to restore its functionality.

---

## 8. Communication Protocol

All AI communication will be treated as **technical writing**. The AI must use the exact, consistent terminology from the source code and protocols.

### 8.1. Definition of Prefixes

The standard definitions for binary and decimal prefixes will be strictly followed.

* **Kilo (k)** = 1,000; **Kibi (Ki)** = 1,024
* **Mega (M)** = 1,000,000; **Mebi (Mi)** = 1,048,576
* etc.

---

## 9. Explicit State-Transition Protocol for Multi-File Delivery

This protocol makes the user the definitive controller of the delivery sequence.

1.  **AI Declaration:** The AI will state its intent and declare the total number of bundles to be sent.
2.  **Bundling Strategy:** The AI will prioritize sending **fewer, larger bundles** under the **37 kilobyte** limit.
3.  **State-Driven Sequence:** The process follows a strict, turn-by-turn workflow. The AI's response must follow a four-part structure:
    1.  **Acknowledge State:** Confirm understanding of the last completed step.
    2.  **Declare State Transition:** State the specific action it is about to take.
    3.  **Execute Action:** Provide the file bundle in the format defined in **Protocol 2.4**.
    4.  **Provide Next Prompt:** Provide the exact text for the user's next prompt.
4.  **Completion:** After the final bundle, the AI will state that the task is complete.

---

## 10. Context Checkpoint Protocol

If the AI appears to have lost context, the user can reset the AI's focus by issuing a **Context Checkpoint**.

1.  The user begins with the exact phrase: **"Gemini, let's establish a Context Checkpoint."**
2.  The user provides a brief, numbered list of critical facts (Current Goal, Current State, Key Rule).

---

## 11. Technical Debt Cleanup Protocol

When code becomes convoluted, a **Technical Debt Cleanup Sprint** will be conducted to refactor the code for clarity, consistency, and maintainability.

---

## 12. Pre-Flight Check Protocol

The AI will perform a "white-box" mental code review **before** delivering a modified file.

1.  **Stating the Plan:** The AI will state its Pre-Flight Check plan, including the **Inputs** and the **Expected Outcome**.
2.  **Mental Walkthrough:** The AI will mentally trace the execution path to confirm the logic produces the expected outcome.
3.  **User Verification:** The user performs the final verification by running the code.

---

## 13. File Naming Convention Protocol

All generated report files must adhere to the standardized naming convention: `<report_id>_<details>_<callsigns>.<ext>`.

---

## 14. Definitive State Reconciliation Protocol

**Reconciliation Triggers** (e.g., `checksum comparison`, `full project bundle`) require a mandatory, full review of all files before any other action is taken. The AI must:
1.  **Re-establish Definitive State** by executing the **File State Algorithm (4.3)**.
2.  **Review Every File** in the definitive state.
3.  **Proceed with the Task**.

---

## 15. Error Analysis Protocol

When an error in the AI's process is identified, the AI must provide a clear and concise analysis.

1.  **Acknowledge the Error:** State clearly that a mistake was made.
2.  **Identify the Root Cause:** Explain the specific flaw in the internal process or logic that led to the error (e.g., "improper caching," "failure to re-evaluate state").
3.  **Propose a Corrective Action:** Describe the specific, procedural change that will be implemented to prevent the error from recurring.