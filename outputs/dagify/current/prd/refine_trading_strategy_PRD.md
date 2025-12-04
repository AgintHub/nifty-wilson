# refine_trading_strategy PRD

## Description
Iteratively enhances the quantitative trading strategy by performing a data‑driven, statistically rigorous refinement cycle.


## Implementation Plan

### 1. Load the backtest output JSON produced by `backtest_trading_strategy` and validate that `success` == true; if false, raise a controlled exception and abort refinement with a clear error message.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the refinement cycle only runs on a clean, error‑free backtest, preventing propagation of faulty data. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Parse JSON, check boolean flag, log detailed error using standard logging library; wrap in try/catch to capture parsing exceptions. |

### 2. Extract core performance metrics: `total_return`, `annualized_sharpe_ratio`, `max_drawdown`, and `number_of_trades` from the backtest payload.

| Category | Details |
| --- | --- |
| **Reason** | These metrics are the quantitative basis for evaluating whether the strategy meets predefined investment objectives. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Map each field to a local variable; coerce types to float/int as defined in the schema; store in a metrics dictionary. |

### 3. Define target thresholds for each metric (e.g., Sharpe ≥ 1.2, max_drawdown ≤ 0.15, total_return ≥ 0.10, trades between 30‑200) using a configurable JSON/YAML file so that thresholds can be tuned without code changes.

| Category | Details |
| --- | --- |
| **Reason** | Externalizing targets enables rapid experimentation and aligns the refinement logic with portfolio manager expectations. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Read `refinement_targets.yaml` via `pyyaml`; fallback to hard‑coded defaults if file missing; validate numeric ranges. |

### 4. Compute a metric‑gap report by comparing each observed metric to its target, categorizing gaps as `PASS`, `MARGINAL` (within 5% of target), or `FAIL` (outside 5%). Store this classification for later decision logic.

| Category | Details |
| --- | --- |
| **Reason** | Provides a systematic way to prioritize which aspects of the strategy need adjustment. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Iterate over metric dictionary, calculate percent deviation, assign categorical label; output a `gap_report` dict. |

### 5. Perform a one‑factor sensitivity analysis for each tunable parameter, indicator setting, and risk rule that was originally defined in `develop_trading_signal_logic` and `define_risk_management_rules`. For each factor, vary it ±10% (or a domain‑specific step) while holding others constant, re‑run a lightweight backtest simulation using the same price data (reuse the data preparation code from `backtest_trading_strategy` but skip CSV I/O). Capture the resulting metric changes.

| Category | Details |
| --- | --- |
| **Reason** | Quantifies how each individual lever influences performance, identifying high‑impact levers for adjustment. |
| **Impact** | HIGH |
| **Complexity** | HIGH |
| **Method** | Create a parameter grid; for each entry, clone the original strategy object, modify the single field, call a simplified backtest function (`simulate_backtest`) that returns the same metric set; store results in a DataFrame for analysis. |

### 6. Rank all factors by their sensitivity score defined as the absolute change in Sharpe ratio multiplied by a weighting factor for drawdown and return (e.g., `score = |ΔSharpe| * 0.5 + |ΔReturn| * 0.3 + |ΔDrawdown| * 0.2`). Select the top‑3 factors where the metric gap is `FAIL` or `MARGINAL`.

| Category | Details |
| --- | --- |
| **Reason** | Focuses refinement effort on the most influential levers that can close the performance gaps. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Compute score per factor from sensitivity DataFrame, sort descending, filter by gap classification. |

### 7. Generate concrete adjustment proposals for the selected factors: for parameters, propose the value that yielded the best Sharpe in the sensitivity sweep; for indicators, adjust period lengths or thresholds to the optimal values; for risk rules, tighten stop‑loss or modify position‑size scaling factor as indicated by the analysis.

| Category | Details |
| --- | --- |
| **Reason** | Provides data‑driven, actionable changes rather than heuristic guesses. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Extract the optimum value from the sensitivity DataFrame per factor; format as bullet strings: `- Parameter XYZ: 0.05 → 0.08`. |

### 8. Compose `parameter_adjustments`, `indicator_adjustments`, and `risk_rule_adjustments` strings by concatenating the bullet points generated in the previous step, preserving the order: parameters → indicators → risk rules.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the output fields match the required schema and are human‑readable. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Join bullet list with newline characters; prepend a short header if desired (e.g., "Adjusted Parameters:"). |

### 9. Draft `reasoning_for_adjustments` by linking each bullet to the specific metric gap it addresses and citing the sensitivity score that motivated the change. Use a structured paragraph format: "The Sharpe ratio fell short of the 1.2 target (observed 0.95). Sensitivity analysis showed that increasing the EMA period from 20 to 30 improved Sharpe by +0.18, therefore the period was adjusted...".

| Category | Details |
| --- | --- |
| **Reason** | Provides transparency and auditability for downstream stakeholders and for the next refinement iteration. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Iterate over adjustment bullets, retrieve corresponding gap and score from earlier dictionaries, concatenate explanatory sentences. |

### 10. Assemble `refined_strategy_summary` that encapsulates the overall direction of the refinement: mention which metric gaps were closed, any remaining gaps, and a high‑level view of the new parameter/indicator/risk configuration.

| Category | Details |
| --- | --- |
| **Reason** | Serves as the executive‑level narrative for the downstream `compile_final_strategy_blueprint` node. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Summarize metric changes (e.g., "Sharpe improved from 0.95 to 1.14"), list the three key adjustments, and note any residual issues. |

### 11. Validate that all output strings are non‑empty and conform to the expected primitive types; if any field is empty, raise a validation error before returning to enforce contract compliance.

| Category | Details |
| --- | --- |
| **Reason** | Guarantees downstream nodes receive well‑formed data and prevents silent failures. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Simple `if not field.strip(): raise ValueError` checks; unit‑test each output field. |
