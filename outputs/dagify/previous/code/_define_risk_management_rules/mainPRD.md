# _define_risk_management_rules - Complete PRD Documentation

## Overview
PRDs for nodes in the '_define_risk_management_rules' module.

## Table of Contents

- [normalize_strategy_type](#normalize_strategy_type)

- [create_rule_templates_mapping](#create_rule_templates_mapping)

- [select_rule_templates](#select_rule_templates)

- [substitute_rule_placeholders](#substitute_rule_placeholders)

- [validate_rule_count](#validate_rule_count)

- [detect_stop_loss_rule](#detect_stop_loss_rule)

- [log_rule_generation_summary](#log_rule_generation_summary)



---

## normalize_strategy_type

### Description
Normalizes a raw strategy_type string to a canonical lowercase identifier, handling synonyms, whitespace, and case variations.

### Implementation Plan

#### 1. Create a synonym dictionary mapping known aliases (e.g., "MOM", "mom", "momentum") to their canonical form.

| Category | Details |
| --- | --- |
| **Reason** | Users may provide strategy names in various abbreviations or capitalizations, and a deterministic mapping is required for downstream rule selection. |
| **Impact** | Ensures consistent strategy identification across the pipeline, preventing mismatches in rule templates. |
| **Complexity** | LOW |
| **Method** | Define a static Python dict `synonym_map` and perform a lookup after normalizing the input to lower‑case and stripping whitespace. |

#### 2. Sanitize the input by trimming leading/trailing whitespace and converting to lower case before lookup.

| Category | Details |
| --- | --- |
| **Reason** | Raw inputs often contain extra spaces or mixed‑case characters that would break direct dictionary matches. |
| **Impact** | Reduces false‑negative matches and eliminates the need for repetitive preprocessing elsewhere. |
| **Complexity** | LOW |
| **Method** | Apply `strategy_type.strip().lower()` prior to dictionary lookup; fallback to the stripped value if not found in the synonym map. |

#### 3. Validate the normalized result against an allow‑list of supported strategies and raise a clear error if unsupported.

| Category | Details |
| --- | --- |
| **Reason** | Downstream nodes assume a known set of strategy identifiers; an invalid value would cause cascade failures. |
| **Impact** | Provides early, descriptive failure feedback, improving debuggability and system robustness. |
| **Complexity** | MEDIUM |
| **Method** | Maintain a set `VALID_STRATEGIES`; after normalization, check membership and raise `ValueError` with a helpful message if absent. |


---

## create_rule_templates_mapping

### Description
Creates a static dictionary that maps each trading strategy type to a predefined list of risk‑management rule templates.

### Implementation Plan

#### 1. Define a hard‑coded dictionary that enumerates all supported strategy identifiers and their corresponding rule‑template lists.

| Category | Details |
| --- | --- |
| **Reason** | The rest of the workflow relies on a deterministic source of templates to generate concrete risk‑management rules. |
| **Impact** | Provides a single source of truth for rule selection, ensuring consistency across runs and simplifying downstream validation. |
| **Complexity** | LOW |
| **Method** | Create a Python dict literal inside the function; optionally load from a JSON/YAML file bundled with the package for easier future updates. |

#### 2. Normalize strategy identifiers (e.g., lowercase, replace spaces with underscores) to guarantee key‑lookup reliability.

| Category | Details |
| --- | --- |
| **Reason** | Input strategy names may come in varied formats; normalization prevents KeyError exceptions during template selection. |
| **Impact** | Improves robustness of `select_rule_templates` and reduces runtime errors caused by mismatched keys. |
| **Complexity** | MEDIUM |
| **Method** | Implement a helper `normalize_strategy_type` that applies `.strip().lower().replace(' ', '_')` and use its output as the dict key. |

#### 3. Include a fallback entry (e.g., "default") that provides a generic set of rule templates for unknown or new strategies.

| Category | Details |
| --- | --- |
| **Reason** | Future strategy types may be introduced before the mapping is updated, and the system must still produce a valid rule set. |
| **Impact** | Ensures graceful degradation, allowing the pipeline to continue operating while flagging the need for mapping expansion. |
| **Complexity** | LOW |
| **Method** | Add a "default" key in the dictionary and have `select_rule_templates` return its value when the normalized strategy is not found. |


---

## select_rule_templates

### Description
Selects and returns a list of rule template strings that correspond to the provided trading strategy.

### Implementation Plan

#### 1. Parse and validate the `templates` JSON string into a dictionary mapping strategy names to lists of rule strings.

| Category | Details |
| --- | --- |
| **Reason** | The shim receives the templates as a serialized string; converting it to a usable data structure is essential for reliable lookup. |
| **Impact** | Prevents runtime errors caused by malformed JSON and ensures subsequent lookup operations have a correct source. |
| **Complexity** | LOW |
| **Method** | Use `json.loads` with exception handling to convert the string to a dict; raise a clear ValueError if parsing fails. |

#### 2. Retrieve the rule list for the given `strategy` key, falling back to a generic default list when the strategy is not present.

| Category | Details |
| --- | --- |
| **Reason** | Not every strategy may have a dedicated template; a fallback guarantees the function always returns a valid list of rules. |
| **Impact** | Ensures the downstream risk‑management node always receives a non‑empty rule set, preserving pipeline continuity. |
| **Complexity** | LOW |
| **Method** | Perform a dict `get` lookup: `selected = templates_dict.get(strategy, templates_dict.get('default', []))`. |

#### 3. Return the selected rule list as the `output` field while echoing the original inputs for traceability.

| Category | Details |
| --- | --- |
| **Reason** | The function’s contract requires returning the rule list together with the inputs to enable downstream logging and debugging. |
| **Impact** | Facilitates auditability and makes the shim’s output compatible with the Pydantic model expectations of the calling node. |
| **Complexity** | LOW |
| **Method** | Construct a dict `{ "output": selected, "strategy": strategy, "templates": templates }` and let the framework serialize it. |


---

## substitute_rule_placeholders

### Description
Replaces strategy‑specific placeholder tokens in risk‑management rule templates with concrete values derived from the selected trading strategy.

### Implementation Plan

#### 1. Detect and parse all placeholder tokens (e.g., {{strategy}}, {{max_drawdown}}) within each rule template.

| Category | Details |
| --- | --- |
| **Reason** | Placeholders must be identified reliably before any substitution can occur. |
| **Impact** | Ensures that every dynamic element is accounted for, preventing incomplete or malformed rules. |
| **Complexity** | MEDIUM |
| **Method** | Compile a regular expression like /\{\{([^}]+)\}\}/ to extract token names, then store them in a set for each rule. |

#### 2. Map each detected placeholder to a concrete value based on the normalized strategy type and replace it in the rule text.

| Category | Details |
| --- | --- |
| **Reason** | The core purpose of the shim is to inject strategy‑specific parameters (e.g., position sizing percentages) into generic templates. |
| **Impact** | Produces fully‑specified, actionable risk‑management rules that downstream nodes can use without further processing. |
| **Complexity** | LOW |
| **Method** | Create a dictionary such as {"strategy": "momentum", "max_drawdown": "10%", "stop_loss": "2%"} and perform string replacement using Python's `re.sub` with a callback that looks up each token in the dictionary. |

#### 3. Validate that no unresolved placeholders remain after substitution and raise an informative error if any are found.

| Category | Details |
| --- | --- |
| **Reason** | Unfilled placeholders indicate missing strategy data and could cause downstream failures. |
| **Impact** | Improves robustness by catching configuration gaps early in the pipeline. |
| **Complexity** | LOW |
| **Method** | After substitution, run a second regex search for any remaining `{{.*}}` patterns; if found, throw a `ValueError` listing the missing tokens. |


---

## validate_rule_count

### Description
Validates that the supplied list of risk‑management rules contains between three and five items and returns the exact count.

### Implementation Plan

#### 1. Parse the incoming `rules` string into a clean list and verify the list length is between 3 and 5.

| Category | Details |
| --- | --- |
| **Reason** | The downstream node expects a strictly bounded number of rules to ensure a concise and enforceable risk‑management framework. |
| **Impact** | Prevents generation of too few or too many rules, guaranteeing that the `rule_count` field satisfies its schema constraints. |
| **Complexity** | LOW |
| **Method** | Split the string on line breaks or commas, strip whitespace, filter out empty entries, then assert `3 <= len(list) <= 5`; raise a descriptive ValueError if the check fails. |

#### 2. Return the validated count as the `output` integer while preserving the original `rules` string unchanged.

| Category | Details |
| --- | --- |
| **Reason** | Downstream logic (e.g., model validation and logging) requires an explicit integer count separate from the rule list. |
| **Impact** | Provides a clear, type‑safe metric for other nodes and enables straightforward audit logging of rule quantity. |
| **Complexity** | LOW |
| **Method** | After successful validation, compute `len(parsed_list)` and assign it to the `output` field; construct the response object adhering to the defined output schema. |


---

## detect_stop_loss_rule

### Description
This shim function determines whether a given list of risk management rules contains an explicit stop-loss rule.

### Implementation Plan

#### 1. Implement keyword search to identify potential stop-loss rules within the input list.

| Category | Details |
| --- | --- |
| **Reason** | To reliably identify stop-loss rules by checking for relevant keywords. |
| **Impact** | Accurately determines the presence of a stop-loss rule, influencing risk management decisions. |
| **Complexity** | MEDIUM |
| **Method** | Utilize regular expressions or keyword lists (e.g., 'stop-loss', 'stop loss', 'SL') to scan each rule in the input list for relevant terms. Case-insensitive matching is recommended. |

#### 2. Consider variations in phrasing and terminology when detecting stop-loss rules.

| Category | Details |
| --- | --- |
| **Reason** | Stop-loss rules can be expressed in multiple ways (e.g., 'trailing stop-loss', 'hard stop'). |
| **Impact** | Ensures a broader range of stop-loss rules are detected, improving accuracy. |
| **Complexity** | MEDIUM |
| **Method** | Expand the keyword list to include common variations and synonyms relating to stop-loss orders. |

#### 3. Return a boolean value indicating the presence or absence of a stop-loss rule.

| Category | Details |
| --- | --- |
| **Reason** | Provides a clear and concise output for use in subsequent logic. |
| **Impact** | Simplifies integration with other components and improves code readability. |
| **Complexity** | LOW |
| **Method** | Return `True` if any of the rules match the stop-loss criteria; otherwise, return `False`. |


---

## log_rule_generation_summary

### Description
This shim function logs a summary of the risk rule generation process, including the trading strategy, generated rules, rule count, and stop-loss presence, for auditing and monitoring purposes.

### Implementation Plan

#### 1. Implement logging mechanism using Python's logging module.

| Category | Details |
| --- | --- |
| **Reason** | To ensure consistent and structured logging. |
| **Impact** | Provides detailed audit trail of rule generation, aiding in debugging and performance monitoring. |
| **Complexity** | LOW |
| **Method** | Utilize `logging.basicConfig` to set up basic logging to a file or console, then use `logging.info` to record the summary data. |

#### 2. Structure the logged data in a consistent format (e.g., JSON or comma-separated values).

| Category | Details |
| --- | --- |
| **Reason** | To facilitate parsing and analysis of the logs. |
| **Impact** | Enables easy querying and reporting on rule generation trends and potential issues. |
| **Complexity** | MEDIUM |
| **Method** | Use the `json` module to serialize the summary data into a JSON string before logging it, or format it into a CSV structure. |

#### 3. Include relevant context in the log message, such as timestamp, log level, and strategy details.

| Category | Details |
| --- | --- |
| **Reason** | To provide a complete picture of the rule generation event. |
| **Impact** | Enhances the usefulness of the logs for root cause analysis and performance optimization. |
| **Complexity** | LOW |
| **Method** | Leverage Python's logging module's features for automatic timestamping and log level assignment.  Include strategy, rules count and list in the formatted log message. |
