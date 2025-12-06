# sum_fuzzing_crashes PRD

## Description
This shim aggregates fuzzing crash counts from two separate fuzzing runs by summing their respective crash counts represented as strings and returns the total as an integer.


## Implementation Plan

### 1. Parse input string crash counts safely into integers, handling any non-numeric or empty values by treating them as zero.

| Category | Details |
| --- | --- |
| **Reason** | Crash counts may be provided as strings and could contain unexpected or malformed data; safely parsing prevents runtime errors and ensures accurate summation. |
| **Impact** | Ensures robust input handling and prevents the shim from causing failures due to bad input formats, maintaining data integrity for further processing. |
| **Complexity** | LOW |
| **Method** | Use Python's int conversion with exception handling (try-except) or default to zero for invalid inputs. |

### 2. Sum the two parsed integer crash counts to produce a single aggregated crash count representing total fuzzing crashes detected.

| Category | Details |
| --- | --- |
| **Reason** | The security report requires a consolidated count of crashes from multiple fuzzing runs to provide a comprehensive risk assessment. |
| **Impact** | Provides an accurate total crash count to downstream nodes for risk evaluation and reporting. |
| **Complexity** | LOW |
| **Method** | Perform simple integer addition of the two parsed values. |

### 3. Return the aggregated crash count as an integer output while preserving input parameters as strings for traceability.

| Category | Details |
| --- | --- |
| **Reason** | Maintaining inputs as strings ensures traceability and debugging ability, while outputting an integer meets downstream type expectations. |
| **Impact** | Facilitates transparent integration and debuggability in the pipeline, while complying with expected output type contracts. |
| **Complexity** | LOW |
| **Method** | Define output schema to include int for the sum and str for inputs, returning values accordingly. |
