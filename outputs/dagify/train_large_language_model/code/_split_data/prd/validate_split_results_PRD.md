# validate_split_results PRD

## Description
Validates that the split sizes match the original count and expected ratios.


## Implementation Plan

### 1. Check that the sum of train, validation, and test sizes equals the original sample count.

| Category | Details |
| --- | --- |
| **Reason** | Ensures no data is lost or duplicated during splitting. |
| **Impact** | Guarantees data integrity for downstream training and evaluation. |
| **Complexity** | LOW |
| **Method** | Convert all size strings to integers, sum them, and compare with the original count; raise an informative ValueError if they differ. |

### 2. Validate that the actual split ratios derived from the sizes match the expected ratios within a tolerance.

| Category | Details |
| --- | --- |
| **Reason** | Guarantees that the splits reflect the intended proportions. |
| **Impact** | Prevents skewed training/validation/test distributions that could bias model performance. |
| **Complexity** | MEDIUM |
| **Method** | Parse the expected_ratios string into a list of floats, compute actual ratios using the sizes, then compare each ratio to the expected value using an epsilon threshold (e.g., 1e-3); raise a ValueError on mismatch. |

### 3. Return a human‑readable status string summarizing the validation outcome.

| Category | Details |
| --- | --- |
| **Reason** | Provides clear feedback to users and downstream nodes. |
| **Impact** | Improves usability and debugging by exposing validation results. |
| **Complexity** | LOW |
| **Method** | If all checks pass, set `output` to "Validation succeeded."; otherwise include error details. |
