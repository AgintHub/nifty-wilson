# preprocess_data PRD

## Description
Cleans and normalizes the merged dataset by standardizing dates, imputing missing numeric data, and dropping rows lacking both Meta and Google Close prices.


## Implementation Plan

### 1. Read the input CSV string into a pandas DataFrame using `pd.read_csv(io.StringIO(csv_data))` while ensuring that all columns are parsed as strings to avoid dtype inference issues.

| Category | Details |
| --- | --- |
| **Reason** | Parsing as strings preserves the raw Date format and any missing numeric values represented as empty strings, facilitating consistent downstream processing. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use the pandas `read_csv` function with `dtype=str` and `keep_default_na=False` to capture blanks as NaN. |

### 2. Convert the `Date` column to ISO 8601 format by parsing with `pd.to_datetime(df['Date'], errors='coerce', dayfirst=False)` and then formatting with `.dt.strftime('%Y-%m-%d')`.

| Category | Details |
| --- | --- |
| **Reason** | Standardizing dates ensures consistent ordering and compatibility with downstream nodes that rely on ISO dates. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Apply `pd.to_datetime` with `errors='coerce'` to safely convert malformed dates to NaT, then `strftime` for ISO formatting; subsequently drop any rows with NaT if present. |

### 3. Forward‑fill missing numeric values using `df.fillna(method='ffill', inplace=True)` after isolating numeric columns (all columns except `Date`).

| Category | Details |
| --- | --- |
| **Reason** | Forward‑fill propagates the last observed non‑missing value, a common strategy for time‑series financial data where gaps are usually short and missing values are best imputed from prior observations. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Identify numeric columns via `df.select_dtypes(include=['float64', 'int64'])` and apply `ffill`; non‑numeric columns remain untouched. |

### 4. Drop rows where both `META_Close` and `GOOGL_Close` are NaN with `df.dropna(subset=['META_Close', 'GOOGL_Close'], how='all', inplace=True)`.

| Category | Details |
| --- | --- |
| **Reason** | The strategy requires at least one Close value for Meta or Google; rows missing both are unusable for return calculations and should be excluded to avoid division by zero or invalid logs. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use pandas `dropna` specifying `subset` and `how='all'` to retain rows where at least one Close value exists. |

### 5. Sort the DataFrame by the ISO `Date` column in ascending order using `df.sort_values('Date', inplace=True)`.

| Category | Details |
| --- | --- |
| **Reason** | Sorted dates are required for accurate rolling calculations and time‑series alignment in downstream nodes. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Call pandas `sort_values` on the standardized Date column. |

### 6. Convert the cleaned DataFrame back to a CSV string with `df.to_csv(index=False)` ensuring no trailing newline or BOM that could corrupt downstream parsing.

| Category | Details |
| --- | --- |
| **Reason** | Providing a clean CSV string aligns with the expected output format of child nodes. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use pandas `to_csv` with `index=False`; optionally apply `strip()` to remove extraneous whitespace. |

### 7. Compute `row_count` as the number of rows in the cleaned DataFrame using `int(df.shape[0])`.

| Category | Details |
| --- | --- |
| **Reason** | Reporting the row count allows downstream nodes to verify data completeness and detect unintended reductions. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use the `shape` attribute of the DataFrame. |

### 8. Wrap the entire transformation in a `try/except` block to catch parsing or conversion errors, log the exception details, and raise a descriptive exception to upstream nodes.

| Category | Details |
| --- | --- |
| **Reason** | Robust error handling ensures that issues such as malformed dates or unexpected NaN propagation do not silently corrupt the dataset. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Implement `try: ... except Exception as e: log.error(...)` and re‑raise a custom `PreprocessDataError`. |
