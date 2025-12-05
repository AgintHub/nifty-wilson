# define_risk_management_rules PRD

## Description
Establish risk management rules for the strategy


## Implementation Plan

### 1. Validate the input from develop_trading_signals – check the `is_valid` flag and ensure that at least one signal is available. If the signals are invalid, default to conservative risk parameters (e.g., risk_per_trade_percent = 0.5%, stop_loss_percent = 5%).

| Category | Details |
| --- | --- |
| **Reason** | Ensures that risk rules are only generated when reliable trading signals exist, preventing the propagation of erroneous risk settings. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Check boolean flag; use conditional logic to assign defaults. |

### 2. Determine the maximum number of simultaneous positions (`max_positions`) by taking the minimum of the number of generated signals (`num_signals`) and a hard‑coded portfolio capacity limit (e.g., 10). This caps exposure and encourages diversification.

| Category | Details |
| --- | --- |
| **Reason** | Balances trade execution volume against portfolio risk limits and prevents over‑concentration. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Apply min(num_signals, 10) to compute max_positions. |

### 3. Compute the base risk‑per‑trade percentage by scaling a default risk appetite (1%) with the strategy’s risk tolerance level. For example, `risk_per_trade_percent = 1.0 * (risk_tolerance_level / 10)`. If the risk_tolerance_level is not available, default to 1.0%.

| Category | Details |
| --- | --- |
| **Reason** | Aligns trade risk with the overall strategy risk tolerance, making the rule adjustable to different risk profiles. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use simple arithmetic; fallback to default if missing. |

### 4. Calculate the stop‑loss threshold (`stop_loss_percent`) as a function of the asset’s historical volatility. Compute a 30‑day rolling volatility of the asset’s returns, convert to a daily volatility, then set `stop_loss_percent = 2.0 + (daily_vol * 100 * 0.5)`. Cap the value at 5% to avoid overly tight stops during high‑volatility periods.

| Category | Details |
| --- | --- |
| **Reason** | Dynamic stop‑loss sizing protects against both low‑ and high‑volatility regimes, improving risk‑adjusted performance. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Run a volatility rolling window calculation, apply scaling, enforce upper bound. |

### 5. Set the maximum drawdown limit (`max_drawdown_percent`) to a conservative fraction (e.g., 75%) of the strategy objective’s maximum drawdown. If the objective maximum drawdown is unavailable, default to 10.0%. This provides a hard stop that aligns with strategic goals.

| Category | Details |
| --- | --- |
| **Reason** | Ensures portfolio drawdown remains within acceptable bounds, protecting capital during adverse market movements. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Multiply objective_max_drawdown by 0.75; fallback to default. |

### 6. Define the position sizing rule (`position_sizing_rule`) as a volatility‑based approach: `position_size = (portfolio_equity * risk_per_trade_percent / 100) / (stop_loss_percent / 100 * entry_price)`. Store a textual description of this methodology.

| Category | Details |
| --- | --- |
| **Reason** | Volatility‑based sizing adapts trade size to market conditions and ensures consistent risk exposure per trade. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Implement the formula; generate description string. |

### 7. Compile additional risk controls into `risk_control_description`: include diversification limits (no single asset pair >20% of portfolio), a market‑volatility filter (skip trades if implied volatility > 30%), daily position limit enforcement, and a mandatory stop‑loss audit. Provide a concise paragraph summarizing these controls.

| Category | Details |
| --- | --- |
| **Reason** | Documenting all supplementary controls ensures transparency and auditability for the strategy. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Concatenate predefined control statements into a single string. |

### 8. Perform consistency checks: ensure that `stop_loss_percent` is between 1% and 5%, `risk_per_trade_percent` between 0.1% and 3%, and `max_drawdown_percent` not exceeding 20%. If any value falls outside these bounds, adjust to nearest permissible limit and record a warning in the `risk_control_description`.

| Category | Details |
| --- | --- |
| **Reason** | Prevents unrealistic or unsafe risk parameters that could jeopardize portfolio stability. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Apply boundary conditions; log adjustments. |

### 9. Output all computed fields in the specified schema, ensuring type correctness: convert percentages to float, integer fields to int, and descriptions to string.

| Category | Details |
| --- | --- |
| **Reason** | Guarantees that downstream nodes receive data in the expected format for accurate backtesting. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Cast values to required types; serialize to JSON. |
