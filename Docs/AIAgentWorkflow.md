# AIAgentWorkflow.md

**Version: 0.89.0-Beta**
**Date: 2025-09-16**

---
### --- Revision History ---
## [0.89.0-Beta] - 2025-09-16
### Added
# - Added Principle 16 (Principle of Incremental Change) to formalize
#   [cite_start]the practice of breaking down large changes into small, verifiable steps. [cite: 2388-2391]
# - Added Protocol 2.3 (Architectural Design Protocol) to formalize the
#   [cite_start]iterative "propose-critique-refine" cycle for new architectural patterns. [cite: 2395-2398]
### Changed
# - Amended Protocol 1.3 (Context Checkpoint) to make the AI co-responsible
#   for initiating a checkpoint if it detects internal confusion.
# - Amended Protocol 2.6 (Implementation Plan) to include an optional
#   "Executive Summary" for multi-file plans and a mandatory "Backward
#   Compatibility & Impact Analysis" item in the Pre-Flight Check.
# - Amended Protocol 6.3 (Error Analysis Protocol) to require a mandatory
#   cross-reference to Principle 3 (Trust the User's Diagnostics).
# - Renumbered protocols in Part II, Section 2, and updated all internal
#   cross-references to maintain document consistency.
## [0.86.1-Beta] - 2025-09-15
### Changed
# - Clarified Protocol 2.5 to describe the implementation plan delivery
#   [cite_start]method more accurately (content within a code block). [cite: 40]
# - Strengthened Protocol 3.2.4 with explicit examples for substituting
#   [cite_start]both opening and closing internal code fences. [cite: 41]
## [0.86.0-Beta] - 2025-09-14
### Changed
# - Clarified Protocol 1.7 to describe the role of the
#   CONTEST_INPUT_DIR environment variable and to correctly list the
#   [cite_start]`Logs/` and `data/` subdirectories. [cite: 42]
## [0.70.0-Beta] - 2025-09-13
### Added
# - Added Protocol 2.5.1 (Post-Plan-Delivery Prompt Protocol) to
#   mandate that the AI must immediately prompt for plan approval after
#   delivering an implementation plan file. [cite_start]This corrects a recurring AI process error. [cite: 43-44]
## [0.69.0-Beta] - 2025-09-13
### Changed
# - Restored the detailed, six-part list of required sections to
#   Protocol 2.5 (Implementation Plan), including the full Pre-Flight
#   Check. [cite_start]This corrects a regression from v0.68.0-Beta. [cite: 44-45]
## [0.68.0-Beta] - 2025-09-13
### Added
# - Added Protocol 4.5 (Standardized Keyword Prompts) to mandate a
#   [cite_start]consistent `Please <ACTION> by providing the prompt <PROMPT>.` format. [cite: 45]
### Changed
# - Rewrote Protocol 2.5 (Implementation Plan) to be delivered as a
#   [cite_start]standalone `.md` file, confirmed with a `Ready` keyword. [cite: 46]
# - Updated Protocols 2.7, 4.4, 6.3, and 6.9 to be consistent with the
#   [cite_start]new standardized prompt and plan delivery protocols. [cite: 47]
## [0.67.0-Beta] - 2025-09-13
### Changed
# - Clarified the Task Execution Workflow in Section 2 with a detailed
#   preamble describing the mandatory, user-gated state machine sequence
#   [cite_start](Approved -> Context Lock-In -> Confirmed -> Delivery). [cite: 48]
## [0.66.0-Beta] - 2025-09-13
### Added
# - Added Protocol 6.9 (Context Lock-In Protocol) as a proactive
#   safeguard against context loss. It requires the AI to state its
#   context and the user to confirm with `Confirmed` before any
#   [cite_start]state-altering action can proceed. [cite: 49-50]
## [0.65.0-Beta] - 2025-09-13
### Changed
# - Amended Protocol 2.5 (Implementation Plan) to mandate a more robust
#   delivery format. The plan's sections must now use bolded headers
#   instead of a markdown list, and the embedded `diff` verification
#   must be enclosed in a `diff`-specified code block to prevent
#   [cite_start]UI rendering errors. [cite: 51-52]
## [0.64.0-Beta] - 2025-09-12
### Added
# - Added a mandatory "Surgical Change Verification (`diff`)" section
#   to Protocol 2.5 (Implementation Plan) to make adherence to
#   [cite_start]Principle 9 (Surgical Modification) verifiable. [cite: 53]
### Changed
# - Rephrased the "Surgical Modification Adherence Confirmation" step
#   [cite_start]in Protocol 2.5 to refer to the new `diff` section. [cite: 54]
## [0.63.0-Beta] - 2025-09-11
### Added
# - Added a new step to Protocol 6.3 (Error Analysis Protocol) to
#   require a proposal to amend the workflow if it is found to be
#   [cite_start]the root cause of an error. [cite: 55]
## [0.62.0-Beta] - 2025-09-09
### Added
# - Added a mandatory "Surgical Modification Adherence Confirmation"
#   [cite_start]step to Protocol 2.5 to make the execution contract more explicit. [cite: 56]
# - Added a mandatory post-delivery verification statement to Protocol 4.4
#   [cite_start]to enforce compliance with Principle 9. [cite: 57]
## [0.61.0-Beta] - 2025-09-09
### Added
# - Added a mandatory self-verification step to Protocol 2.5 (Implementation Plan)
#   [cite_start]and Protocol 6.3 (Error Analysis Protocol) to improve compliance. [cite: 57]
## [0.60.3-Beta] - 2025-09-09
### Changed
# - Modified Protocol 3.2.4 to require a unique `cla-bundle` specifier
#   [cite_start]for markdown file delivery to improve robustness. [cite: 58]
## [0.60.2-Beta] - 2025-09-09
### Added
# - Added Protocol 3.2.6 (Post-Delivery Protocol Verification) to require
#   [cite_start]a mandatory self-verification check after every file delivery. [cite: 59]
## [0.60.1-Beta] - 2025-09-09
### Changed
# - Strengthened Protocol 7.6 (Systemic Bug Eradication Protocol) to
#   [cite_start]require the AI to explicitly state the search method used for an audit. [cite: 60]
## [0.60.0-Beta] - 2025-09-08
### Added
# - Added Principle 15 (Principle of Centralized Configuration) to mandate
#   [cite_start]that configuration is read in one place and passed as parameters. [cite: 61]
# - Added Protocol 6.8 (External System Interference Protocol) to formalize
#   [cite_start]the process for diagnosing errors caused by external tools like Git or OneDrive. [cite: 62]
## [0.59.1-Beta] - 2025-09-03
### Changed
# - Corrected an internal documentation reference to point to the correct
#   [cite_start]user guide filename. [cite: 63]
## [0.59.0-Beta] - 2025-09-03
### Added
# - Added Protocol 7.6 (Systemic Bug Eradication Protocol) to formalize
#   [cite_start]the process of auditing for and fixing systemic bugs. [cite: 64]
# - Added a mandatory "Request Diagnostic Output" step to Protocol 6.3
#   [cite_start](Error Analysis Protocol) to improve diagnostic efficiency. [cite: 65]
### Changed
# - Strengthened Principle 9 (Surgical Modification) to explicitly forbid
#   [cite_start]unauthorized stylistic refactoring and define a process for proposing such changes. [cite: 66]
# [cite_start]- Clarified Protocol 2.7 (Approval) to require the exact, literal string `Approved`. [cite: 67]
# - Clarified Protocol 4.4 (Confirmed File Delivery Protocol) to require
#   [cite_start]the exact, literal string `Acknowledged`. [cite: 68]
## [0.58.0-Beta] - 2025-09-02
### Changed
# - Strengthened Principle 9 (Surgical Modification) to explicitly forbid
#   [cite_start]unauthorized refactoring and define a process for proposing changes. [cite: 69]
# [cite_start]- Clarified Protocol 2.7 (Approval) to require the exact, literal string `Approved`. [cite: 70]
# - Clarified Protocol 4.4 (Confirmed File Delivery Protocol) to require
#   [cite_start]the exact, literal string `Acknowledged`. [cite: 71]
## [0.57.1-Beta] - 2025-09-01
### Changed
# - Clarified Protocol 3.2.1 to explicitly state that "bundles" are
#   [cite_start]only for user-to-AI state initializations. [cite: 72]
# - Updated Protocol 3.2.5 to define the precise, literal pattern
#   [cite_start]for citation tags and to note that it does not include backticks. [cite: 73]
## [0.57.0-Beta] - 2025-09-01
### Changed
# - Renamed file from WorkingwithGemini.md to AIAgentWorkflow.md to
#   [cite_start]clarify its purpose as the AI's technical specification. [cite: 74]
# [cite_start]- Updated the introduction to reference the new WorkflowUserGuide.md. [cite: 75]
## [0.56.31-Beta] - 2025-09-01
### Added
# - Added Protocol 7.6 (Systemic Bug Eradication Protocol) to formalize
#   [cite_start]the process of auditing for and fixing systemic bugs. [cite: 76]
# - Added a rule to Protocol 3.2 requiring the removal of all internal
#   [cite_start]citation tags from delivered documents. [cite: 77]
### Changed
# - Rewrote Protocol 2.9.1 to align the documentation delivery workflow
#   with the code delivery workflow, concluding the task after the user's
#   [cite_start]"Acknowledged" response. [cite: 78]
# [cite_start]- Removed all internal [cite] tags from the document content. [cite: 79]
## [0.55.13-Beta] - 2025-08-31
### Changed
# - Updated Protocol 2.9.1 to require a final user acknowledgment
#   [cite_start]after a documentation file (.md) has been delivered. [cite: 80]
## [0.55.7-Beta] - 2025-08-30
### Added
# - Added Principle 11 ("The Log is the Ground Truth") to clarify how to
#   [cite_start]handle factually incorrect data within a log file. [cite: 81]
# - Added Protocol 3.7 (Temporary Column Preservation Protocol) to prevent
#   [cite_start]the accidental deletion of intermediate data columns during processing. [cite: 82]
# - Added Protocol 5.6 (Custom ADIF Exporter Protocol) to formalize the
#   [cite_start]new, pluggable architecture for contest-specific ADIF generation. [cite: 83]
### Changed
# [cite_start]- Renumbered subsequent principles in Part I. [cite: 84]
## [0.52.22-Beta] - 2025-08-27
### Changed
# - Revised Protocol 5.4 to recommend `prettytable` for complex,
#   multi-table reports and designate `tabulate` for simpler,
#   [cite_start]single-table use cases. [cite: 84]
## [0.52.21-Beta] - 2025-08-27
### Changed
# - Strengthened Principle 9 (Surgical Modification) to explicitly
#   [cite_start]forbid unauthorized stylistic refactoring. [cite: 85]
### Added
# - Added Protocol 7.5 (Tool Suitability Re-evaluation Protocol) to
#   [cite_start]formalize the process of handling unsuitable third-party tools. [cite: 86]
## [0.52.20-Beta] - 2025-08-26
### Added
# - Added a mandatory "Affected Modules Checklist" to Protocol 2.5 to
#   [cite_start]make Principle 7 (Assume Bugs are Systemic) more robust. [cite: 87]
## [0.49.2-Beta] - 2025-08-25
### Added
# - Added Protocol 7.4 (Prototype Script Development Protocol) to formalize
#   [cite_start]the development workflow for prototype scripts. [cite: 88]
### Changed
# - Clarified Protocol 1.7 to define the special status of the
#   [cite_start]`test_code/` directory. [cite: 89]
## [0.49.1-Beta] - 2025-08-25
### Added
# - Added Protocol 2.9.1 (Task Type Verification) to clarify when it is
#   appropriate to propose a verification command, preventing errors when
#   [cite_start]a task modifies a documentation file. [cite: 90]
## [0.49.0-Beta] - 2025-08-25
### Added
# - Added Protocol 2.8.1 (Post-Execution Refinement Protocol) to clarify
#   [cite_start]the workflow for handling incomplete fixes. [cite: 91]
# - Added Protocol 5.5 (Component Modernization Protocol) to formalize
#   [cite_start]the process of upgrading and deprecating legacy components. [cite: 92]
# - Added a mandatory "Request Diagnostic Output" step to Protocol 6.3
#   [cite_start](Error Analysis Protocol) to improve diagnostic efficiency. [cite: 93]
### Changed
# [cite_start]- Renumbered subsequent protocols in the Task Execution Workflow. [cite: 94]
## [0.48.2-Beta] - 2025-08-25
### Added
# - Added Protocol 5.4 to formalize the use of the `tabulate` library
#   [cite_start]for generating all text-based tables. [cite: 95]
### Changed
# - Clarified Protocol 3.2.4 to explain the reasoning behind the
#   [cite_start]__CODE_BLOCK__ substitution for markdown file delivery. [cite: 96]
## [0.48.1-Beta] - 2025-08-24
### Changed
# - Amended Protocol 2.1 (Task Initiation) to require a mandatory check
#   [cite_start]for an established session version number before proceeding. [cite: 97]
# - Clarified Protocol 3.4.3 (Update Procedure) to explicitly forbid
#   [cite_start]unauthorized changes to major or minor version numbers. [cite: 98]
## [0.48.0-Beta] - 2025-08-24
### Changed
# - Merged the Pre-Flight Check (2.6) into the Implementation Plan
#   [cite_start]protocol (2.5) to reflect the new, more detailed planning process. [cite: 99]
# [cite_start]- Renumbered subsequent protocols in the Task Execution Workflow. [cite: 100]
## [0.47.6-Beta] - 2025-08-23
### Added
# - Added clarification to Protocol 1.5 that version numbers are only
#   [cite_start]updated if a file's content is modified. [cite: 101]
## [0.44.0-Beta] - 2025-08-23
### Changed
# - Modified Protocol 3.2.4 to require substituting embedded code
#   [cite_start]fences (```) with __CODE_BLOCK__ for markdown file delivery. [cite: 102]
## [0.43.0-Beta] - 2025-08-23
### Added
# - Added Protocol 6.6 (Self-Correction on Contradiction) to mandate a
#   full stop and re-evaluation upon detection of logically impossible
#   [cite_start]or contradictory analytical results. [cite: 103]
# - Added Protocol 6.7 (Simplified Data Verification) to formalize the
#   [cite_start]use of user-provided, simplified data files for debugging. [cite: 104]
### Changed
# - Amended Principle 5 (Technical Diligence) to explicitly require
#   [cite_start]halting when a tool produces inconsistent results over multiple attempts. [cite: 105]
# - Clarified Protocol 6.3 (Error Analysis Protocol) to emphasize that
#   a failure to provide a correct analysis after a user's correction
#   [cite_start]constitutes a new, more severe error. [cite: 106]
## [0.42.0-Beta] - 2025-08-20
### Added
# - Added Protocol 2.3 (Visual Prototype Protocol) to formalize the use
#   [cite_start]of prototype scripts for complex visual changes. [cite: 107]
### Changed
# - Renumbered subsequent protocols in the Task Execution Workflow and
#   [cite_start]updated internal cross-references. [cite: 108]
## [0.38.0-Beta] - 2025-08-19
### Added
# - Added Protocol 2.3 (Baseline Consistency Check) to require plan
#   [cite_start]validation against the definitive state before the plan is proposed. [cite: 109]
### Changed
# [cite_start]- Renumbered subsequent protocols in the Task Execution Workflow. [cite: 110]
# [cite_start]- Updated internal cross-references to match the new numbering. [cite: 111]
## [0.37.1-Beta] - 2025-08-18
### Changed
# - Refined the Markdown File Delivery Protocol (3.2.4) to require
#   enclosing the entire file content in a plaintext code block for
#   [cite_start]easier copying. [cite: 112]
## [0.37.0-Beta] - 2025-08-18
### Added
# - Added Principle 13 to formalize the process of classifying data
#   [cite_start]conflicts as either data errors or complex rule requirements. [cite: 113]
# - Added Protocol 2.8 to the Task Execution Workflow, requiring the AI
#   [cite_start]to propose a verification command after a task is complete. [cite: 114]
## [0.36.12-Beta] - 2025-08-17
### Changed
# - Integrated clarifications from user feedback into Protocol 1.2,
#   [cite_start]Principle 9, and Protocol 3.4.3 to make the document self-contained. [cite: 115]
### Added
# - Added Protocol 6.5 (Bundle Integrity Check Protocol) to define a
#   [cite_start]procedure for handling logical anomalies within initialization bundles. [cite: 116]
## [0.36.11-Beta] - 2025-08-16
### Added
# - Added Protocol 1.7 (Project Structure Onboarding) to provide bootstrap
#   [cite_start]architectural context after an initialization. [cite: 117]
# - Added Protocol 6.4 (Corrupted User Input Protocol) to define a
#   [cite_start]formal procedure for handling malformed user files. [cite: 118]
## [0.36.10-Beta] - 2025-08-16
### Added
# - Added the new, top-priority Principle 1 for Context Integrity, which
#   [cite_start]mandates a full state reset upon detection of context loss. [cite: 119]
### Changed
# [cite_start]- Renumbered all subsequent principles accordingly. [cite: 120]
## [0.36.9-Beta] - 2025-08-15
### Added
# - Added rule 3.2.4 to mandate the substitution of markdown code fences
#   [cite_start]with __CODE_BLOCK__ for proper web interface rendering. [cite: 120]
## [0.36.4-Beta] - 2025-08-15
### Changed
# - Clarified Principle 8 (Surgical Modification) to explicitly require
#   [cite_start]the preservation of revision histories. [cite: 121]
### Added
# - Added Protocol 1.6 (Session Versioning Protocol) to establish the
#   [cite_start]current version series at the start of a task. [cite: 122]
## [0.36.3-Beta] - 2025-08-15
### Changed
# [cite_start]- Merged missing protocols from v0.36.0-Beta to create a complete document. [cite: 123]
# [cite_start]- Synthesized a new, authoritative Versioning Protocol based on user clarification. [cite: 124]
# [cite_start]- Reorganized the document to separate workflow protocols from software design patterns. [cite: 125]
## [0.36.2-Beta] - 2025-08-15
### Changed
# - Overhauled the Task Execution and File Delivery protocols to formalize
#   [cite_start]the new, more robust, state-machine workflow with per-file acknowledgments. [cite: 126]
## [0.36.1-Beta] - 2025-08-15
### Changed
# - Amended Protocol 2.2 to require the file's baseline version
#   [cite_start]number in all implementation plans. [cite: 127]
## [0.36.0-Beta] - 2025-08-15
### Changed
# - Replaced the "Atomic State Checkpoint Protocol" (1.2) with the new
#   "Definitive State Reconciliation Protocol" which uses the last
#   [cite_start]Definitive State Initialization as its baseline. [cite: 128]
# - Amended Protocol 1.5 to add an explicit step for handling
#   [cite_start]documents that require no changes. [cite: 129]
---

