# generate_symbolic_regression_proposals PRD

## Description
Generate proposals for symbolic regression using the configured LLM


## Implementation Plan

### 1. Retrieve LLM configuration parameters from the parent node `configure_llm_for_proposal_generation`.

| Category | Details |
| --- | --- |
| **Reason** | The LLM must be invoked with the same parameters that were intentionally configured for proposal generation to ensure consistent behavior. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Deserialize the parent output JSON into a dictionary and extract keys: model_name, temperature, max_tokens, prompt_template, input_schema, num_proposals. |

### 2. Validate and transform the objective description and dataset into a JSON payload that matches `input_schema`.

| Category | Details |
| --- | --- |
| **Reason** | The LLM prompt template expects structured data; mismatched formats will cause the model to fail or produce nonsense. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Parse `define_symbolic_regression_objective` output; create a JSON object with keys: objective_description, target_variable, feature_variables, constraints, performance_metrics, dataset_description. Use JSON schema validation libraries to enforce `input_schema` compliance. |

### 3. Populate the `prompt_template` with the objective JSON and any required placeholders.

| Category | Details |
| --- | --- |
| **Reason** | Embedding the objective and data into the prompt ensures the LLM generates contextually relevant expressions. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use Python f-string or `jinja2` templating to replace placeholders like {{objective_json}} within the template. |

### 4. Invoke the LLM using the specified `model_name`, `temperature`, `max_tokens`, and `num_proposals`.

| Category | Details |
| --- | --- |
| **Reason** | Directly controlling sampling and token limits guarantees the output stays within the desired size and diversity. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use the OpenAI or vendor-specific SDK to call `model_name` with `temperature` and `max_tokens`. If `num_proposals` > 1, loop or use `n` sampling parameter. Capture raw text responses. |

### 5. Parse the raw LLM output into individual proposal strings.

| Category | Details |
| --- | --- |
| **Reason** | The LLM may return proposals separated by newlines, bullets, or JSON; a robust parser reduces errors. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | First, attempt to parse as JSON array. If fails, split by newline and regex pattern `^Proposal \d+: (.+)$`. Clean leading/trailing whitespace. |

### 6. Validate syntactic correctness of each proposal expression using a symbolic algebra parser.

| Category | Details |
| --- | --- |
| **Reason** | Invalid expressions would corrupt downstream evaluation and evaluation metrics. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Utilize `sympy.sympify` in a try/except block for each expression. If parsing fails, mark the entire set as invalid and log the error. |

### 7. Compute a complexity score for each proposal.

| Category | Details |
| --- | --- |
| **Reason** | Complexity is a key evaluation metric and required output. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Parse the expression into an AST using `sympy` and count nodes (operators, functions). Return the node count as an integer. |

### 8. Assign a confidence score for each proposal.

| Category | Details |
| --- | --- |
| **Reason** | Confidence informs downstream ranking and selection. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | If LLM provides a probability (e.g., via logit or explicit field), normalize to [0,1]. Otherwise, use uniform confidence of 1/num_proposals or apply a simple heuristic based on expression length (shorter = higher confidence). |

### 9. Aggregate all metrics into the final output dictionary and set `proposal_count` and `proposals_valid`.

| Category | Details |
| --- | --- |
| **Reason** | Ensures conformity to the defined output schema and provides a clear success flag. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Collect lists of expressions, complexities, confidences; compute len(list) for proposal_count; set proposals_valid to True if all expressions parsed successfully, else False. |
