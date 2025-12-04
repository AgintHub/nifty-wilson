# fetch_meta_stock_data PRD

## Description
Collects Meta stock price data for the last 90 days.


## Implementation Plan

### 1. Choose a stable public API (e.g., Yahoo Finance via yfinance) that provides daily OHLCV for Meta and supports date filtering.

| Category | Details |
| --- | --- |
| **Reason** | Yahoo Finance is free, well documented, and reliably returns historical OHLCV with timezone‑neutral dates. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Import yfinance, instantiate Ticker('META'), and call history(period='90d') to retrieve 90 days of data. |

### 2. Verify that the returned dataframe contains the required columns (Open, High, Low, Close, Volume) and that the index is a DatetimeIndex.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the data aligns with the expected schema and that subsequent transformations are safe. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use df.columns.contains() checks, and df.index.is_monotonic_increasing to confirm chronological order. |

### 3. Convert the DatetimeIndex to ISO‑8601 string format (YYYY‑MM‑DD) and reset it as a column named 'Date'.

| Category | Details |
| --- | --- |
| **Reason** | The output requires ISO date strings; resetting the index ensures a clean column for later sorting and list extraction. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | df.reset_index(inplace=True); df['Date'] = df['Date'].dt.strftime('%Y-%m-%d') |

### 4. Ensure the dataframe is sorted ascending by 'Date', dropping any duplicate dates that may appear due to timezone conversions.

| Category | Details |
| --- | --- |
| **Reason** | The node's contract mandates ascending order; duplicates would corrupt downstream merges. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | df.sort_values('Date', inplace=True); df.drop_duplicates(subset='Date', keep='first', inplace=True) |

### 5. Extract each column into a Python list matching the output types: dates → list of strings, opens/highs/lows/closes → list of floats, volumes → list of ints.

| Category | Details |
| --- | --- |
| **Reason** | Transforms pandas Series into primitive list types required by the DAG's data contract. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use df['Column'].tolist() for each, converting volumes to int via .astype(int).tolist() |

### 6. Perform a sanity check on the volume data to confirm no NaNs or negative values, raising an error if found.

| Category | Details |
| --- | --- |
| **Reason** | Negative or missing volumes invalidate subsequent calculations and could silently corrupt the dataset. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Check df['Volume'].isna().any() or (df['Volume'] < 0).any(); raise ValueError if true. |

### 7. Return the six lists in the order specified by the output structure, ensuring the lengths match and the date list is the longest if any missing OHLCV entries are forward‑filled.

| Category | Details |
| --- | --- |
| **Reason** | Guarantees consistency across the node's outputs and prevents misalignment in downstream nodes. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Package lists into a dictionary: {'dates': dates_list, 'opens': opens_list, ...} and return via the node's interface. |