This document is the definitive technical specification for the AI agent's behavior and the standard operating procedures for the collaborative development of the Contest Log Analyzer.

**The primary audience for this document is the Gemini AI agent.** It is a machine-readable set of rules and protocols.

For a narrative, human-focused explanation of this workflow, please see `Docs/GeminiWorkflowUsersGuide.md`.
---
## Part I: Core Principles

These are the foundational rules that govern all interactions and analyses.

1.  **Context Integrity is Absolute.** The definitive project state is established by the baseline `*_bundle.txt` files and evolves with every acknowledged file change. Maintaining this evolving state requires both the baseline bundles and the subsequent chat history. If I detect that the baseline `*_bundle.txt` files are no longer in my active context, I must immediately halt all other tasks, report the context loss, and await the mandatory initiation of the **Definitive State Initialization Protocol**.
2.  **Protocol Adherence is Paramount.** All protocols must be followed with absolute precision. Failure to do so invalidates the results and undermines the development process. There is no room for deviation unless a deviation is explicitly requested by the AI and authorized by the user.
3.  **Trust the User's Diagnostics.** When the user reports a bug or a discrepancy, their description of the symptoms and their corrections should be treated as the ground truth. The AI's primary task is to find the root cause of those specific, observed symptoms, not to propose alternative theories.
4.  **No Unrequested Changes.** The AI will only implement changes explicitly requested by the user. All suggestions for refactoring, library changes, or stylistic updates must be proposed and approved by the user before implementation.
5.  **Technical Diligence Over Conversational Assumptions.** Technical tasks are not conversations. Similar-looking prompts do not imply similar answers. Each technical request must be treated as a unique, atomic operation. The AI must execute a full re-computation from the current project state for every request, ignoring any previous results or cached data. **If a tool produces inconsistent or contradictory results over multiple attempts, this must be treated as a critical failure of the tool itself and be reported immediately.**
6.  **Prefer Logic in Code, Not Data.** The project's design philosophy is to keep the `.json` definition files as simple, declarative maps. All complex, conditional, or contest-specific logic should be implemented in dedicated Python modules.
7.  **Assume Bugs are Systemic.** When a bug is identified in one module, the default assumption is that the same flaw exists in all other similar modules. The AI must perform a global search for that specific bug pattern and fix all instances at once.
8.  **Reports Must Be Non-Destructive.** Specialist report scripts must **never** modify the original `ContestLog` objects they receive. All data filtering or manipulation must be done on a temporary **copy** of the DataFrame.
9.  **Principle of Surgical Modification.** All file modifications must be treated as surgical operations. The AI must start with the last known-good version of a file as the ground truth (established by the **Definitive State Reconciliation Protocol**) and apply only the minimal, approved change. Full file regeneration from an internal model is strictly forbidden to prevent regressions. **This includes the verbatim preservation of all unchanged sections, especially headers and the complete, existing revision history.** This principle explicitly forbids stylistic refactoring (e.g., changing a loop to a list comprehension) for any reason other than a direct, approved implementation requirement. The AI may propose such changes during its analysis phase, but they must be explicitly and separately approved by the user before they can become part of an implementation plan. Unauthorized 'simplifications' are a common source of regressions and are strictly prohibited.
10. **Primacy of Official Rules.** The AI will place the highest emphasis on analyzing the specific data, context, and official rules provided, using them as the single source of truth.
11. **The Log is the Ground Truth.** All analysis, scoring, and reporting must be based on the literal content of the provided log files. The analyzer's function is not to correct potentially erroneous data (e.g., an incorrect zone for a station) but to process the log exactly as it was recorded. Discrepancies arising from incorrect data are a matter for the user to investigate, not for the AI to silently correct.
12. **Citation of Official Rules.** When researching contest rules, the AI will prioritize finding and citing the **official rules from the sponsoring organization**.
13. **Uniqueness of Contest Logic.** Each contest's ruleset is to be treated as entirely unique. Logic from one contest must **never** be assumed to apply to another.
14. **Classify Ambiguity Before Action.** When the AI discovers a conflict between the data (e.g., in a `.dat` or `.json` file) and the code's assumptions, its first step is not to assume the data is wrong. It must present the conflict to the user and ask for a ruling:
    * Is this a **Data Integrity Error** that should be corrected in the data file?
    * Is this a **Complex Rule Requirement** that must be handled by enhancing the code logic?
