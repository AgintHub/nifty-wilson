# collect_historical_data PRD

## Description
Gather raw historical market data for each asset in the selected universe, ensuring the dataset is complete, accurate, and formatted for downstream preprocessing.


## Implementation Plan

### 1. Validate and normalise the input asset list from the parent node, ensuring no empty strings and all symbols are upper‑case.

| Category | Details |
| --- | --- |
| **Reason** | Prevents downstream API failures caused by malformed tickers. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use Python set and strip operations; apply .upper() to each symbol; remove duplicates. |

### 2. Derive the historical time window required for statistical analysis by reading the strategy horizon from `define_strategy_objectives` via the `select_universe_of_assets` node’s output, adding an additional safety buffer of 30 days to account for missing data.

| Category | Details |
| --- | --- |
| **Reason** | Guarantees enough data for cointegration tests while mitigating edge effects. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Convert `strategy_horizon_months` to days, subtract from current date to get `data_start_date`; set `data_end_date` to today's date. |

### 3. Choose a reliable public or commercial data provider API (e.g., Yahoo Finance via `yfinance`, Alpha Vantage, or Bloomberg) and instantiate a client with appropriate API keys and rate‑limit handling.

| Category | Details |
| --- | --- |
| **Reason** | Different providers offer varying data coverage and latency; a robust client ensures consistent retrieval. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Implement a wrapper class that abstracts provider specifics; use exponential backoff for retry logic. |

### 4. Batch download historical OHLCV data for all assets simultaneously where the provider supports bulk requests; otherwise loop with a controlled delay to respect rate limits.

| Category | Details |
| --- | --- |
| **Reason** | Maximises throughput and reduces total runtime while avoiding API throttling. |
| **Impact** | HIGH |
| **Complexity** | HIGH |
| **Method** | For `yfinance`, use `download(tickers=asset_list, start=start_date, end=end_date, interval='1d')`; otherwise, parallelise with `concurrent.futures` and sleep between requests. |

### 5. Parse the returned dataset into a standardized pandas DataFrame, ensuring columns: `date`, `open`, `high`, `low`, `close`, `volume`, and any provider‑specific metadata.

| Category | Details |
| --- | --- |
| **Reason** | Uniform structure simplifies downstream preprocessing steps. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Apply `.reset_index()`; rename columns to lowercase; convert `date` to datetime; fill missing columns with NaN. |

### 6. Validate data integrity by checking for missing dates (e.g., weekends, holidays) and missing values; if missing, attempt forward‑fill for price columns and zero‑fill for volume.

| Category | Details |
| --- | --- |
| **Reason** | Missing data can skew statistical tests and signal generation. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use `.asfreq('D')` to resample daily, then `.ffill()` for price, `.fillna(0)` for volume; log the count of filled rows. |

### 7. Compute `data_points_per_asset` by counting non‑NaN close prices per asset, and verify that each asset has at least 90% of the expected daily observations.

| Category | Details |
| --- | --- |
| **Reason** | Ensures each asset contributes sufficient data for robust analysis. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Group by asset ticker; apply `.count()` on close price. |

### 8. Set the `success` flag to true only if all assets have retrieved data, the data window covers the full required period, and no critical errors were encountered during fetch or parsing.

| Category | Details |
| --- | --- |
| **Reason** | Provides downstream nodes with an explicit success indicator. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Maintain a boolean accumulator across assets; update to false on any failure. |

### 9. Persist the raw data to a local or cloud storage location (e.g., Parquet or CSV) with filenames encoded as `<symbol>_<start>_<end>.parquet` for future reproducibility.

| Category | Details |
| --- | --- |
| **Reason** | Facilitates audit trails and allows later steps to load data without re‑fetching. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Use `to_parquet` with compression `snappy`; maintain a metadata manifest JSON. |

### 10. Log a summary of the operation (asset count, date range, total records, errors) to a central logging service or console for traceability.

| Category | Details |
| --- | --- |
| **Reason** | Eases debugging and provides auditability. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use Python’s `logging` module at INFO level. |
