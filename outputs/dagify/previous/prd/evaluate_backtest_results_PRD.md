# evaluate_backtest_results PRD

## Description
Evaluates the backtest output by transforming raw metrics into standardized, decimal‑based figures, computing derived statistics such as profit factor and average trade PnL, benchmarking against a reference return, and flagging viability against predefined thresholds. The result is a concise, human‑readable summary of strengths, weaknesses, and suggested improvements.


## Implementation Plan

### 1. Validate the backtest_strategy output to ensure all required fields are present and numeric before proceeding.

| Category | Details |
| --- | --- |
| **Reason** | Early validation prevents downstream errors and guarantees that all metrics exist for conversion and calculation. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Check presence of keys ['total_return_pct', 'sharpe_ratio', 'max_drawdown_pct', 'trade_count', 'winning_trade_rate', 'average_profit_per_trade', 'average_loss_per_trade'] and that each value is a float or int; raise informative error if validation fails. |

### 2. Convert percentage‑based metrics from backtest_strategy into decimal form (divide by 100).

| Category | Details |
| --- | --- |
| **Reason** | Standardizes units across all outputs and aligns with the expected output format for total_return, max_drawdown, and benchmark_return. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | total_return = total_return_pct / 100.0; max_drawdown = max_drawdown_pct / 100.0; benchmark_return = benchmark_pct / 100.0 (if benchmark_pct is available). |

### 3. Directly map the Sharpe ratio from backtest_strategy to the output field.

| Category | Details |
| --- | --- |
| **Reason** | Sharpe ratio is already expressed in standard decimal form and does not require scaling. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | sharpe_ratio = backtest_strategy['sharpe_ratio']. |

### 4. Assign the trade count and win rate from backtest_strategy to num_trades and win_rate.

| Category | Details |
| --- | --- |
| **Reason** | These metrics already match the desired output types and represent core performance indicators. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | num_trades = int(backtest_strategy['trade_count']); win_rate = float(backtest_strategy['winning_trade_rate']). |

### 5. Calculate avg_trade_pnl as the net average per trade by subtracting the average loss from the average profit and normalizing by initial capital of 1.

| Category | Details |
| --- | --- |
| **Reason** | Provides a clear per‑trade profitability metric that is independent of capital size. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | avg_trade_pnl = float(backtest_strategy['average_profit_per_trade']) - float(backtest_strategy['average_loss_per_trade']). |

### 6. Derive profit_factor using gross profit and gross loss totals.

| Category | Details |
| --- | --- |
| **Reason** | Profit factor is a key risk‑adjusted metric; calculating it from backtest averages yields an interpretable figure. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | [gross_profit = avg_profit_per_trade * win_rate * num_trades, gross_loss = avg_loss_per_trade * (1 - win_rate) * num_trades, profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')] |

### 7. Determine benchmark_return by retrieving the benchmark's cumulative return for the same date range (assumed available via an external lookup).

| Category | Details |
| --- | --- |
| **Reason** | Benchmark comparison contextualizes performance. |
| **Impact** | LOW |
| **Complexity** | MEDIUM |
| **Method** | If external function get_benchmark_return(start_date, end_date) returns decimal, assign it; otherwise set benchmark_return = 0.0. |

### 8. Apply predefined viability thresholds (e.g., Sharpe > 1.0, max_drawdown < 0.10, win_rate > 0.40, profit_factor > 1.5) to set is_acceptable.

| Category | Details |
| --- | --- |
| **Reason** | Automates decision‑making for strategy refinement and aligns with common risk‑return trade‑offs. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | is_acceptable = all([sharpe_ratio > 1.0, max_drawdown < 0.10, win_rate > 0.40, profit_factor > 1.5]). |

### 9. Generate summary_notes by evaluating each metric against threshold ranges and producing bullet‑point feedback.

| Category | Details |
| --- | --- |
| **Reason** | Provides actionable insight for stakeholders and the refinement step. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | [notes = [], if sharpe_ratio < 1.0: notes.append('- Sharpe ratio below target; consider tightening stop‑loss or improving signal precision.'), if max_drawdown >= 0.10: notes.append('- Drawdown exceeds acceptable limit; review position sizing and risk controls.'), if win_rate < 0.40: notes.append('- Low win rate; examine entry/exit thresholds or incorporate additional filters.'), if profit_factor <= 1.5: notes.append('- Profit factor low; investigate slippage or execution quality.'), if not notes: notes.append('- Strategy meets all viability criteria; ready for deployment.')] |
