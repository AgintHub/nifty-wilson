from ._evaluate_proposal_quality.log_early_exit import log_early_exit
from ._evaluate_proposal_quality.extract_proposal_expressions import extract_proposal_expressions
from ._evaluate_proposal_quality.generate_proposal_ids import generate_proposal_ids
from ._evaluate_proposal_quality.parse_expressions_to_trees import parse_expressions_to_trees
from ._evaluate_proposal_quality.load_training_dataset import load_training_dataset
from ._evaluate_proposal_quality.evaluate_expression_predictions import evaluate_expression_predictions
from ._evaluate_proposal_quality.compute_accuracy_metric import compute_accuracy_metric
from ._evaluate_proposal_quality.calculate_structural_complexity import calculate_structural_complexity
from ._evaluate_proposal_quality.calculate_interpretability_score import calculate_interpretability_score
from ._evaluate_proposal_quality.normalize_complexity_scores import normalize_complexity_scores
from ._evaluate_proposal_quality.compute_overall_quality import compute_overall_quality
from ._evaluate_proposal_quality.log_proposal_warnings import log_proposal_warnings

from pydantic import BaseModel, Field
from typing import List


# -- PRD --
# 1. BULLET: Validate the `proposals_valid` flag from the parent node and abort evaluation
#   if it is false.
#   Reason: Early exit avoids wasted computation on syntactically invalid proposals.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Simple boolean check; log and return empty lists if false.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Assign a deterministic unique identifier to each proposal by concatenating
#   the node name with its index (e.g., `eval_0`).
#   Reason: Consistent IDs are required for downstream selection and traceability.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Iterate over `proposal_expressions` and generate ID strings.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Parse each proposal string into an evaluatable expression tree using SymPy or
#   a similar symbolic library.
#   Reason: Converting to a parse tree allows systematic traversal for metric
#           calculations.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Use `sympy.sympify`; handle parsing errors with try‑except and mark such
#           proposals as invalid.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Load the training dataset from the `define_symbolic_regression_objective`
#   context, ensuring alignment of feature and target variables.
#   Reason: Accuracy metrics require actual data for prediction.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Read CSV/SQL or use pre‑loaded DataFrame; validate column names match
#           `feature_variables` and `target_variable`.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: For each expression, evaluate predictions on the training dataset by
#   substituting feature values.
#   Reason: Predictions are needed to compute accuracy.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Vectorize evaluation using `numpy` arrays; handle division by zero and
#           overflow by clipping results.
# 
# -----------------------------------------------------------------------------
# 6. BULLET: Compute the accuracy metric as the coefficient of determination R². If R²
#   calculation fails (e.g., constant prediction), fall back to negative mean
#   squared error.
#   Reason: R² provides an interpretable measure of explained variance; fallback
#           ensures metric availability.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Use `sklearn.metrics.r2_score`; compute MSE with
#           `sklearn.metrics.mean_squared_error` if required.
# 
# -----------------------------------------------------------------------------
# 7. BULLET: Calculate the structural complexity as the number of operators plus
#   parentheses depth, normalizing by the maximum complexity seen across
#   proposals.
#   Reason: Normalized complexity facilitates fair comparison and weighting.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Traverse the SymPy expression tree; count nodes and compute depth; divide
#           by max across all proposals.
# 
# -----------------------------------------------------------------------------
# 8. BULLET: Derive an interpretability score between 0 and 1 using a heuristic that
#   penalizes nested functions, uncommon operators, and excessive variable
#   usage.
#   Reason: Interpretability is subjective; a rule‑based heuristic offers consistency.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Compute a raw score as: 1 - (depth / max_depth + operator_penalty +
#           variable_penalty); clip to [0,1].
# 
# -----------------------------------------------------------------------------
# 9. BULLET: Combine accuracy, inverse complexity, and interpretability into an overall
#   quality score using the weighting scheme 0.4, 0.3, 0.3 respectively.
#   Reason: Weighted sum balances performance with simplicity and human readability.
#   Impact: HIGH
#   Complexity: LOW
#   Method: overall_quality = 0.4*accuracy + 0.3*(1 - normalized_complexity) +
#           0.3*interpretability.
# 
# -----------------------------------------------------------------------------
# 10. BULLET: Collect all computed metrics into lists aligned with proposal IDs and output
#   them following the defined schema.
#   Reason: Structured output is required for downstream nodes.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Append each metric to its respective list; ensure all lists share the same
#           length.
# 
# -----------------------------------------------------------------------------
# 11. BULLET: Log any proposals that triggered warnings (e.g., division by zero, overflow)
#   and optionally set their metrics to NaN to flag them for review.
#   Reason: Transparency in evaluation aids debugging and future refinement.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Use Python logging; set metric values to `float('nan')`.
# -- END PRD --



