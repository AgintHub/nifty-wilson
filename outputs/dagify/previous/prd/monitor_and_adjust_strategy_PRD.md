# monitor_and_adjust_strategy PRD

## Description
Continuously monitor the strategy's performance and adjust as necessary


## Implementation Plan

### 1. Activate the monitoring flag by setting `monitoring_active` to true when the strategy is in a deployed state (i.e., `deployment_status` equals 'Success').

| Category | Details |
| --- | --- |
| **Reason** | The monitoring process should only run for actively deployed strategies to avoid unnecessary computation on failed or pending deployments. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | If implement_strategy.deployment_status == 'Success' then monitoring_active = True else monitoring_active = False |

### 2. Retrieve the most recent trade and portfolio snapshot from the broker's REST API or database using the `last_deployment_timestamp` as a reference point.

| Category | Details |
| --- | --- |
| **Reason** | Performance metrics must reflect the live state of the strategy after the last deployment, ensuring metrics are up‑to‑date. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use authenticated HTTP requests to the broker's /portfolio endpoint, filter by strategy_id and timestamp >= last_deployment_timestamp, parse JSON into a pandas DataFrame |

### 3. Compute `latest_annualized_return`, `latest_sharpe_ratio`, and `latest_max_drawdown` from the fetched trade history using standard formulas: annualized_return = (final_portfolio_value / initial_value)^(252/total_trading_days) - 1; sharpe = mean(return) / std(return) * sqrt(252); max_drawdown = (peak_portfolio_value - trough_value) / peak_portfolio_value.

| Category | Details |
| --- | --- |
| **Reason** | These metrics provide quantitative indicators of the strategy’s performance and risk profile needed for decision making. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Implement calculation in Python using numpy/pandas; ensure handling of zero variance cases and missing data |

### 4. Count `trades_executed_since_last_check` by grouping the trade history by timestamp and summing trades between the last check timestamp and now.

| Category | Details |
| --- | --- |
| **Reason** | The number of trades indicates market activity and can trigger parameter adjustment thresholds. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use pandas groupby on 'timestamp' and count 'trade_id' |

### 5. Evaluate adjustment criteria: if `latest_sharpe_ratio` falls below a predefined threshold (e.g., 0.5) or `latest_max_drawdown` exceeds the maximum allowed (from `define_risk_management_rules.max_drawdown_percent`), set `adjustments_made` to true and trigger a parameter update cycle.

| Category | Details |
| --- | --- |
| **Reason** | Thresholds provide an objective basis for when to intervene, ensuring the strategy remains within risk tolerance. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Implement a rule engine or simple if/else logic comparing metrics to stored config values |

### 6. If adjustments are triggered, load the current strategy configuration (e.g., from a JSON config file), modify relevant fields such as position sizing multiplier or stop‑loss percent, and record each change in a list for `parameter_change_count`.

| Category | Details |
| --- | --- |
| **Reason** | Parameter adjustments must be transparent and auditable to maintain compliance and reproducibility. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Read config JSON, apply incremental updates, serialize back; increment counter for each field modified |

### 7. Persist the updated configuration back to the deployment environment (e.g., upload to a configuration server or re‑deploy the strategy code) and log the `adjustment_description` summarizing the changes made.

| Category | Details |
| --- | --- |
| **Reason** | Persisting ensures the new parameters are actively used in subsequent trades; logging aids future audits. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use platform's config API or SCP to server; append a human‑readable description to a changelog file |

### 8. Update `last_adjustment_timestamp` with the current UTC timestamp in ISO 8601 format immediately after persisting changes.

| Category | Details |
| --- | --- |
| **Reason** | A timestamp is required for audit trails and to calculate `next_check_in_days` accurately. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | datetime.utcnow().isoformat() + 'Z' |

### 9. Calculate `next_check_in_days` by adding a configurable monitoring interval (e.g., 1 day) to the current date, or dynamically adjusting the interval based on volatility metrics (e.g., increase frequency during high volatility).

| Category | Details |
| --- | --- |
| **Reason** | Adaptive check frequency ensures timely reaction to market changes while conserving resources during stable periods. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | If VIX > threshold then next_check_in_days = 0 else next_check_in_days = 1 |

### 10. Export all computed fields into the defined output structure as JSON, ensuring type compliance (e.g., floats rounded to 4 decimals, integers cast appropriately).

| Category | Details |
| --- | --- |
| **Reason** | Consistent data serialization facilitates downstream ingestion and monitoring dashboards. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use json.dumps with type casting; apply round() for numeric fields |
