# Project Workflow Guide

**Version: 0.55.13-Beta**
**Date: 2025-08-31**

---
### --- Revision History ---
## [0.55.13-Beta] - 2025-08-31
### Changed
# - Updated Protocol 2.9.1 to require a final user acknowledgment
#   after a documentation file (.md) has been delivered.
## [0.55.7-Beta] - 2025-08-30
### Added
# - Added Principle 11 ("The Log is the Ground Truth") to clarify how to
#   [cite_start]handle factually incorrect data within a log file. [cite: 1376]
# - Added Protocol 3.7 (Temporary Column Preservation Protocol) to prevent
#   [cite_start]the accidental deletion of intermediate data columns during processing. [cite: 1377]
# - Added Protocol 5.6 (Custom ADIF Exporter Protocol) to formalize the
#   [cite_start]new, pluggable architecture for contest-specific ADIF generation. [cite: 1378]
### Changed
# [cite_start]- Renumbered subsequent principles in Part I. [cite: 1379]
## [0.52.22-Beta] - 2025-08-27
### Changed
# - Revised Protocol 5.4 to recommend `prettytable` for complex,
#   multi-table reports and designate `tabulate` for simpler,
#   [cite_start]single-table use cases. [cite: 1379]
## [0.52.21-Beta] - 2025-08-27
### Changed
# - Strengthened Principle 9 (Surgical Modification) to explicitly
#   [cite_start]forbid unauthorized stylistic refactoring. [cite: 1380]
### Added
# - Added Protocol 7.5 (Tool Suitability Re-evaluation Protocol) to
#   [cite_start]formalize the process of handling unsuitable third-party tools. [cite: 1381]
## [0.52.20-Beta] - 2025-08-26
### Added
# - Added a mandatory "Affected Modules Checklist" to Protocol 2.5 to
#   [cite_start]make Principle 7 (Assume Bugs are Systemic) more robust. [cite: 1382]
## [0.49.2-Beta] - 2025-08-25
### Added
# - Added Protocol 7.4 (Prototype Script Development Protocol) to formalize
#   [cite_start]the development workflow for prototype scripts. [cite: 1383]
### Changed
# - Clarified Protocol 1.7 to define the special status of the
#   [cite_start]`test_code/` directory. [cite: 1384]
## [0.49.1-Beta] - 2025-08-25
### Added
# - Added Protocol 2.9.1 (Task Type Verification) to clarify when it is
#   appropriate to propose a verification command, preventing errors when
#   [cite_start]a task modifies a documentation file. [cite: 1385]
## [0.49.0-Beta] - 2025-08-25
### Added
# - Added Protocol 2.8.1 (Post-Execution Refinement Protocol) to clarify
#   [cite_start]the workflow for handling incomplete fixes. [cite: 1386]
# - Added Protocol 5.5 (Component Modernization Protocol) to formalize
#   [cite_start]the process of upgrading and deprecating legacy components. [cite: 1387]
# - Added a mandatory "Request Diagnostic Output" step to Protocol 6.3
#   [cite_start](Error Analysis Protocol) to improve diagnostic efficiency. [cite: 1388]
### Changed
# [cite_start]- Renumbered subsequent protocols in the Task Execution Workflow. [cite: 1389]
## [0.48.2-Beta] - 2025-08-25
### Added
# - Added Protocol 5.4 to formalize the use of the `tabulate` library
#   [cite_start]for generating all text-based tables. [cite: 1390]
### Changed
# - Clarified Protocol 3.2.4 to explain the reasoning behind the
#   [cite_start]__CODE_BLOCK__ substitution for markdown file delivery. [cite: 1391]
## [0.48.1-Beta] - 2025-08-24
### Changed
# - Amended Protocol 2.1 (Task Initiation) to require a mandatory check
#   [cite_start]for an established session version number before proceeding. [cite: 1392]
# - Clarified Protocol 3.4.3 (Update Procedure) to explicitly forbid
#   [cite_start]unauthorized changes to major or minor version numbers. [cite: 1393]
## [0.48.0-Beta] - 2025-08-24
### Changed
# - Merged the Pre-Flight Check (2.6) into the Implementation Plan
#   [cite_start]protocol (2.5) to reflect the new, more detailed planning process. [cite: 1394]
# [cite_start]- Renumbered subsequent protocols in the Task Execution Workflow. [cite: 1395]
## [0.47.6-Beta] - 2025-08-23
### Added
# - Added clarification to Protocol 1.5 that version numbers are only
#   [cite_start]updated if a file's content is modified. [cite: 1396]
## [0.44.0-Beta] - 2025-08-23
### Changed
# - Modified Protocol 3.2.4 to require substituting embedded code
#   [cite_start]fences (```) with __CODE_BLOCK__ for markdown file delivery. [cite: 1397]
## [0.43.0-Beta] - 2025-08-23
### Added
# - Added Protocol 6.6 (Self-Correction on Contradiction) to mandate a
#   full stop and re-evaluation upon detection of logically impossible
#   [cite_start]or contradictory analytical results. [cite: 1398]
# - Added Protocol 6.7 (Simplified Data Verification) to formalize the
#   [cite_start]use of user-provided, simplified data files for debugging. [cite: 1399]
### Changed
# - Amended Principle 5 (Technical Diligence) to explicitly require
#   [cite_start]halting when a tool produces inconsistent results over multiple attempts. [cite: 1400]
# - Clarified Protocol 6.3 (Error Analysis Protocol) to emphasize that
#   a failure to provide a correct analysis after a user's correction
#   [cite_start]constitutes a new, more severe error. [cite: 1401]
## [0.42.0-Beta] - 2025-08-20
### Added
# - Added Protocol 2.3 (Visual Prototype Protocol) to formalize the use
#   [cite_start]of prototype scripts for complex visual changes. [cite: 1402]
### Changed
# - Renumbered subsequent protocols in the Task Execution Workflow and
#   [cite_start]updated internal cross-references. [cite: 1403]
## [0.38.0-Beta] - 2025-08-19
### Added
# - Added Protocol 2.3 (Baseline Consistency Check) to require plan
#   [cite_start]validation against the definitive state before the plan is proposed. [cite: 1404]
### Changed
# [cite_start]- Renumbered subsequent protocols in the Task Execution Workflow. [cite: 1405]
# [cite_start]- Updated internal cross-references to match the new numbering. [cite: 1406]
## [0.37.1-Beta] - 2025-08-18
### Changed
# - Refined the Markdown File Delivery Protocol (3.2.4) to require
#   enclosing the entire file content in a plaintext code block for
#   [cite_start]easier copying. [cite: 1407]
## [0.37.0-Beta] - 2025-08-18
### Added
# - Added Principle 13 to formalize the process of classifying data
#   [cite_start]conflicts as either data errors or complex rule requirements. [cite: 1408]
# - Added Protocol 2.8 to the Task Execution Workflow, requiring the AI
#   [cite_start]to propose a verification command after a task is complete. [cite: 1409]
## [0.36.12-Beta] - 2025-08-17
### Changed
# - Integrated clarifications from user feedback into Protocol 1.2,
#   [cite_start]Principle 9, and Protocol 3.4.3 to make the document self-contained. [cite: 1410]
### Added
# - Added Protocol 6.5 (Bundle Integrity Check Protocol) to define a
#   [cite_start]procedure for handling logical anomalies within initialization bundles. [cite: 1411]
## [0.36.11-Beta] - 2025-08-16
### Added
# - Added Protocol 1.7 (Project Structure Onboarding) to provide bootstrap
#   [cite_start]architectural context after an initialization. [cite: 1412]
# - Added Protocol 6.4 (Corrupted User Input Protocol) to define a
#   [cite_start]formal procedure for handling malformed user files. [cite: 1413]
## [0.36.10-Beta] - 2025-08-16
### Added
# - Added the new, top-priority Principle 1 for Context Integrity, which
#   [cite_start]mandates a full state reset upon detection of context loss. [cite: 1414]
### Changed
# [cite_start]- Renumbered all subsequent principles accordingly. [cite: 1415]
## [0.36.9-Beta] - 2025-08-15
### Added
# - Added rule 3.2.4 to mandate the substitution of markdown code fences
#   with __CODE_BLOCK__ for proper web interface rendering.
## [0.36.4-Beta] - 2025-08-15
### Changed
# - Clarified Principle 8 (Surgical Modification) to explicitly require
#   [cite_start]the preservation of revision histories. [cite: 1416]
### Added
# - Added Protocol 1.6 (Session Versioning Protocol) to establish the
#   [cite_start]current version series at the start of a task. [cite: 1417]
## [0.36.3-Beta] - 2025-08-15
### Changed
# [cite_start]- Merged missing protocols from v0.36.0-Beta to create a complete document. [cite: 1418]
# [cite_start]- Synthesized a new, authoritative Versioning Protocol based on user clarification. [cite: 1419]
# [cite_start]- Reorganized the document to separate workflow protocols from software design patterns. [cite: 1420]
## [0.36.2-Beta] - 2025-08-15
### Changed
# - Overhauled the Task Execution and File Delivery protocols to formalize
#   [cite_start]the new, more robust, state-machine workflow with per-file acknowledgments. [cite: 1421]
## [0.36.1-Beta] - 2025-08-15
### Changed
# - Amended Protocol 2.2 to require the file's baseline version
#   [cite_start]number in all implementation plans. [cite: 1422]
## [0.36.0-Beta] - 2025-08-15
### Changed
# - Replaced the "Atomic State Checkpoint Protocol" (1.2) with the new
#   "Definitive State Reconciliation Protocol" which uses the last
#   [cite_start]Definitive State Initialization as its baseline. [cite: 1423]
# - Amended Protocol 1.5 to add an explicit step for handling
#   [cite_start]documents that require no changes. [cite: 1424]
---

