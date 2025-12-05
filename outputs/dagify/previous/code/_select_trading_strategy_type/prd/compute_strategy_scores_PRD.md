# compute_strategy_scores PRD

## Description
Generates a weighted score dictionary for candidate trading strategies using data classification, technique mapping, and the summary note.


## Implementation Plan

### 1. Design a scoring matrix that assigns weights to each candidate strategy based on data classification attributes (latency, granularity, asset coverage) and technique mapping categories.

| Category | Details |
| --- | --- |
| **Reason** | A quantitative model is required to compare heterogeneous strategy candidates on a common scale. |
| **Impact** | Enables deterministic selection of the highest‑scoring strategy and provides transparency for downstream audit. |
| **Complexity** | MEDIUM |
| **Method** | Create a configurable dictionary of weight factors, multiply by normalized attribute scores, and sum to produce a final score per strategy. |

### 2. Extract qualitative constraints from the summary_note (e.g., licensing limits, computational budget) and apply adjustment factors to the raw scores.

| Category | Details |
| --- | --- |
| **Reason** | The summary note may contain critical non‑numeric considerations that should influence the final ranking. |
| **Impact** | Produces scores that reflect both quantitative data and business‑level constraints, reducing the risk of selecting infeasible strategies. |
| **Complexity** | MEDIUM |
| **Method** | Implement simple keyword‑based parsing or use a lightweight NLP library (e.g., spaCy) to detect constraint phrases and modify scores with predefined multipliers. |

### 3. Serialize the computed scores dictionary to a JSON string and bundle it with the original inputs for traceability.

| Category | Details |
| --- | --- |
| **Reason** | Downstream nodes expect a stringified dict and often need the raw inputs for debugging or logging. |
| **Impact** | Guarantees a consistent payload format and makes the shim’s operation auditable. |
| **Complexity** | LOW |
| **Method** | Use Python's json.dumps to convert the scores dict; ensure all input parameters are cast to strings before returning them in the response object. |
