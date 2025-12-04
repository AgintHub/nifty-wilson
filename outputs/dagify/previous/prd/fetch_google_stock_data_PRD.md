# fetch_google_stock_data PRD

## Description
Collects Google (GOOGL) stock price data for the most recent 90 calendar days, ensuring the data is cleaned, sorted, and converted into the specified list outputs.


## Implementation Plan

### 1. Determine the exact 90‑day date range: compute the date 90 calendar days before the current date and use that as the start date, ensuring the end date is the most recent trading day.

| Category | Details |
| --- | --- |
| **Reason** | Accurate date range guarantees consistent data volume across executions. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use Python datetime to calculate start and end dates, adjust for weekends/holidays by querying the trading calendar or simply allow the API to filter non‑trading days. |

### 2. Select a reliable public data provider that offers GOOGL OHLCV data, e.g., Yahoo Finance via the yfinance library or Alpha Vantage’s free API, prioritizing providers with robust error handling and rate‑limit compliance.

| Category | Details |
| --- | --- |
| **Reason** | Provider reliability reduces downtime and ensures data integrity. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Write a small wrapper function that attempts the first provider and falls back to the second if a network or API error occurs. |

### 3. Fetch raw data using the chosen provider’s API: request daily adjusted close, high, low, open, and volume data for the ticker GOOGL covering the determined date range.

| Category | Details |
| --- | --- |
| **Reason** | Direct API access is the most efficient way to obtain up‑to‑date OHLCV data. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use yfinance's `Ticker.history(period='90d', interval='1d', auto_adjust=False)` or Alpha Vantage’s `TIME_SERIES_DAILY_ADJUSTED` endpoint; capture JSON/CSV response. |

### 4. Parse the downloaded data into a Pandas DataFrame, ensuring column names match the required output (Date, Open, High, Low, Close, Volume).

| Category | Details |
| --- | --- |
| **Reason** | Pandas provides robust parsing and type inference for CSV/JSON data. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Load with `pd.read_csv` for CSV or `pd.DataFrame.from_dict` for JSON; rename columns if necessary. |

### 5. Convert the Date column to ISO 8601 string format (YYYY‑MM‑DD) and sort the DataFrame ascending by date.

| Category | Details |
| --- | --- |
| **Reason** | ISO format standardizes dates for downstream consumption and sorting ensures chronological order. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use `pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')` and `df.sort_values('Date', inplace=True)`. |

### 6. Validate numeric columns (Open, High, Low, Close, Volume) for data type consistency, converting to float for prices and int for volume, and fill any missing values using forward‑fill to preserve market continuity.

| Category | Details |
| --- | --- |
| **Reason** | Consistent numeric types are required for downstream calculations and the PRD’s output schema. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Apply `df[col] = pd.to_numeric(df[col], errors='coerce')` then `df[col].fillna(method='ffill', inplace=True)`. |

### 7. Extract each column into a Python list in the order of the sorted DataFrame and cast to the appropriate list type (list of str, list of float, list of int).

| Category | Details |
| --- | --- |
| **Reason** | The output structure requires pure Python lists rather than Pandas objects. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use `df['Date'].tolist()`, `df['Open'].tolist()`, etc., and cast volume list to int if not already. |

### 8. Perform a sanity check: ensure the lengths of all output lists match and equal the number of trading days retrieved; if mismatched, raise a descriptive error.

| Category | Details |
| --- | --- |
| **Reason** | Prevents downstream nodes from receiving inconsistent data. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Assert `len(dates) == len(open_prices) == ...` and raise ValueError with context if false. |

### 9. Package the six lists into the node’s output dictionary as per the defined output structure and return it as the node’s result.

| Category | Details |
| --- | --- |
| **Reason** | Fulfills the node contract and allows parent nodes to consume the data seamlessly. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Return `{'dates': dates, 'open_prices': open_prices, 'high_prices': high_prices, 'low_prices': low_prices, 'close_prices': close_prices, 'volumes': volumes}`. |
