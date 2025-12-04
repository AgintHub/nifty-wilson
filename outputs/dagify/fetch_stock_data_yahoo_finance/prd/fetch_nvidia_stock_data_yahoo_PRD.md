# fetch_nvidia_stock_data_yahoo PRD

## Description
Fetches Nvidia (NVDA) stock data for the last 90 days from Yahoo Finance and formats it as lists.


## Implementation Plan

### 1. Import the yfinance library and the datetime module to fetch and process dates.

| Category | Details |
| --- | --- |
| **Reason** | yfinance is the sole data source required; datetime is needed to format dates into ISO strings. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use 'import yfinance as yf' and 'from datetime import datetime' in the script. |

### 2. Define the ticker symbol 'NVDA' and set the data period to 90 days with daily interval.

| Category | Details |
| --- | --- |
| **Reason** | Specifying the exact ticker and period ensures the correct data range is retrieved from Yahoo Finance. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | ticker = yf.Ticker('NVDA')
period = '90d'
interval = '1d' |

### 3. Use the ticker.history() method to pull OHLCV data, handling potential network failures with a retry loop and timeout.

| Category | Details |
| --- | --- |
| **Reason** | Network reliability can vary; a retry loop ensures data retrieval success without manual intervention. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Implement a try-except block that retries up to 3 times with a 5-second delay between attempts; set a reasonable timeout parameter. |

### 4. Verify the returned DataFrame contains all required columns: Date, Open, High, Low, Close, Volume.

| Category | Details |
| --- | --- |
| **Reason** | Ensures downstream steps have the expected schema; missing columns can break the pipeline. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Check DataFrame columns against the expected list; raise a descriptive error if any are missing. |

### 5. Convert the DataFrame index (dates) to ISO 8601 formatted strings (YYYY-MM-DD).

| Category | Details |
| --- | --- |
| **Reason** | Uniform date format facilitates sorting and compatibility with downstream JSON serialization. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use df.index.strftime('%Y-%m-%d').tolist() to produce the date list. |

### 6. Sort the DataFrame by the Date index in ascending order to match the output specification.

| Category | Details |
| --- | --- |
| **Reason** | Some data sources may return unsorted data; sorting guarantees chronological order. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Apply df.sort_index(ascending=True) before extracting columns. |

### 7. Extract each OHLCV column into separate Python lists, casting to the correct primitive types: float for prices and int for volume.

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

### 8. Perform data cleaning by removing rows with NaN values in any of the OHLCV fields.

| Category | Details |
| --- | --- |
| **Reason** | Missing values can corrupt the resulting lists and violate the assumption that each list has the same length. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use df.dropna(subset=['Open', 'High', 'Low', 'Close', 'Volume']) before extraction. |

### 9. Validate that all six output lists have equal lengths, raising an informative exception if not.

| Category | Details |
| --- | --- |
| **Reason** | Ensures data consistency; a mismatch indicates a problem in the cleaning or extraction steps. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | len(dates) == len(open_prices) == ...; else raise ValueError('Output list length mismatch'). |

### 10. Return a dictionary containing the six lists, ready for serialization to JSON.

| Category | Details |
| --- | --- |
| **Reason** | The node's consumer expects a JSON-serializable payload with the specified fields. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Construct {'dates': dates, 'open_prices': open_prices, ...} and return. |

### 11. Add comprehensive logging at each critical step (fetch, cleaning, conversion) to aid debugging and traceability.

| Category | Details |
| --- | --- |
| **Reason** | Logging provides visibility into the node's operations without altering the functional output. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use Python's logging module; log INFO messages after each major operation. |
