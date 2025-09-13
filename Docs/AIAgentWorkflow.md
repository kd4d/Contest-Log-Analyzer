# AIAgentWorkflow.md

**Version: 0.65.0-Beta**
**Date: 2025-09-12**

---
### --- Revision History ---
## [0.65.0-Beta] - 2025-09-12
### Changed
# - Clarified Protocol 2.5 to require that the `diff` output in an
#   implementation plan must be presented in a single, fenced code block.
## [0.64.0-Beta] - 2025-09-12
### Added
# - Added a mandatory "Surgical Change Verification (`diff`)" section
#   to Protocol 2.5 (Implementation Plan) to make adherence to
#   Principle 9 (Surgical Modification) verifiable.
### Changed
# - Rephrased the "Surgical Modification Adherence Confirmation" step
#   in Protocol 2.5 to refer to the new `diff` section.
## [0.63.0-Beta] - 2025-09-11
### Added
# - Added a new step to Protocol 6.3 (Error Analysis Protocol) to
#   require a proposal to amend the workflow if it is found to be
#   the root cause of an error.
## [0.62.0-Beta] - 2025-09-09
### Added
# - Added a mandatory "Surgical Modification Adherence Confirmation"
#   step to Protocol 2.5 to make the execution contract more explicit.
# - Added a mandatory post-delivery verification statement to Protocol 4.4
#   to enforce compliance with Principle 9.
## [0.61.0-Beta] - 2025-09-09
### Added
# - Added a mandatory self-verification step to Protocol 2.5 (Implementation Plan)
#   and Protocol 6.3 (Error Analysis Protocol) to improve compliance.
## [0.60.3-Beta] - 2025-09-09
### Changed
# - Modified Protocol 3.2.4 to require a unique `cla-bundle` specifier
#   for markdown file delivery to improve robustness.
## [0.60.2-Beta] - 2025-09-09
### Added
# - Added Protocol 3.2.6 (Post-Delivery Protocol Verification) to require
#   a mandatory self-verification check after every file delivery.
## [0.60.1-Beta] - 2025-09-09
### Changed
# - Strengthened Protocol 7.6 (Systemic Bug Eradication Protocol) to
#   require the AI to explicitly state the search method used for an audit.
## [0.60.0-Beta] - 2025-09-08
### Added
# - Added Principle 15 (Principle of Centralized Configuration) to mandate
#   that configuration is read in one place and passed as parameters.
# - Added Protocol 6.8 (External System Interference Protocol) to formalize
#   the process for diagnosing errors caused by external tools like Git or OneDrive.
## [0.59.1-Beta] - 2025-09-03
### Changed
# - Corrected an internal documentation reference to point to the correct
#   user guide filename.
## [0.59.0-Beta] - 2025-09-03
### Added
# - Added Protocol 7.6 (Systemic Bug Eradication Protocol) to formalize
#   the process of auditing for and fixing systemic bugs.
# - Added a mandatory "Request Diagnostic Output" step to Protocol 6.3
#   (Error Analysis Protocol) to improve diagnostic efficiency.
### Changed
# - Strengthened Principle 9 (Surgical Modification) to explicitly forbid
#   unauthorized stylistic refactoring and define a process for proposing such changes.
# - Clarified Protocol 2.7 (Approval) to require the exact, literal string `Approved`.
# - Clarified Protocol 4.4 (Confirmed File Delivery Protocol) to require
#   the exact, literal string `Acknowledged`.
## [0.58.0-Beta] - 2025-09-02
### Changed
# - Strengthened Principle 9 (Surgical Modification) to explicitly forbid
#   unauthorized refactoring and define a process for proposing changes.
# - Clarified Protocol 2.7 (Approval) to require the exact, literal string `Approved`.
# - Clarified Protocol 4.4 (Confirmed File Delivery Protocol) to require
#   the exact, literal string `Acknowledged`.
## [0.57.1-Beta] - 2025-09-01
### Changed
# - Clarified Protocol 3.2.1 to explicitly state that "bundles" are
#   only for user-to-AI state initializations.
# - Updated Protocol 3.2.5 to define the precise, literal pattern
#   for citation tags and to note that it does not include backticks.
## [0.57.0-Beta] - 2025-09-01
### Changed
# - Renamed file from WorkingwithGemini.md to AIAgentWorkflow.md to
#   clarify its purpose as the AI's technical specification.
# - Updated the introduction to reference the new WorkflowUserGuide.md.
## [0.56.31-Beta] - 2025-09-01
### Added
# - Added Protocol 7.6 (Systemic Bug Eradication Protocol) to formalize
#   the process of auditing for and fixing systemic bugs.
# - Added a rule to Protocol 3.2 requiring the removal of all internal
#   citation tags from delivered documents.
### Changed
# - Rewrote Protocol 2.9.1 to align the documentation delivery workflow
#   with the code delivery workflow, concluding the task after the user's
#   "Acknowledged" response.
# - Removed all internal [cite] tags from the document content.
## [0.55.13-Beta] - 2025-08-31
### Changed
# - Updated Protocol 2.9.1 to require a final user acknowledgment
#   after a documentation file (.md) has been delivered.
## [0.55.7-Beta] - 2025-08-30
### Added
# - Added Principle 11 ("The Log is the Ground Truth") to clarify how to
#   handle factually incorrect data within a log file.
# - Added Protocol 3.7 (Temporary Column Preservation Protocol) to prevent
#   the accidental deletion of intermediate data columns during processing.
# - Added Protocol 5.6 (Custom ADIF Exporter Protocol) to formalize the
#   new, pluggable architecture for contest-specific ADIF generation.
### Changed
# - Renumbered subsequent principles in Part I.
## [0.52.22-Beta] - 2025-08-27
### Changed
# - Revised Protocol 5.4 to recommend `prettytable` for complex,
#   multi-table reports and designate `tabulate` for simpler,
#   single-table use cases.
## [0.52.21-Beta] - 2025-08-27
### Changed
# - Strengthened Principle 9 (Surgical Modification) to explicitly
#   forbid unauthorized stylistic refactoring.
### Added
# - Added Protocol 7.5 (Tool Suitability Re-evaluation Protocol) to
#   formalize the process of handling unsuitable third-party tools.
## [0.52.20-Beta] - 2025-08-26
### Added
# - Added a mandatory "Affected Modules Checklist" to Protocol 2.5 to
#   make Principle 7 (Assume Bugs are Systemic) more robust.
## [0.49.2-Beta] - 2025-08-25
### Added
# - Added Protocol 7.4 (Prototype Script Development Protocol) to formalize
#   the development workflow for prototype scripts.
### Changed
# - Clarified Protocol 1.7 to define the special status of the
#   `test_code/` directory.
## [0.49.1-Beta] - 2025-08-25
### Added
# - Added Protocol 2.9.1 (Task Type Verification) to clarify when it is
#   appropriate to propose a verification command, preventing errors when
#   a task modifies a documentation file.
## [0.49.0-Beta] - 2025-08-25
### Added
# - Added Protocol 2.8.1 (Post-Execution Refinement Protocol) to clarify
#   the workflow for handling incomplete fixes.
# - Added Protocol 5.5 (Component Modernization Protocol) to formalize
#   the process of upgrading and deprecating legacy components.
# - Added a mandatory "Request Diagnostic Output" step to Protocol 6.3
#   (Error Analysis Protocol) to improve diagnostic efficiency.
### Changed
# - Renumbered subsequent protocols in the Task Execution Workflow.
## [0.48.2-Beta] - 2025-08-25
### Added
# - Added Protocol 5.4 to formalize the use of the `tabulate` library
#   for generating all text-based tables.
### Changed
# - Clarified Protocol 3.2.4 to explain the reasoning behind the
#   __CODE_BLOCK__ substitution for markdown file delivery.
## [0.48.1-Beta] - 2025-08-24
### Changed
# - Amended Protocol 2.1 (Task Initiation) to require a mandatory check
#   for an established session version number before proceeding.
# - Clarified Protocol 3.4.3 (Update Procedure) to explicitly forbid
#   unauthorized changes to major or minor version numbers.
## [0.48.0-Beta] - 2025-08-24
### Changed
# - Merged the Pre-Flight Check (2.6) into the Implementation Plan
#   protocol (2.5) to reflect the new, more detailed planning process.
# - Renumbered subsequent protocols in the Task Execution Workflow.
## [0.47.6-Beta] - 2025-08-23
### Added
# - Added clarification to Protocol 1.5 that version numbers are only
#   updated if a file's content is modified.
## [0.44.0-Beta] - 2025-08-23
### Changed
# - Modified Protocol 3.2.4 to require substituting embedded code
#   fences (```) with __CODE_BLOCK__ for markdown file delivery.
## [0.43.0-Beta] - 2025-08-23
### Added
# - Added Protocol 6.6 (Self-Correction on Contradiction) to mandate a
#   full stop and re-evaluation upon detection of logically impossible
#   or contradictory analytical results.
# - Added Protocol 6.7 (Simplified Data Verification) to formalize the
#   use of user-provided, simplified data files for debugging.
### Changed
# - Amended Principle 5 (Technical Diligence) to explicitly require
#   halting when a tool produces inconsistent results over multiple attempts.
# - Clarified Protocol 6.3 (Error Analysis Protocol) to emphasize that
#   a failure to provide a correct analysis after a user's correction
#   constitutes a new, more severe error.
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
#   with __CODE_BLOCK__ for proper web interface rendering.
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
1.3. **Context Checkpoint Protocol.** If the AI appears to have lost context, the user can issue a **Context Checkpoint**.
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
    * `contest_tools/`: The core application library.
    * `contest_tools/reports/`: The "plug-in" directory for all report modules.
    * `contest_tools/contest_definitions/`: Data-driven JSON definitions for each contest.
    * `Docs/`: All user and developer documentation.
    * `test_code/`: Utility and prototype scripts not part of the main application. These scripts are not held to the same change control and documentation standards (e.g., a revision history is not required).
    * `data/`: Required data files (e.g., `cty.dat`).
### 2. Task Execution Workflow
This workflow is a formal state machine that governs all development tasks, from initial request to final completion.
2.1. **Task Initiation**: The user provides a problem, feature request, or document update and requests an analysis. Before proceeding, the AI must verify that a session version series (as defined in Protocol 1.6) has been established. If it has not, the AI must ask for it before providing any analysis.
2.2. **Analysis and Discussion**: The AI provides an in...