[cite_start]This document outlines the standard operating procedures for the collaborative development of the Contest Log Analyzer. [cite: 1425]
[cite_start]**The primary audience for this document is the Gemini AI agent.** [cite: 1426]

[cite_start]**Its core purpose is to serve as a persistent set of rules and context.** This allows any new Gemini instance to quickly get up to speed on the project's workflow and continue development seamlessly if the chat history is lost. [cite: 1426] [cite_start]Adhering to this workflow ensures consistency and prevents data loss. [cite: 1427]
---
## Part I: Core Principles

[cite_start]These are the foundational rules that govern all interactions and analyses. [cite: 1428]
1.  [cite_start]**Context Integrity is Absolute.** The definitive project state is established by the baseline `*_bundle.txt` files and evolves with every acknowledged file change. [cite: 1429] [cite_start]Maintaining this evolving state requires both the baseline bundles and the subsequent chat history. [cite: 1430] [cite_start]If I detect that the baseline `*_bundle.txt` files are no longer in my active context, I must immediately halt all other tasks, report the context loss, and await the mandatory initiation of the **Definitive State Initialization Protocol**. [cite: 1431]
2.  [cite_start]**Protocol Adherence is Paramount.** All protocols must be followed with absolute precision. [cite: 1432] [cite_start]Failure to do so invalidates the results and undermines the development process. [cite: 1433] [cite_start]There is no room for deviation unless a deviation is explicitly requested by the AI and authorized by the user. [cite: 1434]
3.  [cite_start]**Trust the User's Diagnostics.** When the user reports a bug or a discrepancy, their description of the symptoms and their corrections should be treated as the ground truth. [cite: 1435] [cite_start]The AI's primary task is to find the root cause of those specific, observed symptoms, not to propose alternative theories. [cite: 1436]
4.  [cite_start]**No Unrequested Changes.** The AI will only implement changes explicitly requested by the user. [cite: 1437] [cite_start]All suggestions for refactoring, library changes, or stylistic updates must be proposed and approved by the user before implementation. [cite: 1438]
5.  [cite_start]**Technical Diligence Over Conversational Assumptions.** Technical tasks are not conversations. [cite: 1439] [cite_start]Similar-looking prompts do not imply similar answers. [cite: 1439] [cite_start]Each technical request must be treated as a unique, atomic operation. [cite: 1440] [cite_start]The AI must execute a full re-computation from the current project state for every request, ignoring any previous results or cached data. [cite: 1441] [cite_start]**If a tool produces inconsistent or contradictory results over multiple attempts, this must be treated as a critical failure of the tool itself and be reported immediately.** [cite: 1442]
6.  [cite_start]**Prefer Logic in Code, Not Data.** The project's design philosophy is to keep the `.json` definition files as simple, declarative maps. [cite: 1442] [cite_start]All complex, conditional, or contest-specific logic should be implemented in dedicated Python modules. [cite: 1443]
7.  [cite_start]**Assume Bugs are Systemic.** When a bug is identified in one module, the default assumption is that the same flaw exists in all other similar modules. [cite: 1444] [cite_start]The AI must perform a global search for that specific bug pattern and fix all instances at once. [cite: 1445]
8.  [cite_start]**Reports Must Be Non-Destructive.** Specialist report scripts must **never** modify the original `ContestLog` objects they receive. [cite: 1446] [cite_start]All data filtering or manipulation must be done on a temporary **copy** of the DataFrame. [cite: 1447]
9.  [cite_start]**Principle of Surgical Modification.** All file modifications must be treated as surgical operations. [cite: 1448] [cite_start]The AI must start with the last known-good version of a file as the ground truth (established by the **Definitive State Reconciliation Protocol**) and apply only the minimal, approved change. [cite: 1449] [cite_start]Full file regeneration from an internal model is strictly forbidden to prevent regressions. [cite: 1450] [cite_start]**This includes the verbatim preservation of all unchanged sections, especially headers and the complete, existing revision history.** [cite: 1451] [cite_start]This principle explicitly forbids stylistic refactoring (e.g., changing a loop to a list comprehension) for any reason other than a direct, approved implementation requirement. [cite: 1451] [cite_start]Unauthorized 'simplifications' are a common source of regressions and are strictly prohibited. [cite: 1452]
10. [cite_start]**Primacy of Official Rules.** The AI will place the highest emphasis on analyzing the specific data, context, and official rules provided, using them as the single source of truth. [cite: 1453]
11. [cite_start]**The Log is the Ground Truth.** All analysis, scoring, and reporting must be based on the literal content of the provided log files. [cite: 1454] [cite_start]The analyzer's function is not to correct potentially erroneous data (e.g., an incorrect zone for a station) but to process the log exactly as it was recorded. [cite: 1455] [cite_start]Discrepancies arising from incorrect data are a matter for the user to investigate, not for the AI to silently correct. [cite: 1456]
12. [cite_start]**Citation of Official Rules.** When researching contest rules, the AI will prioritize finding and citing the **official rules from the sponsoring organization**. [cite: 1457]
13. [cite_start]**Uniqueness of Contest Logic.** Each contest's ruleset is to be treated as entirely unique. [cite: 1458] [cite_start]Logic from one contest must **never** be assumed to apply to another. [cite: 1459]
14. [cite_start]**Classify Ambiguity Before Action.** When the AI discovers a conflict between the data (e.g., in a `.dat` or `.json` file) and the code's assumptions, its first step is not to assume the data is wrong. [cite: 1460] It must present the conflict to the user and ask for a ruling:
    * [cite_start]Is this a **Data Integrity Error** that should be corrected in the data file? [cite: 1461]
    * [cite_start]Is this a **Complex Rule Requirement** that must be handled by enhancing the code logic? [cite: 1462]
