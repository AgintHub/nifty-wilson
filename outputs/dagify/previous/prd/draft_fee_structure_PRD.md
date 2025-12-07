# draft_fee_structure PRD

## Description
Set management and performance fee levels.


## Implementation Plan

### 1. Extract and validate all numeric inputs from the two dependency outputs, converting them to floats and ensuring they are non‑negative.

| Category | Details |
| --- | --- |
| **Reason** | Ensures data integrity before any calculations; prevents type‑mismatch errors that would cascade to the final fee percentages. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Parse JSON, cast strings to float, apply `>= 0` checks, and log any anomalies. |

### 2. Calculate `hurdle_rate_percentage` by setting a base hurdle of 5 % absolute return, but increase it to 5 % of the target gross return when the gross target is below 10 %. Cap the hurdle at 8 % to keep the structure attractive.

| Category | Details |
| --- | --- |
| **Reason** | Balances incentive alignment with risk‑adjusted return expectations while keeping the hurdle realistic for the chosen strategy. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Apply formula: `hurdle = min(8.0, max(5.0, gross_return * 0.5))` where `gross_return` is from `set_performance_and_risk_targets`. |

### 3. Determine `management_fee_percentage` by first normalizing the total annual cost against a reference AUM of 100 M USD. If the cost ratio exceeds 3 % of AUM, set the fee to 2 %; otherwise set it to 1.5 %.

| Category | Details |
| --- | --- |
| **Reason** | Guarantees that management fees will cover operating expenses while remaining competitive relative to industry averages. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Compute `cost_ratio = total_estimated_annual_cost / 100_000_000 * 100`; then apply conditional assignment. |

### 4. Set `performance_fee_percentage` to 20 % if the target Sharpe ratio is ≥ 1.0, otherwise 25 %. If the target maximum drawdown exceeds 25 %, increase the fee to 30 %.

| Category | Details |
| --- | --- |
| **Reason** | Aligns performance incentives with the risk‑return profile: lower risk yields a more attractive fee, whereas higher risk commands a premium. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Implement nested conditional logic using the Sharpe ratio and maximum drawdown values from `set_performance_and_risk_targets`. |

### 5. Construct a `summary_sentence` that succinctly states the management fee, performance fee, and hurdle rate, limiting the output to no more than two sentences.

| Category | Details |
| --- | --- |
| **Reason** | Directly satisfies the prompt’s requirement for a concise summary. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Template string interpolation: "Our fund charges a {m_fee:.1f}% management fee, {p_fee:.1f}% performance fee above a {hurdle:.1f}% hurdle." |
