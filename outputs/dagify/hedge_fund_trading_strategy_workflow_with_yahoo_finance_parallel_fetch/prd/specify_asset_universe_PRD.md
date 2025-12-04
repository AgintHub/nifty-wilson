# specify_asset_universe PRD

## Description
Defines the full investable universe that aligns with the selected trading strategy.


## Implementation Plan

### 1. Extract the `strategy_type` string from the output of `select_trading_strategy_type` and store it in a local variable.

| Category | Details |
| --- | --- |
| **Reason** | The chosen strategy type is the sole deterministic input that drives the asset‑class mapping logic. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Parse the parent node JSON, read `strategy_type`, and validate that it is a non‑empty string. |

### 2. Define a static mapping table that links each supported `strategy_type` to a prioritized list of compatible asset classes, based on quantitative finance literature and industry best‑practice (e.g., "momentum" → ["US equities", "ETF futures"], "mean reversion" → ["US equities", "FX spot"], "stat‑arb" → ["US equities", "ETFs", "Options"]).

| Category | Details |
| --- | --- |
| **Reason** | A deterministic mapping ensures reproducibility and removes ambiguity when selecting asset classes. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Create a Python dict or JSON object; include comments citing sources such as academic papers or Bloomberg research for each mapping. |

### 3. Lookup the extracted `strategy_type` in the mapping table; if not found, raise a clear validation error indicating an unsupported strategy.

| Category | Details |
| --- | --- |
| **Reason** | Fail‑fast validation prevents downstream errors in back‑testing caused by mismatched asset universes. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use a try/except block; error message should include the invalid `strategy_type` and list of supported keys. |

### 4. For each selected asset class, apply a rule‑based ticker selection algorithm: 
- US equities → top 100 liquid stocks by average daily dollar volume from the last 6 months (e.g., S&P 500 constituents + high‑cap mid‑caps). 
- Futures → front‑month continuous contracts for major indices, commodities, and FX (e.g., ES, CL, GC, EUR=, JPY=). 
- ETFs → sector‑specific ETFs that best capture the factor exposure (e.g., XLK for tech momentum). 
- Commodities → physically deliverable contracts with sufficient liquidity (e.g., WTI, Gold).

| Category | Details |
| --- | --- |
| **Reason** | Rule‑based selection guarantees that the tickers are both tradable and representative of the underlying asset class, aligning with the strategy’s signal generation requirements. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Implement helper functions that query a static whitelist (hard‑coded lists) or, if allowed, pull the latest constituents from a public API (e.g., Wikipedia S&P 500 table). Ensure each list is de‑duplicated and sorted alphabetically. |

### 5. Validate each candidate ticker symbol for syntactic correctness (uppercase, alphanumeric, optional suffix for futures contracts) and verify that it exists on Yahoo Finance via a lightweight `yfinance.Ticker(ticker).info` call; filter out any symbols that raise an exception or return empty info.

| Category | Details |
| --- | --- |
| **Reason** | Early validation avoids runtime failures in downstream data‑fetch nodes (`fetch_stock_data_yahoo_data`). |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Iterate over the candidate list, perform a try/except around `ticker.info['regularMarketPrice']`; keep only successful symbols. Log any excluded tickers for audit. |

### 6. Assemble the final `asset_classes` list (derived from the mapping step) and the `asset_tickers` list (the validated, de‑duplicated ticker symbols). Preserve the order: asset classes first as they appear in the mapping, tickers sorted alphabetically within each class.

| Category | Details |
| --- | --- |
| **Reason** | Consistent ordering simplifies downstream indexing and debugging, especially when aligning tickers with fetched data frames. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Create two Python lists; use `sorted()` for tickers; concatenate class‑specific ticker sub‑lists if needed. |

### 7. Return a JSON object conforming exactly to the defined `output_structure`: `asset_classes` as a List[str] and `asset_tickers` as a List[str]. Include a top‑level `success` flag in logs (not part of the schema) to indicate whether the universe generation completed without errors.

| Category | Details |
| --- | --- |
| **Reason** | Strict adherence to the schema guarantees compatibility with downstream nodes that consume these fields. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Serialize the two lists using `json.dumps` ensuring no extra fields are present; raise an exception only if serialization fails. |
