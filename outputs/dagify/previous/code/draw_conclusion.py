# -- PRD --
# 1. BULLET: Validate input schema from the `interpret_results` node: ensure that all
#   required fields (`interpretation_summary`, `hypothesis_conclusion`,
#   `key_metric_names`, `key_metric_values`, `limitations`,
#   `recommendations`, `confidence_score`, `is_analysis_valid`) exist and
#   match their declared PrimitiveTypes. Reject execution early with a clear
#   error if validation fails.
#   Reason: Early schema validation prevents downstream type errors and guarantees that
#           the subsequent logic operates on reliable data.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Use a JSON schema validator or type‑check each field explicitly. Log
#           validation failures and abort the process.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Perform an analysis validity guard: if `is_analysis_valid` is False, set
#   `hypothesis_support` to False and construct `conclusion_text` that starts
#   with an explicit warning about invalid analysis, followed by a brief
#   statement that no conclusion can be reliably drawn.
#   Reason: The output must reflect the integrity of the analysis; an invalid analysis
#           invalidates any conclusion.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Conditional branch; concatenate warning string; skip further processing.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Map the textual `hypothesis_conclusion` field to a boolean flag: treat any
#   string containing the word 'supported' (case‑insensitive) as True,
#   containing 'rejected' as False, and any other value (including
#   'inconclusive') as False. Store this mapping in a temporary variable
#   `support_flag`.
#   Reason: A deterministic mapping removes ambiguity when translating natural language
#           into a boolean.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Normalize string to lowercase, use regex or simple `in` checks.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Apply a confidence threshold: if `confidence_score` is below 0.60, downgrade
#   `support_flag` to False regardless of the textual
#   `hypothesis_conclusion`, and annotate the `conclusion_text` with a note
#   about low confidence.
#   Reason: Low confidence indicates that the evidence is weak; the conclusion should
#           reflect uncertainty.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Compare float, set flag, append confidence note.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Construct the `conclusion_text` in a single, readable paragraph that
#   includes:  1. A declarative statement of support or rejection using the
#   final `support_flag`. 2. A concise summary of the key metric names and
#   their values formatted as "MetricName (value)". 3. The confidence level
#   expressed as a percentage. 4. A brief mention of the most significant
#   limitation. 5. The first recommendation from the list if available. Keep
#   the entire text under 200 words to maintain conciseness.
#   Reason: A well‑structured conclusion conveys all essential information while
#           staying readable for reporting.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Use Python f‑strings; iterate over `key_metric_names`/`key_metric_values`
#           pairwise; format float to one decimal place; select the first
#           item from `limitations` and `recommendations` if lists are
#           non‑empty.
# 
# -----------------------------------------------------------------------------
# 6. BULLET: Return the two output fields: `hypothesis_support` set to the final boolean
#   flag and `conclusion_text` containing the assembled paragraph.
#   Reason: Final step completes the node’s contract with the downstream
#           `document_experiment` node.
#   Impact: LOW
#   Complexity: LOW
#   Method: Return a dictionary matching the output structure.
# 
# -----------------------------------------------------------------------------
# 7. BULLET: Include comprehensive unit tests that cover all branches: valid analysis with
#   support, valid analysis with rejection, inconclusive hypothesis, low
#   confidence, invalid analysis, and missing optional fields.
#   Reason: Testing guarantees reliability and helps future maintainers understand
#           expected behavior.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Use a testing framework (e.g., pytest) and mock input data for each
#           scenario.
# 
# -----------------------------------------------------------------------------
# 8. BULLET: Add runtime logging at INFO level for each major step (validation, validity
#   guard, mapping, threshold adjustment, text assembly). Include the values
#   of critical variables to aid debugging.
#   Reason: Traceability is essential for diagnosing issues in complex workflows.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Use Python’s logging module; format messages with variable values.
# -- END PRD --

from pydantic import BaseModel, Field


class InterpretResultsOutput(BaseModel):
    """Pydantic model for interpret_results node outputs."""
    interpretation_summary: str = Field(..., description="A concise narrative summarizing the key interpretations of the analyzed data.")
    hypothesis_conclusion: str = Field(..., description="Indicates whether the hypothesis was supported, rejected, or remains inconclusive.")
    key_metric_names: str = Field(..., description="Names of the primary metrics or statistical tests that informed the interpretation.")
    key_metric_values: float = Field(..., description="Corresponding numerical values (e.g., p-values, effect sizes) for each key metric.")
    limitations: str = Field(..., description="Known limitations or sources of uncertainty affecting the interpretation.")
    recommendations: str = Field(..., description="Suggested next steps or actions based on the interpretation.")
    confidence_score: float = Field(..., description="Quantitative confidence level (0 to 1) that the interpretation accurately reflects the data.")
    is_analysis_valid: bool = Field(..., description="Flag indicating whether the data analysis was performed correctly and results are reliable.")


class DrawConclusionOutput(BaseModel):
    """Pydantic model for draw_conclusion node outputs."""
    hypothesis_support: bool = Field(..., description="True if the hypothesis is supported, False if rejected")
    conclusion_text: str = Field(..., description="A concise textual summary of the conclusion drawn from the experiment")


def draw_conclusion(interpret_results_input: InterpretResultsOutput, **kwargs) -> DrawConclusionOutput:
    """Draw a conclusion based on the experiment's findings

    Args:
        interpret_results_input: Input from the 'interpret_results' node.
        **kwargs: Additional keyword arguments.

    Returns:
        DrawConclusionOutput: Object containing outputs for this node.
    """
    # TODO: Implement this function

    # Return stub output with placeholder values
    return DrawConclusionOutput(
        hypothesis_support=False,
        conclusion_text="",
    )