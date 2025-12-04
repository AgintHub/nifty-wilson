# fetch_meta_stock_data_yahoo PRD

## Description
Fetches Meta (META) stock data for the last 90 days from Yahoo Finance and formats it as lists.


## Implementation Plan

### 1. Import the `yfinance` library and instantiate a `Ticker` object for 'META'. Set the period to '90d' and retrieve historical data using `history(period='90d', auto_adjust=True)`.

| Category | Details |
| --- | --- |
| **Reason** | Using `auto_adjust=True` ensures that any splits or dividends are accounted for, giving accurate OHLCV data for analysis. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Python: `import yfinance as yf; ticker = yf.Ticker('META'); df = ticker.history(period='90d', auto_adjust=True)` |

### 2. Drop any rows with missing data (`df.dropna(inplace=True)`) and reset the index to expose the date column as a regular column.

| Category | Details |
| --- | --- |
| **Reason** | Missing data can arise on holidays or if data is incomplete; dropping ensures clean lists without gaps. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Python: `df.reset_index(inplace=True)`; `df.dropna(inplace=True)` |

### 3. Convert the `Date` column to ISO 8601 string format (`df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')`) and sort the dataframe ascending by this column.

| Category | Details |
| --- | --- |
| **Reason** | ISO format guarantees consistency across downstream systems and sorting ensures chronological order. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Python: `df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')`; `df.sort_values('Date', inplace=True)` |

### 4. Extract each required column into separate lists: `dates`, `open_prices`, `high_prices`, `low_prices`, `close_prices`, and `volumes` (`volumes = df['Volume'].astype(int).tolist()`). Ensure numeric columns are cast to `float` before list conversion.

| Category | Details |
| --- | --- |
| **Reason** | Explicit casting prevents type mismatch errors when the output is consumed by other nodes expecting `PrimitiveType.LIST_FLOAT` or `PrimitiveType.LIST_INT`. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Python: `dates = df['Date'].tolist()`; `open_prices = df['Open'].astype(float).tolist()`, etc. |

### 5. Implement robust error handling: wrap the entire retrieval and processing logic in a `try/except` block that catches `yfinance` connection errors, data‑unavailable errors, or unexpected schema changes, and re‑raise a descriptive `RuntimeError` with the original exception message.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the workflow fails gracefully and provides actionable diagnostics to downstream nodes. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Python: `try: ... except Exception as e: raise RuntimeError('Meta data fetch failed: ' + str(e))` |

### 6. Validate output list lengths: assert that all lists share the same length; if not, raise a `ValueError` with details of mismatched indices.

| Category | Details |
| --- | --- |
| **Reason** | Consistency across parallel lists is critical for downstream merging or visualization steps. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Python: `assert len(dates) == len(open_prices) == len(high_prices) == len(low_prices) == len(close_prices) == len(volumes)` |
