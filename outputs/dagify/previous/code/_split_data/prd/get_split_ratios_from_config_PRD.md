# get_split_ratios_from_config PRD

## Description
Retrieves the train, validation, and test split ratios from the provided configuration kwargs.


## Implementation Plan

### 1. Parse the kwargs string into a dictionary and extract the 'split_ratios' key, ensuring it is a list of three floats summing to 1.0 within a tolerance.

| Category | Details |
| --- | --- |
| **Reason** | The shim must reliably retrieve the split configuration for downstream processing. |
| **Impact** | Prevents configuration errors from propagating to the split logic, ensuring reproducible dataset splits. |
| **Complexity** | MEDIUM |
| **Method** | Use `json.loads` to decode the string, then validate the presence and format of the key, checking length, numeric types, and that the sum of the list elements equals 1.0 ± 1e-6. |

### 2. Return the extracted list of floats as the shim output.

| Category | Details |
| --- | --- |
| **Reason** | The downstream node expects a list of split ratios. |
| **Impact** | Provides the correct data type and value for subsequent split operations. |
| **Complexity** | LOW |
| **Method** | Simply return the validated list. |

### 3. Raise a descriptive `ValueError` if the 'split_ratios' key is missing, malformed, or does not satisfy the sum constraint.

| Category | Details |
| --- | --- |
| **Reason** | Robust error handling is essential to surface misconfigurations early. |
| **Impact** | Avoids silent failures and makes debugging configuration issues straightforward. |
| **Complexity** | LOW |
| **Method** | Implement guard clauses that check for key existence and value validity, raising `ValueError` with clear error messages. |
