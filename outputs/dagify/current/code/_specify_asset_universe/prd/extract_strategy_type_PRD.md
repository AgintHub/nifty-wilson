# extract_strategy_type PRD

## Description
Extracts the strategy_type field from a SelectTradingStrategyTypeOutput object and returns it as a string.


## Implementation Plan

### 1. Parse the input_data JSON string into a Python object and safely retrieve the `strategy_type` attribute.

| Category | Details |
| --- | --- |
| **Reason** | The shim receives data as a raw string; parsing is required to access structured fields. |
| **Impact** | Ensures downstream nodes receive a clean, correctly‑typed strategy identifier. |
| **Complexity** | LOW |
| **Method** | Use `json.loads` to deserialize the string, then access `obj["strategy_type"]` with a fallback default or raise a clear ValueError if missing. |

### 2. Validate that the extracted strategy_type is a non‑empty string and belongs to an allowed set of strategy identifiers.

| Category | Details |
| --- | --- |
| **Reason** | Invalid or misspelled strategy types would break later mapping logic. |
| **Impact** | Prevents runtime errors in `create_strategy_asset_mapping` and improves overall pipeline robustness. |
| **Complexity** | MEDIUM |
| **Method** | Define an immutable list of supported strategies (e.g., ["momentum", "mean_reversion", "arbitrage"]). After extraction, check `isinstance(value, str) and value.strip() and value in SUPPORTED_STRATEGIES`; raise a custom `InvalidStrategyError` if the check fails. |
