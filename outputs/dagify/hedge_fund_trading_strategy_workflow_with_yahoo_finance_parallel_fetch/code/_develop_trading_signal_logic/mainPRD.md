# _develop_trading_signal_logic - Complete PRD Documentation

## Overview
PRDs for nodes in the '_develop_trading_signal_logic' module.

## Table of Contents

- [fetch_parent_indicators](#fetch_parent_indicators)

- [deduplicate_indicators](#deduplicate_indicators)

- [create_indicator_definitions_registry](#create_indicator_definitions_registry)

- [validate_indicators_exist](#validate_indicators_exist)

- [define_buy_rule](#define_buy_rule)

- [define_sell_rule](#define_sell_rule)

- [define_hold_rule](#define_hold_rule)

- [assemble_signal_logic_steps](#assemble_signal_logic_steps)

- [generate_summary](#generate_summary)

- [compute_logic_completeness](#compute_logic_completeness)

- [handle_signal_logic_generation_error](#handle_signal_logic_generation_error)



---

## fetch_parent_indicators

### Description
Fetches and returns the list of technical indicator names from the parent node's output provided as a JSON string.

### Implementation Plan

#### 1. Parse the `input_data` string as JSON and extract the `indicators` array.

| Category | Details |
| --- | --- |
| **Reason** | The parent node supplies its output as a serialized JSON string; the shim must deserialize it to obtain raw data. |
| **Impact** | Provides downstream nodes with a correctly typed list of indicator names, enabling further processing. |
| **Complexity** | LOW |
| **Method** | Use Python's `json.loads` to deserialize; handle `JSONDecodeError` and raise a clear exception if parsing fails. |

#### 2. Validate that the extracted `indicators` field is a list of strings and remove any non‑string entries.

| Category | Details |
| --- | --- |
| **Reason** | Ensures type safety and prevents downstream logic from encountering unexpected data types. |
| **Impact** | Reduces runtime errors in later nodes that assume a clean list of indicator names. |
| **Complexity** | MEDIUM |
| **Method** | Iterate over the list, keep items where `isinstance(item, str)`, and raise a `ValueError` if the resulting list is empty after filtering. |

#### 3. Support both pure JSON output and Pydantic model `json()` strings by attempting JSON parsing first and falling back to Pydantic's `parse_raw` if needed.

| Category | Details |
| --- | --- |
| **Reason** | Different upstream implementations may serialize the model differently; flexible handling improves robustness. |
| **Impact** | Allows the shim to operate correctly across varied serialization formats without manual adjustments. |
| **Complexity** | MEDIUM |
| **Method** | Wrap the JSON parsing in a try/except; on failure, import the `IdentifyTradingIndicatorsOutput` model and call `IdentifyTradingIndicatorsOutput.parse_raw(input_data)` to obtain the object, then extract `indicators`. |


---

## deduplicate_indicators

### Description
Removes duplicate indicator names from the input list while preserving their original order.

### Implementation Plan

#### 1. Implement order‑preserving deduplication by iterating through the list and adding unseen items to the result.

| Category | Details |
| --- | --- |
| **Reason** | The downstream trading‑logic nodes require a unique set of indicators but must respect the order defined by the user or upstream node. |
| **Impact** | Prevents redundant processing of the same indicator and ensures deterministic rule generation. |
| **Complexity** | LOW |
| **Method** | Loop over the input list, maintain a `seen` set, and append an item to the output list only if it is not already in `seen`. |

#### 2. Normalize and clean each indicator string (trim whitespace, handle case‑insensitivity) before duplicate checking while returning the original casing of the first occurrence.

| Category | Details |
| --- | --- |
| **Reason** | User‑provided indicator names may contain extra spaces or varied casing, leading to false negatives in duplicate detection. |
| **Impact** | Improves robustness, avoids accidental duplicates, and maintains user‑intended naming conventions. |
| **Complexity** | MEDIUM |
| **Method** | Strip whitespace with `str.strip()`, compare using a lower‑cased version for membership in `seen`, but store the original string in the output list. |

#### 3. Validate input type and raise a clear `TypeError` if the provided `indicators` argument is not a list of strings.

| Category | Details |
| --- | --- |
| **Reason** | Early validation catches programming errors and provides actionable feedback to developers. |
| **Impact** | Reduces runtime exceptions later in the pipeline and simplifies debugging. |
| **Complexity** | LOW |
| **Method** | Use `isinstance(indicators, list)` and `all(isinstance(i, str) for i in indicators)` checks; raise `TypeError` with an explanatory message on failure. |


---

## create_indicator_definitions_registry

### Description
Generates a dictionary (as a JSON‑encoded string) that maps each technical indicator name to its full definition metadata for downstream trading‑signal logic.

### Implementation Plan

#### 1. Design a fixed schema for each indicator definition (e.g., description, parameters, formula, usage).

| Category | Details |
| --- | --- |
| **Reason** | A consistent schema ensures downstream nodes can reliably parse and utilise the definitions without bespoke handling for each indicator. |
| **Impact** | Enables uniform access to indicator metadata, reducing runtime errors and simplifying validation logic in later stages. |
| **Complexity** | LOW |
| **Method** | Define a Python TypedDict or Pydantic BaseModel named `IndicatorDefinition` with the required fields and use it to type‑check entries. |

#### 2. Populate the registry with a curated set of common technical indicators (e.g., SMA, EMA, RSI, MACD, Bollinger Bands).

| Category | Details |
| --- | --- |
| **Reason** | Providing out‑of‑the‑box definitions covers the majority of use‑cases and accelerates development of signal logic. |
| **Impact** | Developers can immediately reference these indicators; missing entries can be added later without breaking existing logic. |
| **Complexity** | MEDIUM |
| **Method** | Create a hard‑coded dictionary mapping indicator names to `IndicatorDefinition` instances; optionally load additional definitions from a JSON/YAML file to allow easy extension. |

#### 3. Implement validation to guarantee that each definition contains all required keys and that parameter specifications are well‑formed.

| Category | Details |
| --- | --- |
| **Reason** | Invalid or incomplete definitions could cause runtime failures when computing indicator values or generating rules. |
| **Impact** | Early detection of definition errors improves robustness and provides clear feedback to developers adding new indicators. |
| **Complexity** | MEDIUM |
| **Method** | Iterate over the registry after construction, using Pydantic's `parse_obj` or a custom validator function to check each entry; raise a descriptive exception if validation fails. |


---

## validate_indicators_exist

### Description
Ensures that every indicator supplied in the list has a matching entry in the definitions registry and raises a clear error for any missing items.

### Implementation Plan

#### 1. Parse the incoming `indicators` string into a list and verify each entry exists as a key in the `definitions` dictionary.

| Category | Details |
| --- | --- |
| **Reason** | The core responsibility of the shim is to catch mismatches between requested technical indicators and the available definition set before downstream logic runs. |
| **Impact** | Prevents downstream runtime errors and ensures that only supported indicators are used in signal generation. |
| **Complexity** | LOW |
| **Method** | Deserialize the `indicators` JSON‑encoded string (or split on commas), convert `definitions` from its JSON string to a Python dict, then iterate using a set‑based lookup for O(1) membership checks. |

#### 2. Collect any missing indicators and raise a descriptive `ValueError` that lists all absent items.

| Category | Details |
| --- | --- |
| **Reason** | Providing a comprehensive error message aids debugging and allows calling code to surface precise feedback to the user or orchestrator. |
| **Impact** | Immediate failure with clear diagnostics, avoiding partial or silent failures later in the pipeline. |
| **Complexity** | MEDIUM |
| **Method** | Accumulate missing names in a list during verification; if the list is non‑empty, format an error string and raise `ValueError` with that message. |

#### 3. Return a simple acknowledgment string (e.g., "OK") when all indicators are validated.

| Category | Details |
| --- | --- |
| **Reason** | The shim’s output contract expects a string field `output`; returning a constant confirms successful validation without altering downstream data structures. |
| **Impact** | Standardizes the node’s return shape, enabling downstream nodes to rely on the presence of the `output` field. |
| **Complexity** | LOW |
| **Method** | After successful validation, set `output = "OK"` and return it as part of the shim’s response. |


---

## define_buy_rule

### Description
This shim defines the primary buy rule based on provided indicators and their definitions.

### Implementation Plan

#### 1. Implement rule generation logic based on indicator definitions.

| Category | Details |
| --- | --- |
| **Reason** | To dynamically generate specific buy rules tailored to the trading strategy. |
| **Impact** | Allows the system to adapt to new strategies and indicators without requiring manual code changes. |
| **Complexity** | MEDIUM |
| **Method** | Use a template-based approach, where templates define the structure of the buy rule, and the indicator definitions fill in the parameters (values, thresholds, trigger conditions). This allows a level of configuration for the strategy to be more versatile. |

#### 2. Implement validation for buy rule.

| Category | Details |
| --- | --- |
| **Reason** | To provide a check to prevent the generated rules from causing critical errors. |
| **Impact** | Improve system resilience and provide more detailed insight if a problem occurs. |
| **Complexity** | MEDIUM |
| **Method** | Implement a validation procedure, based on checking for acceptable syntax/grammar of the rule and checking numerical values against allowable boundaries. |


---

## define_sell_rule

### Description
Generates a deterministic sell‑signal rule string based on provided indicator names and their technical definitions.

### Implementation Plan

#### 1. Parse and validate the `indicators` and `definitions` inputs, ensuring every indicator appears in the definitions map.

| Category | Details |
| --- | --- |
| **Reason** | Prevent runtime errors caused by missing or malformed definitions and guarantee that the rule can be built reliably. |
| **Impact** | Raises early, clear validation errors; downstream logic receives only verified data, improving robustness. |
| **Complexity** | MEDIUM |
| **Method** | Deserialize `definitions` from JSON, split `indicators` on commas, trim whitespace, then cross‑check each indicator against the dictionary; throw a custom `InvalidIndicatorError` on mismatch. |

#### 2. Translate each indicator into a logical predicate using its definition and combine them into a cohesive sell‑rule expression.

| Category | Details |
| --- | --- |
| **Reason** | The core purpose of the shim is to turn raw technical specifications into an executable decision clause. |
| **Impact** | Produces a deterministic, readable rule (e.g., "IF RSI > 70 AND MACD < 0 THEN SELL") that can be consumed by downstream trading‑engine nodes. |
| **Complexity** | HIGH |
| **Method** | Iterate over the ordered indicator list, fetch its definition, apply a template engine (e.g., Jinja2) to render each predicate, then join predicates with logical operators defined in a configurable strategy (default AND). |

#### 3. Validate the final rule string for syntactic correctness and return it in the `output` field.

| Category | Details |
| --- | --- |
| **Reason** | Even a correctly assembled string may contain syntax errors (unbalanced brackets, missing operators) that would break execution later. |
| **Impact** | Ensures that the downstream `assemble_signal_logic_steps` receives a rule that can be parsed/executed without failure. |
| **Complexity** | LOW |
| **Method** | Run a lightweight grammar check using a regular expression or a simple parser library (e.g., `pyparsing`) to confirm the rule follows the pattern "IF <condition> THEN SELL"; if validation passes, assign to `output`, else raise `RuleSyntaxError`. |


---

## define_hold_rule

### Description
Generates a textual rule that defines the neutral/hold condition for the trading signal logic.

### Implementation Plan

#### 1. Design a generic hold‑rule template that mirrors the structure of the BUY and SELL rule strings.

| Category | Details |
| --- | --- |
| **Reason** | Ensures consistency across all rule definitions and simplifies downstream parsing. |
| **Impact** | Creates a uniform output format that downstream nodes can reliably consume. |
| **Complexity** | LOW |
| **Method** | Define a Python f‑string or format string such as "IF {conditions} THEN HOLD" and store it as a constant. |

#### 2. Incorporate any indicator‑specific neutral conditions into the template when applicable.

| Category | Details |
| --- | --- |
| **Reason** | Some indicators have explicit neutral zones (e.g., RSI between 40‑60) that should be reflected in the hold rule. |
| **Impact** | Improves the fidelity of the trading logic by accurately capturing when no action should be taken. |
| **Complexity** | MEDIUM |
| **Method** | Iterate over the list of used indicators, consult a predefined mapping of neutral thresholds, and dynamically inject those conditions into the template. |

#### 3. Validate the final hold‑rule string for syntactic correctness and completeness.

| Category | Details |
| --- | --- |
| **Reason** | Downstream execution engines expect well‑formed logical expressions; malformed rules could cause runtime failures. |
| **Impact** | Prevents errors during signal evaluation and guarantees that the rule can be parsed or compiled. |
| **Complexity** | MEDIUM |
| **Method** | Use a simple parser or regular‑expression check to confirm that the rule contains a valid IF‑THEN structure and that all referenced indicators exist in the definitions registry. |


---

## assemble_signal_logic_steps

### Description
Assembles the BUY, SELL, and HOLD rule strings into an ordered list of signal logic steps.

### Implementation Plan

#### 1. Validate and normalize each rule string to enforce consistent formatting and punctuation.

| Category | Details |
| --- | --- |
| **Reason** | Input rules may contain irregular whitespace, casing, or missing periods, which could cause downstream parsing errors. |
| **Impact** | Produces clean, uniform rule statements that downstream modules can reliably consume. |
| **Complexity** | LOW |
| **Method** | Trim leading/trailing whitespace, convert to sentence case, ensure each rule ends with a period using simple regex checks. |

#### 2. Concatenate the validated rules into a deterministic ordered list reflecting the decision priority (BUY → SELL → HOLD).

| Category | Details |
| --- | --- |
| **Reason** | The overall logic must preserve the intended execution order to correctly represent the trading strategy. |
| **Impact** | Creates a clear, sequential representation that can be rendered in documentation or fed into execution engines. |
| **Complexity** | MEDIUM |
| **Method** | Build a list [buy_rule, sell_rule, hold_rule]; optionally prefix each entry with a step identifier (e.g., "Step 1:") and verify no duplicate entries. |

#### 3. Return the assembled list under the 'output' field while also returning the original rule strings for traceability.

| Category | Details |
| --- | --- |
| **Reason** | Consumers may need both the aggregated list and the individual rule texts for auditing or debugging purposes. |
| **Impact** | Ensures transparency and facilitates troubleshooting without requiring additional data retrieval steps. |
| **Complexity** | LOW |
| **Method** | Construct a dictionary matching the output_structure; assign the ordered list to the 'output' key and include buy_rule, sell_rule, and hold_rule unchanged. |


---

## generate_summary

### Description
Generates a concise executive summary describing the trading methodology based on provided indicators and logic steps

### Implementation Plan

#### 1. Validate and normalize the `indicators` and `logic_steps` inputs.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the shim receives well‑formed data and prevents downstream formatting errors. |
| **Impact** | Reduces runtime failures and guarantees consistent prompt construction. |
| **Complexity** | LOW |
| **Method** | Strip whitespace, join list inputs into a single comma‑separated string, and escape any special characters that could break the prompt template. |

#### 2. Construct a deterministic prompt that injects the normalized inputs into a predefined summary template.

| Category | Details |
| --- | --- |
| **Reason** | A stable prompt yields reproducible, high‑quality summaries from the language model. |
| **Impact** | Improves reliability of the generated summary and makes unit‑testing straightforward. |
| **Complexity** | MEDIUM |
| **Method** | Use Python f‑strings or Jinja2 templating to embed `{{indicators}}` and `{{logic_steps}}` into the prompt defined above, then send the prompt to the LLM via the existing inference client. |

#### 3. Post‑process the LLM response to enforce length limits and plain‑text output.

| Category | Details |
| --- | --- |
| **Reason** | Consumers of the summary expect a succinct, unformatted string without markdown or extra whitespace. |
| **Impact** | Guarantees downstream nodes receive a clean, predictable summary string. |
| **Complexity** | LOW |
| **Method** | Trim the response, truncate to 150 words if necessary, and strip any surrounding markdown markers before returning the `output` field. |


---

## compute_logic_completeness

### Description
Evaluates whether the signal logic fully accounts for every identified indicator and provides complete decision pathways.

### Implementation Plan

#### 1. Parse and normalize the three input strings into ordered sets of indicator names.

| Category | Details |
| --- | --- |
| **Reason** | Consistent data structures are required to compare coverage accurately. |
| **Impact** | Ensures that whitespace, case, or ordering differences do not cause false negatives in completeness checks. |
| **Complexity** | LOW |
| **Method** | Split each string on commas, trim whitespace, convert to lower‑case, and store in Python sets. |

#### 2. Validate that every parent indicator appears in the used_indicators set.

| Category | Details |
| --- | --- |
| **Reason** | The core definition of completeness is that no identified indicator is omitted from the logic. |
| **Impact** | Detects missing indicators early, allowing downstream nodes to flag or abort the workflow. |
| **Complexity** | MEDIUM |
| **Method** | Compute the set difference parent_indicators − used_indicators; if non‑empty, mark completeness as False. |

#### 3. Inspect signal_logic_steps to confirm explicit BUY, SELL, and NEUTRAL branches for each used indicator.

| Category | Details |
| --- | --- |
| **Reason** | A logic file may list indicators but still lack decision rules for some of them. |
| **Impact** | Guarantees that the algorithm can generate actionable signals for every indicator, preventing runtime gaps. |
| **Complexity** | HIGH |
| **Method** | If signal_logic_steps is JSON, deserialize it and verify that for each indicator there is at least one rule object containing a 'decision' field with values 'BUY', 'SELL', or 'HOLD'; otherwise, perform regex search for keywords (buy|sell|hold) linked to each indicator. |


---

## handle_signal_logic_generation_error

### Description
Formats, logs, and returns a user‑friendly message when an exception occurs during trading signal logic generation.

### Implementation Plan

#### 1. Extract the exception type, message, and stack trace, then compose a single‑line, standardized error string.

| Category | Details |
| --- | --- |
| **Reason** | Downstream components need a consistent error format for reporting and potential automated handling. |
| **Impact** | Ensures uniform error visibility across the pipeline and simplifies downstream parsing. |
| **Complexity** | LOW |
| **Method** | Use Python's traceback module to capture stack info; concatenate exception class name and message into a formatted string. |

#### 2. Write the formatted error string to the application logger with severity set to ERROR.

| Category | Details |
| --- | --- |
| **Reason** | Persistent logging is required for operational monitoring, debugging, and audit trails. |
| **Impact** | Facilitates rapid issue diagnosis by DevOps and maintains a record of failures in log aggregation systems. |
| **Complexity** | LOW |
| **Method** | Leverage the standard logging library (logging.getLogger) configured with appropriate handlers; call logger.error(formatted_message). |

#### 3. Return the formatted error string as the shim's `output` field while also exposing the original error via the `error` field.

| Category | Details |
| --- | --- |
| **Reason** | Upstream nodes may need to display a user‑friendly message, whereas downstream logic might still require the raw error for conditional branching. |
| **Impact** | Provides both a clean message for end‑users and the raw error for programmatic decision making. |
| **Complexity** | MEDIUM |
| **Method** | Create a dataclass or simple dict containing both keys; ensure the function signature matches the declared output_structure. |
