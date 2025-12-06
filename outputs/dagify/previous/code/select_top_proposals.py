from ._select_top_proposals.validate_input_arrays import validate_input_arrays
from ._select_top_proposals.log_validation_failure import log_validation_failure
from ._select_top_proposals.sort_proposals_by_quality import sort_proposals_by_quality
from ._select_top_proposals.format_proposal_ids import format_proposal_ids
from ._select_top_proposals.format_proposal_scores import format_proposal_scores
from ._select_top_proposals.log_selection_results import log_selection_results

from pydantic import BaseModel, Field
from typing import List


# -- PRD --
# 1. BULLET: Validate that all input arrays (`proposal_ids`, `accuracy`, `complexity`,
#   `interpretability`, `overall_quality`) are non‑empty and have the same
#   length. If validation fails, set `is_successful` to `false` and return
#   empty arrays for all outputs.
#   Reason: Ensures data integrity before processing; prevents index errors and
#           guarantees meaningful results.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Use a pre‑processing step that checks `len(proposal_ids) == len(accuracy)
#           == len(complexity) == len(interpretability) ==
#           len(overall_quality)` and that the length is > 0. If not, log
#           the discrepancy and skip further processing.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Determine the number of proposals to select, `k`, as the minimum of 3 and the
#   total number of proposals available.
#   Reason: Adheres to the specification of a top‑3 selection while gracefully handling
#           datasets with fewer proposals.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Set `k = min(3, len(proposal_ids))`.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Create a list of tuples pairing each proposal ID with its corresponding
#   `overall_quality` score, then sort this list in descending order of
#   `overall_quality`.
#   Reason: Facilitates efficient extraction of the top‑k proposals based on a single
#           composite metric.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Use `sorted(zip(proposal_ids, overall_quality), key=lambda x: x[1],
#           reverse=True)`.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Slice the sorted list to obtain the top‑k entries, and separate the proposal
#   IDs and scores into their respective output arrays (`top_proposal_ids`
#   and `top_proposal_scores`).
#   Reason: Directly populates the output fields as required by the schema.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Use list comprehensions: `top_ids = [id for id, score in top_k]` and
#           `top_scores = [score for id, score in top_k]`.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Set `selected_count` to the actual number of selected proposals (`k`), set
#   `selection_criteria` to the string "top‑3 by overall_quality", and set
#   `is_successful` to `true`.
#   Reason: Completes the output specification and signals successful execution.
#   Impact: LOW
#   Complexity: LOW
#   Method: Assign values directly: `selected_count = k; selection_criteria = "top-3 by
#           overall_quality"; is_successful = True`.
# 
# -----------------------------------------------------------------------------
# 6. BULLET: Log the selection process for traceability: number of proposals, chosen IDs,
#   and the top scores. Include this log in the system logs but not in the
#   output fields.
#   Reason: Facilitates debugging and auditability of the selection logic.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Use a structured logging framework to emit a message such as "Selected
#           top-3 proposals: IDs={top_proposal_ids},
#           Scores={top_proposal_scores}".
# -- END PRD --



class EvaluateProposalQualityOutput(BaseModel):
    """Pydantic model for evaluate_proposal_quality node outputs."""
    proposal_ids: List[str] = Field(..., description="List of identifiers for each proposal evaluated")
    accuracy: List[float] = Field(..., description="Accuracy metric of each proposal (e.g., R\u00b2 or mean squared error)")
    complexity: List[float] = Field(..., description="Complexity score based on the structural size of the symbolic expression")
    interpretability: List[float] = Field(..., description="Interpretability score ranging from 0 (poor) to 1 (high), reflecting how easily a human can understand the formula")
    overall_quality: List[float] = Field(..., description="Composite quality score combining accuracy, complexity, and interpretability")


class SelectTopProposalsOutput(BaseModel):
    """Pydantic model for select_top_proposals node outputs."""
    top_proposal_ids: str = Field(..., description="Identifiers of the proposals selected as top candidates.")
    top_proposal_scores: float = Field(..., description="Quality scores for each selected proposal, reflecting accuracy, complexity, and interpretability.")
    selected_count: int = Field(..., description="Number of proposals selected.")
    selection_criteria: str = Field(..., description="The rule or threshold used for selection (e.g., "top\u20113 by overall_quality").")
    is_successful: bool = Field(..., description="Indicates whether the selection process completed without errors.")


def select_top_proposals(evaluate_proposal_quality_input: EvaluateProposalQualityOutput, **kwargs) -> SelectTopProposalsOutput:
    """Select the top proposals based on their evaluated quality, using a top‑k strategy.

    Args:
        evaluate_proposal_quality_input: Input from the 'evaluate_proposal_quality' node.
        **kwargs: Additional keyword arguments.

    Returns:
        SelectTopProposalsOutput: Object containing outputs for this node.
    """
    # Validate input arrays
    is_valid: bool = validate_input_arrays(
        proposal_ids=evaluate_proposal_quality_input.proposal_ids,
        accuracy=evaluate_proposal_quality_input.accuracy,
        complexity=evaluate_proposal_quality_input.complexity,
        interpretability=evaluate_proposal_quality_input.interpretability,
        overall_quality=evaluate_proposal_quality_input.overall_quality
    )
    
    if not is_valid:
        log_validation_failure(arrays_info=evaluate_proposal_quality_input)
        return SelectTopProposalsOutput(
            top_proposal_ids="",
            top_proposal_scores=0.0,
            selected_count=0,
            selection_criteria="",
            is_successful=False
        )
    
    # Determine number of proposals to select (k)
    k: int = min(3, len(evaluate_proposal_quality_input.proposal_ids))
    
    # Create and sort proposal-score pairs
    sorted_proposals: List[tuple] = sort_proposals_by_quality(
        proposal_ids=evaluate_proposal_quality_input.proposal_ids,
        overall_quality=evaluate_proposal_quality_input.overall_quality
    )
    
    # Select top k proposals
    top_k_proposals: List[tuple] = sorted_proposals[:k]
    
    # Extract IDs and scores
    top_ids: List[str] = [proposal_id for proposal_id, score in top_k_proposals]
    top_scores: List[float] = [score for proposal_id, score in top_k_proposals]
    
    # Convert lists to required output format
    top_proposal_ids_str: str = format_proposal_ids(proposal_ids=top_ids)
    top_proposal_scores_float: float = format_proposal_scores(scores=top_scores)
    
    # Log selection process
    log_selection_results(
        selected_count=k,
        proposal_ids=top_ids,
        scores=top_scores
    )
    
    return SelectTopProposalsOutput(
        top_proposal_ids=top_proposal_ids_str,
        top_proposal_scores=top_proposal_scores_float,
        selected_count=k,
        selection_criteria="top-3 by overall_quality",
        is_successful=True
    )