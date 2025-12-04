# fetch_stock_data_yahoo_finance - Complete PRD Documentation

## Overview
PRDs for nodes in the 'fetch_stock_data_yahoo_finance' module.

## Table of Contents

- [fetch_meta_stock_data_yahoo](#fetch_meta_stock_data_yahoo)

- [fetch_google_stock_data_yahoo](#fetch_google_stock_data_yahoo)

- [fetch_nvidia_stock_data_yahoo](#fetch_nvidia_stock_data_yahoo)



---

## fetch_meta_stock_data_yahoo

### Description
Fetches Meta (META) stock data for the last 90 days from Yahoo Finance and formats it as lists.

### Implementation Plan

#### 1. Import the `yfinance` library and instantiate a `Ticker` object for 'META'. Set the period to '90d' and retrieve historical data using `history(period='90d', auto_adjust=True)`.

| Category | Details |
| --- | --- |
| **Reason** | Using `auto_adjust=True` ensures that any splits or dividends are accounted for, giving accurate OHLCV data for analysis. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Python: `import yfinance as yf; ticker = yf.Ticker('META'); df = ticker.history(period='90d', auto_adjust=True)` |

#### 2. Drop any rows with missing data (`df.dropna(inplace=True)`) and reset the index to expose the date column as a regular column.

| Category | Details |
| --- | --- |
| **Reason** | Missing data can arise on holidays or if data is incomplete; dropping ensures clean lists without gaps. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Python: `df.reset_index(inplace=True)`; `df.dropna(inplace=True)` |

#### 3. Convert the `Date` column to ISO 8601 string format (`df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')`) and sort the dataframe ascending by this column.

| Category | Details |
| --- | --- |
| **Reason** | ISO format guarantees consistency across downstream systems and sorting ensures chronological order. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Python: `df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')`; `df.sort_values('Date', inplace=True)` |

#### 4. Extract each required column into separate lists: `dates`, `open_prices`, `high_prices`, `low_prices`, `close_prices`, and `volumes` (`volumes = df['Volume'].astype(int).tolist()`). Ensure numeric columns are cast to `float` before list conversion.

| Category | Details |
| --- | --- |
| **Reason** | Explicit casting prevents type mismatch errors when the output is consumed by other nodes expecting `PrimitiveType.LIST_FLOAT` or `PrimitiveType.LIST_INT`. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Python: `dates = df['Date'].tolist()`; `open_prices = df['Open'].astype(float).tolist()`, etc. |

#### 5. Implement robust error handling: wrap the entire retrieval and processing logic in a `try/except` block that catches `yfinance` connection errors, data‑unavailable errors, or unexpected schema changes, and re‑raise a descriptive `RuntimeError` with the original exception message.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the workflow fails gracefully and provides actionable diagnostics to downstream nodes. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Python: `try: ... except Exception as e: raise RuntimeError('Meta data fetch failed: ' + str(e))` |

#### 6. Validate output list lengths: assert that all lists share the same length; if not, raise a `ValueError` with details of mismatched indices.

| Category | Details |
| --- | --- |
| **Reason** | Consistency across parallel lists is critical for downstream merging or visualization steps. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Python: `assert len(dates) == len(open_prices) == len(high_prices) == len(low_prices) == len(close_prices) == len(volumes)` |


---

## fetch_google_stock_data_yahoo

### Description
Fetches Google (GOOGL) stock data for the last 90 days from Yahoo Finance and formats it as lists.

### Implementation Plan

#### 1. Import the yfinance library and other standard modules (datetime, pandas).

| Category | Details |
| --- | --- |
| **Reason** | Setting up the environment is essential before any data fetching can occur. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use `import yfinance as yf`, `import pandas as pd`, and `from datetime import datetime, timedelta`. |

#### 2. Define the ticker symbol 'GOOGL' and compute the start date as 90 days before today.

| Category | Details |
| --- | --- |
| **Reason** | Ensures we fetch the exact 90‑day window required by the specification. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use `ticker = 'GOOGL'` and `start_date = (datetime.utcnow() - timedelta(days=90)).strftime('%Y-%m-%d')`. |

#### 3. Retrieve historical data using `yf.Ticker(ticker).history(period='90d', auto_adjust=False)`, keeping the 'Open', 'High', 'Low', 'Close', and 'Volume' columns.

| Category | Details |
| --- | --- |
| **Reason** | The yfinance `history` call returns a DataFrame with all requested OHLCV data. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Call `data = yf.Ticker(ticker).history(start=start_date, end=datetime.utcnow().strftime('%Y-%m-%d'), auto_adjust=False)` and select columns via `data = data[['Open', 'High', 'Low', 'Close', 'Volume']]`. |

#### 4. Drop any rows with missing or NaN values to ensure data integrity.

| Category | Details |
| --- | --- |
| **Reason** | Missing values could break downstream consumers expecting complete numeric lists. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Apply `data.dropna(inplace=True)`. |

#### 5. Reset the index so that dates become a column and sort the DataFrame ascending by date.

| Category | Details |
| --- | --- |
| **Reason** | The index may be unsorted or timezone‑aware; normalizing ensures consistent ordering. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use `data.reset_index(inplace=True)` and `data.sort_values('Date', inplace=True)`. |

#### 6. Convert each datetime index to ISO 8601 string format (`YYYY-MM-DD`).

| Category | Details |
| --- | --- |
| **Reason** | The output specification requires dates in ISO string format. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Apply `data['Date'] = data['Date'].dt.strftime('%Y-%m-%d')`. |

#### 7. Extract each column into a Python list of the correct type: `dates` as list of strings, `open_prices`, `high_prices`, `low_prices`, `close_prices` as list of floats, and `volumes` as list of ints.

| Category | Details |
| --- | --- |
| **Reason** | The output structure expects primitive list types, not pandas Series. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use `dates = data['Date'].tolist()`, `open_prices = data['Open'].astype(float).tolist()`, `high_prices = data['High'].astype(float).tolist()`, `low_prices = data['Low'].astype(float).tolist()`, `close_prices = data['Close'].astype(float).tolist()`, `volumes = data['Volume'].astype(int).tolist()`. |

#### 8. Return the six lists in the order defined by the output structure.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the consumer receives data in the exact sequence and format expected. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Construct a dictionary `{ 'dates': dates, 'open_prices': open_prices, 'high_prices': high_prices, 'low_prices': low_prices, 'close_prices': close_prices, 'volumes': volumes }` and output it as JSON or pass directly to the next node. |


---

## fetch_nvidia_stock_data_yahoo

### Description
Fetches Nvidia (NVDA) stock data for the last 90 days from Yahoo Finance and formats it as lists.

### Implementation Plan

#### 1. Import the yfinance library and the datetime module to fetch and process dates.

| Category | Details |
| --- | --- |
| **Reason** | yfinance is the sole data source required; datetime is needed to format dates into ISO strings. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use 'import yfinance as yf' and 'from datetime import datetime' in the script. |

#### 2. Define the ticker symbol 'NVDA' and set the data period to 90 days with daily interval.

| Category | Details |
| --- | --- |
| **Reason** | Specifying the exact ticker and period ensures the correct data range is retrieved from Yahoo Finance. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | ticker = yf.Ticker('NVDA')
period = '90d'
interval = '1d' |

#### 3. Use the ticker.history() method to pull OHLCV data, handling potential network failures with a retry loop and timeout.

| Category | Details |
| --- | --- |
| **Reason** | Network reliability can vary; a retry loop ensures data retrieval success without manual intervention. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Implement a try-except block that retries up to 3 times with a 5-second delay between attempts; set a reasonable timeout parameter. |

#### 4. Verify the returned DataFrame contains all required columns: Date, Open, High, Low, Close, Volume.

| Category | Details |
| --- | --- |
| **Reason** | Ensures downstream steps have the expected schema; missing columns can break the pipeline. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Check DataFrame columns against the expected list; raise a descriptive error if any are missing. |

#### 5. Convert the DataFrame index (dates) to ISO 8601 formatted strings (YYYY-MM-DD).

| Category | Details |
| --- | --- |
| **Reason** | Uniform date format facilitates sorting and compatibility with downstream JSON serialization. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use df.index.strftime('%Y-%m-%d').tolist() to produce the date list. |

#### 6. Sort the DataFrame by the Date index in ascending order to match the output specification.

| Category | Details |
| --- | --- |
| **Reason** | Some data sources may return unsorted data; sorting guarantees chronological order. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Apply df.sort_index(ascending=True) before extracting columns. |

#### 7. Extract each OHLCV column into separate Python lists, casting to the correct primitive types: float for prices and int for volume.

| Category | Details |
| --- | --- |
| **Reason** | The output structure requires specific primitive types; casting prevents type mismatches. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | open_prices = df['Open'].astype(float).tolist()
high_prices = df['High'].astype(float).tolist()
low_prices = df['Low'].astype(float).tolist()
close_prices = df['Close'].astype(float).tolist()
volumes = df['Volume'].astype(int).tolist() |

#### 8. Perform data cleaning by removing rows with NaN values in any of the OHLCV fields.

| Category | Details |
| --- | --- |
| **Reason** | Missing values can corrupt the resulting lists and violate the assumption that each list has the same length. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use df.dropna(subset=['Open', 'High', 'Low', 'Close', 'Volume']) before extraction. |

#### 9. Validate that all six output lists have equal lengths, raising an informative exception if not.

| Category | Details |
| --- | --- |
| **Reason** | Ensures data consistency; a mismatch indicates a problem in the cleaning or extraction steps. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | len(dates) == len(open_prices) == ...; else raise ValueError('Output list length mismatch'). |

#### 10. Return a dictionary containing the six lists, ready for serialization to JSON.

| Category | Details |
| --- | --- |
| **Reason** | The node's consumer expects a JSON-serializable payload with the specified fields. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Construct {'dates': dates, 'open_prices': open_prices, ...} and return. |

#### 11. Add comprehensive logging at each critical step (fetch, cleaning, conversion) to aid debugging and traceability.

| Category | Details |
| --- | --- |
| **Reason** | Logging provides visibility into the node's operations without altering the functional output. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use Python's logging module; log INFO messages after each major operation. |
