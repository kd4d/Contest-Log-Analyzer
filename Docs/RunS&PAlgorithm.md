# Run/S&P/Unknown Classification Algorithm

**Version: 0.30.30-Beta**
**Date: 2025-08-05**

---
### --- Revision History ---
## [0.30.30-Beta] - 2025-08-05
# - No functional changes. Synchronizing version numbers.
## [0.30.0-Beta] - 2025-08-05
# - Initial release of Version 0.30.0-Beta.
# - Standardized all project files to a common baseline version.
---

[cite_start]The purpose of this algorithm is to analyze a contest log and infer the operator's activity for each contact, classifying it as one of three types: **Run**, **Search & Pounce (S&P)**, or **Unknown**. [cite: 2227] [cite_start]The analysis is performed independently for each operating "stream"—a unique combination of a band and mode (e.g., 20M CW is one stream, 40M SSB is another). [cite: 2228] [cite_start]The algorithm uses a two-pass approach. [cite: 2229]
---

### Pass 1: Initial Classification (Run vs. S&P)

[cite_start]The first pass uses a "sticky run" state machine to make an initial classification. [cite: 2229]
1.  [cite_start]**Identifying a Run**: A "run" is defined as a period of high-rate activity on a single frequency. [cite: 2230] [cite_start]The algorithm identifies the start of a run when it detects a minimum number of QSOs (typically 3) occurring on the same frequency within a short time window (e.g., 10 minutes). [cite: 2231]
2.  [cite_start]**The "Sticky" State**: Once a run is identified, the algorithm enters a "run state." [cite: 2232] [cite_start]It assumes the operator is still running and will continue to classify all subsequent QSOs on that frequency as **Run**. [cite: 2233]
3.  [cite_start]**Breaking a Run**: The run state is maintained until one of two conditions is met: [cite: 2234]
    * [cite_start]**Time-Out**: A significant amount of time (e.g., 2 minutes) passes without a QSO on the run frequency. [cite: 2234]
    * [cite_start]**Frequency Change**: The operator makes several consecutive QSOs on other frequencies, indicating they have moved to search for new contacts. [cite: 2235]
4.  [cite_start]**S&P Classification**: Any QSO that is not part of an identified run is initially classified as **S&P**. [cite: 2236]
---

### Pass 2: Reclassification of Low-Rate QSOs

[cite_start]The second pass refines the results by identifying periods of very low activity where the operator's intent is ambiguous. [cite: 2237]
1.  [cite_start]**Reviewing S&P QSOs**: The algorithm re-examines only the QSOs that were classified as **S&P** in the first pass. [cite: 2238]
2.  [cite_start]**Checking the Rate**: For each S&P QSO, it looks at the number of other contacts made in a time window both before and after it (e.g., 15 minutes). [cite: 2239]
3.  [cite_start]**Reclassifying to Unknown**: If the QSO rate in the surrounding period is below a certain threshold, the activity is considered too low to be definitively classified. [cite: 2240] [cite_start]In this case, the QSO's status is changed from S&P to **Unknown**. [cite: 2241]

[cite_start]The final output is a log where every contact is annotated with its inferred operating style: **Run**, **S&P**, or **Unknown**. [cite: 2242]