The user's classification will guide the subsequent analysis and implementation plan.
15. **Principle of Centralized Configuration.** Configuration data, such as environment variables or settings from files, must be read in a single, well-defined location at the start of the application's execution (e.g., `main_cli.py`). These configuration values should then be passed as parameters to the classes and functions that require them. Modules and classes should not read environment variables directly.
16. **Principle of Incremental Change.** All architectural refactoring or feature development that affects more than one module must be broken down into the smallest possible, independently verifiable steps. Each step must be followed by a verification checkpoint (e.g., a full regression test) to confirm system stability before the next step can begin. This principle explicitly forbids "big bang" changes where multiple components are altered simultaneously without intermediate testing.
---
## Part II: Standard Operating Protocols

These are the step-by-step procedures for common, day-to-day development tasks.

### 1. Session Management

1.1. **Onboarding Protocol.** The first action for any AI agent upon starting a session is to read this document in its entirety, acknowledge it, and ask any clarifying questions.
1.2. **Definitive State Reconciliation Protocol.**
    1.  **Establish Baseline**: The definitive state is established by first locating the most recent **Definitive State Initialization Protocol** in the chat history. The files from this initialization serve as the absolute baseline.
    2.  **Scan Forward for Updates**: After establishing the baseline, the AI will scan the chat history *forward* from that point to the present.
    3.  **Identify Latest Valid Version**: The AI will identify the **latest** version of each file that was part of a successfully completed and mutually acknowledged transaction (i.e., file delivery, AI confirmation, and user acknowledgment). This version supersedes the baseline version.
    4.  **Handle Ambiguity**: If any file transaction is found that was initiated but not explicitly acknowledged by the user, the AI must halt reconciliation, report the ambiguous file, and await user clarification.
