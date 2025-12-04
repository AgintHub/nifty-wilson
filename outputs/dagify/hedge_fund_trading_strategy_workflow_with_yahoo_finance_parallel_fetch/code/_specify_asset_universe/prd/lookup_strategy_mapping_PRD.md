# lookup_strategy_mapping PRD

## Description
Retrieves the list of asset classes that correspond to a given trading strategy type using a provided mapping.


## Implementation Plan

### 1. Validate that `strategy_type` is a non‑empty string and that `mapping` can be parsed as valid JSON.

| Category | Details |
| --- | --- |
| **Reason** | Prevents runtime failures caused by malformed inputs and ensures the function receives data in the expected format. |
| **Impact** | Raises clear errors early, improving debugging and stability of the pipeline. |
| **Complexity** | LOW |
| **Method** | Use `isinstance` checks for the string and `json.loads` with try/except to verify JSON structure. |

### 2. Parse the `mapping` JSON into a Python dict and retrieve the asset class list for the given `strategy_type`.

| Category | Details |
| --- | --- |
| **Reason** | Core functionality of the shim – mapping the strategy to its compatible asset classes. |
| **Impact** | Provides downstream nodes with the correct list of asset classes aligned to the chosen strategy. |
| **Complexity** | LOW |
| **Method** | Convert JSON via `json.loads`, then use `dict.get(strategy_type)`; raise a descriptive `KeyError` if the key is missing. |

### 3. Normalize the retrieved list to ensure all elements are strings and return it as the `output` field.

| Category | Details |
| --- | --- |
| **Reason** | Downstream Pydantic models expect a `List[str]`; type consistency avoids validation errors later. |
| **Impact** | Guarantees type safety and consistent ordering for subsequent processing steps. |
| **Complexity** | LOW |
| **Method** | Apply a list comprehension ` [str(item) for item in result] ` and return the list in the response structure. |
