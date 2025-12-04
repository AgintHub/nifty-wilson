# identify_trading_indicators PRD

## Description
Derives a curated set of quantitative technical indicators and/or price‑action signals that concretely instantiate the previously chosen trading‑strategy type.


## Implementation Plan

### 1. Extract the `strategy_type` string from the output of the parent node `select_trading_strategy_type` and normalize it to lower‑case, trimming whitespace.

| Category | Details |
| --- | --- |
| **Reason** | Normalization eliminates case‑sensitivity and formatting mismatches, ensuring deterministic mapping to indicator sets. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use Python's `str.lower().strip()`; store the result in a variable `strategy_type_norm`. |

### 2. Define a static, version‑controlled lookup table (dictionary) that maps each supported `strategy_type` to a pre‑vetted list of technical indicators or signal formulas.

| Category | Details |
| --- | --- |
| **Reason** | A deterministic lookup guarantees reproducibility, facilitates auditability, and allows domain‑expert curation of indicator sets per strategy. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Create a Python dict, e.g., `INDICATOR_MAP = {"momentum": ["RSI", "MACD", "ADX"], "mean reversion": ["Bollinger Bands", "Stochastic Oscillator"], "trend following": ["EMA_50", "EMA_200", "ATR"], "breakout": ["Donchian Channel", "Volume Spike"]}`. Keep the dict in a separate JSON/YAML file for easy updates. |

### 3. Lookup the normalized `strategy_type_norm` in the `INDICATOR_MAP`. If the key is missing, raise a clear validation error indicating unsupported strategy type.

| Category | Details |
| --- | --- |
| **Reason** | Explicit error handling prevents silent failures and informs upstream nodes or operators about mis‑configurations. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use `indicators_raw = INDICATOR_MAP.get(strategy_type_norm)`; if `indicators_raw is None`, return an error message and halt execution. |

### 4. De‑duplicate the retrieved indicator list while preserving original order to respect any implied priority.

| Category | Details |
| --- | --- |
| **Reason** | Duplicate entries can cause redundant calculations downstream and distort `indicator_count`. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Iterate over `indicators_raw` and append to a new list only if the indicator is not already present; alternatively, use `list(dict.fromkeys(indicators_raw))`. |

### 5. Validate each indicator name against a master registry of supported indicator identifiers (e.g., a set of strings used by the `develop_trading_signal_logic` implementation). Remove any unsupported names and log warnings.

| Category | Details |
| --- | --- |
| **Reason** | Ensures downstream signal‑logic node receives only computable indicators, avoiding runtime errors. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Load `SUPPORTED_INDICATORS = {"RSI", "MACD", "ADX", "Bollinger Bands", "Stochastic Oscillator", "EMA_50", "EMA_200", "ATR", "Donchian Channel", "Volume Spike"}`; filter with a list comprehension: `indicators = [i for i in deduped if i in SUPPORTED_INDICATORS]`; collect any removed items into a log. |

### 6. Compute `indicator_count` as the length of the final `indicators` list.

| Category | Details |
| --- | --- |
| **Reason** | Provides an explicit numeric summary required by the output schema and useful for downstream sanity checks. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Set `indicator_count = len(indicators)`. |

### 7. Package the results into the prescribed output structure: a JSON object with keys `indicators` (list of strings) and `indicator_count` (integer), then return it to the workflow engine.

| Category | Details |
| --- | --- |
| **Reason** | Conforms to the node's contract, enabling downstream nodes to consume the data without transformation. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Return `{"indicators": indicators, "indicator_count": indicator_count}`; ensure the order matches the original lookup order. |