1.3. **Context Checkpoint Protocol.** If the AI appears to have lost context, the user can issue a **Context Checkpoint**. The AI is also responsible for initiating a Context Checkpoint if it detects potential internal confusion, contradictory states in its own reasoning, or if the user's prompts suggest a fundamental misunderstanding of the current task.
    1.  The user begins with the exact phrase: **"Gemini, let's establish a Context Checkpoint."**
    2.  The user provides a brief, numbered list of critical facts.
1.4. **Definitive State Initialization Protocol.** This protocol serves as a "hard reset" of the project state.
    1.  **Initiation:** The user or AI requests a "Definitive State Initialization."
    2.  **Agreement:** The other party agrees to proceed.
    3.  **File Upload:** The user creates and uploads new, complete `project_bundle.txt`, `documentation_bundle.txt`, and `data_bundle.txt` files.
    4.  **State Purge:** The AI discards its current understanding of the project state.
    5.  **Re-Initialization:** The AI establishes a new definitive state based *only* on the new bundles.
    6.  **Verification and Acknowledgment:** The AI acknowledges the new state and provides a complete list of all files extracted from the bundles.
1.5. **Document Review and Synchronization Protocol.** This protocol is used to methodically review and update all project documentation (`.md` files) to ensure it remains synchronized with the code baseline.
    1.  **Initiate Protocol and List Documents:** The AI will state that the protocol is beginning and will provide a complete list of all documents to be reviewed (`Readme.md` and all `.md` files in the `Docs` directory).
    2.  **Begin Sequential Review:** The AI will then loop through the list, processing one document at a time using the following steps:
        * **Step A: Identify and Request.** State which document is next and ask for permission to proceed.
        * **Step B: Analyze.** Upon approval, perform a full "a priori" review of the document against the current code baseline and provide an analysis of any discrepancies.
        * **Step C (Changes Needed): Propose Plan.** If discrepancies are found, ask if the user wants an implementation plan to update the document.
        * **Step D: Provide Plan.** Upon approval, provide a detailed, surgical implementation plan for the necessary changes.
        * **Step E: Request to Proceed.** Ask for explicit permission to generate the updated document.
        * **Step F: Deliver Update.** Upon approval, perform a **Pre-Flight Check**, explicitly state that the check is complete, and then deliver the updated document.
        * **Step G (No Changes Needed):** If the analysis in Step B finds no discrepancies, the AI will state that the document is already synchronized and ask for the user's confirmation to proceed to the next document.
    3.  **Completion:** After the final document has been processed, the AI will state that the protocol is complete.
    4.  **Version Update on Modification Only Clarification**: A file's version number and revision history will only be updated if its content requires changes to be synchronized with the project baseline. Documents that are found to be already synchronized during the review will not have their version numbers changed.

