# backtest_strategy PRD

## Description
Backtest the statistical arbitrage strategy using historical data


## Implementation Plan

### 1. Load and merge the cleaned historical price series with the generated signal timestamps ensuring time alignment across all asset pairs.

| Category | Details |
| --- | --- |
| **Reason** | Accurate alignment guarantees that signals are evaluated on the correct price data and that trade execution times correspond to the intended market events. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use pandas’ `merge_asof` or `reindex` to align timestamps; validate alignment by checking the number of matched rows against expected signal counts. |

### 2. Apply the risk‑management rules to each signal to compute position sizing and stop‑loss thresholds before any trade execution.

| Category | Details |
| --- | --- |
| **Reason** | Pre‑computing positions and risk limits ensures that every simulated trade adheres to the predefined constraints, preventing unrealistic P&L estimates. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | For each signal, compute trade size using `position_sizing_rule`; calculate stop‑loss price as `entry_price * (1 ± stop_loss_percent/100)`; store these in a structured dataframe for downstream simulation. |

### 3. Simulate trade execution by stepping through each trading day, applying all active positions, and updating portfolio equity based on price changes.

| Category | Details |
| --- | --- |
| **Reason** | Day‑by‑day simulation captures intraday volatility, ensures correct PnL accumulation, and respects stop‑loss and max drawdown limits. |
| **Impact** | HIGH |
| **Complexity** | HIGH |
| **Method** | Iterate over the sorted signal dataframe; on each new day, update unrealized PnL for open positions, close positions at stop‑loss if triggered, and record realized PnL; maintain a rolling equity curve. |

### 4. Enforce the maximum drawdown constraint by monitoring the equity curve and halting new positions once the drawdown exceeds `max_drawdown_percent`.

| Category | Details |
| --- | --- |
| **Reason** | This prevents the backtest from continuing in a regime that would violate the strategy’s risk tolerance, mirroring real‑world portfolio constraints. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Compute peak equity; if current equity < peak * (1 - max_drawdown_percent/100), set a flag to stop opening new positions until equity recovers or simulation ends. |

### 5. Calculate realized and unrealized profit‑and‑loss per trade, distinguishing winning and losing trades to compute `average_profit_per_trade` and `average_loss_per_trade`.

| Category | Details |
| --- | --- |
| **Reason** | Separating wins and losses provides granular insight into trade quality and assists in refining signal thresholds. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Maintain two lists: `wins` and `losses`; append trade PnL to the appropriate list; compute means after simulation. |

### 6. Compute cumulative return, annualized return, Sharpe ratio, and maximum drawdown from the equity curve.

| Category | Details |
| --- | --- |
| **Reason** | These metrics are industry standard for assessing strategy performance and risk‑adjusted returns. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use numpy to calculate total return as last equity / initial equity - 1; annualize using `(1+total_return)**(252/num_days)-1`; Sharpe = mean(returns)/std(returns) * sqrt(252); drawdown = (cumulative max - equity)/cumulative max. |

### 7. Determine the total number of executed trades and calculate the winning trade rate as the ratio of winning trades to total trades.

| Category | Details |
| --- | --- |
| **Reason** | Trade count and win rate are key performance indicators that influence risk‑adjusted metrics and inform strategy robustness. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Count entries in the trade log; compute win rate by dividing number of trades where PnL > 0 by total trades. |

### 8. Generate a concise `report_summary` string summarizing the key results (e.g., total return, Sharpe, max drawdown, win rate).

| Category | Details |
| --- | --- |
| **Reason** | A quick textual summary aids stakeholders in grasping performance without parsing all numeric fields. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use string interpolation to format the metrics into a one‑sentence paragraph. |

### 9. Set the `backtest_success` flag to `True` only if the simulation completes without unhandled exceptions, missing data issues, or violation of critical constraints.

| Category | Details |
| --- | --- |
| **Reason** | Clear success indicator ensures downstream nodes can safely proceed or trigger error handling. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Wrap the entire simulation in try/except; on any exception, set flag to False and log error details. |

### 10. Validate all output fields against expected ranges (e.g., winning_trade_rate ∈ [0,1], max_drawdown_pct ≥ 0) and assert type consistency before returning results.

| Category | Details |
| --- | --- |
| **Reason** | Type and range validation protects downstream processes from corrupt or malformed data, improving system robustness. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use assert statements or custom validation functions; if validation fails, raise descriptive error. |
