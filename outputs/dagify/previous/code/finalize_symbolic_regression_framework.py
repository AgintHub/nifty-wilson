from ._finalize_symbolic_regression_framework.get_current_framework_version import get_current_framework_version
from ._finalize_symbolic_regression_framework.extract_failure_reasons import extract_failure_reasons
from ._finalize_symbolic_regression_framework.log_framework_failure import log_framework_failure
from ._finalize_symbolic_regression_framework.check_metrics_against_thresholds import check_metrics_against_thresholds
from ._finalize_symbolic_regression_framework.perform_hyperparameter_tuning import perform_hyperparameter_tuning
from ._finalize_symbolic_regression_framework.retrieve_integrated_proposals_data import retrieve_integrated_proposals_data
from ._finalize_symbolic_regression_framework.compute_expression_complexity import compute_expression_complexity
from ._finalize_symbolic_regression_framework.compute_expression_interpretability import compute_expression_interpretability
from ._finalize_symbolic_regression_framework.increment_framework_version import increment_framework_version
from ._finalize_symbolic_regression_framework.compose_adjustments_summary import compose_adjustments_summary
from ._finalize_symbolic_regression_framework.evaluate_framework_robustness import evaluate_framework_robustness

from pydantic import BaseModel, Field


# -- PRD --
# 1. BULLET: Retrieve test results from the parent node and store each field in local
#   variables for analysis.
#   Reason: Ensures all necessary metrics are available for decision making.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Destructure the JSON object received from
#           *test_symbolic_regression_framework* into variables:
#           test_accuracy, test_rmse, test_runtime_seconds, test_success,
#           test_dataset_names, test_summary.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Validate `test_success`. If `False`, log the failure reasons from
#   `test_summary` and exit the adjustment process early, returning the
#   original framework version and a robustness flag of `False`.
#   Reason: Prevents unnecessary computations when foundational performance criteria
#           are not met.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Implement a conditional guard: if !test_success then set framework_version
#           = original, adjustments_summary = 'No changes due to failure',
#           is_framework_robust = False, and skip further steps.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Examine `test_accuracy` and `test_rmse` against predefined thresholds (e.g.,
#   accuracy ≥ 0.90, RMSE ≤ 0.05). If either metric is outside the acceptable
#   range, schedule a hyper‑parameter tuning session using the
#   best‑performing proposals.
#   Reason: Directly targets the primary predictive quality metrics.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Compare metrics to thresholds; if violated, invoke a tuning routine that
#           re‑optimizes parameters such as mutation rate, population size,
#           or expression depth.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Retrieve the list of integrated symbolic proposals from the
#   *integrate_refined_proposals_into_framework* node, which contains
#   `integrated_proposals` and `integration_log`.
#   Reason: These expressions are the basis for computing complexity and
#           interpretability.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Query the system cache or storage for the outputs of
#           *integrate_refined_proposals_into_framework*; extract the
#           `integrated_proposals` array.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Compute `final_performance_complexity` by parsing each integrated expression
#   with SymPy, counting the number of operators and the depth of the syntax
#   tree, and aggregating the results (e.g., average operator count).
#   Reason: Provides an objective, quantifiable measure of model size that aligns with
#           the complexity metric.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: For each expression, use `sympy.sympify` to create an expression tree, then
#           traverse the tree to count operators (`+`, `-`, `*`, `/`, `**`,
#           `log`, etc.) and compute tree depth. Sum or average across all
#           expressions to produce a single float.
# 
# -----------------------------------------------------------------------------
# 6. BULLET: Estimate `final_performance_interpretability` by applying an interpretability
#   heuristic: assign a base score of 1.0 for expressions containing only
#   arithmetic operators and 0 for those that include non‑standard functions
#   (e.g., `exp`, `sin`, `log`). Weight scores by the inverse of tree depth
#   and average across expressions.
#   Reason: Captures human readability while penalizing deep, complex structures.
#   Impact: LOW
#   Complexity: MEDIUM
#   Method: For each expression, check for presence of functions beyond `+`, `-`, `*`,
#           `/`. Compute depth via SymPy; interpretability_score =
#           (is_simple ? 1.0 : 0.0) / (depth + 1). Aggregate across
#           proposals.
# 
# -----------------------------------------------------------------------------
# 7. BULLET: Determine the new `framework_version` by incrementing the minor semantic
#   version if adjustments are minor (e.g., only tuning or simplification),
#   or the major version if a structural redesign (e.g., new integration
#   strategy) was performed.
#   Reason: Versioning communicates the extent of changes to downstream users.
#   Impact: LOW
#   Complexity: LOW
#   Method: Parse the current framework version string (e.g., `v1.2`), apply semantic
#           versioning rules: if any tuning or simplification changes only,
#           increment minor; if architecture changes, increment major and
#           reset minor.
# 
# -----------------------------------------------------------------------------
# 8. BULLET: Compose an `adjustments_summary` that lists each change made, including the
#   type of adjustment (tuning, simplification, re‑integration) and its
#   quantitative impact (e.g., accuracy improvement, complexity reduction).
#   Reason: Provides traceability and aids future maintenance.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Build a string by concatenating bullet points: e.g., '- Tuned mutation rate
#           from 0.05 to 0.02, improving accuracy by 0.004'.
# 
# -----------------------------------------------------------------------------
# 9. BULLET: Set `is_framework_robust` to `True` only if `test_success` is `True` and
#   `test_accuracy` ≥ 0.90, `test_rmse` ≤ 0.05,
#   `final_performance_complexity` ≤ acceptable complexity threshold, and
#   `final_performance_interpretability` ≥ 0.7.
#   Reason: Defines a comprehensive robustness criterion covering accuracy, error,
#           complexity, and interpretability.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Implement a boolean expression that evaluates all conditions; assign result
#           to `is_framework_robust`.
# 
# -----------------------------------------------------------------------------
# 10. BULLET: Populate the output JSON with the computed fields: `framework_version`,
#   `adjustments_summary`, `is_framework_robust`,
#   `final_performance_accuracy`, `final_performance_complexity`, and
#   `final_performance_interpretability`.
#   Reason: Produces the final artifact expected by downstream nodes.
#   Impact: LOW
#   Complexity: LOW
#   Method: Serialize the variables into the prescribed JSON schema.
# -- END PRD --