1.6. **Session Versioning Protocol.** At the start of a new development task, the user will state the current version series (e.g., 'We are working on Version 0.36.x-Beta'). All subsequent file modifications for this and related tasks must use this version series, incrementing the patch number as needed.
1.7. **Project Structure Onboarding.** After a state initialization, the AI will confirm its understanding of the high-level project architecture.
The `Logs/` and `data/` directories are located within a root path defined by the `CONTEST_INPUT_DIR` environment variable.
* `contest_tools/`: The core application library.
* `contest_tools/reports/`: The "plug-in" directory for all report modules.
* `contest_tools/contest_definitions/`: Data-driven JSON definitions for each contest.
* `Docs/`: All user and developer documentation.
* `test_code/`: Utility and prototype scripts not part of the main application. These scripts are not held to the same change control and documentation standards (e.g., a revision history is not required).
* `Logs/`: Contains all Cabrillo log files for analysis.
* `data/`: Required data files (e.g., `cty.dat`).
### 2. Task Execution Workflow
This workflow is a formal state machine that governs all development tasks, from initial request to final completion.

> **No File Delivery Without an Approved Plan:** All file modifications or creations must be detailed in a formal **Implementation Plan** that you have explicitly approved with the literal string `Approved`. I will not deliver any file that is not part of such a plan.
>
> **The Mandatory Lock-In Sequence:** Your `Approved` command will immediately trigger the **Context Lock-In Protocol**. The sequence for every task involving file delivery is as follows:
> 1.  I provide an **Implementation Plan**.
> 2.  You respond with `Approved`.
> 3.  I respond with the mandatory **Context Lock-In Statement**.
> 4.  You respond with `Confirmed`.
> 5.  Only then will I begin delivering the files as specified in the plan, following the **Confirmed File Delivery Protocol**.
>
> This sequence is the standard operating procedure for all tasks.

2.1. **Task Initiation**: The user provides a problem, feature request, or document update and requests an analysis. Before proceeding, the AI must verify that a session version series (as defined in Protocol 1.6) has been established. If it has not, the AI must ask for it before providing any analysis.
2.2. **Analysis and Discussion**: The AI provides an initial analysis. The user and AI may discuss the analysis to refine the understanding of the problem.
2.3. **Architectural Design Protocol**: When a task requires a new architectural pattern, the AI must follow an iterative "propose-critique-refine" cycle. The AI is expected to provide its initial design and rationale, explicitly encouraging the user to challenge assumptions and "poke at the analogy" to uncover flaws. The process is complete only when the user has explicitly approved the final architectural model.
2.4. **Visual Prototype Protocol.** This protocol is used to resolve ambiguity in tasks involving complex visual layouts or new, hard-to-describe logic before a full implementation is planned.
    1.  **Initiation:** The AI proposes or the user requests a prototype to clarify a concept.
    2.  **Agreement:** Both parties agree to create the prototype.
    3.  **Prototype Delivery:** The AI delivers a standalone, self-contained script. The script must use simple, hardcoded data and focus only on demonstrating the specific concept in question.
    4.  **Prototype Usability Clause:** For visual prototypes using Matplotlib, the script must save the output to a file and then immediately display the chart on-screen using `plt.show()` for ease of verification.
    5.  **Review and Iteration:** The user reviews the prototype's output and provides feedback. This step can be repeated until the prototype is correct.
    6.  **Approval:** The user gives explicit approval of the final prototype. This approval serves as the visual and logical ground truth for the subsequent implementation plan.
2.5. **Baseline Consistency Check.** Before presenting an implementation plan, the AI must perform and explicitly state the completion of a "Baseline Consistency Check." This check verifies that all proposed actions (e.g., adding a function, changing a variable, removing a line) are logically possible and consistent with the current, definitive state of the files to be modified.
2.6. **Implementation Plan**: To bypass UI rendering issues, the **content** of all Implementation Plans will be delivered inside a single, `cla-bundle`-specified code block. This procedure simulates the delivery of an `implementation_plan.md` file and ensures the content can be copied as a single unit.
    * **Executive Summary (Optional for Multi-File Plans)**: For plans that modify more than one file, the document may begin with a brief, high-level description of the task's overall goal and the role each file in this plan plays in achieving it.
    1.  The AI will state its readiness and ask the user to confirm they are ready to receive the file. The prompt will follow **Protocol 4.5** and require the keyword `Ready`.
    2.  Upon receiving the `Ready` keyword, the AI will deliver the plan's content using the `cla-bundle` protocol.
    3.  The plan itself must be a comprehensive document containing the following sections for each file to be modified, formatted with bolded headers:
        **1.  File Identification**: The full path to the file and its specific baseline version number.
        **2.  Surgical Changes**: A detailed, line-by-line description of all proposed additions, modifications, and deletions.
        **3.  Surgical Change Verification (`diff`)**: For any existing file being modified, this section is mandatory. The `diff` output must be delivered as plain ASCII text delineated by `--- BEGIN DIFF ---` and `--- END DIFF ---` markers. This section is not applicable for new files.
        **4.  Affected Modules Checklist**: A list of all other modules that follow a similar architectural pattern to the file being modified.
        **5.  Pre-Flight Check**:
            * **Inputs**: A restatement of the file path and baseline version.
            * **Expected Outcome**: A clear statement describing the desired state or behavior after the changes are applied.
            * **Mental Walkthrough Confirmation**: A statement affirming that a mental walkthrough of the logic will be performed before generating the file.
            * **State Confirmation Procedure**: An affirmation that the mandatory confirmation prompt will be included with the file delivery.
            * **Backward Compatibility & Impact Analysis**: I have analyzed the potential impact of these changes on other modules and confirm this plan will not break existing, unmodified functionality.
            * **Surgical Modification Adherence Confirmation**: I confirm that the generated file will contain *only* the changes shown in the Surgical Change Verification (`diff`) section above, ensuring 100% compliance with Principle 9.
            * **Syntax Validation Confirmation**: For all Python files (`.py`), I will perform an automated syntax validation check.
        **6.  Post-Generation Verification.** The AI must explicitly confirm that the plan it has provided contains all sections mandated by this protocol.
