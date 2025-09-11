# collect_data PRD

## Description
Collect and record numerical data and observation notes from the completed experiment, ensuring accuracy and completeness.


## Implementation Plan

### 1. Verify experiment completion and data collection status by checking `experiment_completed`, `data_collection_status`, and `safety_compliance` flags from the parent node. If any of these flags indicate failure, abort data collection and log an error.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that data is only processed from a valid, complete experiment run, preventing propagation of incomplete or unsafe data. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Implement a guard clause that checks all three boolean flags and raises a descriptive exception or returns an empty payload if any is false. |

### 2. Retrieve `observation_count` and `observations` from the input. Confirm that the integer `observation_count` equals the length of the `observations` list; if not, reconcile by truncating or flagging a mismatch.

| Category | Details |
| --- | --- |
| **Reason** | Consistency between declared count and actual notes guarantees accurate mapping between data entries and numeric values. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use a simple `len()` comparison and conditional logic to adjust or record the discrepancy in a diagnostics field. |

### 3. For each observation string in `observations`, apply a robust numeric extraction routine that searches for floating‑point or integer representations, ignoring non‑numeric tokens. Store extracted numbers in `data_values`, inserting `NaN` for observations where no numeric data is found.

| Category | Details |
| --- | --- |
| **Reason** | The output `data_values` must be a list of floats matching the observation order; a flexible extraction ensures resilience to varied logging formats. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use regex pattern `[-+]?[0-9]*\.?[0-9]+` to find all numeric tokens, then convert to float. If the pattern yields no matches, assign `float('nan')`. |

### 4. Perform data quality validation: (a) detect any `NaN` values in `data_values`; (b) compute mean and standard deviation, flagging entries beyond ±3σ as outliers; (c) verify that all numeric values fall within plausible physical ranges defined by the experiment design (e.g., temperature 0–100 °C). If any check fails, set `is_data_valid` to false.

| Category | Details |
| --- | --- |
| **Reason** | Quality control prevents downstream analysis on corrupted or misleading data. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Implement a helper function that returns a boolean by aggregating the three checks; optionally produce a `quality_report` for diagnostics. |

### 5. Populate the output fields: copy the validated `observation_count`, the processed `data_values`, the boolean `is_data_valid`, and the original `observations` into `observation_notes`.

| Category | Details |
| --- | --- |
| **Reason** | Direct mapping guarantees that downstream nodes receive correctly typed and validated data. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Simple assignment statements in the output dictionary. |

### 6. Return the output payload in the required JSON structure. Include an optional diagnostic log in a hidden field if `is_data_valid` is false to aid troubleshooting.

| Category | Details |
| --- | --- |
| **Reason** | Providing diagnostics supports traceability and facilitates quick identification of data issues. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Serialize the payload to JSON, omitting hidden fields unless debugging mode is active. |
