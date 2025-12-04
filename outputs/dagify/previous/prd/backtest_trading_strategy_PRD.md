# backtest_trading_strategy PRD

## Description
Performs a rigorous, production‑grade backtest of the fully specified trading strategy using the fetched Yahoo Finance data, the asset universe, and the signal generation logic.


## Implementation Plan

### 1. Parse the CSV strings from **fetch_stock_data_yahoo_data** into pandas DataFrames, enforce UTC DatetimeIndex, and ensure columns are exactly ['Open','High','Low','Close','Adj Close','Volume'].

| Category | Details |
| --- | --- |
| **Reason** | Standardizing data format guarantees downstream calculations operate on a consistent schema and eliminates hidden timezone bugs. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use pandas.read_csv with StringIO, set parse_dates=True, date_parser=pd.to_datetime, tz='UTC'; validate column order with assert statements. |

### 2. Create a master business‑day calendar covering the intersection of all ticker date ranges; reindex each ticker DataFrame onto this calendar, forward‑fill missing values, and drop leading rows with any NaN after alignment.

| Category | Details |
| --- | --- |
| **Reason** | Aligning on a common index is essential for accurate signal evaluation and portfolio aggregation across assets. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Determine min(max_start_date) and max(min_end_date) across tickers; generate pandas.bdate_range; for each DataFrame, df.reindex(master_index, method='ffill'); drop rows where any ticker still has NaN using df.dropna(how='any'). |

### 3. Translate **develop_trading_signal_logic.signal_logic_steps** into an executable Python function that takes a unified DataFrame (rows=dates, columns=multi‑index ticker/field) and returns a DataFrame of position intents (+1 for long, -1 for short, 0 for flat) per ticker per day.

| Category | Details |
| --- | --- |
| **Reason** | A deterministic, vectorised signal function enables fast daily evaluation and facilitates later backtesting loops. |
| **Impact** | HIGH |
| **Complexity** | HIGH |
| **Method** | Parse the list of textual rules (e.g., "If SMA_20 > SMA_50 then BUY") into pandas boolean masks; combine masks per ticker; store results in a DataFrame called `signals` with same index as price data. |

### 4. Implement an execution engine that iterates over the chronologically ordered dates, compares current positions to previous day's signals, generates trade orders, applies configurable commission (default 0.001 per trade) and slippage (default 0.0005 price offset), and updates cash and holdings accordingly.

| Category | Details |
| --- | --- |
| **Reason** | Simulating realistic trading costs and order execution is crucial for credible performance metrics. |
| **Impact** | HIGH |
| **Complexity** | HIGH |
| **Method** | Maintain variables: cash, holdings dict, portfolio_value series; for each date: identify changed signals, compute trade size = (available_capital * allocation_per_asset) / price; subtract commission = trade_size * commission_rate; adjust fill price = price * (1 + slippage * sign); update holdings and cash. |

### 5. Construct the daily equity curve by summing cash plus market value of all holdings (position * close price) after each day's execution; store results in a pandas Series `equity_curve` indexed by date.

| Category | Details |
| --- | --- |
| **Reason** | The equity curve is the basis for all downstream performance statistics. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | equity_curve[date] = cash + sum(holdings[ticker] * close_price[ticker] for each ticker). |

### 6. Calculate performance metrics: total_return = (final_equity / initial_capital) - 1; daily_returns = equity_curve.pct_change().dropna(); annualized_sharpe = sqrt(252) * mean(daily_returns) / std(daily_returns); max_drawdown = max( (peak - trough)/peak ) using a rolling max; number_of_trades = count of executed orders; backtest_period_start/end = first/last date of equity_curve.

| Category | Details |
| --- | --- |
| **Reason** | These metrics provide a standardized quantification of risk‑adjusted returns and trade activity. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Use numpy and pandas functions: np.sqrt(252), equity_curve.cummax() for drawdown calculation, and simple integer counter for trades. |

### 7. Wrap the entire pipeline in a try/except block; on any exception set `success=False`, log the exception message to a dedicated log string, and populate output fields with NaN/zero defaults; otherwise set `success=True`.

| Category | Details |
| --- | --- |
| **Reason** | Robust error handling ensures the node returns a well‑defined output even when upstream data is malformed. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use Python's try: ... except Exception as e: success=False; log_message=str(e); assign default values; finally return the output dictionary. |
