# Run/S&P/Unknown Classification Algorithm

**Version:** 0.47.4-Beta
**Date:** 2025-08-23
**Last Updated:** 2026-01-24
**Category:** Algorithm Spec
**Compatible with:** up to v1.0.0-alpha.10

---
### --- Revision History ---
## [0.47.4-Beta] - 2026-01-24
### Changed
- Updated "Compatible with" field to include project version v1.0.0-alpha.10

## [0.47.4-Beta] - 2025-08-23
### Changed
- Clarified the Pass 2 reclassification logic to specify the precise dual-window check and QSO threshold used in the code.
## [0.30.30-Beta] - 2025-08-05
# - No functional changes. Synchronizing version numbers.
## [0.30.0-Beta] - 2025-08-05
# - Initial release of Version 0.30.0-Beta.
# - Standardized all project files to a common baseline version.
---

The purpose of this algorithm is to analyze a contest log and infer the operator's activity for each contact, classifying it as one of three types: **Run**, **Search & Pounce (S&P)**, or **Unknown**.
The analysis is performed independently for each operating "stream"—a unique combination of a band and mode (e.g., 20M CW is one stream, 40M SSB is another).
The algorithm uses a two-pass approach.
---

### Pass 1: Initial Classification (Run vs. S&P)

The first pass uses a "sticky run" state machine to make an initial classification.
1.  **Identifying a Run**: A "run" is defined as a period of high-rate activity on a single frequency.
The algorithm identifies the start of a run when it detects a minimum number of QSOs (typically 3) occurring on the same frequency within a short time window (e.g., 10 minutes).
2.  **The "Sticky" State**: Once a run is identified, the algorithm enters a "run state."
It assumes the operator is still running and will continue to classify all subsequent QSOs on that frequency as **Run**.
3.  **Breaking a Run**: The run state is maintained until one of two conditions is met:
    * **Time-Out**: A significant amount of time (e.g., 2 minutes) passes without a QSO on the run frequency.
    * **Frequency Change**: The operator makes several consecutive QSOs on other frequencies, indicating they have moved to search for new contacts.
4.  **S&P Classification**: Any QSO that is not part of an identified run is initially classified as **S&P**.
---

### Pass 2: Reclassification of Low-Rate QSOs

The second pass refines the results by identifying periods of very low activity where the operator's intent is ambiguous.
1.  **Reviewing S&P QSOs**: The algorithm re-examines only the QSOs that were classified as **S&P** in the first pass.
2.  **Checking the Rate**: For each S&P QSO, the algorithm independently checks two separate 15-minute windows: one immediately preceding the QSO and one immediately following it.
3.  **Reclassifying to Unknown**: A QSO is reclassified from S&P to **Unknown** only if the number of contacts in the preceding window is below a threshold (4 QSOs) **AND** the number of contacts in the following window is also below that same threshold.

The final output is a log where every contact is annotated with its inferred operating style: **Run**, **S&P**, or **Unknown**.