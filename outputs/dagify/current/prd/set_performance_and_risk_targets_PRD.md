# set_performance_and_risk_targets PRD

## Description
Quantify return and risk goals.


## Implementation Plan

### 1. Parse the output of the parent node `choose_investment_strategy` to identify the selected strategy category and its qualitative performance benchmarks.

| Category | Details |
| --- | --- |
| **Reason** | The risk and return targets must be calibrated to the chosen strategy; hence we need the strategy name and any high‑level benchmark references. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Read the `strategy_category` field from the parent’s output; if the strategy includes a benchmark (e.g., S&P 500 for Long/Short Equity), retrieve its historical annualized return, volatility, and Sharpe ratio from a pre‑loaded database. Use these figures as a baseline for target setting. |

### 2. Define a target gross return that is 5% above the strategy’s historical mean return, but capped at a realistic maximum of 30% to maintain credibility.

| Category | Details |
| --- | --- |
| **Reason** | Setting targets modestly higher than historical performance provides ambition without overpromising. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Calculate mean annual return (μ) from historical data; set `gross_return = min(μ + 5, 30.0)`. |

### 3. Set volatility to 20–30% higher than the strategy’s historical volatility to account for future uncertainty, with an upper bound of 25% to avoid extreme risk appetite.

| Category | Details |
| --- | --- |
| **Reason** | Risk targets should reflect a conservative margin over past volatility while ensuring the fund is not perceived as excessively risky. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Compute historical σ; set `volatility = min(σ * 1.2, 25.0)`. |

### 4. Derive the Sharpe ratio target as the historical Sharpe ratio plus 0.1, limited to a maximum of 2.0 to maintain realistic expectations.

| Category | Details |
| --- | --- |
| **Reason** | Sharpe ratio is a key performance metric; a modest increase signals performance improvement without being overly optimistic. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Retrieve historical Sharpe S; set `sharpe_ratio = min(S + 0.1, 2.0)`. |

### 5. Define maximum drawdown as 50% of the historical peak‑to‑trough drawdown, but not exceeding 45% to keep the target achievable.

| Category | Details |
| --- | --- |
| **Reason** | Drawdown tolerance should be moderate; tying it to historical extremes ensures realism. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Calculate historical D; set `max_drawdown = min(D * 0.5, 45.0)`. |

### 6. Validate that the resulting target metrics are internally consistent: volatility should be >= target gross return divided by Sharpe ratio, and max_drawdown should be <= 3× volatility to avoid overly aggressive targets.

| Category | Details |
| --- | --- |
| **Reason** | Consistency checks prevent contradictory metrics that could mislead stakeholders. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Perform the two checks; if either fails, adjust volatility downwards or gross_return upwards within the defined bounds until all conditions hold. |

### 7. Format the four numerical outputs into a plain 4‑row table, rounding each value to one decimal place and appending a percentage sign for clarity.

| Category | Details |
| --- | --- |
| **Reason** | The prompt explicitly requests a table; formatting improves readability for downstream nodes. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Generate a string: `| Metric | Target |
|-------|--------|
| Gross Return | X.X% |
| Volatility | Y.Y% |
| Sharpe Ratio | Z.Z |
| Max Drawdown | W.W% |`. |

### 8. Populate the JSON output structure with the computed float values (without percentage signs) to satisfy the downstream node type requirements.

| Category | Details |
| --- | --- |
| **Reason** | While the table is for human consumption, the programmatic output must be in raw numeric form. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Assign `gross_return`, `volatility`, `sharpe_ratio`, and `max_drawdown` to the JSON payload as floats. |
