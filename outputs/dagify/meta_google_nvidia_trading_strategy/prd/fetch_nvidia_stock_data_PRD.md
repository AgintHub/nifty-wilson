# fetch_nvidia_stock_data PRD

## Description
Collects Nvidia stock price data for the last 90 days.


## Implementation Plan

### 1. Import the required third‑party libraries: `pandas` for data manipulation and `yfinance` as the primary data source.

| Category | Details |
| --- | --- |
| **Reason** | These libraries provide a robust, well‑tested interface to Yahoo Finance and efficient DataFrame operations. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | pip install yfinance pandas; import yfinance as yf; import pandas as pd |

### 2. Determine the UTC timestamp for the current day and compute the start date exactly 90 days prior using `datetime`.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that the date range is always accurate regardless of the script run time. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | from datetime import datetime, timedelta; end_date = datetime.utcnow().date(); start_date = end_date - timedelta(days=90) |

### 3. Fetch the daily OHLCV data via `yf.download(ticker='NVDA', start=start_date, end=end_date, interval='1d', progress=False, actions=False)`.

| Category | Details |
| --- | --- |
| **Reason** | Yahoo Finance provides a free, stable API endpoint for historical data, and `yfinance` handles authentication and rate‑limiting internally. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | data = yf.download('NVDA', start=start_date, end=end_date, interval='1d', progress=False, actions=False) |

### 4. Validate the returned DataFrame: check for the presence of the required columns `Open`, `High`, `Low`, `Close`, `Volume`. If any are missing, raise a descriptive exception.

| Category | Details |
| --- | --- |
| **Reason** | Prevents downstream errors due to column mis‑naming or API changes. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | required_cols = {'Open', 'High', 'Low', 'Close', 'Volume'}; missing = required_cols - set(data.columns); if missing: raise ValueError(f'Missing columns: {missing}') |

### 5. Reset the DataFrame index to expose the `Date` column and convert it to ISO‑8601 string format (`YYYY‑MM‑DD`).

| Category | Details |
| --- | --- |
| **Reason** | Standardizes the date representation for consistency across nodes. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | data.reset_index(inplace=True); data['Date'] = pd.to_datetime(data['Date']).dt.strftime('%Y-%m-%d') |

### 6. Sort the DataFrame by `Date` in ascending order to satisfy the prompt requirement.

| Category | Details |
| --- | --- |
| **Reason** | Ensures chronological ordering which is critical for time‑series analyses. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | data.sort_values('Date', inplace=True); data.reset_index(drop=True, inplace=True) |

### 7. Replace any remaining missing numeric values (e.g., due to market holidays) using forward‑fill. If the first rows remain missing, drop those rows.

| Category | Details |
| --- | --- |
| **Reason** | Guarantees that every output list contains valid numeric entries, avoiding downstream NaNs. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | data[['Open', 'High', 'Low', 'Close', 'Volume']] = data[['Open', 'High', 'Low', 'Close', 'Volume']].fillna(method='ffill'); data.dropna(subset=['Open', 'High', 'Low', 'Close', 'Volume'], inplace=True) |

### 8. Cast the numeric columns to appropriate Python types: floats for prices, int for volume.

| Category | Details |
| --- | --- |
| **Reason** | Matches the specified output types (`List[float]` and `List[int]`). |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | data['Volume'] = data['Volume'].astype(int); price_cols = ['Open', 'High', 'Low', 'Close']; data[price_cols] = data[price_cols].astype(float) |

### 9. Extract each column into a Python list in the correct order and assign them to the corresponding output fields.

| Category | Details |
| --- | --- |
| **Reason** | Conforms to the defined `output_structure` while keeping the data in memory‑efficient structures. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | dates = data['Date'].tolist(); open_prices = data['Open'].tolist(); high_prices = data['High'].tolist(); low_prices = data['Low'].tolist(); close_prices = data['Close'].tolist(); volumes = data['Volume'].tolist() |

### 10. Return the six lists as the final node output.

| Category | Details |
| --- | --- |
| **Reason** | The downstream nodes expect this exact structure for further processing. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | return { 'dates': dates, 'open_prices': open_prices, 'high_prices': high_prices, 'low_prices': low_prices, 'close_prices': close_prices, 'volumes': volumes } |

### 11. Implement robust error handling: wrap the entire fetch‑and‑transform logic in a try/except block, logging network errors, API limits, or data validation failures, and re‑raise a custom `RuntimeError` with context.

| Category | Details |
| --- | --- |
| **Reason** | Provides resilience in production environments and aids debugging. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | try: ... except Exception as e: logger.exception('NVDA data fetch failed'); raise RuntimeError(f'NVDA data fetch error: {e}') |

### 12. Add optional caching: store the fetched CSV as a local file with a timestamp; on subsequent runs within 24 h, read from cache instead of querying the API, to reduce external calls and improve speed.

| Category | Details |
| --- | --- |
| **Reason** | Optimizes performance for iterative workflows and respects API rate limits. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | cache_path = Path('cache/nvda_90d.csv'); if cache_path.exists() and age < 24h: data = pd.read_csv(cache_path); else: fetch_and_save_to_cache() |
