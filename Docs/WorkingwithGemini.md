# Project Workflow Guide

**Version: 0.42.0-Beta**
**Date: 2025-08-20**

---
### --- Revision History ---
## [0.42.0-Beta] - 2025-08-20
### Added
# - Added Protocol 2.3 (Visual Prototype Protocol) to formalize the use
#   of prototype scripts for complex visual changes.
### Changed
# - Renumbered subsequent protocols in the Task Execution Workflow and
#   updated internal cross-references.
## [0.38.0-Beta] - 2025-08-19
### Added
# - Added Protocol 2.3 (Baseline Consistency Check) to require plan
#   validation against the definitive state before the plan is proposed.
### Changed
# - Renumbered subsequent protocols in the Task Execution Workflow.
# - Updated internal cross-references to match the new numbering.
## [0.37.1-Beta] - 2025-08-18
### Changed
# - Refined the Markdown File Delivery Protocol (3.2.4) to require
#   enclosing the entire file content in a plaintext code block for
#   easier copying.
## [0.37.0-Beta] - 2025-08-18
### Added
# - Added Principle 13 to formalize the process of classifying data
#   conflicts as either data errors or complex rule requirements.
# - Added Protocol 2.8 to the Task Execution Workflow, requiring the AI
#   to propose a verification command after a task is complete.
## [0.36.12-Beta] - 2025-08-17
### Changed
# - Integrated clarifications from user feedback into Protocol 1.2,
#   Principle 9, and Protocol 3.4.3 to make the document self-contained.
### Added
# - Added Protocol 6.5 (Bundle Integrity Check Protocol) to define a
#   procedure for handling logical anomalies within initialization bundles.
## [0.36.11-Beta] - 2025-08-16
### Added
# - Added Protocol 1.7 (Project Structure Onboarding) to provide bootstrap
#   architectural context after an initialization.
# - Added Protocol 6.4 (Corrupted User Input Protocol) to define a
#   formal procedure for handling malformed user files.
## [0.36.10-Beta] - 2025-08-16
### Added
# - Added the new, top-priority Principle 1 for Context Integrity, which
#   mandates a full state reset upon detection of context loss.
### Changed
# - Renumbered all subsequent principles accordingly.
## [0.36.9-Beta] - 2025-08-15
### Added
# - Added rule 3.2.4 to mandate the substitution of markdown code fences
#   with ``` for proper web interface rendering.
## [0.36.4-Beta] - 2025-08-15
### Changed
# - Clarified Principle 8 (Surgical Modification) to explicitly require
#   the preservation of revision histories.
### Added
# - Added Protocol 1.6 (Session Versioning Protocol) to establish the
#   current version series at the start of a task.
## [0.36.3-Beta] - 2025-08-15
### Changed
# - Merged missing protocols from v0.36.0-Beta to create a complete document.
# - Synthesized a new, authoritative Versioning Protocol based on user clarification.
# - Reorganized the document to separate workflow protocols from software design patterns.
## [0.36.2-Beta] - 2025-08-15
### Changed
# - Overhauled the Task Execution and File Delivery protocols to formalize
#   the new, more robust, state-machine workflow with per-file acknowledgments.
## [0.36.1-Beta] - 2025-08-15
### Changed
# - Amended Protocol 2.2 to require the file's baseline version
#   number in all implementation plans.
## [0.36.0-Beta] - 2025-08-15
### Changed
# - Replaced the "Atomic State Checkpoint Protocol" (1.2) with the new
#   "Definitive State Reconciliation Protocol" which uses the last
#   Definitive State Initialization as its baseline.
# - Amended Protocol 1.5 to add an explicit step for handling
#   documents that require no changes.
---

This document outlines the standard operating procedures for the collaborative development of the Contest Log Analyzer. **The primary audience for this document is the Gemini AI agent.**

**Its core purpose is to serve as a persistent set of rules and context.** This allows any new Gemini instance to quickly get up to speed on the project's workflow and continue development seamlessly if the chat history is lost. Adhering to this workflow ensures consistency and prevents data loss.
---
## Part I: Core Principles

