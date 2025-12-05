# design_compliance_program PRD

## Description
Create compliance policies aligned with regulations and risk.


## Implementation Plan

### 1. Validate and normalize the incoming lists: confirm that `compliance_requirements` is a list of strings and that `risk_controls` is a list of strings; strip whitespace, collapse duplicate entries, and ensure no empty strings are present.

| Category | Details |
| --- | --- |
| **Reason** | Ensures downstream mapping logic receives clean, deterministic inputs, reducing error risk in the mapping step. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use Python list comprehensions with `.strip()` and `set()` to deduplicate, then convert back to list; raise a validation error if types are incorrect. |

### 2. Create a keyword-to-policy dictionary that maps common regulatory requirement themes (e.g., "recordkeeping", "conflict of interest", "cybersecurity", "AML") to internal policy names, drawing from the existing `risk_controls` list and a predefined compliance policy catalog.

| Category | Details |
| --- | --- |
| **Reason** | Provides a deterministic rule‑based foundation for the mapping, enabling consistent policy assignment across similar regulations. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Define a static dict in code; supplement with a lookup in `risk_controls` where applicable; for policies not in risk_controls, reference a compliance policy catalog file. |

### 3. For each requirement in `compliance_requirements`, perform a fuzzy keyword match against the dictionary keys using Levenshtein distance or a simple case‑insensitive substring check; if a match is found, assign the corresponding policy reference; otherwise, default to a generic "Compliance Procedure" policy.

| Category | Details |
| --- | --- |
| **Reason** | Balances precision and flexibility, capturing variations in wording while ensuring every requirement gets a policy reference. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use Python's `difflib.get_close_matches` or `fuzzywuzzy` to compute similarity; threshold set to 0.8 for substring matches; fallback to generic policy. |

### 4. Cross‑reference the assigned policy references with the `risk_controls` list to ensure that each policy is supported by a corresponding risk control; if a policy is missing a risk control, log a warning and append the policy to the `policy_references` list for review.

| Category | Details |
| --- | --- |
| **Reason** | Guarantees alignment between compliance obligations and risk management controls, a key governance requirement. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Iterate through `policy_references`, check membership in `risk_controls`; if absent, write to a diagnostics log. |

### 5. Count the number of mapped pairs, set `mapping_count` to that integer, and compare lengths of `compliance_requirements` and `policy_references` to compute `is_consistent` as a Boolean flag.

| Category | Details |
| --- | --- |
| **Reason** | Provides a quick integrity check for downstream consumers of this node (e.g., the final summary). |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Python `len()` on each list; `is_consistent = len(compliance_requirements) == len(policy_references)`. |

### 6. Return the structured output dictionary matching the specified `output_structure` order, ensuring the lists maintain original requirement order for traceability.

| Category | Details |
| --- | --- |
| **Reason** | Preserves order so that downstream nodes can correlate requirements to policies by index, simplifying auditing. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Construct a dict with keys in order, serialize to JSON or return as a Python dict; no transformation needed beyond previous steps. |
