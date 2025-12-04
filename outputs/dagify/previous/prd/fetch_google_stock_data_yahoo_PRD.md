# fetch_google_stock_data_yahoo PRD

## Description
Fetches Google (GOOGL) stock data for the last 90 days from Yahoo Finance and formats it as lists.


## Implementation Plan

### 1. Import the yfinance library and other standard modules (datetime, pandas).

| Category | Details |
| --- | --- |
| **Reason** | Setting up the environment is essential before any data fetching can occur. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use `import yfinance as yf`, `import pandas as pd`, and `from datetime import datetime, timedelta`. |

### 2. Define the ticker symbol 'GOOGL' and compute the start date as 90 days before today.

| Category | Details |
| --- | --- |
| **Reason** | Ensures we fetch the exact 90‑day window required by the specification. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use `ticker = 'GOOGL'` and `start_date = (datetime.utcnow() - timedelta(days=90)).strftime('%Y-%m-%d')`. |

### 3. Retrieve historical data using `yf.Ticker(ticker).history(period='90d', auto_adjust=False)`, keeping the 'Open', 'High', 'Low', 'Close', and 'Volume' columns.

| Category | Details |
| --- | --- |
| **Reason** | The yfinance `history` call returns a DataFrame with all requested OHLCV data. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Call `data = yf.Ticker(ticker).history(start=start_date, end=datetime.utcnow().strftime('%Y-%m-%d'), auto_adjust=False)` and select columns via `data = data[['Open', 'High', 'Low', 'Close', 'Volume']]`. |

### 4. Drop any rows with missing or NaN values to ensure data integrity.

| Category | Details |
| --- | --- |
| **Reason** | Missing values could break downstream consumers expecting complete numeric lists. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Apply `data.dropna(inplace=True)`. |

### 5. Reset the index so that dates become a column and sort the DataFrame ascending by date.

| Category | Details |
| --- | --- |
| **Reason** | The index may be unsorted or timezone‑aware; normalizing ensures consistent ordering. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use `data.reset_index(inplace=True)` and `data.sort_values('Date', inplace=True)`. |

### 6. Convert each datetime index to ISO 8601 string format (`YYYY-MM-DD`).

| Category | Details |
| --- | --- |
| **Reason** | The output specification requires dates in ISO string format. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Apply `data['Date'] = data['Date'].dt.strftime('%Y-%m-%d')`. |

### 7. Extract each column into a Python list of the correct type: `dates` as list of strings, `open_prices`, `high_prices`, `low_prices`, `close_prices` as list of floats, and `volumes` as list of ints.

| Category | Details |
| --- | --- |
| **Reason** | The output structure expects primitive list types, not pandas Series. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use `dates = data['Date'].tolist()`, `open_prices = data['Open'].astype(float).tolist()`, `high_prices = data['High'].astype(float).tolist()`, `low_prices = data['Low'].astype(float).tolist()`, `close_prices = data['Close'].astype(float).tolist()`, `volumes = data['Volume'].astype(int).tolist()`. |

### 8. Return the six lists in the order defined by the output structure.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the consumer receives data in the exact sequence and format expected. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Construct a dictionary `{ 'dates': dates, 'open_prices': open_prices, 'high_prices': high_prices, 'low_prices': low_prices, 'close_prices': close_prices, 'volumes': volumes }` and output it as JSON or pass directly to the next node. |
