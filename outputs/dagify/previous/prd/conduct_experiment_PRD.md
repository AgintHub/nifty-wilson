# conduct_experiment PRD

## Description
This node executes the laboratory or field experiment as specified in the design and preparation steps. It must follow the experimental protocol, enforce safety checks, log observations and anomalies, and signal whether data collection succeeded.


## Implementation Plan

### 1. Validate that all materials and equipment are prepared by checking the `is_prepared` flag from the `prepare_materials` output. If the flag is false, abort the experiment, set `experiment_completed` to false, and record a safety compliance failure.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that the experiment only proceeds when the required resources are available, preventing equipment failures and safety incidents. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Implement a pre‑execution check: if !is_prepared then set experiment_completed = false, safety_compliance = false, exit loop. |

### 2. Parse the experimental protocol string from the `design_experiment` output into a list of executable steps. Store each step in an array `protocol_steps` for sequential iteration.

| Category | Details |
| --- | --- |
| **Reason** | The protocol must be broken down into actionable operations that the system can iterate over. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Use a simple delimiter (e.g., newline or semicolon) to split the protocol, trim whitespace, and validate step syntax against a known schema. |

### 3. Initialize empty collections for `observations` and `anomaly_descriptions`, and set boolean flags `safety_compliance` and `data_collection_status` to true. Assign the trial number from `design_experiment.sample_size` if it represents a run index, or default to 1 if not provided.

| Category | Details |
| --- | --- |
| **Reason** | Establishes baseline state before experiment execution, allowing clear tracking of changes. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Set trial_number = design_experiment.sample_size or 1; initialize arrays. |

### 4. Iterate over each step in `protocol_steps`. For each step, perform the defined action (e.g., add reagent, adjust temperature, record measurement) and capture a timestamped observation note.

| Category | Details |
| --- | --- |
| **Reason** | Sequential execution is essential to maintain experimental integrity. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Implement a loop: for step in protocol_steps: execute_step(step); append observation = f'{timestamp}: {step_result}'. |

### 5. During step execution, continuously monitor safety compliance against a predefined safety checklist (e.g., PPE usage, containment integrity, emergency procedures). If any violation is detected, set `safety_compliance` to false, log a detailed anomaly description, and abort remaining steps.

| Category | Details |
| --- | --- |
| **Reason** | Safety must be enforced at all times; early abort prevents escalation of hazards. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Embed safety checks within each `execute_step` call; use a rule engine or conditional checks to flag violations. |

### 6. After each step, increment `observation_count` by one, append the observation to the `observations` list, and check if the data collected for that step meets quality criteria (e.g., range checks).

| Category | Details |
| --- | --- |
| **Reason** | Accurate observation recording is necessary for downstream data analysis. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use simple counters and append operations; perform range checks against expected min/max values. |

### 7. If an unexpected event occurs—such as equipment failure, measurement out‑of‑range, or time lag—set `anomalies_detected` to true and append a descriptive message to `anomaly_descriptions`.

| Category | Details |
| --- | --- |
| **Reason** | Anomalies may influence data validity and should be transparently reported. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Wrap critical operations in try/catch blocks; on exception, capture exception message and context. |

### 8. After all steps have been processed, set `experiment_completed` to true if no fatal safety violations occurred, otherwise leave it false.

| Category | Details |
| --- | --- |
| **Reason** | Completion flag is required to determine if the experiment was fully executed. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Check safety_compliance flag; if true then experiment_completed = true. |

### 9. Determine `data_collection_status` by verifying that the number of collected data points matches the expected count defined in `design_experiment.sample_size`. If mismatch, set `data_collection_status` to false.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that the experiment produced a complete dataset for analysis. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Compare observation_count with sample_size; if equal, status = true. |

### 10. Return the constructed output dictionary containing all eight fields, ensuring correct data types (bool, int, List[str]) and that all lists are in the order of execution.

| Category | Details |
| --- | --- |
| **Reason** | A consistent and typed output is required for downstream nodes. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Package variables into a dict: {"experiment_completed":..., "safety_compliance":..., ...}; serialize as JSON. |
