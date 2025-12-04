# validate_indicators_exist PRD

## Description
Ensures that every indicator supplied in the list has a matching entry in the definitions registry and raises a clear error for any missing items.


## Implementation Plan

### 1. Parse the incoming `indicators` string into a list and verify each entry exists as a key in the `definitions` dictionary.

| Category | Details |
| --- | --- |
| **Reason** | The core responsibility of the shim is to catch mismatches between requested technical indicators and the available definition set before downstream logic runs. |
| **Impact** | Prevents downstream runtime errors and ensures that only supported indicators are used in signal generation. |
| **Complexity** | LOW |
| **Method** | Deserialize the `indicators` JSON‑encoded string (or split on commas), convert `definitions` from its JSON string to a Python dict, then iterate using a set‑based lookup for O(1) membership checks. |

### 2. Collect any missing indicators and raise a descriptive `ValueError` that lists all absent items.

| Category | Details |
| --- | --- |
| **Reason** | Providing a comprehensive error message aids debugging and allows calling code to surface precise feedback to the user or orchestrator. |
| **Impact** | Immediate failure with clear diagnostics, avoiding partial or silent failures later in the pipeline. |
| **Complexity** | MEDIUM |
| **Method** | Accumulate missing names in a list during verification; if the list is non‑empty, format an error string and raise `ValueError` with that message. |

### 3. Return a simple acknowledgment string (e.g., "OK") when all indicators are validated.

| Category | Details |
| --- | --- |
| **Reason** | The shim’s output contract expects a string field `output`; returning a constant confirms successful validation without altering downstream data structures. |
| **Impact** | Standardizes the node’s return shape, enabling downstream nodes to rely on the presence of the `output` field. |
| **Complexity** | LOW |
| **Method** | After successful validation, set `output = "OK"` and return it as part of the shim’s response. |
