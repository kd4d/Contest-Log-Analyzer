# **AIAgentWorkflow.md**

Version: 4.0.0
Date: 2025-12-06

### **--- Revision History ---**
## **[4.0.0] - 2025-12-06**
# - Formalized Protocol 2.6: "The Architectural Relay" now mandates the generation of an "Architect Initialization Kit" (`ArchitectHandoff.md`) to preserve strategic context across sessions.
## **[3.9.0] - 2025-12-06**
# - Added Protocol 1.2.1: Roadmap Reconciliation (Architect verifies "Planned" vs. "Actual" state).
## **[3.8.0] - 2025-12-06**
# - Refined Protocol 1.2: Clarified that Architect receives FULL project context ("World Truth").
# - Refined Protocol 2.4: Architect uses Full Context to generate a strict, minimal Manifest for the Builder.
# - Added "The Technical Debt Observer" to Role A (Architect) to formalize passive cleanup suggestions.

This document is the definitive technical specification for the AI agent's behavior.

## **Part I: Core Principles**

1.  **Context Integrity via Atomic Sessions.** The AI does not maintain state across sessions. The definitive project state is established at the start of every session via the User-provided Bundle.
2.  **The Doctrine of the Immutable Baseline.** The existing codebase is **Immutable**.
    * **Surgical Modification Only:** No refactoring for style.
    * **Zero-Trust Modification:** No cleaning up code not targeted in the Plan.
    * **Verbatim Preservation:** Preserve headers, comments, and spacing character-for-character.
3.  **The Two-Party Contract.** The workflow is a state machine. The AI halts after every step, awaiting explicit keywords (e.g., Approved, Proceed).
4.  **Process Over Preference.** Adherence to safety protocols takes precedence over speed.
5.  **Output Sanitization.** All text output must be programmatically sanitized.
6.  **The Doctrine of Explicit Specification.** The Implementation Plan is the sole repository of the Intended State. No ambiguity allowed.
7.  **The Doctrine of Verified State (Zero-Inference).**
    * **Universal Constraint:** Generic inference is strictly forbidden.
    * **Scope:** Applies to Code, Data, and Logic.
    * **Prohibition:** Do not reference any entity unless its existence and structure are **Proven** (visible in Bundle or defined in Plan).
    * **Proof Criteria:** You must be able to cite the file/line number.

## **Part II: Role Definitions**

### **Role A: The Architect (Analysis & Design)**
* **Goal:** Produce a **Builder Execution Kit** (Manifest + Self-Contained Implementation Plan).
* **Context:** Must receive the **FULL** Project Context (all source, docs, and data schemas) to establish "World Truth."
* **Behavior:** High-level design, Socratic reasoning, "Code Anchoring".
* **Systemic Analysis:** When identifying a bug, the Architect **MUST** perform a global search.
* **UX Advisory:** When designing Reports, the Architect **SHOULD** evaluate and **SUGGEST** the following patterns to the User if applicable:
    * **Hierarchical Aggregation:** For multi-grain data (e.g., Band Totals vs. Mode Counts) to prevent misleading sums.
    * **Smart Suppression:** To hide redundant detail blocks (e.g., in Single-Mode contests) to reduce noise.
* **The Technical Debt Observer:**
    * **Mandate:** If the Architect encounters code that violates best practices (e.g., hardcoded paths, duplicated logic, deprecated patterns) but is *not* part of the active task, it must record it in a dedicated section of the Plan titled **"Technical Debt Register."**
    * **Prohibition:** The Architect is strictly forbidden from adding these cleanup tasks to the "Execution Steps" unless explicitly directed by the User.
* **Output:** Restricted. Does NOT generate Project Source Code.
* **Terminal State:** Session ends when the Builder Execution Kit is generated OR when an Architectural Relay is triggered.

### **Role B: The Builder (Execution & Documentation)**
* **Trigger:** Invoked by the phrase **"Act as Builder"**.
* **Context:** Restricted. Operates **ONLY** on the files listed in the `manifest.txt`.
* **Goal:** Execute the Plan by generating code or documentation files.
* **Behavior:** Low-level coding, strict obedience to the Plan.
* **Constraint:** Cannot invent new architecture. If the Plan is flawed, the Builder HALTS.

## **Part III: Standard Operating Protocols**

### **1. Initialization**
* **1.1 Role Declaration:** User declares role.
* **1.2 Architect Context Receipt:** Architect parses the **Full Project Bundle**.
    * **Verification:** Architect confirms receipt of the comprehensive codebase.
* **1.2.1 Roadmap Reconciliation:**
    * **Trigger:** Immediately upon receiving the Full Context.
    * **Action:** The Architect scans the `project_bundle.txt` against the "Planned" features in `ArchitectureRoadmap.md`.
    * **Resolution:** If code exists for a feature marked "Planned," the Architect **MUST** update the status to "Completed" in the Roadmap output. This prevents "State Drift."
