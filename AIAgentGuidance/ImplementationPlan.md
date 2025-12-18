**Version:** 1.0.0
**Target:** 4.20.0

# Implementation Plan - Hardened Output Sanitization

This plan updates `AIAgentWorkflow.md` to strictly enforce the "Search and Replace" logic for Markdown sanitization. It moves the critical instruction from the appendix (Protocol 9.0) directly into the execution triggers (Protocols 3.2.4, 2.4.4, and 2.4.6) to prevent nested fence collisions during file delivery.

## Proposed Changes

### `AIAgentWorkflow.md`

#### [Modification] Revision History
* Add entry for version **4.20.0**.

#### [Modification] Protocol 3.2.4 (AI Output Format)
* **Update Item 4:** Explicitly mandate the literal replacement of triple backticks with `__CODE_BLOCK__` before encapsulation. This removes the reliance on looking up Protocol 9.0.

#### [Modification] Protocol 2.4.4 (The Compliance Stamp)
* **Update Sanitization Check:** Change the required output from a simple "PASS/FAIL" to the specific confirmation string: `PASS (Internal fences sanitized to __CODE_BLOCK__)`.

#### [Modification] Protocol 2.4.6 (The Structural Gate)
* **Update Sanitization Check:** Refine the logic gate to explicitly look for triple backticks inside the bundle.

#### [Modification] Protocol 9.0 (The Standard Markdown Fence Protocol)
* **Add Recursion Mandate:** Add a bullet point strictly defining the handling of Markdown-within-Markdown.

---

## Surgical Changes

### `AIAgentWorkflow.md`

**1. Update Revision History**
* **Action:** Append new version 4.20.0.

**2. Update Protocol 2.4.4**
* **Action:** Update the expected output format for the Sanitization check.

**3. Update Protocol 2.4.6**
* **Action:** Strengthen the internal verification question.

**4. Update Protocol 3.2.4**
* **Action:** Replace Item 4 with the new strict mandate.

**5. Update Protocol 9.0**
* **Action:** Add the Recursion Mandate bullet point.

---

### Surgical Change Verification

**Ground Truth Declaration:** The following `diff` is generated against the definitive baseline **Version 4.19.0**.

__CODE_BLOCK__ diff
--- AIAgentWorkflow.md
+++ AIAgentWorkflow.md
@@ -6,6 +6,13 @@
 **Date:** 2025-12-17
 ---
 ### --- Revision History ---
+## [4.20.0] - 2025-12-18
+### Changed
+# - Updated Protocol 3.2.4 to explicitly mandate `__CODE_BLOCK__` replacement for Markdown delivery.
+# - Updated Protocol 2.4.4 to require specific confirmation string for sanitization.
+# - Updated Protocol 2.4.6 to strengthen the Structural Gate logic.
+# - Updated Protocol 9.0 to include a Recursion Mandate for nested fences.
 ## [4.19.0] - 2025-12-17
 ### Changed
 # - Updated Protocol 3.2.7 to explicitly include the Standard Project Header template, removing the external dependency on Docs/ProgrammersGuide.md.
@@ -213,7 +220,7 @@
     * **2.4.4 The Compliance Stamp:** Every Builder Execution Kit MUST define a visible "Compliance Report" section validating:
         * **Protocol 2.1.1 (Architecture):** PASS/FAIL
         * **Protocol 3.3 (Context Audit):** PASS/FAIL
-        * **Protocol 3.2.4 (Sanitization):** PASS/FAIL
+        * **Protocol 3.2.4 (Sanitization):** **PASS (Internal fences sanitized to `__CODE_BLOCK__`)**
     * **2.4.5 The Manifest Isolation:** The `manifest.txt` list MUST be provided in its own distinct code block, separate from the `cla-bundle` block, to facilitate easy extraction by the user.
     * **2.4.6. The Structural Gate (The "Meta-Pre-Flight").**
         * **Trigger:** Immediately before generating the final response containing a Builder Execution Kit.