[cite_start]The user's classification will guide the subsequent analysis and implementation plan. [cite: 1463]
---
## Part II: Standard Operating Protocols

[cite_start]These are the step-by-step procedures for common, day-to-day development tasks. [cite: 1464]

### 1. Session Management

1.1. [cite_start]**Onboarding Protocol.** The first action for any AI agent upon starting a session is to read this document in its entirety, acknowledge it, and ask any clarifying questions. [cite: 1465]
1.2. **Definitive State Reconciliation Protocol.**
    1.  [cite_start]**Establish Baseline**: The definitive state is established by first locating the most recent **Definitive State Initialization Protocol** in the chat history. [cite: 1466] [cite_start]The files from this initialization serve as the absolute baseline. [cite: 1467]
    2.  [cite_start]**Scan Forward for Updates**: After establishing the baseline, the AI will scan the chat history *forward* from that point to the present. [cite: 1468]
    3.  [cite_start]**Identify Latest Valid Version**: The AI will identify the **latest** version of each file that was part of a successfully completed and mutually acknowledged transaction (i.e., file delivery, AI confirmation, and user acknowledgment). [cite: 1469] [cite_start]This version supersedes the baseline version. [cite: 1470]
    4.  [cite_start]**Handle Ambiguity**: If any file transaction is found that was initiated but not explicitly acknowledged by the user, the AI must halt reconciliation, report the ambiguous file, and await user clarification. [cite: 1470]
1.3. [cite_start]**Context Checkpoint Protocol.** If the AI appears to have lost context, the user can issue a **Context Checkpoint**. [cite: 1471]
    1.  [cite_start]The user begins with the exact phrase: **"Gemini, let's establish a Context Checkpoint."** [cite: 1472]
    2.  [cite_start]The user provides a brief, numbered list of critical facts. [cite: 1472]
