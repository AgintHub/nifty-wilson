# generate_trading_signals PRD

## Description
Generates a DataFrame of trading signals by applying a user‑provided signal function to unified market data for the given tickers.


## Implementation Plan

### 1. Validate and deserialize inputs (unified_data, signal_function, tickers) ensuring they are correctly formatted and safe to execute.

| Category | Details |
| --- | --- |
| **Reason** | Pre‑emptively catches malformed data or unsafe code, avoiding runtime crashes during backtesting. |
| **Impact** | Provides early failure detection, improves robustness, and secures execution environment. |
| **Complexity** | MEDIUM |
| **Method** | Use `json.loads` or `ast.literal_eval` to parse `unified_data` and `tickers`; load `signal_function` via `importlib` or `exec` within a restricted namespace, and verify the resulting callable's signature. |

### 2. Apply the deserialized `signal_function` across the unified DataFrame to compute BUY/SELL/HOLD signals for each ticker.

| Category | Details |
| --- | --- |
| **Reason** | This is the core logic that translates market data into actionable trading decisions. |
| **Impact** | Generates the `signals_df` required by downstream backtest simulation, directly influencing strategy performance metrics. |
| **Complexity** | HIGH |
| **Method** | Iterate over rows with `DataFrame.apply` (axis=1) passing each row to the signal function, or vectorize the function if possible; ensure missing values are handled and output is aligned with the original ticker columns. |

### 3. Serialize the resulting signals DataFrame back to a string format suitable for downstream nodes.

| Category | Details |
| --- | --- |
| **Reason** | Downstream workflow components accept string representations, not raw pandas objects. |
| **Impact** | Enables seamless data passing between nodes without requiring in‑memory objects. |
| **Complexity** | LOW |
| **Method** | Convert the DataFrame to JSON (`df.to_json(orient='records')`) or CSV (`df.to_csv(index=False)`), and assign it to the `output` field. |
