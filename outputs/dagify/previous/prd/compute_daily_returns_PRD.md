# compute_daily_returns PRD

## Description
Calculates daily log returns for Meta, Google, and Nvidia and adds the columns to the dataset.


## Implementation Plan

### 1. Load the cleaned dataset from the `preprocess_data` node's `cleaned_csv` output into a Pandas DataFrame, ensuring that the Date column is parsed as datetime.

| Category | Details |
| --- | --- |
| **Reason** | Pandas offers robust CSV parsing and datetime handling, which is essential for accurate return calculations. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use `pd.read_csv(cleaned_csv, parse_dates=['Date'])`. |

### 2. Verify that the required Close price columns (META_Close, GOOGL_Close, NVDA_Close) exist and contain numeric values; if missing, raise a clear error indicating which column is absent.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that the dataset has all necessary inputs before proceeding, preventing downstream failures. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Check DataFrame columns with `df.columns` and validate dtype with `pd.api.types.is_numeric_dtype`. |

### 3. Compute the daily log return for each stock using the formula `return = np.log(Close_today / Close_yesterday)`, aligning with financial convention for continuously compounded returns.

| Category | Details |
| --- | --- |
| **Reason** | Log returns provide additive properties and are standard in backtesting and statistical analysis. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use vectorized operations: `df['META_Return'] = np.log(df['META_Close'] / df['META_Close'].shift(1))`, similarly for GOOGL and NVDA. |

### 4. Handle the first row where the shift operation produces NaN by filling it with 0 or dropping the row; document the chosen approach.

| Category | Details |
| --- | --- |
| **Reason** | The first day lacks a prior price; deciding how to treat this missing value affects downstream metrics. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use `df.dropna(subset=['META_Return', 'GOOGL_Return', 'NVDA_Return'], inplace=True)` or `df.fillna(0, inplace=True)` based on design choice. |

### 5. Add the three new return columns to the DataFrame and verify their data types are float64.

| Category | Details |
| --- | --- |
| **Reason** | Ensures consistency of output types for downstream nodes. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Confirm with `df.dtypes` and convert if necessary using `df.astype({'META_Return': 'float64', ...})`. |

### 6. Write the augmented DataFrame to a new CSV file in a designated temporary or output directory, preserving the original column order with the new columns appended at the end.

| Category | Details |
| --- | --- |
| **Reason** | Providing a stable file path enables other nodes to reference the dataset reliably. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use `df.to_csv(output_path, index=False)`. |

### 7. Return the path of the newly created CSV as `csv_file_path` and the number of rows in the DataFrame as `row_count`.

| Category | Details |
| --- | --- |
| **Reason** | Matches the defined output structure, allowing downstream nodes to access the results. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Return a dictionary: `{'csv_file_path': output_path, 'row_count': len(df)}`. |
