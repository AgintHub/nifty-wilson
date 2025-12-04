# perform_pairwise_correlation PRD

## Description
Generates a rolling correlation feature between Meta and Google daily log returns and appends it to the dataset.


## Implementation Plan

### 1. Load the dataset from the CSV file path provided by compute_daily_returns into a Pandas DataFrame, ensuring the Date column is parsed as a datetime and the DataFrame is sorted by Date.

| Category | Details |
| --- | --- |
| **Reason** | Pandas efficiently handles CSV I/O and datetime parsing; sorting guarantees correct chronological order for rolling operations. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use pd.read_csv(csv_file_path, parse_dates=['Date']); then df.sort_values('Date', inplace=True). |

### 2. Validate that the columns META_Return and GOOGL_Return exist and contain numeric values. If missing or non-numeric, raise a clear exception.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the rolling correlation computation has the necessary data and prevents silent failures. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use df[['META_Return', 'GOOGL_Return']].apply(pd.to_numeric, errors='raise') to coerce types; check for any NaNs. |

### 3. Compute a 20‑day rolling Pearson correlation between META_Return and GOOGL_Return with a minimum of 20 observations to avoid NaNs for incomplete windows.

| Category | Details |
| --- | --- |
| **Reason** | Specifies the exact window size and ensures the correlation is only calculated when a full window is available. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | df['META_GOOGL_RollingCorr_20'] = df['META_Return'].rolling(window=20, min_periods=20).corr(df['GOOGL_Return']). |

### 4. Leave the first 19 rows of the new column as NaN (the rolling window is incomplete) and do not forward‑fill or impute them; this preserves statistical integrity.

| Category | Details |
| --- | --- |
| **Reason** | Imputing would bias correlation estimates; NaNs correctly signal insufficient data. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | No additional code required; pandas automatically leaves NaNs for incomplete windows. |

### 5. Convert the enriched DataFrame back to a CSV string with no index column and UTF‑8 encoding, ensuring that the output matches the expected primitive type.

| Category | Details |
| --- | --- |
| **Reason** | The downstream nodes expect a single string containing the CSV data; removing the index keeps the format clean. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | csv_data = df.to_csv(index=False, encoding='utf-8') |

### 6. Return a dictionary with the key csv_data mapped to the generated CSV string, matching the defined output structure.

| Category | Details |
| --- | --- |
| **Reason** | Aligns with the DAG framework's contract for node outputs. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | return {'csv_data': csv_data} |

### 7. Include robust error handling: wrap the entire process in a try/except block that logs detailed error messages and propagates exceptions to the DAG system.

| Category | Details |
| --- | --- |
| **Reason** | Facilitates debugging and prevents silent failures that could cascade to downstream nodes. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use Python's logging module; re‑raise exceptions after logging. |
