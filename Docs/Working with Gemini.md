Filename: "Docs/Working with Gemini.md"

# Project Workflow Guide

**Version: 0.28.17-Beta**
**Date: 2025-08-03**

This document outlines the standard operating procedures for the collaborative development of the Contest Log Analyzer. **The primary audience for this document is the Gemini AI agent.**

**Its core purpose is to serve as a persistent set of rules and context.** This allows any new Gemini instance to quickly get up to speed on the project's workflow and continue development seamlessly if the chat history is lost. Adhering to this workflow ensures consistency and prevents data loss.
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

1.  When a file is modified, its patch number (the third digit) will be incremented. For example, a change to a `0.28.16-Beta` file will result in version `0.28.17-Beta` for that file.
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
5.  **Completion:** After sending the final file, the AI will state that the multi-file update is complete.
---

## 10. Protocol for Large File Sets

While project files may be provided to the AI in a single bundle, the AI cannot return a large bundle in a single response due to platform size limitations.

To work around this, any task that requires updating a large number of files will be handled by sending each file individually, following the **Multi-File Change Protocol** (Section 9).