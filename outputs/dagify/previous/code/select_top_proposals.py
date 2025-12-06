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

from pydantic import BaseModel, Field
from typing import List


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
    selection_criteria: str = Field(..., description="The rule or threshold used for selection (e.g., \"top\u20113 by overall_quality\").")
    is_successful: bool = Field(..., description="Indicates whether the selection process completed without errors.")


def select_top_proposals(evaluate_proposal_quality_input: EvaluateProposalQualityOutput, **kwargs) -> SelectTopProposalsOutput:
    """Select the top proposals based on their evaluated quality, using a top‑k strategy.

    Args:
        evaluate_proposal_quality_input: Input from the 'evaluate_proposal_quality' node.
        **kwargs: Additional keyword arguments.

    Returns:
        SelectTopProposalsOutput: Object containing outputs for this node.
    """
    # TODO: Implement this function

    # Return stub output with placeholder values
    return SelectTopProposalsOutput(
        top_proposal_ids="",
        top_proposal_scores=0.0,
        selected_count=0,
        selection_criteria="",
        is_successful=False,
    )