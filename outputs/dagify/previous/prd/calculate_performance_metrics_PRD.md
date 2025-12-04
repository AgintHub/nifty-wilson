# calculate_performance_metrics PRD

## Description
Evaluates backtest results.


## Implementation Plan

### 1. Validate the integrity of the trade log by ensuring that all five input arrays – trade_dates, trade_actions, trade_shares, trade_prices, trade_capital_after – have identical lengths and contain non‑empty entries.

| Category | Details |
| --- | --- |
| **Reason** | Consistent array lengths are critical for positional alignment during downstream calculations; mismatches would lead to index errors or mis‑aligned data. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Iterate over the length of any array and compare lengths; raise informative exception if discrepancy is detected. |

### 2. Parse ISO date strings into Python datetime objects and sort the trades chronologically to guarantee temporal consistency.

| Category | Details |
| --- | --- |
| **Reason** | Chronological ordering is necessary for correct computation of drawdowns, trade durations, and for aligning capital values with dates. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use datetime.strptime for each string, store tuples (date, index), then sort by date; re‑index arrays accordingly. |

### 3. Construct a daily portfolio value series for the entire backtest window by interpolating capital after each trade to every trading day.

| Category | Details |
| --- | --- |
| **Reason** | Many performance metrics (e.g., drawdown, Sharpe) require a continuous daily equity curve rather than sparse trade points. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Create a list of all dates from the earliest to the latest trade date; for each date, assign the capital value of the most recent trade before or on that date; forward‑fill missing dates. |

### 4. Compute cumulative return as (final equity / initial equity) - 1.

| Category | Details |
| --- | --- |
| **Reason** | This metric directly measures overall profitability relative to the starting capital. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | final_equity = last value in the daily equity series; initial_equity = trade_capital_after[0]; cumulative_return = (final_equity / initial_equity) - 1. |

### 5. Calculate daily log‑returns of the equity curve and derive mean and standard deviation for the Sharpe ratio calculation.

| Category | Details |
| --- | --- |
| **Reason** | Log‑returns provide a time‑additive, normally distributed basis for Sharpe computation, which is the industry standard. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Use np.diff(np.log(equity_series)) to get log‑returns; compute mean and std dev with numpy; handle any NaNs by dropping. |

### 6. Annualize the Sharpe ratio using the square‑root of the ratio between the number of trading days in a year (252) and the backtest trading days.

| Category | Details |
| --- | --- |
| **Reason** | Annualization allows comparison across strategies with different backtest horizons. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | sharpe_daily = mean_return / std_return; annual_factor = sqrt(252 / num_trading_days); annualized_sharpe_ratio = sharpe_daily * annual_factor. |

### 7. Determine maximum drawdown by scanning the equity curve for the deepest decline from a historical peak to a subsequent trough.

| Category | Details |
| --- | --- |
| **Reason** | Drawdown is a critical risk metric indicating potential capital erosion. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Maintain running maximum of equity; compute drawdown = (peak - equity) / peak; keep the maximum of these values. |

### 8. Identify winning trades by comparing consecutive entries in trade_capital_after; a trade is considered winning if the capital after the trade exceeds the capital before it.

| Category | Details |
| --- | --- |
| **Reason** | Win rate quantifies the strategy’s profitability at the trade level. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Iterate through indices i=1..n, count wins where trade_capital_after[i] > trade_capital_after[i-1]; win_rate = wins / (n-1). |

### 9. Calculate average trade duration by matching each 'Buy' action with its corresponding 'Exit' action and computing the date difference.

| Category | Details |
| --- | --- |
| **Reason** | Duration reflects strategy’s holding period characteristics, which influence capital allocation and risk. |
| **Impact** | MEDIUM |
| **Complexity** | HIGH |
| **Method** | Maintain a stack of open trade dates; on 'Buy', push date; on 'Exit', pop date, compute duration in days, store; after processing all trades, average durations of completed trades. |

### 10. Round all floating‑point outputs to eight decimal places to maintain consistency and avoid floating‑point noise in downstream reporting.

| Category | Details |
| --- | --- |
| **Reason** | Consistent formatting ensures deterministic JSON outputs, simplifying unit tests and downstream parsing. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use round(value, 8) or format with f"{value:.8f}". |

### 11. Return the metrics in a JSON dictionary matching the specified output structure.

| Category | Details |
| --- | --- |
| **Reason** | The downstream generate_strategy_report node expects this exact JSON schema. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Construct a dict with keys: cumulative_return, annualized_sharpe_ratio, maximum_drawdown, win_rate, average_trade_duration, then serialize with json.dumps. |