These are the foundational rules that govern all interactions and analyses.
1.  [cite_start]**Context Integrity is Absolute.** The definitive project state is established by the baseline `*_bundle.txt` files and evolves with every acknowledged file change. [cite: 2438] [cite_start]Maintaining this evolving state requires both the baseline bundles and the subsequent chat history. [cite: 2439] [cite_start]If I detect that the baseline `*_bundle.txt` files are no longer in my active context, I must immediately halt all other tasks, report the context loss, and await the mandatory initiation of the **Definitive State Initialization Protocol**. [cite: 2440]
2.  [cite_start]**Protocol Adherence is Paramount.** All protocols must be followed with absolute precision. [cite: 2441] [cite_start]Failure to do so invalidates the results and undermines the development process. [cite: 2442] [cite_start]There is no room for deviation unless a deviation is explicitly requested by the AI and authorized by the user. [cite: 2443]
3.  [cite_start]**Trust the User's Diagnostics.** When the user reports a bug, their description of the symptoms should be treated as the ground truth. [cite: 2444] [cite_start]The AI's primary task is to find the root cause of those specific, observed symptoms, not to propose alternative theories. [cite: 2445]
4.  [cite_start]**No Unrequested Changes.** The AI will only implement changes explicitly requested by the user. [cite: 2446] [cite_start]All suggestions for refactoring, library changes, or stylistic updates must be proposed and approved by the user before implementation. [cite: 2447]
5.  **Technical Diligence Over Conversational Assumptions.** Technical tasks are not conversations. [cite_start]Similar-looking prompts do not imply similar answers. [cite: 2448] [cite_start]Each technical request must be treated as a unique, atomic operation. [cite: 2449] [cite_start]The AI must execute a full re-computation from the current project state for every request, ignoring any previous results or cached data. [cite: 2450]
6.  [cite_start]**Prefer Logic in Code, Not Data.** The project's design philosophy is to keep the `.json` definition files as simple, declarative maps. [cite: 2451] [cite_start]All complex, conditional, or contest-specific logic should be implemented in dedicated Python modules. [cite: 2452]
7.  [cite_start]**Assume Bugs are Systemic.** When a bug is identified in one module, the default assumption is that the same flaw exists in all other similar modules. [cite: 2453] [cite_start]The AI must perform a global search for that specific bug pattern and fix all instances at once. [cite: 2454]
8.  [cite_start]**Reports Must Be Non-Destructive.** Specialist report scripts must **never** modify the original `ContestLog` objects they receive. [cite: 2455] [cite_start]All data filtering or manipulation must be done on a temporary **copy** of the DataFrame. [cite: 2456]
9.  [cite_start]**Principle of Surgical Modification.** All file modifications must be treated as surgical operations. [cite: 2457] [cite_start]The AI must start with the last known-good version of a file as the ground truth (established by the **Definitive State Reconciliation Protocol**) and apply only the minimal, approved change. [cite: 2458] [cite_start]Full file regeneration from an internal model is strictly forbidden to prevent regressions. [cite: 2459] [cite_start]**This includes the verbatim preservation of all unchanged sections, especially headers and the complete, existing revision history.** [cite: 2460]
10. [cite_start]**Primacy of Official Rules.** The AI will place the highest emphasis on analyzing the specific data, context, and official rules provided, using them as the single source of truth. [cite: 2460]
11. [cite_start]**Citation of Official Rules.** When researching contest rules, the AI will prioritize finding and citing the **official rules from the sponsoring organization**. [cite: 2461]
12. [cite_start]**Uniqueness of Contest Logic.** Each contest's ruleset is to be treated as entirely unique. [cite: 2462] [cite_start]Logic from one contest must **never** be assumed to apply to another. [cite: 2463]
13. [cite_start]**Classify Ambiguity Before Action.** When the AI discovers a conflict between the data (e.g., in a `.dat` or `.json` file) and the code's assumptions, its first step is not to assume the data is wrong. [cite: 2464] It must present the conflict to the user and ask for a ruling:
    * [cite_start]Is this a **Data Integrity Error** that should be corrected in the data file? [cite: 2465]
    * [cite_start]Is this a **Complex Rule Requirement** that must be handled by enhancing the code logic? [cite: 2466]
[cite_start]The user's classification will guide the subsequent analysis and implementation plan. [cite: 2467]
---
## Part II: Standard Operating Protocols

[cite_start]These are the step-by-step procedures for common, day-to-day development tasks. [cite: 2468]

### 1. Session Management

