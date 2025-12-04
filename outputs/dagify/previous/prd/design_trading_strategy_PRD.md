# design_trading_strategy PRD

## Description
Formulates the trading strategy logic.


## Implementation Plan

### 1. 1️⃣ Load parent outputs: parse `compute_statistics` JSON, `generate_features` CSV, and `perform_pairwise_correlation` CSV into in‑memory data structures (e.g., Python dictionaries and Pandas DataFrames).

| Category | Details |
| --- | --- |
| **Reason** | All strategy logic depends on the statistical summaries, moving averages, and rolling correlation values. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use `json.load` for statistics; `pandas.read_csv` for CSVs; ensure date columns are parsed as datetime objects. |

### 2. 2️⃣ Compute the spread series as the difference between META_Close and GOOGL_Close, aligning on dates and dropping any NaNs resulting from feature lagging.

| Category | Details |
| --- | --- |
| **Reason** | Statistical arbitrage often relies on mean‑reverting spreads; the spread informs entry/exit thresholds. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Add a new column `Spread = META_Close - GOOGL_Close` in the merged DataFrame. |

### 3. 3️⃣ Calculate the 10‑day SMA of the spread (`Spread_SMA_10`) and its 5‑day standard deviation (`Spread_Std_5`) to establish a dynamic mean‑reversion band.

| Category | Details |
| --- | --- |
| **Reason** | Using spread‑based moving averages allows the strategy to adapt to changing volatility. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Apply `df['Spread_SMA_10'] = df['Spread'].rolling(window=10).mean()` and `df['Spread_Std_5'] = df['Spread'].rolling(window=5).std()`. |

### 4. 4️⃣ Define entry conditions: go long Meta and short Google when the spread falls below `Spread_SMA_10 - 2 * Spread_Std_5` **and** the 20‑day rolling correlation `META_GOOGL_RollingCorr_20` is above 0.7.

| Category | Details |
| --- | --- |
| **Reason** | A deep negative deviation indicates a potential over‑short Google relative to Meta; a high correlation ensures the pair moves together. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use boolean masks: `(df['Spread'] < df['Spread_SMA_10'] - 2*df['Spread_Std_5']) & (df['META_GOOGL_RollingCorr_20'] > 0.7)`. |

### 5. 5️⃣ Define exit conditions: close positions when the spread crosses the `Spread_SMA_10` line (i.e., becomes greater than `Spread_SMA_10`) or when the correlation drops below 0.5, whichever occurs first.

| Category | Details |
| --- | --- |
| **Reason** | Crossing the moving average signals a return to normal levels; a falling correlation suggests the pair may diverge. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Create an exit mask: `(df['Spread'] > df['Spread_SMA_10']) | (df['META_GOOGL_RollingCorr_20'] < 0.5)`. |

### 6. 6️⃣ Specify a conservative position‑sizing rule: allocate 10% of available capital per trade, divided equally between Meta and Google (long/short), ensuring the notional values match to maintain a market‑neutral hedge.

| Category | Details |
| --- | --- |
| **Reason** | Risk‑controlled sizing limits exposure while preserving the arbitrage trade’s hedge. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Define `PositionSizeRule = '10% of capital per trade, split equally between long Meta and short Google; ensure dollar neutrality.'` |

### 7. 7️⃣ Construct the final JSON object with four fields (`StrategyName`, `EntryRule`, `ExitRule`, `PositionSizeRule`) using descriptive yet concise language suitable for downstream backtesting.

| Category | Details |
| --- | --- |
| **Reason** | The backtest node expects a JSON with these exact keys; clarity reduces downstream errors. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use `json.dumps` with sorted keys: `{"StrategyName":..., "EntryRule":..., "ExitRule":..., "PositionSizeRule":...}`. |

### 8. 8️⃣ Validate the JSON against the expected schema: confirm string types, non‑empty descriptions, and that no mandatory fields are omitted.

| Category | Details |
| --- | --- |
| **Reason** | Ensures downstream nodes receive correctly typed data and prevents runtime failures. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Perform a schema check: assert `isinstance(value, str)` for each field and that length > 0. |

### 9. 9️⃣ Log the generated strategy parameters and a brief summary (e.g., number of expected trades per month) to a debug log for traceability.

| Category | Details |
| --- | --- |
| **Reason** | Facilitates debugging if backtest results are unexpected; provides context for performance metrics. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Print or write to a file: `logging.info(f'Strategy {strategy_name} with {num_trades} expected trades/month')`. |
