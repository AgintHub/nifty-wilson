# validate_split_ratios PRD

## Description
Validates that the given split ratios list sums to 1.0 within a specified tolerance.


## Implementation Plan

### 1. Parse the input string into a numeric list and compute the sum, ensuring it equals 1.0 within a tolerance of 1e-6.

| Category | Details |
| --- | --- |
| **Reason** | The split ratios must represent a valid probability distribution. |
| **Impact** | Prevents downstream errors caused by incorrect data partitioning. |
| **Complexity** | LOW |
| **Method** | Use json.loads to parse, sum the list, and compare to 1.0 with an epsilon. |

### 2. If the sum deviates slightly due to floating‑point rounding, normalize the ratios by dividing each element by the computed sum.

| Category | Details |
| --- | --- |
| **Reason** | Allows tolerant handling of minor numeric inaccuracies while preserving relative proportions. |
| **Impact** | Ensures robustness of the splitter without manual adjustment. |
| **Complexity** | LOW |
| **Method** | Apply list comprehension: [x / total for x in ratios] and replace the original list. |

### 3. Return a standardized output string ('Valid') or raise a ValueError with a clear message if validation fails.

| Category | Details |
| --- | --- |
| **Reason** | Provides a deterministic contract for downstream nodes to consume. |
| **Impact** | Guarantees consistent error handling across the pipeline. |
| **Complexity** | LOW |
| **Method** | If sum is within tolerance, return 'Valid'; otherwise, raise ValueError(f"Split ratios must sum to 1.0, got {total}"). |
