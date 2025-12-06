# refine_selected_proposals PRD

## Description
This node takes the top symbolic regression proposals identified by the selection step, refines them through optimization (e.g., hyperparameter tuning, ensembling, or simplification), re-evaluates their predictive accuracy and complexity, and outputs the improved expressions along with metrics that quantify the gains.


## Implementation Plan

### 1. Retrieve the list of top proposal IDs and their original accuracy, complexity, and interpretability scores from the output of the `select_top_proposals` node.

| Category | Details |
| --- | --- |
| **Reason** | The refinement process requires baseline metrics to compute improvements and to know which proposals to work on. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Deserialize the JSON payload from the previous node, map each `top_proposal_ids` to its corresponding evaluation metrics stored in a shared data store (e.g., a key‑value map). |

### 2. For each selected proposal, parse the symbolic expression string into an abstract syntax tree (AST) using a domain‑specific parser (e.g., `sympy.sympify` with safe evaluation settings).

| Category | Details |
| --- | --- |
| **Reason** | AST representation enables systematic manipulation for hyperparameter tuning, simplification, and ensembling. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Invoke `sympy.sympify` with custom `locals` mapping to restrict available functions to the domain (e.g., sin, log, exp). Handle parse errors by flagging the proposal as invalid and excluding it from refinement. |

### 3. Apply hyperparameter tuning to each AST by optimizing the coefficients and variable transformations using a gradient‑free optimizer (e.g., Bayesian Optimization with the `scikit-optimize` library).

| Category | Details |
| --- | --- |
| **Reason** | Symbolic regression coefficients often have nonlinear effects; Bayesian Optimization efficiently explores the parameter space with few evaluations. |
| **Impact** | HIGH |
| **Complexity** | HIGH |
| **Method** | Define a cost function that evaluates the MSE on a validation split, constrain coefficient bounds based on domain knowledge, and run a fixed number of acquisition iterations. Store the best coefficient set. |

### 4. Create an ensemble model by averaging predictions from multiple independently tuned variants of the same proposal (e.g., using different random seeds or data bootstraps).

| Category | Details |
| --- | --- |
| **Reason** | Ensembling reduces variance and often improves predictive accuracy without drastically increasing complexity. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Generate `n` tuned copies (n=5) by re‑running the hyperparameter search with different seeds, then compute the mean predicted value for each input sample during evaluation. |

### 5. Simplify the ensemble’s symbolic expression by applying tree‑based reduction rules (e.g., `sympy.simplify`, `sympy.trigsimp`, `sympy.expand` with `force=True`) to remove redundant terms and combine like components.

| Category | Details |
| --- | --- |
| **Reason** | Simplification can reduce complexity while preserving predictive power, directly impacting the complexity_change metric. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Apply a sequence of sympy simplification passes, validate that the simplified expression does not change predictions beyond a tolerance, and record the new node count. |

### 6. Evaluate each refined proposal on an unseen test split to obtain new accuracy metrics (e.g., R² or MSE) and compute `accuracy_improvement` by subtracting the original accuracy.

| Category | Details |
| --- | --- |
| **Reason** | Accurate measurement of improvement is essential to quantify the benefit of refinement. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use the same preprocessing pipeline as the original evaluation, predict with the refined AST, and compute metrics with `sklearn.metrics`. |

### 7. Compute `complexity_change` as the difference between the new AST node count and the original proposal’s complexity score.

| Category | Details |
| --- | --- |
| **Reason** | This metric quantifies whether the refinement simplified or bloated the model. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Count AST nodes using `sympy.count_ops` or a custom traversal; subtract original complexity. |

### 8. Estimate the `interpretability_score` of the refined proposals by combining a syntactic interpretability heuristic (e.g., ratio of unary operators to total nodes) with a human‑readability metric derived from the length of the expression string.

| Category | Details |
| --- | --- |
| **Reason** | Interpretability is a key requirement; a composite score captures both structural simplicity and readability. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Define `syntactic_score = 1 - (num_unary_ops / total_nodes)`, `readability_score = max(0, (max_length - expr_length) / max_length)`, then average the two scores. |

### 9. Serialize the refined AST back into string representation using `sympy.srepr` or `sympy.pretty`, ensuring consistent formatting for downstream integration.

| Category | Details |
| --- | --- |
| **Reason** | The framework expects expressions as plain strings; consistent formatting aids debugging and logging. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Call `str(sympy_expr)` and apply any necessary post‑processing (e.g., removing whitespace, normalizing function names). |

### 10. Package all outputs into the defined output structure, including `refined_proposals`, `accuracy_improvement`, `complexity_change`, and `interpretability_score` as JSON values.

| Category | Details |
| --- | --- |
| **Reason** | Clear and type‑safe output is required for the next node’s ingestion. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use a JSON library to build an object with the correct field names and types, then write to stdout or a temporary file as per platform conventions. |