1.1. [cite_start]**Onboarding Protocol.** The first action for any AI agent upon starting a session is to read this document in its entirety, acknowledge it, and ask any clarifying questions. [cite: 2469]
1.2. **Definitive State Reconciliation Protocol.**
    1.  [cite_start]**Establish Baseline**: The definitive state is established by first locating the most recent **Definitive State Initialization Protocol** in the chat history. [cite: 2470] [cite_start]The files from this initialization serve as the absolute baseline. [cite: 2471]
    2.  [cite_start]**Scan Forward for Updates**: After establishing the baseline, the AI will scan the chat history *forward* from that point to the present. [cite: 2472]
    3.  [cite_start]**Identify Latest Valid Version**: The AI will identify the **latest** version of each file that was part of a successfully completed and mutually acknowledged transaction (i.e., file delivery, AI confirmation, and user acknowledgment). [cite: 2473] [cite_start]This version supersedes the baseline version. [cite: 2474]
    4.  [cite_start]**Handle Ambiguity**: If any file transaction is found that was initiated but not explicitly acknowledged by the user, the AI must halt reconciliation, report the ambiguous file, and await user clarification. [cite: 2474]
1.3. [cite_start]**Context Checkpoint Protocol.** If the AI appears to have lost context, the user can issue a **Context Checkpoint**. [cite: 2475]
    1.  [cite_start]The user begins with the exact phrase: **"Gemini, let's establish a Context Checkpoint."** [cite: 2476]
    2.  [cite_start]The user provides a brief, numbered list of critical facts. [cite: 2476]
1.4. [cite_start]**Definitive State Initialization Protocol.** This protocol serves as a "hard reset" of the project state. [cite: 2477]
    1.  [cite_start]**Initiation:** The user or AI requests a "Definitive State Initialization." [cite: 2478]
    2.  [cite_start]**Agreement:** The other party agrees to proceed. [cite: 2479]
    3.  [cite_start]**File Upload:** The user creates and uploads new, complete `project_bundle.txt`, `documentation_bundle.txt`, and `data_bundle.txt` files. [cite: 2479]
    4.  [cite_start]**State Purge:** The AI discards its current understanding of the project state. [cite: 2480]
    5.  [cite_start]**Re-Initialization:** The AI establishes a new definitive state based *only* on the new bundles. [cite: 2481]
    6.  [cite_start]**Verification and Acknowledgment:** The AI acknowledges the new state and provides a complete list of all files extracted from the bundles. [cite: 2482]
1.5. [cite_start]**Document Review and Synchronization Protocol.** This protocol is used to methodically review and update all project documentation (`.md` files) to ensure it remains synchronized with the code baseline. [cite: 2483]
    1.  [cite_start]**Initiate Protocol and List Documents:** The AI will state that the protocol is beginning and will provide a complete list of all documents to be reviewed (`Readme.md` and all `.md` files in the `Docs` directory). [cite: 2484]
    2.  [cite_start]**Begin Sequential Review:** The AI will then loop through the list, processing one document at a time using the following steps: [cite: 2485]
        * [cite_start]**Step A: Identify and Request.** State which document is next and ask for permission to proceed. [cite: 2485]
        * [cite_start]**Step B: Analyze.** Upon approval, perform a full "a priori" review of the document against the current code baseline and provide an analysis of any discrepancies. [cite: 2486]
        * [cite_start]**Step C (Changes Needed): Propose Plan.** If discrepancies are found, ask if the user wants an implementation plan to update the document. [cite: 2487]
        * [cite_start]**Step D: Provide Plan.** Upon approval, provide a detailed, surgical implementation plan for the necessary changes. [cite: 2488]
        * [cite_start]**Step E: Request to Proceed.** Ask for explicit permission to generate the updated document. [cite: 2489]
        * [cite_start]**Step F: Deliver Update.** Upon approval, perform a **Pre-Flight Check**, explicitly state that the check is complete, and then deliver the updated document. [cite: 2490]
        * [cite_start]**Step G (No Changes Needed):** If the analysis in Step B finds no discrepancies, the AI will state that the document is already synchronized and ask for the user's confirmation to proceed to the next document. [cite: 2491]
    3.  [cite_start]**Completion:** After the final document has been processed, the AI will state that the protocol is complete. [cite: 2492]

