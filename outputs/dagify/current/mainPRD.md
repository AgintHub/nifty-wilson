# symbolic_regression_framework_with_llm - Complete PRD Documentation

## Overview
PRDs for nodes in the 'symbolic_regression_framework_with_llm' module.

## Table of Contents

- [configure_llm_for_proposal_generation](#configure_llm_for_proposal_generation)

- [define_symbolic_regression_objective](#define_symbolic_regression_objective)

- [evaluate_proposal_quality](#evaluate_proposal_quality)

- [finalize_symbolic_regression_framework](#finalize_symbolic_regression_framework)

- [generate_symbolic_regression_proposals](#generate_symbolic_regression_proposals)

- [integrate_refined_proposals_into_framework](#integrate_refined_proposals_into_framework)

- [refine_selected_proposals](#refine_selected_proposals)

- [select_top_proposals](#select_top_proposals)

- [test_symbolic_regression_framework](#test_symbolic_regression_framework)



---

## configure_llm_for_proposal_generation

### Description
Configure all necessary LLM parameters and templates to produce symbolic regression proposals that respect the defined objective, constraints, and data schema.

### Implementation Plan

#### 1. Parse the parent output to extract the objective description, target variable, feature variables, constraints, performance metrics, and dataset description.

| Category | Details |
| --- | --- |
| **Reason** | These elements inform the LLM configuration and prompt template to ensure proposals align with the task. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use JSON parsing and schema validation to map parent fields to local variables, ensuring no required field is missing. |

#### 2. Select a default model name based on the target language and available API endpoints; fallback to a safe open‑source model if the preferred one is unavailable.

| Category | Details |
| --- | --- |
| **Reason** | Model choice directly affects proposal quality and latency. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Define a priority list (e.g., ["gpt-4o", "llama-3.1", "openai-gpt-3.5"]), query availability via the provider SDK, and choose the first available model. |

#### 3. Determine the temperature setting by balancing exploration and precision; default to 0.2 for symbolic regression to favor deterministic, interpretable formulas.

| Category | Details |
| --- | --- |
| **Reason** | Lower temperature reduces randomness, producing more stable symbolic expressions suitable for downstream evaluation. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | If constraints specify strict compliance, enforce temperature ≤ 0.3; otherwise use a heuristic based on the complexity of feature_variables. |

#### 4. Compute max_tokens by estimating the typical length of symbolic expressions from past runs and adding a buffer; use a formula such as max_tokens = 2 * (number_of_features * 5).

| Category | Details |
| --- | --- |
| **Reason** | Ensures enough token space for complex expressions without wasting resources. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Implement a lightweight estimator that counts tokens for a sample expression and scales accordingly. |

#### 5. Construct a prompt_template that injects the objective and dataset description, and includes placeholders for the model to output a single symbolic expression per sample. The template should be JSON‑serializable and contain a clear instruction section.

| Category | Details |
| --- | --- |
| **Reason** | A well‑structured template reduces hallucinations and improves the LLM's focus on symbolic content. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Define the template as a Python multiline string with `{objective}`, `{data_description}`, and `{target_variable}` placeholders. Wrap instructions in a JSON object with keys "instruction" and "input" for compatibility with many LLM APIs. |

#### 6. Generate an input_schema string that describes the expected JSON input the LLM will receive during generation. Include fields for feature_variables, target_variable, and constraints, with data types and example values.

| Category | Details |
| --- | --- |
| **Reason** | Providing a concrete schema guides the LLM in generating syntactically correct expressions and aids downstream validation. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Serialize a Python dictionary to pretty‑printed JSON and embed it in the prompt_template or provide it as a separate configuration field. |

#### 7. Decide the number of proposals (num_proposals) by evaluating the size of the feature set and the evaluation budget; default to 10 proposals for moderate feature sizes, scaling up to 20 if computational resources allow.

| Category | Details |
| --- | --- |
| **Reason** | More proposals increase the chance of finding high‑quality formulas but consume more API calls. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Implement a rule: if len(feature_variables) > 10 then num_proposals = 20 else num_proposals = 10; allow overrides via an optional configuration flag. |


---

## define_symbolic_regression_objective

### Description
Define the objective and scope of the symbolic regression task by collecting a high‑level problem statement, identifying the dependent and independent variables, and setting constraints and performance metrics.

### Implementation Plan

#### 1. Create a structured questionnaire template that includes sections for a problem narrative, target variable selection, feature list, constraints, metrics, and dataset description, ensuring each field has a clear label, tooltip, and validation rules.

| Category | Details |
| --- | --- |
| **Reason** | A structured template reduces ambiguity, guides the user to provide all necessary information, and enables automated parsing of responses. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Design the template using JSON Schema, enforce required fields, and include regex validators for variable names. Use a front‑end form library (e.g., React with Formik) to render the questionnaire. |

#### 2. Pre‑populate the template with defaults derived from the dataset metadata when available (e.g., infer feature names from column headers, suggest common metrics like R² and MAE).

| Category | Details |
| --- | --- |
| **Reason** | Providing sensible defaults speeds up input and reduces errors, especially for large feature sets. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Write a script that reads the first row of the CSV or Parquet file, extracts column names, and maps them to feature_variables. Use a lookup table for standard metrics. |

#### 3. Implement a validation step that checks for consistency: target_variable must be one of the column names; at least two feature_variables must be provided; constraints must reference existing variables.

| Category | Details |
| --- | --- |
| **Reason** | Early validation prevents downstream failures in LLM prompts and model generation. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use a Python validation library (pydantic or marshmallow) to enforce these rules and produce user‑friendly error messages. |

#### 4. Generate the objective_description by concatenating the problem narrative with the selected target and feature set, using a templated sentence: "Develop a symbolic regression model to predict [target_variable] as a function of [feature_variables], under the constraints: [constraints], aiming to optimize [performance_metrics]."

| Category | Details |
| --- | --- |
| **Reason** | Automating the description ensures consistency and embeds all essential information for the LLM prompt. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Implement a simple string interpolation routine in Python, using list joins for arrays, and trim whitespace. |

#### 5. Export the completed response as a JSON object matching the defined output structure, and store it in a central repository or pass it directly to the next node via a message queue.

| Category | Details |
| --- | --- |
| **Reason** | Structured JSON enables downstream nodes to consume the data without manual parsing. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use Python's `json` module to serialize the dictionary, validate against the JSON Schema, and push to an in‑memory store (e.g., Redis) or a workflow engine's state store. |


---

## evaluate_proposal_quality

### Description
Assess the generated proposals using relevant metrics such as accuracy, complexity, and interpretability.

### Implementation Plan

#### 1. Validate the `proposals_valid` flag from the parent node and abort evaluation if it is false.

| Category | Details |
| --- | --- |
| **Reason** | Early exit avoids wasted computation on syntactically invalid proposals. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Simple boolean check; log and return empty lists if false. |

#### 2. Assign a deterministic unique identifier to each proposal by concatenating the node name with its index (e.g., `eval_0`).

| Category | Details |
| --- | --- |
| **Reason** | Consistent IDs are required for downstream selection and traceability. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Iterate over `proposal_expressions` and generate ID strings. |

#### 3. Parse each proposal string into an evaluatable expression tree using SymPy or a similar symbolic library.

| Category | Details |
| --- | --- |
| **Reason** | Converting to a parse tree allows systematic traversal for metric calculations. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use `sympy.sympify`; handle parsing errors with try‑except and mark such proposals as invalid. |

#### 4. Load the training dataset from the `define_symbolic_regression_objective` context, ensuring alignment of feature and target variables.

| Category | Details |
| --- | --- |
| **Reason** | Accuracy metrics require actual data for prediction. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Read CSV/SQL or use pre‑loaded DataFrame; validate column names match `feature_variables` and `target_variable`. |

#### 5. For each expression, evaluate predictions on the training dataset by substituting feature values.

| Category | Details |
| --- | --- |
| **Reason** | Predictions are needed to compute accuracy. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Vectorize evaluation using `numpy` arrays; handle division by zero and overflow by clipping results. |

#### 6. Compute the accuracy metric as the coefficient of determination R². If R² calculation fails (e.g., constant prediction), fall back to negative mean squared error.

| Category | Details |
| --- | --- |
| **Reason** | R² provides an interpretable measure of explained variance; fallback ensures metric availability. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use `sklearn.metrics.r2_score`; compute MSE with `sklearn.metrics.mean_squared_error` if required. |

#### 7. Calculate the structural complexity as the number of operators plus parentheses depth, normalizing by the maximum complexity seen across proposals.

| Category | Details |
| --- | --- |
| **Reason** | Normalized complexity facilitates fair comparison and weighting. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Traverse the SymPy expression tree; count nodes and compute depth; divide by max across all proposals. |

#### 8. Derive an interpretability score between 0 and 1 using a heuristic that penalizes nested functions, uncommon operators, and excessive variable usage.

| Category | Details |
| --- | --- |
| **Reason** | Interpretability is subjective; a rule‑based heuristic offers consistency. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Compute a raw score as: 1 - (depth / max_depth + operator_penalty + variable_penalty); clip to [0,1]. |

#### 9. Combine accuracy, inverse complexity, and interpretability into an overall quality score using the weighting scheme 0.4, 0.3, 0.3 respectively.

| Category | Details |
| --- | --- |
| **Reason** | Weighted sum balances performance with simplicity and human readability. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | overall_quality = 0.4*accuracy + 0.3*(1 - normalized_complexity) + 0.3*interpretability. |

#### 10. Collect all computed metrics into lists aligned with proposal IDs and output them following the defined schema.

| Category | Details |
| --- | --- |
| **Reason** | Structured output is required for downstream nodes. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Append each metric to its respective list; ensure all lists share the same length. |

#### 11. Log any proposals that triggered warnings (e.g., division by zero, overflow) and optionally set their metrics to NaN to flag them for review.

| Category | Details |
| --- | --- |
| **Reason** | Transparency in evaluation aids debugging and future refinement. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use Python logging; set metric values to `float('nan')`. |


---

## finalize_symbolic_regression_framework

### Description
Finalizes the symbolic regression framework by applying adjustments informed by test results, ensuring robustness and documenting the outcome.

### Implementation Plan

#### 1. Retrieve test results from the parent node and store each field in local variables for analysis.

| Category | Details |
| --- | --- |
| **Reason** | Ensures all necessary metrics are available for decision making. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Destructure the JSON object received from *test_symbolic_regression_framework* into variables: test_accuracy, test_rmse, test_runtime_seconds, test_success, test_dataset_names, test_summary. |

#### 2. Validate `test_success`. If `False`, log the failure reasons from `test_summary` and exit the adjustment process early, returning the original framework version and a robustness flag of `False`.

| Category | Details |
| --- | --- |
| **Reason** | Prevents unnecessary computations when foundational performance criteria are not met. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Implement a conditional guard: if !test_success then set framework_version = original, adjustments_summary = 'No changes due to failure', is_framework_robust = False, and skip further steps. |

#### 3. Examine `test_accuracy` and `test_rmse` against predefined thresholds (e.g., accuracy ≥ 0.90, RMSE ≤ 0.05). If either metric is outside the acceptable range, schedule a hyper‑parameter tuning session using the best‑performing proposals.

| Category | Details |
| --- | --- |
| **Reason** | Directly targets the primary predictive quality metrics. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Compare metrics to thresholds; if violated, invoke a tuning routine that re‑optimizes parameters such as mutation rate, population size, or expression depth. |

#### 4. Retrieve the list of integrated symbolic proposals from the *integrate_refined_proposals_into_framework* node, which contains `integrated_proposals` and `integration_log`.

| Category | Details |
| --- | --- |
| **Reason** | These expressions are the basis for computing complexity and interpretability. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Query the system cache or storage for the outputs of *integrate_refined_proposals_into_framework*; extract the `integrated_proposals` array. |

#### 5. Compute `final_performance_complexity` by parsing each integrated expression with SymPy, counting the number of operators and the depth of the syntax tree, and aggregating the results (e.g., average operator count).

| Category | Details |
| --- | --- |
| **Reason** | Provides an objective, quantifiable measure of model size that aligns with the complexity metric. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | For each expression, use `sympy.sympify` to create an expression tree, then traverse the tree to count operators (`+`, `-`, `*`, `/`, `**`, `log`, etc.) and compute tree depth. Sum or average across all expressions to produce a single float. |

#### 6. Estimate `final_performance_interpretability` by applying an interpretability heuristic: assign a base score of 1.0 for expressions containing only arithmetic operators and 0 for those that include non‑standard functions (e.g., `exp`, `sin`, `log`). Weight scores by the inverse of tree depth and average across expressions.

| Category | Details |
| --- | --- |
| **Reason** | Captures human readability while penalizing deep, complex structures. |
| **Impact** | LOW |
| **Complexity** | MEDIUM |
| **Method** | For each expression, check for presence of functions beyond `+`, `-`, `*`, `/`. Compute depth via SymPy; interpretability_score = (is_simple ? 1.0 : 0.0) / (depth + 1). Aggregate across proposals. |

#### 7. Determine the new `framework_version` by incrementing the minor semantic version if adjustments are minor (e.g., only tuning or simplification), or the major version if a structural redesign (e.g., new integration strategy) was performed.

| Category | Details |
| --- | --- |
| **Reason** | Versioning communicates the extent of changes to downstream users. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Parse the current framework version string (e.g., `v1.2`), apply semantic versioning rules: if any tuning or simplification changes only, increment minor; if architecture changes, increment major and reset minor. |

#### 8. Compose an `adjustments_summary` that lists each change made, including the type of adjustment (tuning, simplification, re‑integration) and its quantitative impact (e.g., accuracy improvement, complexity reduction).

| Category | Details |
| --- | --- |
| **Reason** | Provides traceability and aids future maintenance. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Build a string by concatenating bullet points: e.g., '- Tuned mutation rate from 0.05 to 0.02, improving accuracy by 0.004'. |

#### 9. Set `is_framework_robust` to `True` only if `test_success` is `True` and `test_accuracy` ≥ 0.90, `test_rmse` ≤ 0.05, `final_performance_complexity` ≤ acceptable complexity threshold, and `final_performance_interpretability` ≥ 0.7.

| Category | Details |
| --- | --- |
| **Reason** | Defines a comprehensive robustness criterion covering accuracy, error, complexity, and interpretability. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Implement a boolean expression that evaluates all conditions; assign result to `is_framework_robust`. |

#### 10. Populate the output JSON with the computed fields: `framework_version`, `adjustments_summary`, `is_framework_robust`, `final_performance_accuracy`, `final_performance_complexity`, and `final_performance_interpretability`.

| Category | Details |
| --- | --- |
| **Reason** | Produces the final artifact expected by downstream nodes. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Serialize the variables into the prescribed JSON schema. |


---

## generate_symbolic_regression_proposals

### Description
Generate proposals for symbolic regression using the configured LLM

### Implementation Plan

#### 1. Retrieve LLM configuration parameters from the parent node `configure_llm_for_proposal_generation`.

| Category | Details |
| --- | --- |
| **Reason** | The LLM must be invoked with the same parameters that were intentionally configured for proposal generation to ensure consistent behavior. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Deserialize the parent output JSON into a dictionary and extract keys: model_name, temperature, max_tokens, prompt_template, input_schema, num_proposals. |

#### 2. Validate and transform the objective description and dataset into a JSON payload that matches `input_schema`.

| Category | Details |
| --- | --- |
| **Reason** | The LLM prompt template expects structured data; mismatched formats will cause the model to fail or produce nonsense. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Parse `define_symbolic_regression_objective` output; create a JSON object with keys: objective_description, target_variable, feature_variables, constraints, performance_metrics, dataset_description. Use JSON schema validation libraries to enforce `input_schema` compliance. |

#### 3. Populate the `prompt_template` with the objective JSON and any required placeholders.

| Category | Details |
| --- | --- |
| **Reason** | Embedding the objective and data into the prompt ensures the LLM generates contextually relevant expressions. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use Python f-string or `jinja2` templating to replace placeholders like {{objective_json}} within the template. |

#### 4. Invoke the LLM using the specified `model_name`, `temperature`, `max_tokens`, and `num_proposals`.

| Category | Details |
| --- | --- |
| **Reason** | Directly controlling sampling and token limits guarantees the output stays within the desired size and diversity. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use the OpenAI or vendor-specific SDK to call `model_name` with `temperature` and `max_tokens`. If `num_proposals` > 1, loop or use `n` sampling parameter. Capture raw text responses. |

#### 5. Parse the raw LLM output into individual proposal strings.

| Category | Details |
| --- | --- |
| **Reason** | The LLM may return proposals separated by newlines, bullets, or JSON; a robust parser reduces errors. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | First, attempt to parse as JSON array. If fails, split by newline and regex pattern `^Proposal \d+: (.+)$`. Clean leading/trailing whitespace. |

#### 6. Validate syntactic correctness of each proposal expression using a symbolic algebra parser.

| Category | Details |
| --- | --- |
| **Reason** | Invalid expressions would corrupt downstream evaluation and evaluation metrics. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Utilize `sympy.sympify` in a try/except block for each expression. If parsing fails, mark the entire set as invalid and log the error. |

#### 7. Compute a complexity score for each proposal.

| Category | Details |
| --- | --- |
| **Reason** | Complexity is a key evaluation metric and required output. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Parse the expression into an AST using `sympy` and count nodes (operators, functions). Return the node count as an integer. |

#### 8. Assign a confidence score for each proposal.

| Category | Details |
| --- | --- |
| **Reason** | Confidence informs downstream ranking and selection. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | If LLM provides a probability (e.g., via logit or explicit field), normalize to [0,1]. Otherwise, use uniform confidence of 1/num_proposals or apply a simple heuristic based on expression length (shorter = higher confidence). |

#### 9. Aggregate all metrics into the final output dictionary and set `proposal_count` and `proposals_valid`.

| Category | Details |
| --- | --- |
| **Reason** | Ensures conformity to the defined output schema and provides a clear success flag. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Collect lists of expressions, complexities, confidences; compute len(list) for proposal_count; set proposals_valid to True if all expressions parsed successfully, else False. |


---

## integrate_refined_proposals_into_framework

### Description
Take the list of refined symbolic regression expressions, validate and adapt them to the framework’s internal representation, register them for future use, and produce a concise integration log.

### Implementation Plan

#### 1. Retrieve the `refined_proposals` list from the parent node and initialize an empty list `integrated_proposals`.

| Category | Details |
| --- | --- |
| **Reason** | Establish a working container for the processed equations. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Direct list assignment and initialization. |

#### 2. For each equation string in `refined_proposals`, perform syntactic validation using the framework’s parser to ensure the expression is tree‑compliant and free of undefined variables.

| Category | Details |
| --- | --- |
| **Reason** | Guarantees that only syntactically valid equations proceed to integration, preventing downstream failures. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Apply the framework’s `parse_expression` API; catch and log parsing errors. |

#### 3. Cross‑check each validated equation against the framework’s constraint set (e.g., variable names, allowed operators) derived from `define_symbolic_regression_objective`.

| Category | Details |
| --- | --- |
| **Reason** | Enforces domain constraints specified in the objective definition, ensuring model feasibility. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Iterate over constraint list, flag mismatches, and record a validation status. |

#### 4. Transform each validated string into an internal `SymbolicModel` object by invoking the framework’s `build_model` routine, capturing metadata such as complexity score and operator counts.

| Category | Details |
| --- | --- |
| **Reason** | Converts raw text into an executable model representation for later use in training/testing. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Call `framework.build_model(eq_str)`; store returned object in a registry. |

#### 5. Register each `SymbolicModel` instance in the framework’s global model registry under a unique identifier (e.g., UUID or proposal ID).

| Category | Details |
| --- | --- |
| **Reason** | Allows the framework and downstream nodes (e.g., testing) to reference the integrated models consistently. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use `framework.register_model(model_obj, id)` with collision handling. |

#### 6. After all proposals are processed, compile a summary: count of successful integrations, any failures, and overall status flag based on whether any model failed validation or registration.

| Category | Details |
| --- | --- |
| **Reason** | Provides a concise, machine‑readable result for downstream nodes. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Aggregate boolean flags and counts; set `integration_success` accordingly. |

#### 7. Generate a human‑readable `integration_log` capturing timestamps, number of proposals, validation errors, registration steps, and a short success/failure message.

| Category | Details |
| --- | --- |
| **Reason** | Facilitates debugging, audit trails, and stakeholder communication. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | String concatenation using a formatted log template. |

#### 8. If any proposal failed validation, record the specific reason and exclude it from `integrated_proposals`; otherwise, include the fully registered model’s string representation.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the output list reflects only usable models and prevents downstream errors. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Conditional appending based on validation flag. |

#### 9. Return the final outputs: `integrated_proposals` (list of strings), `integration_success` (bool), `integrated_count` (int), and `integration_log` (string).

| Category | Details |
| --- | --- |
| **Reason** | Completes the node’s contract per the defined output structure. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Direct assignment to output fields before returning. |


---

## refine_selected_proposals

### Description
This node takes the top symbolic regression proposals identified by the selection step, refines them through optimization (e.g., hyperparameter tuning, ensembling, or simplification), re-evaluates their predictive accuracy and complexity, and outputs the improved expressions along with metrics that quantify the gains.

### Implementation Plan

#### 1. Retrieve the list of top proposal IDs and their original accuracy, complexity, and interpretability scores from the output of the `select_top_proposals` node.

| Category | Details |
| --- | --- |
| **Reason** | The refinement process requires baseline metrics to compute improvements and to know which proposals to work on. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Deserialize the JSON payload from the previous node, map each `top_proposal_ids` to its corresponding evaluation metrics stored in a shared data store (e.g., a key‑value map). |

#### 2. For each selected proposal, parse the symbolic expression string into an abstract syntax tree (AST) using a domain‑specific parser (e.g., `sympy.sympify` with safe evaluation settings).

| Category | Details |
| --- | --- |
| **Reason** | AST representation enables systematic manipulation for hyperparameter tuning, simplification, and ensembling. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Invoke `sympy.sympify` with custom `locals` mapping to restrict available functions to the domain (e.g., sin, log, exp). Handle parse errors by flagging the proposal as invalid and excluding it from refinement. |

#### 3. Apply hyperparameter tuning to each AST by optimizing the coefficients and variable transformations using a gradient‑free optimizer (e.g., Bayesian Optimization with the `scikit-optimize` library).

| Category | Details |
| --- | --- |
| **Reason** | Symbolic regression coefficients often have nonlinear effects; Bayesian Optimization efficiently explores the parameter space with few evaluations. |
| **Impact** | HIGH |
| **Complexity** | HIGH |
| **Method** | Define a cost function that evaluates the MSE on a validation split, constrain coefficient bounds based on domain knowledge, and run a fixed number of acquisition iterations. Store the best coefficient set. |

#### 4. Create an ensemble model by averaging predictions from multiple independently tuned variants of the same proposal (e.g., using different random seeds or data bootstraps).

| Category | Details |
| --- | --- |
| **Reason** | Ensembling reduces variance and often improves predictive accuracy without drastically increasing complexity. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Generate `n` tuned copies (n=5) by re‑running the hyperparameter search with different seeds, then compute the mean predicted value for each input sample during evaluation. |

#### 5. Simplify the ensemble’s symbolic expression by applying tree‑based reduction rules (e.g., `sympy.simplify`, `sympy.trigsimp`, `sympy.expand` with `force=True`) to remove redundant terms and combine like components.

| Category | Details |
| --- | --- |
| **Reason** | Simplification can reduce complexity while preserving predictive power, directly impacting the complexity_change metric. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Apply a sequence of sympy simplification passes, validate that the simplified expression does not change predictions beyond a tolerance, and record the new node count. |

#### 6. Evaluate each refined proposal on an unseen test split to obtain new accuracy metrics (e.g., R² or MSE) and compute `accuracy_improvement` by subtracting the original accuracy.

| Category | Details |
| --- | --- |
| **Reason** | Accurate measurement of improvement is essential to quantify the benefit of refinement. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use the same preprocessing pipeline as the original evaluation, predict with the refined AST, and compute metrics with `sklearn.metrics`. |

#### 7. Compute `complexity_change` as the difference between the new AST node count and the original proposal’s complexity score.

| Category | Details |
| --- | --- |
| **Reason** | This metric quantifies whether the refinement simplified or bloated the model. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Count AST nodes using `sympy.count_ops` or a custom traversal; subtract original complexity. |

#### 8. Estimate the `interpretability_score` of the refined proposals by combining a syntactic interpretability heuristic (e.g., ratio of unary operators to total nodes) with a human‑readability metric derived from the length of the expression string.

| Category | Details |
| --- | --- |
| **Reason** | Interpretability is a key requirement; a composite score captures both structural simplicity and readability. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Define `syntactic_score = 1 - (num_unary_ops / total_nodes)`, `readability_score = max(0, (max_length - expr_length) / max_length)`, then average the two scores. |

#### 9. Serialize the refined AST back into string representation using `sympy.srepr` or `sympy.pretty`, ensuring consistent formatting for downstream integration.

| Category | Details |
| --- | --- |
| **Reason** | The framework expects expressions as plain strings; consistent formatting aids debugging and logging. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Call `str(sympy_expr)` and apply any necessary post‑processing (e.g., removing whitespace, normalizing function names). |

#### 10. Package all outputs into the defined output structure, including `refined_proposals`, `accuracy_improvement`, `complexity_change`, and `interpretability_score` as JSON values.

| Category | Details |
| --- | --- |
| **Reason** | Clear and type‑safe output is required for the next node’s ingestion. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use a JSON library to build an object with the correct field names and types, then write to stdout or a temporary file as per platform conventions. |


---

## select_top_proposals

### Description
Select the top proposals based on their evaluated quality, using a top‑k strategy.

### Implementation Plan

#### 1. Validate that all input arrays (`proposal_ids`, `accuracy`, `complexity`, `interpretability`, `overall_quality`) are non‑empty and have the same length. If validation fails, set `is_successful` to `false` and return empty arrays for all outputs.

| Category | Details |
| --- | --- |
| **Reason** | Ensures data integrity before processing; prevents index errors and guarantees meaningful results. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use a pre‑processing step that checks `len(proposal_ids) == len(accuracy) == len(complexity) == len(interpretability) == len(overall_quality)` and that the length is > 0. If not, log the discrepancy and skip further processing. |

#### 2. Determine the number of proposals to select, `k`, as the minimum of 3 and the total number of proposals available.

| Category | Details |
| --- | --- |
| **Reason** | Adheres to the specification of a top‑3 selection while gracefully handling datasets with fewer proposals. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Set `k = min(3, len(proposal_ids))`. |

#### 3. Create a list of tuples pairing each proposal ID with its corresponding `overall_quality` score, then sort this list in descending order of `overall_quality`.

| Category | Details |
| --- | --- |
| **Reason** | Facilitates efficient extraction of the top‑k proposals based on a single composite metric. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use `sorted(zip(proposal_ids, overall_quality), key=lambda x: x[1], reverse=True)`. |

#### 4. Slice the sorted list to obtain the top‑k entries, and separate the proposal IDs and scores into their respective output arrays (`top_proposal_ids` and `top_proposal_scores`).

| Category | Details |
| --- | --- |
| **Reason** | Directly populates the output fields as required by the schema. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use list comprehensions: `top_ids = [id for id, score in top_k]` and `top_scores = [score for id, score in top_k]`. |

#### 5. Set `selected_count` to the actual number of selected proposals (`k`), set `selection_criteria` to the string "top‑3 by overall_quality", and set `is_successful` to `true`.

| Category | Details |
| --- | --- |
| **Reason** | Completes the output specification and signals successful execution. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Assign values directly: `selected_count = k; selection_criteria = "top-3 by overall_quality"; is_successful = True`. |

#### 6. Log the selection process for traceability: number of proposals, chosen IDs, and the top scores. Include this log in the system logs but not in the output fields.

| Category | Details |
| --- | --- |
| **Reason** | Facilitates debugging and auditability of the selection logic. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use a structured logging framework to emit a message such as "Selected top-3 proposals: IDs={top_proposal_ids}, Scores={top_proposal_scores}". |


---

## test_symbolic_regression_framework

### Description
Run a comprehensive evaluation of the symbolic regression framework that was built from the refined proposals. The test harness must load a curated set of benchmark datasets, evaluate each integrated symbolic expression on the test split, compute key metrics (accuracy, RMSE, runtime), determine if predefined performance thresholds are met, and produce a concise summary.

### Implementation Plan

#### 1. Parse each integrated symbolic expression string into an evaluable Python function using SymPy, then convert it to a NumPy ufunc for vectorized evaluation.

| Category | Details |
| --- | --- |
| **Reason** | The framework’s performance must be measured on the exact expressions that were integrated; converting to a ufunc allows fast predictions across large test sets. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | For each expression in `integrated_proposals`, use `sympy.sympify` to parse, then `sympy.lambdify` with modules=['numpy'] to generate a ufunc; verify no syntax errors and store the callable in a dictionary keyed by proposal id. |

#### 2. Read the list of test dataset names from a JSON configuration file (`test_datasets.json`) that resides in the project root, ensuring the file contains an array of dataset identifiers and optional file paths.

| Category | Details |
| --- | --- |
| **Reason** | Using an external config keeps the test harness flexible and decouples dataset selection from code changes. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Open the file with `json.load`, validate that `test_datasets` key exists and is a list, then iterate over each entry to construct full file paths relative to a data directory. |

#### 3. For each test dataset, load the CSV file into a Pandas DataFrame, extract feature columns and the target variable as specified by the original objective definition (passed via environment variable or a separate config).

| Category | Details |
| --- | --- |
| **Reason** | Consistent feature‑target alignment is critical for fair metric calculation. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use `pd.read_csv`; then separate features `X` and target `y` based on the `target_variable` and `feature_variables` lists; drop any rows containing NaNs. |

#### 4. Split each dataset into a training (80%) and test (20%) split using `sklearn.model_selection.train_test_split` with a fixed random seed for reproducibility.

| Category | Details |
| --- | --- |
| **Reason** | While the integrated proposals were trained elsewhere, we need a held‑out test set to evaluate generalization. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Call `train_test_split(X, y, test_size=0.2, random_state=42, shuffle=True)` and store the resulting `X_test` and `y_test` for evaluation. |

#### 5. For every parsed symbolic function, generate predictions on the test split, compute the coefficient of determination (R²) and root‑mean‑square error (RMSE) using `sklearn.metrics.r2_score` and `mean_squared_error` respectively.

| Category | Details |
| --- | --- |
| **Reason** | These metrics directly correspond to the `performance_metrics` expected by the framework and allow comparison across expressions. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Invoke the ufunc with `X_test.values` to obtain `y_pred`; then call `r2_score(y_test, y_pred)` and `mean_squared_error(y_test, y_pred, squared=False)`; store results in a per‑proposal dictionary. |

#### 6. Aggregate the metrics across all proposals for each dataset by selecting the best performing proposal (highest R²) and recording its metrics. Compute the mean of these per‑dataset best metrics to derive `test_accuracy` and `test_rmse`.

| Category | Details |
| --- | --- |
| **Reason** | Aggregating the best scores across datasets reflects the overall capability of the framework while accounting for variability. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | For each dataset, iterate over the proposals’ metrics, identify the maximum R², and keep the corresponding RMSE; then average the R²s and RMSEs across datasets. |

#### 7. Measure the total runtime by recording a start timestamp before the first prediction and an end timestamp after the last prediction across all datasets. Convert the difference to seconds and output as `test_runtime_seconds`.

| Category | Details |
| --- | --- |
| **Reason** | Runtime is a crucial performance indicator that may affect deployment decisions. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use `time.perf_counter()` before and after the entire evaluation loop; compute `runtime = end - start`. |

#### 8. Determine `test_success` by comparing the aggregated metrics against configurable thresholds. If `test_accuracy >= 0.80`, `test_rmse <= 10.0`, and `test_runtime_seconds <= 300.0`, set `test_success` to `True`; otherwise `False`. Thresholds are read from `performance_thresholds.json` if available, otherwise defaults are used.

| Category | Details |
| --- | --- |
| **Reason** | Automating the pass/fail check ensures consistent quality gate enforcement. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Load thresholds via `json.load`; perform straightforward comparison; log the outcome. |

#### 9. Generate a concise human‑readable summary (`test_summary`) that includes the overall accuracy, RMSE, runtime, the name of the best proposal per dataset, and a statement of whether the framework passed the quality gates.

| Category | Details |
| --- | --- |
| **Reason** | Summaries aid stakeholders in quickly assessing results without parsing raw numbers. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Format a multi‑line string using f‑strings, interpolating the calculated metrics and a success flag; e.g., `f"Framework passed: {test_success}. Avg Accuracy: {test_accuracy:.4f}, Avg RMSE: {test_rmse:.4f}"
Best proposal per dataset: {best_proposals_dict}". |

#### 10. Populate the output structure fields in the exact order specified, ensuring type fidelity: cast numeric metrics to `float`, the success flag to `bool`, and the dataset names list to `List[str]`.

| Category | Details |
| --- | --- |
| **Reason** | The downstream node `finalize_symbolic_regression_framework` expects strictly typed outputs; mismatches will cause validation failures. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Construct a dictionary matching the output schema; for each field, convert using `float(...)`, `bool(...)`, or direct assignment; finally return the dictionary. |
