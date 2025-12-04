# fetch_parent_indicators PRD

## Description
Fetches and returns the list of technical indicator names from the parent node's output provided as a JSON string.


## Implementation Plan

### 1. Parse the `input_data` string as JSON and extract the `indicators` array.

| Category | Details |
| --- | --- |
| **Reason** | The parent node supplies its output as a serialized JSON string; the shim must deserialize it to obtain raw data. |
| **Impact** | Provides downstream nodes with a correctly typed list of indicator names, enabling further processing. |
| **Complexity** | LOW |
| **Method** | Use Python's `json.loads` to deserialize; handle `JSONDecodeError` and raise a clear exception if parsing fails. |

### 2. Validate that the extracted `indicators` field is a list of strings and remove any non‑string entries.

| Category | Details |
| --- | --- |
| **Reason** | Ensures type safety and prevents downstream logic from encountering unexpected data types. |
| **Impact** | Reduces runtime errors in later nodes that assume a clean list of indicator names. |
| **Complexity** | MEDIUM |
| **Method** | Iterate over the list, keep items where `isinstance(item, str)`, and raise a `ValueError` if the resulting list is empty after filtering. |

### 3. Support both pure JSON output and Pydantic model `json()` strings by attempting JSON parsing first and falling back to Pydantic's `parse_raw` if needed.

| Category | Details |
| --- | --- |
| **Reason** | Different upstream implementations may serialize the model differently; flexible handling improves robustness. |
| **Impact** | Allows the shim to operate correctly across varied serialization formats without manual adjustments. |
| **Complexity** | MEDIUM |
| **Method** | Wrap the JSON parsing in a try/except; on failure, import the `IdentifyTradingIndicatorsOutput` model and call `IdentifyTradingIndicatorsOutput.parse_raw(input_data)` to obtain the object, then extract `indicators`. |