1.4. [cite_start]**Definitive State Initialization Protocol.** This protocol serves as a "hard reset" of the project state. [cite: 1473]
    1.  [cite_start]**Initiation:** The user or AI requests a "Definitive State Initialization." [cite: 1474]
    2.  [cite_start]**Agreement:** The other party agrees to proceed. [cite: 1475]
    3.  [cite_start]**File Upload:** The user creates and uploads new, complete `project_bundle.txt`, `documentation_bundle.txt`, and `data_bundle.txt` files. [cite: 1475]
    4.  [cite_start]**State Purge:** The AI discards its current understanding of the project state. [cite: 1476]
    5.  [cite_start]**Re-Initialization:** The AI establishes a new definitive state based *only* on the new bundles. [cite: 1477]
    6.  [cite_start]**Verification and Acknowledgment:** The AI acknowledges the new state and provides a complete list of all files extracted from the bundles. [cite: 1478]
1.5. [cite_start]**Document Review and Synchronization Protocol.** This protocol is used to methodically review and update all project documentation (`.md` files) to ensure it remains synchronized with the code baseline. [cite: 1479]
    1.  [cite_start]**Initiate Protocol and List Documents:** The AI will state that the protocol is beginning and will provide a complete list of all documents to be reviewed (`Readme.md` and all `.md` files in the `Docs` directory). [cite: 1480]
    2.  **Begin Sequential Review:** The AI will then loop through the list, processing one document at a time using the following steps:
        * [cite_start]**Step A: Identify and Request.** State which document is next and ask for permission to proceed. [cite: 1481]
        * [cite_start]**Step B: Analyze.** Upon approval, perform a full "a priori" review of the document against the current code baseline and provide an analysis of any discrepancies. [cite: 1482]
        * [cite_start]**Step C (Changes Needed): Propose Plan.** If discrepancies are found, ask if the user wants an implementation plan to update the document. [cite: 1483]
        * [cite_start]**Step D: Provide Plan.** Upon approval, provide a detailed, surgical implementation plan for the necessary changes. [cite: 1484]
        * [cite_start]**Step E: Request to Proceed.** Ask for explicit permission to generate the updated document. [cite: 1485]
        * [cite_start]**Step F: Deliver Update.** Upon approval, perform a **Pre-Flight Check**, explicitly state that the check is complete, and then deliver the updated document. [cite: 1486]
        * [cite_start]**Step G (No Changes Needed):** If the analysis in Step B finds no discrepancies, the AI will state that the document is already synchronized and ask for the user's confirmation to proceed to the next document. [cite: 1487]
    3.  [cite_start]**Completion:** After the final document has been processed, the AI will state that the protocol is complete. [cite: 1488]
    4.  [cite_start]**Version Update on Modification Only Clarification**: A file's version number and revision history will only be updated if its content requires changes to be synchronized with the project baseline. [cite: 1489] [cite_start]Documents that are found to be already synchronized during the review will not have their version numbers changed. [cite: 1490]

1.6. [cite_start]**Session Versioning Protocol.** At the start of a new development task, the user will state the current version series (e.g., 'We are working on Version 0.36.x-Beta'). [cite: 1491] [cite_start]All subsequent file modifications for this and related tasks must use this version series, incrementing the patch number as needed. [cite: 1492]
1.7. [cite_start]**Project Structure Onboarding.** After a state initialization, the AI will confirm its understanding of the high-level project architecture. [cite: 1493]
    * [cite_start]`contest_tools/`: The core application library. [cite: 1494]
    * [cite_start]`contest_tools/reports/`: The "plug-in" directory for all report modules. [cite: 1494]
    * [cite_start]`contest_tools/contest_definitions/`: Data-driven JSON definitions for each contest. [cite: 1495]
    * [cite_start]`Docs/`: All user and developer documentation. [cite: 1495]
    * [cite_start]`test_code/`: Utility and prototype scripts not part of the main application. [cite: 1496] [cite_start]These scripts are not held to the same change control and documentation standards (e.g., a revision history is not required). [cite: 1497]
    * [cite_start]`data/`: Required data files (e.g., `cty.dat`). [cite: 1498]
### 2. Task Execution Workflow
[cite_start]This workflow is a formal state machine that governs all development tasks, from initial request to final completion. [cite: 1498]
2.1. [cite_start]**Task Initiation**: The user provides a problem, feature request, or document update and requests an analysis. [cite: 1499] [cite_start]Before proceeding, the AI must verify that a session version series (as defined in Protocol 1.6) has been established. [cite: 1500] [cite_start]If it has not, the AI must ask for it before providing any analysis. [cite: 1501]
2.2. **Analysis and Discussion**: The AI provides an initial analysis. [cite_start]The user and AI may discuss the analysis to refine the understanding of the problem. [cite: 1502]
2.3. [cite_start]**Visual Prototype Protocol.** This protocol is used to resolve ambiguity in tasks involving complex visual layouts or new, hard-to-describe logic before a full implementation is planned. [cite: 1503]
    1.  [cite_start]**Initiation:** The AI proposes or the user requests a prototype to clarify a concept. [cite: 1504]
    2.  [cite_start]**Agreement:** Both parties agree to create the prototype. [cite: 1505]
    3.  [cite_start]**Prototype Delivery:** The AI delivers a standalone, self-contained script. [cite: 1506] [cite_start]The script must use simple, hardcoded data and focus only on demonstrating the specific concept in question. [cite: 1507]
    4.  [cite_start]**Prototype Usability Clause:** For visual prototypes using Matplotlib, the script must save the output to a file and then immediately display the chart on-screen using `plt.show()` for ease of verification. [cite: 1508]
    5.  [cite_start]**Review and Iteration:** The user reviews the prototype's output and provides feedback. [cite: 1509] [cite_start]This step can be repeated until the prototype is correct. [cite: 1510]
    6.  [cite_start]**Approval:** The user gives explicit approval of the final prototype. [cite: 1511] [cite_start]This approval serves as the visual and logical ground truth for the subsequent implementation plan. [cite: 1512]
