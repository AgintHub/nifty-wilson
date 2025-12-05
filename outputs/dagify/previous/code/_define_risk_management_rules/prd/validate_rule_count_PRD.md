# validate_rule_count PRD

## Description
Validates that the supplied list of risk‑management rules contains between three and five items and returns the exact count.


## Implementation Plan

### 1. Parse the incoming `rules` string into a clean list and verify the list length is between 3 and 5.

| Category | Details |
| --- | --- |
| **Reason** | The downstream node expects a strictly bounded number of rules to ensure a concise and enforceable risk‑management framework. |
| **Impact** | Prevents generation of too few or too many rules, guaranteeing that the `rule_count` field satisfies its schema constraints. |
| **Complexity** | LOW |
| **Method** | Split the string on line breaks or commas, strip whitespace, filter out empty entries, then assert `3 <= len(list) <= 5`; raise a descriptive ValueError if the check fails. |

### 2. Return the validated count as the `output` integer while preserving the original `rules` string unchanged.

| Category | Details |
| --- | --- |
| **Reason** | Downstream logic (e.g., model validation and logging) requires an explicit integer count separate from the rule list. |
| **Impact** | Provides a clear, type‑safe metric for other nodes and enables straightforward audit logging of rule quantity. |
| **Complexity** | LOW |
| **Method** | After successful validation, compute `len(parsed_list)` and assign it to the `output` field; construct the response object adhering to the defined output schema. |
