# design_risk_management_framework PRD

## Description
Outline quantitative and qualitative risk controls.


## Implementation Plan

### 1. Collect the numerical performance and risk targets from the parent node, specifically the annual gross return, volatility, Sharpe ratio, and maximum drawdown percentages, and store them in local variables.

| Category | Details |
| --- | --- |
| **Reason** | These metrics serve as the reference points for calibrating each risk control to the fund’s strategic objectives. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Parse JSON output of 'set_performance_and_risk_targets', assign values to variables: gross_return, volatility, sharpe_ratio, max_drawdown. |

### 2. Define a position limit rule that caps the total exposure per trade as a fixed percentage of the total AUM, calculated as 5% of the target gross return divided by the target Sharpe ratio, rounded to the nearest 0.5%.

| Category | Details |
| --- | --- |
| **Reason** | Position limits prevent over‑concentration and tie exposure to expected risk‑adjusted performance. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Compute limit = round((gross_return / sharpe_ratio) * 0.05, 2). Ensure the result is expressed as a percentage of AUM. |

### 3. Set a VaR limit at the 95% confidence level equal to 1% of the portfolio value, scaled by the square root of the target volatility to reflect expected market swings.

| Category | Details |
| --- | --- |
| **Reason** | VaR limits quantify potential loss within a confidence interval and are directly linked to volatility expectations. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | VaR_limit = 0.01 * sqrt(volatility) * portfolio_value. Format as a percentage of AUM. |

### 4. Implement a stop‑loss rule that triggers an exit when a single trade’s unrealized loss exceeds 2% of its position size, or 1% of the total portfolio if the trade volatility exceeds the target volatility by more than 50%.

| Category | Details |
| --- | --- |
| **Reason** | Stop‑losses protect against unexpected adverse moves and adapt to trade‑specific risk. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Use trade‑level volatility estimate to adjust the stop threshold; apply the higher of the two percentage triggers. |

### 5. Establish a liquidity threshold requiring that at least 20% of the portfolio remain in highly liquid instruments, ensuring the fund can meet liquidity demands within the maximum drawdown window.

| Category | Details |
| --- | --- |
| **Reason** | Liquidity thresholds safeguard against forced sales during stressed market conditions. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Maintain a separate liquid asset buffer; monitor daily liquidity ratio against the 20% benchmark. |

### 6. Compile the formulated controls into a single list of string statements, each clearly referencing the associated metric and percentage, and assign this list to the 'risk_controls' output field.

| Category | Details |
| --- | --- |
| **Reason** | The final output must adhere to the defined output structure and provide a consumable risk control summary for downstream nodes. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Concatenate formatted strings: e.g., "Position limit: ≤ X% of AUM", "VaR limit: 95% VaR ≤ 1% of portfolio", etc.; set risk_controls = [list of strings]. |
