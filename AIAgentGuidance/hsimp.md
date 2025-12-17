**Version:** 1.0.0
**Target:** 4.19.0

# Implementation Plan - Workflow Amendment (Header Standard)

This plan amends `AIAgentWorkflow.md` to explicitly include the **Standard Project Header** template directly within the protocol text. This eliminates the need for the AI to "consult" external documentation to find the required format, preventing future compliance failures.

## Proposed Changes

### 1. Modified File: `AIAgentWorkflow.md`
**Purpose:** Hard-code the mandatory Python file header template into the primary operating manual.
* **Update Protocol 3.2.7:** Replace the instruction to "consult `Docs/ProgrammersGuide.md`" with the literal header template itself.
* **Constraint:** This ensures the header format is always in the AI's immediate context window.

## Affected Modules Checklist
* `AIAgentWorkflow.md`

## Pre-Flight Check
* **Inputs:** The verified standard header template from `Docs/ProgrammersGuide.md`.
* **Expected Outcome:** `AIAgentWorkflow.md` will contain the verbatim text block required for all Python files.
* **Backward Compatibility:** No code changes; purely a process documentation update.
* **Surgical Modification:** Only Protocol 3.2.7 is being altered.

--- BEGIN DIFF ---
@@ -420,7 +420,24 @@
     6.  **Post-Delivery Protocol Verification.** Immediately following any file delivery, the AI must explicitly state which sub-protocol from Section 3.2 it followed and confirm that its last output was fully compliant.
-    7.  **Python Header Standard Mandate.** All Python files (`.py`) generated or modified by the AI must conform to the standard header definition found in `Docs/ProgrammersGuide.md`. Before generating a Python file, the AI must consult this guide to ensure compliance.
+    7.  **Python Header Standard Mandate.** All Python files (`.py`) generated or modified by the AI must begin with the following standard header block. The AI must populate the `{placeholders}` with the correct module-specific data.
+        __CODE_BLOCK__ python
+        # {filename}.py
+        #
+        # Purpose: {A concise, one-sentence description of the module's primary responsibility.}
+        #
+        # Author: Gemini AI
+        # Date: {YYYY-MM-DD}
+        # Version: {x.y.z-Beta}
+        #
+        # Copyright (c) 2025 Mark Bailey, KD4D
+        # Contact: kd4d@kd4d.org
+        #
+        # License: Mozilla Public License, v. 2.0
+        #          (https://www.mozilla.org/MPL/2.0/)
+        #
+        # This Source Code Form is subject to the terms of the Mozilla Public
+        # License, v. 2.0. If a copy of the MPL was not distributed with this
+        # file, You can obtain one at http://mozilla.org/MPL/2.0/.
+        #
+        # --- Revision History ---
+        # [{version}] - {YYYY-MM-DD}
+        # - {Description of changes}
+        __CODE_BLOCK__
 3.3. **Context Audit (Mandatory)**: Builder cross-references the Plan's requirements against `builder_bundle.txt`.
     * **Pass:** Proceed to Pre-Flight.
--- END DIFF ---