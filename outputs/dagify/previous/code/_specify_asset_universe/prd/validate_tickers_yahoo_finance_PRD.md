# validate_tickers_yahoo_finance PRD

## Description
Validates a list of ticker symbols for correct syntax and confirms their existence on Yahoo Finance, returning only the verified tickers.


## Implementation Plan

### 1. Implement syntactic validation of each ticker using a regular expression that enforces allowed characters and length limits.

| Category | Details |
| --- | --- |
| **Reason** | Ensures only plausibly correct ticker symbols proceed to the external lookup, reducing unnecessary API calls. |
| **Impact** | Filters out obviously malformed tickers early, improving performance and lowering request volume to Yahoo Finance. |
| **Complexity** | LOW |
| **Method** | Define a regex pattern (e.g., `^[A-Z]{1,5}(\.[A-Z]{1,2})?$`) and apply it to each ticker after stripping whitespace. |

### 2. Verify each syntactically valid ticker against Yahoo Finance using the `yfinance` library (or a direct HTTP request to the Yahoo Finance API) and keep only those that return a non‑empty info dict.

| Category | Details |
| --- | --- |
| **Reason** | Only tickers that exist on Yahoo Finance can be used downstream for price retrieval and analysis. |
| **Impact** | Produces a reliable list of tradable symbols, preventing downstream failures when fetching market data. |
| **Complexity** | MEDIUM |
| **Method** | Iterate over the filtered tickers, instantiate `yfinance.Ticker(ticker)`, call `.info` or `.history(period="1d")`, and treat a successful response as validation; handle rate‑limiting with exponential back‑off and cache results for repeated symbols. |
