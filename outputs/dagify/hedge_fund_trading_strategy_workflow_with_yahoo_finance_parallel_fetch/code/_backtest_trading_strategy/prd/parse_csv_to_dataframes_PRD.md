# parse_csv_to_dataframes PRD

## Description
Converts CSV strings for each ticker into a JSON‑encoded dictionary of pandas DataFrames with UTC timestamps and uniform column names.


## Implementation Plan

### 1. Validate that the number of CSV strings matches the number of tickers and that each string is non‑empty.

| Category | Details |
| --- | --- |
| **Reason** | Mismatched or missing data would cause downstream parsing errors and corrupt the backtest. |
| **Impact** | Prevents runtime exceptions and ensures data integrity before heavy processing. |
| **Complexity** | LOW |
| **Method** | Deserialize the `csv_strings` and `tickers` JSON arrays, compare their lengths, and raise a clear ValueError if they differ or contain empty entries. |

### 2. Parse each CSV string into a pandas DataFrame, enforce a UTC datetime index, and rename columns to a standard OHLCV schema.

| Category | Details |
| --- | --- |
| **Reason** | Downstream pipeline components expect uniform DataFrames with a timezone‑aware index and consistent column names. |
| **Impact** | Provides a clean, predictable data structure for alignment, signal generation, and backtesting stages. |
| **Complexity** | MEDIUM |
| **Method** | Loop over `zip(tickers, csv_strings)`, use `io.StringIO` with `pd.read_csv(parse_dates=['Date'])`, set `df.set_index('Date', inplace=True)`, apply `df.index = df.index.tz_localize('UTC')` (or `tz_convert` if already tz‑aware), and rename columns via a mapping dict (e.g., {'Open':'open','High':'high',...}). |

### 3. Serialize the resulting ticker‑to‑DataFrame dictionary into a JSON string for the shim output.

| Category | Details |
| --- | --- |
| **Reason** | The shim’s declared output type is STR, so the complex object must be encoded as a string that can be deserialized later. |
| **Impact** | Allows the `backtest_trading_strategy` node to easily reconstruct the DataFrames via `json.loads` and `pd.read_json`. |
| **Complexity** | LOW |
| **Method** | Create a dict `{ticker: df.to_json(date_format='iso', orient='split') for ticker, df in parsed_dict.items()}`, then `json.dumps` the dict; return this string as the `output` field. |
