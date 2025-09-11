# test_science_experiment_workflow - Complete PRD Documentation

## Overview
PRDs for nodes in the 'test_science_experiment_workflow' module.

## Table of Contents

- [analyze_data](#analyze_data)

- [collect_data](#collect_data)

- [conduct_experiment](#conduct_experiment)

- [design_experiment](#design_experiment)

- [document_experiment](#document_experiment)

- [draw_conclusion](#draw_conclusion)

- [formulate_hypothesis](#formulate_hypothesis)

- [interpret_results](#interpret_results)

- [prepare_materials](#prepare_materials)



---

## analyze_data

### Description
This node consumes the raw data and metadata produced by the collect_data node, performs a rigorous statistical analysis, and outputs a structured summary of findings that will feed into downstream interpretation.

### Implementation Plan

#### 1. Validate incoming data: Verify that the 'is_data_valid' flag from collect_data is true; if false, abort analysis and set 'is_analysis_successful' to false.

| Category | Details |
| --- | --- |
| **Reason** | Early validation prevents wasted computational effort and ensures downstream steps are based on trustworthy data. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Check boolean flag; log error message; return failure state. |

#### 2. Calculate descriptive statistics: Compute mean, median, standard deviation, min, and max for each numeric column in 'data_values' to establish baseline variability.

| Category | Details |
| --- | --- |
| **Reason** | Descriptive stats provide context for trend and correlation detection. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use NumPy or Pandas aggregation functions; store results in temporary variables. |

#### 3. Detect temporal or sequential trends: If data has an inherent order (e.g., observation index), apply a linear regression or moving‑average smoothing to identify monotonic increases or decreases.

| Category | Details |
| --- | --- |
| **Reason** | Temporal trends are often key insights in experimental data. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Fit simple linear regression with observation index as predictor; extract slope and p‑value; record trend description if slope significant at alpha=0.05. |

#### 4. Compute pairwise correlations: For each pair of variables (if multiple variables exist in data), calculate Pearson or Spearman correlation coefficients and corresponding p‑values.

| Category | Details |
| --- | --- |
| **Reason** | Correlation analysis uncovers relationships that may inform hypothesis testing. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use SciPy stats.pearsonr or stats.spearmanr; filter pairs with |r|>0.5 and p<0.05; compile correlation summary string. |

#### 5. Identify significant factors: Apply a simple univariate analysis (e.g., t‑test or ANOVA) comparing outcome variable against each independent variable, recording those with p<0.05.

| Category | Details |
| --- | --- |
| **Reason** | Highlights variables that drive the dependent outcome. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use SciPy stats.ttest_ind or stats.f_oneway; map significant variable names to 'significant_factors' list. |

#### 6. Synthesize analysis summary: Concatenate key descriptive statistics, trend findings, correlation results, and significant factor list into a cohesive narrative, ensuring readability and inclusion of statistical significance statements.

| Category | Details |
| --- | --- |
| **Reason** | Provides a human‑readable output that downstream nodes can directly consume. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Template string formatting; include bullet points for each major finding; embed p‑value and r‑value values. |

#### 7. Populate output fields: Assign computed values to 'analysis_summary', 'trend_descriptions', 'correlation_summary', 'significant_factors', and set 'is_analysis_successful' to true upon successful completion of all steps.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the node's contract is fulfilled exactly as defined. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Direct assignment of variables to output JSON structure. |


---

## collect_data

### Description
Collect and record numerical data and observation notes from the completed experiment, ensuring accuracy and completeness.

### Implementation Plan

#### 1. Verify experiment completion and data collection status by checking `experiment_completed`, `data_collection_status`, and `safety_compliance` flags from the parent node. If any of these flags indicate failure, abort data collection and log an error.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that data is only processed from a valid, complete experiment run, preventing propagation of incomplete or unsafe data. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Implement a guard clause that checks all three boolean flags and raises a descriptive exception or returns an empty payload if any is false. |

#### 2. Retrieve `observation_count` and `observations` from the input. Confirm that the integer `observation_count` equals the length of the `observations` list; if not, reconcile by truncating or flagging a mismatch.

| Category | Details |
| --- | --- |
| **Reason** | Consistency between declared count and actual notes guarantees accurate mapping between data entries and numeric values. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use a simple `len()` comparison and conditional logic to adjust or record the discrepancy in a diagnostics field. |

#### 3. For each observation string in `observations`, apply a robust numeric extraction routine that searches for floating‑point or integer representations, ignoring non‑numeric tokens. Store extracted numbers in `data_values`, inserting `NaN` for observations where no numeric data is found.

| Category | Details |
| --- | --- |
| **Reason** | The output `data_values` must be a list of floats matching the observation order; a flexible extraction ensures resilience to varied logging formats. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use regex pattern `[-+]?[0-9]*\.?[0-9]+` to find all numeric tokens, then convert to float. If the pattern yields no matches, assign `float('nan')`. |

#### 4. Perform data quality validation: (a) detect any `NaN` values in `data_values`; (b) compute mean and standard deviation, flagging entries beyond ±3σ as outliers; (c) verify that all numeric values fall within plausible physical ranges defined by the experiment design (e.g., temperature 0–100 °C). If any check fails, set `is_data_valid` to false.

| Category | Details |
| --- | --- |
| **Reason** | Quality control prevents downstream analysis on corrupted or misleading data. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Implement a helper function that returns a boolean by aggregating the three checks; optionally produce a `quality_report` for diagnostics. |

#### 5. Populate the output fields: copy the validated `observation_count`, the processed `data_values`, the boolean `is_data_valid`, and the original `observations` into `observation_notes`.

| Category | Details |
| --- | --- |
| **Reason** | Direct mapping guarantees that downstream nodes receive correctly typed and validated data. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Simple assignment statements in the output dictionary. |

#### 6. Return the output payload in the required JSON structure. Include an optional diagnostic log in a hidden field if `is_data_valid` is false to aid troubleshooting.

| Category | Details |
| --- | --- |
| **Reason** | Providing diagnostics supports traceability and facilitates quick identification of data issues. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Serialize the payload to JSON, omitting hidden fields unless debugging mode is active. |


---

## conduct_experiment

### Description
This node executes the laboratory or field experiment as specified in the design and preparation steps. It must follow the experimental protocol, enforce safety checks, log observations and anomalies, and signal whether data collection succeeded.

### Implementation Plan

#### 1. Validate that all materials and equipment are prepared by checking the `is_prepared` flag from the `prepare_materials` output. If the flag is false, abort the experiment, set `experiment_completed` to false, and record a safety compliance failure.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that the experiment only proceeds when the required resources are available, preventing equipment failures and safety incidents. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Implement a pre‑execution check: if !is_prepared then set experiment_completed = false, safety_compliance = false, exit loop. |

#### 2. Parse the experimental protocol string from the `design_experiment` output into a list of executable steps. Store each step in an array `protocol_steps` for sequential iteration.

| Category | Details |
| --- | --- |
| **Reason** | The protocol must be broken down into actionable operations that the system can iterate over. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Use a simple delimiter (e.g., newline or semicolon) to split the protocol, trim whitespace, and validate step syntax against a known schema. |

#### 3. Initialize empty collections for `observations` and `anomaly_descriptions`, and set boolean flags `safety_compliance` and `data_collection_status` to true. Assign the trial number from `design_experiment.sample_size` if it represents a run index, or default to 1 if not provided.

| Category | Details |
| --- | --- |
| **Reason** | Establishes baseline state before experiment execution, allowing clear tracking of changes. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Set trial_number = design_experiment.sample_size or 1; initialize arrays. |

#### 4. Iterate over each step in `protocol_steps`. For each step, perform the defined action (e.g., add reagent, adjust temperature, record measurement) and capture a timestamped observation note.

| Category | Details |
| --- | --- |
| **Reason** | Sequential execution is essential to maintain experimental integrity. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Implement a loop: for step in protocol_steps: execute_step(step); append observation = f'{timestamp}: {step_result}'. |

#### 5. During step execution, continuously monitor safety compliance against a predefined safety checklist (e.g., PPE usage, containment integrity, emergency procedures). If any violation is detected, set `safety_compliance` to false, log a detailed anomaly description, and abort remaining steps.

| Category | Details |
| --- | --- |
| **Reason** | Safety must be enforced at all times; early abort prevents escalation of hazards. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Embed safety checks within each `execute_step` call; use a rule engine or conditional checks to flag violations. |

#### 6. After each step, increment `observation_count` by one, append the observation to the `observations` list, and check if the data collected for that step meets quality criteria (e.g., range checks).

| Category | Details |
| --- | --- |
| **Reason** | Accurate observation recording is necessary for downstream data analysis. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use simple counters and append operations; perform range checks against expected min/max values. |

#### 7. If an unexpected event occurs—such as equipment failure, measurement out‑of‑range, or time lag—set `anomalies_detected` to true and append a descriptive message to `anomaly_descriptions`.

| Category | Details |
| --- | --- |
| **Reason** | Anomalies may influence data validity and should be transparently reported. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Wrap critical operations in try/catch blocks; on exception, capture exception message and context. |

#### 8. After all steps have been processed, set `experiment_completed` to true if no fatal safety violations occurred, otherwise leave it false.

| Category | Details |
| --- | --- |
| **Reason** | Completion flag is required to determine if the experiment was fully executed. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Check safety_compliance flag; if true then experiment_completed = true. |

#### 9. Determine `data_collection_status` by verifying that the number of collected data points matches the expected count defined in `design_experiment.sample_size`. If mismatch, set `data_collection_status` to false.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that the experiment produced a complete dataset for analysis. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Compare observation_count with sample_size; if equal, status = true. |

#### 10. Return the constructed output dictionary containing all eight fields, ensuring correct data types (bool, int, List[str]) and that all lists are in the order of execution.

| Category | Details |
| --- | --- |
| **Reason** | A consistent and typed output is required for downstream nodes. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Package variables into a dict: {"experiment_completed":..., "safety_compliance":..., ...}; serialize as JSON. |


---

## design_experiment

### Description
Design the experiment to test the hypothesis

### Implementation Plan

#### 1. 1️⃣ Extract the single-sentence hypothesis from the parent node *formulate_hypothesis* and assign it to the `hypothesis` field.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the hypothesis is directly inherited and not re-formulated, maintaining consistency across the workflow. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Parse the parent output `hypothesis_sentence`, trim whitespace, and store as `hypothesis`. |

#### 2. 2️⃣ Identify all factors relevant to the research objective that can be intentionally manipulated by the experimenter; list them in the `independent_variables` field.

| Category | Details |
| --- | --- |
| **Reason** | Independent variables are the key drivers that the experiment will test, directly affecting the outcome. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Apply a knowledge‑base lookup of standard experimental variables for the domain; filter by relevance; ensure at least two distinct levels per variable to allow statistical analysis. |

#### 3. 3️⃣ For each independent variable, determine the measurable outcome(s) it is expected to influence; compile these into the `dependent_variables` list.

| Category | Details |
| --- | --- |
| **Reason** | Dependent variables represent the experiment’s outcomes, enabling quantitative evaluation of the hypothesis. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Map each independent variable to its theoretical effect using causal diagrams; cross‑check with the hypothesis statement; avoid duplication. |

#### 4. 4️⃣ Enumerate all environmental or procedural factors that must remain constant across trials to prevent confounding; place them in `control_variables`.

| Category | Details |
| --- | --- |
| **Reason** | Controls isolate the effect of independent variables, ensuring validity. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | List temperature, humidity, equipment calibration, operator, timing, and any other potentially influencing factors; confirm via a design-of-experiments checklist. |

#### 5. 5️⃣ For each dependent variable, specify the measurement instrument or protocol (e.g., spectrophotometer reading, time‑to‑completion, survey score) and store the description in `measurement_methods`.

| Category | Details |
| --- | --- |
| **Reason** | Clear measurement methods enable reproducibility and data integrity. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Match each dependent variable with an appropriate instrument from the domain’s standard equipment list; document calibration steps and unit conventions. |

#### 6. 6️⃣ Calculate the required `sample_size` using a power analysis that incorporates the expected effect size, alpha level (commonly 0.05), desired power (commonly 0.8), and the number of independent variables.

| Category | Details |
| --- | --- |
| **Reason** | Adequate sample size ensures statistical validity and mitigates Type II error. |
| **Impact** | HIGH |
| **Complexity** | HIGH |
| **Method** | Employ a statistical software API (e.g., G*Power, scipy.stats) with effect size from pilot data or literature; round up to nearest integer; enforce a minimum threshold (e.g., 30 per group) if calculation yields low numbers. |

#### 7. 7️⃣ Draft a comprehensive `experimental_protocol` string that sequences the experiment from preparation to data capture, including safety checks, randomization, blinding (if applicable), and data logging procedures.

| Category | Details |
| --- | --- |
| **Reason** | A detailed protocol guarantees consistency across multiple trials and operators. |
| **Impact** | HIGH |
| **Complexity** | HIGH |
| **Method** | Structure the protocol in numbered paragraphs: (1) Setup, (2) Calibration, (3) Randomization of treatment groups, (4) Execution steps for each trial, (5) Data recording, (6) Decontamination, (7) Safety checks. Embed placeholders for variable values (e.g., `{{temperature}}`). |

#### 8. 8️⃣ Validate the design by performing a quick risk assessment and ensuring all safety protocols are feasible within the defined experimental setting.

| Category | Details |
| --- | --- |
| **Reason** | Prevents experiment abortion due to oversight of safety or regulatory compliance. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Cross‑reference the protocol with institutional safety guidelines; flag any missing PPE or hazard mitigation steps. |

#### 9. 9️⃣ Review the entire output dictionary for type consistency and completeness before returning it to the workflow engine.

| Category | Details |
| --- | --- |
| **Reason** | Type mismatches would cause downstream node failures. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Automate a schema validation routine: assert `hypothesis` is string, `independent_variables` is list of strings, etc.; generate error logs for missing fields. |


---

## document_experiment

### Description
Document the entire experiment process and findings.

### Implementation Plan

#### 1. Extract the hypothesis sentence from the `formulate_hypothesis` node output and store it in the `hypothesis` field.

| Category | Details |
| --- | --- |
| **Reason** | The hypothesis is the foundational statement that guides all subsequent sections of the report. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Retrieve `hypothesis_sentence` directly; perform a shallow copy to `hypothesis`. |

#### 2. Synthesize the experimental design details from the `design_experiment` node output into a concise paragraph for `design_summary`.

| Category | Details |
| --- | --- |
| **Reason** | A clear design summary ensures readers understand the methodology, variables, and controls. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Concatenate the following fields: `hypothesis`, `independent_variables`, `dependent_variables`, `control_variables`, `measurement_methods`, and `experimental_protocol`. Apply sentence templating to maintain readability. |

#### 3. Create a data collection overview by aggregating metrics from the `collect_data` node (`observation_count`, `data_values`, `is_data_valid`, `observation_notes`).

| Category | Details |
| --- | --- |
| **Reason** | Summarizing raw data quality and volume gives transparency to the data foundation. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Generate a paragraph stating the total observations, the range of data values, any validation flags, and highlight notable observation notes. Format numeric summaries using statistical descriptors (mean, median, std). |

#### 4. Compose the `analysis_summary` section by summarizing key outputs from the `analyze_data` node (`analysis_summary`, `trend_descriptions`, `correlation_summary`, `significant_factors`).

| Category | Details |
| --- | --- |
| **Reason** | Providing a high‑level analytical narrative bridges raw data and scientific interpretation. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Insert the provided `analysis_summary` verbatim. Append bullet points for each trend, correlation, and significant factor. Use LaTeX for correlation coefficients if necessary. |

#### 5. Integrate the interpretation text from the `interpret_results` node into the `interpretation` field, ensuring it references the hypothesis and key metrics.

| Category | Details |
| --- | --- |
| **Reason** | Interpretation contextualizes statistical findings within the experimental question. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Copy `interpretation_summary` and optionally prepend a sentence linking it to the hypothesis. Verify that all `key_metric_names` and `key_metric_values` are mentioned. |

#### 6. Generate the final `conclusion` field by combining `hypothesis_support` and `conclusion_text` from the `draw_conclusion` node.

| Category | Details |
| --- | --- |
| **Reason** | The conclusion must clearly state support status and summarise overall findings. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | If `hypothesis_support` is true, prepend "The hypothesis is supported;" otherwise prepend "The hypothesis is rejected;" then append `conclusion_text`. |

#### 7. Create a list of visual aid references for `visual_aids` by collating file names of graphs and diagrams generated during the analysis phase (e.g., "temperature_over_time.png", "correlation_matrix.pdf").

| Category | Details |
| --- | --- |
| **Reason** | Visual aids enhance comprehension of complex data. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Query the analysis module for generated graph files. If none are available, generate new plots using matplotlib or seaborn based on the data arrays. Store each filename in the list. |

#### 8. Determine the `report_title` by embedding the hypothesis into a standardized title format, e.g., "Experiment Report: [Hypothesis]".

| Category | Details |
| --- | --- |
| **Reason** | A descriptive title improves searchability and context. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Concatenate a prefix string with the `hypothesis` value, truncating if necessary to stay within 80 characters. |

#### 9. Validate that all required fields are non‑empty and set `is_complete` to true only when all validation checks pass.

| Category | Details |
| --- | --- |
| **Reason** | Ensures report integrity before downstream consumption. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Iterate over all output fields, checking string length > 0 or list length > 0. If any fail, set `is_complete` to false and log the missing field. |

#### 10. Serialize the assembled report into JSON format, matching the specified output structure, and return it as the node's result.

| Category | Details |
| --- | --- |
| **Reason** | Consistent JSON output allows automatic ingestion by downstream systems. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Construct a Python dict with keys matching the output structure and convert it using `json.dumps`. |


---

## draw_conclusion

### Description
Draw a conclusion based on the experiment's findings

### Implementation Plan

#### 1. Validate input schema from the `interpret_results` node: ensure that all required fields (`interpretation_summary`, `hypothesis_conclusion`, `key_metric_names`, `key_metric_values`, `limitations`, `recommendations`, `confidence_score`, `is_analysis_valid`) exist and match their declared PrimitiveTypes. Reject execution early with a clear error if validation fails.

| Category | Details |
| --- | --- |
| **Reason** | Early schema validation prevents downstream type errors and guarantees that the subsequent logic operates on reliable data. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use a JSON schema validator or type‑check each field explicitly. Log validation failures and abort the process. |

#### 2. Perform an analysis validity guard: if `is_analysis_valid` is False, set `hypothesis_support` to False and construct `conclusion_text` that starts with an explicit warning about invalid analysis, followed by a brief statement that no conclusion can be reliably drawn.

| Category | Details |
| --- | --- |
| **Reason** | The output must reflect the integrity of the analysis; an invalid analysis invalidates any conclusion. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Conditional branch; concatenate warning string; skip further processing. |

#### 3. Map the textual `hypothesis_conclusion` field to a boolean flag: treat any string containing the word 'supported' (case‑insensitive) as True, containing 'rejected' as False, and any other value (including 'inconclusive') as False. Store this mapping in a temporary variable `support_flag`.

| Category | Details |
| --- | --- |
| **Reason** | A deterministic mapping removes ambiguity when translating natural language into a boolean. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Normalize string to lowercase, use regex or simple `in` checks. |

#### 4. Apply a confidence threshold: if `confidence_score` is below 0.60, downgrade `support_flag` to False regardless of the textual `hypothesis_conclusion`, and annotate the `conclusion_text` with a note about low confidence.

| Category | Details |
| --- | --- |
| **Reason** | Low confidence indicates that the evidence is weak; the conclusion should reflect uncertainty. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Compare float, set flag, append confidence note. |

#### 5. Construct the `conclusion_text` in a single, readable paragraph that includes: 
1. A declarative statement of support or rejection using the final `support_flag`.
2. A concise summary of the key metric names and their values formatted as "MetricName (value)".
3. The confidence level expressed as a percentage.
4. A brief mention of the most significant limitation.
5. The first recommendation from the list if available.
Keep the entire text under 200 words to maintain conciseness.

| Category | Details |
| --- | --- |
| **Reason** | A well‑structured conclusion conveys all essential information while staying readable for reporting. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use Python f‑strings; iterate over `key_metric_names`/`key_metric_values` pairwise; format float to one decimal place; select the first item from `limitations` and `recommendations` if lists are non‑empty. |

#### 6. Return the two output fields: `hypothesis_support` set to the final boolean flag and `conclusion_text` containing the assembled paragraph.

| Category | Details |
| --- | --- |
| **Reason** | Final step completes the node’s contract with the downstream `document_experiment` node. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Return a dictionary matching the output structure. |

#### 7. Include comprehensive unit tests that cover all branches: valid analysis with support, valid analysis with rejection, inconclusive hypothesis, low confidence, invalid analysis, and missing optional fields.

| Category | Details |
| --- | --- |
| **Reason** | Testing guarantees reliability and helps future maintainers understand expected behavior. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use a testing framework (e.g., pytest) and mock input data for each scenario. |

#### 8. Add runtime logging at INFO level for each major step (validation, validity guard, mapping, threshold adjustment, text assembly). Include the values of critical variables to aid debugging.

| Category | Details |
| --- | --- |
| **Reason** | Traceability is essential for diagnosing issues in complex workflows. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use Python’s logging module; format messages with variable values. |


---

## formulate_hypothesis

### Description
Generate a concise, testable hypothesis that encapsulates the expected relationship between the experiment's variables. The hypothesis must be expressed as a single, grammatically correct sentence.

### Implementation Plan

#### 1. Retrieve the experiment objective from the execution context (e.g., an environment variable, a user prompt, or a configuration file).

| Category | Details |
| --- | --- |
| **Reason** | The hypothesis must be grounded in the experiment’s stated purpose, so the objective is the primary source of information. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use a predefined key (e.g., `experiment_objective`) to read the value from the context object or pass it as a function argument. |

#### 2. Validate that the objective is sufficiently descriptive by ensuring it contains a clear target variable and a condition or intervention.

| Category | Details |
| --- | --- |
| **Reason** | A vague objective will lead to an ambiguous hypothesis, reducing testability. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Apply a simple rule‑based check: the text must contain at least one noun phrase denoting a variable and one verb phrase indicating a change or condition. |

#### 3. Extract or request the independent and dependent variables from the user if they are not explicitly mentioned in the objective.

| Category | Details |
| --- | --- |
| **Reason** | A hypothesis must reference these two variable types to be scientifically valid. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | If variables are missing, prompt the user with: "Please specify the independent variable(s) and dependent variable(s) for the experiment." Capture responses in `independent_variables` and `dependent_variables` lists. |

#### 4. Construct the hypothesis sentence using a controlled template that ensures testability: "When [independent] is [modified], [dependent] will [increase/decrease/alter] accordingly."

| Category | Details |
| --- | --- |
| **Reason** | Template usage guarantees that the sentence remains single‑sentence and includes both variable types, satisfying the testable criterion. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Populate the template with the extracted variables and a suitable outcome verb. If multiple variables exist, use plural forms or multiple clauses separated by commas. |

#### 5. Apply a short grammar and length check to ensure the sentence is concise (≤ 25 words) and free of run‑on structures.

| Category | Details |
| --- | --- |
| **Reason** | Readability and clarity aid in later design steps and prevent ambiguity. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Count words and run a simple regex to detect consecutive commas or semicolons. If the check fails, adjust the template or request clarification from the user. |

#### 6. Assign the finalized sentence to the `hypothesis_sentence` output field, ensuring the string is returned exactly as produced.

| Category | Details |
| --- | --- |
| **Reason** | This completes the node’s contract with downstream nodes. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Return the string via the node’s output dictionary or API response. |


---

## interpret_results

### Description
Interprets statistical findings from the analysis stage, synthesizing them into a narrative that addresses the hypothesis and informs next steps.

### Implementation Plan

#### 1. Validate the underlying analysis by checking the `is_analysis_successful` flag from the `analyze_data` output. If the flag is `false`, immediately set `is_analysis_valid` to `false`, generate a generic interpretation stating that the analysis could not be validated, and skip further metric extraction.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that we only interpret trustworthy results, preventing misleading conclusions from flawed analyses. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Conditional branch based on boolean; short-circuit return of default values. |

#### 2. Parse the `analysis_summary`, `trend_descriptions`, `correlation_summary`, and `significant_factors` strings to extract metric names and their numeric values. Use regex patterns to locate expressions such as `p=0.03`, `r=0.65`, or `effect size=1.2`. Store extracted names in `key_metric_names` and numeric values in `key_metric_values`. If a numeric value is not present, default to `null` and note the missing value in `limitations`.

| Category | Details |
| --- | --- |
| **Reason** | Transforms human-readable statistical statements into machine‑readable lists that can be referenced in the interpretation summary. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Python regex extraction; fallback handling for missing values. |

#### 3. Determine `hypothesis_conclusion` by applying a rule set: if any `significant_factors` list is non‑empty and at least one extracted p‑value is below 0.05, set conclusion to "supported"; if all p‑values are above 0.05 and no significant factors are reported, set to "rejected"; otherwise set to "inconclusive".

| Category | Details |
| --- | --- |
| **Reason** | Provides a clear, objective mapping from statistical results to hypothesis status, aligning with conventional scientific reporting. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Logical evaluation over extracted data. |

#### 4. Construct `interpretation_summary` by concatenating: 1) a brief recap of the analysis goal, 2) the key metrics and their significance, 3) the inferred impact on the hypothesis, and 4) an overarching conclusion. Use template strings to keep the narrative concise (<200 words).

| Category | Details |
| --- | --- |
| **Reason** | Delivers a reader‑friendly synthesis that is easy to include in reports or presentations. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | String templating; insertion of dynamic content from previous steps. |

#### 5. Compile a `limitations` list that includes: (a) any missing numeric values extracted, (b) the `is_analysis_successful` status if `false`, (c) potential sample size constraints inferred from `sample_size` in the design stage (via additional context if available), and (d) any anomalies flagged during data collection.

| Category | Details |
| --- | --- |
| **Reason** | Transparency about data and analysis quality is essential for reproducibility and for guiding future work. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Aggregation of context from parent nodes and analysis flags. |

#### 6. Generate a `recommendations` list that suggests: 1) replication with larger sample size if inconclusive, 2) refinement of measurement methods if high variance observed, 3) further investigation of any unexpected correlations, and 4) immediate next experimental steps based on the conclusion.

| Category | Details |
| --- | --- |
| **Reason** | Provides actionable guidance for researchers to build upon the current findings. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Rule‑based mapping from conclusion and limitations to next steps. |

#### 7. Calculate a `confidence_score` as the product of three components: (i) a binary factor of 1 if `is_analysis_successful` is true else 0, (ii) an average of extracted p‑values normalized to 0–1 (higher significance → higher score), and (iii) a penalty factor of 0.5 if any limitations were recorded. Clamp the result to the 0–1 range.

| Category | Details |
| --- | --- |
| **Reason** | Quantifies the overall trustworthiness of the interpretation, enabling downstream nodes to make informed decisions. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Arithmetic operations and conditional logic. |

#### 8. Populate the final output fields with the derived values: `interpretation_summary`, `hypothesis_conclusion`, `key_metric_names`, `key_metric_values`, `limitations`, `recommendations`, `confidence_score`, and `is_analysis_valid`. Ensure data types exactly match the specified schema and that lists are properly ordered.

| Category | Details |
| --- | --- |
| **Reason** | Conforms to the node's contract, guaranteeing compatibility with downstream nodes like `draw_conclusion` and `document_experiment`. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Dictionary assembly and type validation. |


---

## prepare_materials

### Description
Prepare the necessary materials and equipment required for the experiment based on the design specifications.

### Implementation Plan

#### 1. Retrieve the full design_experiment output and deserialize the JSON into an in-memory object.

| Category | Details |
| --- | --- |
| **Reason** | The design_experiment output contains the experiment variables and protocol which dictate material requirements. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use a JSON parser to load design_experiment JSON into a dictionary or a typed data class. Validate all required keys exist. |

#### 2. Map each measurement method and dependent variable to its specific instrument or consumable (e.g., a pH meter for pH measurement).

| Category | Details |
| --- | --- |
| **Reason** | Accurately linking measurement needs to physical items ensures no gaps in equipment. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Implement a lookup table (dictionary) mapping variable names to instrument/consumable types. Apply fallback rules for unspecified variables. |

#### 3. Enumerate required reagents, chemicals, and labware by cross-referencing independent variables, dependent variables, and sample size.

| Category | Details |
| --- | --- |
| **Reason** | The quantity of consumables depends on how many samples and repetitions are planned. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | For each sample unit, multiply reagent volumes by sample_size. Add safety margins (e.g., +10%). Use unit conversion functions to standardize measurements. |

#### 4. Validate availability of each item by querying the laboratory inventory system (or a static inventory list).

| Category | Details |
| --- | --- |
| **Reason** | Prevents delays during execution due to missing items. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Call an inventory API or read a CSV of available items. If an item is out of stock, flag a warning and suggest an alternative or reorder. |

#### 5. Calculate the cost of each item by multiplying the unit price by the required quantity.

| Category | Details |
| --- | --- |
| **Reason** | Provides a financial estimate needed for budgeting. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Store unit prices in a price catalog dictionary. Perform arithmetic operations and sum totals. Round to two decimal places. |

#### 6. Aggregate all items, quantities, and costs into the required_items, quantities, and total_cost output fields.

| Category | Details |
| --- | --- |
| **Reason** | Organizes data into the defined output structure for downstream nodes. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Append each item, quantity, and cost to respective lists; compute total_cost as sum of item costs. |

#### 7. Set is_prepared to True only after confirming all items are available, quantities match calculations, and cost estimate is finalized.

| Category | Details |
| --- | --- |
| **Reason** | Guarantees that the experiment will not halt due to missing resources. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | If any availability check fails or quantity mismatch occurs, set is_prepared to False and record details in preparation_notes. |

#### 8. Compile a detailed preparation_notes string that logs any substitutions, special handling instructions, or procurement actions taken.

| Category | Details |
| --- | --- |
| **Reason** | Provides traceability and context for future troubleshooting. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Concatenate status messages from prior steps, include timestamps, and format as a multiline string. |
