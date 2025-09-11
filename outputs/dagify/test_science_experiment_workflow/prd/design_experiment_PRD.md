# design_experiment PRD

## Description
Design the experiment to test the hypothesis


## Implementation Plan

### 1. 1️⃣ Extract the single-sentence hypothesis from the parent node *formulate_hypothesis* and assign it to the `hypothesis` field.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the hypothesis is directly inherited and not re-formulated, maintaining consistency across the workflow. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Parse the parent output `hypothesis_sentence`, trim whitespace, and store as `hypothesis`. |

### 2. 2️⃣ Identify all factors relevant to the research objective that can be intentionally manipulated by the experimenter; list them in the `independent_variables` field.

| Category | Details |
| --- | --- |
| **Reason** | Independent variables are the key drivers that the experiment will test, directly affecting the outcome. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Apply a knowledge‑base lookup of standard experimental variables for the domain; filter by relevance; ensure at least two distinct levels per variable to allow statistical analysis. |

### 3. 3️⃣ For each independent variable, determine the measurable outcome(s) it is expected to influence; compile these into the `dependent_variables` list.

| Category | Details |
| --- | --- |
| **Reason** | Dependent variables represent the experiment’s outcomes, enabling quantitative evaluation of the hypothesis. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Map each independent variable to its theoretical effect using causal diagrams; cross‑check with the hypothesis statement; avoid duplication. |

### 4. 4️⃣ Enumerate all environmental or procedural factors that must remain constant across trials to prevent confounding; place them in `control_variables`.

| Category | Details |
| --- | --- |
| **Reason** | Controls isolate the effect of independent variables, ensuring validity. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | List temperature, humidity, equipment calibration, operator, timing, and any other potentially influencing factors; confirm via a design-of-experiments checklist. |

### 5. 5️⃣ For each dependent variable, specify the measurement instrument or protocol (e.g., spectrophotometer reading, time‑to‑completion, survey score) and store the description in `measurement_methods`.

| Category | Details |
| --- | --- |
| **Reason** | Clear measurement methods enable reproducibility and data integrity. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Match each dependent variable with an appropriate instrument from the domain’s standard equipment list; document calibration steps and unit conventions. |

### 6. 6️⃣ Calculate the required `sample_size` using a power analysis that incorporates the expected effect size, alpha level (commonly 0.05), desired power (commonly 0.8), and the number of independent variables.

| Category | Details |
| --- | --- |
| **Reason** | Adequate sample size ensures statistical validity and mitigates Type II error. |
| **Impact** | HIGH |
| **Complexity** | HIGH |
| **Method** | Employ a statistical software API (e.g., G*Power, scipy.stats) with effect size from pilot data or literature; round up to nearest integer; enforce a minimum threshold (e.g., 30 per group) if calculation yields low numbers. |

### 7. 7️⃣ Draft a comprehensive `experimental_protocol` string that sequences the experiment from preparation to data capture, including safety checks, randomization, blinding (if applicable), and data logging procedures.

| Category | Details |
| --- | --- |
| **Reason** | A detailed protocol guarantees consistency across multiple trials and operators. |
| **Impact** | HIGH |
| **Complexity** | HIGH |
| **Method** | Structure the protocol in numbered paragraphs: (1) Setup, (2) Calibration, (3) Randomization of treatment groups, (4) Execution steps for each trial, (5) Data recording, (6) Decontamination, (7) Safety checks. Embed placeholders for variable values (e.g., `{{temperature}}`). |

### 8. 8️⃣ Validate the design by performing a quick risk assessment and ensuring all safety protocols are feasible within the defined experimental setting.

| Category | Details |
| --- | --- |
| **Reason** | Prevents experiment abortion due to oversight of safety or regulatory compliance. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Cross‑reference the protocol with institutional safety guidelines; flag any missing PPE or hazard mitigation steps. |

### 9. 9️⃣ Review the entire output dictionary for type consistency and completeness before returning it to the workflow engine.

| Category | Details |
| --- | --- |
| **Reason** | Type mismatches would cause downstream node failures. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Automate a schema validation routine: assert `hypothesis` is string, `independent_variables` is list of strings, etc.; generate error logs for missing fields. |