class TestSymbolicRegressionFrameworkOutput(BaseModel):
    """Pydantic model for test_symbolic_regression_framework node outputs."""
    test_accuracy: float = Field(..., description="Overall accuracy of the framework on the test datasets")
    test_rmse: float = Field(..., description="Root mean squared error on the test datasets")
    test_runtime_seconds: float = Field(..., description="Total execution time in seconds for all test runs")
    test_success: bool = Field(..., description="Whether the framework met the predefined performance thresholds")
    test_dataset_names: str = Field(..., description="Names of the test datasets used in the evaluation")
    test_summary: str = Field(..., description="Short textual summary of the test results and observations")


class FinalizeSymbolicRegressionFrameworkOutput(BaseModel):
    """Pydantic model for finalize_symbolic_regression_framework node outputs."""
    framework_version: str = Field(..., description="Version identifier of the finalized symbolic regression framework")
    adjustments_summary: str = Field(..., description="Concise summary of modifications made based on test results")
    is_framework_robust: bool = Field(..., description="Indicates whether the framework meets robustness criteria after adjustments")
    final_performance_accuracy: float = Field(..., description="Accuracy metric achieved by the finalized framework on the test dataset")
    final_performance_complexity: float = Field(..., description="Complexity metric of the finalized model")
    final_performance_interpretability: float = Field(..., description="Interpretability metric of the finalized model")


