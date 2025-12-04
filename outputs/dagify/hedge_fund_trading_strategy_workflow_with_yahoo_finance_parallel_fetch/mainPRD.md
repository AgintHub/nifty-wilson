# hedge_fund_trading_strategy_workflow_with_yahoo_finance_parallel_fetch - Complete PRD Documentation

## Overview
PRDs for nodes in the 'hedge_fund_trading_strategy_workflow_with_yahoo_finance_parallel_fetch' module.

## Table of Contents

- [backtest_trading_strategy](#backtest_trading_strategy)

- [compile_final_strategy_blueprint](#compile_final_strategy_blueprint)

- [define_market_analysis](#define_market_analysis)

- [define_risk_management_rules](#define_risk_management_rules)

- [develop_trading_signal_logic](#develop_trading_signal_logic)

- [fetch_stock_data_yahoo_data](#fetch_stock_data_yahoo_data)

- [fetch_stock_data_yahoo_status](#fetch_stock_data_yahoo_status)

- [identify_trading_indicators](#identify_trading_indicators)

- [refine_trading_strategy](#refine_trading_strategy)

- [select_trading_strategy_type](#select_trading_strategy_type)

- [specify_asset_universe](#specify_asset_universe)



---

## backtest_trading_strategy

### Description
Performs a rigorous, production‑grade backtest of the fully specified trading strategy using the fetched Yahoo Finance data, the asset universe, and the signal generation logic.

### Implementation Plan

#### 1. Parse the CSV strings from **fetch_stock_data_yahoo_data** into pandas DataFrames, enforce UTC DatetimeIndex, and ensure columns are exactly ['Open','High','Low','Close','Adj Close','Volume'].

| Category | Details |
| --- | --- |
| **Reason** | Standardizing data format guarantees downstream calculations operate on a consistent schema and eliminates hidden timezone bugs. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use pandas.read_csv with StringIO, set parse_dates=True, date_parser=pd.to_datetime, tz='UTC'; validate column order with assert statements. |

#### 2. Create a master business‑day calendar covering the intersection of all ticker date ranges; reindex each ticker DataFrame onto this calendar, forward‑fill missing values, and drop leading rows with any NaN after alignment.

| Category | Details |
| --- | --- |
| **Reason** | Aligning on a common index is essential for accurate signal evaluation and portfolio aggregation across assets. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Determine min(max_start_date) and max(min_end_date) across tickers; generate pandas.bdate_range; for each DataFrame, df.reindex(master_index, method='ffill'); drop rows where any ticker still has NaN using df.dropna(how='any'). |

#### 3. Translate **develop_trading_signal_logic.signal_logic_steps** into an executable Python function that takes a unified DataFrame (rows=dates, columns=multi‑index ticker/field) and returns a DataFrame of position intents (+1 for long, -1 for short, 0 for flat) per ticker per day.

| Category | Details |
| --- | --- |
| **Reason** | A deterministic, vectorised signal function enables fast daily evaluation and facilitates later backtesting loops. |
| **Impact** | HIGH |
| **Complexity** | HIGH |
| **Method** | Parse the list of textual rules (e.g., "If SMA_20 > SMA_50 then BUY") into pandas boolean masks; combine masks per ticker; store results in a DataFrame called `signals` with same index as price data. |

#### 4. Implement an execution engine that iterates over the chronologically ordered dates, compares current positions to previous day's signals, generates trade orders, applies configurable commission (default 0.001 per trade) and slippage (default 0.0005 price offset), and updates cash and holdings accordingly.

| Category | Details |
| --- | --- |
| **Reason** | Simulating realistic trading costs and order execution is crucial for credible performance metrics. |
| **Impact** | HIGH |
| **Complexity** | HIGH |
| **Method** | Maintain variables: cash, holdings dict, portfolio_value series; for each date: identify changed signals, compute trade size = (available_capital * allocation_per_asset) / price; subtract commission = trade_size * commission_rate; adjust fill price = price * (1 + slippage * sign); update holdings and cash. |

#### 5. Construct the daily equity curve by summing cash plus market value of all holdings (position * close price) after each day's execution; store results in a pandas Series `equity_curve` indexed by date.

| Category | Details |
| --- | --- |
| **Reason** | The equity curve is the basis for all downstream performance statistics. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | equity_curve[date] = cash + sum(holdings[ticker] * close_price[ticker] for each ticker). |

#### 6. Calculate performance metrics: total_return = (final_equity / initial_capital) - 1; daily_returns = equity_curve.pct_change().dropna(); annualized_sharpe = sqrt(252) * mean(daily_returns) / std(daily_returns); max_drawdown = max( (peak - trough)/peak ) using a rolling max; number_of_trades = count of executed orders; backtest_period_start/end = first/last date of equity_curve.

| Category | Details |
| --- | --- |
| **Reason** | These metrics provide a standardized quantification of risk‑adjusted returns and trade activity. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Use numpy and pandas functions: np.sqrt(252), equity_curve.cummax() for drawdown calculation, and simple integer counter for trades. |

#### 7. Wrap the entire pipeline in a try/except block; on any exception set `success=False`, log the exception message to a dedicated log string, and populate output fields with NaN/zero defaults; otherwise set `success=True`.

| Category | Details |
| --- | --- |
| **Reason** | Robust error handling ensures the node returns a well‑defined output even when upstream data is malformed. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use Python's try: ... except Exception as e: success=False; log_message=str(e); assign default values; finally return the output dictionary. |


---

## compile_final_strategy_blueprint

### Description
Synthesizes the refined trading logic, rigorously defined risk‑management policies, and the designated asset universe into a single, end‑to‑end blueprint ready for implementation, back‑testing, and deployment.

### Implementation Plan

#### 1. Extract the full refined‑strategy payload from the **refine_trading_strategy** node – specifically the fields `refined_strategy_summary`, `parameter_adjustments`, `indicator_adjustments`, and `risk_rule_adjustments` – and concatenate them into a single, coherent technical description for `refined_strategy_details`.

| Category | Details |
| --- | --- |
| **Reason** | The refined strategy details must capture all final rule‑level changes (parameters, indicators, risk tweaks) in an easily readable format for developers and reviewers. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Parse each string field, strip any leading/trailing whitespace, and join sections using clear headings (e.g., "## Parameter Adjustments"). Ensure bullet‑point consistency by prefixing each adjustment with a dash. Preserve original numeric precision. |

#### 2. Read the `risk_management_rules` list from the **define_risk_management_rules** node and verify that the list length is between 3 and 5 items and that at least one rule contains the keyword "stop‑loss" (ensuring `has_stop_loss` is true).

| Category | Details |
| --- | --- |
| **Reason** | Compliance with the specification guarantees a disciplined risk‑control framework and satisfies downstream validation checks. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Iterate over the list, count elements, and perform a case‑insensitive search for the substring "stop‑loss". Raise a clear error message if constraints are violated. |

#### 3. Obtain the asset‑universe ticker list from the **specify_asset_universe** node – field `asset_tickers` – and assign it to the output field `asset_universe`.

| Category | Details |
| --- | --- |
| **Reason** | Although not a direct dependency in the DAG, the blueprint must expose the exact symbols that will be traded; pulling them from the asset‑universe node ensures source‑of‑truth consistency. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Reference the global execution context to read `asset_tickers`. Validate that each ticker is a non‑empty string and deduplicate any accidental repeats. |

#### 4. Craft the `blueprint_summary` string by merging (a) the strategic intent described in `refined_strategy_summary`, (b) the market thesis inferred from the chosen strategy type, and (c) quantitative targets (e.g., target annualized Sharpe > 1.5, max drawdown < 10%). Include a one‑sentence operational cadence (e.g., "Daily end‑of‑day signal generation and execution").

| Category | Details |
| --- | --- |
| **Reason** | Stakeholders need a concise executive overview that communicates why the strategy is pursued and what performance benchmarks are expected. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use a template:
```
[Strategy Name] – [Market Thesis]
Target Return‑to‑Risk: [target ratio]
Operational Cadence: [frequency]
```
Populate placeholders from the refined summary and, when necessary, from back‑test metrics (available upstream). |

#### 5. Generate an `Implementation Checklist` as a plain‑text bullet list (not part of the explicit output fields but useful for internal documentation) covering: data ingestion, signal computation, risk‑rule enforcement, order routing, position monitoring, logging, and periodic performance review.

| Category | Details |
| --- | --- |
| **Reason** | A checklist ensures that every component required for production deployment is accounted for and can be handed off to engineering teams. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Create a static list of 7‑8 items, each prefixed with "- ". Store it as an internal variable that can be optionally appended to the `blueprint_summary` if desired. |

#### 6. Validate final output types: ensure `blueprint_summary` and `refined_strategy_details` are strings, `risk_management_rules` is a list of strings, and `asset_universe` is a list of strings. Throw descriptive exceptions for any mismatch.

| Category | Details |
| --- | --- |
| **Reason** | Strict type compliance prevents downstream runtime errors and aligns with the platform's schema enforcement. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Perform isinstance checks; for list elements, iterate and assert isinstance(item, str). |

#### 7. Serialize the four output fields into the node's response JSON adhering exactly to the defined `output_structure` order.

| Category | Details |
| --- | --- |
| **Reason** | Correct serialization is required for the orchestration engine to route the data to subsequent nodes. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Construct a Python dict with keys matching the field names and feed it to the platform's `return` routine. |


---

## define_market_analysis

### Description
Develops a detailed blueprint of all external market data feeds and internal analytical methods that will be leveraged by the trading strategy.

### Implementation Plan

#### 1. Create an exhaustive inventory of all potential market data providers relevant to the intended asset classes (equities, futures, FX, macro‑economic indicators, alternative data).

| Category | Details |
| --- | --- |
| **Reason** | A complete provider list ensures no critical data source is overlooked, which could impair signal generation or risk assessment. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Conduct desk research using vendor documentation, industry surveys, and existing internal data catalogs; record provider name, URL, and contact details in a spreadsheet. |

#### 2. For each provider, classify the available data products into categories (e.g., real‑time quotes, end‑of‑day bars, fundamentals, news, sentiment, macro‑economics).

| Category | Details |
| --- | --- |
| **Reason** | Categorization allows downstream mapping of technique inputs to the correct data stream. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Create a matrix with rows = providers, columns = data categories; fill cells with yes/no and short notes on coverage. |

#### 3. Capture technical attributes for every data product: granularity (tick, 1‑min, daily), update latency (ms, seconds, minutes), delivery method (API, streaming, FTP), licensing model (subscription, per‑call, open‑source), and cost (USD per month or per request).

| Category | Details |
| --- | --- |
| **Reason** | These attributes directly affect feasibility, compliance, and budget planning. |
| **Impact** | HIGH |
| **Complexity** | HIGH |
| **Method** | Extract specifications from provider datasheets or API reference docs; store in a structured JSON schema for automated consumption. |

#### 4. Select the subset of providers and data products that satisfy the strategy’s requirements for coverage, latency, and budget, and document them as the final `market_data_sources` list.

| Category | Details |
| --- | --- |
| **Reason** | Only the chosen sources will be integrated into the pipeline; a curated list prevents scope creep. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Apply filter criteria (e.g., latency < 500 ms for high‑frequency, cost < $5000/month) on the attribute matrix; output provider names as a plain‑text list. |

#### 5. Identify analytical techniques needed to transform the selected data into actionable signals, spanning four families: statistical & technical indicators, machine‑learning models, sentiment & news analytics, and macro‑factor regressions.

| Category | Details |
| --- | --- |
| **Reason** | A taxonomy of techniques guides the development of the signal logic and ensures coverage of all information dimensions. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Review academic literature, industry white‑papers, and internal expertise; list each technique with a short definition. |

#### 6. For every technique, enumerate required inputs (specific data fields, look‑back windows, transformation steps), estimate computational complexity (O(N), O(N log N), or O(N^2)), and list software/library dependencies (e.g., NumPy, pandas‑ta, TensorFlow, spaCy).

| Category | Details |
| --- | --- |
| **Reason** | Explicit input‑dependency mapping prevents runtime failures and clarifies resource budgeting. |
| **Impact** | HIGH |
| **Complexity** | HIGH |
| **Method** | Create a per‑technique specification table: Technique | Inputs | Complexity | Dependencies; use Big‑O notation and tag required Python packages. |

#### 7. Consolidate the technique names into the `analysis_techniques` output list, preserving the same order as the specification table.

| Category | Details |
| --- | --- |
| **Reason** | A clean, ordered list is required by downstream nodes (identify_trading_indicators). |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Extract the ‘Technique’ column from the specification table and output as a List[str]. |

#### 8. Draft a concise `summary_note` that links each selected data source to the techniques that consume it, highlights any licensing constraints (e.g., redistribution limits), and provides an estimate of CPU/GPU resources needed for the full pipeline (e.g., 4‑core CPU, 16 GB RAM, optional GPU for deep‑learning models).

| Category | Details |
| --- | --- |
| **Reason** | The summary serves as a quick reference for architects and compliance officers and satisfies the node’s output requirement. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Use a templated paragraph: "Data source X provides Y (granularity Z) which feeds into technique A and B; licensing is …; anticipated compute per day is …"; ensure length < 500 words. |

#### 9. Validate that all three output fields conform to their declared PrimitiveTypes and that no duplicate entries exist in the lists.

| Category | Details |
| --- | --- |
| **Reason** | Strict type compliance avoids downstream schema violations and simplifies integration testing. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Run a Python validation script: assert isinstance(market_data_sources, list) and all(isinstance(s, str) for s in market_data_sources), similarly for analysis_techniques; ensure summary_note is a str. |

#### 10. Package the three outputs into the final JSON payload as defined in `output_structure` and return it to the orchestrator.

| Category | Details |
| --- | --- |
| **Reason** | Proper packaging completes the node’s contract with the workflow engine. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Construct a dictionary with keys 'market_data_sources', 'analysis_techniques', 'summary_note' and serialize with json.dumps() (if required by the platform). |


---

## define_risk_management_rules

### Description
Establishes a rigorous, quantitative risk‑management framework that translates the chosen trading strategy into actionable safeguards.

### Implementation Plan

#### 1. Extract the `strategy_type` string from the output of the parent node **select_trading_strategy_type** and normalize it to lower‑case for deterministic matching.

| Category | Details |
| --- | --- |
| **Reason** | A normalized strategy identifier eliminates case‑sensitivity bugs and enables reliable rule‑selection logic. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Read the JSON field `strategy_type`, apply `.strip().lower()`; store the result in a variable `strategy`. Raise a clear error if the field is missing or empty. |

#### 2. Create a static mapping dictionary where each possible `strategy_type` (e.g., "momentum", "mean reversion", "statistical arbitrage", "trend following") maps to a pre‑validated list of 3‑5 risk‑management rule templates.

| Category | Details |
| --- | --- |
| **Reason** | A deterministic mapping guarantees reproducible rule generation and aligns risk controls with the underlying tactical logic of each strategy. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Define a Python dict `RULE_TEMPLATES = { 'momentum': [ 'Limit position size to X% of portfolio equity per ticker.', 'Set a trailing stop‑loss at Y% below entry price.', 'Cap daily portfolio turnover at Z% of total equity.', 'Restrict maximum drawdown to D% of peak equity.', 'Allocate no more than N% of capital to any single sector.' ], ... }`. Ensure each list contains between 3 and 5 items and includes at least one stop‑loss rule. |

#### 3. Select the appropriate rule list from `RULE_TEMPLATES` using the normalized `strategy` key; if the key is absent, fall back to a generic baseline rule set and log a warning.

| Category | Details |
| --- | --- |
| **Reason** | Fallback handling prevents the workflow from failing for unexpected strategy strings while still providing sensible risk controls. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use `rules = RULE_TEMPLATES.get(strategy, RULE_TEMPLATES['generic'])`. Store the selected list in `selected_rules`. |

#### 4. Iterate over `selected_rules` and perform placeholder substitution for any strategy‑specific parameters (e.g., replace X, Y, Z, D, N with concrete numeric values derived from typical industry standards or configurable constants).

| Category | Details |
| --- | --- |
| **Reason** | Dynamic substitution turns abstract templates into actionable, concrete rules ready for downstream consumption. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Define a constants dict `DEFAULTS = { 'X': '2%', 'Y': '5%', 'Z': '15%', 'D': '10%', 'N': '20%' }`. For each rule string, replace each placeholder token using regex `re.sub(r'\bX\b', DEFAULTS['X'], rule)` etc. |

#### 5. Compute `rule_count` as `len(selected_rules)` and verify that it lies within the required range [3,5]; raise a validation exception if not.

| Category | Details |
| --- | --- |
| **Reason** | Enforcing the rule‑count constraint ensures compliance with the node's output contract and downstream expectations. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | If `rule_count < 3 or rule_count > 5`: `raise ValueError('Risk‑management rule count must be between 3 and 5.')`. |

#### 6. Determine `has_stop_loss` by scanning the finalized rule strings for the substring "stop‑loss" (case‑insensitive). Set the boolean accordingly.

| Category | Details |
| --- | --- |
| **Reason** | Explicit detection of a stop‑loss rule is required for the `has_stop_loss` output field. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | `has_stop_loss = any('stop-loss' in rule.lower() for rule in selected_rules)`. |

#### 7. Assemble the final output payload: `risk_management_rules` = `selected_rules` (preserve order), `rule_count` = computed integer, `has_stop_loss` = boolean flag; serialize to the expected JSON schema.

| Category | Details |
| --- | --- |
| **Reason** | A single, well‑structured payload enables downstream nodes (e.g., **compile_final_strategy_blueprint**) to consume the data without additional transformation. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Create a dict `{ 'risk_management_rules': selected_rules, 'rule_count': rule_count, 'has_stop_loss': has_stop_loss }` and return it as the node's response. |

#### 8. Log a concise human‑readable summary containing the selected strategy, the generated rules, `rule_count`, and `has_stop_loss` for auditability.

| Category | Details |
| --- | --- |
| **Reason** | Transparent logging aids debugging and provides traceability for compliance reviews. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use the platform logger: `logger.info(f"Strategy: {strategy}; Rules: {selected_rules}; Count: {rule_count}; Stop‑Loss present: {has_stop_loss}")`. |


---

## develop_trading_signal_logic

### Description
Transforms the set of technical indicators identified for the chosen strategy into a deterministic, production‑grade algorithm that emits precise buy and sell signals.

### Implementation Plan

#### 1. Fetch the `indicators` list from the output of the `identify_trading_indicators` node and store it in a local variable `parent_indicators`.

| Category | Details |
| --- | --- |
| **Reason** | Provides the authoritative source of which technical measures the strategy is allowed to use. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Execute a JSON read of the parent node's output; assert the field exists and is a non‑empty List[str]; raise a meaningful error if missing. |

#### 2. Deduplicate `parent_indicators` while preserving order and assign the result to `used_indicators`.

| Category | Details |
| --- | --- |
| **Reason** | Ensures deterministic behaviour and matches the required output field exactly. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Iterate through `parent_indicators`, add each unique entry to a new list; use a set for O(1) membership checks. |

#### 3. Create a registry (dictionary) named `indicator_definitions` that maps each indicator name to a pre‑defined calculation template, default parameters, and signal direction (e.g., bullish when value > threshold).

| Category | Details |
| --- | --- |
| **Reason** | Encapsulates domain expertise for each technical indicator, making later rule composition straightforward and auditable. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Populate the dictionary manually for common indicators (e.g., SMA, EMA, RSI, MACD, Bollinger Bands). Include keys: `calc_expression`, `lookback`, `upper_thresh`, `lower_thresh`, `type` (trend/momentum/volatility). |

#### 4. Validate that every entry in `used_indicators` exists in `indicator_definitions`; if any are missing, abort with a clear message listing unsupported indicators.

| Category | Details |
| --- | --- |
| **Reason** | Prevents runtime failures during back‑test when an undefined indicator would be referenced. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Loop over `used_indicators`; raise Exception if `indicator not in indicator_definitions`. |

#### 5. Define the primary BUY rule: combine one or more bullish conditions using logical AND/OR as dictated by typical strategy patterns (e.g., SMA_fast > SMA_slow AND RSI < 30).

| Category | Details |
| --- | --- |
| **Reason** | Establishes the core entry logic which must be explicit and deterministic. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | For each indicator, substitute its `calc_expression` into a templated condition string; concatenate conditions with `and`/`or` based on a configurable `combination_map` (hard‑coded for this PRD). |

#### 6. Define the primary SELL rule: mirror the BUY rule but with opposite (bearish) thresholds (e.g., SMA_fast < SMA_slow OR RSI > 70).

| Category | Details |
| --- | --- |
| **Reason** | Provides an equally clear exit logic, ensuring symmetric treatment of opposite market signals. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Reuse `indicator_definitions` with opposite threshold values; generate condition strings analogous to BUY rule. |

#### 7. Define a NEUTRAL/HOLD rule that activates when neither BUY nor SELL conditions are satisfied; this rule typically results in maintaining the current position.

| Category | Details |
| --- | --- |
| **Reason** | Guarantees that every possible market state maps to a deterministic output (BUY, SELL, or HOLD). |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Create a third step: `else: HOLD` and document it as a logical fallback. |

#### 8. Assemble the three rule strings into an ordered list `signal_logic_steps` following the sequence: 1) BUY condition, 2) SELL condition, 3) HOLD fallback.

| Category | Details |
| --- | --- |
| **Reason** | Matches the required output format and provides an intuitive, readable rule set for downstream consumption. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Create a List[str] where each element is a plain‑English description of the condition plus the action (e.g., "If SMA_20 > SMA_50 AND RSI < 30 → BUY"). |

#### 9. Generate the `summary` field: a concise paragraph (≤ 3 sentences) that outlines the overall methodology (indicator combination, hierarchy, risk overlay), key decision pathways (BUY → SELL → HOLD), and any built‑in risk‑management overlay (e.g., maximum exposure check).

| Category | Details |
| --- | --- |
| **Reason** | Provides stakeholders with a quick high‑level view of the signal engine without digging into the step list. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Compose a string using f‑string interpolation of the indicator set and rule count; mention deterministic nature and that all indicators are used. |

#### 10. Compute `is_logic_complete` as `True` only if (a) every indicator in `parent_indicators` appears in `used_indicators` and (b) BUY, SELL, and HOLD branches are all explicitly defined in `signal_logic_steps`; otherwise set to `False`.

| Category | Details |
| --- | --- |
| **Reason** | Explicitly signals to downstream nodes whether the signal definition is exhaustive, enabling error‑handling before back‑testing. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Boolean check: `all(i in used_indicators for i in parent_indicators) and len(signal_logic_steps) == 3`. |

#### 11. Package the four outputs (`signal_logic_steps`, `used_indicators`, `summary`, `is_logic_complete`) into a JSON object matching the declared `output_structure` and return it.

| Category | Details |
| --- | --- |
| **Reason** | Conforms to the workflow contract so that subsequent nodes can reliably consume the data. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Serialize the constructed Python dict using `json.dumps` with ensure_ascii=False; no extra fields. |

#### 12. Include defensive error handling: if any step fails (e.g., missing indicator definition, malformed parameter), raise a descriptive exception so that the orchestrator can capture the failure and mark downstream `success` flags accordingly.

| Category | Details |
| --- | --- |
| **Reason** | Improves robustness of the pipeline and aids debugging in production. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Wrap the entire generation logic in a try/except block; on exception, log the stack trace and re‑raise a custom `SignalLogicGenerationError`. |


---

## fetch_stock_data_yahoo_data

### Description
Downloads historical OHLCV data for each ticker in the asset universe and returns the raw ticker list, CSV‑encoded data strings, and per‑ticker record counts.

### Implementation Plan

#### 1. Extract the ordered list of ticker symbols from the output of the `specify_asset_universe` node (field `asset_tickers`).

| Category | Details |
| --- | --- |
| **Reason** | Provides the definitive source of symbols that the downstream strategy expects; ensures alignment with upstream decisions. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Read the parent node's JSON payload, validate that `asset_tickers` exists and is a non‑empty List[str]; raise a clear error if validation fails. |

#### 2. Validate the ticker list for duplicates and illegal characters (e.g., whitespace, commas).

| Category | Details |
| --- | --- |
| **Reason** | Duplicate or malformed tickers cause yfinance to raise errors or return ambiguous data, breaking downstream alignment. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Iterate over the list, strip whitespace, use a set to detect duplicates, and filter out any ticker that does not match the regex `^[A-Z\.\-]{1,10}$`. Preserve original order after cleaning. |

#### 3. Create a thread‑pool executor (e.g., `concurrent.futures.ThreadPoolExecutor`) sized to the number of CPU cores (or a configurable max workers) to fetch tickers in parallel while preserving order.

| Category | Details |
| --- | --- |
| **Reason** | Historical data for dozens of tickers can be fetched concurrently, reducing overall latency without overwhelming Yahoo Finance's rate limits. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Define a worker function `fetch_one(ticker)` that encapsulates the per‑ticker logic (next bullets). Submit all tickers to the executor, collect `Future` objects, and later re‑order results based on the original ticker list. |

#### 4. Inside `fetch_one(ticker)`, call `yfinance.download(ticker, period='max', interval='1d', auto_adjust=False, progress=False, threads=False)` to obtain a pandas DataFrame.

| Category | Details |
| --- | --- |
| **Reason** | Using `period='max'` guarantees the longest available history; disabling auto‑adjust preserves the raw OHLCV columns needed later. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Import `yfinance as yf`; invoke `df = yf.download(ticker, period='max', interval='1d', auto_adjust=False, progress=False, threads=False)`. |

#### 5. If the returned DataFrame is empty or `None`, log a warning, return an empty CSV string (`""`) and a record count of `0` for that ticker.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the output lists stay aligned with the input order even when a ticker has no data, allowing downstream nodes to handle missing data gracefully. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Check `if df is None or df.empty:`; use Python's `logging` module to emit a warning with the ticker name. |

#### 6. Force the DataFrame index to be a timezone‑aware `DatetimeIndex` in UTC.

| Category | Details |
| --- | --- |
| **Reason** | Downstream alignment on a common business‑day index assumes UTC; naive timestamps cause mismatches and subtle bugs in time‑series operations. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | If `df.index.tz` is `None`, apply `df.index = df.index.tz_localize('UTC')`; otherwise, convert with `df.index = df.index.tz_convert('UTC')`. |

#### 7. Standardize the column set to exactly `['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']` in that order.

| Category | Details |
| --- | --- |
| **Reason** | Consistent column ordering simplifies CSV generation and guarantees downstream parsers receive expected fields. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Define `required_cols = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']`. Reindex the DataFrame: `df = df.reindex(columns=required_cols)`. Missing columns will be filled with `NaN`; extra columns are dropped. |

#### 8. Sort the DataFrame by index ascending to guarantee chronological order.

| Category | Details |
| --- | --- |
| **Reason** | Chronological order is required for back‑testing calculations that assume forward progression of time. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Execute `df.sort_index(inplace=True)`. |

#### 9. Serialize the validated DataFrame to a CSV‑formatted string while preserving the index as the first column named `Date`.

| Category | Details |
| --- | --- |
| **Reason** | The downstream back‑test node expects CSV strings that include the date index for proper alignment. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use `io.StringIO()` as an in‑memory buffer: `buf = io.StringIO(); df.to_csv(buf, index=True, header=True, date_format='%Y-%m-%d'); csv_str = buf.getvalue(); buf.close()`. |

#### 10. Capture the record count as `len(df)` (number of trading days).

| Category | Details |
| --- | --- |
| **Reason** | Provides a quick sanity check for each ticker and is required for the `record_counts` output field. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Assign `record_count = int(df.shape[0])`. |

#### 11. Return a tuple `(ticker, csv_str, record_count)` from `fetch_one`; on exception, catch, log the exception, and return `(ticker, "", 0)`.

| Category | Details |
| --- | --- |
| **Reason** | Guarantees that the main thread can always assemble results in the original order, regardless of per‑ticker failures. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Wrap the logic in a `try/except Exception as e:` block; use `logging.error` to capture stack trace. |

#### 12. After all futures complete, reconstruct three ordered lists (`tickers_out`, `csv_out`, `counts_out`) by iterating over the original ticker order and pulling the corresponding tuple from the future results.

| Category | Details |
| --- | --- |
| **Reason** | ThreadPoolExecutor does not preserve submission order when retrieving results; explicit re‑ordering ensures deterministic output alignment. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Create a dict `result_map[ticker] = (csv_str, count)` inside the worker; after `as_completed`, fill the dict. Finally, for `t in original_tickers: tickers_out.append(t); csv_out.append(result_map[t][0]); counts_out.append(result_map[t][1])`. |

#### 13. Validate that the three output lists have identical lengths and that each element in `record_counts` is a non‑negative integer.

| Category | Details |
| --- | --- |
| **Reason** | Prevents schema violations before the node returns its payload, ensuring downstream type safety. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Assert `len(tickers_out) == len(csv_out) == len(counts_out)`; loop through `counts_out` to assert `isinstance(c, int) and c >= 0`. |

#### 14. Assemble the final JSON payload with keys `tickers`, `data_csv`, and `record_counts` using the three ordered lists.

| Category | Details |
| --- | --- |
| **Reason** | Matches the exact output structure required by downstream nodes and the system's type‑checking layer. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Return `{"tickers": tickers_out, "data_csv": csv_out, "record_counts": counts_out}`. |

#### 15. Implement a top‑level try/except around the entire orchestration to catch unexpected errors, log a fatal error, and raise a `RuntimeError` with a concise message.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that a failure surface is visible to the workflow engine, which can then trigger the companion `fetch_stock_data_yahoo_status` node for graceful degradation. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Wrap the main function body in `try: ... except Exception as e: logging.exception('fetch_stock_data_yahoo_data failed'); raise RuntimeError(str(e))`. |

#### 16. Add optional configuration parameters (environment variables or function arguments) for max workers, request timeout, and retry count, but default them to safe values (e.g., `max_workers = min(32, os.cpu_count() + 4)`).

| Category | Details |
| --- | --- |
| **Reason** | Provides flexibility for production deployments where rate‑limit handling or resource constraints differ. |
| **Impact** | LOW |
| **Complexity** | MEDIUM |
| **Method** | Read `os.getenv('YF_MAX_WORKERS')` and cast to int; pass to `ThreadPoolExecutor(max_workers=...)`. Use `requests.adapters.HTTPAdapter(max_retries=3)` if needed. |

#### 17. Document the module with a docstring that outlines the input expectations, output schema, and any side‑effects (e.g., network I/O, logging).

| Category | Details |
| --- | --- |
| **Reason** | Facilitates maintainability and future extensions by other developers. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Write a triple‑quoted string at the top of the Python file describing the function `fetch_stock_data_yahoo_data`. |


---

## fetch_stock_data_yahoo_status

### Description
Performs the same Yahoo Finance download and reports overall success flag and a concise human‑readable status message.

### Implementation Plan

#### 1. Extract the list of ticker symbols from the `specify_asset_universe` node's `asset_tickers` output and store it in a local variable `tickers` preserving order.

| Category | Details |
| --- | --- |
| **Reason** | The status node must operate on the exact same universe that the data‑download node consumes; using the upstream output guarantees consistency. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Read JSON payload from parent node, assign `tickers = parent_output['asset_tickers']`. |

#### 2. Initialize two tracking structures: `failed_tickers = []` to record any ticker that ultimately fails, and `success_flags = {}` (ticker → bool) to capture per‑ticker success.

| Category | Details |
| --- | --- |
| **Reason** | Explicit containers simplify later aggregation of overall success and enable detailed message construction. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use Python dictionaries/lists; e.g., `failed_tickers = []`, `success_flags = {ticker: False for ticker in tickers}`. |

#### 3. For each ticker in `tickers`, execute a retry loop with a maximum of three attempts. Use exponential back‑off delays of 1 s, 2 s, and 4 s between attempts.

| Category | Details |
| --- | --- |
| **Reason** | Network glitches or temporary API throttling are common; exponential back‑off reduces hammering the Yahoo Finance endpoint while maximizing chance of success. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | ```
import time, yfinance as yf
for ticker in tickers:
    attempt = 0
    while attempt < 3:
        try:
            df = yf.Ticker(ticker).history(period='max', auto_adjust=False)
            # Validate DataFrame (see next bullet)
            success_flags[ticker] = True
            break
        except Exception as e:
            attempt += 1
            if attempt < 3:
                time.sleep(2 ** (attempt - 1))  # 1, 2, 4 seconds
            else:
                failed_tickers.append(ticker)
``` |

#### 4. After a successful download, validate the DataFrame: ensure it is non‑empty, the index is a timezone‑aware `DatetimeIndex` in UTC, and columns exactly match `['Open','High','Low','Close','Adj Close','Volume']`. If validation fails, treat it as a download failure and trigger a retry.

| Category | Details |
| --- | --- |
| **Reason** | YFinance may return malformed frames (e.g., missing columns or naive timestamps) which would break downstream processing; early validation prevents silent corruption. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | ```
if df.empty:
    raise ValueError('Empty DataFrame')
if not isinstance(df.index, pd.DatetimeIndex) or df.index.tz is None:
    df = df.tz_localize('UTC')
expected_cols = ['Open','High','Low','Close','Adj Close','Volume']
if list(df.columns) != expected_cols:
    raise ValueError('Unexpected column set')
``` |

#### 5. Collect any exception messages for failed attempts to enrich the final status message (e.g., network timeout, HTTP 429, validation error).

| Category | Details |
| --- | --- |
| **Reason** | Providing concrete failure reasons improves observability for operators and aids debugging without altering the strict output schema. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Maintain a dict `error_details = {ticker: str(e)}` on the final failure path. |

#### 6. After processing all tickers, compute `retrieval_success` as `True` if `failed_tickers` is empty; otherwise `False`.

| Category | Details |
| --- | --- |
| **Reason** | The specification explicitly requires a boolean that reflects *all* tickers succeeding. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | `retrieval_success = len(failed_tickers) == 0` |

#### 7. Construct `retrieval_message`:
   - If `retrieval_success` is True → "All {N} tickers downloaded successfully."
   - If False → "Downloaded {S} of {N} tickers successfully; failures: {ticker1}, {ticker2} (see logs for details)."
   Include the count of successful tickers (`S = N - len(failed_tickers)`).

| Category | Details |
| --- | --- |
| **Reason** | A concise, human‑readable summary satisfies the output requirement while still conveying enough detail for downstream users. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | String formatting with f‑strings; optionally append a truncated list if >5 failures. |

#### 8. Return a JSON‑compatible dictionary containing exactly the two fields `retrieval_success` and `retrieval_message` in the order defined by the output structure.

| Category | Details |
| --- | --- |
| **Reason** | Strict adherence to the schema guarantees downstream nodes can deserialize the response without schema violations. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | ```
output = {
    "retrieval_success": retrieval_success,
    "retrieval_message": retrieval_message
}
print(json.dumps(output))
``` |


---

## identify_trading_indicators

### Description
Derives a curated set of quantitative technical indicators and/or price‑action signals that concretely instantiate the previously chosen trading‑strategy type.

### Implementation Plan

#### 1. Extract the `strategy_type` string from the output of the parent node `select_trading_strategy_type` and normalize it to lower‑case, trimming whitespace.

| Category | Details |
| --- | --- |
| **Reason** | Normalization eliminates case‑sensitivity and formatting mismatches, ensuring deterministic mapping to indicator sets. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use Python's `str.lower().strip()`; store the result in a variable `strategy_type_norm`. |

#### 2. Define a static, version‑controlled lookup table (dictionary) that maps each supported `strategy_type` to a pre‑vetted list of technical indicators or signal formulas.

| Category | Details |
| --- | --- |
| **Reason** | A deterministic lookup guarantees reproducibility, facilitates auditability, and allows domain‑expert curation of indicator sets per strategy. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Create a Python dict, e.g., `INDICATOR_MAP = {"momentum": ["RSI", "MACD", "ADX"], "mean reversion": ["Bollinger Bands", "Stochastic Oscillator"], "trend following": ["EMA_50", "EMA_200", "ATR"], "breakout": ["Donchian Channel", "Volume Spike"]}`. Keep the dict in a separate JSON/YAML file for easy updates. |

#### 3. Lookup the normalized `strategy_type_norm` in the `INDICATOR_MAP`. If the key is missing, raise a clear validation error indicating unsupported strategy type.

| Category | Details |
| --- | --- |
| **Reason** | Explicit error handling prevents silent failures and informs upstream nodes or operators about mis‑configurations. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use `indicators_raw = INDICATOR_MAP.get(strategy_type_norm)`; if `indicators_raw is None`, return an error message and halt execution. |

#### 4. De‑duplicate the retrieved indicator list while preserving original order to respect any implied priority.

| Category | Details |
| --- | --- |
| **Reason** | Duplicate entries can cause redundant calculations downstream and distort `indicator_count`. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Iterate over `indicators_raw` and append to a new list only if the indicator is not already present; alternatively, use `list(dict.fromkeys(indicators_raw))`. |

#### 5. Validate each indicator name against a master registry of supported indicator identifiers (e.g., a set of strings used by the `develop_trading_signal_logic` implementation). Remove any unsupported names and log warnings.

| Category | Details |
| --- | --- |
| **Reason** | Ensures downstream signal‑logic node receives only computable indicators, avoiding runtime errors. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Load `SUPPORTED_INDICATORS = {"RSI", "MACD", "ADX", "Bollinger Bands", "Stochastic Oscillator", "EMA_50", "EMA_200", "ATR", "Donchian Channel", "Volume Spike"}`; filter with a list comprehension: `indicators = [i for i in deduped if i in SUPPORTED_INDICATORS]`; collect any removed items into a log. |

#### 6. Compute `indicator_count` as the length of the final `indicators` list.

| Category | Details |
| --- | --- |
| **Reason** | Provides an explicit numeric summary required by the output schema and useful for downstream sanity checks. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Set `indicator_count = len(indicators)`. |

#### 7. Package the results into the prescribed output structure: a JSON object with keys `indicators` (list of strings) and `indicator_count` (integer), then return it to the workflow engine.

| Category | Details |
| --- | --- |
| **Reason** | Conforms to the node's contract, enabling downstream nodes to consume the data without transformation. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Return `{"indicators": indicators, "indicator_count": indicator_count}`; ensure the order matches the original lookup order. |


---

## refine_trading_strategy

### Description
Iteratively enhances the quantitative trading strategy by performing a data‑driven, statistically rigorous refinement cycle.

### Implementation Plan

#### 1. Load the backtest output JSON produced by `backtest_trading_strategy` and validate that `success` == true; if false, raise a controlled exception and abort refinement with a clear error message.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the refinement cycle only runs on a clean, error‑free backtest, preventing propagation of faulty data. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Parse JSON, check boolean flag, log detailed error using standard logging library; wrap in try/catch to capture parsing exceptions. |

#### 2. Extract core performance metrics: `total_return`, `annualized_sharpe_ratio`, `max_drawdown`, and `number_of_trades` from the backtest payload.

| Category | Details |
| --- | --- |
| **Reason** | These metrics are the quantitative basis for evaluating whether the strategy meets predefined investment objectives. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Map each field to a local variable; coerce types to float/int as defined in the schema; store in a metrics dictionary. |

#### 3. Define target thresholds for each metric (e.g., Sharpe ≥ 1.2, max_drawdown ≤ 0.15, total_return ≥ 0.10, trades between 30‑200) using a configurable JSON/YAML file so that thresholds can be tuned without code changes.

| Category | Details |
| --- | --- |
| **Reason** | Externalizing targets enables rapid experimentation and aligns the refinement logic with portfolio manager expectations. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Read `refinement_targets.yaml` via `pyyaml`; fallback to hard‑coded defaults if file missing; validate numeric ranges. |

#### 4. Compute a metric‑gap report by comparing each observed metric to its target, categorizing gaps as `PASS`, `MARGINAL` (within 5% of target), or `FAIL` (outside 5%). Store this classification for later decision logic.

| Category | Details |
| --- | --- |
| **Reason** | Provides a systematic way to prioritize which aspects of the strategy need adjustment. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Iterate over metric dictionary, calculate percent deviation, assign categorical label; output a `gap_report` dict. |

#### 5. Perform a one‑factor sensitivity analysis for each tunable parameter, indicator setting, and risk rule that was originally defined in `develop_trading_signal_logic` and `define_risk_management_rules`. For each factor, vary it ±10% (or a domain‑specific step) while holding others constant, re‑run a lightweight backtest simulation using the same price data (reuse the data preparation code from `backtest_trading_strategy` but skip CSV I/O). Capture the resulting metric changes.

| Category | Details |
| --- | --- |
| **Reason** | Quantifies how each individual lever influences performance, identifying high‑impact levers for adjustment. |
| **Impact** | HIGH |
| **Complexity** | HIGH |
| **Method** | Create a parameter grid; for each entry, clone the original strategy object, modify the single field, call a simplified backtest function (`simulate_backtest`) that returns the same metric set; store results in a DataFrame for analysis. |

#### 6. Rank all factors by their sensitivity score defined as the absolute change in Sharpe ratio multiplied by a weighting factor for drawdown and return (e.g., `score = |ΔSharpe| * 0.5 + |ΔReturn| * 0.3 + |ΔDrawdown| * 0.2`). Select the top‑3 factors where the metric gap is `FAIL` or `MARGINAL`.

| Category | Details |
| --- | --- |
| **Reason** | Focuses refinement effort on the most influential levers that can close the performance gaps. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Compute score per factor from sensitivity DataFrame, sort descending, filter by gap classification. |

#### 7. Generate concrete adjustment proposals for the selected factors: for parameters, propose the value that yielded the best Sharpe in the sensitivity sweep; for indicators, adjust period lengths or thresholds to the optimal values; for risk rules, tighten stop‑loss or modify position‑size scaling factor as indicated by the analysis.

| Category | Details |
| --- | --- |
| **Reason** | Provides data‑driven, actionable changes rather than heuristic guesses. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Extract the optimum value from the sensitivity DataFrame per factor; format as bullet strings: `- Parameter XYZ: 0.05 → 0.08`. |

#### 8. Compose `parameter_adjustments`, `indicator_adjustments`, and `risk_rule_adjustments` strings by concatenating the bullet points generated in the previous step, preserving the order: parameters → indicators → risk rules.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the output fields match the required schema and are human‑readable. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Join bullet list with newline characters; prepend a short header if desired (e.g., "Adjusted Parameters:"). |

#### 9. Draft `reasoning_for_adjustments` by linking each bullet to the specific metric gap it addresses and citing the sensitivity score that motivated the change. Use a structured paragraph format: "The Sharpe ratio fell short of the 1.2 target (observed 0.95). Sensitivity analysis showed that increasing the EMA period from 20 to 30 improved Sharpe by +0.18, therefore the period was adjusted...".

| Category | Details |
| --- | --- |
| **Reason** | Provides transparency and auditability for downstream stakeholders and for the next refinement iteration. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Iterate over adjustment bullets, retrieve corresponding gap and score from earlier dictionaries, concatenate explanatory sentences. |

#### 10. Assemble `refined_strategy_summary` that encapsulates the overall direction of the refinement: mention which metric gaps were closed, any remaining gaps, and a high‑level view of the new parameter/indicator/risk configuration.

| Category | Details |
| --- | --- |
| **Reason** | Serves as the executive‑level narrative for the downstream `compile_final_strategy_blueprint` node. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Summarize metric changes (e.g., "Sharpe improved from 0.95 to 1.14"), list the three key adjustments, and note any residual issues. |

#### 11. Validate that all output strings are non‑empty and conform to the expected primitive types; if any field is empty, raise a validation error before returning to enforce contract compliance.

| Category | Details |
| --- | --- |
| **Reason** | Guarantees downstream nodes receive well‑formed data and prevents silent failures. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Simple `if not field.strip(): raise ValueError` checks; unit‑test each output field. |


---

## select_trading_strategy_type

### Description
Determines the optimal primary trading strategy category based on the market analysis.

### Implementation Plan

#### 1. Retrieve the complete output payload from the parent node **define_market_analysis**, specifically the three fields: `market_data_sources`, `analysis_techniques`, and `summary_note`.

| Category | Details |
| --- | --- |
| **Reason** | All subsequent decision logic relies on an accurate, unaltered view of the data ecosystem and analytical toolkit defined upstream. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Invoke the DAG runtime API to fetch the parent node's output JSON; deserialize into native Python structures (list of strings for sources and techniques, string for summary). |

#### 2. Classify each entry in `market_data_sources` by data latency (real‑time vs end‑of‑day), granularity (tick, minute, daily), and asset class coverage (equities, futures, FX, commodities).

| Category | Details |
| --- | --- |
| **Reason** | Strategy feasibility is heavily driven by the timeliness and granularity of the underlying data; e.g., high‑frequency momentum requires sub‑second latency. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Define a static taxonomy dictionary mapping known providers (e.g., Bloomberg, Yahoo Finance) to their latency/granularity attributes; iterate over the list and build a structured summary dictionary. |

#### 3. Map each technique listed in `analysis_techniques` to one or more canonical strategy archetypes using a pre‑defined mapping matrix (e.g., "Moving Average Crossover" → Momentum, "Bollinger Bands" → Mean Reversion, "Factor Model" → Statistical Arbitrage).

| Category | Details |
| --- | --- |
| **Reason** | Creating an explicit link between techniques and strategy families enables systematic scoring rather than ad‑hoc intuition. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Maintain a JSON‑encoded mapping table; for each technique, lookup corresponding archetype(s) and increment a counter in a `strategy_score` dict. |

#### 4. Construct a weighted scoring model that evaluates candidate strategy types (`momentum`, `mean_reversion`, `stat_arbitrage`, `sentiment_driven`, etc.) on three axes: (1) Data Suitability (latency & granularity match), (2) Technique Alignment (count of mapped techniques), (3) Cost/Licensing Feasibility (derived from `summary_note` keywords such as "low cost" or "premium").

| Category | Details |
| --- | --- |
| **Reason** | A quantitative score reduces bias and provides a reproducible basis for selection. |
| **Impact** | HIGH |
| **Complexity** | HIGH |
| **Method** | Assign axis weights (e.g., 0.4, 0.4, 0.2). For each candidate, compute: data_score = sum(latency_match*weight_lat + granularity_match*weight_gran), technique_score = technique_counter * weight_tech, cost_score = 1 if summary_note contains low‑cost indicator else 0. Multiply by axis weights and sum to produce a final score. |

#### 5. Select the strategy type with the highest aggregated score; in case of a tie, apply a deterministic tie‑breaker that prefers lower‑frequency strategies (to honor typical end‑of‑day data availability from Yahoo Finance).

| Category | Details |
| --- | --- |
| **Reason** | Ensures a single, repeatable output even when multiple strategies appear equally viable. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Sort the `strategy_score` dictionary by value descending; if multiple entries share the top score, order them by a predefined precedence list ["momentum", "mean_reversion", "stat_arbitrage", "sentiment_driven"]. |

#### 6. Compose a one‑sentence `rationale` that references the most influential data source and the dominant analysis technique driving the decision (e.g., "Momentum is selected because the high‑frequency daily price feed from Bloomberg aligns with our Moving‑Average‑Crossover indicator set.")

| Category | Details |
| --- | --- |
| **Reason** | The rationale must be concise yet traceable to the underlying analysis, satisfying the output specification. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Identify the top‑scoring data source category and the highest‑frequency technique from the mapping; interpolate into a template string. |

#### 7. Validate the final output payload against the declared `output_structure`: ensure `strategy_type` is a non‑empty string drawn from the allowed enumeration and `rationale` is a single‑sentence string (max 200 characters). Raise an error if validation fails.

| Category | Details |
| --- | --- |
| **Reason** | Guarantees downstream nodes receive well‑formed inputs and prevents silent propagation of errors. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Implement a lightweight schema validator (e.g., jsonschema) using the `output_structure` definition; assert string types and non‑emptiness; log descriptive error messages. |


---

## specify_asset_universe

### Description
Defines the full investable universe that aligns with the selected trading strategy.

### Implementation Plan

#### 1. Extract the `strategy_type` string from the output of `select_trading_strategy_type` and store it in a local variable.

| Category | Details |
| --- | --- |
| **Reason** | The chosen strategy type is the sole deterministic input that drives the asset‑class mapping logic. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Parse the parent node JSON, read `strategy_type`, and validate that it is a non‑empty string. |

#### 2. Define a static mapping table that links each supported `strategy_type` to a prioritized list of compatible asset classes, based on quantitative finance literature and industry best‑practice (e.g., "momentum" → ["US equities", "ETF futures"], "mean reversion" → ["US equities", "FX spot"], "stat‑arb" → ["US equities", "ETFs", "Options"]).

| Category | Details |
| --- | --- |
| **Reason** | A deterministic mapping ensures reproducibility and removes ambiguity when selecting asset classes. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Create a Python dict or JSON object; include comments citing sources such as academic papers or Bloomberg research for each mapping. |

#### 3. Lookup the extracted `strategy_type` in the mapping table; if not found, raise a clear validation error indicating an unsupported strategy.

| Category | Details |
| --- | --- |
| **Reason** | Fail‑fast validation prevents downstream errors in back‑testing caused by mismatched asset universes. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use a try/except block; error message should include the invalid `strategy_type` and list of supported keys. |

#### 4. For each selected asset class, apply a rule‑based ticker selection algorithm: 
- US equities → top 100 liquid stocks by average daily dollar volume from the last 6 months (e.g., S&P 500 constituents + high‑cap mid‑caps). 
- Futures → front‑month continuous contracts for major indices, commodities, and FX (e.g., ES, CL, GC, EUR=, JPY=). 
- ETFs → sector‑specific ETFs that best capture the factor exposure (e.g., XLK for tech momentum). 
- Commodities → physically deliverable contracts with sufficient liquidity (e.g., WTI, Gold).

| Category | Details |
| --- | --- |
| **Reason** | Rule‑based selection guarantees that the tickers are both tradable and representative of the underlying asset class, aligning with the strategy’s signal generation requirements. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Implement helper functions that query a static whitelist (hard‑coded lists) or, if allowed, pull the latest constituents from a public API (e.g., Wikipedia S&P 500 table). Ensure each list is de‑duplicated and sorted alphabetically. |

#### 5. Validate each candidate ticker symbol for syntactic correctness (uppercase, alphanumeric, optional suffix for futures contracts) and verify that it exists on Yahoo Finance via a lightweight `yfinance.Ticker(ticker).info` call; filter out any symbols that raise an exception or return empty info.

| Category | Details |
| --- | --- |
| **Reason** | Early validation avoids runtime failures in downstream data‑fetch nodes (`fetch_stock_data_yahoo_data`). |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Iterate over the candidate list, perform a try/except around `ticker.info['regularMarketPrice']`; keep only successful symbols. Log any excluded tickers for audit. |

#### 6. Assemble the final `asset_classes` list (derived from the mapping step) and the `asset_tickers` list (the validated, de‑duplicated ticker symbols). Preserve the order: asset classes first as they appear in the mapping, tickers sorted alphabetically within each class.

| Category | Details |
| --- | --- |
| **Reason** | Consistent ordering simplifies downstream indexing and debugging, especially when aligning tickers with fetched data frames. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Create two Python lists; use `sorted()` for tickers; concatenate class‑specific ticker sub‑lists if needed. |

#### 7. Return a JSON object conforming exactly to the defined `output_structure`: `asset_classes` as a List[str] and `asset_tickers` as a List[str]. Include a top‑level `success` flag in logs (not part of the schema) to indicate whether the universe generation completed without errors.

| Category | Details |
| --- | --- |
| **Reason** | Strict adherence to the schema guarantees compatibility with downstream nodes that consume these fields. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Serialize the two lists using `json.dumps` ensuring no extra fields are present; raise an exception only if serialization fails. |