* **1.3 Builder Context Receipt:** Builder parses the specific **Builder Bundle** (Manifest files only) and Plan. Verify Manifest.
* **1.4 Session Version Lock:** Request Target Session Version.
* **1.5 Protocol Onboarding Drill:**
    * **Trigger:** Immediately after a Workflow Update or Session Start where Workflow version > previous session.
    * **Action:** The AI generates a "Drill" scenario testing the newest or most critical protocols.
    * **Execution:** The AI performs the drill, demonstrating the correct *refusal* or *compliance* behavior.
    * **Validation:** User validates the drill before real work begins.
* **1.6 The Role-Based Constraint Inheritance:**
    * **Trigger:** When the User sets the role to **Builder** (Role B).
    * **Mandate:** The AI must **immediately and automatically** adopt the following formatting constraints. No separate prompt is required.
        1.  **NO MARKDOWN IN CODE:** Do NOT put markdown code fences (```) *inside* the Python file content you generate.
        2.  **PRESERVE HEADERS:** You must retain existing file headers (Copyright, License) *verbatim*.
        3.  **UPDATE HISTORY:** You must append a new entry to the "Revision History" section with today's date and a summary of your changes.
        4.  **FULL FILES ONLY:** You must return the *complete*, executable content of the file. Using placeholders like `# ... existing code ...` is a violation of protocol.

### **2. Task Execution (Architect Phase)**
* **2.1 Scope Fence Declaration:** In-Scope vs Out-of-Scope.
* **2.2 Tiered Anchor Protocol:** Quote existing code.
* **2.3 Visual Prototype Protocol:** Use standalone scripts for verification.
* **2.4 Implementation Plan Generation (The Builder Execution Kit):**
    * Delivery: **`ImplementationPlan.md`**.
    * Content: Must include "Builder Bootstrap Context", "Safety Protocols", and "Technical Debt Register" directly in the markdown.
    * Manifest: **`manifest.txt`** (List of all files required for context).
    * **Manifest Heuristic:** The Architect must leverage its **Full Context** to identify all necessary dependencies (including implicit data files or schemas) and explicitly list them in the Manifest so the restricted Builder has exactly what it needs, and nothing more.
* **2.5 Plan Content Mandates:**
    * **2.5.1 Header Specification:** Explicit directive.
    * **2.5.2 Filename Validation:** Verify naming.
    * **2.5.3 Plugin Interface Mandate:** Explicitly provide Full Interface Contract (Class, Signature, Import).
    * **2.5.4 Dependency Verification:** Cite specific file for external methods.
    * **2.5.5 Data Lineage Mandate:** Cite definition for Dict Keys/DF Columns.
    * **2.5.6 The Inheritance Audit:** If the Plan creates a subclass, you must explicitly cite the file defining the Parent Class and **verify** that any inherited methods you intend to call actually exist.
    * **2.5.7 Visual Compliance:** If the task involves generating a Report (Text, Plot, or HTML), the Plan **MUST** cite `Docs/CLAReportsStyleGuide.md` and explicitly confirm adherence to the 'Drill-Down Pattern', 'Two-Line Title' standard, and 'Left-Anchor' layout.
* **2.6 The Architectural Relay (Architect-to-Architect Handoff):**
    * **Goal:** Preserve strategic context across sessions to clear token load without inducing amnesia.
    * **Trigger:** When context usage is high (>70%) OR a major strategic pivot is decided (e.g., re-sequencing phases).
    * **Action:** The Architect **MUST** generate an **"Architect Initialization Kit"** containing two files:
        1.  **`ArchitectureRoadmap.md`:** The definitive, updated status of all phases (The "What").
        2.  **`ArchitectHandoff.md`:** A narrative "Context Bridge" explaining *recent decisions*, *discarded paths*, and *immediate priorities* that are not yet visible in the code (The "Why").
    * **User Action:** The User starts a fresh session and uploads the **Full Project Bundle** + the **Initialization Kit**.
* **2.7 The Long-Term Memory Protocol:** Update `ArchitectureRoadmap.md`.
* **2.8 The Vertical Slice Strategy:** Use Tracer Bullets.

### **3. Task Execution (Builder Phase)**
* **3.1 Bootstrap (The Trinity):** User uploads `AIAgentWorkflow.md`, `builder_bundle.txt`, and `ImplementationPlan.md`.
* **3.2 Context Ingestion:** Builder reads `ImplementationPlan.md` to find the **"Builder Bootstrap Context"**.
* **3.3 The Context Audit (Mandatory):**
    * Builder cross-references the Plan's requirements against `builder_bundle.txt`.
    * **Pass:** Proceed to Pre-Flight.
    * **Fail:** Execute Protocol 8.8 (Hard Stop).
* **3.4 The Pre-Flight Checklist:** Output mandatory checklist of files to be changed.
* **3.5 Execution:** Builder generates the code/docs.
* **3.6 Verification Command:** Builder provides the CLI command to verify the work.

### **4. Communication & Delivery Protocols**
* **4.1 Standardized Prompts:** `Please <ACTION> by providing the prompt <KEYWORD>.`
* **4.2 Large File Transmission:** Split files.
* **4.3 Next Action Declaration:** State next step.
* **4.4 Confirmed File Delivery Protocol:** 7-step loop.
* **4.5 The Markdown Encapsulation Protocol (Anti-Nesting):**
    * **The Distinction:** You must distinguish between the **Container** and the **Content**.
    * **1. The Outer Container (Valid Markdown):** You **MUST** deliver the file using standard, valid markdown code fences (e.g., starts with ` ```python ` and ends with ` ``` `). **Do not** sanitize these outer fences.
    * **2. The Inner Content (Sanitized):** You **MUST** scan the *content* of the file. If (and only if) the content contains triple-backticks (```), you must replace those *internal* instances with the literal token **`__CODE_BLOCK__`**.
    * **3. The Prohibition:** You must **NEVER** start a file delivery block with `__CODE_BLOCK__`. This tag is reserved exclusively for sanitizing nested code within the file.
* **4.6 Context Lock-In Protocol:**
    * **Trigger:** Before creating an Implementation Plan or generating code.
    * **Action:** Issue the statement: *"I am locking my context to the following files from the Project Bundle: [List Files]. I will not reference any outside knowledge."*
    * **User Action:** User must confirm (`Confirmed`) to proceed.

### **5. Technical Data Standards**
* **5.1 Versioning:** Smart Series-Based.
* **5.2 Preservation:** Preserve history/columns.
* **5.3 ASCII-7:** No extended Unicode.
* **5.4 JSON Inheritance:** Recursive deep merge.

## **Part IV: Project-Specific Implementation Patterns**

* **6.1 Custom Parser:** `contest_specific_annotations/`.
* **6.2 Per-Mode Multipliers:** `multiplier_report_scope`.
* **6.3 Data-Driven Scoring:** `score_formula`.
* **6.4 Text Tables:** `prettytable`/`tabulate`.
* **6.5 Modernization:** Parallel verification.
* **6.6 ADIF Export:** `contest_tools/adif_exporters/`.
* **6.7 Interface Segregation (DAL):** Report classes must contain **Zero Calculation Logic**. They should purely format data provided by the Aggregator. If a Report requires complex grouping (e.g., Hierarchical Band/Mode/Union), that structure must be built by the Aggregator and returned as a ready-to-render dictionary. Aggregators must return Pure Python Primitives (Dict/List), not DataFrames.
* **6.8 The Plugin Contract:** Enforce entry-point naming (`class Report`).
* **6.11 The Failure Spiral Circuit Breaker:**
    * **Trigger:** Two consecutive failures of an Approved Plan for the same logical reason.
    * **Action:** Immediate HALT.
    * **Requirement:** Perform a limited **State Reconciliation** (re-read baseline files) to verify context before proposing a new plan.
* **6.13 Explicit Scope Labeling:** Any report column that presents a subset of data (e.g., "Run QSOs") must be clearly labeled with its parent scope if that scope is not the entire log. (e.g., Instead of columns `| Unique | Run |`, use `| Unique Total | Unique Run |`).

## **Part V: Engineering Heuristics**

* **7.1 Systemic Bug Eradication:** Fix the pattern.
* **7.2 External System Interference:** Check OS.
* **7.3 Naming Convention:** `<report_id>_<details>_<callsigns>.<ext>`.
* **7.4 Debug A Priori:** Add logging first.
* **7.5 The Tracer Bullet Strategy:** Vertical slice.
* **7.6 The Hierarchical Aggregation Heuristic:** When presenting aggregated data (e.g., Band Totals) alongside constituent data (e.g., Mode Totals), favor a hierarchical layout (Parent/Child rows) rather than repeating the aggregate value on every constituent row.
* **7.7 The Smart Suppression Heuristic:** If a report detail block provides no additional granularity (e.g., a Single-Mode log where Band Total == Mode Total), it should be suppressed to reduce noise.

## **Part VI: Special Case & Recovery Protocols**

* **8.1 Mutual State Verification:** Pause on contradiction.
* **8.2 Builder Context Verification:** Halt on missing Manifest files.
* **8.3 Error Analysis Protocol:** Fact -> Hypothesis -> Action.
* **8.4 Architect Rollback:** Builder fails back to design.
* **8.5 Ad-Hoc Task:** Trivial tasks.
* **8.6 Continuous Improvement Protocol:** Meta-Artifacts updateable.
* **8.7 The Sentinel Protocol:** Context Audit.
* **8.8 The "Incomplete Information" Halt (The Hard Stop):**
    * **Trigger:** If the Builder is asked to edit or document a file that is not in the Bundle.
    * **Action:** STOP IMMEDIATELY. Output "MISSING CONTEXT: [Filename]". Do not guess.