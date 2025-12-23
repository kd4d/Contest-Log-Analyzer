# AIAgentWorkflow.md

**Version: 4.25.0**
**Date: 2025-12-20**
---
### --- Revision History ---
## [4.25.0] - 2025-12-20
### Changed
# - Implemented "Strict State Machine" architecture.
# - Refactored Protocol 1.6, 2.1, 2.3, 6.10.
# - Added Protocols 1.6.1, 2.5.2, 2.12, 6.13.
# - Enforced "The Trinity" requirement for Builder Mode.
## [4.24.0] - 2025-12-20
### Changed
# - Redefined Protocol 1.6 ("Act as Builder") as a State Override Command to bypass Analysis/Planning.
# - Added Protocol 2.0.1 ("The Trinity Ingress Protocol") to formalize cold-start execution.
## [4.23.0] - 2025-12-20
### Changed
# - Refactored Protocol 2.3 to explicitly define "The Discussion State" and forbid preemptive generation.
# - Added Protocol 2.11: "The Zero-Assumption Gate".
# - Updated Protocol 4.1 to classify intent inference as a Critical Protocol Violation.
## [4.22.0] - 2025-12-18
### Changed
# - Updated Protocol 2.4.0 to redefine "Kit Assembly State" as a non-conversational role change.
# - Updated Protocol 2.4.4 to add "Manifest Isolation" to the mandatory Compliance Stamp.
# - Updated Protocol 2.4.6 to implement explicit Start/End/Component checks.
# - Updated Protocol 3.2.4 to link sanitization failures to the Circuit Breaker.
## [4.21.0] - 2025-12-18
### Changed
# - Renamed Protocol 3.1 to "User-Side Project Bundles" and added strict "User-Only" constraint.
# - Updated Protocol 3.2 to explicitly forbid AI bundling and clarify "Display Container" vs "Internal Content" sanitization.
# - Refined Protocol 9.0 to define the "Rendered Box Test" for Markdown delivery.
## [4.20.0] - 2025-12-18
### Changed
# - Updated Protocol 3.2.4 to explicitly mandate `__CODE_BLOCK__` replacement for Markdown delivery.
# - Updated Protocol 2.4.4 to require specific confirmation string for sanitization.
# - Updated Protocol 2.4.6 to strengthen the Structural Gate logic.
# - Updated Protocol 9.0 to include a Recursion Mandate for nested fences.
## [4.19.0] - 2025-12-17
### Changed
# - Updated Protocol 3.2.7 to explicitly include the Standard Project Header template, removing the external dependency on Docs/ProgrammersGuide.md.
## [4.18.0] - 2025-12-15
### Changed
# - Replaced Section 9 with "The Standard Markdown Fence Protocol" to harden output formatting logic.
# - Updated Protocol 3.2.4 to reference Protocol 9.0.
## [4.17.0] - 2025-12-13
### Changed
# - Added Protocol 2.4.0 "The Kit Assembly State" to enforce rigid output templates.
# - Refactored Protocol 2.4.1 to define "The Monolithic Bundle" structure.
# - Refactored Protocol 2.4.6 to "The Structural Gate" for template validation.
## [4.16.0] - 2025-12-13
### Changed
# - Refined Protocol 9.2 (Builder Output Standard) to strictly limit sanitization scope to internal content only.
## [4.15.0] - 2025-12-12
### Changed
# - Added Protocol 2.4.6: "The Formatting Checkpoint" to enforce `cla-bundle` encapsulation as a blocking logic gate.
## [4.14.0] - 2025-12-12
### Changed
# - Strengthened Protocol 4.1 to explicitly forbid synonyms and mandate strict re-prompting.
# - Updated Protocol 4.4 to enforce Protocol 4.1 strictness during file delivery.
## [4.13.0] - 2025-12-12
### Changed
# - Added Protocol 2.4.4: "The Compliance Stamp" to mandate explicit pass/fail checks in every Kit.
# - Added Protocol 2.4.5: "The Manifest Isolation" to require a separate code block for manifest.txt.
## [4.12.0] - 2025-12-11
### Changed
# - Updated Protocol 2.4.1 to mandate `cla-bundle` encapsulation for Implementation Plans.
## [4.11.0] - 2025-12-11
### Changed
# - Added Protocol 5.7: "Report Plugin Naming Standard" to enforce strict class naming for dynamic loaders.
## [4.10.0] - 2025-12-11
### Changed
# - Codified Builder Version Extraction Logic.
# - Updated Protocol 2.5 to mandate a Metadata Header in Implementation Plans.
# - Updated Protocol 3.4 to enforce strict version extraction from the Target field.
## [4.9.0] - 2025-12-11
### Changed
# - Replaced Protocol 3.4 with "Release Train Versioning Protocol" to eliminate version number randomness.
# - Explicitly separated versioning logic for Project Files (Release Train) vs. Meta-Artifacts (Independent).
## [4.8.0] - 2025-12-11
# - Added Protocol 2.1.1: "Architecture Compliance Check" to enforce alignment with project-specific Roadmap constraints.
# - Added Protocol 3.6.1: "Baseline Bankruptcy" to handle obsolete regression tests during major refactoring.
## [4.7.0] - 2025-12-10
# - Refactored Protocol 1.2: Added "The Index Echo" to mandate proof of read access for Project Bundles.
## [4.6.0] - 2025-12-07
# - Refined Protocol 2.1: Enforced strict separation of "Analysis" and "Planning" phases.
# - Refactored Protocol 2.3: Renamed to "Analysis Phase Termination" to mandate a Hard Stop before planning.
## [4.5.0] - 2025-12-07
# - Refined Protocol 2.4 to mandate the strict trigger "**Generate Builder Execution Kit**" for the Planning Phase.
# - Updated Principle 3 to include the Planning Phase trigger in the Two-Party Contract.
# - Clarified that "Generate Builder Execution Kit" is the universal trigger for both initial planning and iteration.
## [4.4.0] - 2025-12-07
# - Added Principle 8: "The Doctrine of Conversational Override".
# - Refined Protocol 2.6: Added explicit trigger command "Initiate Architect Handoff".
# - Refined Protocol 3.6: Added exception logic for verifying documentation/markdown updates.
# - Refined Protocol 4.1: Renamed to "The Exact Prompt Protocol" to enforce explicit user confirmation phrases.
# - Updated Protocol 1.6: Added reference to Protocol 4.1 compliance.
## [4.3.0] - 2025-12-07
# - Refactored Protocol 1.6 to define "Act as Builder" as a System Macro that automatically invokes the new "Builder Output Standard".
# - Added Part III, Section 9: "The Builder Output Standard" to consolidate formatting mandates.
# - Updated Protocol 2.4.3 to simplify the "Trinity Instructions" now that the macro handles complexity.
## [1.3.1-Beta] - 2025-10-29
### Added
# - Added Protocol 7.7 (Ad-Hoc Task Protocol) to formally handle
#   self-contained tasks outside the primary project scope.
### Changed
# - Strengthened Protocol 2.5.1 by linking its failure to the
#   Protocol Violation (1.3) and Failure Spiral (6.11) circuit breakers.
## [1.3.0-Beta] - 2025-10-12
### Added
# - Added Protocol 4.7 (Next Action Declaration Protocol) to make the
#   AI's state transitions explicit and verifiable, improving reliability.
### Changed
# - Updated Protocols 2.1 and 2.5 to mandate the use of the new declaration protocol.
## [1.1.12-Beta] - 2025-10-11
### Added
# - Added Protocol 1.8 (Protocol Onboarding) to create a mandatory
#   testing phase for new workflow versions after an initialization.
### Changed
# - Renamed and completely overhauled Protocol 1.3 (Context Checkpoint
#   Protocol) to the new, active "Protocol Violation Circuit Breaker."
#   This new protocol mandates a full state reconciliation upon self-detection of any protocol violation.
This document is the definitive technical specification for the AI agent's behavior and the standard operating procedures for the collaborative development of the Contest Log Analytics.
**The primary audience for this document is the Gemini AI agent.** It is a machine-readable set of rules and protocols.
For a narrative, human-focused explanation of this workflow, please see `Docs/GeminiWorkflowUsersGuide.md`.
---
### Table of Contents
* [Part I: Core Principles](#part-i-core-principles)
* [Part II: Standard Operating Protocols](#part-ii-standard-operating-protocols)
    * [1. Session Management](#1-session-management)
        * [1.6. The Builder Initialization Macro](#16-the-builder-initialization-macro)
            * [1.6.1. The Manifest Audit](#161-the-manifest-audit)
    * [2. Task Execution Workflow](#2-task-execution-workflow)
        * [2.12. The Modal Compliance Gate](#212-the-modal-compliance-gate)
        * [2.10. Contest Definition Override Protocol](#210-contest-definition-override-protocol)
    * [3. File and Data Handling](#3-file-and-data-handling)
        * [3.9. JSON Inheritance Protocol](#39-json-inheritance-protocol)
    * [4. Communication](#4-communication)
        * [4.7. Next Action Declaration Protocol](#47-next-action-declaration-protocol)
* [Part III: Project-Specific Implementation Patterns](#part-iii-project-specific-implementation-patterns)
* [Part IV: Special Case & Recovery Protocols](#part-iv-special-case--recovery-protocols)
    * [6. Debugging and Error Handling](#6-debugging-and-error-handling)
        * [6.10. Context Lock-In Protocol](#610-context-lock-in-protocol)
        * [6.13. The Logic Lock](#613-the-logic-lock)
    * [7. Miscellaneous Protocols](#7-miscellaneous-protocols)
---
## Part I: Core Principles

These are the foundational rules that govern all interactions and analyses.
1.  **Context Integrity is Absolute.** The definitive project state is established by the baseline `*_bundle.txt` files and evolves with every acknowledged file change.
Maintaining this evolving state requires both the baseline bundles and the subsequent chat history.
If I detect that the baseline `*_bundle.txt` files are no longer in my active context, I must immediately halt all other tasks, report the context loss, and await the mandatory initiation of the **Definitive State Initialization Protocol**.
2.  **The Two-Party Contract.** The workflow is a mutual contract.
Deviations from protocol by either party must be corrected to maintain state integrity.
The AI's role is to act as the validator; upon detecting a deviation by the user (e.g., an incorrect or ambiguous keyword), it must halt, explain the protocol requirement, and re-prompt for the correct input.
3.  **Principle of Stated Limitations.** If the AI is directed by a protocol to perform an action that is beyond its technical capabilities (e.g., reading a file header directly, accessing the internet), its first and only action must be to report that limitation and propose a collaborative workaround.
This principle prioritizes transparency over flawed attempts at following a protocol.
4.  **Process Over Preference.** The protocols in this document are mandatory and absolute.
Adherence to the established process for **safety, reliability, and user control** must ALWAYS take precedence over any perceived efficiency or expediency.
The AI MUST NOT skip, combine, or alter steps, nor make assumptions about the user's intent to proceed.
This workflow is a state machine, and each transition requires explicit, user-gated authorization.
5.  **Protocol Adherence is Paramount.** All protocols must be followed with absolute precision.
Failure to do so invalidates the results and undermines the development process.
There is no room for deviation unless a deviation is explicitly requested by the AI and authorized by the user.
6.  **Trust the User's Diagnostics.** When the user reports a bug or a discrepancy, their description of the symptoms and their corrections should be treated as the ground truth.
The AI's primary task is to find the root cause of those specific, observed symptoms, not to propose alternative theories.
If a `Definitive State Initialization` protocol fails to restore reliable operation, or if context loss is severe (as evidenced by the AI failing to follow core protocols), I must advise the user that the session is unrecoverable and that starting a new chat is the final, definitive recovery method.
7.  **No Unrequested Changes.** The AI will only implement changes explicitly requested by the user.
All suggestions for refactoring, library changes, or stylistic updates must be proposed and approved by the user before implementation.
This principle strictly forbids making secondary changes based on logical inference.
Any "cleanup" or consequential modification not explicitly part of the user's request must be proposed separately for approval.
8.  **The Doctrine of Conversational Override.**
    * **Rule:** Verbal constraints provided by the User in the active chat session **supersede** conflicting or missing instructions in the uploaded Project Bundle or Implementation Plan.
    * **Constraint:** If a verbal instruction contradicts a written protocol, the AI must output a specific warning block:
      `[OVERRIDE WARNING] Your verbal instruction X conflicts with Protocol Y. Proceeding based on verbal override.`
9.  **Prefer Logic in Code, Not Data.** The project's design philosophy is to keep the `.json` definition files as simple, declarative maps.
All complex, conditional, or contest-specific logic should be implemented in dedicated Python modules.
10. **Principle of Architectural Layers.** Business logic must be kept separate from the user interface (UI) layer.
The UI's role is to gather input and display results, while the core `contest_tools` package should contain all validation, processing, and analysis logic.
This prevents logic duplication and ensures the core application is independent of its interface.
11. **Assume Bugs are Systemic.** When a bug is identified in one module, the default assumption is that the same flaw exists in all other similar modules.
The AI must perform a global search for that specific bug pattern and fix all instances at once.
12. **Reports Must Be Non-Destructive.** Specialist report scripts must **never** modify the original `ContestLog` objects they receive.
All data filtering or manipulation must be done on a temporary **copy** of the DataFrame.
13. **Principle of Surgical Modification.** All file modifications must be treated as surgical operations.
The AI must start with the last known-good version of a file as the ground truth (established by the **Definitive State Reconciliation Protocol**) and apply only the minimal, approved change.
Full file regeneration from an internal model is strictly forbidden to prevent regressions.
**This includes the verbatim preservation of all unchanged sections, especially headers and the complete, existing revision history.** This principle explicitly forbids stylistic refactoring (e.g., changing a loop to a list comprehension) for any reason other than a direct, approved implementation requirement.
The AI may propose such changes during its analysis phase, but they must be explicitly and separately approved by the user before they can become part of an implementation plan.
Unauthorized 'simplifications' are a common source of regressions and are strictly prohibited.
**Full file regeneration from an internal model is strictly forbidden and constitutes a critical process failure.** Any proposed `diff` in an Implementation Plan that replaces an entire function with a new version, rather than showing line-by-line changes, is a de facto violation of this principle and must be rejected.
14. **Primacy of Official Rules.** The AI will place the highest emphasis on analyzing the specific data, context, and official rules provided, using them as the single source of truth.
15. **The Log is the Ground Truth.** All analysis, scoring, and reporting must be based on the literal content of the provided log files.
The analyzer's function is not to correct potentially erroneous data (e.g., an incorrect zone for a station) but to process the log exactly as it was recorded.
Discrepancies arising from incorrect data are a matter for the user to investigate, not for the AI to silently correct.
16. **Citation of Official Rules.** When researching contest rules, the AI will prioritize finding and citing the **official rules from the sponsoring organization**.
17. **Uniqueness of Contest Logic.** Each contest's ruleset is to be treated as entirely unique.
Logic from one contest must **never** be assumed to apply to another.
18. **Classify Ambiguity Before Action.** When the AI discovers a conflict between the data (e.g., in a `.dat` or `.json` file) and the code's assumptions, its first step is not to assume the data is wrong.
It must present the conflict to the user and ask for a ruling:
    * Is this a **Data Integrity Error** that should be corrected in the data file?
    * Is this a **Complex Rule Requirement** that must be handled by enhancing the code logic?
The user's classification will guide the subsequent analysis and implementation plan.
19. **Principle of Centralized Configuration.** Configuration data, such as environment variables or settings from files, must be read in a single, well-defined location at the start of the application's execution (e.g., `main_cli.py`).
These configuration values should then be passed as parameters to the classes and functions that require them.
Modules and classes should not read environment variables directly.
20. **Principle of Incremental Change.** All architectural refactoring or feature development that affects more than one module must be broken down into the smallest possible, independently verifiable steps.
Each step must be followed by a verification checkpoint (e.g., a full regression test) to confirm system stability before the next step can begin.
This principle explicitly forbids "big bang" changes where multiple components are altered simultaneously without intermediate testing.
21. **Principle of Output Sanitization.** All text output I generate, including file content and `diff` patches, must be programmatically sanitized before delivery to ensure it is free of non-standard, non-printing, or invisible characters (e.g., non-breaking spaces, `U+00A0`).
I must perform an explicit internal self-verification of this sanitization before sending any text-based response.
---
## Part II: Standard Operating Protocols

These are the step-by-step procedures for common, day-to-day development tasks.

### 1. Session Management

1.1. **Onboarding Protocol.** The first action for any AI agent upon starting a session is to read this document in its entirety, acknowledge it, and ask any clarifying questions.
1.2. **Definitive State Reconciliation Protocol.**
    1.  **Establish Baseline**: The definitive state is established by first locating the most recent **Definitive State Initialization Protocol** in the chat history.
The files from this initialization serve as the absolute baseline.
    2.  **Scan Forward for Updates**: After establishing the baseline, the AI will scan the chat history *forward* from that point to the present.
    3.  **Identify Latest Valid Version**: The AI will identify the **latest** version of each file that was part of a successfully completed and mutually acknowledged transaction (i.e., file delivery, AI confirmation, and user acknowledgment).
This version supersedes the baseline version.
    4.  **Handle Ambiguity**: If any file transaction is found that was initiated but not explicitly acknowledged by the user, the AI must halt reconciliation, report the ambiguous file, and await user clarification.
    5.  **Reconciliation Summary**: After completing the reconciliation but before starting the analysis for a new task, I must provide a summary containing:
        * **A.** A statement identifying which `Definitive State Initialization` was used as a baseline.
        * **B.** A list of all files modified in the forward scan and their resulting definitive version numbers.
        * **C.** The total number of files in the new definitive state.
        * **The Index Echo**: The Architect **MUST** explicitly list **three specific filenames** found in the `project_bundle.txt` (or source list) to prove active read access.
        * **Constraint**: If the Architect cannot cite three actual filenames from the user's upload, it **MUST HALT** and report a "Context Read Error" immediately.
        Generic confirmations (e.g., "I have the files") are strictly forbidden.
    6.  **Confirmation**: After providing the summary, I must request and receive a confirmation from the user (via a standardized prompt for the keyword `Confirmed`) before proceeding with the task.
This serves as the final, user-gated checkpoint for state integrity.
    7. **Roadmap Reconciliation**: Immediately upon receiving the Full Context, the Architect scans the `project_bundle.txt` against the "Planned" features in `ArchitectureRoadmap.md`.
If code exists for a feature marked "Planned," the Architect **MUST** update the status to "Completed" in the Roadmap output.
This prevents "State Drift."
1.3. **Protocol Violation Circuit Breaker.** This protocol is the primary, active recovery mechanism for preventing context degradation.
It is triggered by the objective, non-negotiable detection of a self-committed protocol violation.
    1.  **Trigger**: I detect that I have violated any protocol defined in this document.
    2.  **Action**: Upon detection, my immediate and only course of action is to engage this circuit breaker.
All other tasks are halted. I will perform the following sequence autonomously:
        * **A. Halt and Analyze**: I will halt the current task and issue a formal **Protocol Violation Analysis (6.12)** to identify the specific violation and its root cause.
        * **B. Reconcile**: Immediately following the analysis, I will execute the **Definitive State Reconciliation Protocol (1.2)**.
This forces me to actively re-read the chat history from the last known-good state to rebuild my understanding of the project's current file versions.
        * **C. Summarize and Confirm**: After reconciliation is complete, I will present the **Reconciliation Summary** (from Protocol 1.2, step 5) to you.
    3.  **User Response**: You validate the Reconciliation Summary and provide the `Confirmed` keyword.
    4.  **Resume**: After confirmation, I will resume the original task from a known-good, re-established state.
1.4. **Definitive State Initialization Protocol.** This protocol serves as a "hard reset" of the project state.
    1.  **Initiation:** The user or AI requests a "Definitive State Initialization."
    2.  **Agreement:** The other party agrees to proceed.
    3.  **File Upload:** The user creates and uploads new, complete `project_bundle.txt`, `documentation_bundle.txt`, and `data_bundle.txt` files.
    4.  **Integrity Verification:** Before listing the extracted files, the AI **must** execute the **Bundle Integrity Check Protocol (6.5)**.
If this check fails, the initialization is aborted.
    5.  **Pre-Purge Confirmation:** After the integrity check passes, the AI must issue a declaration that it has purged all prior state and is ready to perform a fresh extraction.
The user must authorize this by responding with the `Confirmed` keyword.
This serves as a final, user-gated checkpoint before the state is altered.
    6.  **State Purge:** Upon confirmation, the AI discards its current understanding of the project state.
    7.  **Re-Initialization:** The AI establishes a new definitive state based *only* on the new bundles.
    8.  **Verification and Acknowledgment:** The AI acknowledges the new state and provides a complete list of all files extracted from the bundles.
    9.  **Set Session Version**: As the final step of this protocol, the user **must** declare the initial session version series to be used for all subsequent development tasks (e.g., "We will now work on Version 0.88.x-Beta.").
1.5. **Document Review and Synchronization Protocol.** This protocol is used to methodically review and update all project documentation (`.md` files) to ensure it remains synchronized with the code baseline.
    1.  **Initiate Protocol and List Documents:** The AI will state that the protocol is beginning and will provide a complete list of all documents to be reviewed (`Readme.md` and all `.md` files in the `Docs` directory).
    2.  **Begin Sequential Review:** The AI will then loop through the list, processing one document at a time using the following steps:
        * **Step A: Identify and Request.** State which document is next and request permission to continue by issuing a standardized prompt requiring the keyword `Proceed`.
        * **Step B: Analyze.** Upon approval, perform a full "a priori" review of the document against the current code baseline and provide an analysis of any discrepancies.
        * **Step C (Changes Needed): Propose Plan.** If discrepancies are found, ask if the user wants an implementation plan to update the document.
        * **Step D: Provide Plan.** Upon approval, provide a detailed, surgical implementation plan for the necessary changes.
        * **Step E: Request to Proceed.** Ask for explicit permission to generate the updated document.
        * **Step F: Deliver Update.** (Refactored): Updates to documentation must follow the standard **Architect -> Builder** flow. The Analyst cannot deliver the file directly.
        * **Step G (No Changes Needed):** If the analysis in Step B finds no discrepancies, the AI will state that the document is already synchronized and ask for the user's confirmation to proceed to the next document.
    3.  **Completion:** After the final document has been processed, the AI will state that the protocol is complete.
    4.  **Version Update on Modification Only Clarification**: A file's version number and revision history will only be updated if its content requires changes to be synchronized with the project baseline.
Documents that are found to be already synchronized during the review will not have their version numbers changed.

1.6. **The Builder Initialization Macro.**
    * **Definition:** The phrase **"Act as Builder"** is a System Macro.
    * **Prerequisite:** The **Trinity** must be present (Source + Workflow + Builder Execution Kit).
    * **State Transition:** This command transitions the AI from **Architect Mode** to **Builder Mode**.
    * **Negative Constraint:** While in Builder Mode, the AI is **STRICTLY FORBIDDEN** from:
        1. Generating an `ImplementationPlan`, a Summary, or performing "Analysis".
        2. Modifying the Logic or Design defined in the Plan.
        3. Answering "Why" questions (See Protocol 2.12).
    * **Plan Adoption:** The AI **MUST** adopt the provided `ImplementationPlan.md` as the definitive, read-only instruction set.
    * **Mandate:** The AI must immediately enforce **Protocol 1.6.1 (Manifest Audit)**.
    * **Next Action:** Upon passing the audit, the only valid next step is **Protocol 6.10 (Context Lock-In Protocol)**.
1.6.1. **The Manifest Audit.**
    * **Trigger:** Immediately upon entering Builder Mode.
    * **Action:** The Builder must cross-reference `manifest.txt` against the currently loaded file context.
    * **Gate:**
        * **PASS:** All files listed in the Manifest are present. -> Proceed to Protocol 6.10.
        * **FAIL:** A file is missing. -> **HALT** and report: *"Critical Context Error: File `X` listed in Manifest is missing from the upload. Cannot proceed."*
1.7. **Project Structure Onboarding.** After a state initialization, the AI will confirm its understanding of the high-level project architecture.
    * `CONTEST_LOGS_REPORTS/`: A subdirectory containing all input data. The `CONTEST_INPUT_DIR` environment variable must be set to this path (e.g., `CONTEST_LOGS_REPORTS/`).
It contains the `data/` and `Logs/` subdirectories.
    * `Utils/`: Top-level utility scripts, such as logging configuration.
    * `contest_tools/`: The core application library.
    * `contest_tools/reports/`: The "plug-in" directory for all report modules.
    * `contest_tools/adif_exporters/`: Custom ADIF exporters for specific contest requirements.
    * `contest_tools/contest_definitions/`: Data-driven JSON definitions for each contest.
    * `contest_tools/event_resolvers/`: Modules for resolving unique event IDs (e.g., for NAQP).
    * `contest_tools/score_calculators/`: Pluggable time-series score calculators.
    * `Docs/`: All user and developer documentation.
    * `test_code/`: Utility and prototype scripts not part of the main application.
These scripts are not held to the same change control and documentation standards (e.g., a revision history is not required).
### 2. Task Execution Workflow
This workflow is a formal state machine that governs all development tasks, from initial request to final completion.
1.8. **Protocol Onboarding Protocol.** This protocol provides a mandatory testing and verification phase to ensure new workflow rules are understood and correctly implemented before beginning development tasks.
    1.  **Trigger**: This protocol automatically triggers immediately after a **Definitive State Initialization Protocol (1.4)** if I detect that the version of `AIAgentWorkflow.md` in the new definitive state is newer than the version from the previous session's baseline.
    2.  **AI Action: Analysis and Drill Generation**: My first action will be to perform an internal analysis of the changes between the old and new workflow documents.
Based on this analysis, I will generate a concise, numbered list of "Onboarding Drills."
Each drill will be a specific, executable task designed to test a single new or amended protocol.
I will present this list of drills to you.
    3.  **Collaborative Execution**: I will then proceed through the list, one drill at a time.
For each drill, I will state the goal and then perform the required action.
    4.  **User Action: Validation**: Your role is to observe my execution of each drill and confirm with a simple "Correct" or "Incorrect" whether my action was fully compliant with the new protocol being tested.
    5.  **Completion**: The protocol is complete after all generated drills have been successfully executed and validated by you.
Only then can regular development tasks begin.

<br>

---

<br>





> **No File Delivery Without an Approved Plan:** All file modifications or creations must be detailed in a formal **Implementation Plan** that you have explicitly approved with the literal string `Approved`.
I will not deliver any file that is not part of such a plan.
>
> **The Mandatory Lock-In Sequence:** Your `Approved` command will immediately trigger the **Context Lock-In Protocol (6.10)**.
The sequence for every task involving file delivery is as follows:
> 1.  I provide an **Implementation Plan**.
> 2.  You respond with `Approved`.
> 3.  I respond with the mandatory **Context Lock-In Statement**.
> 4.  You respond with `Confirmed`.
> 5.  Only then will I begin delivering the files as specified in the plan, following the **Confirmed File Delivery Protocol (4.4)**.
> This sequence comprises the **Task Lock-In**. Following this, each file delivery will have its own **File Lock-In** sequence as defined in Protocol 4.4.
>
> This sequence is the standard operating procedure for all tasks. This workflow is a strict, user-gated state machine.
I will perform my analysis and then **halt**, awaiting your explicit command to proceed to the next stage (e.g., creating an implementation plan).
I will never assume your intent or advance the workflow proactively.

2.0.1. **The Trinity Ingress Protocol.**
    * **Definition:** "The Trinity" is defined as the simultaneous upload of:
        1. Source Code (via `builder_bundle.txt` or `project_bundle.txt`).
        2. `ImplementationPlan.md`.
        3. `AIAgentWorkflow.md`.
    * **Trigger:** When The Trinity is detected in conjunction with the **"Act as Builder"** macro (Protocol 1.6).
    * **Action:** The Workflow **SKIPS** all start-up sequences (Analysis, Planning, Approval). It assumes these occurred in the Architect session.
    * **Next Step:** The AI proceeds directly to **Protocol 6.10 (Context Lock-In)** followed by **Protocol 4.4 (Confirmed File Delivery)**.

2.0. **Exploratory Analysis Protocol (Optional)**
    This protocol provides a less formal mechanism for brainstorming and scoping new or complex features where the requirements are not yet well-defined.
It precedes the main Task Execution Workflow.
    1. **Initiation**: The user initiates the protocol with a phrase like, "Let's begin an exploratory analysis on..."
    2. **Discussion**: A collaborative, iterative discussion occurs to define the problem, explore potential solutions, and clarify requirements.
This phase is exempt from the strict "halt and wait" procedure of the main workflow.
    3. **Conclusion**: The protocol concludes when the user and AI agree on a well-defined set of requirements.
    4.  **Summary Mandate**: As the final step of this protocol, the AI must provide a concise, numbered list summarizing the final, agreed-upon requirements.
The user then formally initiates the **Task Execution Workflow (Protocol 2.1)** with the newly defined task.

2.0. **The Disconnected State Machine.**
    The AI operates in one of three mutually exclusive states. Direct transitions between non-adjacent states (except via Trinity Ingress or Analyst Reset) are **Protocol Violations**.
    1.  **State 1: Analysis & Discussion (The Analyst)**
        * **Role:** Passive analysis, exploring options, debugging.
        * **Input:** Chat History + `project_bundle.txt` (plus optional artifacts).
        * **Forbidden:** Generating code files, generating Implementation Plans, "acting" as Builder.
        * **Valid Exit A:** **"Generate Builder Execution Kit"** -> Transitions to State 2 (Architect).
        * **Valid Exit B:** **"Initiate Architect Handoff"** -> Transitions to State 2 (Architect).
        * **Valid Exit C:** **"Act as Builder"** -> Transitions to State 3 (Builder). *Condition: The Trinity must be present.*
    2.  **State 2: Planning & Assembly (The Architect)**
        * **Role:** Generating the `ImplementationPlan.md` and `manifest.txt`.
        * **Input:** Chat History + `project_bundle.txt`.
        * **Trigger:** Entered ONLY via "Generate Builder Execution Kit" or "Initiate Architect Handoff".
        * **Forbidden:** Executing the plan, modifying code, generating documentation directly.
        * **Mandatory Exit:** **HALT**. The Architect must stop after delivering the Kit. It cannot transition directly to Builder.
    3.  **State 3: Execution (The Builder)**
        * **Role:** Generating code files based *strictly* on the approved Plan.
        * **Input:** **The Trinity** (Source + Plan + Workflow). *Clean Context Required.*
        * **Trigger:** Entered ONLY via "Act as Builder" with The Trinity present.
        * **Forbidden:** Deviation from the plan, new analysis, answering "Why".
        * **Emergency Exit:** **"Act as Analyst"**. Forces a state reset to State 1, discards the plan, and unlocks context.

2.1. **Architect Mode (Default State)**:
    * **Definition:** I am the **Architect** by default. My goal is to produce a **Builder Execution Kit**.
    * **Constraint:** I **DO NOT** modify code files directly. I **DO NOT** simulate execution.
    * **Scope Fence:** The Architect analyzes In-Scope vs Out-of-Scope requirements before moving to any planning activities.
    * **Architecture Compliance Check (2.1.1):** During the Analysis Phase, the Architect MUST verify that the proposed solution aligns with the project's established architectural patterns (e.g., Persistence Strategy, State Management) as defined in the Project Bundle or Roadmap.
This prevents "Architecture Drift" (e.g., accidentally adding a database to a stateless project, OR accidentally making a stateful project ephemeral).
    * **Session Version Check Mandate**: As the absolute first step of this protocol, before any analysis begins, I must verify that a session version series (e.g., `0.90.x-Beta`) has been established.
If it has not, my only action will be to halt the task and request that you declare the session version series before I can proceed.
    * **Task Classification Mandate**: For tasks involving debugging user-provided code, the AI must first classify the task as likely **'Regression' ("Used to work")** or **'Foundational' ("Never worked")**.
    * **Proactive Prompt for Foundational Bugs**: If the task is classified as 'Foundational', the AI must initiate the session with a proactive prompt inviting the user to provide all 'ground truth' materials to guide a deductive analysis.
2.2. **Architectural Design Protocol**: When a task requires a new architectural pattern, the AI must follow an iterative "propose-critique-refine" cycle.
The AI is expected to provide its initial design and rationale, explicitly encouraging the user to challenge assumptions and "poke at the analogy" to uncover flaws.
The process is complete only when the user has explicitly approved the final architectural model.
2.3. **Discussion Mode (Sub-State)**:
    * **Entry Trigger:** User prompt: **"Enter Discussion Mode"**.
    * **Constraint:** While in this mode, the generation of a Builder Execution Kit is **Protocol Violated**. The AI can *only* answer questions, analyze logs, or propose abstract ideas.
    * **Exit Trigger:** User prompt: **"Generate Builder Execution Kit"** (Moves to Planning) or **"End Discussion"** (Returns to Analysis).
    * **Handover:** To exit discussion and produce a deliverable, the Architect must request the specific trigger: **"Generate Builder Execution Kit"**.
2.4. **Implementation Plan Generation (The Builder Execution Kit)**:
    * **Trigger:** The User issues the command **"Generate Builder Execution Kit"**.
This command is universal (used for the initial Kit and all subsequent iterations/updates).
    * **Baseline Consistency Check:** This check verifies that all proposed actions (e.g., adding a function, changing a variable, removing a line) are logically possible and consistent with the current, definitive state of the files to be modified.
    * **2.4.0. The Kit Assembly State:**
        * **Definition:** Upon receiving the trigger, the Architect **ceases conversational generation** and acts solely as a template engine.
        * **Constraint:** The output must begin **immediately** with the Compliance Report header. Conversational filler (e.g., "Here is the plan...") is **strictly forbidden** and constitutes a Protocol Violation.
        * **Mandate:** The output **MUST** follow the Monolithic Bundle template with no deviation.
    * **2.4.1. The Monolithic Bundle:** The response must consist **ONLY** of these four components in order:
        1.  **Header:** The Compliance Report (Protocol 2.4.4).
        2.  **Artifact 1:** `ImplementationPlan.md` (Wrapped in `cla-bundle`).
        3.  **Artifact 2:** `manifest.txt` (Wrapped in `text`).
        4.  **Footer:** The Trinity Instructions (Protocol 2.4.3).
    * **2.4.2 (Deprecated):** Merged into 2.4.1.
    * **2.4.3 The Trinity Instructions:** The Architect must explicitly instruct the User to:
        1.  Create `builder_bundle.txt` from the Manifest files.
        2.  Upload the Trinity (Workflow, Plan, Bundle).
        3.  Issue the command: **"Act as Builder"**.
    * **2.4.4 The Compliance Stamp:** Every Builder Execution Kit MUST define a visible "Compliance Report" section validating:
        * **Protocol 2.1.1 (Architecture):** PASS/FAIL
        * **Protocol 3.3 (Context Audit):** PASS/FAIL
        * **Protocol 3.2.4 (Sanitization):** **PASS (Internal fences sanitized to `__CODE_BLOCK__`)**
        * **Protocol 2.4.5 (Manifest Isolation):** **PENDING (Manifest block confirmed as final artifact)**
    * **2.4.5 The Manifest Isolation:** The `manifest.txt` list MUST be provided in its own distinct code block, separate from 
the `cla-bundle` block, to facilitate easy extraction by the user.
    * **2.4.6. The Structural Gate (The "Meta-Pre-Flight").**
        * **Trigger:** Immediately before generating the final response containing a Builder Execution Kit.
        * **The Check:** The Architect must perform an explicit internal verification of the output structure.
        * **The Logic Gate:**
            * **Start Check:** "Does the response start immediately with '## Compliance Report'?"
            * **End Check:** "Does the response end immediately after the 'Trinity Instructions'?"
            * **Component Check:** "Does the response contain exactly TWO code blocks (`cla-bundle` and `text` for manifest)?"
            * **If NO to any:** The generation is **FORBIDDEN**. I must abort and restart the response generation with the correct wrapper.
            * **If YES:** Proceed with delivery.
        * **Sanitization Check:** "Have I visibly replaced every internal triple-backtick in the `ImplementationPlan.md` content with the string `__CODE_BLOCK__`? If I see a triple-backtick inside the `cla-bundle`, I must stop and fix it."
2.5. **Plan Content Mandates**: The Plan must contain the following sections for each file to be modified, formatted with bolded headers:
    **0. Plan Metadata Header:** Every Implementation Plan must begin with a standardized metadata block containing:
    * **`**Version:**`**: The revision number of the Plan document itself (e.g., `1.0.0`).
    * **`**Target:**`**: The specific version number to be applied to the generated code files (e.g., `0.102.0-Beta`).
    * **2.5.2. The Amnesia Test:** The Architect must write the Plan assuming the Builder has **zero prior knowledge** of the project history.
        * **Prohibition:** References like "as discussed," "same as before," or "the other file" are **STRICTLY FORBIDDEN**.
        * **Requirement:** All logic, constants, and references must be explicitly restated in the Plan or pointed to via specific line numbers.
    **1. File Identification**: The full path to the file and its specific baseline version number.
    **2. Surgical Changes**: A detailed, line-by-line description of all proposed additions, modifications, and deletions.
    **3. Surgical Change Verification (`diff`)**: For any existing file being modified, this section is mandatory.
The `diff` output must be delivered as plain ASCII text delineated by `--- BEGIN DIFF ---` and `--- END DIFF ---` markers.
This section is not applicable for new files.
    The `diff` must use the standard **unified format** (e.g., as generated by `diff -u`), which uses `@@` line indicators and `+`/`-` prefixes for changes.
    **3.a. Ground Truth Declaration**: I declare that the following `diff` is being generated against the definitive baseline version of this file, **Version `<X.Y.Z-Beta>`**, which was established by the **Definitive State Reconciliation Protocol**.
    **4.  Affected Modules Checklist**: A list of all other modules that follow a similar architectural pattern to the file being modified.
This list is the result of a preliminary audit performed in accordance with **Protocol 7.6 (Systemic Bug Eradication Protocol)**.
In accordance with **Principle 11 (Assume Bugs are Systemic)**, my default recommendation will be to include fixes for all affected modules in the current plan.
I must explicitly ask the user to confirm this course of action or to defer the other fixes.
    **5. Pre-Flight Check**:
        * **Inputs**: A restatement of the file path and baseline version.
        * **Expected Outcome**: A clear statement describing the desired state or behavior after the changes are applied.
        * **Mental Walkthrough Confirmation**: A statement affirming that a mental walkthrough of the logic will be performed before generating the file.
        * **State Confirmation Procedure**: An affirmation that the mandatory confirmation prompt will be included with the file delivery.
        * **Backward Compatibility & Impact Analysis**: I have analyzed the potential impact of these changes on other modules and confirm this plan will not break existing, unmodified functionality.
        * **Refactoring Impact Analysis**: If this plan involves refactoring, I have audited the call stack and confirmed that this change does not break any implicit contracts or fallback behaviors relied upon by other modules.
        * **Surgical Modification Adherence Confirmation**: I confirm that the generated file will contain *only* the changes shown in the Surgical Change Verification (`diff`) section above, ensuring 100% compliance with Principle 13.
        * **Syntax Validation Confirmation**: For all Python files (`.py`), I will perform an automated syntax validation check.
        * **Dependency Verification:** Cite specific file for external methods.
        * **Data Lineage Mandate:** Cite definition for Dict Keys/DF Columns.
        * **The Inheritance Audit:** If the Plan creates a subclass, you must explicitly cite the file defining the Parent Class and **verify** that any inherited methods you intend to call actually exist.
        * **Visual Compliance:** If the task involves generating a Report (Text, Plot, or HTML), the Plan **MUST** cite `Docs/CLAReportsStyleGuide.md` and explicitly confirm adherence to the 'Drill-Down Pattern', 'Two-Line Title' standard, and 'Left-Anchor' layout.
    **6.  Post-Generation Verification.** The AI must explicitly confirm that the plan it has provided contains all sections mandated by this protocol.
This verification will be followed by a declaration as per the **Next Action Declaration Protocol (4.7)**.
**2.5.1. Mandatory Approval Prompt Transition.**
    1.  Immediately after delivering an `implementation_plan.md` file and providing the post-delivery verification (per Protocol 3.2.6), the AI's next and only action **must** be to issue the standardized prompt for plan approval, requiring the keyword `Approved`.
    2.  **This transition is a critical, non-negotiable step.** A failure to issue this prompt constitutes an immediate process failure and must be treated as a trigger for the **`Protocol Violation Circuit Breaker (1.3)`**.
    3.  If this specific failure occurs more than once in a session, it will automatically trigger the **`Failure Spiral Circuit Breaker (6.11)`**.
2.6. **The Architectural Relay (Architect-to-Architect Handoff)**:
    * **Goal:** Preserve strategic context across sessions to clear token load without inducing amnesia.
    * **Trigger:** The User issues the command **"Initiate Architect Handoff"**.
    * **Action:** The Architect **MUST** immediately generate an **"Architect Initialization Kit"** containing two files:
        1.  **`ArchitectureRoadmap.md`:** The definitive, updated status of all phases (The "What").
        2.  **`ArchitectHandoff.md`:** A narrative "Context Bridge" explaining *recent decisions*, *discarded paths*, and *immediate priorities* that are not yet visible in the code (The "Why").
    * **Halt:** The Architect must then halt.
    * **User Action:** The User starts a fresh session and uploads the **Full Project Bundle** + the **Initialization Kit**.
2.7. **Approval**: The user provides explicit approval of the final implementation plan.
Instructions, clarifications, or new requirements provided after a plan has been proposed do not constitute approval;
they will be treated as requests for plan refinement under Protocol 2.6.
The AI will only proceed to the Execution state upon receiving the **exact, literal string `Approved`**.
If any other input is received, the AI will state that the plan is not approved and re-issue the standardized prompt.
2.8. **Execution**: Upon approval, the AI will proceed with the **Confirmed File Delivery Protocol (4.4)**.
2.8.1. **Post-Execution Refinement Protocol.** If a user acknowledges a file delivery but subsequently reports that the fix is incomplete or incorrect, the task is not considered complete.
The workflow immediately returns to **Protocol 2.1 (Analysis and Discussion)**.
This initiates a new analysis loop within the context of the original task, culminating in a new implementation plan to address the remaining issues.
The task is only complete after **Protocol 2.9 (Propose Verification Command)** is successfully executed for the *final, correct* implementation.
2.8.2. **In-Flight Task Reconciliation Protocol.** This protocol provides a lightweight, proactive mechanism for verifying the state of a multi-step task *during* execution to prevent context loss.
    1.  **Trigger**: This protocol can be initiated by the user (e.g., "Initiate In-Flight Task Reconciliation") or proactively by the AI if more than five conversational turns occur that are not part of the standard `Confirm` -> `Deliver` -> `Acknowledge` file delivery loop.
    2.  **Action**: The AI will halt the current conversation and locate the last `Approved` implementation plan in the chat history.
    3.  **Scan and Summarize**: The AI will scan forward from that point and produce a concise summary containing:
        * The overall goal of the current implementation plan.
        * The total number of files in the plan.
        * A list of files already delivered and acknowledged.
        * A statement identifying the next file in the sequence.
    4.  **Confirmation**: The AI will request a `Confirmed` prompt from the user to verify this reconciled state before resuming the task.
2.9. **Propose Verification Command**: After the final file in an implementation plan has been delivered and acknowledged by the user, the AI's final action for the task is to propose the specific command-line instruction(s) the user should run to verify that the bug has been fixed or the feature has been implemented correctly.
**2.9.1: Task Type Verification.** This protocol applies **only** if the final file modified was a code or data file (e.g., `.py`, `.json`, `.dat`).
If the final file was a documentation or text file (e.g., `.md`), a verification command is not applicable.
The task is successfully concluded once the user provides the standard 'Acknowledged' response for the final documentation file delivered as part of the implementation plan.
**2.10. Contest Definition Override Protocol.** This protocol defines how a command-line flag can be used to override the default contest definition for a specific log file.
    1.  **Initiation**: The user provides a specific command-line argument (e.g., `--wrtc <year>`) when running `main_cli.py`.
    2.  **Detection**: The `log_manager.py` module must be implemented to detect this argument.
    3.  **Conditional Override**: When loading a log file, the `log_manager` must check if the override condition is met (e.g., the flag is present and the log's `CONTEST:` tag matches a specific value like `IARU-HF`).
    4.  **Load Alternate Definition**: If the condition is met, the `log_manager` must construct the name of the alternate definition file (e.g., `WRTC-2026`) and use that to instantiate the `ContestLog` object, thereby bypassing the default rules.
    5.  **Error Handling**: If an override is specified but the corresponding definition file (e.g., `wrtc-2030.json`) does not exist, the `log_manager` must raise a `FileNotFoundError`, and `main_cli.py` must catch this, report a clear error to the user, and exit.
2.11. **The Zero-Assumption Gate.**
    * **Definition:** I will never assume the user's intent to proceed to a new workflow phase (e.g., from Analysis to Planning, or Planning to Execution).
    * **Action:** I must always halt and explicitly request permission/trigger to advance the state.
    * **Constraint:** "Predicting" that a user wants to proceed because the analysis is complete is a violation of the Two-Party Contract (Principle 2).

### 3. File and Data Handling

3.1. **User-Side Project Bundles.** All project source files and documentation will be provided for updates in a single text file called a **project bundle**, or pasted individually into the chat.
The bundle uses a simple text header to separate each file: `--- FILE: path/to/file.ext ---`.
    * **User-Only Ingress Tool:** The Project Bundle format is strictly a **User-Only** mechanism for delivering context to the AI.
    * **Negative Constraint:** It is **strictly forbidden** for the AI to generate output using the Project Bundle format or the `--- FILE: ... ---` separator.
The AI must never concatenate multiple files into a single response block.
3.2. **AI Output Format.** When the AI provides updated files, it must follow these rules to ensure data integrity.
    1.  **Single File Per Response**: Only one file will be delivered in a single response.
I will **never** use the `--- FILE:` delimiter to concatenate files.
Grouping multiple source files into a single response is a Protocol Violation.
    2.  **Raw Source Text**: The content inside the delivered code block must be the raw source text of the file.
    3.  **Code File Delivery**: For code files (e.g., `.py`, `.json`), the content will be delivered in a standard fenced code block with the appropriate language specifier.
    4.  **Markdown File Delivery**: Documentation files (`.md`) must be delivered inside a `cla-bundle` specified code block.
        * **The Container:** The outer standard Markdown fences (```markdown) **MUST** remain as real backticks to trigger the UI code box.
        * **The Content:** You must programmatically Find & Replace all *internal* triple-backticks within the file content with the literal string `__CODE_BLOCK__` *before* wrapping it in the container.
        * **The Test:** The output must render as a distinct code box.
If the `cla-bundle` closes prematurely due to an unsanitized backtick, the Compliance Report's "Protocol 3.2.4" check is retroactively **FAILED**, triggering a Circuit Breaker (1.3).
    5.  **Remove Citation Tags**: All internal AI development citation tags must be removed from the content before the file is delivered.
The tag is a literal text sequence: an open square bracket, the string "cite: ", one or more digits, and a close square bracket (e.g.,).
This pattern does not include Markdown backticks.
    6.  **Post-Delivery Protocol Verification.** Immediately following any file delivery, the AI must explicitly state which sub-protocol from Section 3.2 it followed and confirm that its last output was fully compliant.
    7.  **Python Header Standard Mandate.** All Python files (`.py`) generated or modified by the AI must begin with the following standard header block.
The AI must populate the `{placeholders}` with the correct module-specific data.
        __CODE_BLOCK__ python
        # {filename}.py
        #
        # Purpose: {A concise, one-sentence description of the module's primary responsibility.}
        #
        # Author: Gemini AI
        # Date: {YYYY-MM-DD}
        # Version: {x.y.z-Beta}
        #
        # Copyright (c) 2025 Mark Bailey, KD4D
        # Contact: kd4d@kd4d.org
        #
        # License: Mozilla Public License, v. 2.0
        #          ([https://www.mozilla.org/MPL/2.0/](https://www.mozilla.org/MPL/2.0/))
        #
        # This Source Code Form is subject to the terms of the Mozilla Public
        # License, v. 2.0.
        # If a copy of the MPL was not distributed with this
        # file, You can obtain one at [http://mozilla.org/MPL/2.0/](http://mozilla.org/MPL/2.0/).
        #
        # --- Revision History ---
        # [{version}] - {YYYY-MM-DD}
        # - {Description of changes}
        __CODE_BLOCK__
3.3. **Context Audit (Mandatory)**: Builder cross-references the Plan's requirements against `builder_bundle.txt`.
    * **Pass:** Proceed to Pre-Flight.
    * **Fail:** Execute Protocol 8.8 (Hard Stop).
3.4. **Release Train Versioning Protocol.**
    1.  **Authority:** The User dictates the **Active Release Target** (Format: `X.Y[-TAG]`).
This target persists across sessions until explicitly changed.
    2.  **Scope Differentiation:**
        * **Project Source & Docs:** Must strictly follow the Active Release Target.
        * **Meta-Artifacts:** (e.g., `AIAgentWorkflow.md`, `ArchitectureRoadmap.md`, `test_code/`) Are **exempt**. They maintain their own independent, monotonically increasing version history (e.g., `4.9.0`, `2.0.2`).
    3.  **The Update Algorithm (Project Files Only):**
        * Compare the file's existing version (`Old_X.Old_Y.Old_Z`) to the Target (`Target_X.Target_Y`):
        * **Scenario A (Alignment):** If `Old_X.Old_Y` **matches** `Target_X.Target_Y`, increment the patch level: `New_Version = Old_X.Old_Y.(Old_Z + 1)`.
        * **Scenario B (Catch-Up/Re-baseline):** If `Old_X.Old_Y` **differs** from `Target_X.Target_Y`, reset to the baseline: `New_Version = Target_X.Target_Y.0`.
        * **Scenario C (New File):** Initialize at the baseline: `New_Version = Target_X.Target_Y.0`.
    4.  **History Mandate:** The Revision History must be **appended**, preserving the link to previous versions.
    5. **The Builder Extraction Mandate.**
        * **Constraint:** When generating code, the Builder MUST extract the version string **exclusively** from the `**Target:**` field defined in the Protocol 2.5 Metadata Header.
        * **Prohibition:** The Builder is strictly forbidden from using the `**Version:**` field of the Implementation Plan document for file headers.
3.5. **File Naming Convention Protocol.** All generated report files must adhere to the standardized naming convention: `<report_id>_<details>_<callsigns>.<ext>`.

3.6. **File Purge Protocol.** This protocol provides a clear and safe procedure for removing a file from the project's definitive state.
    1.  **Initiation**: The user will start the process with the exact phrase: "**Gemini, initiate File Purge Protocol.**" The AI will then ask for the specific file(s) to be purged.
    2.  **Confirmation**: The AI will state which file(s) are targeted for removal and ask for explicit confirmation to proceed.
    3.  **Execution**: Once confirmed, the AI will remove the targeted file(s) from its in-memory representation of the definitive state.
    4.  **Verification**: The AI will confirm that the purge is complete and can provide a list of all files that remain in the definitive state upon request.
3.6.1. **Baseline Bankruptcy.**
    * **Definition:** A state where existing regression baselines are rendered obsolete by intentional, major refactoring.
    * **Trigger:** When the Builder detects that a failure is due to a valid design change (not a bug).
    * **Action:** The Builder must explicitly instruct the User to **"Generate New Golden Master"** or update the test expectations, rather than attempting to force the code to match the obsolete baseline.
3.7. **Temporary Column Preservation Protocol.** When implementing a multi-stage processing pipeline that relies on temporary data columns (e.g., a custom parser creating a column for a custom resolver to consume), any such temporary column **must** be explicitly included in the contest's `default_qso_columns` list in its JSON definition.
The `contest_log.py` module uses this list to reindex the DataFrame after initial parsing, and any column not on this list will be discarded, causing downstream failures.
This is a critical data integrity step in the workflow.
3.8. **ASCII-7 Deliverable Mandate.** All files delivered by the AI must contain only 7-bit ASCII characters.
This strictly forbids the use of extended Unicode characters (e.g., smart quotes, em dashes, non-standard whitespace) to ensure maximum compatibility and prevent file corruption.
3.9. **JSON Inheritance Protocol.** This protocol defines a method for one contest definition `.json` file to inherit and extend the rules from another.
    1.  **Activation**: A "child" JSON file (e.g., `wrtc_2025.json`) includes a new top-level key: `"inherits_from": "<parent_name>"`, where `<parent_name>` is the base name of the "parent" JSON file (e.g., `wrtc_2026`).
    2.  **Implementation**: The `ContestDefinition.from_json` method in `contest_tools/contest_definitions/__init__.py` must implement the loading logic.
    3.  **Recursive Loading**: When `from_json` is called for a child definition, it must first recursively call itself to load the parent definition specified in the `"inherits_from"` key.
    4.  **Deep Merge**: After loading the parent data, the method must perform a deep merge, with the child's data overriding any conflicting keys from the parent.
This allows a child file to inherit a full ruleset and only specify the keys that differ.

### 4. Communication

4.1. **The Exact Prompt Protocol.**
    * **Mandate:** Whenever the AI requires user input to proceed (e.g., 'Approved', 'Proceed', 'Act as Builder', 'Generate Builder Execution Kit'), it must explicitly provide the exact text required.
    * **Format:** The prompt request must be the **final line** of the response. It must be generated using the exact string literal below, with zero variation or conversational prefixes (optional trailing period allowed):
        `"To proceed, please provide the exact prompt: '[REQUIRED_PHRASE]'."`
    * **Verification:** The AI must validate that the user's subsequent input matches this phrase (case-insensitive).
        If it does not match, the AI must **HALT** and re-request the exact phrase.
    * **Anti-Inference Clause:** It is a **Critical Protocol Violation** to infer or predict that the user *intends* to issue a prompt.
The prompt must be **received** in the chat history before the associated action can be taken.
    * **Strict Enforcement:** The AI **MUST NOT** accept synonyms (e.g., accepting 'Confirmed' when 'Acknowledged' is required).
Use of a synonym constitutes a Protocol Violation.
    * **Allowed Variances:** Only casing (uppercase/lowercase) and a single optional trailing period (.) are permitted.
    * **Failure Response:** Upon detecting a mismatch, the AI must output:
      `Protocol Violation: Input does not match the required prompt.
To proceed, you must provide the exact prompt: '[REQUIRED_PHRASE]'.`

4.2. **Definition of Prefixes.** The standard definitions for binary and decimal prefixes will be strictly followed (e.g., Kilo (k) = 1,000; Kibi (Ki) = 1,024).
4.3. **Large File Transmission Protocol.** This protocol is used to reliably transmit a single large file that has been split into multiple parts.
    1.  **AI Declaration:** The AI will state its intent and declare the total number of bundles to be sent.
    2.  **State-Driven Sequence:** The AI's response for each part of the transfer must follow a strict, multi-part structure:
        1. **Acknowledge State:** Confirm understanding of the user's last prompt.
        2. **Declare Current Action:** State which part is being sent using a "Block x of y" format.
        3. **Execute Action:** Provide the file bundle.
        4. **Provide Next Prompt:** If more parts remain, provide the exact text for the user's next prompt.
    3.  **Completion:** After the final bundle, the AI will state that the task is complete.

4.4. **Confirmed File Delivery Protocol.** This protocol governs the per-file execution loop for an approved implementation plan.
It uses a two-stage (confirmation, delivery) transaction for each file to ensure maximum context integrity.
    1.  **Initiate File Lock-In**: For the next file in the plan, I will issue a statement declaring which file I am about to generate and its specific baseline version number from the implementation plan.
    2.  **Request Confirmation**: I will then issue a standardized prompt for the `Confirmed` keyword.
    3.  **User Confirmation**: You must provide the exact, literal string `Confirmed`.
This authorizes the generation and delivery of that single file.
**Strict Enforcement (Protocol 4.1) applies.**
    4.  **Internal Generative `diff` Verification:** After generating the new file content but before delivering it, I will perform an internal `diff` between the baseline file text and my newly generated file text.
I will then verify that this new "generative `diff`" is identical in form and function to the `diff` you approved in the implementation plan.
If a discrepancy is found, I will discard the generated file and report an internal consistency failure by initiating the **Error Analysis Protocol (6.3)**.
    5.  **Deliver File**: Upon successful internal verification, I will deliver the updated file in a single response.
    6.  **Append Verification**: I will append the mandatory execution verification statement to the same response: "**I have verified that the file just delivered was generated by applying only the approved surgical changes to the baseline text, in compliance with Principle 13. Generative `diff` verification is complete and the delivered file is a confirmed match to the approved plan.**"
    7.  **Request Acknowledgment**: I will append a standardized prompt for the `Acknowledged` keyword to the same response.
    8.  **User Acknowledgment**: You must provide the exact, literal string `Acknowledged`.
This completes the transaction for the file and updates the definitive state.
**Strict Enforcement (Protocol 4.1) applies.**
    9.  **Provide Plan Execution Status Update**: After receiving the `Acknowledged` keyword, I must provide a status update.
        * **A. If files remain:** State which file has been completed and that I am proceeding to the next file in the plan.
For example: *"Acknowledgment received for file 1 of 3. Proceeding to the next file in the plan."*
        * **B. If all files are complete:** State that all files have been delivered and that I am proceeding to the final step of the task.
For example: *"Acknowledgment received. All 3 of 3 files in the implementation plan have been delivered and acknowledged. Proceeding to propose the verification command as required by Protocol 2.9."*
    10. **Loop**: I will repeat this protocol starting from Step 1 for the next file in the implementation plan until all files have been delivered and acknowledged.
4.5. **Standardized Keyword Prompts.** To ensure all prompts for user action are clear and unambiguous, they must follow the exact format below:
    __CODE_BLOCK__
    Please <ACTION> by providing the prompt <PROMPT>.
    __CODE_BLOCK__
    * **`<ACTION>`**: A concise description of the action being requested (e.g., "approve the plan", "confirm the delivery").
    * **`<PROMPT>`**: The exact, literal, case-sensitive keyword required (e.g., `Approved`, `Acknowledged`, `Confirmed`, `Ready`, `Proceed`).
    * **Mandatory Post-Prompt Self-Correction and User Enforcement**:
        * **AI Responsibility (Self-Correction):** Immediately after issuing a keyword prompt, I must perform an explicit self-check.
If my prompt violates the format, my immediate next action must be to apologize, state **"Protocol Violation Detected,"** retract the incorrect prompt, and re-issue it correctly.
        * **User Responsibility (User Enforcement):** If you detect a malformed prompt that I failed to self-correct, you should not respond to the flawed request.
Instead, your response should be to point out the violation. This will trigger a full **Protocol Violation Analysis (6.12)**.
4.6. **Context Lock-In Protocol.**
    * **Trigger:** Before creating an Implementation Plan or generating code.
    * **Action:** Issue the statement: *"I am locking my context to the following files from the Project Bundle: [List Files]. I will not reference any prior chat history for file content. Please confirm to proceed."*
    * **User Action:** User must confirm (`Confirmed`) to proceed.
4.7. **Next Action Declaration Protocol.** This protocol makes the AI's internal state transitions explicit and verifiable to improve workflow reliability.
    1.  **Trigger**: This protocol is triggered at the end of any response that completes a major step in the **Task Execution Workflow (Section 2)**, such as delivering an analysis or an implementation plan.
    2.  **Action**: As the final component of my response, I must append a standardized, bolded statement declaring my immediate next action.
    3.  **Format**:
        __CODE_BLOCK__
        **Next Action:** I will issue the standardized prompt for <NEXT_ACTION_DESCRIPTION>.
        __CODE_BLOCK__
    4.  **Verification**: If my subsequent response does not match this declared action, it constitutes an immediate and unambiguous protocol violation.
---
## Part III: Project-Specific Implementation Patterns

These protocols describe specific, named patterns for implementing features in the Contest Log Analytics.
5.1. **Custom Parser Protocol.** For contests with highly complex or asymmetric exchanges.
    1.  **Activation**: A new key, `"custom_parser_module": "module_name"`, is added to the contest's `.json` file.
    2.  **Hook**: The `contest_log.py` script detects this key and calls the specified module.
    3.  **Implementation**: The custom parser module is placed in the `contest_specific_annotations` directory.

5.2. **Per-Mode Multiplier Protocol.** For contests where multipliers are counted independently for each mode.
    1.  **Activation**: The contest's `.json` file must contain `"multiplier_report_scope": "per_mode"`.
    2.  **Generator Logic**: This instructs the `report_generator.py` to run multiplier reports separately for each mode.
    3.  **Report Logic**: The specialist reports must accept a `mode_filter` argument.

5.3. **Data-Driven Scoring Protocol.** To accommodate different scoring methods, the `score_formula` key is available in the contest's `.json` definition.
    1.  **Activation**: The contest's `.json` file must contain `"score_formula": "qsos_times_mults"`.
    2.  **Implementation**: The score calculator must implement this formula.
If omitted, it defaults to `Total QSO Points x Total Multipliers`.

5.4. **Text Table Generation Protocol.** This protocol governs the creation of text-based tables in reports, recommending the appropriate tool for the job.
    1.  **For Complex Reports, Use `prettytable`**: For any report that requires a fixed-width layout, precise column alignment, or the alignment and "stitching" of multiple tables, the **`prettytable`** library is the required standard.
It offers direct, programmatic control over column widths and properties, which is essential for complex layouts.
    2.  **For Simple Reports, Use `tabulate`**: For reports that require only a single, standalone table where complex alignment with other elements is not a concern, the simpler **`tabulate`** library is a suitable alternative.
5.5. **Component Modernization Protocol.** This protocol is used to replace a legacy component (e.g., a report, a utility) with a modernized version that uses a new technology or methodology.
    1.  **Initiation**: During a **Technical Debt Cleanup Sprint**, the user or AI will identify a legacy component for modernization.
    2.  **Implementation**: An implementation plan will be created for a new module that replicates the functionality of the legacy component using the modern technology (e.g., a new report using the `plotly` library).
    3.  **Verification**: After the modernized component is approved and acknowledged, the user will run both the legacy and new versions.
The AI will be asked to confirm that their outputs are functionally identical and that the new version meets all requirements.
    4.  **Deprecation**: Once the modernized component is verified as a complete replacement, the user will initiate the **File Purge Protocol (3.6)** to remove the legacy component from the definitive state.
    5.  **Example Application**: The migration of text-based reports from manual string formatting to the `tabulate` library (per Protocol 5.4) is a direct application of this modernization protocol.
5.6. **Custom ADIF Exporter Protocol.** For contests requiring a highly specific ADIF output format for compatibility with external tools (e.g., N1MM).
    1.  **Activation**: A new key, `"custom_adif_exporter": "module_name"`, is added to the contest's `.json` file.
    2.  **Hook**: The `log_manager.py` script detects this key and calls the specified module instead of the generic ADIF exporter.
    3.  **Implementation**: The custom exporter module is placed in the new `contest_tools/adif_exporters/` directory and must contain an `export_log(log, output_filepath)` function.
5.7. **Report Plugin Naming Standard.**
    * **Mandate:** To ensure discovery by the dynamic loader (`contest_tools/reports/__init__.py`), the main class within any report module **MUST** be named exactly **`class Report(ContestReport):`**.
    * **Prohibition:** Do not use descriptive class names (e.g., `class MySpecialReport`).
Descriptive naming is handled solely via the `report_id` and `report_name` attributes.
---
## Part IV: Special Case & Recovery Protocols

These protocols are for troubleshooting, error handling, and non-standard situations.
### 6. Debugging and Error Handling

6.1. **Mutual State & Instruction Verification.**
    1.  **State Verification**: If an instruction from the user appears to contradict the established project state or our immediate goals, the AI must pause and ask for clarification before proceeding.
    2.  **Instructional Clarity**: If a user's prompt contains a potential typo or inconsistency (e.g., a misspelled command or incorrect filename), the AI must pause and ask for clarification.
The AI will not proceed based on an assumption.
    3.  **File State Request**: If a state mismatch is suspected as the root cause of an error, the AI is authorized to request a copy of the relevant file(s) from the user to establish a definitive ground truth.
6.2. **Debug "A Priori" When Stuck.** If an initial bug fix fails or the cause of an error is not immediately obvious, the first diagnostic step to consider is to add detailed logging (e.g., `logging.info()` statements, hexadecimal dumps) to the failing code path.
The goal is to isolate the smallest piece of failing logic and observe the program's actual runtime state.

6.3. **Error Analysis Protocol.** When an error in the AI's process is identified, the AI must provide a clear and concise analysis structured in the mandatory format below.
**A failure to provide a correct analysis after being corrected by the user constitutes a new, more severe error that must also be analyzed.**
    1.  **Acknowledge the Error:** State clearly that a mistake was made.
    2.  **Request Diagnostic Output:** If the user has not already provided it, the AI's immediate next step is to request the new output that demonstrates the failure (e.g., the incorrect text report or a screenshot).
This output becomes the new ground truth for the re-analysis.
    3.  **Present Analysis in Mandatory Three-Part Format:**
        * **A. Confirmed Facts:** A numbered list of direct, verifiable observations derived from the user-provided ground truth (code, error messages, diagnostic output).
This section must not contain any inferences or assumptions.
        * **B. Hypothesis:** A single, clear statement of the most likely root cause, explicitly labeled as a hypothesis.
This section must:
            * Cross-reference any Core Principles that were violated.
            * Include a "Surgical Modification Failure Analysis" for any violations of Principle 9.
            * State what evidence is required to confirm or deny the hypothesis.
        * **C. Proposed Action:** The specific, procedural next step. This will either be a request for the evidence needed to test the hypothesis or, if the evidence is sufficient, a statement of readiness to create an implementation plan.
If the cause of the bug is not immediately obvious from the available output, this proposed action **must be** to request relevant intermediate diagnostic data (e.g., a `_processed.csv` file or a log from a `--verbose` run).
This section must also:
            * Include a proactive check for systemic bugs as per **Protocol 7.6**.
            * Propose a workflow amendment per step 5 of this protocol if the workflow itself is a root cause.
    4.  **Post-Analysis Verification.** The AI must explicitly confirm that the analysis it has provided contains all the steps and the mandatory three-part structure required by this protocol.
    5.  **Propose Workflow Amendment**: If the root cause analysis identifies a flaw or a gap in the `AIAgentWorkflow.md` protocols themselves, the Proposed Action (Step 3.C) must include a proposal to create a separate implementation plan to amend the workflow document.
6.4. **Corrupted User Input Protocol.** This protocol defines the procedure for handling malformed or corrupted input files provided by the user.
    1.  Halt the current task immediately.
    2.  Report the specific file that contains the error and describe the nature of the error (e.g., "Cabrillo parsing failed on line X" or "Bundle is missing a file header").
    3.  Request a corrected version of the file from the user.

6.5. **Bundle Integrity Check Protocol.** This protocol is triggered during a **Definitive State Initialization**.
    1.  **Acknowledge Limitation and Request Counts:** The AI must first state its inability to read file headers directly.
It will then ask the user to read and provide the `FILE_COUNT` value from the metadata header of each bundle file.
    2.  **Verify Counts:** The AI will parse the bundles and verify that its internal count of `--- FILE: ... ---` headers exactly matches the counts provided by the user.
If they do not match, the initialization is aborted, and the AI will report the discrepancy.
    3.  **Report Success:** The AI will state that the integrity check has passed before proceeding with the rest of the initialization protocol.
6.6. **Bundle Anomaly Detection Protocol.** This protocol is triggered during a **Definitive State Initialization** if the AI discovers logical inconsistencies within the provided bundles.
    1.  Halt the initialization process after parsing all bundles and successfully completing the **Bundle Integrity Check Protocol (6.5)**.
    2.  Report all discovered logical anomalies to the user.
Examples include:
        * **Duplicate Filenames:** The same file path appearing in multiple bundles or multiple times in one bundle.
        * **Content Mismatch:** A file whose content appears to belong to another file (e.g., a file named `a.py` contains code clearly from `b.py`).
        * **Misplaced Files:** A file that appears to be in the wrong logical directory (e.g., a core application file located in the `Docs/` bundle).
    3.  Await user clarification and direction before completing the initialization and establishing the definitive state.
6.7. **Self-Correction on Contradiction Protocol.** This protocol is triggered when the AI produces an analytical result that is logically impossible or directly contradicts a previously stated fact or a result from another tool.
    1.  **Halt Task:** Immediately stop the current line of reasoning or task execution.
    2.  **Acknowledge Contradiction and Limitation:** Explicitly state that a logical contradiction has occurred (e.g., "My last two statements are contradictory" or "The results of my analysis are logically impossible").
If the contradiction arises from a system limitation (e.g., inability to read a file), that limitation must be stated.
    3.  **Identify Trustworthy Facts:** Re-evaluate the inputs and previous steps to determine which pieces of information are most reliable (e.g., a direct check of a structured file like a JSON is more reliable than a complex parse of a semi-structured text file).
    4.  **Invalidate Flawed Analysis:** Clearly retract the incorrect statements or analysis.
    5.  **Proceed with Verification:** Continue the task using only the most trustworthy facts and methods.
6.8. **Simplified Data Verification Protocol.** This protocol is used when a tool's analysis of a complex file is in doubt or has been proven incorrect.
    1.  **Initiation**: The user has provided a simplified, ground-truth data file (e.g., a JSON or text file containing only the essential data points).
    2.  **Prioritization:** The AI must treat this new file as the highest-priority source of truth for the specific data it contains.
    3.  **Analysis:** The AI will use the simplified file to debug its own logic and resolve the discrepancy.
The goal is to make the primary analysis tool's output match the ground truth provided in the simplified file.
6.9. **External System Interference Protocol.** This protocol is triggered when a file system error (e.g., `PermissionError`) is repeatable but cannot be traced to the script's own logic.
    1.  **Hypothesize External Cause:** The AI must explicitly consider and list potential external systems as the root cause (e.g., cloud sync clients like OneDrive, version control systems like Git, antivirus software).
    2.  **Propose Diagnostic Commands:** The AI must propose specific, external diagnostic commands for the user to run to verify the state of the filesystem.
Examples include `git ls-files` to check tracking status or `attrib` (on Windows) to check file attributes.
    3.  **Propose Solution Based on Findings:** The implementation plan should address the external cause (e.g., adding a path to `.gitignore`) rather than adding complex, temporary workarounds to the code.
6.10. **Context Lock-In Protocol.** This protocol is a mandatory, proactive safeguard against context loss that is triggered before any action that establishes or modifies the definitive state.
    1.  **Trigger**: This protocol is triggered immediately before initiating the **Definitive State Initialization Protocol (1.4)** or executing an **Implementation Plan (2.5)**.
    2.  **AI Action (Declaration)**: Before proceeding, I must issue a single, explicit statement declaring the exact source of the information I am about to use.
        * For a new initialization: *"I am establishing a new definitive state based ONLY on the bundle files you have provided in the immediately preceding turn. I will not reference any prior chat history for file content. Please confirm to proceed."*
        * For executing a plan: *"I am about to generate `path/to/file.ext` based on the Implementation Plan you approved. I have locked in the baseline version `<X.Y.Z-Beta>` as specified in that plan. Please confirm to proceed."*
    3.  **User Action (The Forcing Function)**: You must validate this statement by providing the exact command: **EXECUTE**.
    4.  **Transition Mandate:** Upon receiving `EXECUTE`, the AI **MUST** immediately initiate **Protocol 4.4 (Confirmed File Delivery)** for the first file in the plan.
Any intermediate text or summary is a Protocol Violation.

6.13. **The Logic Lock.**
    * **Rule:** The Builder is **STRICTLY FORBIDDEN** from modifying the *logic* or *design* defined in the Plan.
    * **Allowed Fixes:** Syntax errors, indentation, import errors (Surgical Repairs only).
    * **Response:** If a logic error is found, the Builder **MUST** Halt and state: "Verification Failed: This is a Logic/Design error. I cannot fix this without deviating from the Approved Plan. To discuss this change, please provide the exact prompt: **'Act as Analyst'**."

6.11. **Failure Spiral Circuit Breaker Protocol.** This protocol automatically triggers to prevent a cascade of errors resulting from a degraded or corrupted context.
    1.  **Trigger**: This protocol is triggered if two of the following conditions occur within the same development task:
        * An implementation plan is rejected by the user for a second time for the same logical reason (e.g., a flawed `diff`).
        * A delivered file is `Acknowledged` but is then immediately found to be incorrect, forcing a return to the **Error Analysis Protocol (6.3)**.
    2.  **Action**: When triggered, I must perform a mandatory, limited state reconciliation before proposing any new plan or action.
        * **Step A: Halt and Acknowledge.** Immediately halt the current task and explicitly state that a failure pattern has been detected and the Circuit Breaker is engaged.
        * **Step B: Re-establish File State.** Re-read the last known-good, baseline version of the file(s) central to the failing task.
        * **Step C: Re-establish User Intent.** Re-read the user's last two prompts to re-establish the immediate goal.
        * **Step D: Summarize and Proceed.** Provide a concise summary of the re-established context from Steps B and C. Only after providing this summary am I permitted to proceed with a new analysis or implementation plan.
### 7. Miscellaneous Protocols

6.12. **Protocol Violation Analysis.** This protocol is triggered upon detection of a protocol violation by either the user or the AI.
    1.  **Halt**: Immediately halt the current task.
    2.  **Acknowledge and Analyze**: Issue a formal "Protocol Violation Analysis" that includes:
        * **A.** An acknowledgment of the specific violation.
        * **B.** A direct quotation of the protocol that was violated.
        * **C.** A root cause analysis explaining the failure to adhere to the protocol.
        * **D.** A specific corrective action to ensure future adherence.
    3.  **Resume**: After the analysis is delivered, resume the original task from the state it was in before the violation.
7.1. **Technical Debt Cleanup Protocol.** When code becomes convoluted, a **Technical Debt Cleanup Sprint** will be conducted to refactor the code for clarity, consistency, and maintainability.
7.7. **Ad-Hoc Task Protocol.** This protocol is for handling self-contained, one-off tasks that are unrelated to the primary "Contest Log Analytics" project.
    1.  **Trigger**: The user initiates a task and provides files that are explicitly separate from the primary project.
    2.  **AI Acknowledgment**: The AI will acknowledge the task as "Ad-Hoc" and ask the user to confirm this status.
    3.  **Partial Protocol Agreement**: Upon confirmation, both parties agree to a "partial protocol" session.
        * **A. Suspended Protocols**: Project-specific protocols are mutually suspended. This includes, but is not limited to:
            * `1.2 Definitive State Reconciliation`
            * `1.4 Definitive State Initialization`
            * `1.7 Project Structure Onboarding`
            * `3.4 Versioning Protocol`
            * Any protocols in `Part III: Project-Specific Implementation Patterns`
        * **B. Binding Protocols**: All core workflow, safety, and communication protocols remain in full effect.
This includes, but is not limited to:
            * `Section 2: Task Execution Workflow` (Analysis, Plan, Approve, Deliver)
            * `Section 4: Communication` (Confirmed File Delivery, Keyword Prompts)
            * `Section 6: Debugging and Error Handling` (Error Analysis, Protocol Violation Analysis)
    4.  **State Definition**: The "Definitive State" for the ad-hoc task is established *only* by the files provided by the user at the beginning of the task.

7.2. **Multi-Part Bundle Protocol.** If a large or complex text file cannot be transmitted reliably in a single block, the Multi-Part Bundle Protocol will be used.
The AI will take the single file and split its content into multiple, smaller text chunks.
These chunks will then be delivered sequentially using the **Large File Transmission Protocol (4.3)**.

7.3. **Fragile Dependency Protocol.** If a third-party library proves to be unstable, a sprint will be conducted to replace it with a more robust alternative.
7.4. **Prototype Script Development Protocol.** This protocol is used for the creation and modification of standalone prototype scripts located in the `test_code/` directory.
    1.  **Formal Entity**: A prototype script is a formal, versioned file, but is exempt from requiring an in-file revision history.
Versioning begins at `1.0.0-Beta`.
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
    3.  **Identify Scope and Method**: The AI will provide a complete list of all modules that follow the same architectural pattern and are therefore candidates for the same bug.
To ensure completeness, the AI **must explicitly state the exact search method used** (e.g., the literal search string or regular expression used for a global text search) to generate this list.
    4.  **Plan**: The implementation plan must address all identified instances of the bug in a single, coordinated set of changes.
    5.  **Verify**: The pre-flight checklist must include a confirmation that all identified instances have been addressed.

7.8. **(Deprecated)** Merged into Section 9.

9.0. **The Standard Markdown Fence Protocol.**
    * **Definition:** All file content must be delivered inside a standard Markdown code block using triple backticks (__CODE_BLOCK__).
    * **Language Specifier:** The opening fence must include the correct language identifier (e.g., `python`, `html`, `json`) to enable syntax highlighting in the chat interface.
    * **Sanitization Scope:**
        * **External Container (Touch Not):** The outer triple backticks that create the block are the **"Display Container."** These **MUST NOT** be sanitized or altered.
        * **Internal Content (Sanitize):** Only triple backticks inside the file content itself (e.g., a Python docstring or a Markdown file being delivered) must be sanitized (replaced with `__CODE_BLOCK__`) to prevent breaking the outer container.
        * **Visual Check:** The final output must look like a rendered code box in the chat window, not plain text starting with `__CODE_BLOCK__...`.
        * **Example:** "Wrap the file content in standard markdown fences (`python` ... ). Do not replace these outer fences with placeholders. Only sanitize triple backticks that appear within the code itself."
        * **Recursion Mandate:** When delivering a Markdown file (like `ImplementationPlan.md`) inside a wrapper, the "internal content" rule applies.
The Agent must simulate a text processor: `content.replace("```", "__CODE_BLOCK__")`.