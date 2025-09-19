# compute_split_boundaries PRD

## Description
Computes integer split boundaries for training, validation, and test sets based on total sample count and split ratios.


## Implementation Plan

### 1. Validate that `sample_count` is a positive integer and `ratios` is a list of floats summing to 1.0 within a small tolerance.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the function receives valid numeric inputs before performing calculations. |
| **Impact** | Prevents runtime errors and guarantees meaningful split boundaries. |
| **Complexity** | LOW |
| **Method** | Parse the string inputs into integers and floats; use `abs(sum(ratios) - 1.0) < 1e-6` for tolerance. |

### 2. Compute cumulative split counts by multiplying `sample_count` with each ratio and casting to integers, then adjust for any rounding error to ensure the sum equals `sample_count`.

| Category | Details |
| --- | --- |
| **Reason** | Accurate boundaries are critical for balanced dataset splits. |
| **Impact** | Guarantees that no samples are lost or duplicated across splits. |
| **Complexity** | MEDIUM |
| **Method** | Use a loop to calculate each boundary: `boundary = int(round(sample_count * cumulative_ratio))`; after computing all boundaries, adjust the last boundary to `sample_count` if necessary. |

### 3. Return the computed boundaries as a tuple `(train_boundary, val_boundary)` for downstream slicing.

| Category | Details |
| --- | --- |
| **Reason** | Provides a clear and consistent API for the `split_data` node. |
| **Impact** | Enables deterministic slicing of the shuffled permutation indices. |
| **Complexity** | LOW |
| **Method** | Return a Python tuple of the two boundary integers; optionally wrap in a JSON-serializable string if required by the shim interface. |
