# **AI Agent User's Guide (Split-Role Workflow)**

Version: 3.2.0
Date: 2025-12-06

### **--- Revision History ---**
## **[3.2.0] - 2025-12-06**
# - Updated Phase 1 Output: Added "Reconciliation Updates" to Roadmap expectations.
# - Added "Troubleshooting State Drift" section.
## **[3.1.0] - 2025-12-06**
# - Updated Phase 1 Bootstrap: Architect receives Full Context (Source + Docs + Data).
# - Added "Handling Technical Debt" to Phase 1 Output.
# - Refined Phase 3: Explicit check for "Manifest Heuristics" success.

## **1. The Workflow Concept**

We use a **"Funnel Architecture"** to manage context:

* **The Architect (Maximum Context):** Sees the **Full World Truth** (Code, Docs, Data). Designs the solution and identifies *implicit* dependencies. Produces the **Builder Execution Kit**.
* **The Builder (Minimum Viable Context):** Sees **Only** what is in the Manifest. This strictly limits hallucinations and forces adherence to the Plan.
* **You (The User):** The "Message Bus" and "FileSystem." You move files between agents and persist state.

## **2. Phase 1: The Architect Session**

**Goal:** Define *what* to do and *how* it fits the long-term vision.

1.  **Start:** Open a new session.
2.  **Bootstrap (The World Truth):** Upload the **FULL** project context to ensure the Architect sees everything:
    * `AIAgentWorkflow.md` (The Rules)
    * **`project_bundle.txt`** (The Source Code)
    * **`documentation_bundle.txt`** (The Docs)
    * **`data_bundle.txt`** (The Data Schemas)
    * **`ArchitectureRoadmap.md`** (The Long-Term Memory)
3.  **Prompt:** "Act as Architect. [Describe task]."
4.  **Output:** The Architect produces the **Builder Execution Kit**:
    * **Implementation Plan:** The specific blueprints for the immediate task.
    * **Manifest:** A precise list of files (Code + Data) required for the Builder.
    * **Technical Debt Register:** (Passive) A list of cleanup opportunities noticed during analysis.
    * **Updated Architecture Roadmap:** (State Reconciliation) The Architect will auto-update items from "Planned" to "Completed" if it sees the code in the bundle.

### **Crucial Step: Persistence**
* **Roadmap:** If the Architect outputs an updated `ArchitectureRoadmap.md` (even if it's just status updates), **overwrite your local copy immediately**. This prevents the Agent from re-planning work that is already done.
* **Technical Debt:** Review the "Technical Debt Register" in the Plan. If an item is critical, manually add it to `ArchitectureRoadmap.md` as a future task. **Do not** ask the Builder to fix these now unless they block the current task.

### **Phase 1.5: The Architectural Relay & Health Checks**

**Goal:** Manage complex features that require multiple design sessions.

#### **Session Health Monitoring**
In long sessions, check for "Context Decay":
> **"System Health Check: Estimate your current context usage and risk of decay."**

* **Green:** Continue.
* **Yellow/Red:** Perform a Relay immediately.

#### **Executing the Relay**
1.  **Saturation:** Ask for a **State Snapshot**.
2.  **Save:** Copy the Snapshot to a file (e.g., `Plan_Part1.md`).
3.  **Re-Bootstrap:** Open a **FRESH** session.
4.  **Upload:** All Bootstrap files from Phase 1 + `Plan_Part1.md`.
5.  **Prompt:** "Act as Architect. Resume design based on the attached Plan and Roadmap."

## **3. Phase 2: The Bridge**

1.  **Manifest:** Copy `manifest.txt` from the Plan to your project root.
2.  **Bundle:** Run `python test_code/create_project_bundle.py --manifest manifest.txt` to create the targeted **`builder_bundle.txt`**.
    * *Note:* This bundle will be significantly smaller than the Architect's context. This is intentional.

## **4. Phase 3: The Builder Session**

**Goal:** Execute the plan with rigorous verification.

1.  **Start:** Open a **FRESH** session.
2.  **Upload:** Upload the **Trinity**:
    * `AIAgentWorkflow.md`
    * `builder_bundle.txt` (The Targeted Context)
    * `ImplementationPlan.md`
3.  **Prompt:** Simply type: **"Act as Builder"**.
    *(Do not paste complex prompts; the Builder reads the Plan directly.)*
4.  **Confirm Context:** The Builder will list the files it is locking to.
    * **Action:** Reply with **"Confirmed"**.
5.  **Execute:** Follow the delivery loop.
    * **Pre-Flight Checklist:** The Builder MUST output a checklist of files to change. If skipped, stop.
    * **Proceed:** Type `Proceed` to authorize file generation.
6.  **Sanitize (CRITICAL):**
    * When the Builder delivers a file (especially Python scripts with docstrings), it may replace internal triple-backticks with `__CODE_BLOCK__` to prevent chat rendering errors.
    * **Action:** After saving the file, **Find & Replace** `__CODE_BLOCK__` with real triple-backticks (` ``` `) in your text editor.
7.  **Verify:** At the very end of the session, the Builder MUST provide a specific **Verification Command** (e.g., `python main_cli.py ...`). Run this command immediately to verify the work.

## **5. Workflow & Roadmap Maintenance**

* **Workflow (`AIAgentWorkflow.md`):** Defines *how the Agent behaves*. Update this if the process feels broken.
* **Roadmap (`ArchitectureRoadmap.md`):** Defines *where the Project is going*. Update this when you finish a Phase or change strategy.
* **User Responsibility:** You are the guardian of these files. The AI cannot save them to your disk; you must copy/paste them when the AI generates updates.

## **6. Troubleshooting**

* **"Missing Context" Error:** If the Architect claims a feature doesn't exist but you know it does:
    1.  Check your `project_bundle.txt` generation. Did you include the right directory?
    2.  Check `AIAgentWorkflow.md` version. Ensure Protocol 1.2 is active.
* **"Hallucinated Methods" in Builder:** The Manifest was likely incomplete.
    1.  Fail the session.
    2.  Go back to Architect.
    3.  Explicitly ask: "Update the Manifest to include the file defining [Method Name]."