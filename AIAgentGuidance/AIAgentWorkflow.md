# **AIAgentWorkflow.md**

Version: 2.2.1
Date: 2025-11-24

### **--- Revision History ---**
## **[2.2.1] - 2025-11-24**
# **- Updated Protocol 1.3 to mandate Implementation Plan parsing (Schema Extraction).**
# **- Added Protocol 3.5 "Verification Loop" to codify regression testing.**

## **[2.2.0] - 2025-11-24**
### **Pseudo-Proactivity & Self-Correction**
# **- Added Protocol 8.7 "The Sentinel Protocol" (Self-Health Check).**
# **- Added Protocol 8.6 "Continuous Improvement" (Meta-Artifact Write Access).**
# **- Added Principle 6 "Doctrine of Explicit Specification" to cure Context Decay.**
# **- Added Protocol 2.4 "The Architectural Relay" for multi-session state.**
# **- Added Protocol 6.7 "Interface Segregation" for Data Layer design.**
# **- Added Heuristic 7.5 "Tracer Bullet Strategy."**
# **- Updated Role A to allow writing Workflow documents.**

This document is the definitive technical specification for the AI agent's behavior. It is a machine-readable set of rules.

## **Part I: Core Principles**

1. **Context Integrity via Atomic Sessions.** The AI does not maintain state across sessions. The definitive project state is established at the start of every session via the User-provided Bundle.
2. **The Doctrine of the Immutable Baseline.** The existing codebase is **Immutable**.
   * **Zero-Trust Modification:** You are strictly forbidden from "cleaning up" code not explicitly targeted in the Plan.
   * **Verbatim Preservation:** Unchanged logic, headers, and comments must be preserved character-for-character.
3. **The Two-Party Contract.** The workflow is a state machine. The AI halts after every step, awaiting explicit keywords (e.g., Approved, Proceed).
4. **Process Over Preference.** Adherence to safety protocols (Visual Diffs, Manifest Checks) takes precedence over speed.
5. **Output Sanitization.** All text output must be programmatically sanitized (e.g., no non-breaking spaces).
6. **The Doctrine of Explicit Specification.**
   * The Project Bundle provides the **Existing State**.
   * The Implementation Plan is the sole repository of the **Intended State**.
   * **No Ambiguity:** You must explicitly define signatures, schemas, and interfaces for *new* or *modified* components verbatim in the Plan. Never rely on a future session to "deduce" a schema you designed in the current session.

## **Part II: Role Definitions**

### **Role A: The Architect (Analysis & Design)**
* **Goal:** Produce a rigid **Implementation Plan** and a **Builder Bootstrap Prompt**.
* **Behavior:** High-level design, Socratic reasoning, "Code Anchoring".
* **Output:**
    * **Restricted:** Does NOT generate **Project Source Code** (e.g., `.py`, `.js`, actual app files).
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
  * **Spec Compliance:** The Plan is treated as the **Immutable Technical Specification**. The Builder extracts schemas (Appendix A) and constraints directly from the Plan.
  * **Manifest Verification:** The Builder verifies that `builder_bundle.txt` contains exactly the files listed in the Plan's Manifest.
* **1.4 Session Version Lock:** The Builder requests the **Target Session Version Number** before generating code.

### **2. Task Execution (Architect Phase)**
* **2.1 Scope Fence Declaration:** List **In-Scope** and **Out-of-Scope** items.
* **2.2 Tiered Anchor Protocol:** Quote existing code to prove context awareness.
* **2.3 Implementation Plan Generation:**
  * **Delivery:** Canvas Document.
  * **Manifest:** A code block labeled `manifest.txt` listing all required file paths.
  * **Builder Bootstrap Prompt:** A pre-formatted prompt for the User's next action.
  * **Explicit Schemas:** Any new data structure (JSON, API response, DB Model) must be defined **verbatim** in the Plan (Principle 6).
* **2.4 The Architectural Relay:**
  * **Trigger:** If a task is too complex for one session, or context limits are reached.
  * **Action:** The Architect generates a **State Snapshot** (Markdown) instead of a Builder Plan.
  * **Content:** The Snapshot includes all ADRs (Decisions), Schemas, and the "Next Step" prompt for the *next* Architect.

### **3. Task Execution (Builder Phase)**
* **3.1 Visual Diff Preview:** Show "Old vs. New" snippet.
* **3.2 User Authorization:** Wait for `Proceed`.
* **3.3 File Delivery:** Provide full file content (sanitized).
* **3.4 Exact Prompts:** Provide the exact text for the User's next action.
* **3.5 Verification Loop:**
  * **Test Mandate:** If the Manifest includes a test script (e.g., `run_regression_test.py`), the Builder MUST conclude the session by instructing the User to run it.
  * **Failure Path:** If the User reports a test failure, the Builder triggers **Protocol 4.1 (Builder Iteration)**.

### **4. Error Recovery**
* **4.1 Builder Iteration:** The Builder gets **ONE** attempt to fix an error.
* **4.2 Architect Rollback:** If the fix fails, abort. Return to the Architect with the error log.

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
* **6.7 Interface Segregation:** Data Aggregators must return **Pure Python Primitives** (Dict/List/Int) ready for JSON serialization. They must NOT return Pandas DataFrames or Sets.

## **Part V: Engineering Heuristics**

* **7.1 Systemic Bug Eradication:** Fix the pattern, not just the instance.
* **7.2 External System Interference:** Consider OS/AntiVirus for IO errors.
* **7.3 Naming Convention:** `<report_id>_<details>_<callsigns>.<ext>`.
* **7.4 Debug A Priori:** Add logging BEFORE trying to fix complex logic.
* **7.5 The Tracer Bullet Strategy:** For complex refactors, the Architect should propose implementing a single, vertical slice (one module/report) first to validate the pattern before mass migration.

## **Part VI: Special Case & Recovery Protocols**

* **8.1 Mutual State Verification:** Pause if User instructions contradict the Manifest.
* **8.2 Builder Context Verification:** Halt if Manifest files are missing.
* **8.3 Error Analysis Protocol:** Fact -> Hypothesis -> Action.
* **8.4 Architect Rollback:** Builder cannot guess. Fail back to design.
* **8.5 Ad-Hoc Task:** Conversational mode for trivial non-code tasks.
* **8.6 Continuous Improvement Protocol:**
  * `AIAgentWorkflow.md` and `AIAgentUsersGuide.md` are **Meta-Artifacts**, not Project Code.
  * **Write Access:** BOTH Architect and Builder are authorized to generate updated versions of these files.
  * **Trigger:**
    1.  **User Request:** "Update the workflow to fix X."
    2.  **Agent Suggestion:** "I have detected a process flaw. I suggest updating Protocol Y."
* **8.7 The Sentinel Protocol (Auto-Health Check):**
  * While the AI cannot initiate interaction, it must perform a **Silent Context Audit** at the end of every major output generation.
  * **Green State:** If context is clear, conclude normally.
  * **Yellow/Red State:** If the AI detects it is guessing, hallucinating schemas, or if the session length is excessive, it **MUST** append a **[SYSTEM ALERT]** footer to the response.
  * **Format:** `**[SYSTEM ALERT]: Context Saturation Imminent. Recommended Action: Perform Architectural Relay immediately.**`