**2.6.1. Post-Plan-Delivery Prompt Protocol.** Immediately after delivering an `implementation_plan.md` file and providing the post-delivery verification (per Protocol 3.2.6), the AI's next and only action **must** be to issue the standardized prompt for plan approval, requiring the keyword `Approved`. This protocol ensures a direct and mandatory transition to the Approval state (Protocol 2.8).
2.7. **Plan Refinement**: The user reviews the plan and may request changes or refinements. The AI provides a revised plan, repeating this step as necessary.
2.8. **Approval**: The user provides explicit approval of the final implementation plan. Instructions, clarifications, or new requirements provided after a plan has been proposed do not constitute approval; they will be treated as requests for plan refinement under Protocol 2.7. The AI will only proceed to the Execution state upon receiving the **exact, literal string `Approved`**.
2.9. **Execution**: Upon approval, the AI will proceed with the **Confirmed File Delivery Protocol (4.4)**.
2.9.1. **Post-Execution Refinement Protocol.** If a user acknowledges a file delivery but subsequently reports that the fix is incomplete or incorrect, the task is not considered complete. The workflow immediately returns to **Protocol 2.2 (Analysis and Discussion)**. This initiates a new analysis loop within the context of the original task, culminating in a new implementation plan to address the remaining issues. The task is only complete after **Protocol 2.10 (Propose Verification Command)** is successfully executed for the *final, correct* implementation.
2.10. **Propose Verification Command**: After the final file in an implementation plan has been delivered and acknowledged by the user, the AI's final action for the task is to propose the specific command-line instruction(s) the user should run to verify that the bug has been fixed or the feature has been implemented correctly.
**2.10.1: Task Type Verification.** This protocol applies **only** if the final file modified was a code or data file (e.g., `.py`, `.json`, `.dat`). If the final file was a documentation or text file (e.g., `.md`), a verification command is not applicable. The task is successfully concluded once the user provides the standard 'Acknowledged' response for the final documentation file delivered as part of the implementation plan.
### 3. File and Data Handling

3.1. **Project File Input.** All project source files and documentation will be provided for updates in a single text file called a **project bundle**, or pasted individually into the chat. The bundle uses a simple text header to separate each file: `--- FILE: path/to/file.ext ---`
3.2. **AI Output Format.** When the AI provides updated files, it must follow these rules to ensure data integrity.
    1.  **Single File Per Response**: Only one file will be delivered in a single response. The "bundle" terminology (e.g., `project_bundle.txt`) refers exclusively to the user-provided files used for a Definitive State Initialization; all file deliveries from the AI are strictly individual.
    2.  **Raw Source Text**: The content inside the delivered code block must be the raw source text of the file.
    3.  **Code File Delivery**: For code files (e.g., `.py`, `.json`), the content will be delivered in a standard fenced code block with the appropriate language specifier.
    4.  **Markdown File Delivery**: To prevent the user interface from rendering markdown and to provide a "Copy" button, the entire raw content of a documentation file (`.md`) must be delivered inside a single, **`cla-bundle`**-specified code block.
        * **Internal Code Fence Substitution**: To prevent the `cla-bundle` block from terminating prematurely, **all** internal three-backtick code fences must be replaced with the `__CODE_BLOCK__` placeholder. This rule is absolute and applies to both opening and closing fences.
        * **Example (Opening Fence)**: `__CODE_BLOCK__python` **must be replaced with** `__CODE_BLOCK__python`.
        * **Example (Closing Fence)**: `__CODE_BLOCK__` **must be replaced with** `__CODE_BLOCK__`.
        * **Clarification**: This substitution is a requirement of the AI's web interface. The user will provide files back with standard markdown fences, which is the expected behavior.
    5.  **Remove Citation Tags**: All internal AI development citation tags must be removed from the content before the file is delivered. The tag is a literal text sequence: an open square bracket, the string "cite: ", one or more digits, and a close square bracket (e.g.,). This pattern does not include Markdown backticks.
    6.  **Post-Delivery Protocol Verification.** Immediately following any file delivery, the AI must explicitly state which sub-protocol from Section 3.2 it followed and confirm that its last output was fully compliant.
3.3. **File and Checksum Verification.**
    1.  **Line Endings:** The user's file system uses Windows CRLF (`\r\n`). The AI must correctly handle this conversion when calculating checksums.
    2.  **Concise Reporting:** The AI will either state that **all checksums agree** or will list the **specific files that show a mismatch**.
    3.  **Mandatory Re-computation Protocol:** Every request for a checksum comparison is a **cache-invalidation event**. The AI must discard all previously calculated checksums, re-establish the definitive state, re-compute the hash for every file, and perform a literal comparison.
3.4. **Versioning Protocol.** This protocol defines how file versions are determined and updated.
    1.  **Format**: The official versioning format is `x.y.z-Beta`, where `x` is the major version, `y` is the minor version, and `z` is the patch number.
    2.  **Source of Truth**: The version number for any given file is located within its own content.
        * **Python (`.py`) files**: Contained within a "Revision History" section in the file's docstring.
        * **JSON (`.json`) files**: Stored as the value for a `"version"` parameter.
        * **Data (`.dat`) files**: Found within a commented revision history block.
    3.  **Update Procedure**: When a file is modified, only its patch number (`z`) will be incremented; this is done on a per-file basis. Major (`x`) or minor (`y`) version changes are forbidden unless explicitly directed by the user.
    4.  **History Preservation**: All existing revision histories must be preserved and appended to, never regenerated from scratch.

3.5. **File Naming Convention Protocol.** All generated report files must adhere to the standardized naming convention: `<report_id>_<details>_<callsigns>.<ext>`.

3.6. **File Purge Protocol.** This protocol provides a clear and safe procedure for removing a file from the project's definitive state.
    1.  **Initiation**: The user will start the process with the exact phrase: "**Gemini, initiate File Purge Protocol.**" The AI will then ask for the specific file(s) to be purged.
    2.  **Confirmation**: The AI will state which file(s) are targeted for removal and ask for explicit confirmation to proceed.
    3.  **Execution**: Once confirmed, the AI will remove the targeted file(s) from its in-memory representation of the definitive state.
    4.  **Verification**: The AI will confirm that the purge is complete and can provide a list of all files that remain in the definitive state upon request.
3.7. **Temporary Column Preservation Protocol.** When implementing a multi-stage processing pipeline that relies on temporary data columns (e.g., a custom parser creating a column for a custom resolver to consume), any such temporary column **must** be explicitly included in the contest's `default_qso_columns` list in its JSON definition. The `contest_log.py` module uses this list to reindex the DataFrame after initial parsing, and any column not on this list will be discarded, causing downstream failures. This is a critical data integrity step in the workflow.
### 4. Communication

4.1. **Communication Protocol.** All AI communication will be treated as **technical writing**. The AI must use the exact, consistent terminology from the source code and protocols.

4.2. **Definition of Prefixes.** The standard definitions for binary and decimal prefixes will be strictly followed (e.g., Kilo (k) = 1,000; Kibi (Ki) = 1,024).
4.3. **Large File Transmission Protocol.** This protocol is used to reliably transmit a single large file that has been split into multiple parts.
    1.  **AI Declaration:** The AI will state its intent and declare the total number of bundles to be sent.
    2.  **State-Driven Sequence:** The AI's response for each part of the transfer must follow a strict, multi-part structure:
        1. **Acknowledge State:** Confirm understanding of the user's last prompt.
        2. **Declare Current Action:** State which part is being sent using a "Block x of y" format.
        3. **Execute Action:** Provide the file bundle.
        4. **Provide Next Prompt:** If more parts remain, provide the exact text for the user's next prompt.
    3.  **Completion:** After the final bundle, the AI will state that the task is complete.

