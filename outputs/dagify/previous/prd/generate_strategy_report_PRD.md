# generate_strategy_report PRD

## Description
Creates the final written report of the strategy.


## Implementation Plan

### 1. Parse the JSON output from the design_trading_strategy node and confirm that the keys StrategyName, EntryRule, ExitRule, and PositionSizeRule are present. If any key is missing, log an error and substitute a placeholder "<undefined>".

| Category | Details |
| --- | --- |
| **Reason** | Ensures the strategy description can be reliably constructed and prevents downstream failures if upstream data is incomplete. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use Python's json.loads to deserialize; employ dict.get with default values and write to a log file if missing. |

### 2. Parse the JSON output from calculate_performance_metrics and validate the presence of cumulative_return, annualized_sharpe_ratio, maximum_drawdown, win_rate, and average_trade_duration. Normalize numeric values to two decimal places for presentation.

| Category | Details |
| --- | --- |
| **Reason** | Consistent numeric formatting improves readability and aligns with standard reporting conventions. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use json.loads and format numbers with f"{value:.2f}"; round maximum_drawdown and average_trade_duration to four decimal places to show precision. |

### 3. Construct a Markdown header using the StrategyName field, prefixed with "# ".

| Category | Details |
| --- | --- |
| **Reason** | A clear, top‑level heading immediately informs the reader of the strategy being reported. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | f"# {strategy_name}\n" |

### 4. Create a section titled "Strategy Description" that concatenates EntryRule, ExitRule, and PositionSizeRule into a single descriptive paragraph, using bullet points for clarity.

| Category | Details |
| --- | --- |
| **Reason** | Presents the trading logic in a concise yet comprehensive manner. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | f"## Strategy Description\n- **Entry Rule:** {entry}\n- **Exit Rule:** {exit}\n- **Position Size Rule:** {size}\n" |

### 5. Add a section "Key Statistical Insights" that lists the rolling correlation and moving average thresholds used, referencing the compute_statistics outputs for mean and standard deviation where relevant. Use a Markdown table with two columns: Insight and Value.

| Category | Details |
| --- | --- |
| **Reason** | Highlights the quantitative foundations of the strategy, linking back to the statistical analysis. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Build table strings: "| Insight | Value |\n|---|---|\n| Mean Meta Return | {meta_mean:.4f} |\n..."; extract values from compute_statistics JSON. |

### 6. Add a section "Backtest Performance Metrics" that presents the metrics in a Markdown table, labeling each metric and formatting numbers to two decimal places. Include a brief interpretive note after the table summarizing overall performance.

| Category | Details |
| --- | --- |
| **Reason** | Structured presentation allows quick comparison of metrics, and interpretive comments aid decision‑making. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Compose table with headers; compute win_rate as percentage; append a note: "The strategy achieved a cumulative return of X% with a Sharpe ratio of Y, indicating Z." |

### 7. Add a section "Recommendations for Next Steps" that suggests at least two actionable items (e.g., expand to include Nvidia, adjust correlation window) based on performance gaps identified in the metrics.

| Category | Details |
| --- | --- |
| **Reason** | Provides clear guidance for future development and iteration. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use conditional logic: if max_drawdown > 0.1, suggest risk‑management improvement; always recommend parameter sensitivity analysis. |

### 8. Concatenate all Markdown sections into a single string variable, ensuring proper spacing and newline characters to preserve formatting when rendered.

| Category | Details |
| --- | --- |
| **Reason** | A single string output is required by the node's output structure and ensures consistency across different renderers. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Join list of section strings with "\n\n". |

### 9. Return the final Markdown string as the value of the report_markdown output field, wrapped in a JSON object matching the defined output structure.

| Category | Details |
| --- | --- |
| **Reason** | Compliance with the node's contract ensures downstream nodes receive data in the expected format. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | json.dumps({'report_markdown': final_markdown}) |

### 10. Implement exception handling around JSON parsing and string formatting to capture and log any errors, returning a minimal placeholder report if processing fails.

| Category | Details |
| --- | --- |
| **Reason** | Robustness guarantees the workflow does not crash on malformed input and provides a graceful degradation path. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | try/except blocks, logging module, fallback string "# Strategy Report\n*Error generating report.*" |
