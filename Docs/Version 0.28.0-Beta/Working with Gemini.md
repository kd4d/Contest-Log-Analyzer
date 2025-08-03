# Project Workflow Guide

**Version: 0.28.8-Beta**
**Date: 2025-08-03**

This document outlines the standard operating procedures for developing and documenting the Contest Log Analyzer. Adhering to this workflow ensures consistency, prevents data loss, and allows for efficient collaboration.

---
### --- Revision History ---
- 2025-08-03: Added Section 7, Communication Protocol, to mandate the use of precise and consistent technical terminology.
- 2025-08-02: Clarified rules for versioning, markdown file delivery, and line endings.
- 2025-08-02: Updated workflow with new versioning scheme, file delivery instructions, and debugging/Canvas protocols.
---

## 1. Project File Input

All project source files (`.py`, `.json`) and documentation files (`.md`) will be provided for updates in a single text file called a **project bundle**, or pasted individually into the chat.

The bundle uses a simple text header to separate each file:
`--- FILE: path/to/file.ext ---`

---

## 2. Your Output Format

When you provide updated files back to me, you must follow these rules:

1.  Provide only **one file per response**.
2.  The content inside the block must be the **raw source text**.
3.  To ensure markdown files are delivered correctly without formatting being destroyed, I will use the following specific instruction: **"Provide the entire response as a single, raw markdown code block delivered directly in the chat."**
4.  When following the instruction above, you must enclose the entire file content within a standard fenced code block, using `markdown` as the language specifier (e.g., ```markdown ... ```). This will preserve the raw source text by preventing the chat interface from rendering it.

---

## 3. Versioning and Revision History

1.  All new and modified files will start with version **`0.28.0-Beta`**. When a specific file is modified, its patch number (the third digit) will be incremented. For example, a change to a `0.28.0-Beta` file will result in version `0.28.1-Beta` for that file.
2.  Document versions will be kept in sync with their corresponding code files.
3.  For every file you change, you must update the `Version:` and `Date:` in the file's header comment block and add a new, dated entry to the top of the `--- Revision History ---` block describing the change.

---

## 4. File Verification

My file system uses Windows CRLF (`\r\n`) line endings. This is important for SHA-256 checksum verification. Your output can use standard LF (`\n`) line endings, and you should just be aware of this difference if we need to compare checksums.

---

## 5. Debugging Protocol

When a bug or regression is identified, you will place a greater emphasis on analyzing the specific data and context provided before proposing a solution, rather than relying on general patterns.

---

## 6. Canvas Interface Fallback

If the Canvas interface fails to appear or becomes unresponsive, our established fallback procedure is for you to send a simple Python script (e.g., 'Hello, world!') to the Canvas to restore its functionality.

---

## 7. Communication Protocol

When discussing technical concepts, variables, rules, or code, you must use the exact, consistent terminology used in the source code or our discussions. Do not use conversational synonyms or rephrase technical terms. Precision and consistency are paramount.