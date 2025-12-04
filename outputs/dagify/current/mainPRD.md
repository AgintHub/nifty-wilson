# meta_google_nvidia_trading_strategy - Complete PRD Documentation

## Overview
PRDs for nodes in the 'meta_google_nvidia_trading_strategy' module.

## Table of Contents

- [backtest_strategy](#backtest_strategy)

- [calculate_performance_metrics](#calculate_performance_metrics)

- [compute_daily_returns](#compute_daily_returns)

- [compute_statistics](#compute_statistics)

- [design_trading_strategy](#design_trading_strategy)

- [fetch_google_stock_data](#fetch_google_stock_data)

- [fetch_meta_stock_data](#fetch_meta_stock_data)

- [fetch_nvidia_stock_data](#fetch_nvidia_stock_data)

- [generate_features](#generate_features)

- [generate_strategy_report](#generate_strategy_report)

- [merge_stock_datasets](#merge_stock_datasets)

- [merge_stock_datasets_nvidia](#merge_stock_datasets_nvidia)

- [perform_pairwise_correlation](#perform_pairwise_correlation)

- [preprocess_data](#preprocess_data)



---

## backtest_strategy

### Description
Runs a backtest of the trading strategy defined in the Design Trading Strategy node over the dataset produced by Compute Daily Returns. The backtest simulates daily trading decisions, records every executed trade, and outputs the trade log as lists of dates, actions, shares, prices, and capital after each trade.

### Implementation Plan

#### 1. Load the CSV produced by Compute Daily Returns and parse it into a Pandas DataFrame, ensuring the 'Date' column is parsed as a datetime object and sorted chronologically.

| Category | Details |
| --- | --- |
| **Reason** | The backtest must process data in date order; parsing dates correctly guarantees accurate rolling calculations. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use pd.read_csv(csv_file_path, parse_dates=['Date']) followed by df.sort_values('Date').reset_index(drop=True). |

#### 2. Read the JSON output from Design Trading Strategy into a dictionary and extract the four rule strings: StrategyName, EntryRule, ExitRule, PositionSizeRule.

| Category | Details |
| --- | --- |
| **Reason** | The strategy logic is provided as human‑readable text; we need to capture it for subsequent parsing. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Deserialize the JSON using json.loads and assign each key to a variable. |

#### 3. Implement a lightweight rule‑parser that transforms the EntryRule and ExitRule strings into executable Python lambda functions. The parser should handle simple boolean expressions such as 'META_Close > GOOGL_Close', 'rolling_corr < 0.5', and moving average crossovers.

| Category | Details |
| --- | --- |
| **Reason** | Directly evaluating the raw text is error‑prone; a parser ensures deterministic and safe rule evaluation. |
| **Impact** | HIGH |
| **Complexity** | HIGH |
| **Method** | Use regular expressions to extract operands and operators, construct a dictionary of allowed variables, and compile a lambda via eval in a restricted namespace. Example: lambda df, row: row['META_Close'] > row['GOOGL_Close']. |

#### 4. Parse the PositionSizeRule string to determine the fraction of available capital to allocate per trade (e.g., 'Allocate 10% of capital'). Extract the numeric percentage using regex and convert it to a decimal.

| Category | Details |
| --- | --- |
| **Reason** | Accurate position sizing is critical for realistic backtesting outcomes. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Regex search for patterns like r'(?P<percent>\d+)%', then set position_fraction = int(percent)/100.0. |

#### 5. Enrich the DataFrame with any rolling indicators referenced in the rules but not present in the CSV (e.g., 20‑day rolling correlation, 10‑day moving averages). Compute these using pandas’ rolling methods and merge the results into the DataFrame.

| Category | Details |
| --- | --- |
| **Reason** | The strategy may rely on these indicators; missing values would cause rule evaluation failures. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | For a 20‑day rolling correlation: df['rolling_corr'] = df['META_Close'].rolling(20).corr(df['GOOGL_Close']); for a 10‑day SMA: df['META_SMA_10'] = df['META_Close'].rolling(10).mean(). |

#### 6. Initialize the backtest state: starting capital = 100,000, no open position, and empty lists for trade_dates, trade_actions, trade_shares, trade_prices, trade_capital_after.

| Category | Details |
| --- | --- |
| **Reason** | State variables are required to track capital, holdings, and trade history across the simulation loop. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Set capital = 100000.0; position_shares = 0; trade_dates = []; trade_actions = []; trade_shares = []; trade_prices = []; trade_capital_after = []. |

#### 7. Iterate over the DataFrame row by row. At each date, first evaluate the EntryRule if no position is currently held. If the rule evaluates to True, compute the number of shares to purchase using the position fraction and the current closing price of the target asset.

| Category | Details |
| --- | --- |
| **Reason** | Entry decisions are contingent on the current market state and capital allocation. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use the compiled lambda: if entry_rule(df, row): shares_to_buy = floor((capital * position_fraction) / row['META_Close']); update capital and position_shares; record trade. |

#### 8. After processing an entry, evaluate the ExitRule on each subsequent date if a position is open. If the rule evaluates to True, sell all shares at the current closing price, update capital, close the position, and record the exit trade.

| Category | Details |
| --- | --- |
| **Reason** | Exit logic closes trades and locks in profits or losses. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | If exit_rule(df, row): proceeds = position_shares * row['META_Close']; capital += proceeds; record trade with action 'Sell'; set position_shares = 0. |

#### 9. After each trade (Buy or Sell), append the execution date (ISO string), action, shares, price, and updated capital to their respective output lists. Ensure that the lists maintain the chronological order of trades.

| Category | Details |
| --- | --- |
| **Reason** | Ordered logs are required by the output schema and for downstream performance calculation. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Append to lists using list.append() after each trade event. |

#### 10. At the end of the loop, return the five lists (trade_dates, trade_actions, trade_shares, trade_prices, trade_capital_after) as the node’s output.

| Category | Details |
| --- | --- |
| **Reason** | These are the primitive type lists expected by downstream nodes. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Return a dictionary mapping each key to its list, e.g., {'trade_dates': trade_dates, ...}. |

#### 11. Optionally generate a CSV file of the trade log for debugging or archival purposes. The CSV should have columns: Date, Action, Shares, Price, CapitalAfterTrade.

| Category | Details |
| --- | --- |
| **Reason** | Provides a human‑readable record of the backtest which can aid in verification and reporting. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Create a Pandas DataFrame from the output lists and use df.to_csv('backtest_trades.csv', index=False). |


---

## calculate_performance_metrics

### Description
Evaluates backtest results.

### Implementation Plan

#### 1. Validate the integrity of the trade log by ensuring that all five input arrays – trade_dates, trade_actions, trade_shares, trade_prices, trade_capital_after – have identical lengths and contain non‑empty entries.

| Category | Details |
| --- | --- |
| **Reason** | Consistent array lengths are critical for positional alignment during downstream calculations; mismatches would lead to index errors or mis‑aligned data. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Iterate over the length of any array and compare lengths; raise informative exception if discrepancy is detected. |

#### 2. Parse ISO date strings into Python datetime objects and sort the trades chronologically to guarantee temporal consistency.

| Category | Details |
| --- | --- |
| **Reason** | Chronological ordering is necessary for correct computation of drawdowns, trade durations, and for aligning capital values with dates. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use datetime.strptime for each string, store tuples (date, index), then sort by date; re‑index arrays accordingly. |

#### 3. Construct a daily portfolio value series for the entire backtest window by interpolating capital after each trade to every trading day.

| Category | Details |
| --- | --- |
| **Reason** | Many performance metrics (e.g., drawdown, Sharpe) require a continuous daily equity curve rather than sparse trade points. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Create a list of all dates from the earliest to the latest trade date; for each date, assign the capital value of the most recent trade before or on that date; forward‑fill missing dates. |

#### 4. Compute cumulative return as (final equity / initial equity) - 1.

| Category | Details |
| --- | --- |
| **Reason** | This metric directly measures overall profitability relative to the starting capital. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | final_equity = last value in the daily equity series; initial_equity = trade_capital_after[0]; cumulative_return = (final_equity / initial_equity) - 1. |

#### 5. Calculate daily log‑returns of the equity curve and derive mean and standard deviation for the Sharpe ratio calculation.

| Category | Details |
| --- | --- |
| **Reason** | Log‑returns provide a time‑additive, normally distributed basis for Sharpe computation, which is the industry standard. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Use np.diff(np.log(equity_series)) to get log‑returns; compute mean and std dev with numpy; handle any NaNs by dropping. |

#### 6. Annualize the Sharpe ratio using the square‑root of the ratio between the number of trading days in a year (252) and the backtest trading days.

| Category | Details |
| --- | --- |
| **Reason** | Annualization allows comparison across strategies with different backtest horizons. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | sharpe_daily = mean_return / std_return; annual_factor = sqrt(252 / num_trading_days); annualized_sharpe_ratio = sharpe_daily * annual_factor. |

#### 7. Determine maximum drawdown by scanning the equity curve for the deepest decline from a historical peak to a subsequent trough.

| Category | Details |
| --- | --- |
| **Reason** | Drawdown is a critical risk metric indicating potential capital erosion. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Maintain running maximum of equity; compute drawdown = (peak - equity) / peak; keep the maximum of these values. |

#### 8. Identify winning trades by comparing consecutive entries in trade_capital_after; a trade is considered winning if the capital after the trade exceeds the capital before it.

| Category | Details |
| --- | --- |
| **Reason** | Win rate quantifies the strategy’s profitability at the trade level. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Iterate through indices i=1..n, count wins where trade_capital_after[i] > trade_capital_after[i-1]; win_rate = wins / (n-1). |

#### 9. Calculate average trade duration by matching each 'Buy' action with its corresponding 'Exit' action and computing the date difference.

| Category | Details |
| --- | --- |
| **Reason** | Duration reflects strategy’s holding period characteristics, which influence capital allocation and risk. |
| **Impact** | MEDIUM |
| **Complexity** | HIGH |
| **Method** | Maintain a stack of open trade dates; on 'Buy', push date; on 'Exit', pop date, compute duration in days, store; after processing all trades, average durations of completed trades. |

#### 10. Round all floating‑point outputs to eight decimal places to maintain consistency and avoid floating‑point noise in downstream reporting.

| Category | Details |
| --- | --- |
| **Reason** | Consistent formatting ensures deterministic JSON outputs, simplifying unit tests and downstream parsing. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use round(value, 8) or format with f"{value:.8f}". |

#### 11. Return the metrics in a JSON dictionary matching the specified output structure.

| Category | Details |
| --- | --- |
| **Reason** | The downstream generate_strategy_report node expects this exact JSON schema. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Construct a dict with keys: cumulative_return, annualized_sharpe_ratio, maximum_drawdown, win_rate, average_trade_duration, then serialize with json.dumps. |


---

## compute_daily_returns

### Description
Calculates daily log returns for Meta, Google, and Nvidia and adds the columns to the dataset.

### Implementation Plan

#### 1. Load the cleaned dataset from the `preprocess_data` node's `cleaned_csv` output into a Pandas DataFrame, ensuring that the Date column is parsed as datetime.

| Category | Details |
| --- | --- |
| **Reason** | Pandas offers robust CSV parsing and datetime handling, which is essential for accurate return calculations. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use `pd.read_csv(cleaned_csv, parse_dates=['Date'])`. |

#### 2. Verify that the required Close price columns (META_Close, GOOGL_Close, NVDA_Close) exist and contain numeric values; if missing, raise a clear error indicating which column is absent.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that the dataset has all necessary inputs before proceeding, preventing downstream failures. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Check DataFrame columns with `df.columns` and validate dtype with `pd.api.types.is_numeric_dtype`. |

#### 3. Compute the daily log return for each stock using the formula `return = np.log(Close_today / Close_yesterday)`, aligning with financial convention for continuously compounded returns.

| Category | Details |
| --- | --- |
| **Reason** | Log returns provide additive properties and are standard in backtesting and statistical analysis. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use vectorized operations: `df['META_Return'] = np.log(df['META_Close'] / df['META_Close'].shift(1))`, similarly for GOOGL and NVDA. |

#### 4. Handle the first row where the shift operation produces NaN by filling it with 0 or dropping the row; document the chosen approach.

| Category | Details |
| --- | --- |
| **Reason** | The first day lacks a prior price; deciding how to treat this missing value affects downstream metrics. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use `df.dropna(subset=['META_Return', 'GOOGL_Return', 'NVDA_Return'], inplace=True)` or `df.fillna(0, inplace=True)` based on design choice. |

#### 5. Add the three new return columns to the DataFrame and verify their data types are float64.

| Category | Details |
| --- | --- |
| **Reason** | Ensures consistency of output types for downstream nodes. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Confirm with `df.dtypes` and convert if necessary using `df.astype({'META_Return': 'float64', ...})`. |

#### 6. Write the augmented DataFrame to a new CSV file in a designated temporary or output directory, preserving the original column order with the new columns appended at the end.

| Category | Details |
| --- | --- |
| **Reason** | Providing a stable file path enables other nodes to reference the dataset reliably. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use `df.to_csv(output_path, index=False)`. |

#### 7. Return the path of the newly created CSV as `csv_file_path` and the number of rows in the DataFrame as `row_count`.

| Category | Details |
| --- | --- |
| **Reason** | Matches the defined output structure, allowing downstream nodes to access the results. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Return a dictionary: `{'csv_file_path': output_path, 'row_count': len(df)}`. |


---

## compute_statistics

### Description
Generates summary statistics of the daily log returns for Meta, Google, and Nvidia, including mean, standard deviation, pairwise correlations, and skewness.

### Implementation Plan

#### 1. Read the CSV file produced by the compute_daily_returns node into a Pandas DataFrame, ensuring that the META_Return, GOOGL_Return, and NVDA_Return columns are parsed as float.

| Category | Details |
| --- | --- |
| **Reason** | The downstream statistics calculation requires numeric types; reading via Pandas provides robust handling of CSV parsing and missing values. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use `pd.read_csv(csv_file_path)` with `dtype={'META_Return': float, 'GOOGL_Return': float, 'NVDA_Return': float}` and `parse_dates` if needed. |

#### 2. Drop any rows where any of the return columns contain NaN to avoid distortion of mean, std, skewness, and correlation calculations.

| Category | Details |
| --- | --- |
| **Reason** | Statistical functions in Pandas ignore NaNs by default but pairwise correlation requires aligned rows; explicit drop ensures consistent dataset. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Apply `df.dropna(subset=['META_Return','GOOGL_Return','NVDA_Return'])`. |

#### 3. Compute the mean of each return series using `Series.mean()` and round the result to 8 decimal places for consistency.

| Category | Details |
| --- | --- |
| **Reason** | Mean is a simple aggregate; rounding reduces floating point noise in the JSON output. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Store in variables `meta_mean = df['META_Return'].mean().round(8)` etc. |

#### 4. Compute the standard deviation of each return series using `Series.std(ddof=1)` to reflect sample std, and round to 8 decimal places.

| Category | Details |
| --- | --- |
| **Reason** | Using sample standard deviation aligns with typical financial analysis; rounding maintains readability. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use `df['META_Return'].std(ddof=1).round(8)`. |

#### 5. Compute the skewness of each return series using `Series.skew()` from SciPy or Pandas, rounding to 8 decimal places.

| Category | Details |
| --- | --- |
| **Reason** | Skewness provides insight into return distribution asymmetry; rounding keeps output concise. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | If Pandas does not provide skewness, use `from scipy.stats import skew; skew(df['META_Return']).round(8)`. |

#### 6. Compute Pearson correlations for each unique pair of return series using `DataFrame.corr(method='pearson')`, selecting the corresponding matrix entries and rounding to 8 decimal places.

| Category | Details |
| --- | --- |
| **Reason** | Pearson correlation captures linear dependence; rounding ensures JSON numerical precision. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Create `corr_matrix = df[['META_Return','GOOGL_Return','NVDA_Return']].corr()` then extract `corr_meta_googl = corr_matrix.loc['META_Return','GOOGL_Return'].round(8)` and similarly for other pairs. |

#### 7. Assemble all computed metrics into a dictionary matching the defined output fields.

| Category | Details |
| --- | --- |
| **Reason** | The node contract requires a JSON object with specific keys; assembling in a dict guarantees correct key order and type. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use `output_dict = {'meta_return_mean': meta_mean, 'meta_return_std': meta_std, ...}`. |

#### 8. Serialize the dictionary to JSON and return it as the node's output, ensuring that numerical values are cast to float types (not numpy floats).

| Category | Details |
| --- | --- |
| **Reason** | JSON expects standard Python types; converting avoids serialization errors. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use `json.dumps(output_dict)` after converting values with `float()` if necessary. |


---

## design_trading_strategy

### Description
Formulates the trading strategy logic.

### Implementation Plan

#### 1. 1️⃣ Load parent outputs: parse `compute_statistics` JSON, `generate_features` CSV, and `perform_pairwise_correlation` CSV into in‑memory data structures (e.g., Python dictionaries and Pandas DataFrames).

| Category | Details |
| --- | --- |
| **Reason** | All strategy logic depends on the statistical summaries, moving averages, and rolling correlation values. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use `json.load` for statistics; `pandas.read_csv` for CSVs; ensure date columns are parsed as datetime objects. |

#### 2. 2️⃣ Compute the spread series as the difference between META_Close and GOOGL_Close, aligning on dates and dropping any NaNs resulting from feature lagging.

| Category | Details |
| --- | --- |
| **Reason** | Statistical arbitrage often relies on mean‑reverting spreads; the spread informs entry/exit thresholds. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Add a new column `Spread = META_Close - GOOGL_Close` in the merged DataFrame. |

#### 3. 3️⃣ Calculate the 10‑day SMA of the spread (`Spread_SMA_10`) and its 5‑day standard deviation (`Spread_Std_5`) to establish a dynamic mean‑reversion band.

| Category | Details |
| --- | --- |
| **Reason** | Using spread‑based moving averages allows the strategy to adapt to changing volatility. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Apply `df['Spread_SMA_10'] = df['Spread'].rolling(window=10).mean()` and `df['Spread_Std_5'] = df['Spread'].rolling(window=5).std()`. |

#### 4. 4️⃣ Define entry conditions: go long Meta and short Google when the spread falls below `Spread_SMA_10 - 2 * Spread_Std_5` **and** the 20‑day rolling correlation `META_GOOGL_RollingCorr_20` is above 0.7.

| Category | Details |
| --- | --- |
| **Reason** | A deep negative deviation indicates a potential over‑short Google relative to Meta; a high correlation ensures the pair moves together. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use boolean masks: `(df['Spread'] < df['Spread_SMA_10'] - 2*df['Spread_Std_5']) & (df['META_GOOGL_RollingCorr_20'] > 0.7)`. |

#### 5. 5️⃣ Define exit conditions: close positions when the spread crosses the `Spread_SMA_10` line (i.e., becomes greater than `Spread_SMA_10`) or when the correlation drops below 0.5, whichever occurs first.

| Category | Details |
| --- | --- |
| **Reason** | Crossing the moving average signals a return to normal levels; a falling correlation suggests the pair may diverge. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Create an exit mask: `(df['Spread'] > df['Spread_SMA_10']) | (df['META_GOOGL_RollingCorr_20'] < 0.5)`. |

#### 6. 6️⃣ Specify a conservative position‑sizing rule: allocate 10% of available capital per trade, divided equally between Meta and Google (long/short), ensuring the notional values match to maintain a market‑neutral hedge.

| Category | Details |
| --- | --- |
| **Reason** | Risk‑controlled sizing limits exposure while preserving the arbitrage trade’s hedge. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Define `PositionSizeRule = '10% of capital per trade, split equally between long Meta and short Google; ensure dollar neutrality.'` |

#### 7. 7️⃣ Construct the final JSON object with four fields (`StrategyName`, `EntryRule`, `ExitRule`, `PositionSizeRule`) using descriptive yet concise language suitable for downstream backtesting.

| Category | Details |
| --- | --- |
| **Reason** | The backtest node expects a JSON with these exact keys; clarity reduces downstream errors. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use `json.dumps` with sorted keys: `{"StrategyName":..., "EntryRule":..., "ExitRule":..., "PositionSizeRule":...}`. |

#### 8. 8️⃣ Validate the JSON against the expected schema: confirm string types, non‑empty descriptions, and that no mandatory fields are omitted.

| Category | Details |
| --- | --- |
| **Reason** | Ensures downstream nodes receive correctly typed data and prevents runtime failures. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Perform a schema check: assert `isinstance(value, str)` for each field and that length > 0. |

#### 9. 9️⃣ Log the generated strategy parameters and a brief summary (e.g., number of expected trades per month) to a debug log for traceability.

| Category | Details |
| --- | --- |
| **Reason** | Facilitates debugging if backtest results are unexpected; provides context for performance metrics. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Print or write to a file: `logging.info(f'Strategy {strategy_name} with {num_trades} expected trades/month')`. |


---

## fetch_google_stock_data

### Description
Collects Google (GOOGL) stock price data for the most recent 90 calendar days, ensuring the data is cleaned, sorted, and converted into the specified list outputs.

### Implementation Plan

#### 1. Determine the exact 90‑day date range: compute the date 90 calendar days before the current date and use that as the start date, ensuring the end date is the most recent trading day.

| Category | Details |
| --- | --- |
| **Reason** | Accurate date range guarantees consistent data volume across executions. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use Python datetime to calculate start and end dates, adjust for weekends/holidays by querying the trading calendar or simply allow the API to filter non‑trading days. |

#### 2. Select a reliable public data provider that offers GOOGL OHLCV data, e.g., Yahoo Finance via the yfinance library or Alpha Vantage’s free API, prioritizing providers with robust error handling and rate‑limit compliance.

| Category | Details |
| --- | --- |
| **Reason** | Provider reliability reduces downtime and ensures data integrity. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Write a small wrapper function that attempts the first provider and falls back to the second if a network or API error occurs. |

#### 3. Fetch raw data using the chosen provider’s API: request daily adjusted close, high, low, open, and volume data for the ticker GOOGL covering the determined date range.

| Category | Details |
| --- | --- |
| **Reason** | Direct API access is the most efficient way to obtain up‑to‑date OHLCV data. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use yfinance's `Ticker.history(period='90d', interval='1d', auto_adjust=False)` or Alpha Vantage’s `TIME_SERIES_DAILY_ADJUSTED` endpoint; capture JSON/CSV response. |

#### 4. Parse the downloaded data into a Pandas DataFrame, ensuring column names match the required output (Date, Open, High, Low, Close, Volume).

| Category | Details |
| --- | --- |
| **Reason** | Pandas provides robust parsing and type inference for CSV/JSON data. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Load with `pd.read_csv` for CSV or `pd.DataFrame.from_dict` for JSON; rename columns if necessary. |

#### 5. Convert the Date column to ISO 8601 string format (YYYY‑MM‑DD) and sort the DataFrame ascending by date.

| Category | Details |
| --- | --- |
| **Reason** | ISO format standardizes dates for downstream consumption and sorting ensures chronological order. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use `pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')` and `df.sort_values('Date', inplace=True)`. |

#### 6. Validate numeric columns (Open, High, Low, Close, Volume) for data type consistency, converting to float for prices and int for volume, and fill any missing values using forward‑fill to preserve market continuity.

| Category | Details |
| --- | --- |
| **Reason** | Consistent numeric types are required for downstream calculations and the PRD’s output schema. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Apply `df[col] = pd.to_numeric(df[col], errors='coerce')` then `df[col].fillna(method='ffill', inplace=True)`. |

#### 7. Extract each column into a Python list in the order of the sorted DataFrame and cast to the appropriate list type (list of str, list of float, list of int).

| Category | Details |
| --- | --- |
| **Reason** | The output structure requires pure Python lists rather than Pandas objects. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use `df['Date'].tolist()`, `df['Open'].tolist()`, etc., and cast volume list to int if not already. |

#### 8. Perform a sanity check: ensure the lengths of all output lists match and equal the number of trading days retrieved; if mismatched, raise a descriptive error.

| Category | Details |
| --- | --- |
| **Reason** | Prevents downstream nodes from receiving inconsistent data. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Assert `len(dates) == len(open_prices) == ...` and raise ValueError with context if false. |

#### 9. Package the six lists into the node’s output dictionary as per the defined output structure and return it as the node’s result.

| Category | Details |
| --- | --- |
| **Reason** | Fulfills the node contract and allows parent nodes to consume the data seamlessly. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Return `{'dates': dates, 'open_prices': open_prices, 'high_prices': high_prices, 'low_prices': low_prices, 'close_prices': close_prices, 'volumes': volumes}`. |


---

## fetch_meta_stock_data

### Description
Collects Meta stock price data for the last 90 days.

### Implementation Plan

#### 1. Choose a stable public API (e.g., Yahoo Finance via yfinance) that provides daily OHLCV for Meta and supports date filtering.

| Category | Details |
| --- | --- |
| **Reason** | Yahoo Finance is free, well documented, and reliably returns historical OHLCV with timezone‑neutral dates. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Import yfinance, instantiate Ticker('META'), and call history(period='90d') to retrieve 90 days of data. |

#### 2. Verify that the returned dataframe contains the required columns (Open, High, Low, Close, Volume) and that the index is a DatetimeIndex.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the data aligns with the expected schema and that subsequent transformations are safe. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use df.columns.contains() checks, and df.index.is_monotonic_increasing to confirm chronological order. |

#### 3. Convert the DatetimeIndex to ISO‑8601 string format (YYYY‑MM‑DD) and reset it as a column named 'Date'.

| Category | Details |
| --- | --- |
| **Reason** | The output requires ISO date strings; resetting the index ensures a clean column for later sorting and list extraction. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | df.reset_index(inplace=True); df['Date'] = df['Date'].dt.strftime('%Y-%m-%d') |

#### 4. Ensure the dataframe is sorted ascending by 'Date', dropping any duplicate dates that may appear due to timezone conversions.

| Category | Details |
| --- | --- |
| **Reason** | The node's contract mandates ascending order; duplicates would corrupt downstream merges. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | df.sort_values('Date', inplace=True); df.drop_duplicates(subset='Date', keep='first', inplace=True) |

#### 5. Extract each column into a Python list matching the output types: dates → list of strings, opens/highs/lows/closes → list of floats, volumes → list of ints.

| Category | Details |
| --- | --- |
| **Reason** | Transforms pandas Series into primitive list types required by the DAG's data contract. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use df['Column'].tolist() for each, converting volumes to int via .astype(int).tolist() |

#### 6. Perform a sanity check on the volume data to confirm no NaNs or negative values, raising an error if found.

| Category | Details |
| --- | --- |
| **Reason** | Negative or missing volumes invalidate subsequent calculations and could silently corrupt the dataset. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Check df['Volume'].isna().any() or (df['Volume'] < 0).any(); raise ValueError if true. |

#### 7. Return the six lists in the order specified by the output structure, ensuring the lengths match and the date list is the longest if any missing OHLCV entries are forward‑filled.

| Category | Details |
| --- | --- |
| **Reason** | Guarantees consistency across the node's outputs and prevents misalignment in downstream nodes. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Package lists into a dictionary: {'dates': dates_list, 'opens': opens_list, ...} and return via the node's interface. |


---

## fetch_nvidia_stock_data

### Description
Collects Nvidia stock price data for the last 90 days.

### Implementation Plan

#### 1. Import the required third‑party libraries: `pandas` for data manipulation and `yfinance` as the primary data source.

| Category | Details |
| --- | --- |
| **Reason** | These libraries provide a robust, well‑tested interface to Yahoo Finance and efficient DataFrame operations. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | pip install yfinance pandas; import yfinance as yf; import pandas as pd |

#### 2. Determine the UTC timestamp for the current day and compute the start date exactly 90 days prior using `datetime`.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that the date range is always accurate regardless of the script run time. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | from datetime import datetime, timedelta; end_date = datetime.utcnow().date(); start_date = end_date - timedelta(days=90) |

#### 3. Fetch the daily OHLCV data via `yf.download(ticker='NVDA', start=start_date, end=end_date, interval='1d', progress=False, actions=False)`.

| Category | Details |
| --- | --- |
| **Reason** | Yahoo Finance provides a free, stable API endpoint for historical data, and `yfinance` handles authentication and rate‑limiting internally. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | data = yf.download('NVDA', start=start_date, end=end_date, interval='1d', progress=False, actions=False) |

#### 4. Validate the returned DataFrame: check for the presence of the required columns `Open`, `High`, `Low`, `Close`, `Volume`. If any are missing, raise a descriptive exception.

| Category | Details |
| --- | --- |
| **Reason** | Prevents downstream errors due to column mis‑naming or API changes. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | required_cols = {'Open', 'High', 'Low', 'Close', 'Volume'}; missing = required_cols - set(data.columns); if missing: raise ValueError(f'Missing columns: {missing}') |

#### 5. Reset the DataFrame index to expose the `Date` column and convert it to ISO‑8601 string format (`YYYY‑MM‑DD`).

| Category | Details |
| --- | --- |
| **Reason** | Standardizes the date representation for consistency across nodes. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | data.reset_index(inplace=True); data['Date'] = pd.to_datetime(data['Date']).dt.strftime('%Y-%m-%d') |

#### 6. Sort the DataFrame by `Date` in ascending order to satisfy the prompt requirement.

| Category | Details |
| --- | --- |
| **Reason** | Ensures chronological ordering which is critical for time‑series analyses. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | data.sort_values('Date', inplace=True); data.reset_index(drop=True, inplace=True) |

#### 7. Replace any remaining missing numeric values (e.g., due to market holidays) using forward‑fill. If the first rows remain missing, drop those rows.

| Category | Details |
| --- | --- |
| **Reason** | Guarantees that every output list contains valid numeric entries, avoiding downstream NaNs. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | data[['Open', 'High', 'Low', 'Close', 'Volume']] = data[['Open', 'High', 'Low', 'Close', 'Volume']].fillna(method='ffill'); data.dropna(subset=['Open', 'High', 'Low', 'Close', 'Volume'], inplace=True) |

#### 8. Cast the numeric columns to appropriate Python types: floats for prices, int for volume.

| Category | Details |
| --- | --- |
| **Reason** | Matches the specified output types (`List[float]` and `List[int]`). |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | data['Volume'] = data['Volume'].astype(int); price_cols = ['Open', 'High', 'Low', 'Close']; data[price_cols] = data[price_cols].astype(float) |

#### 9. Extract each column into a Python list in the correct order and assign them to the corresponding output fields.

| Category | Details |
| --- | --- |
| **Reason** | Conforms to the defined `output_structure` while keeping the data in memory‑efficient structures. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | dates = data['Date'].tolist(); open_prices = data['Open'].tolist(); high_prices = data['High'].tolist(); low_prices = data['Low'].tolist(); close_prices = data['Close'].tolist(); volumes = data['Volume'].tolist() |

#### 10. Return the six lists as the final node output.

| Category | Details |
| --- | --- |
| **Reason** | The downstream nodes expect this exact structure for further processing. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | return { 'dates': dates, 'open_prices': open_prices, 'high_prices': high_prices, 'low_prices': low_prices, 'close_prices': close_prices, 'volumes': volumes } |

#### 11. Implement robust error handling: wrap the entire fetch‑and‑transform logic in a try/except block, logging network errors, API limits, or data validation failures, and re‑raise a custom `RuntimeError` with context.

| Category | Details |
| --- | --- |
| **Reason** | Provides resilience in production environments and aids debugging. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | try: ... except Exception as e: logger.exception('NVDA data fetch failed'); raise RuntimeError(f'NVDA data fetch error: {e}') |

#### 12. Add optional caching: store the fetched CSV as a local file with a timestamp; on subsequent runs within 24 h, read from cache instead of querying the API, to reduce external calls and improve speed.

| Category | Details |
| --- | --- |
| **Reason** | Optimizes performance for iterative workflows and respects API rate limits. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | cache_path = Path('cache/nvda_90d.csv'); if cache_path.exists() and age < 24h: data = pd.read_csv(cache_path); else: fetch_and_save_to_cache() |


---

## generate_features

### Description
Adds rolling moving averages and volatility features to the cleaned merged stock dataset.

### Implementation Plan

#### 1. Parse the cleaned CSV string into a pandas DataFrame and enforce ISO 8601 date ordering.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that all subsequent rolling calculations operate on chronologically sorted data and that the date format matches downstream expectations. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use `pandas.read_csv` with `parse_dates=['Date']`, `skipinitialspace=True`, then `df.sort_values('Date', inplace=True)`. |

#### 2. Validate that the DataFrame contains the required columns: `META_Close` and `GOOGL_Close`.

| Category | Details |
| --- | --- |
| **Reason** | Prevents downstream KeyErrors and guarantees that the feature calculation has the necessary data. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Check `set(['META_Close', 'GOOGL_Close']).issubset(df.columns)`; if not, raise a descriptive ValueError. |

#### 3. Compute the 10‑day simple moving averages for Meta and Google using `rolling(window=10, min_periods=10).mean()`.

| Category | Details |
| --- | --- |
| **Reason** | Using `min_periods=10` ensures that only full windows contribute to the average, yielding `NaN` for the first nine rows. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Assign new columns: `df['META_MovingAvg_10'] = df['META_Close'].rolling(10, min_periods=10).mean()` and similarly for GOOGL. |

#### 4. Compute the 5‑day rolling standard deviations for Meta and Google using `rolling(window=5, min_periods=5).std()`.

| Category | Details |
| --- | --- |
| **Reason** | Captures short‑term volatility dynamics and aligns with the strategy's volatility thresholds. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Assign new columns: `df['META_Std_5'] = df['META_Close'].rolling(5, min_periods=5).std()` and similarly for GOOGL. |

#### 5. Replace any remaining `NaN` values in the new feature columns with `None` to produce JSON‑compatible nulls.

| Category | Details |
| --- | --- |
| **Reason** | JSON serialization cannot encode `NaN`; representing missing values as `null` keeps semantic meaning intact. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use `df[col].where(df[col].notna(), None).tolist()` for each new feature column. |

#### 6. Extract the date list and feature lists from the DataFrame and return them as separate lists matching the output schema.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that the function signature and downstream consumers receive strictly typed and ordered arrays. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Build the result dictionary: `date_list = df['Date'].dt.strftime('%Y-%m-%d').tolist()`, and assign each feature list from the corresponding column. |


---

## generate_strategy_report

### Description
Creates the final written report of the strategy.

### Implementation Plan

#### 1. Parse the JSON output from the design_trading_strategy node and confirm that the keys StrategyName, EntryRule, ExitRule, and PositionSizeRule are present. If any key is missing, log an error and substitute a placeholder "<undefined>".

| Category | Details |
| --- | --- |
| **Reason** | Ensures the strategy description can be reliably constructed and prevents downstream failures if upstream data is incomplete. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use Python's json.loads to deserialize; employ dict.get with default values and write to a log file if missing. |

#### 2. Parse the JSON output from calculate_performance_metrics and validate the presence of cumulative_return, annualized_sharpe_ratio, maximum_drawdown, win_rate, and average_trade_duration. Normalize numeric values to two decimal places for presentation.

| Category | Details |
| --- | --- |
| **Reason** | Consistent numeric formatting improves readability and aligns with standard reporting conventions. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use json.loads and format numbers with f"{value:.2f}"; round maximum_drawdown and average_trade_duration to four decimal places to show precision. |

#### 3. Construct a Markdown header using the StrategyName field, prefixed with "# ".

| Category | Details |
| --- | --- |
| **Reason** | A clear, top‑level heading immediately informs the reader of the strategy being reported. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | f"# {strategy_name}\n" |

#### 4. Create a section titled "Strategy Description" that concatenates EntryRule, ExitRule, and PositionSizeRule into a single descriptive paragraph, using bullet points for clarity.

| Category | Details |
| --- | --- |
| **Reason** | Presents the trading logic in a concise yet comprehensive manner. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | f"## Strategy Description\n- **Entry Rule:** {entry}\n- **Exit Rule:** {exit}\n- **Position Size Rule:** {size}\n" |

#### 5. Add a section "Key Statistical Insights" that lists the rolling correlation and moving average thresholds used, referencing the compute_statistics outputs for mean and standard deviation where relevant. Use a Markdown table with two columns: Insight and Value.

| Category | Details |
| --- | --- |
| **Reason** | Highlights the quantitative foundations of the strategy, linking back to the statistical analysis. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Build table strings: "| Insight | Value |\n|---|---|\n| Mean Meta Return | {meta_mean:.4f} |\n..."; extract values from compute_statistics JSON. |

#### 6. Add a section "Backtest Performance Metrics" that presents the metrics in a Markdown table, labeling each metric and formatting numbers to two decimal places. Include a brief interpretive note after the table summarizing overall performance.

| Category | Details |
| --- | --- |
| **Reason** | Structured presentation allows quick comparison of metrics, and interpretive comments aid decision‑making. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Compose table with headers; compute win_rate as percentage; append a note: "The strategy achieved a cumulative return of X% with a Sharpe ratio of Y, indicating Z." |

#### 7. Add a section "Recommendations for Next Steps" that suggests at least two actionable items (e.g., expand to include Nvidia, adjust correlation window) based on performance gaps identified in the metrics.

| Category | Details |
| --- | --- |
| **Reason** | Provides clear guidance for future development and iteration. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use conditional logic: if max_drawdown > 0.1, suggest risk‑management improvement; always recommend parameter sensitivity analysis. |

#### 8. Concatenate all Markdown sections into a single string variable, ensuring proper spacing and newline characters to preserve formatting when rendered.

| Category | Details |
| --- | --- |
| **Reason** | A single string output is required by the node's output structure and ensures consistency across different renderers. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Join list of section strings with "\n\n". |

#### 9. Return the final Markdown string as the value of the report_markdown output field, wrapped in a JSON object matching the defined output structure.

| Category | Details |
| --- | --- |
| **Reason** | Compliance with the node's contract ensures downstream nodes receive data in the expected format. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | json.dumps({'report_markdown': final_markdown}) |

#### 10. Implement exception handling around JSON parsing and string formatting to capture and log any errors, returning a minimal placeholder report if processing fails.

| Category | Details |
| --- | --- |
| **Reason** | Robustness guarantees the workflow does not crash on malformed input and provides a graceful degradation path. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | try/except blocks, logging module, fallback string "# Strategy Report\n*Error generating report.*" |


---

## merge_stock_datasets

### Description
Creates a unified dataset containing Meta and Google OHLCV data.

### Implementation Plan

#### 1. Parse the parent node outputs by converting the date and OHLCV lists from Meta and Google into two separate dictionaries keyed by ISO‑format date strings, mapping each date to a sub‑dictionary of its OHLCV values.

| Category | Details |
| --- | --- |
| **Reason** | Using dictionaries allows constant‑time lookup for matching dates and keeps the OHLCV data grouped logically. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Iterate over the lists, zip them together, and store in a Python dict: meta_dict[date] = {'Open': open, 'High': high, 'Low': low, 'Close': close, 'Volume': vol}. |

#### 2. Compute the intersection of date keys between the Meta and Google dictionaries to identify only those dates that appear in both datasets.

| Category | Details |
| --- | --- |
| **Reason** | The requirement explicitly states to keep rows that have dates present in both datasets. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use set operations: common_dates = sorted(set(meta_dict.keys()) & set(google_dict.keys())) to preserve ascending order. |

#### 3. For each date in the sorted list of common dates, create a merged row by extracting the OHLCV values from both dictionaries and prefixing each column name with META_ or GOOGL_. Assemble the row values in the order: Date, META_Open, META_High, META_Low, META_Close, META_Volume, GOOGL_Open, GOOGL_High, GOOGL_Low, GOOGL_Close, GOOGL_Volume.

| Category | Details |
| --- | --- |
| **Reason** | Explicit column ordering ensures consistency across all consumers of the CSV. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Loop over common_dates, build a list of strings, e.g., [date, str(meta_open), …, str(googl_volume)], and append to a row list. |

#### 4. Create the header row by concatenating the prefixed column names exactly once, ensuring no duplicate or missing headers.

| Category | Details |
| --- | --- |
| **Reason** | The output must include a header for downstream processing and human readability. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use a static list: ['Date', 'META_Open', 'META_High', 'META_Low', 'META_Close', 'META_Volume', 'GOOGL_Open', 'GOOGL_High', 'GOOGL_Low', 'GOOGL_Close', 'GOOGL_Volume'] and join with commas. |

#### 5. Convert each merged row (including the header) into a single comma‑separated string, ensuring that numeric values are formatted with at least two decimal places for consistency.

| Category | Details |
| --- | --- |
| **Reason** | Consistent formatting prevents parsing errors in downstream nodes. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use Python f‑strings or format specifiers: f"{value:.2f}" for floats and str(value) for integers. |

#### 6. Return the list of CSV strings as the value of the output field merged_csv.

| Category | Details |
| --- | --- |
| **Reason** | The downstream nodes expect a list of strings to write or further process. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Assign merged_csv = [header_row] + row_strings and return this list. |


---

## merge_stock_datasets_nvidia

### Description
Extends the merged dataset to include Nvidia OHLCV data.

### Implementation Plan

#### 1. Parse the merged_csv output from merge_stock_datasets into a DataFrame using pandas, ensuring the first row is treated as header and subsequent rows as data.

| Category | Details |
| --- | --- |
| **Reason** | Using pandas provides robust CSV parsing and easy column manipulation while handling edge cases like commas in data. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | df_meta_google = pd.read_csv(StringIO(merged_csv_text)) |

#### 2. Construct a DataFrame from the six output lists of fetch_nvidia_stock_data, assigning column names: ['Date', 'NVDA_Open', 'NVDA_High', 'NVDA_Low', 'NVDA_Close', 'NVDA_Volume']. Convert all numeric columns to appropriate dtypes and the Date column to pandas datetime.

| Category | Details |
| --- | --- |
| **Reason** | Consistent data types are essential for accurate merging and sorting. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | df_nvidia = pd.DataFrame({'Date': dates, 'NVDA_Open': open_prices, ...}); df_nvidia['Date'] = pd.to_datetime(df_nvidia['Date']) |

#### 3. Ensure the Date column in both DataFrames is in ISO format (YYYY‑MM‑DD). If merge_stock_datasets used a different format, standardize it using pd.to_datetime and then format.

| Category | Details |
| --- | --- |
| **Reason** | A common date format guarantees a correct join key. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | df_meta_google['Date'] = pd.to_datetime(df_meta_google['Date']).dt.date.astype(str) |

#### 4. Perform an inner merge on the 'Date' column, retaining only rows that exist in both DataFrames. Use the 'how="inner"' parameter to enforce intersection.

| Category | Details |
| --- | --- |
| **Reason** | Inner join guarantees that only dates present in all three original datasets are kept, as required by the prompt. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | merged_df = pd.merge(df_meta_google, df_nvidia, on='Date', how='inner') |

#### 5. Sort the merged DataFrame by the 'Date' column in ascending order to satisfy the output requirement.

| Category | Details |
| --- | --- |
| **Reason** | A sorted output improves downstream processing and readability. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | merged_df.sort_values(by='Date', inplace=True) |

#### 6. Convert the merged DataFrame back to a CSV string, using a comma separator and including the header row. Ensure that the output is a single string suitable for the PrimitiveType.STR field.

| Category | Details |
| --- | --- |
| **Reason** | The downstream node expects a single CSV string, not a list of rows. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | csv_output = merged_df.to_csv(index=False) |

#### 7. Return the csv_output string as the value for the 'csv_data' field, completing the node's contract.

| Category | Details |
| --- | --- |
| **Reason** | Explicitly mapping the final string to the defined output field ensures consistency with the DAG schema. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | return { 'csv_data': csv_output } |


---

## perform_pairwise_correlation

### Description
Generates a rolling correlation feature between Meta and Google daily log returns and appends it to the dataset.

### Implementation Plan

#### 1. Load the dataset from the CSV file path provided by compute_daily_returns into a Pandas DataFrame, ensuring the Date column is parsed as a datetime and the DataFrame is sorted by Date.

| Category | Details |
| --- | --- |
| **Reason** | Pandas efficiently handles CSV I/O and datetime parsing; sorting guarantees correct chronological order for rolling operations. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use pd.read_csv(csv_file_path, parse_dates=['Date']); then df.sort_values('Date', inplace=True). |

#### 2. Validate that the columns META_Return and GOOGL_Return exist and contain numeric values. If missing or non-numeric, raise a clear exception.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the rolling correlation computation has the necessary data and prevents silent failures. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use df[['META_Return', 'GOOGL_Return']].apply(pd.to_numeric, errors='raise') to coerce types; check for any NaNs. |

#### 3. Compute a 20‑day rolling Pearson correlation between META_Return and GOOGL_Return with a minimum of 20 observations to avoid NaNs for incomplete windows.

| Category | Details |
| --- | --- |
| **Reason** | Specifies the exact window size and ensures the correlation is only calculated when a full window is available. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | df['META_GOOGL_RollingCorr_20'] = df['META_Return'].rolling(window=20, min_periods=20).corr(df['GOOGL_Return']). |

#### 4. Leave the first 19 rows of the new column as NaN (the rolling window is incomplete) and do not forward‑fill or impute them; this preserves statistical integrity.

| Category | Details |
| --- | --- |
| **Reason** | Imputing would bias correlation estimates; NaNs correctly signal insufficient data. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | No additional code required; pandas automatically leaves NaNs for incomplete windows. |

#### 5. Convert the enriched DataFrame back to a CSV string with no index column and UTF‑8 encoding, ensuring that the output matches the expected primitive type.

| Category | Details |
| --- | --- |
| **Reason** | The downstream nodes expect a single string containing the CSV data; removing the index keeps the format clean. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | csv_data = df.to_csv(index=False, encoding='utf-8') |

#### 6. Return a dictionary with the key csv_data mapped to the generated CSV string, matching the defined output structure.

| Category | Details |
| --- | --- |
| **Reason** | Aligns with the DAG framework's contract for node outputs. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | return {'csv_data': csv_data} |

#### 7. Include robust error handling: wrap the entire process in a try/except block that logs detailed error messages and propagates exceptions to the DAG system.

| Category | Details |
| --- | --- |
| **Reason** | Facilitates debugging and prevents silent failures that could cascade to downstream nodes. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use Python's logging module; re‑raise exceptions after logging. |


---

## preprocess_data

### Description
Cleans and normalizes the merged dataset by standardizing dates, imputing missing numeric data, and dropping rows lacking both Meta and Google Close prices.

### Implementation Plan

#### 1. Read the input CSV string into a pandas DataFrame using `pd.read_csv(io.StringIO(csv_data))` while ensuring that all columns are parsed as strings to avoid dtype inference issues.

| Category | Details |
| --- | --- |
| **Reason** | Parsing as strings preserves the raw Date format and any missing numeric values represented as empty strings, facilitating consistent downstream processing. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use the pandas `read_csv` function with `dtype=str` and `keep_default_na=False` to capture blanks as NaN. |

#### 2. Convert the `Date` column to ISO 8601 format by parsing with `pd.to_datetime(df['Date'], errors='coerce', dayfirst=False)` and then formatting with `.dt.strftime('%Y-%m-%d')`.

| Category | Details |
| --- | --- |
| **Reason** | Standardizing dates ensures consistent ordering and compatibility with downstream nodes that rely on ISO dates. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Apply `pd.to_datetime` with `errors='coerce'` to safely convert malformed dates to NaT, then `strftime` for ISO formatting; subsequently drop any rows with NaT if present. |

#### 3. Forward‑fill missing numeric values using `df.fillna(method='ffill', inplace=True)` after isolating numeric columns (all columns except `Date`).

| Category | Details |
| --- | --- |
| **Reason** | Forward‑fill propagates the last observed non‑missing value, a common strategy for time‑series financial data where gaps are usually short and missing values are best imputed from prior observations. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Identify numeric columns via `df.select_dtypes(include=['float64', 'int64'])` and apply `ffill`; non‑numeric columns remain untouched. |

#### 4. Drop rows where both `META_Close` and `GOOGL_Close` are NaN with `df.dropna(subset=['META_Close', 'GOOGL_Close'], how='all', inplace=True)`.

| Category | Details |
| --- | --- |
| **Reason** | The strategy requires at least one Close value for Meta or Google; rows missing both are unusable for return calculations and should be excluded to avoid division by zero or invalid logs. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use pandas `dropna` specifying `subset` and `how='all'` to retain rows where at least one Close value exists. |

#### 5. Sort the DataFrame by the ISO `Date` column in ascending order using `df.sort_values('Date', inplace=True)`.

| Category | Details |
| --- | --- |
| **Reason** | Sorted dates are required for accurate rolling calculations and time‑series alignment in downstream nodes. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Call pandas `sort_values` on the standardized Date column. |

#### 6. Convert the cleaned DataFrame back to a CSV string with `df.to_csv(index=False)` ensuring no trailing newline or BOM that could corrupt downstream parsing.

| Category | Details |
| --- | --- |
| **Reason** | Providing a clean CSV string aligns with the expected output format of child nodes. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use pandas `to_csv` with `index=False`; optionally apply `strip()` to remove extraneous whitespace. |

#### 7. Compute `row_count` as the number of rows in the cleaned DataFrame using `int(df.shape[0])`.

| Category | Details |
| --- | --- |
| **Reason** | Reporting the row count allows downstream nodes to verify data completeness and detect unintended reductions. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use the `shape` attribute of the DataFrame. |

#### 8. Wrap the entire transformation in a `try/except` block to catch parsing or conversion errors, log the exception details, and raise a descriptive exception to upstream nodes.

| Category | Details |
| --- | --- |
| **Reason** | Robust error handling ensures that issues such as malformed dates or unexpected NaN propagation do not silently corrupt the dataset. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Implement `try: ... except Exception as e: log.error(...)` and re‑raise a custom `PreprocessDataError`. |
