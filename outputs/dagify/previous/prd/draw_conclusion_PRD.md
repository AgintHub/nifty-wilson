# draw_conclusion PRD

## Description
Draw a conclusion based on the experiment's findings


## Implementation Plan

### 1. Validate input schema from the `interpret_results` node: ensure that all required fields (`interpretation_summary`, `hypothesis_conclusion`, `key_metric_names`, `key_metric_values`, `limitations`, `recommendations`, `confidence_score`, `is_analysis_valid`) exist and match their declared PrimitiveTypes. Reject execution early with a clear error if validation fails.

| Category | Details |
| --- | --- |
| **Reason** | Early schema validation prevents downstream type errors and guarantees that the subsequent logic operates on reliable data. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use a JSON schema validator or type‑check each field explicitly. Log validation failures and abort the process. |

### 2. Perform an analysis validity guard: if `is_analysis_valid` is False, set `hypothesis_support` to False and construct `conclusion_text` that starts with an explicit warning about invalid analysis, followed by a brief statement that no conclusion can be reliably drawn.

| Category | Details |
| --- | --- |
| **Reason** | The output must reflect the integrity of the analysis; an invalid analysis invalidates any conclusion. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Conditional branch; concatenate warning string; skip further processing. |

### 3. Map the textual `hypothesis_conclusion` field to a boolean flag: treat any string containing the word 'supported' (case‑insensitive) as True, containing 'rejected' as False, and any other value (including 'inconclusive') as False. Store this mapping in a temporary variable `support_flag`.

| Category | Details |
| --- | --- |
| **Reason** | A deterministic mapping removes ambiguity when translating natural language into a boolean. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Normalize string to lowercase, use regex or simple `in` checks. |

### 4. Apply a confidence threshold: if `confidence_score` is below 0.60, downgrade `support_flag` to False regardless of the textual `hypothesis_conclusion`, and annotate the `conclusion_text` with a note about low confidence.

| Category | Details |
| --- | --- |
| **Reason** | Low confidence indicates that the evidence is weak; the conclusion should reflect uncertainty. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Compare float, set flag, append confidence note. |

### 5. Construct the `conclusion_text` in a single, readable paragraph that includes: 
1. A declarative statement of support or rejection using the final `support_flag`.
2. A concise summary of the key metric names and their values formatted as "MetricName (value)".
3. The confidence level expressed as a percentage.
4. A brief mention of the most significant limitation.
5. The first recommendation from the list if available.
Keep the entire text under 200 words to maintain conciseness.

| Category | Details |
| --- | --- |
| **Reason** | A well‑structured conclusion conveys all essential information while staying readable for reporting. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use Python f‑strings; iterate over `key_metric_names`/`key_metric_values` pairwise; format float to one decimal place; select the first item from `limitations` and `recommendations` if lists are non‑empty. |

### 6. Return the two output fields: `hypothesis_support` set to the final boolean flag and `conclusion_text` containing the assembled paragraph.

| Category | Details |
| --- | --- |
| **Reason** | Final step completes the node’s contract with the downstream `document_experiment` node. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Return a dictionary matching the output structure. |

### 7. Include comprehensive unit tests that cover all branches: valid analysis with support, valid analysis with rejection, inconclusive hypothesis, low confidence, invalid analysis, and missing optional fields.

| Category | Details |
| --- | --- |
| **Reason** | Testing guarantees reliability and helps future maintainers understand expected behavior. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use a testing framework (e.g., pytest) and mock input data for each scenario. |

### 8. Add runtime logging at INFO level for each major step (validation, validity guard, mapping, threshold adjustment, text assembly). Include the values of critical variables to aid debugging.

| Category | Details |
| --- | --- |
| **Reason** | Traceability is essential for diagnosing issues in complex workflows. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use Python’s logging module; format messages with variable values. |