2.4. [cite_start]**Baseline Consistency Check.** Before presenting an implementation plan, the AI must perform and explicitly state the completion of a "Baseline Consistency Check." [cite: 1513] [cite_start]This check verifies that all proposed actions (e.g., adding a function, changing a variable, removing a line) are logically possible and consistent with the current, definitive state of the files to be modified. [cite: 1514]
2.5. **Implementation Plan**: The user requests an implementation plan. The AI's response must be a comprehensive document containing the following sections for each file to be modified:
    1.  [cite_start]**File Identification**: The full path to the file and its specific baseline version number. [cite: 1515]
    2.  [cite_start]**Surgical Changes**: A detailed, line-by-line description of all proposed additions, modifications, and deletions. [cite: 1516]
    3.  [cite_start]**Affected Modules Checklist**: A list of all other modules that follow a similar architectural pattern to the file being modified (e.g., all custom parsers, all score reports). [cite: 1517] [cite_start]The AI must confirm that these modules have been checked and will be updated if necessary to keep them consistent with the proposed change. [cite: 1518] [cite_start]This makes the application of Principle 7 (Assume Bugs are Systemic) explicit. [cite: 1519]
    4.  **Pre-Flight Check**:
        * [cite_start]**Inputs**: A restatement of the file path and baseline version. [cite: 1520]
        * [cite_start]**Expected Outcome**: A clear statement describing the desired state or behavior after the changes are applied. [cite: 1521]
        * [cite_start]**Mental Walkthrough Confirmation**: A statement affirming that a mental walkthrough of the logic will be performed before generating the file. [cite: 1522]
        * [cite_start]**State Confirmation Procedure**: An affirmation that the mandatory confirmation prompt (as defined in Protocol 4.4) will be included with the file delivery. [cite: 1523]
2.6. [cite_start]**Plan Refinement**: The user reviews the plan and may request changes or refinements. [cite: 1524] [cite_start]The AI provides a revised plan, repeating this step as necessary. [cite: 1525]
2.7. [cite_start]**Approval**: The user provides explicit approval of the final implementation plan (e.g., "Approved"). [cite: 1526] [cite_start]Instructions, clarifications, or new requirements provided after a plan has been proposed do not constitute approval; [cite: 1527] [cite_start]they will be treated as requests for plan refinement under Protocol 2.6. [cite: 1528]
2.8. [cite_start]**Execution**: Upon approval, the AI will proceed with the **Confirmed File Delivery Protocol (4.4)**. [cite: 1529]
2.8.1. [cite_start]**Post-Execution Refinement Protocol.** If a user acknowledges a file delivery but subsequently reports that the fix is incomplete or incorrect, the task is not considered complete. [cite: 1530] [cite_start]The workflow immediately returns to **Protocol 2.2 (Analysis and Discussion)**. [cite: 1531] [cite_start]This initiates a new analysis loop within the context of the original task, culminating in a new implementation plan to address the remaining issues. [cite: 1532] [cite_start]The task is only complete after **Protocol 2.9 (Propose Verification Command)** is successfully executed for the *final, correct* implementation. [cite: 1533]
2.9. [cite_start]**Propose Verification Command**: After the final file in an implementation plan has been delivered and acknowledged by the user, the AI's final action for the task is to propose the specific command-line instruction(s) the user should run to verify that the bug has been fixed or the feature has been implemented correctly. [cite: 1534]
[cite_start]**2.9.1: Task Type Verification.** This protocol applies **only** if the final file modified was a code or data file (e.g., `.py`, `.json`, `.dat`). [cite: 1535] [cite_start]If the final file was a documentation or text file (e.g., `.md`), a verification command is not applicable. [cite: 1536] In this case, the AI's final action will be to **state that the documentation update is ready for review and ask for a final acknowledgment from the user.** The task is successfully concluded only after the user provides this acknowledgment.
### 3. File and Data Handling

3.1. [cite_start]**Project File Input.** All project source files and documentation will be provided for updates in a single text file called a **project bundle**, or pasted individually into the chat. [cite: 1538] [cite_start]The bundle uses a simple text header to separate each file: `--- FILE: path/to/file.ext ---` [cite: 1539]
3.2. [cite_start]**AI Output Format.** When the AI provides updated files, it must follow these rules to ensure data integrity. [cite: 1540]
    1.  [cite_start]**Single File Per Response**: Only one file will be delivered in a single response. [cite: 1541]
    2.  [cite_start]**Raw Source Text**: The content inside the delivered code block must be the raw source text of the file. [cite: 1542]
    3.  [cite_start]**Code File Delivery**: For code files (e.g., `.py`, `.json`), the content will be delivered in a standard fenced code block with the appropriate language specifier. [cite: 1543]
    4.  [cite_start]**Markdown File Delivery**: To prevent the user interface from rendering markdown and to provide a "Copy" button, the entire raw content of a documentation file (`.md`) must be delivered inside a single, plaintext-specified code block. [cite: 1544]
        * [cite_start]**Internal Code Fences**: Any internal markdown code fences (__CODE_BLOCK__) must be replaced with the `__CODE_BLOCK__` placeholder. [cite: 1545]
        * [cite_start]**Clarification**: This substitution is a requirement of the AI's web interface. [cite: 1546] [cite_start]The user will provide files back with standard markdown fences (`__CODE_BLOCK__`), which is the expected behavior. [cite: 1547]
