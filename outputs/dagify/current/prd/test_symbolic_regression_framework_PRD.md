# test_symbolic_regression_framework PRD

## Description
Run a comprehensive evaluation of the symbolic regression framework that was built from the refined proposals. The test harness must load a curated set of benchmark datasets, evaluate each integrated symbolic expression on the test split, compute key metrics (accuracy, RMSE, runtime), determine if predefined performance thresholds are met, and produce a concise summary.


## Implementation Plan

### 1. Parse each integrated symbolic expression string into an evaluable Python function using SymPy, then convert it to a NumPy ufunc for vectorized evaluation.

| Category | Details |
| --- | --- |
| **Reason** | The framework’s performance must be measured on the exact expressions that were integrated; converting to a ufunc allows fast predictions across large test sets. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | For each expression in `integrated_proposals`, use `sympy.sympify` to parse, then `sympy.lambdify` with modules=['numpy'] to generate a ufunc; verify no syntax errors and store the callable in a dictionary keyed by proposal id. |

### 2. Read the list of test dataset names from a JSON configuration file (`test_datasets.json`) that resides in the project root, ensuring the file contains an array of dataset identifiers and optional file paths.

| Category | Details |
| --- | --- |
| **Reason** | Using an external config keeps the test harness flexible and decouples dataset selection from code changes. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Open the file with `json.load`, validate that `test_datasets` key exists and is a list, then iterate over each entry to construct full file paths relative to a data directory. |

### 3. For each test dataset, load the CSV file into a Pandas DataFrame, extract feature columns and the target variable as specified by the original objective definition (passed via environment variable or a separate config).

| Category | Details |
| --- | --- |
| **Reason** | Consistent feature‑target alignment is critical for fair metric calculation. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use `pd.read_csv`; then separate features `X` and target `y` based on the `target_variable` and `feature_variables` lists; drop any rows containing NaNs. |

### 4. Split each dataset into a training (80%) and test (20%) split using `sklearn.model_selection.train_test_split` with a fixed random seed for reproducibility.

| Category | Details |
| --- | --- |
| **Reason** | While the integrated proposals were trained elsewhere, we need a held‑out test set to evaluate generalization. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Call `train_test_split(X, y, test_size=0.2, random_state=42, shuffle=True)` and store the resulting `X_test` and `y_test` for evaluation. |

### 5. For every parsed symbolic function, generate predictions on the test split, compute the coefficient of determination (R²) and root‑mean‑square error (RMSE) using `sklearn.metrics.r2_score` and `mean_squared_error` respectively.

| Category | Details |
| --- | --- |
| **Reason** | These metrics directly correspond to the `performance_metrics` expected by the framework and allow comparison across expressions. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Invoke the ufunc with `X_test.values` to obtain `y_pred`; then call `r2_score(y_test, y_pred)` and `mean_squared_error(y_test, y_pred, squared=False)`; store results in a per‑proposal dictionary. |

### 6. Aggregate the metrics across all proposals for each dataset by selecting the best performing proposal (highest R²) and recording its metrics. Compute the mean of these per‑dataset best metrics to derive `test_accuracy` and `test_rmse`.

| Category | Details |
| --- | --- |
| **Reason** | Aggregating the best scores across datasets reflects the overall capability of the framework while accounting for variability. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | For each dataset, iterate over the proposals’ metrics, identify the maximum R², and keep the corresponding RMSE; then average the R²s and RMSEs across datasets. |

### 7. Measure the total runtime by recording a start timestamp before the first prediction and an end timestamp after the last prediction across all datasets. Convert the difference to seconds and output as `test_runtime_seconds`.

| Category | Details |
| --- | --- |
| **Reason** | Runtime is a crucial performance indicator that may affect deployment decisions. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use `time.perf_counter()` before and after the entire evaluation loop; compute `runtime = end - start`. |

### 8. Determine `test_success` by comparing the aggregated metrics against configurable thresholds. If `test_accuracy >= 0.80`, `test_rmse <= 10.0`, and `test_runtime_seconds <= 300.0`, set `test_success` to `True`; otherwise `False`. Thresholds are read from `performance_thresholds.json` if available, otherwise defaults are used.

| Category | Details |
| --- | --- |
| **Reason** | Automating the pass/fail check ensures consistent quality gate enforcement. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Load thresholds via `json.load`; perform straightforward comparison; log the outcome. |

### 9. Generate a concise human‑readable summary (`test_summary`) that includes the overall accuracy, RMSE, runtime, the name of the best proposal per dataset, and a statement of whether the framework passed the quality gates.

| Category | Details |
| --- | --- |
| **Reason** | Summaries aid stakeholders in quickly assessing results without parsing raw numbers. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Format a multi‑line string using f‑strings, interpolating the calculated metrics and a success flag; e.g., `f"Framework passed: {test_success}. Avg Accuracy: {test_accuracy:.4f}, Avg RMSE: {test_rmse:.4f}"
Best proposal per dataset: {best_proposals_dict}". |

### 10. Populate the output structure fields in the exact order specified, ensuring type fidelity: cast numeric metrics to `float`, the success flag to `bool`, and the dataset names list to `List[str]`.

| Category | Details |
| --- | --- |
| **Reason** | The downstream node `finalize_symbolic_regression_framework` expects strictly typed outputs; mismatches will cause validation failures. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Construct a dictionary matching the output schema; for each field, convert using `float(...)`, `bool(...)`, or direct assignment; finally return the dictionary. |
