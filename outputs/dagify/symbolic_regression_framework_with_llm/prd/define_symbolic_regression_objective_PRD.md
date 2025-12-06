# define_symbolic_regression_objective PRD

## Description
Define the objective and scope of the symbolic regression task by collecting a high‑level problem statement, identifying the dependent and independent variables, and setting constraints and performance metrics.


## Implementation Plan

### 1. Create a structured questionnaire template that includes sections for a problem narrative, target variable selection, feature list, constraints, metrics, and dataset description, ensuring each field has a clear label, tooltip, and validation rules.

| Category | Details |
| --- | --- |
| **Reason** | A structured template reduces ambiguity, guides the user to provide all necessary information, and enables automated parsing of responses. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Design the template using JSON Schema, enforce required fields, and include regex validators for variable names. Use a front‑end form library (e.g., React with Formik) to render the questionnaire. |

### 2. Pre‑populate the template with defaults derived from the dataset metadata when available (e.g., infer feature names from column headers, suggest common metrics like R² and MAE).

| Category | Details |
| --- | --- |
| **Reason** | Providing sensible defaults speeds up input and reduces errors, especially for large feature sets. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Write a script that reads the first row of the CSV or Parquet file, extracts column names, and maps them to feature_variables. Use a lookup table for standard metrics. |

### 3. Implement a validation step that checks for consistency: target_variable must be one of the column names; at least two feature_variables must be provided; constraints must reference existing variables.

| Category | Details |
| --- | --- |
| **Reason** | Early validation prevents downstream failures in LLM prompts and model generation. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use a Python validation library (pydantic or marshmallow) to enforce these rules and produce user‑friendly error messages. |

### 4. Generate the objective_description by concatenating the problem narrative with the selected target and feature set, using a templated sentence: "Develop a symbolic regression model to predict [target_variable] as a function of [feature_variables], under the constraints: [constraints], aiming to optimize [performance_metrics]."

| Category | Details |
| --- | --- |
| **Reason** | Automating the description ensures consistency and embeds all essential information for the LLM prompt. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Implement a simple string interpolation routine in Python, using list joins for arrays, and trim whitespace. |

### 5. Export the completed response as a JSON object matching the defined output structure, and store it in a central repository or pass it directly to the next node via a message queue.

| Category | Details |
| --- | --- |
| **Reason** | Structured JSON enables downstream nodes to consume the data without manual parsing. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use Python's `json` module to serialize the dictionary, validate against the JSON Schema, and push to an in‑memory store (e.g., Redis) or a workflow engine's state store. |