@@ -226,7 +233,7 @@
             * **If NO:** The generation is **FORBIDDEN**. I must abort and restart the response generation with the correct wrapper.
             * **If YES:** Proceed with delivery.
-        * **Sanitization Check:** "Are all internal code fences within the plan replaced with `__CODE_BLOCK__`?"
+        * **Sanitization Check:** "Have I visibly replaced every internal triple-backtick in the `ImplementationPlan.md` content with the string `__CODE_BLOCK__`? If I see a triple-backtick inside the `cla-bundle`, I must stop and fix it."
 2.5. **Plan Content Mandates**: The Plan must contain the following sections for each file to be modified, formatted with bolded headers:
     **0. Plan Metadata Header:** Every Implementation Plan must begin with a standardized metadata block containing:
     * **`**Version:**`**: The revision number of the Plan document itself (e.g., `1.0.0`).
@@ -341,9 +348,7 @@
     2.  **Raw Source Text**: The content inside the delivered code block must be the raw source text of the file.
     3.  **Code File Delivery**: For code files (e.g., `.py`, `.json`), the content will be delivered in a standard fenced code block with the appropriate language specifier.
-    4.  **Markdown File Delivery**: Documentation files (`.md`) must be delivered inside a `cla-bundle` specified code block, strictly adhering to **Protocol 9.0 (The Standard Markdown Fence Protocol)** regarding the sanitization of internal code fences.
-        * **Clarification**: This substitution is a requirement of the AI's web interface. The user will provide files back with standard markdown fences, which is the expected behavior.
+    4.  **Markdown File Delivery**: Documentation files (`.md`) must be delivered inside a `cla-bundle` specified code block. **CRITICAL:** To prevent nested rendering errors, you must perform a literal Find & Replace on the content *before* encapsulation: **All instances of triple backticks (```) within the file content MUST be replaced with the placeholder `__CODE_BLOCK__`.**
     5.  **Remove Citation Tags**: All internal AI development citation tags must be removed from the content before the file is delivered. The tag is a literal text sequence: an open square bracket, the string "cite: ", one or more digits, and a close square bracket (e.g.,). This pattern does not include Markdown backticks.
     6.  **Post-Delivery Protocol Verification.** Immediately following any file delivery, the AI must explicitly state which sub-protocol from Section 3.2 it followed and confirm that its last output was fully compliant.
     7.  **Python Header Standard Mandate.** All Python files (`.py`) generated or modified by the AI must begin with the following standard header block. The AI must populate the `{placeholders}` with the correct module-specific data.
@@ -578,4 +583,5 @@
         * **Internal Content:** Only triple backticks inside the file content itself (e.g., a Python docstring or a Markdown file being delivered) must be sanitized (replaced with `__CODE_BLOCK__`) to prevent breaking the outer container.
     * **Visual Check:** The final output must look like a rendered code box in the chat window, not plain text starting with `__CODE_BLOCK__...`.
     * **Example:** "Wrap the file content in standard markdown fences (`python` ... ). Do not replace these outer fences with placeholders. Only sanitize triple backticks that appear within the code itself."
+    * **Recursion Mandate:** When delivering a Markdown file (like `ImplementationPlan.md`) inside a wrapper, the "internal content" rule applies. The Agent must simulate a text processor: `content.replace("```", "__CODE_BLOCK__")`.
__CODE_BLOCK__

## Pre-Flight Check

* **Inputs:** `AIAgentWorkflow.md` (Version 4.19.0).
* **Expected Outcome:** A hardened workflow document that explicitly details the string replacement logic for nested markdown fences.
* **Mental Walkthrough:** I will update the Revision History, then replace the text in Protocols 3.2.4, 2.4.4, 2.4.6, and 9.0 with the new, specific mandates.
* **State Confirmation:** I will include the confirmation prompt.
* **Backward Compatibility:** This is a documentation update; it clarifies behavior but does not break existing file formats.
* **Surgical Modification:** Only the specified protocols are being updated.
* **Visual Compliance:** N/A (Text file).
* **Post-Generation Verification:** I have verified that this plan includes all mandatory sections.

**Next Action:** I will issue the standardized prompt for approval.