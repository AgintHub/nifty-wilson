# align_dataframes_to_master_calendar PRD

## Description
Aligns multiple ticker DataFrames to a unified master business‑day calendar, ensuring consistent timestamps across all assets.


## Implementation Plan

### 1. Parse and validate the `dataframes` and `tickers` JSON strings into Python objects.

| Category | Details |
| --- | --- |
| **Reason** | The shim receives raw JSON strings; they must be deserialized and checked for completeness before any alignment logic can run. |
| **Impact** | Prevents runtime errors caused by malformed inputs and ensures only the requested tickers are processed. |
| **Complexity** | LOW |
| **Method** | Use `json.loads` to convert the strings, verify that `dataframes` is a dict and `tickers` is a list, and raise a clear `ValueError` for mismatches. |

### 2. Create a master business‑day calendar covering the full date range of all ticker DataFrames.

| Category | Details |
| --- | --- |
| **Reason** | A single unified index is required so that downstream back‑testing logic can assume all assets share identical timestamps. |
| **Impact** | All subsequent calculations (signals, portfolio equity, etc.) operate on synchronized data, eliminating alignment bugs. |
| **Complexity** | MEDIUM |
| **Method** | Collect the minimum start date and maximum end date across all parsed DataFrames, then generate a `pd.date_range(start, end, freq='B', tz='UTC')`. Store this as `master_index`. |

### 3. Reindex each ticker DataFrame to `master_index`, forward‑fill missing values, and serialize back to CSV strings.

| Category | Details |
| --- | --- |
| **Reason** | Reindexing ensures every ticker has rows for every business day; forward‑fill maintains the last known price when data is missing (e.g., holidays). |
| **Impact** | Produces the final aligned dictionary that the back‑test engine consumes, guaranteeing consistent shape and index across assets. |
| **Complexity** | MEDIUM |
| **Method** | Iterate over the tickers list, read each CSV into a `pd.DataFrame` (parse dates, set index), `df.reindex(master_index).ffill().bfill()`, then `df.to_csv(index=True)` and store in the result dict. Finally `json.dumps` the dict for the `output` field. |
