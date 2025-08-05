# Project Workflow Guide

**Version: 0.30.0-Beta**
**Date: 2025-08-05**

---
### --- Revision History ---
## [0.30.0-Beta] - 2025-08-05
# - Initial release of Version 0.30.0-Beta.
# - Standardized all project files to a common baseline version.
---

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
`