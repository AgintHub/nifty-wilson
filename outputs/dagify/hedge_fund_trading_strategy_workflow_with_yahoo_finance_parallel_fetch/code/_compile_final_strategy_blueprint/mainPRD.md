# _compile_final_strategy_blueprint - Complete PRD Documentation

## Overview
PRDs for nodes in the '_compile_final_strategy_blueprint' module.

## Table of Contents

- [extract_and_concatenate_strategy_details](#extract_and_concatenate_strategy_details)

- [validate_risk_management_rules](#validate_risk_management_rules)

- [get_asset_universe_from_context](#get_asset_universe_from_context)

- [craft_blueprint_summary](#craft_blueprint_summary)

- [generate_implementation_checklist](#generate_implementation_checklist)

- [validate_output_types](#validate_output_types)



---

## extract_and_concatenate_strategy_details

### Description
Combines the refined strategy summary and all adjustment sections into a single, well‑formatted narrative string.

### Implementation Plan

#### 1. Concatenate the four input strings with section headings and line breaks to form a cohesive narrative.

| Category | Details |
| --- | --- |
| **Reason** | The downstream blueprint builder expects a single, human‑readable description that aggregates all refinement information. |
| **Impact** | Produces a clear, organized output that downstream nodes can embed directly into documentation and UI displays. |
| **Complexity** | LOW |
| **Method** | Implement a simple string‑formatting function using f‑strings or `str.join`, inserting headings like "Parameter Adjustments:" before each corresponding input. |

#### 2. Validate each input is a non‑empty string and raise a descriptive ValueError if any are missing or invalid.

| Category | Details |
| --- | --- |
| **Reason** | Ensures data integrity; downstream processing assumes all sections are present and prevents obscure failures later in the pipeline. |
| **Impact** | Early detection of malformed inputs, leading to faster debugging and more reliable pipeline execution. |
| **Complexity** | MEDIUM |
| **Method** | Add a helper validation routine that checks `isinstance(x, str) and x.strip()` for each argument; wrap the concatenation in a try/except block to surface errors clearly. |

#### 3. Enforce a maximum character length (e.g., 4000 chars) on the final output, truncating with an ellipsis if the limit is exceeded.

| Category | Details |
| --- | --- |
| **Reason** | The final blueprint may be stored or transmitted to services with token or payload limits. |
| **Impact** | Prevents downstream API calls from failing due to oversized payloads while preserving the most important information. |
| **Complexity** | MEDIUM |
| **Method** | After concatenation, compare `len(output)` to the limit; if exceeded, truncate each section proportionally or keep the leading portion and append "... (truncated)". |


---

## validate_risk_management_rules

### Description
Validates a list of risk‑management rules ensuring the correct count and mandatory stop‑loss inclusion, returning the sanitized list.

### Implementation Plan

#### 1. Parse the `rules` string into a Python list of trimmed rule strings.

| Category | Details |
| --- | --- |
| **Reason** | The shim receives rules as a raw string; converting to a list enables reliable validation and downstream processing. |
| **Impact** | Ensures consistent data type for further checks and prevents malformed inputs from propagating. |
| **Complexity** | LOW |
| **Method** | Use `json.loads` for JSON arrays; fallback to splitting on newlines; strip whitespace from each element. |

#### 2. Validate that the rule count is between 3 and 5 inclusive.

| Category | Details |
| --- | --- |
| **Reason** | Business logic requires a concise yet comprehensive set of risk controls. |
| **Impact** | Guarantees the strategy adheres to expected risk‑management granularity and prevents over‑/under‑specification. |
| **Complexity** | LOW |
| **Method** | Check `len(rules_list)`; raise `ValueError` with a clear message if out of bounds. |

#### 3. If `has_stop_loss` is true, confirm at least one rule mentions a stop‑loss and raise an error otherwise.

| Category | Details |
| --- | --- |
| **Reason** | A stop‑loss is a critical safety mechanism for the strategy; its absence when required is unacceptable. |
| **Impact** | Prevents deployment of strategies lacking essential protection, reducing potential losses. |
| **Complexity** | MEDIUM |
| **Method** | Normalize `has_stop_loss` to a boolean; search the list for case‑insensitive substrings like "stop‑loss" or "stop loss"; raise `ValueError` if not found. |


---

## get_asset_universe_from_context

### Description
Extracts the list of tradable asset identifiers from the execution context supplied to the node.

### Implementation Plan

#### 1. Read the asset universe from a well‑known key (e.g., `asset_universe`) within **kwargs** and return it directly.

| Category | Details |
| --- | --- |
| **Reason** | The downstream `compile_final_strategy_blueprint` node requires this list to build the final blueprint. |
| **Impact** | Provides a deterministic source of tradable symbols, preventing missing‑data errors later in the pipeline. |
| **Complexity** | LOW |
| **Method** | Implement a simple dictionary lookup: `asset_tickers = kwargs.get('asset_universe', [])`; if the key is absent, return an empty list or raise a clear exception. |

#### 2. Validate the extracted list to ensure all entries are non‑empty strings and that the list contains unique symbols.

| Category | Details |
| --- | --- |
| **Reason** | Invalid or duplicated tickers can cause back‑testing failures and inaccurate risk calculations. |
| **Impact** | Guarantees data integrity for all downstream components that iterate over the asset universe. |
| **Complexity** | MEDIUM |
| **Method** | Iterate over the list, strip whitespace, filter out falsy values, and use a `set` to detect duplicates; raise a `ValueError` with a helpful message if validation fails. |

#### 3. Accept flexible input formats (list, comma‑separated string, or JSON‑encoded string) and normalize them to a `List[str]`.

| Category | Details |
| --- | --- |
| **Reason** | Different upstream nodes or user‑provided contexts may supply the universe in varied representations. |
| **Impact** | Increases robustness and reduces coupling, allowing the shim to be reused across multiple workflows. |
| **Complexity** | MEDIUM |
| **Method** | Detect the type of the retrieved value: if `list`, use as‑is; if `str`, split on commas and strip spaces; if JSON‑parsable, `json.loads` to a list; then apply the validation logic from the previous bullet. |


---

## craft_blueprint_summary

### Description
Generates a high‑level narrative blueprint summary from a refined trading‑strategy summary.

### Implementation Plan

#### 1. Parse the incoming **strategy_summary** and extract key elements: purpose, market thesis, target return‑to‑risk ratio, and cadence.

| Category | Details |
| --- | --- |
| **Reason** | The blueprint summary must be grounded in the core concepts already defined by the refined strategy. |
| **Impact** | Ensures the generated summary is accurate, focused, and aligns with downstream documentation and stakeholder expectations. |
| **Complexity** | LOW |
| **Method** | Use simple string manipulation or a lightweight NLP library (e.g., spaCy) to identify sentences containing the required keywords and map them to the four target elements. |

#### 2. Compose a concise paragraph (2‑3 sentences) that weaves the extracted elements into a coherent narrative.

| Category | Details |
| --- | --- |
| **Reason** | The blueprint summary should be brief yet comprehensive, suitable for executive overviews and automated documentation pipelines. |
| **Impact** | Produces a standardized, human‑readable output that downstream nodes can embed without additional formatting. |
| **Complexity** | MEDIUM |
| **Method** | Leverage a templated string with placeholders for the four elements, optionally employing a language model call (e.g., OpenAI gpt‑3.5) with a deterministic temperature (0) to ensure reproducibility. |

#### 3. Validate that the final **output** is a non‑empty string and does not exceed 500 characters.

| Category | Details |
| --- | --- |
| **Reason** | Downstream nodes expect a short summary; overly long text could break UI components or exceed storage limits. |
| **Impact** | Guarantees compliance with system constraints and prevents runtime errors in later stages. |
| **Complexity** | LOW |
| **Method** | Implement a post‑generation check that trims whitespace, asserts length ≤ 500, and raises a clear exception if validation fails. |


---

## generate_implementation_checklist

### Description
Generates a list of checklist items documenting the steps required to implement the compiled trading strategy blueprint.

### Implementation Plan

#### 1. Create a predefined template of checklist entries that cover strategy deployment, data pipeline configuration, risk‑management integration, back‑testing validation, and ongoing monitoring.

| Category | Details |
| --- | --- |
| **Reason** | A consistent baseline ensures that every compiled blueprint includes essential implementation steps regardless of downstream variations. |
| **Impact** | Provides immediate, actionable guidance for engineers and quant analysts, reducing the risk of omitted critical tasks. |
| **Complexity** | LOW |
| **Method** | Define a constant Python list of strings; each entry is a concise imperative sentence. Return a copy of this list to avoid mutation. |

#### 2. Enhance the template dynamically by inspecting kwargs (e.g., asset_universe, risk_management_rules) and appending context‑specific items such as "Configure data feeds for [ticker]" or "Implement stop‑loss logic as defined in risk rules".

| Category | Details |
| --- | --- |
| **Reason** | Different strategies may require additional or specialized steps; dynamic augmentation keeps the checklist relevant without manual edits. |
| **Impact** | Tailors the documentation to the exact blueprint, improving clarity for implementation teams and reducing follow‑up clarification cycles. |
| **Complexity** | MEDIUM |
| **Method** | Iterate over known keys in kwargs; for each recognized key, format a checklist string and extend the base list. Use helper functions to keep the augmentation logic modular and testable. |


---

## validate_output_types

### Description
Ensures that the blueprint summary, refined strategy details, risk management rules, and asset universe are all strings, raising errors if any type mismatches are detected.

### Implementation Plan

#### 1. Implement runtime type checks for each argument using isinstance.

| Category | Details |
| --- | --- |
| **Reason** | The node must guarantee that downstream components receive correctly typed data to prevent runtime failures. |
| **Impact** | Prevents type‑related crashes later in the pipeline and provides early feedback to developers or users. |
| **Complexity** | LOW |
| **Method** | Create a dictionary mapping field names to values, iterate over it, and apply isinstance(value, str) for each; collect any mismatches. |

#### 2. Raise a detailed ValueError listing all fields with incorrect types.

| Category | Details |
| --- | --- |
| **Reason** | A single generic error makes debugging difficult; users need to know exactly which field is problematic. |
| **Impact** | Improves developer experience and speeds up troubleshooting by pinpointing the source of the type violation. |
| **Complexity** | LOW |
| **Method** | If mismatches are found, concatenate field names and expected/actual types into an error message and raise ValueError(message). |
