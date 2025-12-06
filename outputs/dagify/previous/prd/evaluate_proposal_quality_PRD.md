# evaluate_proposal_quality PRD

## Description
Assess the generated proposals using relevant metrics such as accuracy, complexity, and interpretability.


## Implementation Plan

### 1. Validate the `proposals_valid` flag from the parent node and abort evaluation if it is false.

| Category | Details |
| --- | --- |
| **Reason** | Early exit avoids wasted computation on syntactically invalid proposals. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Simple boolean check; log and return empty lists if false. |

### 2. Assign a deterministic unique identifier to each proposal by concatenating the node name with its index (e.g., `eval_0`).

| Category | Details |
| --- | --- |
| **Reason** | Consistent IDs are required for downstream selection and traceability. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Iterate over `proposal_expressions` and generate ID strings. |

### 3. Parse each proposal string into an evaluatable expression tree using SymPy or a similar symbolic library.

| Category | Details |
| --- | --- |
| **Reason** | Converting to a parse tree allows systematic traversal for metric calculations. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use `sympy.sympify`; handle parsing errors with try‑except and mark such proposals as invalid. |

### 4. Load the training dataset from the `define_symbolic_regression_objective` context, ensuring alignment of feature and target variables.

| Category | Details |
| --- | --- |
| **Reason** | Accuracy metrics require actual data for prediction. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Read CSV/SQL or use pre‑loaded DataFrame; validate column names match `feature_variables` and `target_variable`. |

### 5. For each expression, evaluate predictions on the training dataset by substituting feature values.

| Category | Details |
| --- | --- |
| **Reason** | Predictions are needed to compute accuracy. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Vectorize evaluation using `numpy` arrays; handle division by zero and overflow by clipping results. |

### 6. Compute the accuracy metric as the coefficient of determination R². If R² calculation fails (e.g., constant prediction), fall back to negative mean squared error.

| Category | Details |
| --- | --- |
| **Reason** | R² provides an interpretable measure of explained variance; fallback ensures metric availability. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use `sklearn.metrics.r2_score`; compute MSE with `sklearn.metrics.mean_squared_error` if required. |

### 7. Calculate the structural complexity as the number of operators plus parentheses depth, normalizing by the maximum complexity seen across proposals.

| Category | Details |
| --- | --- |
| **Reason** | Normalized complexity facilitates fair comparison and weighting. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Traverse the SymPy expression tree; count nodes and compute depth; divide by max across all proposals. |

### 8. Derive an interpretability score between 0 and 1 using a heuristic that penalizes nested functions, uncommon operators, and excessive variable usage.

| Category | Details |
| --- | --- |
| **Reason** | Interpretability is subjective; a rule‑based heuristic offers consistency. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Compute a raw score as: 1 - (depth / max_depth + operator_penalty + variable_penalty); clip to [0,1]. |

### 9. Combine accuracy, inverse complexity, and interpretability into an overall quality score using the weighting scheme 0.4, 0.3, 0.3 respectively.

| Category | Details |
| --- | --- |
| **Reason** | Weighted sum balances performance with simplicity and human readability. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | overall_quality = 0.4*accuracy + 0.3*(1 - normalized_complexity) + 0.3*interpretability. |

### 10. Collect all computed metrics into lists aligned with proposal IDs and output them following the defined schema.

| Category | Details |
| --- | --- |
| **Reason** | Structured output is required for downstream nodes. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Append each metric to its respective list; ensure all lists share the same length. |

### 11. Log any proposals that triggered warnings (e.g., division by zero, overflow) and optionally set their metrics to NaN to flag them for review.

| Category | Details |
| --- | --- |
| **Reason** | Transparency in evaluation aids debugging and future refinement. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use Python logging; set metric values to `float('nan')`. |
