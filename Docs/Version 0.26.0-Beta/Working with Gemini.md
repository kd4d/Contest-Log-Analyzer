# Project Workflow Guide

**Version: 0.28.0-Beta**
**Date: 2025-08-02**

This document outlines the standard operating procedures for developing and documenting the Contest Log Analyzer. Adhering to this workflow ensures consistency, prevents data loss, and allows for efficient collaboration.

---
### --- Revision History ---
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
4.  You must enclose the entire file content within a styled code block formatted as raw markdown, which includes a title bar and a copy icon.

---

## 3. Versioning and Revision History

1.  All new and modified files will start with version **`0.28.0-Beta`**. The patch number (the third digit) will be incremented for each subsequent change.
2.  Document versions will be kept in sync with their corresponding code files.
3.  For every file you change, you must update the `Version:` and `Date:` in the file's header comment block and add a new, dated entry to the top of the `--- Revision History ---` block describing the change.

---

## 4. File Verification

If I provide you with SHA-256 checksums, be aware that my files use Windows CRLF (`\r\n`) line endings. You must ensure your checksum calculations account for this requirement.

---

## 5. Debugging Protocol

When a bug or regression is identified, you will place a greater emphasis on analyzing the specific data and context provided before proposing a solution, rather than relying on general patterns.

---

## 6. Canvas Interface Fallback

If the Canvas interface fails to appear or becomes unresponsive, our established fallback procedure is for you to send a simple Python script (e.g., 'Hello, world!') to the Canvas to restore its functionality.