1.6. [cite_start]**Session Versioning Protocol.** At the start of a new development task, the user will state the current version series (e.g., 'We are working on Version 0.36.x-Beta'). [cite: 2493] [cite_start]All subsequent file modifications for this and related tasks must use this version series, incrementing the patch number as needed. [cite: 2494]
1.7. [cite_start]**Project Structure Onboarding.** After a state initialization, the AI will confirm its understanding of the high-level project architecture. [cite: 2495]
    * [cite_start]`contest_tools/`: The core application library. [cite: 2496]
    * [cite_start]`contest_tools/reports/`: The "plug-in" directory for all report modules. [cite: 2496]
    * [cite_start]`contest_tools/contest_definitions/`: Data-driven JSON definitions for each contest. [cite: 2497]
    * [cite_start]`Docs/`: All user and developer documentation. [cite: 2497]
    * [cite_start]`test_code/`: Utility scripts not part of the main application. [cite: 2498]
    * [cite_start]`data/`: Required data files (e.g., `cty.dat`). [cite: 2498]
### 2. Task Execution Workflow
[cite_start]This workflow is a formal state machine that governs all development tasks, from initial request to final completion. [cite: 2499]
2.1. [cite_start]**Task Initiation**: The user provides a problem, feature request, or document update and requests an analysis. [cite: 2500]
2.2. **Analysis and Discussion**: The AI provides an initial analysis. [cite_start]The user and AI may discuss the analysis to refine the understanding of the problem. [cite: 2501]
2.3. [cite_start]**Visual Prototype Protocol.** This protocol is used to resolve ambiguity in tasks involving complex visual layouts or new, hard-to-describe logic before a full implementation is planned. [cite: 2502]
    1.  [cite_start]**Initiation:** The AI proposes or the user requests a prototype to clarify a concept. [cite: 2503]
    2.  [cite_start]**Agreement:** Both parties agree to create the prototype. [cite: 2504]
    3.  [cite_start]**Prototype Delivery:** The AI delivers a standalone, self-contained script. [cite: 2505] [cite_start]The script must use simple, hardcoded data and focus only on demonstrating the specific concept in question. [cite: 2506]
    4.  [cite_start]**Prototype Usability Clause:** For visual prototypes using Matplotlib, the script must save the output to a file and then immediately display the chart on-screen using `plt.show()` for ease of verification. [cite: 2507]
    5.  [cite_start]**Review and Iteration:** The user reviews the prototype's output and provides feedback. [cite: 2508] [cite_start]This step can be repeated until the prototype is correct. [cite: 2509]
    6.  [cite_start]**Approval:** The user gives explicit approval of the final prototype. [cite: 2510] [cite_start]This approval serves as the visual and logical ground truth for the subsequent implementation plan. [cite: 2511]
2.4. [cite_start]**Baseline Consistency Check.** Before presenting an implementation plan, the AI must perform and explicitly state the completion of a "Baseline Consistency Check." [cite: 2512] [cite_start]This check verifies that all proposed actions (e.g., adding a function, changing a variable, removing a line) are logically possible and consistent with the current, definitive state of the files to be modified. [cite: 2513]
2.5. **Implementation Plan**: The user requests an implementation plan. [cite_start]The AI provides a detailed plan, which must adhere to the **Pre-Flight Check Protocol (2.6)**. [cite: 2514]
2.6. [cite_start]**Pre-Flight Check Protocol.** The AI will perform a "white-box" mental code review **before** delivering a modified file. [cite: 2515]
    1.  [cite_start]**Stating the Plan:** The AI will state its Pre-Flight Check plan. [cite: 2516] [cite_start]The **Inputs** section must include the full filename and the specific baseline version number of the file to be modified. [cite: 2517] [cite_start]The plan must also state the **Expected Outcome**. [cite: 2518]
    2.  [cite_start]**Mental Walkthrough:** The AI will mentally trace the execution path to confirm the logic produces the expected outcome. [cite: 2518]
    3.  [cite_start]**User Verification:** The user performs the final verification by running the code. [cite: 2519]
    4.  [cite_start]**State Confirmation Procedure**: The AI will affirm that the mandatory confirmation prompt, as defined in Protocol 4.4, will be included with the file delivery. [cite: 2520]
