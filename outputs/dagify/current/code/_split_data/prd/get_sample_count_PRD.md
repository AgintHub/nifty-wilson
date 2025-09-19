# get_sample_count PRD

## Description
Retrieves the total sample count from the provided training data metadata.


## Implementation Plan

### 1. Validate that the metadata contains a `sample_count` attribute of type integer.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that the shim receives valid input before proceeding. |
| **Impact** | Prevents downstream failures caused by missing or malformed data. |
| **Complexity** | LOW |
| **Method** | Use `hasattr` and `isinstance(metadata.sample_count, int)` checks. |

### 2. Return the `sample_count` value as the output.

| Category | Details |
| --- | --- |
| **Reason** | This is the core functionality required by downstream nodes. |
| **Impact** | Provides the necessary numeric value for data splitting logic. |
| **Complexity** | LOW |
| **Method** | Simple return statement: `return metadata.sample_count`. |

### 3. Raise a descriptive `ValueError` if the `sample_count` attribute is missing or not an integer.

| Category | Details |
| --- | --- |
| **Reason** | Robust error handling improves reliability and debuggability. |
| **Impact** | Allows the system to fail fast with clear diagnostics. |
| **Complexity** | LOW |
| **Method** | Implement a conditional raise: `raise ValueError("Missing or invalid sample_count in metadata")`. |
