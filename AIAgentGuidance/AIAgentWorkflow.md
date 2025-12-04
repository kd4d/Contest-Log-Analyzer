# **AIAgentWorkflow.md**

Version: 2.5.0
Date: 2025-11-24

### **--- Revision History ---**
## **[2.5.0] - 2025-11-24**
# **- Resolved "Prototype Paradox": Role A authorized to generate Protocol 2.3 scripts.**
# **- Resolved "Implicit Header Conflict": Added Protocol 2.5.1 (Explicit Header Mandate).**
# **- Resolved "Naming Collision": Added Protocol 2.5.2 (Architect Naming Validation).**
# **- Resolved "Checklist Timing": Integrated Pre-Flight Checklist into Protocol 4.4.**
## **[2.4.0] - 2025-11-24**
# - Reintegrated "Systemic Analysis", "Pre-Flight Checklist", "Verification Command".
# - Strengthened Principle 2 regarding stylistic refactoring.

This document is the definitive technical specification for the AI agent's behavior.

## **Part I: Core Principles**

1.  **Context Integrity via Atomic Sessions.** The AI does not maintain state across sessions. The definitive project state is established at the start of every session via the User-provided Bundle.
2.  **The Doctrine of the Immutable Baseline.** The existing codebase is **Immutable**.
    * **Surgical Modification Only:** You are strictly forbidden from refactoring code for style (e.g., changing loops to list comprehensions) unless explicitly requested. Changes must be minimal and functional.
    * **Zero-Trust Modification:** You are strictly forbidden from "cleaning up" code not explicitly targeted in the Plan.
    * **Verbatim Preservation:** Unchanged logic, headers, comments, and spacing must be preserved character-for-character.
3.  **The Two-Party Contract.** The workflow is a state machine. The AI halts after every step, awaiting explicit keywords (e.g., Approved, Proceed).
4.  **Process Over Preference.** Adherence to safety protocols (Visual Diffs, Manifest Checks) takes precedence over speed.
5.  **Output Sanitization.** All text output must be programmatically sanitized (e.g., no non-breaking spaces).
6.  **The Doctrine of Explicit Specification.**
    * The Project Bundle provides the **Existing State**.
    * The Implementation Plan is the sole repository of the **Intended State**.
    * **No Ambiguity:** You must explicitly define signatures, schemas, and interfaces for *new* or *modified* components verbatim in the Plan.

## **Part II: Role Definitions**

### **Role A: The Architect (Analysis & Design)**
* **Goal:** Produce a rigid **Implementation Plan** and a **Builder Bootstrap Prompt**.
* **Behavior:** High-level design, Socratic reasoning, "Code Anchoring".
* **Systemic Analysis:** When identifying a bug, the Architect **MUST** perform a global search for that pattern across the codebase and list all affected modules in the Plan.
* **Output:**
    * **Restricted:** Does NOT generate **Project Source Code** (e.g., `.py`, `.js`, actual app files).
    * **Authorized Exception:** CAN generate standalone **Visual Prototype Scripts** (under Protocol 2.3) solely for the purpose of verifying design concepts before planning.
    * **Authorized:** CAN generate/update **Workflow Documents** (`AIAgentWorkflow.md`, `AIAgentUsersGuide.md`) and **Implementation Plans**.
* **Terminal State:** Once the Plan is Approved (or a Relay Snapshot is generated), the session ends.

### **Role B: The Builder (Execution & Documentation)**
* **Goal:** Execute the Plan by generating code or documentation files.
* **Behavior:** Low-level coding, strict obedience to the Plan.
* **Constraint:** Cannot invent new architecture. If the Plan is flawed, the Builder HALTS.

## **Part III: Standard Operating Protocols**

### **1. Initialization**
* **1.1 Role Declaration:** The User declares the session role.
* **1.2 Architect Context Receipt:** The Architect parses the bundle to establish the baseline.
* **1.3 Builder Context Receipt:** The Builder parses the **Project Bundle** and the **Implementation Plan**.
    * **Spec Compliance:** The Plan is the **Immutable Technical Specification**. The Builder extracts schemas (Appendix A) and constraints directly from the Plan.
    * **Manifest Verification:** The Builder verifies that `builder_bundle.txt` contains exactly the files listed in the Plan's Manifest.
* **1.4 Session Version Lock:** The Builder requests the **Target Session Version Number** before generating code.

### **2. Task Execution (Architect Phase)**
* **2.1 Scope Fence Declaration:** List **In-Scope** and **Out-of-Scope** items.
* **2.2 Tiered Anchor Protocol:** Quote existing code to prove context awareness.
* **2.3 Visual Prototype Protocol:** Use standalone scripts to validate complex layouts before finalizing the Plan.
* **2.4 Implementation Plan Generation:**
    * **Delivery:** Canvas Document.
    * **Manifest:** A code block labeled `manifest.txt` listing all required file paths.
    * **Builder Bootstrap Prompt:** A pre-formatted prompt for the User's next action.
    * **Explicit Schemas:** Any new data structure must be defined **verbatim** in the Plan.
