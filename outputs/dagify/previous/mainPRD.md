# build_aquant_trading_strategy_statarb - Complete PRD Documentation

## Overview
PRDs for nodes in the 'build_aquant_trading_strategy_statarb' module.

## Table of Contents

- [backtest_strategy](#backtest_strategy)

- [clean_and_preprocess_data](#clean_and_preprocess_data)

- [collect_historical_data](#collect_historical_data)

- [define_risk_management_rules](#define_risk_management_rules)

- [define_strategy_objectives](#define_strategy_objectives)

- [develop_trading_signals](#develop_trading_signals)

- [evaluate_backtest_results](#evaluate_backtest_results)

- [implement_strategy](#implement_strategy)

- [monitor_and_adjust_strategy](#monitor_and_adjust_strategy)

- [perform_cointegration_analysis](#perform_cointegration_analysis)

- [refine_strategy](#refine_strategy)

- [select_universe_of_assets](#select_universe_of_assets)



---

## backtest_strategy

### Description
Backtest the statistical arbitrage strategy using historical data

### Implementation Plan

#### 1. Load and merge the cleaned historical price series with the generated signal timestamps ensuring time alignment across all asset pairs.

| Category | Details |
| --- | --- |
| **Reason** | Accurate alignment guarantees that signals are evaluated on the correct price data and that trade execution times correspond to the intended market events. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use pandas’ `merge_asof` or `reindex` to align timestamps; validate alignment by checking the number of matched rows against expected signal counts. |

#### 2. Apply the risk‑management rules to each signal to compute position sizing and stop‑loss thresholds before any trade execution.

| Category | Details |
| --- | --- |
| **Reason** | Pre‑computing positions and risk limits ensures that every simulated trade adheres to the predefined constraints, preventing unrealistic P&L estimates. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | For each signal, compute trade size using `position_sizing_rule`; calculate stop‑loss price as `entry_price * (1 ± stop_loss_percent/100)`; store these in a structured dataframe for downstream simulation. |

#### 3. Simulate trade execution by stepping through each trading day, applying all active positions, and updating portfolio equity based on price changes.

| Category | Details |
| --- | --- |
| **Reason** | Day‑by‑day simulation captures intraday volatility, ensures correct PnL accumulation, and respects stop‑loss and max drawdown limits. |
| **Impact** | HIGH |
| **Complexity** | HIGH |
| **Method** | Iterate over the sorted signal dataframe; on each new day, update unrealized PnL for open positions, close positions at stop‑loss if triggered, and record realized PnL; maintain a rolling equity curve. |

#### 4. Enforce the maximum drawdown constraint by monitoring the equity curve and halting new positions once the drawdown exceeds `max_drawdown_percent`.

| Category | Details |
| --- | --- |
| **Reason** | This prevents the backtest from continuing in a regime that would violate the strategy’s risk tolerance, mirroring real‑world portfolio constraints. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Compute peak equity; if current equity < peak * (1 - max_drawdown_percent/100), set a flag to stop opening new positions until equity recovers or simulation ends. |

#### 5. Calculate realized and unrealized profit‑and‑loss per trade, distinguishing winning and losing trades to compute `average_profit_per_trade` and `average_loss_per_trade`.

| Category | Details |
| --- | --- |
| **Reason** | Separating wins and losses provides granular insight into trade quality and assists in refining signal thresholds. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Maintain two lists: `wins` and `losses`; append trade PnL to the appropriate list; compute means after simulation. |

#### 6. Compute cumulative return, annualized return, Sharpe ratio, and maximum drawdown from the equity curve.

| Category | Details |
| --- | --- |
| **Reason** | These metrics are industry standard for assessing strategy performance and risk‑adjusted returns. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use numpy to calculate total return as last equity / initial equity - 1; annualize using `(1+total_return)**(252/num_days)-1`; Sharpe = mean(returns)/std(returns) * sqrt(252); drawdown = (cumulative max - equity)/cumulative max. |

#### 7. Determine the total number of executed trades and calculate the winning trade rate as the ratio of winning trades to total trades.

| Category | Details |
| --- | --- |
| **Reason** | Trade count and win rate are key performance indicators that influence risk‑adjusted metrics and inform strategy robustness. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Count entries in the trade log; compute win rate by dividing number of trades where PnL > 0 by total trades. |

#### 8. Generate a concise `report_summary` string summarizing the key results (e.g., total return, Sharpe, max drawdown, win rate).

| Category | Details |
| --- | --- |
| **Reason** | A quick textual summary aids stakeholders in grasping performance without parsing all numeric fields. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use string interpolation to format the metrics into a one‑sentence paragraph. |

#### 9. Set the `backtest_success` flag to `True` only if the simulation completes without unhandled exceptions, missing data issues, or violation of critical constraints.

| Category | Details |
| --- | --- |
| **Reason** | Clear success indicator ensures downstream nodes can safely proceed or trigger error handling. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Wrap the entire simulation in try/except; on any exception, set flag to False and log error details. |

#### 10. Validate all output fields against expected ranges (e.g., winning_trade_rate ∈ [0,1], max_drawdown_pct ≥ 0) and assert type consistency before returning results.

| Category | Details |
| --- | --- |
| **Reason** | Type and range validation protects downstream processes from corrupt or malformed data, improving system robustness. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use assert statements or custom validation functions; if validation fails, raise descriptive error. |


---

## clean_and_preprocess_data

### Description
Clean and preprocess the collected historical data

### Implementation Plan

#### 1. Validate the success flag from collect_historical_data; abort cleaning if the flag is false to avoid processing invalid datasets.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the node only operates on valid data, preventing cascading errors downstream. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Check `success` in parent output; if false, set all outputs to default failure values and return. |

#### 2. Load raw historical data into a Pandas DataFrame, using asset symbols as keys to create a multi‑index (date, symbol) structure for efficient manipulation.

| Category | Details |
| --- | --- |
| **Reason** | A multi‑index allows column‑wise operations across all assets while preserving date alignment. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Read CSV/JSON files into DataFrames, set `date` as the first index level and `symbol` as the second; ensure datetime dtype. |

#### 3. Compute the total number of cells and the total number of missing cells across all numeric columns to derive the missing data ratio.

| Category | Details |
| --- | --- |
| **Reason** | Provides a quantitative baseline of data quality before any imputation. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use `DataFrame.size` for total cells and `DataFrame.isna().sum().sum()` for missing count; calculate ratio as missing/total. |

#### 4. Identify and remove duplicate rows based on the multi‑index to ensure each date‑symbol combination is unique.

| Category | Details |
| --- | --- |
| **Reason** | Duplicates can bias statistical tests and cointegration analysis. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Apply `DataFrame.drop_duplicates()` with `subset=['date', 'symbol']`. |

#### 5. Apply forward‑fill (`ffill`) then backward‑fill (`bfill`) to propagate existing observations into missing slots, followed by linear interpolation for remaining gaps.

| Category | Details |
| --- | --- |
| **Reason** | Combines robust edge‑handling with smoothness for time‑series data. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Chain `DataFrame.fillna(method='ffill').fillna(method='bfill').interpolate(method='linear')`. |

#### 6. Count the number of missing values that were actually filled during imputation to populate `missing_values_count`.

| Category | Details |
| --- | --- |
| **Reason** | Provides transparency about the extent of imputation performed. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Subtract pre‑imputation missing count from post‑imputation missing count. |

#### 7. Standardize column names by converting all to lowercase and replacing spaces or special characters with underscores.

| Category | Details |
| --- | --- |
| **Reason** | Ensures consistent column references in downstream modules. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use `DataFrame.rename(columns=lambda x: re.sub(r'[^a-z0-9]', '_', x.lower()))`. |

#### 8. Detect outliers in price‑related columns (`open`, `high`, `low`, `close`) using the Inter‑Quartile Range (IQR) method with a 1.5× multiplier.

| Category | Details |
| --- | --- |
| **Reason** | IQR is robust to extreme values and preserves the bulk of the distribution. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | For each column, compute Q1, Q3, IQR = Q3−Q1; flag rows where value < Q1−1.5×IQR or > Q3+1.5×IQR. |

#### 9. Remove all flagged outlier rows from the DataFrame, and record the count in `outliers_removed_count`.

| Category | Details |
| --- | --- |
| **Reason** | Outliers can distort statistical relationships and lead to spurious cointegration signals. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use boolean indexing to drop flagged rows; sum the number of dropped rows. |

#### 10. Confirm that all remaining missing values are resolved and that data types are correct (e.g., numeric for price columns, integer for volume).

| Category | Details |
| --- | --- |
| **Reason** | Prevents type‑related errors in subsequent statistical analyses. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Apply `DataFrame.dtypes` check and cast columns using `astype` where necessary. |

#### 11. Generate the `processed_columns` list by extracting the names of all columns that underwent cleaning or transformation.

| Category | Details |
| --- | --- |
| **Reason** | Provides a traceable record of what was altered, useful for audit and debugging. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Maintain a set of column names during each transformation step and output as a list. |

#### 12. Persist the cleaned DataFrame to a standardized file format (e.g., Parquet) for efficient I/O during cointegration analysis.

| Category | Details |
| --- | --- |
| **Reason** | Parquet offers columnar storage and compression, speeding up downstream reads. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use `DataFrame.to_parquet('cleaned_data.parquet')`. |

#### 13. Set `cleaned_data_available` to true upon successful completion of all steps; otherwise, set to false and populate remaining outputs with sentinel values.

| Category | Details |
| --- | --- |
| **Reason** | Clear success indicator for downstream nodes. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Wrap entire pipeline in try/except; on exception, log error and return failure flags. |


---

## collect_historical_data

### Description
Gather raw historical market data for each asset in the selected universe, ensuring the dataset is complete, accurate, and formatted for downstream preprocessing.

### Implementation Plan

#### 1. Validate and normalise the input asset list from the parent node, ensuring no empty strings and all symbols are upper‑case.

| Category | Details |
| --- | --- |
| **Reason** | Prevents downstream API failures caused by malformed tickers. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use Python set and strip operations; apply .upper() to each symbol; remove duplicates. |

#### 2. Derive the historical time window required for statistical analysis by reading the strategy horizon from `define_strategy_objectives` via the `select_universe_of_assets` node’s output, adding an additional safety buffer of 30 days to account for missing data.

| Category | Details |
| --- | --- |
| **Reason** | Guarantees enough data for cointegration tests while mitigating edge effects. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Convert `strategy_horizon_months` to days, subtract from current date to get `data_start_date`; set `data_end_date` to today's date. |

#### 3. Choose a reliable public or commercial data provider API (e.g., Yahoo Finance via `yfinance`, Alpha Vantage, or Bloomberg) and instantiate a client with appropriate API keys and rate‑limit handling.

| Category | Details |
| --- | --- |
| **Reason** | Different providers offer varying data coverage and latency; a robust client ensures consistent retrieval. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Implement a wrapper class that abstracts provider specifics; use exponential backoff for retry logic. |

#### 4. Batch download historical OHLCV data for all assets simultaneously where the provider supports bulk requests; otherwise loop with a controlled delay to respect rate limits.

| Category | Details |
| --- | --- |
| **Reason** | Maximises throughput and reduces total runtime while avoiding API throttling. |
| **Impact** | HIGH |
| **Complexity** | HIGH |
| **Method** | For `yfinance`, use `download(tickers=asset_list, start=start_date, end=end_date, interval='1d')`; otherwise, parallelise with `concurrent.futures` and sleep between requests. |

#### 5. Parse the returned dataset into a standardized pandas DataFrame, ensuring columns: `date`, `open`, `high`, `low`, `close`, `volume`, and any provider‑specific metadata.

| Category | Details |
| --- | --- |
| **Reason** | Uniform structure simplifies downstream preprocessing steps. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Apply `.reset_index()`; rename columns to lowercase; convert `date` to datetime; fill missing columns with NaN. |

#### 6. Validate data integrity by checking for missing dates (e.g., weekends, holidays) and missing values; if missing, attempt forward‑fill for price columns and zero‑fill for volume.

| Category | Details |
| --- | --- |
| **Reason** | Missing data can skew statistical tests and signal generation. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use `.asfreq('D')` to resample daily, then `.ffill()` for price, `.fillna(0)` for volume; log the count of filled rows. |

#### 7. Compute `data_points_per_asset` by counting non‑NaN close prices per asset, and verify that each asset has at least 90% of the expected daily observations.

| Category | Details |
| --- | --- |
| **Reason** | Ensures each asset contributes sufficient data for robust analysis. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Group by asset ticker; apply `.count()` on close price. |

#### 8. Set the `success` flag to true only if all assets have retrieved data, the data window covers the full required period, and no critical errors were encountered during fetch or parsing.

| Category | Details |
| --- | --- |
| **Reason** | Provides downstream nodes with an explicit success indicator. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Maintain a boolean accumulator across assets; update to false on any failure. |

#### 9. Persist the raw data to a local or cloud storage location (e.g., Parquet or CSV) with filenames encoded as `<symbol>_<start>_<end>.parquet` for future reproducibility.

| Category | Details |
| --- | --- |
| **Reason** | Facilitates audit trails and allows later steps to load data without re‑fetching. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Use `to_parquet` with compression `snappy`; maintain a metadata manifest JSON. |

#### 10. Log a summary of the operation (asset count, date range, total records, errors) to a central logging service or console for traceability.

| Category | Details |
| --- | --- |
| **Reason** | Eases debugging and provides auditability. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use Python’s `logging` module at INFO level. |


---

## define_risk_management_rules

### Description
Establish risk management rules for the strategy

### Implementation Plan

#### 1. Validate the input from develop_trading_signals – check the `is_valid` flag and ensure that at least one signal is available. If the signals are invalid, default to conservative risk parameters (e.g., risk_per_trade_percent = 0.5%, stop_loss_percent = 5%).

| Category | Details |
| --- | --- |
| **Reason** | Ensures that risk rules are only generated when reliable trading signals exist, preventing the propagation of erroneous risk settings. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Check boolean flag; use conditional logic to assign defaults. |

#### 2. Determine the maximum number of simultaneous positions (`max_positions`) by taking the minimum of the number of generated signals (`num_signals`) and a hard‑coded portfolio capacity limit (e.g., 10). This caps exposure and encourages diversification.

| Category | Details |
| --- | --- |
| **Reason** | Balances trade execution volume against portfolio risk limits and prevents over‑concentration. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Apply min(num_signals, 10) to compute max_positions. |

#### 3. Compute the base risk‑per‑trade percentage by scaling a default risk appetite (1%) with the strategy’s risk tolerance level. For example, `risk_per_trade_percent = 1.0 * (risk_tolerance_level / 10)`. If the risk_tolerance_level is not available, default to 1.0%.

| Category | Details |
| --- | --- |
| **Reason** | Aligns trade risk with the overall strategy risk tolerance, making the rule adjustable to different risk profiles. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use simple arithmetic; fallback to default if missing. |

#### 4. Calculate the stop‑loss threshold (`stop_loss_percent`) as a function of the asset’s historical volatility. Compute a 30‑day rolling volatility of the asset’s returns, convert to a daily volatility, then set `stop_loss_percent = 2.0 + (daily_vol * 100 * 0.5)`. Cap the value at 5% to avoid overly tight stops during high‑volatility periods.

| Category | Details |
| --- | --- |
| **Reason** | Dynamic stop‑loss sizing protects against both low‑ and high‑volatility regimes, improving risk‑adjusted performance. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Run a volatility rolling window calculation, apply scaling, enforce upper bound. |

#### 5. Set the maximum drawdown limit (`max_drawdown_percent`) to a conservative fraction (e.g., 75%) of the strategy objective’s maximum drawdown. If the objective maximum drawdown is unavailable, default to 10.0%. This provides a hard stop that aligns with strategic goals.

| Category | Details |
| --- | --- |
| **Reason** | Ensures portfolio drawdown remains within acceptable bounds, protecting capital during adverse market movements. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Multiply objective_max_drawdown by 0.75; fallback to default. |

#### 6. Define the position sizing rule (`position_sizing_rule`) as a volatility‑based approach: `position_size = (portfolio_equity * risk_per_trade_percent / 100) / (stop_loss_percent / 100 * entry_price)`. Store a textual description of this methodology.

| Category | Details |
| --- | --- |
| **Reason** | Volatility‑based sizing adapts trade size to market conditions and ensures consistent risk exposure per trade. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Implement the formula; generate description string. |

#### 7. Compile additional risk controls into `risk_control_description`: include diversification limits (no single asset pair >20% of portfolio), a market‑volatility filter (skip trades if implied volatility > 30%), daily position limit enforcement, and a mandatory stop‑loss audit. Provide a concise paragraph summarizing these controls.

| Category | Details |
| --- | --- |
| **Reason** | Documenting all supplementary controls ensures transparency and auditability for the strategy. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Concatenate predefined control statements into a single string. |

#### 8. Perform consistency checks: ensure that `stop_loss_percent` is between 1% and 5%, `risk_per_trade_percent` between 0.1% and 3%, and `max_drawdown_percent` not exceeding 20%. If any value falls outside these bounds, adjust to nearest permissible limit and record a warning in the `risk_control_description`.

| Category | Details |
| --- | --- |
| **Reason** | Prevents unrealistic or unsafe risk parameters that could jeopardize portfolio stability. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Apply boundary conditions; log adjustments. |

#### 9. Output all computed fields in the specified schema, ensuring type correctness: convert percentages to float, integer fields to int, and descriptions to string.

| Category | Details |
| --- | --- |
| **Reason** | Guarantees that downstream nodes receive data in the expected format for accurate backtesting. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Cast values to required types; serialize to JSON. |


---

## define_strategy_objectives

### Description
Define the primary objectives of the statistical arbitrage strategy

### Implementation Plan

#### 1. Gather high‑level business and stakeholder goals through structured interviews and questionnaires, capturing desired return targets, acceptable risk levels, and investment horizon preferences.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that the objectives are rooted in real business intent and not just theoretical constructs. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use a standardized interview guide, record responses in a shared spreadsheet, and tag each goal with the originating stakeholder. |

#### 2. Translate qualitative goals into quantitative metrics: convert requested return percentages into decimal form, define drawdown as a decimal, and map qualitative risk appetite to a 1‑10 scale.

| Category | Details |
| --- | --- |
| **Reason** | Quantification is required for downstream modeling and risk‑management alignment. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Apply simple arithmetic (e.g., 12% → 0.12) and a mapping table for risk tolerance levels. |

#### 3. Define target markets by evaluating liquidity, volatility, and historical cointegration potential across candidate asset classes; produce a ranked list of markets that meet a minimum liquidity threshold (e.g., average daily volume > $10M).

| Category | Details |
| --- | --- |
| **Reason** | Market selection directly affects transaction costs, slippage, and the ability to identify mean‑reverting pairs. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Query a market data repository, apply filters, and generate a CSV of markets with key metrics. |

#### 4. Determine strategy horizon months by analyzing typical mean‑reversion cycle lengths and aligning them with the intended capital deployment schedule; recommend a horizon that covers at least 3–5 full cycles.

| Category | Details |
| --- | --- |
| **Reason** | Horizon decisions impact backtest length, risk metrics, and capital allocation. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Perform a rolling window statistical analysis of historical pair spreads and calculate average cycle duration. |

#### 5. Set minimum trade size based on the average bid‑ask spread, slippage tolerance, and transaction cost model; compute a conservative size that ensures a minimum spread capture relative to cost.

| Category | Details |
| --- | --- |
| **Reason** | Avoids trade execution that is dominated by cost and ensures meaningful signal validation. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use cost‑to‑trade formulas: trade_size ≥ (average_spread * transaction_cost_factor) / expected_profit_per_share. |

#### 6. Estimate trade frequency per day by simulating the signal generation logic on a sample of recent data and counting the average number of valid signals per trading day.

| Category | Details |
| --- | --- |
| **Reason** | Provides a realistic expectation for infrastructure load and risk‑management bandwidth. |
| **Impact** | LOW |
| **Complexity** | MEDIUM |
| **Method** | Run a back‑test kernel on a 30‑day window, record signal count, and calculate the mean. |

#### 7. Validate that the maximum drawdown and risk tolerance level are consistent with the risk‑management rule set produced in define_risk_management_rules; adjust if any conflicts exist.

| Category | Details |
| --- | --- |
| **Reason** | Ensures coherence across strategy definition and risk controls. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Cross‑reference numerical thresholds and, if necessary, iterate with the risk‑management node to reconcile. |

#### 8. Document all assumptions, source data, and decision rationales in a single markdown file that will feed into select_universe_of_assets for transparency and future audits.

| Category | Details |
| --- | --- |
| **Reason** | Facilitates traceability and allows stakeholders to review the objective setting process. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Auto‑generate a markdown template and populate fields using the results from previous bullets. |


---

## develop_trading_signals

### Description
Develop trading signals based on the cointegration analysis

### Implementation Plan

#### 1. Validate the input from perform_cointegration_analysis: ensure 'cointegrated_pairs' is a non-empty list and that 'johansen_p_value' is below the significance threshold (e.g., 0.05). If validation fails, set 'is_valid' to false and terminate early.

| Category | Details |
| --- | --- |
| **Reason** | Early validation prevents downstream errors and guarantees that only statistically significant relationships are used for signal generation. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Simple length check and conditional comparison of p-value; raise a descriptive exception if invalid. |

#### 2. Iterate over each pair in 'cointegrated_pairs' and retrieve the corresponding time series of asset prices from the preprocessed dataset (assumed available globally or passed via context).

| Category | Details |
| --- | --- |
| **Reason** | Signal generation requires real price data; iterating allows pair‑wise processing. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Use a for‑loop with a dictionary lookup or SQL query to pull the two series; store them in a pandas DataFrame for vectorized operations. |

#### 3. Compute the hedge ratio (β) for each pair using ordinary least squares (OLS) regression of AssetB on AssetA. Store β to construct the spread series: spread = price_B - β * price_A.

| Category | Details |
| --- | --- |
| **Reason** | Hedge ratio defines the linear relationship that should hold under equilibrium; accurate β is critical for mean‑reversion detection. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Leverage statsmodels' OLS; handle singular matrix exceptions; normalize β to account for scale differences. |

#### 4. Calculate the rolling mean and rolling standard deviation of the spread using a fixed window (e.g., 30 days). Compute the Z‑score: z = (spread - mean_spread) / std_spread.

| Category | Details |
| --- | --- |
| **Reason** | Z‑score normalizes the spread, enabling threshold‑based signal decisions irrespective of absolute price levels. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use pandas' rolling().mean() and rolling().std(); ensure min_periods=window to avoid NaNs. |

#### 5. Define entry and exit thresholds for mean‑reversion: e.g., entry at |z| > 1.5 and exit at |z| < 0.5. For each timestamp, generate a 'long' signal when z < -entry_threshold and a 'short' when z > entry_threshold; close positions when z crosses the exit threshold.

| Category | Details |
| --- | --- |
| **Reason** | Thresholds translate statistical deviations into actionable trade decisions and help control risk exposure. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Vectorized comparison; maintain a position flag per pair to avoid duplicate signals; use pandas' where() to label signals. |

#### 6. Calculate signal strength as the absolute Z‑score normalized by a maximum observed Z‑score across all pairs and time points (strength = |z| / max_z). Clip values to the [0,1] range.

| Category | Details |
| --- | --- |
| **Reason** | Provides a continuous confidence metric that can be used for position sizing or risk weighting. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Compute max_z once per pair; divide; use numpy.clip. |

#### 7. Aggregate results into three lists: 'pair_ids' (pair string), 'signal_type' (list of 'long'/'short'), and 'signal_strength' (list of floats). Count total signals to set 'num_signals' and set 'is_valid' to true if lists are non‑empty.

| Category | Details |
| --- | --- |
| **Reason** | Matches the required output schema and ensures completeness of the signal set. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Append to lists in the loop; after loop, compute length; convert to appropriate types. |

#### 8. Implement error handling for missing data: if a pair’s price series contains NaNs beyond a tolerance threshold (e.g., >10%), discard the pair and log the exclusion with a warning.

| Category | Details |
| --- | --- |
| **Reason** | Avoids generating misleading signals from incomplete data which could harm backtest fidelity. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use pandas Series.isna().sum() to count; compare to threshold; use Python logging. |

#### 9. Create a deterministic seed for any random components (e.g., if simulating stochastic thresholds) to ensure reproducibility of signals across runs.

| Category | Details |
| --- | --- |
| **Reason** | Statistical arbitrage strategies must be reproducible for debugging and audit purposes. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Set numpy.random.seed(42) at the start of the module. |

#### 10. Validate that the total number of generated signals does not exceed a predefined maximum per day (e.g., 20) to respect trading capacity constraints; if exceeded, rank signals by strength and retain top N.

| Category | Details |
| --- | --- |
| **Reason** | Prevents over‑trading and ensures compliance with market microstructure constraints. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Group signals by date; if len > max, sort by strength descending and slice. |

#### 11. Serialize the output dictionaries into the specified JSON format, ensuring data types match the schema (e.g., convert numpy types to native Python types).

| Category | Details |
| --- | --- |
| **Reason** | Compatibility with downstream nodes that expect pure Python primitives. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use json.dumps() with a custom encoder or cast explicitly before assignment. |

#### 12. Log a summary of signal generation: number of pairs processed, average signal strength, and any pairs discarded for data quality reasons.

| Category | Details |
| --- | --- |
| **Reason** | Provides transparency for debugging and audit trails. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Python logging at INFO level. |


---

## evaluate_backtest_results

### Description
Evaluates the backtest output by transforming raw metrics into standardized, decimal‑based figures, computing derived statistics such as profit factor and average trade PnL, benchmarking against a reference return, and flagging viability against predefined thresholds. The result is a concise, human‑readable summary of strengths, weaknesses, and suggested improvements.

### Implementation Plan

#### 1. Validate the backtest_strategy output to ensure all required fields are present and numeric before proceeding.

| Category | Details |
| --- | --- |
| **Reason** | Early validation prevents downstream errors and guarantees that all metrics exist for conversion and calculation. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Check presence of keys ['total_return_pct', 'sharpe_ratio', 'max_drawdown_pct', 'trade_count', 'winning_trade_rate', 'average_profit_per_trade', 'average_loss_per_trade'] and that each value is a float or int; raise informative error if validation fails. |

#### 2. Convert percentage‑based metrics from backtest_strategy into decimal form (divide by 100).

| Category | Details |
| --- | --- |
| **Reason** | Standardizes units across all outputs and aligns with the expected output format for total_return, max_drawdown, and benchmark_return. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | total_return = total_return_pct / 100.0; max_drawdown = max_drawdown_pct / 100.0; benchmark_return = benchmark_pct / 100.0 (if benchmark_pct is available). |

#### 3. Directly map the Sharpe ratio from backtest_strategy to the output field.

| Category | Details |
| --- | --- |
| **Reason** | Sharpe ratio is already expressed in standard decimal form and does not require scaling. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | sharpe_ratio = backtest_strategy['sharpe_ratio']. |

#### 4. Assign the trade count and win rate from backtest_strategy to num_trades and win_rate.

| Category | Details |
| --- | --- |
| **Reason** | These metrics already match the desired output types and represent core performance indicators. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | num_trades = int(backtest_strategy['trade_count']); win_rate = float(backtest_strategy['winning_trade_rate']). |

#### 5. Calculate avg_trade_pnl as the net average per trade by subtracting the average loss from the average profit and normalizing by initial capital of 1.

| Category | Details |
| --- | --- |
| **Reason** | Provides a clear per‑trade profitability metric that is independent of capital size. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | avg_trade_pnl = float(backtest_strategy['average_profit_per_trade']) - float(backtest_strategy['average_loss_per_trade']). |

#### 6. Derive profit_factor using gross profit and gross loss totals.

| Category | Details |
| --- | --- |
| **Reason** | Profit factor is a key risk‑adjusted metric; calculating it from backtest averages yields an interpretable figure. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | [gross_profit = avg_profit_per_trade * win_rate * num_trades, gross_loss = avg_loss_per_trade * (1 - win_rate) * num_trades, profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')] |

#### 7. Determine benchmark_return by retrieving the benchmark's cumulative return for the same date range (assumed available via an external lookup).

| Category | Details |
| --- | --- |
| **Reason** | Benchmark comparison contextualizes performance. |
| **Impact** | LOW |
| **Complexity** | MEDIUM |
| **Method** | If external function get_benchmark_return(start_date, end_date) returns decimal, assign it; otherwise set benchmark_return = 0.0. |

#### 8. Apply predefined viability thresholds (e.g., Sharpe > 1.0, max_drawdown < 0.10, win_rate > 0.40, profit_factor > 1.5) to set is_acceptable.

| Category | Details |
| --- | --- |
| **Reason** | Automates decision‑making for strategy refinement and aligns with common risk‑return trade‑offs. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | is_acceptable = all([sharpe_ratio > 1.0, max_drawdown < 0.10, win_rate > 0.40, profit_factor > 1.5]). |

#### 9. Generate summary_notes by evaluating each metric against threshold ranges and producing bullet‑point feedback.

| Category | Details |
| --- | --- |
| **Reason** | Provides actionable insight for stakeholders and the refinement step. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | [notes = [], if sharpe_ratio < 1.0: notes.append('- Sharpe ratio below target; consider tightening stop‑loss or improving signal precision.'), if max_drawdown >= 0.10: notes.append('- Drawdown exceeds acceptable limit; review position sizing and risk controls.'), if win_rate < 0.40: notes.append('- Low win rate; examine entry/exit thresholds or incorporate additional filters.'), if profit_factor <= 1.5: notes.append('- Profit factor low; investigate slippage or execution quality.'), if not notes: notes.append('- Strategy meets all viability criteria; ready for deployment.')] |


---

## implement_strategy

### Description
Implement the refined statistical arbitrage strategy in a trading system

### Implementation Plan

#### 1. Extract refined strategy parameters, signal rules, and risk updates from the `refine_strategy` node and map them to code‑ready constants and configuration objects.

| Category | Details |
| --- | --- |
| **Reason** | Centralizes all adjustments in a single, reusable configuration module, ensuring consistency between the refined strategy and the production implementation. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Create a Python module `config.py` that reads a JSON/YAML file generated by `refine_strategy`. Use dataclasses for type safety; populate fields such as `PARAMETER_ADJUSTMENTS`, `SIGNAL_RULE_CHANGES`, `RISK_RULE_UPDATES`. |

#### 2. Design the signal generation engine to consume the configuration constants and apply the refined signal rules on incoming market data streams.

| Category | Details |
| --- | --- |
| **Reason** | Keeps the signal logic decoupled from static code, allowing future rule changes without code redeployment. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Implement a `SignalGenerator` class that accepts a `Pair` object and a `SignalRule` dataclass. Use vectorized NumPy/Pandas operations for real‑time performance. Validate output with unit tests against historical backtests. |

#### 3. Implement the position sizing and risk control logic using the updated `RISK_RULE_UPDATES` from the parent node, referencing original risk definitions from `define_risk_management_rules` when necessary.

| Category | Details |
| --- | --- |
| **Reason** | Guarantees that the live strategy enforces the same risk limits refined from backtests. |
| **Impact** | HIGH |
| **Complexity** | HIGH |
| **Method** | Create a `RiskManager` class that calculates trade size based on `risk_per_trade_percent`, `max_drawdown_percent`, and `max_positions`. Use a rolling volatility estimator (e.g., ATR or standard deviation) to adjust size dynamically. Include stop‑loss and take‑profit triggers derived from `stop_loss_percent` and new thresholds. |

#### 4. Wrap the signal and risk modules into a trade execution handler that interfaces with the chosen broker API (e.g., Interactive Brokers, Alpaca, or a proprietary engine).

| Category | Details |
| --- | --- |
| **Reason** | Provides the necessary bridge between strategy logic and real‑time order execution. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Implement an `OrderExecutor` that uses the broker's REST/WebSocket SDK. Abstract connection details in a config file; implement order lifecycle callbacks (order sent, filled, canceled). Handle partial fills and slippage modeling. |

#### 5. Implement comprehensive logging, monitoring, and alerting to track strategy performance and risk metrics in real time.

| Category | Details |
| --- | --- |
| **Reason** | Facilitates rapid detection of anomalies and ensures compliance with risk thresholds. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Use structured logging (JSON) to a central log store. Push key metrics to a monitoring dashboard (Prometheus + Grafana). Set alert rules for breaches of `max_drawdown_percent` and `risk_per_trade_percent`. |

#### 6. Write integration tests that deploy the strategy into a sandbox environment, validate order execution, and confirm risk control enforcement.

| Category | Details |
| --- | --- |
| **Reason** | Detects integration issues before live deployment. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use pytest with fixtures that mock broker responses. Verify that orders are not placed if risk limits are exceeded. Capture logs to confirm `risk_control_compliance` flag is true. |

#### 7. Create a CI/CD pipeline that builds, tests, packages, and deploys the strategy code to the live environment, automatically updating `code_file_paths` and recording deployment timestamps.

| Category | Details |
| --- | --- |
| **Reason** | Ensures repeatable, auditable deployments and automatic tracking of deployment history. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use GitHub Actions or Jenkins. Define jobs: lint → test → build → deploy. On successful deploy, push `code_file_paths`, set `deployment_status='Success'`, record `last_deployment_timestamp` via `datetime.utcnow().isoformat()`. If deployment fails, set status to 'Failure' and log error. |

#### 8. Generate `integration_notes` summarizing platform specifics (API endpoints, authentication, order types) and any platform‑specific quirks (e.g., quote currency, lot size limits).

| Category | Details |
| --- | --- |
| **Reason** | Provides maintainers with quick reference to platform integration details. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Collect notes during the implementation phase; store them in a markdown file and reference the path in the `integration_notes` output. |

#### 9. After deployment, run a short live test to confirm that orders are executed and risk controls trigger as expected, then set `risk_control_compliance=True`.

| Category | Details |
| --- | --- |
| **Reason** | Validates that the strategy behaves correctly in a live market and meets the defined risk thresholds. |
| **Impact** | HIGH |
| **Complexity** | HIGH |
| **Method** | Execute a series of simulated orders in a paper trading account. Capture risk metrics (drawdown, position size). If all limits are respected and no violations occur, set the compliance flag to true; otherwise, log detailed failure reasons. |

#### 10. Document the entire codebase, including module responsibilities, configuration schemas, and deployment instructions, and store it in a centralized repository.

| Category | Details |
| --- | --- |
| **Reason** | Facilitates knowledge transfer and future maintenance. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Create README.md, API documentation (e.g., using Sphinx or MkDocs), and a `docs/` folder with architecture diagrams. |


---

## monitor_and_adjust_strategy

### Description
Continuously monitor the strategy's performance and adjust as necessary

### Implementation Plan

#### 1. Activate the monitoring flag by setting `monitoring_active` to true when the strategy is in a deployed state (i.e., `deployment_status` equals 'Success').

| Category | Details |
| --- | --- |
| **Reason** | The monitoring process should only run for actively deployed strategies to avoid unnecessary computation on failed or pending deployments. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | If implement_strategy.deployment_status == 'Success' then monitoring_active = True else monitoring_active = False |

#### 2. Retrieve the most recent trade and portfolio snapshot from the broker's REST API or database using the `last_deployment_timestamp` as a reference point.

| Category | Details |
| --- | --- |
| **Reason** | Performance metrics must reflect the live state of the strategy after the last deployment, ensuring metrics are up‑to‑date. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use authenticated HTTP requests to the broker's /portfolio endpoint, filter by strategy_id and timestamp >= last_deployment_timestamp, parse JSON into a pandas DataFrame |

#### 3. Compute `latest_annualized_return`, `latest_sharpe_ratio`, and `latest_max_drawdown` from the fetched trade history using standard formulas: annualized_return = (final_portfolio_value / initial_value)^(252/total_trading_days) - 1; sharpe = mean(return) / std(return) * sqrt(252); max_drawdown = (peak_portfolio_value - trough_value) / peak_portfolio_value.

| Category | Details |
| --- | --- |
| **Reason** | These metrics provide quantitative indicators of the strategy’s performance and risk profile needed for decision making. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Implement calculation in Python using numpy/pandas; ensure handling of zero variance cases and missing data |

#### 4. Count `trades_executed_since_last_check` by grouping the trade history by timestamp and summing trades between the last check timestamp and now.

| Category | Details |
| --- | --- |
| **Reason** | The number of trades indicates market activity and can trigger parameter adjustment thresholds. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use pandas groupby on 'timestamp' and count 'trade_id' |

#### 5. Evaluate adjustment criteria: if `latest_sharpe_ratio` falls below a predefined threshold (e.g., 0.5) or `latest_max_drawdown` exceeds the maximum allowed (from `define_risk_management_rules.max_drawdown_percent`), set `adjustments_made` to true and trigger a parameter update cycle.

| Category | Details |
| --- | --- |
| **Reason** | Thresholds provide an objective basis for when to intervene, ensuring the strategy remains within risk tolerance. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Implement a rule engine or simple if/else logic comparing metrics to stored config values |

#### 6. If adjustments are triggered, load the current strategy configuration (e.g., from a JSON config file), modify relevant fields such as position sizing multiplier or stop‑loss percent, and record each change in a list for `parameter_change_count`.

| Category | Details |
| --- | --- |
| **Reason** | Parameter adjustments must be transparent and auditable to maintain compliance and reproducibility. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Read config JSON, apply incremental updates, serialize back; increment counter for each field modified |

#### 7. Persist the updated configuration back to the deployment environment (e.g., upload to a configuration server or re‑deploy the strategy code) and log the `adjustment_description` summarizing the changes made.

| Category | Details |
| --- | --- |
| **Reason** | Persisting ensures the new parameters are actively used in subsequent trades; logging aids future audits. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use platform's config API or SCP to server; append a human‑readable description to a changelog file |

#### 8. Update `last_adjustment_timestamp` with the current UTC timestamp in ISO 8601 format immediately after persisting changes.

| Category | Details |
| --- | --- |
| **Reason** | A timestamp is required for audit trails and to calculate `next_check_in_days` accurately. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | datetime.utcnow().isoformat() + 'Z' |

#### 9. Calculate `next_check_in_days` by adding a configurable monitoring interval (e.g., 1 day) to the current date, or dynamically adjusting the interval based on volatility metrics (e.g., increase frequency during high volatility).

| Category | Details |
| --- | --- |
| **Reason** | Adaptive check frequency ensures timely reaction to market changes while conserving resources during stable periods. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | If VIX > threshold then next_check_in_days = 0 else next_check_in_days = 1 |

#### 10. Export all computed fields into the defined output structure as JSON, ensuring type compliance (e.g., floats rounded to 4 decimals, integers cast appropriately).

| Category | Details |
| --- | --- |
| **Reason** | Consistent data serialization facilitates downstream ingestion and monitoring dashboards. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use json.dumps with type casting; apply round() for numeric fields |


---

## perform_cointegration_analysis

### Description
Conduct cointegration analysis on the preprocessed data to discover statistically meaningful long‑term equilibrium relationships among asset prices.

### Implementation Plan

#### 1. Validate that the parent node produced a usable cleaned dataset by checking the 'cleaned_data_available' flag. If false, set all outputs to safe defaults (empty list, 0.0, false, 0) and exit.

| Category | Details |
| --- | --- |
| **Reason** | Avoid downstream failures caused by attempting statistical tests on missing or incomplete data. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | If cleaned_data_available == False: return outputs with defaults. |

#### 2. Retrieve the cleaned price matrix from shared storage (e.g., a CSV file or in‑memory DataFrame). Ensure columns correspond to asset tickers and that the DataFrame is indexed by date with no missing rows.

| Category | Details |
| --- | --- |
| **Reason** | The Johansen test requires a clean, aligned multivariate time series. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use pandas.read_csv or a global variable. Validate date range consistency across assets. |

#### 3. Determine the list of asset symbols to test by filtering columns that contain price data (e.g., close prices). Use the 'processed_columns' from the parent node to confirm these columns.

| Category | Details |
| --- | --- |
| **Reason** | Focus the test only on relevant price series and avoid including non‑numeric or auxiliary columns. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Select columns where dtype is numeric and not in a blacklist. |

#### 4. For each unordered asset pair (A,B), construct a 2‑column sub‑DataFrame and apply the Johansen cointegration test with lag order 1 (or determine optimal lag using AIC/BIC on the full multivariate system).

| Category | Details |
| --- | --- |
| **Reason** | Pair‑wise testing captures specific long‑run relationships needed for statistical arbitrage signals. |
| **Impact** | HIGH |
| **Complexity** | HIGH |
| **Method** | Use statsmodels.tsa.vector_ar.vecm.coint_johansen on the 2‑column data. Set det_order=0 to test for a cointegrating relationship without deterministic trend. |

#### 5. Extract the trace statistic and critical values from the test results. Compute the p‑value by comparing the trace statistic to the asymptotic chi‑square distribution using the eigenvalues provided by the library.

| Category | Details |
| --- | --- |
| **Reason** | The trace statistic indicates the number of cointegrating vectors; p‑value quantifies significance. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use results.lr1 for trace stats and results.cvt for critical values; compute p-value with scipy.stats.chi2.sf(trace_stat, df). |

#### 6. Declare a pair as cointegrated if the trace statistic exceeds the 5% critical value (or any user‑defined significance level). Append the pair in 'AssetA-AssetB' format to 'cointegrated_pairs'.

| Category | Details |
| --- | --- |
| **Reason** | Ensures only statistically robust relationships are used downstream. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Compare trace_stat > results.cvt[0, 4] (5% level). |

#### 7. After iterating over all pairs, compute the overall Johansen trace statistic for the full asset universe by running the test on the full cleaned DataFrame and aggregating the trace statistics for each possible cointegrating rank.

| Category | Details |
| --- | --- |
| **Reason** | Provides a global metric of cointegration strength across the selected assets. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Run coint_johansen on the full DataFrame, use the largest eigenvalue statistic as overall trace. |

#### 8. Calculate a single overall p‑value by assessing the significance of the largest trace statistic against its chi‑square distribution with df equal to the number of assets minus one.

| Category | Details |
| --- | --- |
| **Reason** | Allows downstream components to gauge overall market integration. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | p_value = scipy.stats.chi2.sf(max_trace, df). |

#### 9. Set 'is_significant' to True if at least one pair passed the significance test; otherwise False.

| Category | Details |
| --- | --- |
| **Reason** | Provides a quick flag for the trading signals module. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | is_significant = len(cointegrated_pairs) > 0. |

#### 10. Populate 'num_pairs' with the length of the 'cointegrated_pairs' list.

| Category | Details |
| --- | --- |
| **Reason** | Facilitates downstream reporting and threshold checks. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | num_pairs = len(cointegrated_pairs). |

#### 11. Wrap the entire procedure in a try/except block to catch statistical convergence warnings or data issues. On exception, log the error, return safe defaults, and set 'is_significant' to False.

| Category | Details |
| --- | --- |
| **Reason** | Robustness against edge cases like singular covariance matrices or insufficient data. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use warnings.catch_warnings, filterwarnings('error'), and log exceptions. |


---

## refine_strategy

### Description
Refine the statistical arbitrage strategy based on backtest results

### Implementation Plan

#### 1. Extract all numeric performance metrics from the `evaluate_backtest_results` output to establish a baseline for refinement.

| Category | Details |
| --- | --- |
| **Reason** | The baseline metrics are required to assess gaps relative to strategy objectives and to guide parameter tuning. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Read the JSON fields: total_return, sharpe_ratio, max_drawdown, win_rate, avg_trade_pnl, profit_factor, benchmark_return, and is_acceptable. Store them in a local dictionary for subsequent calculations. |

#### 2. Compare the backtest Sharpe ratio, maximum drawdown, and win‑rate against the target thresholds derived from `define_strategy_objectives` and risk‑tolerance settings.

| Category | Details |
| --- | --- |
| **Reason** | Identifying quantitative shortfalls enables a focused refinement of parameters that directly affect these metrics. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | If sharpe_ratio < 1.0 or max_drawdown > 0.1 or win_rate < 0.4, flag the metric as needing improvement. Compute delta values for each flagged metric. |

#### 3. Generate a list of parameter adjustments by mapping identified metric gaps to concrete tweak rules (e.g., reducing the entry z‑score threshold, shortening the look‑back period, or lowering the position sizing factor).

| Category | Details |
| --- | --- |
| **Reason** | Rule‑based mapping provides a systematic, reproducible way to alter strategy inputs that influence performance. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Create a decision table: if max_drawdown > target, add "Reduce stop‑loss to X%"; if win_rate < target, add "Increase entry threshold from Y to Z"; if avg_trade_pnl low, add "Increase trade frequency by N trades/day". Append each suggested tweak to `parameter_adjustments`. |

#### 4. Formulate signal rule changes that refine trade entry and exit logic by tightening confidence filters and adding trend‑filter conditions.

| Category | Details |
| --- | --- |
| **Reason** | Reducing signal noise improves win‑rate and Sharpe ratio without significantly impacting return. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Analyse the `signal_strength` distribution; propose new thresholds (e.g., only act when signal_strength > 0.8). Also suggest adding a momentum filter: only trade when the underlying spread’s recent slope is > 0.2. Record each rule change in `signal_rule_changes`. |

#### 5. Update risk‑management rules to align with new parameter and signal settings, ensuring that position sizing, stop‑loss levels, and maximum drawdown limits remain coherent.

| Category | Details |
| --- | --- |
| **Reason** | Risk controls must adapt to the modified strategy to maintain overall portfolio safety. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | If stop‑loss percent was lowered, also reduce `max_drawdown_percent` by 2%. If position sizing was increased, adjust `risk_per_trade_percent` downward to keep total risk capped. Log each adjustment in `risk_rule_updates`. |

#### 6. Estimate projected performance improvements using heuristic multipliers: assume a 20% relative increase in Sharpe ratio, 1–2% absolute increase in annualized return, and a 1–2% absolute reduction in max drawdown for the refined strategy.

| Category | Details |
| --- | --- |
| **Reason** | Providing quantified expectations helps stakeholders assess the value of the refinements and informs the next deployment. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Compute `expected_sharpe_increase` = sharpe_ratio * 0.20; compute `expected_annual_return_increase` = benchmark_return * 0.01 (or 0.02 if current return < benchmark); compute `expected_drawdown_reduction` = max_drawdown * 0.10. Round each to four decimal places. |

#### 7. Populate all output lists (`parameter_adjustments`, `signal_rule_changes`, `risk_rule_updates`) with the strings generated in the previous steps, then assign the projected improvement values to the numeric output fields.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the node’s output conforms exactly to the defined output structure. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Create a result dictionary matching the output structure and serialize it to JSON. |


---

## select_universe_of_assets

### Description
Choose the universe of assets for the statistical arbitrage strategy

### Implementation Plan

#### 1. Parse the outputs from **define_strategy_objectives** to build a high‑level asset‑class preference map.

| Category | Details |
| --- | --- |
| **Reason** | The objective definitions (target markets, risk tolerance, expected return, trade frequency) directly constrain which asset classes are suitable for a statistical arbitrage approach. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use a structured mapping table that links target market strings (e.g., 'US Equity', 'EM Equity', 'US ETF') to canonical asset classes. Apply risk tolerance to exclude over‑volatile classes if risk_tolerance_level < 5, and filter out low‑return markets if expected_annual_return > 0.15. |

#### 2. Translate trade_frequency_per_day and strategy_horizon_months into a dynamic liquidity requirement.

| Category | Details |
| --- | --- |
| **Reason** | High trade frequency necessitates sufficient daily trading volume; otherwise transaction costs erode profitability. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Compute required daily volume as: 
- RequiredShares = minimum_trade_size * trade_frequency_per_day
- For each candidate ticker, retrieve average daily volume (ADV) over the past 6 months. Keep tickers where ADV >= 10 * RequiredShares to provide a safety margin. |

#### 3. Rank candidates by historical volatility and filter to match the specified maximum_drawdown and risk_tolerance_level.

| Category | Details |
| --- | --- |
| **Reason** | Statistical arbitrage relies on mean‑reverting relationships; overly volatile pairs can increase drawdown risk. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Calculate the 30‑day rolling standard deviation for each ticker. Compute an adjusted volatility score = StdDev / sqrt(annualization_factor). Keep tickers with adjusted volatility below a threshold derived from maximum_drawdown: Threshold = max_drawdown * 1.5. This ensures that the expected drawdown stays within specification. |

#### 4. Enforce a universe size cap based on the strategy horizon to avoid over‑diversification and maintain manageable backtest granularity.

| Category | Details |
| --- | --- |
| **Reason** | An overly large universe increases data latency, computational cost, and can dilute the statistical signal. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Calculate MaxPositions = strategy_horizon_months * trade_frequency_per_day. If the filtered list exceeds MaxPositions, truncate to the top‑ranked (lowest volatility, highest liquidity) tickers up to MaxPositions. |

#### 5. Query a reliable financial data provider (Yahoo Finance, Bloomberg, or Refinitiv) to resolve ticker symbols and asset class metadata for each shortlisted candidate.

| Category | Details |
| --- | --- |
| **Reason** | Accurate identifiers and metadata are required for downstream data collection and signal generation. |
| **Impact** | HIGH |
| **Complexity** | HIGH |
| **Method** | Implement a batched API request pipeline with retry logic. For each ticker, extract: symbol, market, primary asset class, and any relevant sector tags. Store results in a temporary data frame and validate against the filter criteria (e.g., no missing fields). |

#### 6. Aggregate final outputs: assemble the selected_assets list, asset_classes set, compose a concise selection_criteria string, and compute number_of_assets.

| Category | Details |
| --- | --- |
| **Reason** | The downstream node **collect_historical_data** expects a clean, validated list of symbols. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Convert the validated DataFrame to a list of symbols for selected_assets; deduplicate asset_classes; format selection_criteria as: "Selected {len} {asset_classes} based on liquidity ≥ 10× required shares, volatility ≤ {max_drawdown*1.5}, and risk tolerance ≤ {risk_tolerance_level}."; set number_of_assets to len(selected_assets). |
