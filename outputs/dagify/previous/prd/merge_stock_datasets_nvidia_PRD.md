# merge_stock_datasets_nvidia PRD

## Description
Extends the merged dataset to include Nvidia OHLCV data.


## Implementation Plan

### 1. Parse the merged_csv output from merge_stock_datasets into a DataFrame using pandas, ensuring the first row is treated as header and subsequent rows as data.

| Category | Details |
| --- | --- |
| **Reason** | Using pandas provides robust CSV parsing and easy column manipulation while handling edge cases like commas in data. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | df_meta_google = pd.read_csv(StringIO(merged_csv_text)) |

### 2. Construct a DataFrame from the six output lists of fetch_nvidia_stock_data, assigning column names: ['Date', 'NVDA_Open', 'NVDA_High', 'NVDA_Low', 'NVDA_Close', 'NVDA_Volume']. Convert all numeric columns to appropriate dtypes and the Date column to pandas datetime.

| Category | Details |
| --- | --- |
| **Reason** | Consistent data types are essential for accurate merging and sorting. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | df_nvidia = pd.DataFrame({'Date': dates, 'NVDA_Open': open_prices, ...}); df_nvidia['Date'] = pd.to_datetime(df_nvidia['Date']) |

### 3. Ensure the Date column in both DataFrames is in ISO format (YYYY‑MM‑DD). If merge_stock_datasets used a different format, standardize it using pd.to_datetime and then format.

| Category | Details |
| --- | --- |
| **Reason** | A common date format guarantees a correct join key. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | df_meta_google['Date'] = pd.to_datetime(df_meta_google['Date']).dt.date.astype(str) |

### 4. Perform an inner merge on the 'Date' column, retaining only rows that exist in both DataFrames. Use the 'how="inner"' parameter to enforce intersection.

| Category | Details |
| --- | --- |
| **Reason** | Inner join guarantees that only dates present in all three original datasets are kept, as required by the prompt. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | merged_df = pd.merge(df_meta_google, df_nvidia, on='Date', how='inner') |

### 5. Sort the merged DataFrame by the 'Date' column in ascending order to satisfy the output requirement.

| Category | Details |
| --- | --- |
| **Reason** | A sorted output improves downstream processing and readability. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | merged_df.sort_values(by='Date', inplace=True) |

### 6. Convert the merged DataFrame back to a CSV string, using a comma separator and including the header row. Ensure that the output is a single string suitable for the PrimitiveType.STR field.

| Category | Details |
| --- | --- |
| **Reason** | The downstream node expects a single CSV string, not a list of rows. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | csv_output = merged_df.to_csv(index=False) |

### 7. Return the csv_output string as the value for the 'csv_data' field, completing the node's contract.

| Category | Details |
| --- | --- |
| **Reason** | Explicitly mapping the final string to the defined output field ensures consistency with the DAG schema. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | return { 'csv_data': csv_output } |