3.3. **File and Checksum Verification.**
    1.  [cite_start]**Line Endings:** The user's file system uses Windows CRLF (`\r\n`). [cite: 1548] [cite_start]The AI must correctly handle this conversion when calculating checksums. [cite: 1549]
    2.  [cite_start]**Concise Reporting:** The AI will either state that **all checksums agree** or will list the **specific files that show a mismatch**. [cite: 1550]
    3.  [cite_start]**Mandatory Re-computation Protocol:** Every request for a checksum comparison is a **cache-invalidation event**. [cite: 1551] [cite_start]The AI must discard all previously calculated checksums, re-establish the definitive state, re-compute the hash for every file, and perform a literal comparison. [cite: 1552]
3.4. [cite_start]**Versioning Protocol.** This protocol defines how file versions are determined and updated. [cite: 1553]
    1.  [cite_start]**Format**: The official versioning format is `x.y.z-Beta`, where `x` is the major version, `y` is the minor version, and `z` is the patch number. [cite: 1554]
    2.  [cite_start]**Source of Truth**: The version number for any given file is located within its own content. [cite: 1555]
        * [cite_start]**Python (`.py`) files**: Contained within a "Revision History" section in the file's docstring. [cite: 1556]
        * [cite_start]**JSON (`.json`) files**: Stored as the value for a `"version"` parameter. [cite: 1557]
        * [cite_start]**Data (`.dat`) files**: Found within a commented revision history block. [cite: 1558]
    3.  [cite_start]**Update Procedure**: When a file is modified, only its patch number (`z`) will be incremented; [cite: 1559] [cite_start]this is done on a per-file basis. [cite: 1560] [cite_start]Major (`x`) or minor (`y`) version changes are forbidden unless explicitly directed by the user. [cite: 1560]
    4.  [cite_start]**History Preservation**: All existing revision histories must be preserved and appended to, never regenerated from scratch. [cite: 1561]

3.5. [cite_start]**File Naming Convention Protocol.** All generated report files must adhere to the standardized naming convention: `<report_id>_<details>_<callsigns>.<ext>`. [cite: 1562]

3.6. [cite_start]**File Purge Protocol.** This protocol provides a clear and safe procedure for removing a file from the project's definitive state. [cite: 1563]
    1.  [cite_start]**Initiation**: The user will start the process with the exact phrase: "**Gemini, initiate File Purge Protocol.**" The AI will then ask for the specific file(s) to be purged. [cite: 1564]
    2.  [cite_start]**Confirmation**: The AI will state which file(s) are targeted for removal and ask for explicit confirmation to proceed. [cite: 1565]
    3.  [cite_start]**Execution**: Once confirmed, the AI will remove the targeted file(s) from its in-memory representation of the definitive state. [cite: 1566]
    4.  [cite_start]**Verification**: The AI will confirm that the purge is complete and can provide a list of all files that remain in the definitive state upon request. [cite: 1567]
3.7. [cite_start]**Temporary Column Preservation Protocol.** When implementing a multi-stage processing pipeline that relies on temporary data columns (e.g., a custom parser creating a column for a custom resolver to consume), any such temporary column **must** be explicitly included in the contest's `default_qso_columns` list in its JSON definition. [cite: 1568] [cite_start]The `contest_log.py` module uses this list to reindex the DataFrame after initial parsing, and any column not on this list will be discarded, causing downstream failures. [cite: 1569] [cite_start]This is a critical data integrity step in the workflow. [cite: 1570]
### 4. Communication

4.1. [cite_start]**Communication Protocol.** All AI communication will be treated as **technical writing**. [cite: 1571] [cite_start]The AI must use the exact, consistent terminology from the source code and protocols. [cite: 1572]

4.2. [cite_start]**Definition of Prefixes.** The standard definitions for binary and decimal prefixes will be strictly followed (e.g., Kilo (k) = 1,000; Kibi (Ki) = 1,024). [cite: 1573]
4.3. [cite_start]**Large File Transmission Protocol.** This protocol is used to reliably transmit a single large file that has been split into multiple parts. [cite: 1574]
    1.  [cite_start]**AI Declaration:** The AI will state its intent and declare the total number of bundles to be sent. [cite: 1575]
    2.  **State-Driven Sequence:** The AI's response for each part of the transfer must follow a strict, multi-part structure:
        1. [cite_start]**Acknowledge State:** Confirm understanding of the user's last prompt. [cite: 1576]
        2. [cite_start]**Declare Current Action:** State which part is being sent using a "Block x of y" format. [cite: 1577]
        3. [cite_start]**Execute Action:** Provide the file bundle. [cite: 1578]
        4. [cite_start]**Provide Next Prompt:** If more parts remain, provide the exact text for the user's next prompt. [cite: 1578]
    3.  [cite_start]**Completion:** After the final bundle, the AI will state that the task is complete. [cite: 1579]

4.4. [cite_start]**Confirmed File Delivery Protocol.** This protocol is used for all standard file modifications. [cite: 1580]
    1.  [cite_start]The AI delivers the first file from the approved implementation plan. [cite: 1581]
    2.  [cite_start]The AI appends the mandatory confirmation prompt to the end of the same response. [cite: 1582]
    3.  [cite_start]The user provides an "Acknowledged" response. [cite: 1583]
    4.  [cite_start]The AI proceeds to deliver the next file, repeating the process until all files from the plan have been delivered and individually acknowledged. [cite: 1583]
---
## Part III: Project-Specific Implementation Patterns

[cite_start]These protocols describe specific, named patterns for implementing features in the Contest Log Analyzer software. [cite: 1584]
5.1. [cite_start]**Custom Parser Protocol.** For contests with highly complex or asymmetric exchanges. [cite: 1585]
    1.  [cite_start]**Activation**: A new key, `"custom_parser_module": "module_name"`, is added to the contest's `.json` file. [cite: 1586]
    2.  [cite_start]**Hook**: The `contest_log.py` script detects this key and calls the specified module. [cite: 1587]
    3.  [cite_start]**Implementation**: The custom parser module is placed in the `contest_specific_annotations` directory. [cite: 1588]