def finalize_symbolic_regression_framework(test_symbolic_regression_framework_input: TestSymbolicRegressionFrameworkOutput, **kwargs) -> FinalizeSymbolicRegressionFrameworkOutput:
    """Finalizes the symbolic regression framework by applying adjustments informed by test results, ensuring robustness and documenting the outcome.

    Args:
        test_symbolic_regression_framework_input: Input from the 'test_symbolic_regression_framework' node.
        **kwargs: Additional keyword arguments.

    Returns:
        FinalizeSymbolicRegressionFrameworkOutput: Object containing outputs for this node.
    """
    # Retrieve test results from parent node and store in local variables
    test_accuracy: float = test_symbolic_regression_framework_input.test_accuracy
    test_rmse: float = test_symbolic_regression_framework_input.test_rmse
    test_runtime_seconds: float = test_symbolic_regression_framework_input.test_runtime_seconds
    test_success: bool = test_symbolic_regression_framework_input.test_success
    test_dataset_names: str = test_symbolic_regression_framework_input.test_dataset_names
    test_summary: str = test_symbolic_regression_framework_input.test_summary
    
    # Get current framework version for potential adjustments
    current_framework_version: str = get_current_framework_version()
    
    # Validate test_success and exit early if failure
    if not test_success:
        failure_reasons: str = extract_failure_reasons(test_summary=test_summary)
        log_framework_failure(reasons=failure_reasons)
        return FinalizeSymbolicRegressionFrameworkOutput(
            framework_version=current_framework_version,
            adjustments_summary="No changes due to failure",
            is_framework_robust=False,
            final_performance_accuracy=test_accuracy,
            final_performance_complexity=0.0,
            final_performance_interpretability=0.0,
        )
    
    # Check accuracy and RMSE against thresholds and apply tuning if needed
    accuracy_threshold: float = 0.90
    rmse_threshold: float = 0.05
    needs_tuning: bool = check_metrics_against_thresholds(
        accuracy=test_accuracy, 
        rmse=test_rmse, 
        accuracy_threshold=accuracy_threshold, 
        rmse_threshold=rmse_threshold
    )
    
    adjustments_made = []
    final_accuracy = test_accuracy
    
    if needs_tuning:
        tuning_results = perform_hyperparameter_tuning(
            current_accuracy=test_accuracy, 
            current_rmse=test_rmse
        )
        final_accuracy = tuning_results["improved_accuracy"]
        adjustments_made.append(tuning_results["tuning_summary"])
    
    # Retrieve integrated proposals from integration node
    integration_data = retrieve_integrated_proposals_data()
    integrated_proposals = integration_data["integrated_proposals"]
    integration_log = integration_data["integration_log"]
    
    # Compute final performance complexity using SymPy analysis
    final_performance_complexity: float = compute_expression_complexity(
        expressions=integrated_proposals
    )
    
    # Estimate final performance interpretability using heuristic
    final_performance_interpretability: float = compute_expression_interpretability(
        expressions=integrated_proposals
    )
    
    # Determine new framework version based on adjustments
    framework_version: str = increment_framework_version(
        current_version=current_framework_version,
        adjustments_made=adjustments_made
    )
    
    # Compose adjustments summary
    adjustments_summary: str = compose_adjustments_summary(
        adjustments_list=adjustments_made,
        complexity_change=final_performance_complexity,
        accuracy_improvement=final_accuracy - test_accuracy
    )
    
    # Determine framework robustness based on comprehensive criteria
    complexity_threshold: float = 10.0
    interpretability_threshold: float = 0.7
    is_framework_robust: bool = evaluate_framework_robustness(
        test_success=test_success,
        accuracy=final_accuracy,
        rmse=test_rmse,
        complexity=final_performance_complexity,
        interpretability=final_performance_interpretability,
        accuracy_threshold=accuracy_threshold,
        rmse_threshold=rmse_threshold,
        complexity_threshold=complexity_threshold,
        interpretability_threshold=interpretability_threshold
    )
    
    return FinalizeSymbolicRegressionFrameworkOutput(
        framework_version=framework_version,
        adjustments_summary=adjustments_summary,
        is_framework_robust=is_framework_robust,
        final_performance_accuracy=final_accuracy,
        final_performance_complexity=final_performance_complexity,
        final_performance_interpretability=final_performance_interpretability,
    )