# Run/S&P/Unknown Classification Algorithm

**Version:** 0.50.0-Beta
**Date:** 2026-02-02
**Category:** Algorithm Spec

---
### --- Revision History ---
## [0.50.0-Beta] - 2026-02-02
### Changed
- Synchronized Pass 1 and Pass 2 thresholds to 10 minutes and 3 QSOs to eliminate the misclassification of slow-rate stationary activity as S&P.
- Updated "Pass 2" logic to ensure low-rate activity is correctly flagged as "Unknown."

---

## 1. Purpose
The purpose of this algorithm is to analyze a contest log and infer the operator's activity for each contact, classifying it as **Run**, **Search & Pounce (S&P)**, or **Unknown**. Analysis is performed independently for each operating "stream" (a unique combination of MyCall, Band, and Mode).

---

## 2. Pass 1: Initial Classification (Sticky Run Logic)
The first pass uses a state machine to detect "Runs" based on frequency stability and activity rate.

* **Run Identification**: A Run is initiated when **3 QSOs** are detected on the same frequency within a **10-minute** window.
* **Frequency Tolerance**: The algorithm allows for a tolerance of 0.1 kHz for CW or 0.5 kHz for Phone.
* **Retroactive Tagging**: When a Run is identified, the initial QSOs in the buffer that triggered the detection are retroactively reclassified from S&P to **Run**.
* **Sticky State Maintenance**: Once active, the "Run" state is maintained for all subsequent QSOs on that frequency until:
    * **Time-Out**: 2 minutes pass without a QSO on the run frequency.
    * **Frequency Change**: 3 consecutive QSOs occur on a different frequency.
* **Initial S&P**: Any QSO not meeting the above criteria is initially classified as **S&P**.

---

## 3. Pass 2: Reclassification of Ambiguous Activity
The second pass refines the results by identifying periods where the activity rate is too low to reliably distinguish between a struggling Run and an S&P attempt.

* **Targeting S&P**: The algorithm re-examines only QSOs currently labeled as **S&P**.
* **Synchronized Density Check**: For each target QSO, the algorithm counts contacts in two separate **10-minute** windows: one immediately preceding and one immediately following the contact.
* **Classification to Unknown**: If the count in **both** windows is below the threshold of **3 QSOs**, the contact is reclassified as **Unknown**.

---

## 4. Classification Matrix (Summary)
| Activity Rate | Frequency Stability | Final Result |
| :--- | :--- | :--- |
| $\geq$ 3 per 10 min | Static | **Run** |
| $\geq$ 3 per 10 min | Agile | **S&P** |
| $<$ 3 per 10 min | Any | **Unknown** |