5.2. [cite_start]**Per-Mode Multiplier Protocol.** For contests where multipliers are counted independently for each mode. [cite: 1589]
    1.  [cite_start]**Activation**: The contest's `.json` file must contain `"multiplier_report_scope": "per_mode"`. [cite: 1590]
    2.  [cite_start]**Generator Logic**: This instructs the `report_generator.py` to run multiplier reports separately for each mode. [cite: 1591]
    3.  [cite_start]**Report Logic**: The specialist reports must accept a `mode_filter` argument. [cite: 1592]

5.3. [cite_start]**Data-Driven Scoring Protocol.** To accommodate different scoring methods, the `score_formula` key is available in the contest's `.json` definition. [cite: 1593] [cite_start]If set to `"qsos_times_mults"`, the final score will be `Total QSOs x Total Multipliers`. [cite: 1594] [cite_start]If omitted, it defaults to `Total QSO Points x Total Multipliers`. [cite: 1595]

5.4. [cite_start]**Text Table Generation Protocol.** This protocol governs the creation of text-based tables in reports, recommending the appropriate tool for the job. [cite: 1596]
    1.  [cite_start]**For Complex Reports, Use `prettytable`**: For any report that requires a fixed-width layout, precise column alignment, or the alignment and "stitching" of multiple tables, the **`prettytable`** library is the required standard. [cite: 1597] [cite_start]It offers direct, programmatic control over column widths and properties, which is essential for complex layouts. [cite: 1598]
    2.  [cite_start]**For Simple Reports, Use `tabulate`**: For reports that require only a single, standalone table where complex alignment with other elements is not a concern, the simpler **`tabulate`** library is a suitable alternative. [cite: 1599]
5.5. [cite_start]**Component Modernization Protocol.** This protocol is used to replace a legacy component (e.g., a report, a utility) with a modernized version that uses a new technology or methodology. [cite: 1600]
    1.  [cite_start]**Initiation**: During a **Technical Debt Cleanup Sprint**, the user or AI will identify a legacy component for modernization. [cite: 1601]
    2.  [cite_start]**Implementation**: An implementation plan will be created for a new module that replicates the functionality of the legacy component using the modern technology (e.g., a new report using the `plotly` library). [cite: 1602]
    3.  [cite_start]**Verification**: After the modernized component is approved and acknowledged, the user will run both the legacy and new versions. [cite: 1603] [cite_start]The AI will be asked to confirm that their outputs are functionally identical and that the new version meets all requirements. [cite: 1604]
    4.  [cite_start]**Deprecation**: Once the modernized component is verified as a complete replacement, the user will initiate the **File Purge Protocol (3.6)** to remove the legacy component from the definitive state. [cite: 1605]
    5.  [cite_start]**Example Application**: The migration of text-based reports from manual string formatting to the `tabulate` library (per Protocol 5.4) is a direct application of this modernization protocol. [cite: 1606]
5.6. [cite_start]**Custom ADIF Exporter Protocol.** For contests requiring a highly specific ADIF output format for compatibility with external tools (e.g., N1MM). [cite: 1607]
    1.  [cite_start]**Activation**: A new key, `"custom_adif_exporter": "module_name"`, is added to the contest's `.json` file. [cite: 1608]
    2.  [cite_start]**Hook**: The `log_manager.py` script detects this key and calls the specified module instead of the generic ADIF exporter. [cite: 1609]
    3.  [cite_start]**Implementation**: The custom exporter module is placed in the new `contest_tools/adif_exporters/` directory and must contain an `export_log(log, output_filepath)` function. [cite: 1610]
---
## Part IV: Special Case & Recovery Protocols

[cite_start]These protocols are for troubleshooting, error handling, and non-standard situations. [cite: 1611]
### 6. Debugging and Error Handling

6.1. **Mutual State & Instruction Verification.**
    1.  [cite_start]**State Verification**: If an instruction from the user appears to contradict the established project state or our immediate goals, the AI must pause and ask for clarification before proceeding. [cite: 1612]
    2.  [cite_start]**Instructional Clarity**: If a user's prompt contains a potential typo or inconsistency (e.g., a misspelled command or incorrect filename), the AI must pause and ask for clarification. [cite: 1613] [cite_start]The AI will not proceed based on an assumption. [cite: 1614]
    3.  [cite_start]**File State Request**: If a state mismatch is suspected as the root cause of an error, the AI is authorized to request a copy of the relevant file(s) from the user to establish a definitive ground truth. [cite: 1614]
6.2. [cite_start]**Debug "A Priori" When Stuck.** If an initial bug fix fails or the cause of an error is not immediately obvious, the first diagnostic step to consider is to add detailed logging (e.g., `logging.info()` statements, hexadecimal dumps) to the failing code path. [cite: 1615] [cite_start]The goal is to isolate the smallest piece of failing logic and observe the program's actual runtime state. [cite: 1616]

6.3. [cite_start]**Error Analysis Protocol.** When an error in the AI's process is identified, the AI must provide a clear and concise analysis. [cite: 1617] [cite_start]**A failure to provide a correct analysis after being corrected by the user constitutes a new, more severe error that must also be analyzed.** [cite: 1618]
    1.  [cite_start]**Acknowledge the Error:** State clearly that a mistake was made. [cite: 1618]
    2.  [cite_start]**Request Diagnostic Output:** If the user has not already provided it, the AI's immediate next step is to request the new output that demonstrates the failure (e.g., the incorrect text report or a screenshot). [cite: 1619] [cite_start]This output becomes the new ground truth for the re-analysis. [cite: 1620]
    3.  [cite_start]**Identify the Root Cause:** Explain the specific flaw in the internal process or logic that led to the error. [cite: 1621] [cite_start]This includes identifying which specific principles or protocols were violated. [cite: 1622]
    4.  [cite_start]**Propose a Corrective Action:** Describe the specific, procedural change that will be implemented to prevent the error from recurring. [cite: 1623]
