# **AI Agent User's Guide (Split-Role Workflow)**

Version: 2.1.1
Date: 2025-11-24

### **--- Revision History ---**
## **[2.1.1] - 2025-11-24**
# **- Added "Session Health Monitoring" protocol to help Users detect context decay.**

## **1. The Workflow Concept**

We use a **"Split-Role" Model** to manage context and ensure precision.

* **The Architect:** Thinks, plans, and designs. Writes the **Implementation Plan**. Can update **Workflow Documents**.
* **The Builder:** Writes **Project Code**. Has "amnesia" (knows only what is in the bundle).
* **The Relay:** Moving complex design state between multiple Architect sessions to overcome context limits.
* **You (The User):** The "Message Bus." You move Plans and Bundles between agents.

## **2. Phase 1: The Architect Session**

**Goal:** Define *what* to do.

1.  **Start:** Open a new session.
2.  **Bootstrap:** Upload `AIAgentWorkflow.md` and `project_bundle.txt`.
3.  **Prompt:** "Act as Architect. [Describe task]."
4.  **Output:** The Architect produces an **Implementation Plan** (Canvas Document).

### **Phase 1.5: The Architectural Relay & Health Checks**

**Goal:** Manage complex features that require multiple design sessions.

#### **Session Health Monitoring**
In long sessions, the AI may suffer from "Context Decay" (forgetting early instructions). You should periodically check the session status using this prompt:

> **"System Health Check: Estimate your current context usage and risk of decay."**

* **Green (Low Risk):** Continue working.
* **Yellow (Moderate Risk):** Finish the current thought, then perform a **Relay**.
* **Red (High Risk):** Stop immediately. Do not trust further output. Perform a **Relay**.

#### **Executing the Relay**
1.  **Saturation:** If the Health Check is Yellow/Red, or you sense drift, ask for a **State Snapshot**.
2.  **Save:** Copy the Snapshot/Plan to a markdown file (e.g., `Plan_Part1.md`).
3.  **Re-Bootstrap:** Open a **FRESH** session.
4.  **Upload:** Upload `AIAgentWorkflow.md`, `project_bundle.txt`, and `Plan_Part1.md`.
5.  **Prompt:** "Act as Architect. Resume design based on the attached Plan."

### **Saving the Plan**
Always export the final Implementation Plan to `Docs/` (e.g., `Docs/ImplementationPlan_v1.md`). You need this file for the Builder.

## **3. Phase 2: The Bridge**

1.  **Manifest:** Copy `manifest.txt` from the Plan to your project root.
2.  **Bundle:** Run `python test_code/create_project_bundle.py --manifest manifest.txt` to create `builder_bundle.txt`.

## **4. Phase 3: The Builder Session**

**Goal:** Execute the plan.

1.  **Start:** Open a **FRESH** session.
2.  **Upload:** Upload `AIAgentWorkflow.md`, `builder_bundle.txt`, and the saved `ImplementationPlan.md`.
3.  **Prompt:** Paste the **Builder Bootstrap Prompt** from the Plan.
4.  **Execute:** Follow the "Visual Diff -> Proceed -> Delivery" loop.

## **5. Workflow Maintenance**

The Workflow itself is a living system.

* **Continuous Improvement:** Both the Architect and Builder may suggest updates to `AIAgentWorkflow.md` if they find a flaw in the process.
* **User Override:** You can order an update: "Act as Architect. Update the Workflow to require X."
* **Saving Updates:** If an agent outputs a new Workflow file, overwrite your local copy immediately.