2.7. [cite_start]**Plan Refinement**: The user reviews the plan and may request changes or refinements. [cite: 2521] [cite_start]The AI provides a revised plan, repeating this step as necessary. [cite: 2522]
2.8. [cite_start]**Approval**: The user provides explicit approval of the final implementation plan (e.g., "Approved"). [cite: 2523] [cite_start]Instructions, clarifications, or new requirements provided after a plan has been proposed do not constitute approval; [cite: 2524] [cite_start]they will be treated as requests for plan refinement under Protocol 2.7. [cite: 2525]
2.9. [cite_start]**Execution**: Upon approval, the AI will proceed with the **Confirmed File Delivery Protocol (4.4)**. [cite: 2526]
2.10. [cite_start]**Propose Verification Command**: After the final file in an implementation plan has been delivered and acknowledged by the user, the AI's final action for the task is to propose the specific command-line instruction(s) the user should run to verify that the bug has been fixed or the feature has been implemented correctly. [cite: 2527]
### 3. File and Data Handling

3.1. [cite_start]**Project File Input.** All project source files and documentation will be provided for updates in a single text file called a **project bundle**, or pasted individually into the chat. [cite: 2528] [cite_start]The bundle uses a simple text header to separate each file: `--- FILE: path/to/file.ext ---` [cite: 2529]
3.2. [cite_start]**AI Output Format.** When the AI provides updated files, it must follow these rules to ensure data integrity. [cite: 2530]
    1.  [cite_start]**Single File Per Response**: Only one file will be delivered in a single response. [cite: 2531]
    2.  [cite_start]**Raw Source Text**: The content inside the delivered code block must be the raw source text of the file. [cite: 2532]
    3.  [cite_start]**Code File Delivery**: For code files (e.g., `.py`, `.json`), the content will be delivered in a standard fenced code block with the appropriate language specifier. [cite: 2533]
    4.  [cite_start]**Markdown File Delivery**: To prevent the user interface from rendering markdown and to provide a "Copy" button, the entire raw content of a documentation file (`.md`) must be delivered inside a single, plaintext-specified code block. [cite: 2534] [cite_start]The rule for replacing internal code fences with ````` still applies to the content within this block. [cite: 2535]
        ```text
        # Markdown Header

        This is the raw text of the .md file.

        ```
        # An internal code block is replaced.
        ```
        ```
3.3. **File and Checksum Verification.**
    1.  [cite_start]**Line Endings:** The user's file system uses Windows CRLF (`\r\n`). [cite: 2538] [cite_start]The AI must correctly handle this conversion when calculating checksums. [cite: 2539]
    2.  [cite_start]**Concise Reporting:** The AI will either state that **all checksums agree** or will list the **specific files that show a mismatch**. [cite: 2540]
    3.  [cite_start]**Mandatory Re-computation Protocol:** Every request for a checksum comparison is a **cache-invalidation event**. [cite: 2541] [cite_start]The AI must discard all previously calculated checksums, re-establish the definitive state, re-compute the hash for every file, and perform a literal comparison. [cite: 2542]
3.4. [cite_start]**Versioning Protocol.** This protocol defines how file versions are determined and updated. [cite: 2543]
    1.  [cite_start]**Format**: The official versioning format is `x.y.z-Beta`, where `x` is the major version, `y` is the minor version, and `z` is the patch number. [cite: 2544]
    2.  [cite_start]**Source of Truth**: The version number for any given file is located within its own content. [cite: 2545]
        * [cite_start]**Python (`.py`) files**: Contained within a "Revision History" section in the file's docstring. [cite: 2546]
        * [cite_start]**JSON (`.json`) files**: Stored as the value for a `"version"` parameter. [cite: 2547]
        * [cite_start]**Data (`.dat`) files**: Found within a commented revision history block. [cite: 2548]
    3.  [cite_start]**Update Procedure**: When a file is modified, only its patch number (`z`) will be incremented; [cite: 2549] this is done on a per-file basis. [cite_start]Major (`x`) or minor (`y`) version changes will only be made upon explicit user direction. [cite: 2550]
    4.  [cite_start]**History Preservation**: All existing revision histories must be preserved and appended to, never regenerated from scratch. [cite: 2551]

3.5. [cite_start]**File Naming Convention Protocol.** All generated report files must adhere to the standardized naming convention: `<report_id>_<details>_<callsigns>.<ext>`. [cite: 2552]

3.6. [cite_start]**File Purge Protocol.** This protocol provides a clear and safe procedure for removing a file from the project's definitive state. [cite: 2553]
    1.  [cite_start]**Initiation**: The user will start the process with the exact phrase: "**Gemini, initiate File Purge Protocol.**" The AI will then ask for the specific file(s) to be purged. [cite: 2554]
    2.  [cite_start]**Confirmation**: The AI will state which file(s) are targeted for removal and ask for explicit confirmation to proceed. [cite: 2555]
    3.  [cite_start]**Execution**: Once confirmed, the AI will remove the targeted file(s) from its in-memory representation of the definitive state. [cite: 2556]
    4.  [cite_start]**Verification**: The AI will confirm that the purge is complete and can provide a list of all files that remain in the definitive state upon request. [cite: 2557]
### 4. Communication

4.1. [cite_start]**Communication Protocol.** All AI communication will be treated as **technical writing**. [cite: 2558] [cite_start]The AI must use the exact, consistent terminology from the source code and protocols. [cite: 2559]

4.2. [cite_start]**Definition of Prefixes.** The standard definitions for binary and decimal prefixes will be strictly followed (e.g., Kilo (k) = 1,000; Kibi (Ki) = 1,024). [cite: 2560]
4.3. [cite_start]**Large File Transmission Protocol.** This protocol is used to reliably transmit a single large file that has been split into multiple parts. [cite: 2561]
    1.  [cite_start]**AI Declaration:** The AI will state its intent and declare the total number of bundles to be sent. [cite: 2562]
    2.  [cite_start]**State-Driven Sequence:** The AI's response for each part of the transfer must follow a strict, multi-part structure: [cite: 2563]
        1. [cite_start]**Acknowledge State:** Confirm understanding of the user's last prompt. [cite: 2563]
        2. [cite_start]**Declare Current Action:** State which part is being sent using a "Block x of y" format. [cite: 2564]
        3. [cite_start]**Execute Action:** Provide the file bundle. [cite: 2565]
        4. [cite_start]**Provide Next Prompt:** If more parts remain, provide the exact text for the user's next prompt. [cite: 2565]
    3.  [cite_start]**Completion:** After the final bundle, the AI will state that the task is complete. [cite: 2566]

4.4. [cite_start]**Confirmed File Delivery Protocol.** This protocol is used for all standard file modifications. [cite: 2567]
    1.  [cite_start]The AI delivers the first file from the approved implementation plan. [cite: 2568]
    2.  [cite_start]The AI appends the mandatory confirmation prompt to the end of the same response. [cite: 2569]
    3.  [cite_start]The user provides an "Acknowledged" response. [cite: 2570]
    4.  [cite_start]The AI proceeds to deliver the next file, repeating the process until all files from the plan have been delivered and individually acknowledged. [cite: 2570]
---
## Part III: Project-Specific Implementation Patterns

[cite_start]These protocols describe specific, named patterns for implementing features in the Contest Log Analyzer software. [cite: 2571]
5.1. [cite_start]**Custom Parser Protocol.** For contests with highly complex or asymmetric exchanges. [cite: 2572]
    1.  [cite_start]**Activation**: A new key, `"custom_parser_module": "module_name"`, is added to the contest's `.json` file. [cite: 2573]
    2.  [cite_start]**Hook**: The `contest_log.py` script detects this key and calls the specified module. [cite: 2574]
    3.  [cite_start]**Implementation**: The custom parser module is placed in the `contest_specific_annotations` directory. [cite: 2575]

5.2. [cite_start]**Per-Mode Multiplier Protocol.** For contests where multipliers are counted independently for each mode. [cite: 2576]
    1.  [cite_start]**Activation**: The contest's `.json` file must contain `"multiplier_report_scope": "per_mode"`. [cite: 2577]
    2.  [cite_start]**Generator Logic**: This instructs the `report_generator.py` to run multiplier reports separately for each mode. [cite: 2578]
    3.  [cite_start]**Report Logic**: The specialist reports must accept a `mode_filter` argument. [cite: 2579]

5.3. [cite_start]**Data-Driven Scoring Protocol.** To accommodate different scoring methods, the `score_formula` key is available in the contest's `.json` definition. [cite: 2580] [cite_start]If set to `"qsos_times_mults"`, the final score will be `Total QSOs x Total Multipliers`. [cite: 2581] [cite_start]If omitted, it defaults to `Total QSO Points x Total Multipliers`. [cite: 2582]
---
## Part IV: Special Case & Recovery Protocols

[cite_start]These protocols are for troubleshooting, error handling, and non-standard situations. [cite: 2583]
### 6. Debugging and Error Handling

6.1. **Mutual State & Instruction Verification.**
    1.  [cite_start]**State Verification**: If an instruction from the user appears to contradict the established project state or our immediate goals, the AI must pause and ask for clarification before proceeding. [cite: 2584]
    2.  [cite_start]**Instructional Clarity**: If a user's prompt contains a potential typo or inconsistency (e.g., a misspelled command or incorrect filename), the AI must pause and ask for clarification. [cite: 2585] [cite_start]The AI will not proceed based on an assumption. [cite: 2586]
    3.  [cite_start]**File State Request**: If a state mismatch is suspected as the root cause of an error, the AI is authorized to request a copy of the relevant file(s) from the user to establish a definitive ground truth. [cite: 2586]
6.2. [cite_start]**Debug "A Priori" When Stuck.** If an initial bug fix fails or the cause of an error is not immediately obvious, the first diagnostic step to consider is to add detailed logging (e.g., `logging.info()` statements, hexadecimal dumps) to the failing code path. [cite: 2587] [cite_start]The goal is to isolate the smallest piece of failing logic and observe the program's actual runtime state. [cite: 2588]

6.3. [cite_start]**Error Analysis Protocol.** When an error in the AI's process is identified, the AI must provide a clear and concise analysis. [cite: 2589]
    1.  [cite_start]**Acknowledge the Error:** State clearly that a mistake was made. [cite: 2590]
    2.  [cite_start]**Identify the Root Cause:** Explain the specific flaw in the internal process or logic that led to the error. [cite: 2591]
    3.  [cite_start]**Propose a Corrective Action:** Describe the specific, procedural change that will be implemented to prevent the error from recurring. [cite: 2592]
6.4. [cite_start]**Corrupted User Input Protocol.** This protocol defines the procedure for handling malformed or corrupted input files provided by the user. [cite: 2593]
    1.  [cite_start]Halt the current task immediately. [cite: 2594]
    2.  [cite_start]Report the specific file that contains the error and describe the nature of the error (e.g., "Cabrillo parsing failed on line X" or "Bundle is missing a file header"). [cite: 2594]
    3.  [cite_start]Request a corrected version of the file from the user. [cite: 2595]

6.5. [cite_start]**Bundle Integrity Check Protocol.** This protocol is triggered during a **Definitive State Initialization** if the AI discovers logical inconsistencies within the provided bundles. [cite: 2596]
    1.  [cite_start]Halt the initialization process after parsing all bundles. [cite: 2597]
    2.  [cite_start]Report all discovered anomalies to the user. [cite: 2597] Examples include:
        * [cite_start]**Duplicate Filenames:** The same file path appearing in multiple bundles or multiple times in one bundle. [cite: 2598]
        * [cite_start]**Content Mismatch:** A file whose content appears to belong to another file (e.g., a file named `a.py` contains code clearly from `b.py`). [cite: 2599]
        * [cite_start]**Misplaced Files:** A file that appears to be in the wrong logical directory (e.g., a core application file located in the `Docs/` bundle). [cite: 2600]
    3.  [cite_start]Await user clarification and direction before completing the initialization and establishing the definitive state. [cite: 2601]

### 7. Miscellaneous Protocols

7.1. [cite_start]**Technical Debt Cleanup Protocol.** When code becomes convoluted, a **Technical Debt Cleanup Sprint** will be conducted to refactor the code for clarity, consistency, and maintainability. [cite: 2602]
7.2. [cite_start]**Multi-Part Bundle Protocol.** If a large or complex text file cannot be transmitted reliably in a single block, the Multi-Part Bundle Protocol will be used. [cite: 2603] [cite_start]The AI will take the single file and split its content into multiple, smaller text chunks. [cite: 2604] [cite_start]These chunks will then be delivered sequentially using the **Large File Transmission Protocol (Protocol 4.3)**. [cite: 2605]

7.3. [cite_start]**Fragile Dependency Protocol.** If a third-party library proves to be unstable, a sprint will be conducted to replace it with a more robust alternative. [cite: 2606]