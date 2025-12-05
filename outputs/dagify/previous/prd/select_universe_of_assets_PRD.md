# select_universe_of_assets PRD

## Description
Choose the universe of assets for the statistical arbitrage strategy


## Implementation Plan

### 1. Parse the outputs from **define_strategy_objectives** to build a high‑level asset‑class preference map.

| Category | Details |
| --- | --- |
| **Reason** | The objective definitions (target markets, risk tolerance, expected return, trade frequency) directly constrain which asset classes are suitable for a statistical arbitrage approach. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use a structured mapping table that links target market strings (e.g., 'US Equity', 'EM Equity', 'US ETF') to canonical asset classes. Apply risk tolerance to exclude over‑volatile classes if risk_tolerance_level < 5, and filter out low‑return markets if expected_annual_return > 0.15. |

### 2. Translate trade_frequency_per_day and strategy_horizon_months into a dynamic liquidity requirement.

| Category | Details |
| --- | --- |
| **Reason** | High trade frequency necessitates sufficient daily trading volume; otherwise transaction costs erode profitability. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Compute required daily volume as: 
- RequiredShares = minimum_trade_size * trade_frequency_per_day
- For each candidate ticker, retrieve average daily volume (ADV) over the past 6 months. Keep tickers where ADV >= 10 * RequiredShares to provide a safety margin. |

### 3. Rank candidates by historical volatility and filter to match the specified maximum_drawdown and risk_tolerance_level.

| Category | Details |
| --- | --- |
| **Reason** | Statistical arbitrage relies on mean‑reverting relationships; overly volatile pairs can increase drawdown risk. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Calculate the 30‑day rolling standard deviation for each ticker. Compute an adjusted volatility score = StdDev / sqrt(annualization_factor). Keep tickers with adjusted volatility below a threshold derived from maximum_drawdown: Threshold = max_drawdown * 1.5. This ensures that the expected drawdown stays within specification. |

### 4. Enforce a universe size cap based on the strategy horizon to avoid over‑diversification and maintain manageable backtest granularity.

| Category | Details |
| --- | --- |
| **Reason** | An overly large universe increases data latency, computational cost, and can dilute the statistical signal. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Calculate MaxPositions = strategy_horizon_months * trade_frequency_per_day. If the filtered list exceeds MaxPositions, truncate to the top‑ranked (lowest volatility, highest liquidity) tickers up to MaxPositions. |

### 5. Query a reliable financial data provider (Yahoo Finance, Bloomberg, or Refinitiv) to resolve ticker symbols and asset class metadata for each shortlisted candidate.

| Category | Details |
| --- | --- |
| **Reason** | Accurate identifiers and metadata are required for downstream data collection and signal generation. |
| **Impact** | HIGH |
| **Complexity** | HIGH |
| **Method** | Implement a batched API request pipeline with retry logic. For each ticker, extract: symbol, market, primary asset class, and any relevant sector tags. Store results in a temporary data frame and validate against the filter criteria (e.g., no missing fields). |

### 6. Aggregate final outputs: assemble the selected_assets list, asset_classes set, compose a concise selection_criteria string, and compute number_of_assets.

| Category | Details |
| --- | --- |
| **Reason** | The downstream node **collect_historical_data** expects a clean, validated list of symbols. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Convert the validated DataFrame to a list of symbols for selected_assets; deduplicate asset_classes; format selection_criteria as: "Selected {len} {asset_classes} based on liquidity ≥ 10× required shares, volatility ≤ {max_drawdown*1.5}, and risk tolerance ≤ {risk_tolerance_level}."; set number_of_assets to len(selected_assets). |
