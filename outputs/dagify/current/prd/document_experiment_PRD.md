# document_experiment PRD

## Description
Document the entire experiment process and findings.


## Implementation Plan

### 1. Extract the hypothesis sentence from the `formulate_hypothesis` node output and store it in the `hypothesis` field.

| Category | Details |
| --- | --- |
| **Reason** | The hypothesis is the foundational statement that guides all subsequent sections of the report. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Retrieve `hypothesis_sentence` directly; perform a shallow copy to `hypothesis`. |

### 2. Synthesize the experimental design details from the `design_experiment` node output into a concise paragraph for `design_summary`.

| Category | Details |
| --- | --- |
| **Reason** | A clear design summary ensures readers understand the methodology, variables, and controls. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Concatenate the following fields: `hypothesis`, `independent_variables`, `dependent_variables`, `control_variables`, `measurement_methods`, and `experimental_protocol`. Apply sentence templating to maintain readability. |

### 3. Create a data collection overview by aggregating metrics from the `collect_data` node (`observation_count`, `data_values`, `is_data_valid`, `observation_notes`).

| Category | Details |
| --- | --- |
| **Reason** | Summarizing raw data quality and volume gives transparency to the data foundation. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Generate a paragraph stating the total observations, the range of data values, any validation flags, and highlight notable observation notes. Format numeric summaries using statistical descriptors (mean, median, std). |

### 4. Compose the `analysis_summary` section by summarizing key outputs from the `analyze_data` node (`analysis_summary`, `trend_descriptions`, `correlation_summary`, `significant_factors`).

| Category | Details |
| --- | --- |
| **Reason** | Providing a high‑level analytical narrative bridges raw data and scientific interpretation. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Insert the provided `analysis_summary` verbatim. Append bullet points for each trend, correlation, and significant factor. Use LaTeX for correlation coefficients if necessary. |

### 5. Integrate the interpretation text from the `interpret_results` node into the `interpretation` field, ensuring it references the hypothesis and key metrics.

| Category | Details |
| --- | --- |
| **Reason** | Interpretation contextualizes statistical findings within the experimental question. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Copy `interpretation_summary` and optionally prepend a sentence linking it to the hypothesis. Verify that all `key_metric_names` and `key_metric_values` are mentioned. |

### 6. Generate the final `conclusion` field by combining `hypothesis_support` and `conclusion_text` from the `draw_conclusion` node.

| Category | Details |
| --- | --- |
| **Reason** | The conclusion must clearly state support status and summarise overall findings. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | If `hypothesis_support` is true, prepend "The hypothesis is supported;" otherwise prepend "The hypothesis is rejected;" then append `conclusion_text`. |

### 7. Create a list of visual aid references for `visual_aids` by collating file names of graphs and diagrams generated during the analysis phase (e.g., "temperature_over_time.png", "correlation_matrix.pdf").

| Category | Details |
| --- | --- |
| **Reason** | Visual aids enhance comprehension of complex data. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Query the analysis module for generated graph files. If none are available, generate new plots using matplotlib or seaborn based on the data arrays. Store each filename in the list. |

### 8. Determine the `report_title` by embedding the hypothesis into a standardized title format, e.g., "Experiment Report: [Hypothesis]".

| Category | Details |
| --- | --- |
| **Reason** | A descriptive title improves searchability and context. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Concatenate a prefix string with the `hypothesis` value, truncating if necessary to stay within 80 characters. |

### 9. Validate that all required fields are non‑empty and set `is_complete` to true only when all validation checks pass.

| Category | Details |
| --- | --- |
| **Reason** | Ensures report integrity before downstream consumption. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Iterate over all output fields, checking string length > 0 or list length > 0. If any fail, set `is_complete` to false and log the missing field. |

### 10. Serialize the assembled report into JSON format, matching the specified output structure, and return it as the node's result.

| Category | Details |
| --- | --- |
| **Reason** | Consistent JSON output allows automatic ingestion by downstream systems. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Construct a Python dict with keys matching the output structure and convert it using `json.dumps`. |
