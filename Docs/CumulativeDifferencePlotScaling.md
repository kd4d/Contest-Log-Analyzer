# Cumulative Difference Plot: Dual Y-Axis Scaling

This document describes how the two Y-axes (cumulative and hourly) are scaled and aligned in the cumulative difference plot. It is written for both human readers and AI agents that need to implement or modify this behavior.

---

## 1. What the plot shows

- **Left Y-axis (primary):** Cumulative difference over time (e.g. QSOs or points, Log1 − Log2, summed up to each hour).
- **Right Y-axis (secondary):** Hourly difference (same metric, per-hour only; often shown as stacked bars).
- **Shared X-axis:** Time (contest hours).
- **Constraint:** Both axes **MUST** use the **same physical grid lines** (same N horizontal lines at the same vertical positions). There is a **maximum of 15 horizontal grid lines**; the cumulative axis step is chosen so that N ≤ 15 with "nice" rounded labels (25, 50, 100, 250, 500, 1000, 2000, 5000). The **bar axis zero** may sit on a **different** grid line than the cumulative axis zero (zeros can diverge). Bar zero is placed on the grid line **closest to the ideal P/N position** for the bars, and the bar range is **expanded as needed** so that the exact ratio and rounding rules (multiples of 5, etc.) are satisfied with **no tolerance**. The **top and bottom** grid lines are shown in the plot area.
- **Layering:** In Plotly, traces on the secondary y-axis are drawn on top of primary-axis traces. So the bars (right axis) appear in front of the cumulative line (left axis). This is accepted; the axis layout (cumulative left, hourly right) is preferred.

---

## 2. Core principles

- **Cumulative axis is established first.** Its range and N grid lines are fixed from the cumulative data (data-derived P/N ratio, floor/ceiling rounding). **At most 15 grid lines:** the step is the smallest "nice" value (25, 50, 100, 250, 500, 1000, 2000, 5000) that is ≥ range/14 so N ≤ 15.
- **Same N physical grid lines.** The bar axis uses the **same N** grid lines (same vertical positions). Bar tick **values** map to those same positions; the bar axis zero sits on **one** of those lines (grid line index k).
- **Bar zero can diverge.** The bar axis zero does **not** have to align with the cumulative axis zero. It is placed on the grid line **closest to the ideal P/N position** for the bar data, so the bar scale is more readable while still using the shared grid.
- **Expand bar range for exact alignment.** The bar axis range may be **larger than strictly necessary** to contain the data so that (1) bar zero lies exactly on the chosen grid line (exact ratio) and (2) endpoints satisfy the rounding constraints (e.g. multiples of 5). No tiny tolerances: we expand the range until both conditions hold exactly.
- **Rounding constraints unchanged.** Cumulative: floor min, ceiling max; step is a "nice" value (25, 50, 100, 250, 500, 1000, 2000, 5000) chosen so N ≤ 15. Bar: endpoints and labels multiples of 5; floor bar_min, ceiling bar_max so data is not truncated.

---

## 3. How ranges are chosen

### Step 1: Cumulative axis (established first)

- Use the **cumulative natural P/N ratio** when cumulative data crosses zero (otherwise hourly or fallback). Compute smallest range that contains the data with that ratio. **Maximum 15 grid lines:** require step ≥ range/14 so N ≤ 15. Choose the **smallest "nice" step** ≥ range/14 from the set 25, 50, 100, 250, 500, 1000, 2000, 5000 (if range is very large, round up to the next 1000). **Floor** min and **ceiling** max to that step. Build ticks: `cumul_tickvals = range(cumul_min, cumul_max + 1, step_cumul)`. **N** = number of ticks (≤ 15). Top and bottom grid lines are at the first and last tick.

### Step 2: Bar axis (after cumulative is fixed)

