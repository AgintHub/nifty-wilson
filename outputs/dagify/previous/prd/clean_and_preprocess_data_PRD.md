# clean_and_preprocess_data PRD

## Description
Clean and preprocess the collected historical data


## Implementation Plan

### 1. Validate the success flag from collect_historical_data; abort cleaning if the flag is false to avoid processing invalid datasets.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the node only operates on valid data, preventing cascading errors downstream. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Check `success` in parent output; if false, set all outputs to default failure values and return. |

### 2. Load raw historical data into a Pandas DataFrame, using asset symbols as keys to create a multi‑index (date, symbol) structure for efficient manipulation.

| Category | Details |
| --- | --- |
| **Reason** | A multi‑index allows column‑wise operations across all assets while preserving date alignment. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Read CSV/JSON files into DataFrames, set `date` as the first index level and `symbol` as the second; ensure datetime dtype. |

### 3. Compute the total number of cells and the total number of missing cells across all numeric columns to derive the missing data ratio.

| Category | Details |
| --- | --- |
| **Reason** | Provides a quantitative baseline of data quality before any imputation. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use `DataFrame.size` for total cells and `DataFrame.isna().sum().sum()` for missing count; calculate ratio as missing/total. |

### 4. Identify and remove duplicate rows based on the multi‑index to ensure each date‑symbol combination is unique.

| Category | Details |
| --- | --- |
| **Reason** | Duplicates can bias statistical tests and cointegration analysis. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Apply `DataFrame.drop_duplicates()` with `subset=['date', 'symbol']`. |

### 5. Apply forward‑fill (`ffill`) then backward‑fill (`bfill`) to propagate existing observations into missing slots, followed by linear interpolation for remaining gaps.

| Category | Details |
| --- | --- |
| **Reason** | Combines robust edge‑handling with smoothness for time‑series data. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Chain `DataFrame.fillna(method='ffill').fillna(method='bfill').interpolate(method='linear')`. |

### 6. Count the number of missing values that were actually filled during imputation to populate `missing_values_count`.

| Category | Details |
| --- | --- |
| **Reason** | Provides transparency about the extent of imputation performed. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Subtract pre‑imputation missing count from post‑imputation missing count. |

### 7. Standardize column names by converting all to lowercase and replacing spaces or special characters with underscores.

| Category | Details |
| --- | --- |
| **Reason** | Ensures consistent column references in downstream modules. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use `DataFrame.rename(columns=lambda x: re.sub(r'[^a-z0-9]', '_', x.lower()))`. |

### 8. Detect outliers in price‑related columns (`open`, `high`, `low`, `close`) using the Inter‑Quartile Range (IQR) method with a 1.5× multiplier.

| Category | Details |
| --- | --- |
| **Reason** | IQR is robust to extreme values and preserves the bulk of the distribution. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | For each column, compute Q1, Q3, IQR = Q3−Q1; flag rows where value < Q1−1.5×IQR or > Q3+1.5×IQR. |

### 9. Remove all flagged outlier rows from the DataFrame, and record the count in `outliers_removed_count`.

| Category | Details |
| --- | --- |
| **Reason** | Outliers can distort statistical relationships and lead to spurious cointegration signals. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use boolean indexing to drop flagged rows; sum the number of dropped rows. |

### 10. Confirm that all remaining missing values are resolved and that data types are correct (e.g., numeric for price columns, integer for volume).

| Category | Details |
| --- | --- |
| **Reason** | Prevents type‑related errors in subsequent statistical analyses. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Apply `DataFrame.dtypes` check and cast columns using `astype` where necessary. |

### 11. Generate the `processed_columns` list by extracting the names of all columns that underwent cleaning or transformation.

| Category | Details |
| --- | --- |
| **Reason** | Provides a traceable record of what was altered, useful for audit and debugging. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Maintain a set of column names during each transformation step and output as a list. |

### 12. Persist the cleaned DataFrame to a standardized file format (e.g., Parquet) for efficient I/O during cointegration analysis.

| Category | Details |
| --- | --- |
| **Reason** | Parquet offers columnar storage and compression, speeding up downstream reads. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use `DataFrame.to_parquet('cleaned_data.parquet')`. |

### 13. Set `cleaned_data_available` to true upon successful completion of all steps; otherwise, set to false and populate remaining outputs with sentinel values.

| Category | Details |
| --- | --- |
| **Reason** | Clear success indicator for downstream nodes. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Wrap entire pipeline in try/except; on exception, log error and return failure flags. |
