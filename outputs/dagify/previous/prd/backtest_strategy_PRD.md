# backtest_strategy PRD

## Description
Runs a backtest of the trading strategy defined in the Design Trading Strategy node over the dataset produced by Compute Daily Returns. The backtest simulates daily trading decisions, records every executed trade, and outputs the trade log as lists of dates, actions, shares, prices, and capital after each trade.


## Implementation Plan

### 1. Load the CSV produced by Compute Daily Returns and parse it into a Pandas DataFrame, ensuring the 'Date' column is parsed as a datetime object and sorted chronologically.

| Category | Details |
| --- | --- |
| **Reason** | The backtest must process data in date order; parsing dates correctly guarantees accurate rolling calculations. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use pd.read_csv(csv_file_path, parse_dates=['Date']) followed by df.sort_values('Date').reset_index(drop=True). |

### 2. Read the JSON output from Design Trading Strategy into a dictionary and extract the four rule strings: StrategyName, EntryRule, ExitRule, PositionSizeRule.

| Category | Details |
| --- | --- |
| **Reason** | The strategy logic is provided as human‑readable text; we need to capture it for subsequent parsing. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Deserialize the JSON using json.loads and assign each key to a variable. |

### 3. Implement a lightweight rule‑parser that transforms the EntryRule and ExitRule strings into executable Python lambda functions. The parser should handle simple boolean expressions such as 'META_Close > GOOGL_Close', 'rolling_corr < 0.5', and moving average crossovers.

| Category | Details |
| --- | --- |
| **Reason** | Directly evaluating the raw text is error‑prone; a parser ensures deterministic and safe rule evaluation. |
| **Impact** | HIGH |
| **Complexity** | HIGH |
| **Method** | Use regular expressions to extract operands and operators, construct a dictionary of allowed variables, and compile a lambda via eval in a restricted namespace. Example: lambda df, row: row['META_Close'] > row['GOOGL_Close']. |

### 4. Parse the PositionSizeRule string to determine the fraction of available capital to allocate per trade (e.g., 'Allocate 10% of capital'). Extract the numeric percentage using regex and convert it to a decimal.

| Category | Details |
| --- | --- |
| **Reason** | Accurate position sizing is critical for realistic backtesting outcomes. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Regex search for patterns like r'(?P<percent>\d+)%', then set position_fraction = int(percent)/100.0. |

### 5. Enrich the DataFrame with any rolling indicators referenced in the rules but not present in the CSV (e.g., 20‑day rolling correlation, 10‑day moving averages). Compute these using pandas’ rolling methods and merge the results into the DataFrame.

| Category | Details |
| --- | --- |
| **Reason** | The strategy may rely on these indicators; missing values would cause rule evaluation failures. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | For a 20‑day rolling correlation: df['rolling_corr'] = df['META_Close'].rolling(20).corr(df['GOOGL_Close']); for a 10‑day SMA: df['META_SMA_10'] = df['META_Close'].rolling(10).mean(). |

### 6. Initialize the backtest state: starting capital = 100,000, no open position, and empty lists for trade_dates, trade_actions, trade_shares, trade_prices, trade_capital_after.

| Category | Details |
| --- | --- |
| **Reason** | State variables are required to track capital, holdings, and trade history across the simulation loop. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Set capital = 100000.0; position_shares = 0; trade_dates = []; trade_actions = []; trade_shares = []; trade_prices = []; trade_capital_after = []. |

### 7. Iterate over the DataFrame row by row. At each date, first evaluate the EntryRule if no position is currently held. If the rule evaluates to True, compute the number of shares to purchase using the position fraction and the current closing price of the target asset.

| Category | Details |
| --- | --- |
| **Reason** | Entry decisions are contingent on the current market state and capital allocation. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use the compiled lambda: if entry_rule(df, row): shares_to_buy = floor((capital * position_fraction) / row['META_Close']); update capital and position_shares; record trade. |

### 8. After processing an entry, evaluate the ExitRule on each subsequent date if a position is open. If the rule evaluates to True, sell all shares at the current closing price, update capital, close the position, and record the exit trade.

| Category | Details |
| --- | --- |
| **Reason** | Exit logic closes trades and locks in profits or losses. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | If exit_rule(df, row): proceeds = position_shares * row['META_Close']; capital += proceeds; record trade with action 'Sell'; set position_shares = 0. |

### 9. After each trade (Buy or Sell), append the execution date (ISO string), action, shares, price, and updated capital to their respective output lists. Ensure that the lists maintain the chronological order of trades.

| Category | Details |
| --- | --- |
| **Reason** | Ordered logs are required by the output schema and for downstream performance calculation. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Append to lists using list.append() after each trade event. |

### 10. At the end of the loop, return the five lists (trade_dates, trade_actions, trade_shares, trade_prices, trade_capital_after) as the node’s output.

| Category | Details |
| --- | --- |
| **Reason** | These are the primitive type lists expected by downstream nodes. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Return a dictionary mapping each key to its list, e.g., {'trade_dates': trade_dates, ...}. |

### 11. Optionally generate a CSV file of the trade log for debugging or archival purposes. The CSV should have columns: Date, Action, Shares, Price, CapitalAfterTrade.

| Category | Details |
| --- | --- |
| **Reason** | Provides a human‑readable record of the backtest which can aid in verification and reporting. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Create a Pandas DataFrame from the output lists and use df.to_csv('backtest_trades.csv', index=False). |