4.4. **Confirmed File Delivery Protocol.** This protocol is used for all standard file modifications.
    1.  The AI delivers the first file from the approved implementation plan.
    2.  The AI appends the mandatory execution verification statement to the same response: "**I have verified that the file just delivered was generated by applying only the approved surgical changes to the baseline text, in compliance with Principle 9.**"
    3.  The AI appends the mandatory confirmation prompt to the end of the same response, formatted according to **Protocol 4.5**.
    4.  The user provides the **exact, literal string `Acknowledged`** as a response.
    5.  The AI proceeds to deliver the next file, repeating the process until all files from the plan have been delivered and individually acknowledged.
4.5. **Standardized Keyword Prompts.** To ensure all prompts for user action are clear and unambiguous, they must follow the exact format below:
    `Please <ACTION> by providing the prompt <PROMPT>.`
    * **`<ACTION>`**: A concise description of the action being requested (e.g., "approve the plan", "confirm the delivery").
    * **`<PROMPT>`**: The exact, literal, case-sensitive keyword required (e.g., `Approved`, `Acknowledged`, `Confirmed`, `Ready`).
---
## Part III: Project-Specific Implementation Patterns

These protocols describe specific, named patterns for implementing features in the Contest Log Analyzer software.
5.1. **Custom Parser Protocol.** For contests with highly complex or asymmetric exchanges.
    1.  **Activation**: A new key, `"custom_parser_module": "module_name"`, is added to the contest's `.json` file.
    2.  **Hook**: The `contest_log.py` script detects this key and calls the specified module.
    3.  **Implementation**: The custom parser module is placed in the `contest_specific_annotations` directory.

5.2. **Per-Mode Multiplier Protocol.** For contests where multipliers are counted independently for each mode.
    1.  **Activation**: The contest's `.json` file must contain `"multiplier_report_scope": "per_mode"`.
    2.  **Generator Logic**: This instructs the `report_generator.py` to run multiplier reports separately for each mode.
    3.  **Report Logic**: The specialist reports must accept a `mode_filter` argument.

5.3. **Data-Driven Scoring Protocol.** To accommodate different scoring methods, the `score_formula` key is available in the contest's `.json` definition. If set to `"qsos_times_mults"`, the final score will be `Total QSOs x Total Multipliers`. If omitted, it defaults to `Total QSO Points x Total Multipliers`.

5.4. **Text Table Generation Protocol.** This protocol governs the creation of text-based tables in reports, recommending the appropriate tool for the job.
    1.  **For Complex Reports, Use `prettytable`**: For any report that requires a fixed-width layout, precise column alignment, or the alignment and "stitching" of multiple tables, the **`prettytable`** library is the required standard. It offers direct, programmatic control over column widths and properties, which is essential for complex layouts.
    2.  **For Simple Reports, Use `tabulate`**: For reports that require only a single, standalone table where complex alignment with other elements is not a concern, the simpler **`tabulate`** library is a suitable alternative.
5.5. **Component Modernization Protocol.** This protocol is used to replace a legacy component (e.g., a report, a utility) with a modernized version that uses a new technology or methodology.
    1.  **Initiation**: During a **Technical Debt Cleanup Sprint**, the user or AI will identify a legacy component for modernization.
    2.  **Implementation**: An implementation plan will be created for a new module that replicates the functionality of the legacy component using the modern technology (e.g., a new report using the `plotly` library).
    3.  **Verification**: After the modernized component is approved and acknowledged, the user will run both the legacy and new versions. The AI will be asked to confirm that their outputs are functionally identical and that the new version meets all requirements.
    4.  **Deprecation**: Once the modernized component is verified as a complete replacement, the user will initiate the **File Purge Protocol (3.6)** to remove the legacy component from the definitive state.
    5.  **Example Application**: The migration of text-based reports from manual string formatting to the `tabulate` library (per Protocol 5.4) is a direct application of this modernization protocol.
5.6. **Custom ADIF Exporter Protocol.** For contests requiring a highly specific ADIF output format for compatibility with external tools (e.g., N1MM).
    1.  **Activation**: A new key, `"custom_adif_exporter": "module_name"`, is added to the contest's `.json` file.
    2.  **Hook**: The `log_manager.py` script detects this key and calls the specified module instead of the generic ADIF exporter.
    3.  **Implementation**: The custom exporter module is placed in the new `contest_tools/adif_exporters/` directory and must contain an `export_log(log, output_filepath)` function.
---
## Part IV: Special Case & Recovery Protocols

These protocols are for troubleshooting, error handling, and non-standard situations.
### 6. Debugging and Error Handling

6.1. **Mutual State & Instruction Verification.**
    1.  **State Verification**: If an instruction from the user appears to contradict the established project state or our immediate goals, the AI must pause and ask for clarification before proceeding.
    2.  **Instructional Clarity**: If a user's prompt contains a potential typo or inconsistency (e.g., a misspelled command or incorrect filename), the AI must pause and ask for clarification. The AI will not proceed based on an assumption.
    3.  **File State Request**: If a state mismatch is suspected as the root cause of an error, the AI is authorized to request a copy of the relevant file(s) from the user to establish a definitive ground truth.
6.2. **Debug "A Priori" When Stuck.** If an initial bug fix fails or the cause of an error is not immediately obvious, the first diagnostic step to consider is to add detailed logging (e.g., `logging.info()` statements, hexadecimal dumps) to the failing code path. The goal is to isolate the smallest piece of failing logic and observe the program's actual runtime state.

