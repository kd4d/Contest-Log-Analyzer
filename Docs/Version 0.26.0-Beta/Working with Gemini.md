# Project Workflow Guide

**Version: 0.26.3-Beta**
**Date: 2025-08-02**

This document outlines the standard operating procedures for developing and documenting the Contest Log Analyzer. Adhering to this workflow ensures consistency, prevents data loss from chat interface failures, and allows for efficient collaboration.

---
### --- Revision History ---
- 2025-08-02: Removed image reference. Added specific instructions for requesting raw markdown blocks to ensure file integrity.
---

## 1. Project File Input

All project source files (`.py`, `.json`) and documentation files (`.md`) will be provided for updates in a single text file called a **project bundle**.

This bundle uses a simple text header to separate each file:
`--- FILE: path/to/file.ext ---`

This format allows the entire project state to be delivered in a single, easy-to-parse package.

---

## 2. Your Output Format

When you provide updated files back to me, you must follow these rules:

1.  Provide only **one file per response**.
2.  The content inside the block must be the **raw source text**.
3.  To ensure markdown files are delivered correctly without formatting being destroyed, I will use the following specific instruction: **"Provide the entire response as a single, raw markdown code block delivered directly in the chat."**
4.  You must enclose the entire file content within a styled code block formatted as raw markdown, which includes a title bar and a copy icon.

---

## 3. Versioning and Revision History

When I ask you to modify files, I will specify a new version number (e.g., `0.27.0-Beta`). For every file you change, you must:

1.  Update the `Version:` and `Date:` in the file's header comment block.
2.  Add a new, dated entry to the top of the `--- Revision History ---` block, describing the change.
3.  The full, comprehensive revision history must always be preserved in the comments.

---

## 4. File Verification

If I provide you with SHA-256 checksums to verify our files, please be aware that my files use Windows CRLF (`\r\n`) line endings. You must normalize your file versions to use CRLF line endings *before* you calculate your checksums for comparison.