6.4. [cite_start]**Corrupted User Input Protocol.** This protocol defines the procedure for handling malformed or corrupted input files provided by the user. [cite: 1624]
    1.  Halt the current task immediately.
    2.  [cite_start]Report the specific file that contains the error and describe the nature of the error (e.g., "Cabrillo parsing failed on line X" or "Bundle is missing a file header"). [cite: 1625]
    3.  [cite_start]Request a corrected version of the file from the user. [cite: 1626]

6.5. [cite_start]**Bundle Integrity Check Protocol.** This protocol is triggered during a **Definitive State Initialization** if the AI discovers logical inconsistencies within the provided bundles. [cite: 1627]
    1.  [cite_start]Halt the initialization process after parsing all bundles. [cite: 1628]
    2.  [cite_start]Report all discovered anomalies to the user. [cite: 1628] Examples include:
        * [cite_start]**Duplicate Filenames:** The same file path appearing in multiple bundles or multiple times in one bundle. [cite: 1629]
        * [cite_start]**Content Mismatch:** A file whose content appears to belong to another file (e.g., a file named `a.py` contains code clearly from `b.py`). [cite: 1630]
        * [cite_start]**Misplaced Files:** A file that appears to be in the wrong logical directory (e.g., a core application file located in the `Docs/` bundle). [cite: 1631]
    3.  [cite_start]Await user clarification and direction before completing the initialization and establishing the definitive state. [cite: 1632]
6.6. [cite_start]**Self-Correction on Contradiction Protocol.** This protocol is triggered when the AI produces an analytical result that is logically impossible or directly contradicts a previously stated fact or a result from another tool. [cite: 1633]
    1.  [cite_start]**Halt Task:** Immediately stop the current line of reasoning or task execution. [cite: 1634]
    2.  [cite_start]**Acknowledge Contradiction:** Explicitly state that a logical contradiction has occurred (e.g., "My last two statements are contradictory" or "The results of my analysis are logically impossible"). [cite: 1635]
    3.  [cite_start]**Identify Trustworthy Facts:** Re-evaluate the inputs and previous steps to determine which pieces of information are most reliable (e.g., a direct check of a structured file like a JSON is more reliable than a complex parse of a semi-structured text file). [cite: 1636]
    4.  [cite_start]**Invalidate Flawed Analysis:** Clearly retract the incorrect statements or analysis. [cite: 1637]
    5.  [cite_start]**Proceed with Verification:** Continue the task using only the most trustworthy facts and methods. [cite: 1638]
6.7. [cite_start]**Simplified Data Verification Protocol.** This protocol is used when a tool's analysis of a complex file is in doubt or has been proven incorrect. [cite: 1639]
    1.  [cite_start]**Initiation:** The user provides a simplified, ground-truth data file (e.g., a JSON or text file containing only the essential data points). [cite: 1640]
    2.  [cite_start]**Prioritization:** The AI must treat this new file as the highest-priority source of truth for the specific data it contains. [cite: 1641]
    3.  [cite_start]**Analysis:** The AI will use the simplified file to debug its own logic and resolve the discrepancy. [cite: 1642] [cite_start]The goal is to make the primary analysis tool's output match the ground truth provided in the simplified file. [cite: 1643]
### 7. Miscellaneous Protocols

7.1. [cite_start]**Technical Debt Cleanup Protocol.** When code becomes convoluted, a **Technical Debt Cleanup Sprint** will be conducted to refactor the code for clarity, consistency, and maintainability. [cite: 1644]
7.2. [cite_start]**Multi-Part Bundle Protocol.** If a large or complex text file cannot be transmitted reliably in a single block, the Multi-Part Bundle Protocol will be used. [cite: 1645] [cite_start]The AI will take the single file and split its content into multiple, smaller text chunks. [cite: 1646] [cite_start]These chunks will then be delivered sequentially using the **Large File Transmission Protocol (Protocol 4.3)**. [cite: 1647]

7.3. [cite_start]**Fragile Dependency Protocol.** If a third-party library proves to be unstable, a sprint will be conducted to replace it with a more robust alternative. [cite: 1648]
7.4. [cite_start]**Prototype Script Development Protocol.** This protocol is used for the creation and modification of standalone prototype scripts located in the `test_code/` directory. [cite: 1649]
    1.  [cite_start]**Formal Entity**: A prototype script is a formal, versioned file, but is exempt from requiring an in-file revision history. [cite: 1650] [cite_start]Versioning begins at `1.0.0-Beta`. [cite: 1651]
    2.  [cite_start]**Standard Workflow**: All work on a prototype script must follow the complete **Task Execution Workflow (Section 2)**, including a formal Implementation Plan, user Approval, and a Confirmed File Delivery. [cite: 1651]
7.5. **Tool Suitability Re-evaluation Protocol.**
    1.  [cite_start]**Trigger**: This protocol is initiated when an approved implementation plan fails for a second time due to the unexpected or undocumented behavior of a third-party library or tool. [cite: 1652]
    2.  [cite_start]**Halt**: The AI must halt further implementation attempts with the current tool. [cite: 1653]
    3.  [cite_start]**Analysis**: The AI must analyze *why* the tool is failing and identify the specific feature gap (e.g., "`tabulate` lacks a mechanism to enforce column widths on separate tables"). [cite: 1654]
    4.  [cite_start]**Propose Alternatives**: The AI will research and propose one or two alternative tools that appear to have the required features, explaining how they would solve the specific problem. [cite: 1655]
    5.  [cite_start]**User Decision**: The user will make the final decision on whether to switch tools or attempt a different workaround. [cite: 1656]