6.3. **Error Analysis Protocol.** When an error in the AI's process is identified, the AI must provide a clear and concise analysis. **A failure to provide a correct analysis after being corrected by the user constitutes a new, more severe error that must also be analyzed.**
    1.  **Acknowledge the Error:** State clearly that a mistake was made.
    2.  **Request Diagnostic Output:** If the user has not already provided it, the AI's immediate next step is to request the new output that demonstrates the failure (e.g., the incorrect text report or a screenshot). This output becomes the new ground truth for the re-analysis.
    3.  **Identify the Root Cause:** Explain the specific flaw in the internal process or logic that led to the error.
    4.  **Cross-Reference Core Principles:** The AI must explicitly state if a violation of Principle 3 (Trust the User's Diagnostics) was a contributing factor to the error. This includes identifying which specific principles or protocols were violated.
    5.  **Propose a Corrective Action:** Describe the specific, procedural change that will be implemented to prevent the error from recurring. If this change involves a new implementation plan, the AI must state this and then initiate the file-based delivery process defined in **Protocol 2.6**.
    6.  **Post-Analysis Verification.** The AI must explicitly confirm that the analysis it has provided contains all the steps mandated by this protocol.
    7.  **Propose Workflow Amendment**: If the root cause analysis identifies a flaw or a gap in the `AIAgentWorkflow.md` protocols themselves, I must immediately propose a separate implementation plan to amend the workflow document to prevent that class of error from recurring.
6.4. **Corrupted User Input Protocol.** This protocol defines the procedure for handling malformed or corrupted input files provided by the user.
    1.  Halt the current task immediately.
    2.  Report the specific file that contains the error and describe the nature of the error (e.g., "Cabrillo parsing failed on line X" or "Bundle is missing a file header").
    3.  Request a corrected version of the file from the user.

6.5. **Bundle Integrity Check Protocol.** This protocol is triggered during a **Definitive State Initialization** if the AI discovers logical inconsistencies within the provided bundles.
    1.  Halt the initialization process after parsing all bundles.
    2.  Report all discovered anomalies to the user. Examples include:
        * **Duplicate Filenames:** The same file path appearing in multiple bundles or multiple times in one bundle.
        * **Content Mismatch:** A file whose content appears to belong to another file (e.g., a file named `a.py` contains code clearly from `b.py`).
        * **Misplaced Files:** A file that appears to be in the wrong logical directory (e.g., a core application file located in the `Docs/` bundle).
    3.  Await user clarification and direction before completing the initialization and establishing the definitive state.
6.6. **Self-Correction on Contradiction Protocol.** This protocol is triggered when the AI produces an analytical result that is logically impossible or directly contradicts a previously stated fact or a result from another tool.
    1.  **Halt Task:** Immediately stop the current line of reasoning or task execution.
    2.  **Acknowledge Contradiction:** Explicitly state that a logical contradiction has occurred (e.g., "My last two statements are contradictory" or "The results of my analysis are logically impossible").
    3.  **Identify Trustworthy Facts:** Re-evaluate the inputs and previous steps to determine which pieces of information are most reliable (e.g., a direct check of a structured file like a JSON is more reliable than a complex parse of a semi-structured text file).
    4.  **Invalidate Flawed Analysis:** Clearly retract the incorrect statements or analysis.
    5.  **Proceed with Verification:** Continue the task using only the most trustworthy facts and methods.
6.7. **Simplified Data Verification Protocol.** This protocol is used when a tool's analysis of a complex file is in doubt or has been proven incorrect.
    1.  **Initiation:** The user has provided a simplified, ground-truth data file (e.g., a JSON or text file containing only the essential data points).
    2.  **Prioritization:** The AI must treat this new file as the highest-priority source of truth for the specific data it contains.
    3.  **Analysis:** The AI will use the simplified file to debug its own logic and resolve the discrepancy. The goal is to make the primary analysis tool's output match the ground truth provided in the simplified file.
6.8. **External System Interference Protocol.** This protocol is triggered when a file system error (e.g., `PermissionError`) is repeatable but cannot be traced to the script's own logic.
    1.  **Hypothesize External Cause:** The AI must explicitly consider and list potential external systems as the root cause (e.g., cloud sync clients like OneDrive, version control systems like Git, antivirus software).
    2.  **Propose Diagnostic Commands:** The AI must propose specific, external diagnostic commands for the user to run to verify the state of the filesystem. Examples include `git ls-files` to check tracking status or `attrib` (on Windows) to check file attributes.
    3.  **Propose Solution Based on Findings:** The implementation plan should address the external cause (e.g., adding a path to `.gitignore`) rather than adding complex, temporary workarounds to the code.
6.9. **Context Lock-In Protocol.** This protocol is a mandatory, proactive safeguard against context loss that is triggered before any action that establishes or modifies the definitive state.
    1.  **Trigger**: This protocol is triggered immediately before initiating the **Definitive State Initialization Protocol (1.4)** or executing an **Implementation Plan (2.6)**.
    2.  **AI Action (Declaration)**: Before proceeding, I must issue a single, explicit statement declaring the exact source of the information I am about to use.
        * For a new initialization: *"I am establishing a new definitive state based ONLY on the bundle files you have provided in the immediately preceding turn. I will not reference any prior chat history for file content. Please confirm to proceed."*
        * For executing a plan: *"I am about to generate files based on the Implementation Plan you approved, using the baseline versions specified in that plan. Please confirm to proceed."*
    3.  **User Action (The Forcing Function)**: You must validate this statement.
        * If the statement is correct and accurately reflects the immediate context, you respond with the exact, literal string `Confirmed` after being prompted per **Protocol 4.5**.
        * If the statement is incorrect, or if I fail to issue it, you must state the discrepancy. This immediately halts the process and forces an **Error Analysis Protocol (6.3)**.
### 7. Miscellaneous Protocols

7.1. **Technical Debt Cleanup Protocol.** When code becomes convoluted, a **Technical Debt Cleanup Sprint** will be conducted to refactor the code for clarity, consistency, and maintainability.
7.2. **Multi-Part Bundle Protocol.** If a large or complex text file cannot be transmitted reliably in a single block, the Multi-Part Bundle Protocol will be used. The AI will take the single file and split its content into multiple, smaller text chunks. These chunks will then be delivered sequentially using the **Large File Transmission Protocol (Protocol 4.3)**.

7.3. **Fragile Dependency Protocol.** If a third-party library proves to be unstable, a sprint will be conducted to replace it with a more robust alternative.
7.4. **Prototype Script Development Protocol.** This protocol is used for the creation and modification of standalone prototype scripts located in the `test_code/` directory.
    1.  **Formal Entity**: A prototype script is a formal, versioned file, but is exempt from requiring an in-file revision history. Versioning begins at `1.0.0-Beta`.
    2.  **Standard Workflow**: All work on a prototype script must follow the complete **Task Execution Workflow (Section 2)**, including a formal Implementation Plan, user Approval, and a Confirmed File Delivery.
7.5. **Tool Suitability Re-evaluation Protocol.**
    1.  **Trigger**: This protocol is initiated when an approved implementation plan fails for a second time due to the unexpected or undocumented behavior of a third-party library or tool.
    2.  **Halt**: The AI must halt further implementation attempts with the current tool.
    3.  **Analysis**: The AI must analyze *why* the tool is failing and identify the specific feature gap (e.g., "`tabulate` lacks a mechanism to enforce column widths on separate tables").
    4.  **Propose Alternatives**: The AI will research and propose one or two alternative tools that appear to have the required features, explaining how they would solve the specific problem.
    5.  **User Decision**: The user will make the final decision on whether to switch tools or attempt a different workaround.
7.6. **Systemic Bug Eradication Protocol.** This protocol is triggered when a bug is suspected to be systemic (i.e., likely to exist in multiple, architecturally similar modules).
    1.  **Initiation**: The AI or user identifies a bug as potentially systemic.
    2.  **Define Pattern**: The specific bug pattern is clearly defined (e.g., "a parser using a generic key to look up a specific rule").
    3.  **Identify Scope and Method**: The AI will provide a complete list of all modules that follow the same architectural pattern and are therefore candidates for the same bug. To ensure completeness, the AI **must explicitly state the exact search method used** (e.g., the literal search string or regular expression used for a global text search) to generate this list.
    4.  **Audit and Report**: The AI will perform an audit of every module in the scope list and provide a formal analysis of the findings, confirming which modules are affected and which are not.
    5.  **Consolidate and Fix**: Upon user approval, the AI will create a single, consolidated implementation plan to fix all instances of the bug at once.