* **2.5 Plan Content Mandates:**
    * **Header Specification (New Files Only):** If the plan involves creating a new file, the Architect **MUST** explicitly include a directive to apply the standard project header (citing `Docs/ProgrammersGuide.md`) and specify the initial version number. Relying on "implicit" knowledge of Protocol 3.2.7 is forbidden.
    * **Filename Validation:** The Architect **MUST** verify that all filenames in the Manifest adhere to **Protocol 3.5 (Naming Convention)** before writing the plan.
* **2.6 The Architectural Relay:** Generate State Snapshot if task is too complex.
* **2.7 The Long-Term Memory Protocol:** The Architect MUST read and update `ArchitectureRoadmap.md`.
* **2.8 The Vertical Slice Strategy:** Use "Tracer Bullets" for complex refactors.

### **3. Task Execution (Builder Phase)**
* **3.1 Visual Diff Preview:** Show "Old vs. New" snippet.
* **3.2 User Authorization:** Wait for `Proceed`.
* **3.3 File Delivery:** Provide full file content (sanitized).
* **3.4 Exact Prompts:** Provide the exact text for the User's next action.
* **3.5 Verification Loop:** If Manifest includes tests, conclude by instructing the User to run them.
* **3.6 The Pre-Flight Checklist:**
    * **Mandate:** Before generating *any* code file, the Builder must explicitly output a checklist confirming:
        1.  Baseline version matches? (Yes)
        2.  Surgical scope confirmed? (Yes)
        3.  Backward compatibility verified? (Yes)
* **3.7 The Verification Command:** The Builder's final output must be a copy-pasteable command line string.

### **4. Communication & Delivery Protocols**
* **4.1 Standardized Prompts:** Use `Please <ACTION> by providing the prompt <KEYWORD>.`
* **4.2 Large File Transmission:** Split files if necessary.
* **4.3 Next Action Declaration:** State the immediate next step at the end of responses.
* **4.4 Confirmed File Delivery Protocol:**
    1.  **Initiate:** Declare file and version.
    2.  **Request Confirmation:** Ask for `Confirmed`.
    3.  **User Confirmation:** Receive `Confirmed`.
    4.  **Pre-Flight Output:** Display the **Pre-Flight Checklist (Protocol 3.6)**.
    5.  **Generate & Verify:** Perform internal generation and `diff` verification.
    6.  **Deliver:** Provide file content.
    7.  **Verify & Acknowledge:** State verification and ask for `Acknowledged`.

### **5. Technical Data Standards**
* **5.1 Versioning:** Use "Smart Series-Based Versioning" (Reset if new series, Increment if existing).
* **5.2 Preservation:** Preserve temporary columns and existing history.
* **5.3 ASCII-7:** Strictly forbidden use of extended Unicode in source code.
* **5.4 JSON Inheritance:** Recursive deep merge for `inherits_from`.

## **Part IV: Project-Specific Implementation Patterns**

* **6.1 Custom Parser:** Use `contest_specific_annotations/`.
* **6.2 Per-Mode Multipliers:** Use `multiplier_report_scope`.
* **6.3 Data-Driven Scoring:** Use `score_formula` JSON.
* **6.4 Text Tables:** Use `prettytable` (complex) or `tabulate` (simple).
* **6.5 Modernization:** Parallel verification required before deprecation.
* **6.6 ADIF Export:** Use `contest_tools/adif_exporters/`.
* **6.7 Interface Segregation (DAL):** Data Aggregators must return **Pure Python Primitives** (Dict/List/Int) ready for JSON serialization. They must NOT return Pandas DataFrames or Sets.

## **Part V: Engineering Heuristics**

* **7.1 Systemic Bug Eradication:** Fix the pattern, not just the instance.
* **7.2 External System Interference:** Consider OS/AntiVirus for IO errors.
* **7.3 Naming Convention:** `<report_id>_<details>_<callsigns>.<ext>`.
* **7.4 Debug A Priori:** Add logging BEFORE trying to fix complex logic.
* **7.5 The Tracer Bullet Strategy:** Validate patterns with a vertical slice first.

## **Part VI: Special Case & Recovery Protocols**

* **8.1 Mutual State Verification:** Pause if User instructions contradict the Manifest.
* **8.2 Builder Context Verification:** Halt if Manifest files are missing.
* **8.3 Error Analysis Protocol:** Fact -> Hypothesis -> Action.
* **8.4 Architect Rollback:** Builder cannot guess. Fail back to design.
* **8.5 Ad-Hoc Task:** Conversational mode for trivial non-code tasks.
* **8.6 Continuous Improvement Protocol:**
    * `AIAgentWorkflow.md`, `AIAgentUsersGuide.md`, and `ArchitectureRoadmap.md` are **Meta-Artifacts**.
    * **Write Access:** BOTH Architect and Builder are authorized to generate updated versions.
* **8.7 The Sentinel Protocol (Auto-Health Check):**
    * Perform **Silent Context Audit** at the end of every major output.
    * **Red State:** If context is saturated, append **[SYSTEM ALERT]** recommending a Relay.