- **Ideal bar zero position:** When bar data crosses zero, ideal position (0–1 from bottom) = `|hourly_data_min| / (|hourly_data_min| + hourly_data_max)`.
- **Snap to closest grid line:** `k = round(ideal_pos * (N-1))`, clamped to `[0, N-1]`. Bar zero will sit on grid line k (physical position k/(N-1)).
- **Bar axis ratio:** For bar zero at grid line k, the bar axis must satisfy `bar_max / |bar_min| = (N-1-k) / k` (so that the tick at index k has value 0). When k=0: bar_min=0 (zero at bottom). When k=N-1: bar_max=0 (zero at top).
- **Expand range for exact ratio + rounding:** Choose bar_max (and thus bar_min from the ratio) so that (1) the range contains the bar data, (2) the ratio is exact for grid line k, and (3) bar_min and bar_max are nice (multiples of 5). If the minimum range that fits the data does not yield nice endpoints with the exact ratio, **increase the range** (e.g. use a step derived from `5*(N-1-k)/gcd(k,N-1-k)`) until we get a valid pair. No tolerance: zero lies exactly on grid line k; endpoints are exactly rounded.
- **Same N ticks:** `hourly_tickvals[i] = hourly_min + i * (hourly_max - hourly_min) / (N-1)` for i = 0..N-1. Bar tick **labels** multiples of 5.

---

## 4. Same N grid lines (shared physical positions)

- **Cumulative axis** defines N and the physical positions: ticks at `cumul_min`, …, `cumul_max` (evenly spaced).
- **Bar axis** uses the **same N** positions. Tick **values** differ (different scale). Bar zero is at position k, so the k-th tick value is 0. Grid lines are shared; cumulative zero and bar zero may be on different lines (they can diverge).
- **Top and bottom:** The first and last tick values on each axis are the axis min and max, so the bottom and top grid lines are drawn at the plot edges.

---

## 5. Data in native coordinates (no rescaling)

- **Cumulative line:** Y-values are the **actual** cumulative difference values; plotted on the left axis only.
- **Hourly bars:** Y-values (and bases) are the **actual** hourly difference values; plotted on the right axis only.
- Do not rescale either series to the other axis. Alignment is achieved by using the same N physical grid lines and placing bar zero on one of them (closest to ideal P/N).

---

## 6. Data types

- Counts (e.g. QSO differences) are **integers**. Use Python `int` for plot values so labels and tooltips show whole numbers.

---

## 7. Algorithm summary (for AI agents)

1. **Compute data extents:** `cumul_data_min`, `cumul_data_max`; `hourly_data_min`, `hourly_data_max` (over all hourly/stacked bar values).

2. **Cumulative axis:** Natural P/N ratio; range with floor min / ceiling max. **Max 15 grid lines:** min_step = range/14; step_cumul = smallest "nice" (25, 50, 100, 250, 500, 1000, 2000, 5000) ≥ min_step. `cumul_tickvals = range(cumul_min, cumul_max+1, step_cumul)`; **N** = len(cumul_tickvals) (≤ 15).

3. **Bar axis:**
   - If bar data crosses zero: `ideal_pos = |hourly_data_min| / (|hourly_data_min| + hourly_data_max)`; `k = round(ideal_pos * (N-1))`, clamp to [0, N-1]. Else: k = 0 (all positive) or k = N-1 (all negative).
   - **k=0:** bar_min=0; bar_max = ceil(max(hourly_data_max, …) / 5) * 5.
   - **k=N-1:** bar_max=0; bar_min = floor(min(hourly_data_min, …) / 5) * 5.
   - **0 < k < N-1:** Ratio (N-1-k)/k. Step for bar_max = 5*(N-1-k)/gcd(k,N-1-k). bar_max_min = max(hourly_data_max, |hourly_data_min|*(N-1-k)/k). bar_max = step * ceil(bar_max_min/step); bar_min = -k*bar_max/(N-1-k). (Both end up multiples of 5 when step is used.)
   - `hourly_tickvals = [hourly_min + i*(hourly_max-hourly_min)/(N-1) for i in range(N)]`; labels multiples of 5.

4. **Plot:** Cumulative and bar ranges and tick arrays as above. Ensure tick lists include axis min and max so top and bottom grid lines are drawn.

5. **Zero line:** A horizontal line at y=0 in primary (cumulative) coordinates. Bar axis zero is at grid line k (may differ from cumulative zero).

---

## 8. Summary

- **Same physical grid lines** for both axes; **at most 15** horizontal grid lines; step is a "nice" value so labels are reasonable and rounded correctly.
- **Bar zero can diverge** from cumulative zero; bar zero is placed on the **grid line closest to the ideal P/N position** for the bars.
- **Expand the bar range** as needed so exact ratio and rounding hold; no tolerances.
- Rounding constraints (multiples of 5, floor/ceiling) remain unchanged.
