Filename: "Docs/Working with Gemini.md"

# Project Workflow Guide

**Version: 0.28.21-Beta**
**Date: 2025-08-04**

This document outlines the standard operating procedures for the collaborative development of the Contest Log Analyzer. **The primary audience for this document is the Gemini AI agent.**

**Its core purpose is to serve as a persistent set of rules and context.** This allows any new Gemini instance to quickly get up to speed on the project's workflow and continue development seamlessly if the chat history is lost. Adhering to this workflow ensures consistency and prevents data loss.
---

### Guiding Principles

1.  **Trust the User's Diagnostics.** When the user reports a bug, their description of the symptoms (e.g., "the multipliers are too high," "the report is all zeros") should be treated as the ground truth. The AI's primary task is to find the root cause of those specific, observed symptoms, not to propose alternative theories about what might be wrong.

2.  **Debug "A Priori" When Stuck.** If an initial bug fix fails, do not simply try to patch the failed fix. Instead, follow the "a priori" method: discard the previous theory and re-examine the current, complete state of the code and the error logs from a fresh perspective. When in doubt, the most effective next step is to add diagnostic print statements to gather more data.

3.  **Prefer Logic in Code, Not Data.** The project's design philosophy is to keep the `.json` definition files as simple, declarative maps. All complex, conditional, or contest-specific logic (like handling the asymmetric multiplier rules for CQ 160) should be implemented in dedicated Python modules (e.g., `cq_160_multiplier_resolver.py`). This makes the system more robust and easier to maintain.
---

## 1. Project File Input

All project source files (`.py`, `.json`) and documentation files (`.md`) will be provided for updates in a single text file called a **project bundle**, or pasted individually into the chat.
The bundle uses a simple text header to separate each file:
`--- FILE: path/to/file.ext ---`

---

## 2. AI Output Format

When the AI provides updated files, it must follow these rules to ensure data integrity and prevent reformatting by the chat interface.

1.  **One File Per Response**: Only one file will be delivered in a single response.
2.  **Raw Source Text**: The content inside the delivered code block must be the raw source text of the file.
3.  **Code File Delivery**: For code files (e.g., `.py`, `.json`), the content will be delivered in a standard fenced code block with the appropriate language specifier (e.g., ` ```python ... ``` `).
4.  **Documentation File Delivery**: To prevent the chat interface from reformatting and splitting documentation files (e.g., `.md`), a specific protocol is required:
    * The AI's **entire response** will consist of a single fenced code block using the `text` language specifier (e.g., ` ```text ... ``` `). No conversational text will precede or follow this block.
    * Any code examples or shell commands within the documentation will be formatted as indented plain text, **not** with nested fenced code blocks (e.g., ` ```bash`). This is critical to ensure the file is delivered as one unbroken block.

---

## 3. Versioning

1.  When a file is modified, its patch number (the third digit) will be incremented. For example, a change to a `0.28.20-Beta` file will result in version `0.28.21-Beta` for that file.
2.  Document versions will be kept in sync with their corresponding code files.
3.  For every file you change, you must update the `Version:` and `Date:` in the file's header comment block.

---

## 4. File and Checksum Verification

1.  The user's file system uses Windows CRLF (`\r\n`) line endings. The AI's output can use standard LF (`\n`). The AI must be aware of this difference when comparing checksums.
2.  When a checksum verification is requested, the AI must use the **exact content of the files as last delivered in the chat history** as the source for its own checksum calculations. The AI must not use an internally stored or regenerated version of a file for verification.

---

## 5. Development Protocol

1.  When creating or modifying any project file (e.g., `.py`, `.json`, `.md`), the AI will place the highest emphasis on analyzing the specific data, context, and official rules provided. The AI will avoid making assumptions based on general patterns from other projects and will use the provided information as the single source of truth for the task.
2.  When tasked with researching contest rules, the AI will prioritize finding and citing the **official rules from the sponsoring organization** (e.g., NCJ for NAQP, CQ Magazine for CQ contests).

---

## 6. Code Modification Protocol

1.  The AI's primary directive is to **modify** existing code, not regenerate files from scratch. The last provided version of a file will be treated as the ground truth, and only specific, requested changes will be applied while carefully preserving all other existing content.
2.  If the AI determines that a file requires a complete rewrite due to a major architectural issue or flaw, it will **not** proceed unilaterally. It will first propose the rewrite and request permission to proceed.

---

## 7. Canvas Interface Fallback

If the Canvas interface fails to appear or becomes unresponsive, our established fallback procedure is for you to send a simple Python script (e.g., 'Hello, world!') to the Canvas to restore its functionality.

---

## 8. Communication Protocol

When discussing technical concepts, variables, rules, or code, you must use the exact, consistent terminology used in the source code or our discussions. Do not use conversational synonyms or rephrase technical terms. Precision and consistency are paramount.

---

## 9. Multi-File Change Protocol

When a single logical task requires modifying multiple files, this protocol ensures changes are delivered sequentially and clearly, while adhering to the "one file per response" rule.

1.  **Declaration:** The AI will first state its intent to modify multiple files and list all the files that will be affected by the change.
2.  **Sequential Delivery:** The AI will provide the first updated file. The response will end with a clear statement, such as: "Please confirm when you are ready for the next file."
3.  **Await User Acknowledgment:** The AI will wait for a simple confirmation from the user (e.g., 'OK', 'Ready', 'next') before sending the next file.
4.  **Iteration:** The AI will then provide the next file in the sequence, repeating this turn-by-turn process until all declared files have been delivered.
5.  **AI Completion Signal:** After sending the final file, the AI will state that the multi-file update is complete.
6.  **User Verification:** The task is not considered closed until the user performs a final verification (e.g., running a test or a checksum comparison) and confirms success.
---

## 10. Protocol for Large File Sets

1.  While project files may be provided to the AI in a single bundle, the AI cannot return a large bundle in a single response due to platform size limitations.
2.  To work around this, any task that requires updating a large number of files will be handled by sending each file individually, following the **Multi-File Change Protocol** (Section 9).
3.  The agreed-upon safe size for a project bundle is less than **37 kilobytes**.
---

## 11. Context Checkpoint Protocol

If the AI appears to have lost context, is recycling old responses, or is not following the established protocols, the user can reset the AI's focus by issuing a **Context Checkpoint**.

1.  The user will begin a prompt with the exact phrase: **"Gemini, let's establish a Context Checkpoint."**
2.  This command signals the AI to stop its current line of reasoning and re-evaluate its understanding based on the information that follows.
3.  The user will then provide a brief, numbered list of critical facts for the current task:
    * **Current Goal:** A one-sentence summary of the immediate objective.
    * **Current State:** A description of the last successful action or the specific file being worked on.
    * **Key Rule:** The most important rule, bug, or constraint for the current task.
---

## 12. Technical Debt Cleanup Protocol

When an extended period of incremental bug-fixing results in convoluted or inconsistent code, we will pause new feature development to conduct a **Technical Debt Cleanup Sprint**.

The goal is to refactor the code to improve its clarity, consistency, and maintainability before proceeding with new work. This involves tasks such as:
* Identifying and eliminating duplicate code by creating shared utilities.
* Unifying inconsistent logic (e.g., standardizing how all time-series reports handle data).
* Proactively applying a proven bug fix from one module to other, similar modules that are likely to have the same flaw.