class GenerateSymbolicRegressionProposalsOutput(BaseModel):
    """Pydantic model for generate_symbolic_regression_proposals node outputs."""
    proposal_expressions: str = Field(..., description="The symbolic regression expressions generated by the LLM, each represented as a string.")
    proposal_complexities: int = Field(..., description="Integer complexity scores for each proposal, indicating the number of operators or depth of the expression tree.")
    proposal_confidences: float = Field(..., description="Confidence or probability estimates for each proposal, ranging from 0.0 to 1.0.")
    proposal_count: int = Field(..., description="Total number of proposals generated.")
    proposals_valid: bool = Field(..., description="Whether the proposal set passed preliminary validation (e.g., syntactic correctness).")


class EvaluateProposalQualityOutput(BaseModel):
    """Pydantic model for evaluate_proposal_quality node outputs."""
    proposal_ids: List[str] = Field(..., description="List of identifiers for each proposal evaluated")
    accuracy: List[float] = Field(..., description="Accuracy metric of each proposal (e.g., R\u00b2 or mean squared error)")
    complexity: List[float] = Field(..., description="Complexity score based on the structural size of the symbolic expression")
    interpretability: List[float] = Field(..., description="Interpretability score ranging from 0 (poor) to 1 (high), reflecting how easily a human can understand the formula")
    overall_quality: List[float] = Field(..., description="Composite quality score combining accuracy, complexity, and interpretability")


def evaluate_proposal_quality(generate_symbolic_regression_proposals_input: GenerateSymbolicRegressionProposalsOutput, **kwargs) -> EvaluateProposalQualityOutput:
    """Assess the generated proposals using relevant metrics such as accuracy, complexity, and interpretability.

    Args:
        generate_symbolic_regression_proposals_input: Input from the 'generate_symbolic_regression_proposals' node.
        **kwargs: Additional keyword arguments.

    Returns:
        EvaluateProposalQualityOutput: Object containing outputs for this node.
    """
    # Validate proposals_valid flag and early exit if false
    if not generate_symbolic_regression_proposals_input.proposals_valid:
        log_early_exit(reason="proposals_valid is false")
        return EvaluateProposalQualityOutput(
            proposal_ids=[],
            accuracy=[],
            complexity=[],
            interpretability=[],
            overall_quality=[]
        )
    
    # Extract proposal expressions and generate deterministic IDs
    proposal_expressions: List[str] = extract_proposal_expressions(input_data=generate_symbolic_regression_proposals_input)
    proposal_ids: List[str] = generate_proposal_ids(expressions=proposal_expressions, node_name="eval")
    
    # Parse expressions into evaluatable expression trees
    parsed_expressions: List = parse_expressions_to_trees(expressions=proposal_expressions)
    
    # Load training dataset from context
    training_data = load_training_dataset(context=kwargs)
    
    # Initialize metric lists
    accuracy_scores: List[float] = []
    complexity_scores: List[float] = []
    interpretability_scores: List[float] = []
    
    # Evaluate each expression
    for i, expression_tree in enumerate(parsed_expressions):
        # Evaluate predictions on training dataset
        predictions = evaluate_expression_predictions(expression=expression_tree, dataset=training_data)
        
        # Compute accuracy metric (R² with MSE fallback)
        accuracy: float = compute_accuracy_metric(predictions=predictions, targets=training_data)
        accuracy_scores.append(accuracy)
        
        # Calculate structural complexity
        complexity: float = calculate_structural_complexity(expression=expression_tree)
        complexity_scores.append(complexity)
        
        # Derive interpretability score
        interpretability: float = calculate_interpretability_score(expression=expression_tree)
        interpretability_scores.append(interpretability)
    
    # Normalize complexity scores
    normalized_complexity: List[float] = normalize_complexity_scores(complexity_scores=complexity_scores)
    
    # Combine metrics into overall quality scores
    overall_quality_scores: List[float] = compute_overall_quality(
        accuracy=accuracy_scores,
        complexity=normalized_complexity,
        interpretability=interpretability_scores
    )
    
    # Log any proposals with warnings
    log_proposal_warnings(proposal_ids=proposal_ids, metrics={
        "accuracy": accuracy_scores,
        "complexity": normalized_complexity,
        "interpretability": interpretability_scores
    })
    
    return EvaluateProposalQualityOutput(
        proposal_ids=proposal_ids,
        accuracy=accuracy_scores,
        complexity=normalized_complexity,
        interpretability=interpretability_scores,
        overall_quality=overall_quality_scores
    )