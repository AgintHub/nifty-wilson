# _select_trading_strategy_type - Complete PRD Documentation

## Overview
PRDs for nodes in the '_select_trading_strategy_type' module.

## Table of Contents

- [classify_market_data_sources](#classify_market_data_sources)

- [map_techniques_to_archetypes](#map_techniques_to_archetypes)

- [compute_strategy_scores](#compute_strategy_scores)

- [select_top_strategy_with_tiebreaker](#select_top_strategy_with_tiebreaker)

- [generate_strategy_rationale](#generate_strategy_rationale)

- [validate_output_payload](#validate_output_payload)



---

## classify_market_data_sources

### Description
Classifies a list of market data sources into categories such as latency, granularity, and asset‑class coverage.

### Implementation Plan

#### 1. Create a static lookup table that maps known data providers to their typical latency, granularity, and asset‑class coverage.

| Category | Details |
| --- | --- |
| **Reason** | The downstream strategy scoring relies on accurate, pre‑defined characteristics for each source. |
| **Impact** | Enables deterministic classification and reduces the need for external API calls at runtime. |
| **Complexity** | MEDIUM |
| **Method** | Define a Python dictionary (or JSON file) keyed by provider name; populate it with curated metadata from documentation or industry resources; load it lazily within the shim. |

#### 2. Parse the incoming `sources` string, validate each entry, and apply fallback logic for unknown providers.

| Category | Details |
| --- | --- |
| **Reason** | Inputs may come in various formats or include unregistered sources; robust handling prevents crashes later in the pipeline. |
| **Impact** | Ensures the shim always returns a well‑formed classification map, improving reliability of downstream nodes. |
| **Complexity** | LOW |
| **Method** | Use `json.loads` to convert the string to a list; iterate over items, lookup in the static table, and for missing entries assign a default classification (e.g., latency: "unknown", granularity: "unknown", asset_classes: []). |

#### 3. Serialize the resulting classification dictionary back to a JSON string for the `output` field.

| Category | Details |
| --- | --- |
| **Reason** | Downstream nodes expect a string payload; JSON provides a portable, language‑agnostic representation. |
| **Impact** | Standardizes data exchange format, facilitating easy deserialization by later nodes. |
| **Complexity** | LOW |
| **Method** | Use `json.dumps` with `ensure_ascii=False` to convert the dictionary to a string; optionally sort keys for deterministic output. |


---

## map_techniques_to_archetypes

### Description
Maps a list of analysis technique identifiers to their corresponding strategy archetype classifications.

### Implementation Plan

#### 1. Create a static lookup table that maps known analysis techniques to their corresponding strategy archetypes.

| Category | Details |
| --- | --- |
| **Reason** | A deterministic mapping ensures downstream strategy selection uses consistent archetype information. |
| **Impact** | Provides a reliable reference for translating techniques into strategy categories, reducing ambiguity in later scoring stages. |
| **Complexity** | MEDIUM |
| **Method** | Define a Python dictionary (or load from a YAML/JSON config) where keys are technique identifiers and values are archetype strings; support easy extension via external config files. |

#### 2. Validate the incoming techniques list against the lookup table and handle unknown entries gracefully.

| Category | Details |
| --- | --- |
| **Reason** | Input validation prevents runtime errors and ensures only supported techniques are processed. |
| **Impact** | Improves robustness of the pipeline by catching unsupported techniques early and providing clear error messages. |
| **Complexity** | LOW |
| **Method** | Parse the input string into a Python list (using json.loads), iterate over each technique, check presence in the lookup dictionary, and raise a descriptive ValueError for any missing keys. |

#### 3. Serialize the resulting technique‑to‑archetype mapping as a JSON string to match the expected output format.

| Category | Details |
| --- | --- |
| **Reason** | Downstream nodes expect the mapping payload as a stringified dictionary. |
| **Impact** | Ensures seamless data flow between nodes without type mismatches. |
| **Complexity** | LOW |
| **Method** | Construct a new dict containing only the validated techniques with their archetype values, then use json.dumps to produce the output string. |


---

## compute_strategy_scores

### Description
Generates a weighted score dictionary for candidate trading strategies using data classification, technique mapping, and the summary note.

### Implementation Plan

#### 1. Design a scoring matrix that assigns weights to each candidate strategy based on data classification attributes (latency, granularity, asset coverage) and technique mapping categories.

| Category | Details |
| --- | --- |
| **Reason** | A quantitative model is required to compare heterogeneous strategy candidates on a common scale. |
| **Impact** | Enables deterministic selection of the highest‑scoring strategy and provides transparency for downstream audit. |
| **Complexity** | MEDIUM |
| **Method** | Create a configurable dictionary of weight factors, multiply by normalized attribute scores, and sum to produce a final score per strategy. |

#### 2. Extract qualitative constraints from the summary_note (e.g., licensing limits, computational budget) and apply adjustment factors to the raw scores.

| Category | Details |
| --- | --- |
| **Reason** | The summary note may contain critical non‑numeric considerations that should influence the final ranking. |
| **Impact** | Produces scores that reflect both quantitative data and business‑level constraints, reducing the risk of selecting infeasible strategies. |
| **Complexity** | MEDIUM |
| **Method** | Implement simple keyword‑based parsing or use a lightweight NLP library (e.g., spaCy) to detect constraint phrases and modify scores with predefined multipliers. |

#### 3. Serialize the computed scores dictionary to a JSON string and bundle it with the original inputs for traceability.

| Category | Details |
| --- | --- |
| **Reason** | Downstream nodes expect a stringified dict and often need the raw inputs for debugging or logging. |
| **Impact** | Guarantees a consistent payload format and makes the shim’s operation auditable. |
| **Complexity** | LOW |
| **Method** | Use Python's json.dumps to convert the scores dict; ensure all input parameters are cast to strings before returning them in the response object. |


---

## select_top_strategy_with_tiebreaker

### Description
Selects the highest‑scoring trading strategy from a scores dictionary and applies a deterministic tie‑breaker when scores are equal.

### Implementation Plan

#### 1. Parse the input JSON string into a Python dict of {strategy: score}.

| Category | Details |
| --- | --- |
| **Reason** | The function receives scores as a string, so it must be converted to a usable data structure. |
| **Impact** | Enables subsequent numeric comparisons and provides clear error handling for malformed input. |
| **Complexity** | LOW |
| **Method** | Use json.loads with try/except to catch JSONDecodeError and raise a descriptive exception. |

#### 2. Identify the maximum score and collect all strategies that share this score.

| Category | Details |
| --- | --- |
| **Reason** | Multiple strategies may have identical top scores, requiring a tie‑breaker. |
| **Impact** | Ensures all candidate strategies are considered before applying deterministic selection. |
| **Complexity** | MEDIUM |
| **Method** | Iterate over the dict values to find max_score, then build a list comprehension of strategies where score == max_score. |

#### 3. Apply a deterministic tie‑breaking rule (alphabetical order) and return the chosen strategy as a string.

| Category | Details |
| --- | --- |
| **Reason** | A consistent rule guarantees reproducible results across runs and environments. |
| **Impact** | Provides a single, predictable output even when ties occur, satisfying downstream node expectations. |
| **Complexity** | LOW |
| **Method** | If the tie list has more than one element, use sorted(tie_list)[0]; otherwise return the sole element. |


---

## generate_strategy_rationale

### Description
Generates a concise rationale explaining why the selected trading strategy is optimal given the data classification and technique mapping.

### Implementation Plan

#### 1. Parse and validate the three input strings (selected_strategy, data_classification, technique_mapping) ensuring they are present and non‑empty.

| Category | Details |
| --- | --- |
| **Reason** | Invalid or missing inputs would cause downstream errors and produce nonsensical rationales. |
| **Impact** | Prevents runtime failures and guarantees that the rationale is based on reliable data. |
| **Complexity** | LOW |
| **Method** | Implement simple conditional checks; raise a ValueError with a clear message if any input is missing or empty. |

#### 2. Construct the rationale using a rule‑based template that incorporates the dominant factors extracted from data_classification and technique_mapping.

| Category | Details |
| --- | --- |
| **Reason** | A deterministic template ensures consistent, explainable output while still reflecting the key characteristics of the inputs. |
| **Impact** | Produces a human‑readable, context‑aware justification that can be audited or displayed to end users. |
| **Complexity** | MEDIUM |
| **Method** | Create a mapping of strategy types to template fragments; deserialize the JSON‑like strings, identify the most influential classification (e.g., low latency) and technique (e.g., sentiment analysis), and interpolate them into the template using Python f‑strings or the `format` method. |

#### 3. Return a dictionary containing the generated rationale as `output` together with the original input fields.

| Category | Details |
| --- | --- |
| **Reason** | The node contract expects both the rationale and the original context for downstream nodes. |
| **Impact** | Ensures downstream compatibility and allows other nodes to reuse the input data without recomputation. |
| **Complexity** | LOW |
| **Method** | Assemble the result dict with keys `output`, `selected_strategy`, `data_classification`, and `technique_mapping` and return it. |


---

## validate_output_payload

### Description
Validates that the selected strategy type and its rationale conform to expected string formats and basic business rules before returning the payload.

### Implementation Plan

#### 1. Perform type checking to ensure both `strategy_type` and `rationale` are strings.

| Category | Details |
| --- | --- |
| **Reason** | The downstream Pydantic model expects string fields; type mismatches would raise runtime errors. |
| **Impact** | Prevents crashes and guarantees downstream schema compatibility. |
| **Complexity** | LOW |
| **Method** | Use `isinstance(value, str)` checks or leverage Python's `typing` module with `assert isinstance(..., str)`. |

#### 2. Enforce non‑empty and length constraints on the strings.

| Category | Details |
| --- | --- |
| **Reason** | Empty or overly long values provide no useful information and may violate business policies. |
| **Impact** | Improves data quality and ensures meaningful rationale is captured. |
| **Complexity** | MEDIUM |
| **Method** | Define minimum and maximum length constants and raise a `ValueError` if `len(value.strip())` falls outside the range. |

#### 3. Integrate the validation into a reusable utility that raises a standardized `ValidationError` on failure.

| Category | Details |
| --- | --- |
| **Reason** | A uniform error type simplifies error handling for calling nodes and centralises validation logic. |
| **Impact** | Consistent error reporting across the workflow and easier future extensions (e.g., adding more fields). |
| **Complexity** | MEDIUM |
| **Method** | Create a small Pydantic `BaseModel` with `strategy_type` and `rationale` fields, call `model.parse_obj(...)` inside the shim, and catch `pydantic.ValidationError` to re‑raise a custom exception. |
