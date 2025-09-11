# interpret_results PRD

## Description
Interprets statistical findings from the analysis stage, synthesizing them into a narrative that addresses the hypothesis and informs next steps.


## Implementation Plan

### 1. Validate the underlying analysis by checking the `is_analysis_successful` flag from the `analyze_data` output. If the flag is `false`, immediately set `is_analysis_valid` to `false`, generate a generic interpretation stating that the analysis could not be validated, and skip further metric extraction.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that we only interpret trustworthy results, preventing misleading conclusions from flawed analyses. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Conditional branch based on boolean; short-circuit return of default values. |

### 2. Parse the `analysis_summary`, `trend_descriptions`, `correlation_summary`, and `significant_factors` strings to extract metric names and their numeric values. Use regex patterns to locate expressions such as `p=0.03`, `r=0.65`, or `effect size=1.2`. Store extracted names in `key_metric_names` and numeric values in `key_metric_values`. If a numeric value is not present, default to `null` and note the missing value in `limitations`.

| Category | Details |
| --- | --- |
| **Reason** | Transforms human-readable statistical statements into machine‑readable lists that can be referenced in the interpretation summary. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Python regex extraction; fallback handling for missing values. |

### 3. Determine `hypothesis_conclusion` by applying a rule set: if any `significant_factors` list is non‑empty and at least one extracted p‑value is below 0.05, set conclusion to "supported"; if all p‑values are above 0.05 and no significant factors are reported, set to "rejected"; otherwise set to "inconclusive".

| Category | Details |
| --- | --- |
| **Reason** | Provides a clear, objective mapping from statistical results to hypothesis status, aligning with conventional scientific reporting. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Logical evaluation over extracted data. |

### 4. Construct `interpretation_summary` by concatenating: 1) a brief recap of the analysis goal, 2) the key metrics and their significance, 3) the inferred impact on the hypothesis, and 4) an overarching conclusion. Use template strings to keep the narrative concise (<200 words).

| Category | Details |
| --- | --- |
| **Reason** | Delivers a reader‑friendly synthesis that is easy to include in reports or presentations. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | String templating; insertion of dynamic content from previous steps. |

### 5. Compile a `limitations` list that includes: (a) any missing numeric values extracted, (b) the `is_analysis_successful` status if `false`, (c) potential sample size constraints inferred from `sample_size` in the design stage (via additional context if available), and (d) any anomalies flagged during data collection.

| Category | Details |
| --- | --- |
| **Reason** | Transparency about data and analysis quality is essential for reproducibility and for guiding future work. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Aggregation of context from parent nodes and analysis flags. |

### 6. Generate a `recommendations` list that suggests: 1) replication with larger sample size if inconclusive, 2) refinement of measurement methods if high variance observed, 3) further investigation of any unexpected correlations, and 4) immediate next experimental steps based on the conclusion.

| Category | Details |
| --- | --- |
| **Reason** | Provides actionable guidance for researchers to build upon the current findings. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Rule‑based mapping from conclusion and limitations to next steps. |

### 7. Calculate a `confidence_score` as the product of three components: (i) a binary factor of 1 if `is_analysis_successful` is true else 0, (ii) an average of extracted p‑values normalized to 0–1 (higher significance → higher score), and (iii) a penalty factor of 0.5 if any limitations were recorded. Clamp the result to the 0–1 range.

| Category | Details |
| --- | --- |
| **Reason** | Quantifies the overall trustworthiness of the interpretation, enabling downstream nodes to make informed decisions. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Arithmetic operations and conditional logic. |

### 8. Populate the final output fields with the derived values: `interpretation_summary`, `hypothesis_conclusion`, `key_metric_names`, `key_metric_values`, `limitations`, `recommendations`, `confidence_score`, and `is_analysis_valid`. Ensure data types exactly match the specified schema and that lists are properly ordered.

| Category | Details |
| --- | --- |
| **Reason** | Conforms to the node's contract, guaranteeing compatibility with downstream nodes like `draw_conclusion` and `document_experiment`. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Dictionary assembly and type validation. |
