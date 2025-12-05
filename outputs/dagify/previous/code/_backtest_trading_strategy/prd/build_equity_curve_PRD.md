# build_equity_curve PRD

## Description
Generates a daily equity‑curve pandas Series by combining cash balances, holdings positions, and price data for the backtest simulation.


## Implementation Plan

### 1. Deserialize the three input strings into pandas Series/DataFrames with matching datetime indices.

| Category | Details |
| --- | --- |
| **Reason** | The backtest engine passes data as serialized strings; they must be converted back to pandas objects for arithmetic. |
| **Impact** | Ensures subsequent calculations operate on correctly typed, index‑aligned data, preventing shape mismatches. |
| **Complexity** | MEDIUM |
| **Method** | Use json.loads or pd.read_json / pd.read_csv depending on the chosen serialization format; enforce UTC timezone and forward‑fill missing dates to create a unified index. |

### 2. Compute the equity curve as cash + (holdings × price) for each date.

| Category | Details |
| --- | --- |
| **Reason** | The equity curve reflects total portfolio value, which is the sum of liquid cash and market value of positions. |
| **Impact** | Produces the core performance metric required for downstream analytics such as returns, Sharpe, and drawdown. |
| **Complexity** | LOW |
| **Method** | Perform element‑wise multiplication of the holdings Series with the price Series, add the cash Series, and store the result as a new pandas Series. |

### 3. Handle edge cases (NaNs, mis‑aligned indices, zero‑division) and serialize the resulting Series back to a string.

| Category | Details |
| --- | --- |
| **Reason** | Real‑world data may contain missing values or mismatched dates; robust handling prevents runtime failures and preserves data integrity. |
| **Impact** | Guarantees that the shim always returns a valid, consumable equity curve string, even when input data is imperfect. |
| **Complexity** | MEDIUM |
| **Method** | Apply .fillna(method='ffill').fillna(0) to the intermediate Series, verify index alignment with .reindex, then serialize using Series.to_json(orient='split') or to_csv with index=True. |
