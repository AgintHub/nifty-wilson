# compile_final_strategy_blueprint PRD

## Description
Synthesizes the refined trading logic, rigorously defined risk‑management policies, and the designated asset universe into a single, end‑to‑end blueprint ready for implementation, back‑testing, and deployment.


## Implementation Plan

### 1. Extract the full refined‑strategy payload from the **refine_trading_strategy** node – specifically the fields `refined_strategy_summary`, `parameter_adjustments`, `indicator_adjustments`, and `risk_rule_adjustments` – and concatenate them into a single, coherent technical description for `refined_strategy_details`.

| Category | Details |
| --- | --- |
| **Reason** | The refined strategy details must capture all final rule‑level changes (parameters, indicators, risk tweaks) in an easily readable format for developers and reviewers. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Parse each string field, strip any leading/trailing whitespace, and join sections using clear headings (e.g., "## Parameter Adjustments"). Ensure bullet‑point consistency by prefixing each adjustment with a dash. Preserve original numeric precision. |

### 2. Read the `risk_management_rules` list from the **define_risk_management_rules** node and verify that the list length is between 3 and 5 items and that at least one rule contains the keyword "stop‑loss" (ensuring `has_stop_loss` is true).

| Category | Details |
| --- | --- |
| **Reason** | Compliance with the specification guarantees a disciplined risk‑control framework and satisfies downstream validation checks. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Iterate over the list, count elements, and perform a case‑insensitive search for the substring "stop‑loss". Raise a clear error message if constraints are violated. |

### 3. Obtain the asset‑universe ticker list from the **specify_asset_universe** node – field `asset_tickers` – and assign it to the output field `asset_universe`.

| Category | Details |
| --- | --- |
| **Reason** | Although not a direct dependency in the DAG, the blueprint must expose the exact symbols that will be traded; pulling them from the asset‑universe node ensures source‑of‑truth consistency. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Reference the global execution context to read `asset_tickers`. Validate that each ticker is a non‑empty string and deduplicate any accidental repeats. |

### 4. Craft the `blueprint_summary` string by merging (a) the strategic intent described in `refined_strategy_summary`, (b) the market thesis inferred from the chosen strategy type, and (c) quantitative targets (e.g., target annualized Sharpe > 1.5, max drawdown < 10%). Include a one‑sentence operational cadence (e.g., "Daily end‑of‑day signal generation and execution").

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

### 5. Generate an `Implementation Checklist` as a plain‑text bullet list (not part of the explicit output fields but useful for internal documentation) covering: data ingestion, signal computation, risk‑rule enforcement, order routing, position monitoring, logging, and periodic performance review.

| Category | Details |
| --- | --- |
| **Reason** | A checklist ensures that every component required for production deployment is accounted for and can be handed off to engineering teams. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Create a static list of 7‑8 items, each prefixed with "- ". Store it as an internal variable that can be optionally appended to the `blueprint_summary` if desired. |

### 6. Validate final output types: ensure `blueprint_summary` and `refined_strategy_details` are strings, `risk_management_rules` is a list of strings, and `asset_universe` is a list of strings. Throw descriptive exceptions for any mismatch.

| Category | Details |
| --- | --- |
| **Reason** | Strict type compliance prevents downstream runtime errors and aligns with the platform's schema enforcement. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Perform isinstance checks; for list elements, iterate and assert isinstance(item, str). |

### 7. Serialize the four output fields into the node's response JSON adhering exactly to the defined `output_structure` order.

| Category | Details |
| --- | --- |
| **Reason** | Correct serialization is required for the orchestration engine to route the data to subsequent nodes. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Construct a Python dict with keys matching the field names and feed it to the platform's `return` routine. |
