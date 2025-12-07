# Implementation Plan - Stacked Butterfly Chart

## **Goal**
Create a new chart report (`chart_comparative_activity_butterfly`) that visualizes hourly QSO rates for two logs as a "Butterfly Chart" (diverging bar chart).
* **Structure:** One subplot per band (up to 6 per page).
* **Data:** QSOs per hour.
* **Segmentation:** Stacked bars showing **Run** (Green), **S&P** (Red), and **Unknown** (Yellow).
* **Orientation:** Log 1 extends Up (Positive), Log 2 extends Down (Negative).

## **Proposed Changes**

### **1. Data Abstraction Layer (DAL) Update**
**Target File:** `contest_tools/data_aggregators/matrix_stats.py`

We need a new aggregation method because the existing `get_matrix_data` flattens the "Run/S&P" status into a single "Dominant" status per hour. We need the raw counts for *each* status per hour.

**New Method:** `get_stacked_matrix_data(bin_size='60min', mode_filter=None)`
* **Logic:**
    1.  Iterate through logs.
    2.  Filter DataFrame by `mode_filter` if provided.
    3.  Group by `[Datetime, Band, Run]`.
    4.  Pivot/Unstack to create a grid where the columns are Time and the index is `(Band, RunStatus)`.
    5.  Reindex to the master time index (filling 0).
    6.  Convert to a nested dictionary structure for JSON-safe return:
        * `{ CALLSIGN: { BAND: { 'Run': [list_of_ints], 'S&P': [...], 'Unknown': [...] } } }`

### **2. Report Generation**
**New File:** `contest_tools/reports/chart_comparative_activity_butterfly.py`

**Class Structure:**
* Inherits from `ContestReport`.
* `report_id`: "chart_comparative_activity_butterfly"
* `supports_pairwise`: True

**Generation Logic (`generate` method):**
1.  **Data Fetch:** Call `aggregator.get_stacked_matrix_data(bin_size='60min')`.
2.  **Band Identification:** Identify all bands present in the data.
3.  **Pagination:** Calculate pages needed (Max 6 bands per page). Loop through pages.
4.  **Plotting (per page):**
    * Create `plt.subplots` (Nx1 grid).
    * **Loop Bands:**
        * **Log 1 (Upper Stack):**
            * `y_run` = Data['Run']
            * `y_sp` = Data['S&P']
            * `y_unk` = Data['Unknown']
            * Plot `y_run` (Green).
            * Plot `y_sp` (Red, bottom=`y_run`).
            * Plot `y_unk` (Yellow, bottom=`y_run + y_sp`).
        * **Log 2 (Lower Stack):**
            * Negate values.
            * Plot `-y_run` (Green).
            * Plot `-y_sp` (Red, bottom=`-y_run`).
            * Plot `-y_unk` (Yellow, bottom=`-(y_run + y_sp)`).
        * **Styling:**
            * Add horizontal line at y=0.
            * Calculate dynamic Y-limit (round up to nearest 5 or 10 based on max hourly rate).
            * Add gridlines.
            * Label Y-axis with Band Name.
    * **Formatting:**
        * Title: "Comparative Activity Breakdown: [Year] [Contest] - [Call1] vs [Call2]".
        * Legend: "Run (Green), S&P (Red), Unknown (Yellow)".
        * Save to `reports/.../charts/`.

## **Verification Plan**

### **Automated Verification**
The Builder will not run the full suite but should verify syntax.

### **Manual Verification Command**
To be run by the user after implementation:
__CODE_BLOCK__python
python main_cli.py --report chart_comparative_activity_butterfly <Log1> <Log2>
__CODE_BLOCK__

## **Detailed Specifications**

### **A. `contest_tools/data_aggregators/matrix_stats.py`**

Add `get_stacked_matrix_data`:

__CODE_BLOCK__python
    def get_stacked_matrix_data(self, bin_size: str = '60min', mode_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Generates 3D data (Band x Time x RunStatus) for stacked charts.
        """
        # ... Implementation details ...
        # 1. Establish Master Time Index
        # 2. Iterate Logs
        # 3. Pivot table on ['Band', 'Run'] vs Datetime
        # 4. Fill missing Run/S&P/Unknown columns with 0
        # 5. Export to dict structure
__CODE_BLOCK__

### **B. `contest_tools/reports/chart_comparative_activity_butterfly.py`**

__CODE_BLOCK__python
class Report(ContestReport):
    report_id = 'chart_comparative_activity_butterfly'
    # ...
    
    # Colors defined per user request
    COLORS = {'Run': 'green', 'S&P': 'red', 'Unknown': 'yellow'}

    def generate(self, output_path: str, **kwargs) -> str:
        # ... Logic for pagination and stacking ...
__CODE_BLOCK__