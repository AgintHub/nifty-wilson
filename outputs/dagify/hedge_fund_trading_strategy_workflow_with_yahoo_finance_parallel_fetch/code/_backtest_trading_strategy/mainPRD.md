# _backtest_trading_strategy - Complete PRD Documentation

## Overview
PRDs for nodes in the '_backtest_trading_strategy' module.

## Table of Contents

- [parse_csv_to_dataframes](#parse_csv_to_dataframes)

- [align_dataframes_to_master_calendar](#align_dataframes_to_master_calendar)

- [create_unified_dataframe](#create_unified_dataframe)

- [create_signal_function](#create_signal_function)

- [generate_trading_signals](#generate_trading_signals)

- [execute_backtest_simulation](#execute_backtest_simulation)

- [build_equity_curve](#build_equity_curve)

- [calculate_performance_metrics](#calculate_performance_metrics)

- [log_backtest_error](#log_backtest_error)



---

## parse_csv_to_dataframes

### Description
Converts CSV strings for each ticker into a JSON‑encoded dictionary of pandas DataFrames with UTC timestamps and uniform column names.

### Implementation Plan

#### 1. Validate that the number of CSV strings matches the number of tickers and that each string is non‑empty.

| Category | Details |
| --- | --- |
| **Reason** | Mismatched or missing data would cause downstream parsing errors and corrupt the backtest. |
| **Impact** | Prevents runtime exceptions and ensures data integrity before heavy processing. |
| **Complexity** | LOW |
| **Method** | Deserialize the `csv_strings` and `tickers` JSON arrays, compare their lengths, and raise a clear ValueError if they differ or contain empty entries. |

#### 2. Parse each CSV string into a pandas DataFrame, enforce a UTC datetime index, and rename columns to a standard OHLCV schema.

| Category | Details |
| --- | --- |
| **Reason** | Downstream pipeline components expect uniform DataFrames with a timezone‑aware index and consistent column names. |
| **Impact** | Provides a clean, predictable data structure for alignment, signal generation, and backtesting stages. |
| **Complexity** | MEDIUM |
| **Method** | Loop over `zip(tickers, csv_strings)`, use `io.StringIO` with `pd.read_csv(parse_dates=['Date'])`, set `df.set_index('Date', inplace=True)`, apply `df.index = df.index.tz_localize('UTC')` (or `tz_convert` if already tz‑aware), and rename columns via a mapping dict (e.g., {'Open':'open','High':'high',...}). |

#### 3. Serialize the resulting ticker‑to‑DataFrame dictionary into a JSON string for the shim output.

| Category | Details |
| --- | --- |
| **Reason** | The shim’s declared output type is STR, so the complex object must be encoded as a string that can be deserialized later. |
| **Impact** | Allows the `backtest_trading_strategy` node to easily reconstruct the DataFrames via `json.loads` and `pd.read_json`. |
| **Complexity** | LOW |
| **Method** | Create a dict `{ticker: df.to_json(date_format='iso', orient='split') for ticker, df in parsed_dict.items()}`, then `json.dumps` the dict; return this string as the `output` field. |


---

## align_dataframes_to_master_calendar

### Description
Aligns multiple ticker DataFrames to a unified master business‑day calendar, ensuring consistent timestamps across all assets.

### Implementation Plan

#### 1. Parse and validate the `dataframes` and `tickers` JSON strings into Python objects.

| Category | Details |
| --- | --- |
| **Reason** | The shim receives raw JSON strings; they must be deserialized and checked for completeness before any alignment logic can run. |
| **Impact** | Prevents runtime errors caused by malformed inputs and ensures only the requested tickers are processed. |
| **Complexity** | LOW |
| **Method** | Use `json.loads` to convert the strings, verify that `dataframes` is a dict and `tickers` is a list, and raise a clear `ValueError` for mismatches. |

#### 2. Create a master business‑day calendar covering the full date range of all ticker DataFrames.

| Category | Details |
| --- | --- |
| **Reason** | A single unified index is required so that downstream back‑testing logic can assume all assets share identical timestamps. |
| **Impact** | All subsequent calculations (signals, portfolio equity, etc.) operate on synchronized data, eliminating alignment bugs. |
| **Complexity** | MEDIUM |
| **Method** | Collect the minimum start date and maximum end date across all parsed DataFrames, then generate a `pd.date_range(start, end, freq='B', tz='UTC')`. Store this as `master_index`. |

#### 3. Reindex each ticker DataFrame to `master_index`, forward‑fill missing values, and serialize back to CSV strings.

| Category | Details |
| --- | --- |
| **Reason** | Reindexing ensures every ticker has rows for every business day; forward‑fill maintains the last known price when data is missing (e.g., holidays). |
| **Impact** | Produces the final aligned dictionary that the back‑test engine consumes, guaranteeing consistent shape and index across assets. |
| **Complexity** | MEDIUM |
| **Method** | Iterate over the tickers list, read each CSV into a `pd.DataFrame` (parse dates, set index), `df.reindex(master_index).ffill().bfill()`, then `df.to_csv(index=True)` and store in the result dict. Finally `json.dumps` the dict for the `output` field. |


---

## create_unified_dataframe

### Description
Combines multiple aligned ticker DataFrames into a single multi‑index pandas DataFrame for unified analysis.

### Implementation Plan

#### 1. Validate that aligned_data is a JSON‑serializable mapping of ticker strings to CSV‑formatted DataFrame strings.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the shim receives correctly structured data before attempting any transformation. |
| **Impact** | Prevents runtime errors and provides clear feedback to upstream nodes if the input is malformed. |
| **Complexity** | MEDIUM |
| **Method** | Parse the aligned_data string into a Python dict using json.loads, then iterate to confirm each value can be read by pandas.read_csv with a datetime index. |

#### 2. Load each ticker's CSV string into a pandas DataFrame and standardize column names and dtype.

| Category | Details |
| --- | --- |
| **Reason** | Uniform DataFrames are required to concatenate them reliably across tickers. |
| **Impact** | Guarantees consistent data schema (e.g., OHLCV columns) and timezone‑aware datetime indexes for downstream calculations. |
| **Complexity** | MEDIUM |
| **Method** | Use pandas.read_csv with StringIO, enforce parse_dates on the index column, set utc=True, and rename columns to a canonical set if needed. |

#### 3. Concatenate all DataFrames into a single multi‑index DataFrame where the first level is the ticker symbol.

| Category | Details |
| --- | --- |
| **Reason** | A unified structure simplifies signal generation, backtesting, and analytics across the entire asset universe. |
| **Impact** | Provides a single source of truth for price and indicator data, enabling vectorized operations and reducing memory overhead. |
| **Complexity** | MEDIUM |
| **Method** | Add a new column 'ticker' to each DataFrame, set the index to ['ticker', original_datetime_index] using pandas.concat with keys=tickers, and sort the index for chronological order. |


---

## create_signal_function

### Description
Creates a callable trading signal function from textual logic steps and a list of required indicators.

### Implementation Plan

#### 1. Parse the `signal_logic_steps` string into a safe executable Python function.

| Category | Details |
| --- | --- |
| **Reason** | The textual description must be transformed into executable code that can be applied to market data. |
| **Impact** | Enables dynamic generation of signal logic without manual coding, allowing end‑users to define strategies in plain language. |
| **Complexity** | MEDIUM |
| **Method** | Use the `ast` module to parse and validate the expression, then compile it with `compile()` and wrap it in a closure that receives indicator values. |

#### 2. Validate that all `used_indicators` are present in the data passed to the generated function.

| Category | Details |
| --- | --- |
| **Reason** | Ensuring required indicators exist prevents runtime KeyError exceptions during backtesting. |
| **Impact** | Improves robustness of the backtest pipeline and provides clear error messages to the user. |
| **Complexity** | LOW |
| **Method** | Compare the set of indicator names extracted from the parsed logic with the `used_indicators` list; raise a descriptive `ValueError` if any are missing. |

#### 3. Wrap the compiled logic into a callable that accepts a dictionary (or DataFrame row) of indicator values and returns a standard signal label (e.g., "BUY", "SELL", "NEUTRAL").

| Category | Details |
| --- | --- |
| **Reason** | Downstream nodes expect a uniform interface to generate trading signals across multiple assets. |
| **Impact** | Provides a consistent API for signal generation, simplifying integration with `generate_trading_signals` and the backtest engine. |
| **Complexity** | HIGH |
| **Method** | Create a function string like `def signal_fn(indicators): <compiled_body>`; execute it in a dedicated namespace using `exec`, capture the resulting `signal_fn`, and serialize its reference as a string (e.g., via `cloudpickle` or `inspect.getsource`). |


---

## generate_trading_signals

### Description
Generates a DataFrame of trading signals by applying a user‑provided signal function to unified market data for the given tickers.

### Implementation Plan

#### 1. Validate and deserialize inputs (unified_data, signal_function, tickers) ensuring they are correctly formatted and safe to execute.

| Category | Details |
| --- | --- |
| **Reason** | Pre‑emptively catches malformed data or unsafe code, avoiding runtime crashes during backtesting. |
| **Impact** | Provides early failure detection, improves robustness, and secures execution environment. |
| **Complexity** | MEDIUM |
| **Method** | Use `json.loads` or `ast.literal_eval` to parse `unified_data` and `tickers`; load `signal_function` via `importlib` or `exec` within a restricted namespace, and verify the resulting callable's signature. |

#### 2. Apply the deserialized `signal_function` across the unified DataFrame to compute BUY/SELL/HOLD signals for each ticker.

| Category | Details |
| --- | --- |
| **Reason** | This is the core logic that translates market data into actionable trading decisions. |
| **Impact** | Generates the `signals_df` required by downstream backtest simulation, directly influencing strategy performance metrics. |
| **Complexity** | HIGH |
| **Method** | Iterate over rows with `DataFrame.apply` (axis=1) passing each row to the signal function, or vectorize the function if possible; ensure missing values are handled and output is aligned with the original ticker columns. |

#### 3. Serialize the resulting signals DataFrame back to a string format suitable for downstream nodes.

| Category | Details |
| --- | --- |
| **Reason** | Downstream workflow components accept string representations, not raw pandas objects. |
| **Impact** | Enables seamless data passing between nodes without requiring in‑memory objects. |
| **Complexity** | LOW |
| **Method** | Convert the DataFrame to JSON (`df.to_json(orient='records')`) or CSV (`df.to_csv(index=False)`), and assign it to the `output` field. |


---

## execute_backtest_simulation

### Description
Simulates execution of a trading strategy by applying commission and slippage to price data and signals, returning a result dictionary as a string.

### Implementation Plan

#### 1. Parse and validate the incoming price_data and signals strings into structured pandas DataFrames.

| Category | Details |
| --- | --- |
| **Reason** | Downstream calculations require numeric time‑series data; malformed input would cause runtime failures. |
| **Impact** | Ensures reliable data handling and prevents crashes during the backtest simulation. |
| **Complexity** | MEDIUM |
| **Method** | Use `json.loads` or `pd.read_csv` on the string inputs, verify required columns (e.g., Open, High, Low, Close, Volume), set a UTC index, and raise a clear exception for missing fields. |

#### 2. Apply commission and slippage adjustments to each simulated trade based on the provided rates.

| Category | Details |
| --- | --- |
| **Reason** | Real‑world trading incurs transaction costs that materially affect performance metrics. |
| **Impact** | Generates realistic cash flow, holdings, and trade‑count outputs that downstream metrics can rely on. |
| **Complexity** | MEDIUM |
| **Method** | Iterate through the signals DataFrame chronologically; when a BUY/SELL signal occurs, compute trade value, subtract `commission_rate * trade_value` and `slippage_rate * price`, update cash and position holdings, and tally trades in a result dictionary. |

#### 3. Serialize the execution results into a JSON‑encoded string for the `output` field.

| Category | Details |
| --- | --- |
| **Reason** | The surrounding workflow expects the shim's output to be a string representing a dictionary. |
| **Impact** | Provides a consistent, language‑agnostic payload that can be parsed by any downstream node. |
| **Complexity** | LOW |
| **Method** | Collect cash series, holdings series, trade count, and any auxiliary metrics into a plain Python dict, then use `json.dumps` with `default=str` to convert to a string. |


---

## build_equity_curve

### Description
Generates a daily equity‑curve pandas Series by combining cash balances, holdings positions, and price data for the backtest simulation.

### Implementation Plan

#### 1. Deserialize the three input strings into pandas Series/DataFrames with matching datetime indices.

| Category | Details |
| --- | --- |
| **Reason** | The backtest engine passes data as serialized strings; they must be converted back to pandas objects for arithmetic. |
| **Impact** | Ensures subsequent calculations operate on correctly typed, index‑aligned data, preventing shape mismatches. |
| **Complexity** | MEDIUM |
| **Method** | Use json.loads or pd.read_json / pd.read_csv depending on the chosen serialization format; enforce UTC timezone and forward‑fill missing dates to create a unified index. |

#### 2. Compute the equity curve as cash + (holdings × price) for each date.

| Category | Details |
| --- | --- |
| **Reason** | The equity curve reflects total portfolio value, which is the sum of liquid cash and market value of positions. |
| **Impact** | Produces the core performance metric required for downstream analytics such as returns, Sharpe, and drawdown. |
| **Complexity** | LOW |
| **Method** | Perform element‑wise multiplication of the holdings Series with the price Series, add the cash Series, and store the result as a new pandas Series. |

#### 3. Handle edge cases (NaNs, mis‑aligned indices, zero‑division) and serialize the resulting Series back to a string.

| Category | Details |
| --- | --- |
| **Reason** | Real‑world data may contain missing values or mismatched dates; robust handling prevents runtime failures and preserves data integrity. |
| **Impact** | Guarantees that the shim always returns a valid, consumable equity curve string, even when input data is imperfect. |
| **Complexity** | MEDIUM |
| **Method** | Apply .fillna(method='ffill').fillna(0) to the intermediate Series, verify index alignment with .reindex, then serialize using Series.to_json(orient='split') or to_csv with index=True. |


---

## calculate_performance_metrics

### Description
Computes a dictionary of key back‑test performance metrics from a provided equity curve series and trade count.

### Implementation Plan

#### 1. Parse the incoming `equity_curve` string into a pandas Series of daily portfolio values.

| Category | Details |
| --- | --- |
| **Reason** | The shim receives the equity curve as a serialized string; converting it to a numeric series is required for calculations. |
| **Impact** | Enables downstream vectorized operations for return, drawdown, and Sharpe calculations. |
| **Complexity** | LOW |
| **Method** | Use `json.loads` or `ast.literal_eval` to convert the string to a list, then create a `pd.Series` with a datetime index inferred from the data. |

#### 2. Calculate total return, annualized Sharpe ratio (risk‑free rate = 0), maximum drawdown, and the back‑test period start/end dates.

| Category | Details |
| --- | --- |
| **Reason** | These metrics are the core performance indicators needed by the `BacktestTradingStrategyOutput` model. |
| **Impact** | Provides the quantitative summary that downstream nodes and users rely on for strategy evaluation. |
| **Complexity** | MEDIUM |
| **Method** | Compute daily returns via `pct_change()`, aggregate to total return, use `np.mean` and `np.std` on annualized returns for Sharpe, derive drawdown with a running max, and extract first/last dates from the Series index. |

#### 3. Assemble the computed values and the parsed `number_of_trades` into a JSON‑compatible dictionary and serialize it to a string for the `output` field.

| Category | Details |
| --- | --- |
| **Reason** | The shim contract expects a string representation of a dict, matching the declared output type. |
| **Impact** | Ensures downstream Pydantic validation succeeds and the back‑test node can unpack the metrics reliably. |
| **Complexity** | LOW |
| **Method** | Create a Python dict with keys `total_return`, `annualized_sharpe`, `max_drawdown`, `period_start`, `period_end`, `number_of_trades`; then `json.dumps` the dict to produce the `output` string. |


---

## log_backtest_error

### Description
Logs a backtest exception and returns a string representation of the error.

### Implementation Plan

#### 1. Capture the exception and convert it into a detailed, human‑readable string using the traceback module.

| Category | Details |
| --- | --- |
| **Reason** | Backtest failures need a full stack trace to diagnose the root cause. |
| **Impact** | Provides developers with precise diagnostic information, reducing time to fix bugs. |
| **Complexity** | LOW |
| **Method** | Import `traceback` and call `traceback.format_exception` on the exception object to produce a multi‑line string. |

#### 2. Persist the formatted error message to a centralized logging system (e.g., Python `logging` with a file or cloud handler).

| Category | Details |
| --- | --- |
| **Reason** | Transient console output is lost after execution; persistent logs are required for audit and post‑mortem analysis. |
| **Impact** | Creates an audit trail of backtest failures, enabling trend analysis and compliance reporting. |
| **Complexity** | MEDIUM |
| **Method** | Configure a `logging.Logger` with a rotating file handler or integrate with existing logging infrastructure, then log the error at `ERROR` level. |

#### 3. Return the formatted error string as the shim's output while ensuring no sensitive internal details are leaked.

| Category | Details |
| --- | --- |
| **Reason** | Downstream nodes expect a string output; sanitizing prevents accidental exposure of confidential data. |
| **Impact** | Allows the calling backtest node to handle the failure gracefully and report a clean status to users. |
| **Complexity** | LOW |
| **Method** | Optionally truncate or mask sensitive paths in the traceback, then return the final string from the function. |
