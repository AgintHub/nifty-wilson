# select_trading_strategy_type PRD

## Description
Determines the optimal primary trading strategy category based on the market analysis.


## Implementation Plan

### 1. Retrieve the complete output payload from the parent node **define_market_analysis**, specifically the three fields: `market_data_sources`, `analysis_techniques`, and `summary_note`.

| Category | Details |
| --- | --- |
| **Reason** | All subsequent decision logic relies on an accurate, unaltered view of the data ecosystem and analytical toolkit defined upstream. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Invoke the DAG runtime API to fetch the parent node's output JSON; deserialize into native Python structures (list of strings for sources and techniques, string for summary). |

### 2. Classify each entry in `market_data_sources` by data latency (real‑time vs end‑of‑day), granularity (tick, minute, daily), and asset class coverage (equities, futures, FX, commodities).

| Category | Details |
| --- | --- |
| **Reason** | Strategy feasibility is heavily driven by the timeliness and granularity of the underlying data; e.g., high‑frequency momentum requires sub‑second latency. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Define a static taxonomy dictionary mapping known providers (e.g., Bloomberg, Yahoo Finance) to their latency/granularity attributes; iterate over the list and build a structured summary dictionary. |

### 3. Map each technique listed in `analysis_techniques` to one or more canonical strategy archetypes using a pre‑defined mapping matrix (e.g., "Moving Average Crossover" → Momentum, "Bollinger Bands" → Mean Reversion, "Factor Model" → Statistical Arbitrage).

| Category | Details |
| --- | --- |
| **Reason** | Creating an explicit link between techniques and strategy families enables systematic scoring rather than ad‑hoc intuition. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Maintain a JSON‑encoded mapping table; for each technique, lookup corresponding archetype(s) and increment a counter in a `strategy_score` dict. |

### 4. Construct a weighted scoring model that evaluates candidate strategy types (`momentum`, `mean_reversion`, `stat_arbitrage`, `sentiment_driven`, etc.) on three axes: (1) Data Suitability (latency & granularity match), (2) Technique Alignment (count of mapped techniques), (3) Cost/Licensing Feasibility (derived from `summary_note` keywords such as "low cost" or "premium").

| Category | Details |
| --- | --- |
| **Reason** | A quantitative score reduces bias and provides a reproducible basis for selection. |
| **Impact** | HIGH |
| **Complexity** | HIGH |
| **Method** | Assign axis weights (e.g., 0.4, 0.4, 0.2). For each candidate, compute: data_score = sum(latency_match*weight_lat + granularity_match*weight_gran), technique_score = technique_counter * weight_tech, cost_score = 1 if summary_note contains low‑cost indicator else 0. Multiply by axis weights and sum to produce a final score. |

### 5. Select the strategy type with the highest aggregated score; in case of a tie, apply a deterministic tie‑breaker that prefers lower‑frequency strategies (to honor typical end‑of‑day data availability from Yahoo Finance).

| Category | Details |
| --- | --- |
| **Reason** | Ensures a single, repeatable output even when multiple strategies appear equally viable. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Sort the `strategy_score` dictionary by value descending; if multiple entries share the top score, order them by a predefined precedence list ["momentum", "mean_reversion", "stat_arbitrage", "sentiment_driven"]. |

### 6. Compose a one‑sentence `rationale` that references the most influential data source and the dominant analysis technique driving the decision (e.g., "Momentum is selected because the high‑frequency daily price feed from Bloomberg aligns with our Moving‑Average‑Crossover indicator set.")

| Category | Details |
| --- | --- |
| **Reason** | The rationale must be concise yet traceable to the underlying analysis, satisfying the output specification. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Identify the top‑scoring data source category and the highest‑frequency technique from the mapping; interpolate into a template string. |

### 7. Validate the final output payload against the declared `output_structure`: ensure `strategy_type` is a non‑empty string drawn from the allowed enumeration and `rationale` is a single‑sentence string (max 200 characters). Raise an error if validation fails.

| Category | Details |
| --- | --- |
| **Reason** | Guarantees downstream nodes receive well‑formed inputs and prevents silent propagation of errors. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Implement a lightweight schema validator (e.g., jsonschema) using the `output_structure` definition; assert string types and non‑emptiness; log descriptive error messages. |
