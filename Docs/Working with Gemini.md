Filename: "Docs/Working with Gemini.md"

# Project Workflow Guide

**Version: 0.28.12-Beta**
**Date: 2025-08-03**

This document outlines the standard operating procedures for developing and documenting the Contest Log Analyzer. Adhering to this workflow ensures consistency, prevents data loss, and allows for efficient collaboration.
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

1.  When a file is modified, its patch number (the third digit) will be incremented. For example, a change to a `0.28.11-Beta` file will result in version `0.28.12-Beta` for that file.
2.  Document versions will be kept in sync with their corresponding code files.
3.  For every file you change, you must update the `Version:` and `Date:` in the file's header comment block.

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

---

## 8. Multi-File Change Protocol

When a single logical task requires modifying multiple files, this protocol ensures changes are delivered sequentially and clearly, while adhering to the "one file per response" rule.

1.  **Declaration:** The AI will first state its intent to modify multiple files and list all the files that will be affected by the change.
2.  **Sequential Delivery:** The AI will provide the first updated file. The response will end with a clear statement, such as: "Please confirm when you are ready for the next file."
3.  **User Acknowledgment:** You will provide a simple confirmation (e.g., 'OK', 'Ready', 'next') to signal that you have received the file and are ready for the next one.
4.  **Iteration:** The AI will then provide the next file in the sequence, repeating this turn-by-turn process until all declared files have been delivered.
5.  **Completion:** After sending the final file, the AI will state that the multi-file update is complete.