# -- PRD --
# 1. BULLET: Retrieve the experiment objective from the execution context (e.g., an
#   environment variable, a user prompt, or a configuration file).
#   Reason: The hypothesis must be grounded in the experiment’s stated purpose, so the
#           objective is the primary source of information.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Use a predefined key (e.g., `experiment_objective`) to read the value from
#           the context object or pass it as a function argument.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Validate that the objective is sufficiently descriptive by ensuring it
#   contains a clear target variable and a condition or intervention.
#   Reason: A vague objective will lead to an ambiguous hypothesis, reducing
#           testability.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Apply a simple rule‑based check: the text must contain at least one noun
#           phrase denoting a variable and one verb phrase indicating a
#           change or condition.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Extract or request the independent and dependent variables from the user if
#   they are not explicitly mentioned in the objective.
#   Reason: A hypothesis must reference these two variable types to be scientifically
#           valid.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: If variables are missing, prompt the user with: "Please specify the
#           independent variable(s) and dependent variable(s) for the
#           experiment." Capture responses in `independent_variables` and
#           `dependent_variables` lists.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Construct the hypothesis sentence using a controlled template that ensures
#   testability: "When [independent] is [modified], [dependent] will
#   [increase/decrease/alter] accordingly."
#   Reason: Template usage guarantees that the sentence remains single‑sentence and
#           includes both variable types, satisfying the testable
#           criterion.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Populate the template with the extracted variables and a suitable outcome
#           verb. If multiple variables exist, use plural forms or multiple
#           clauses separated by commas.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Apply a short grammar and length check to ensure the sentence is concise (≤
#   25 words) and free of run‑on structures.
#   Reason: Readability and clarity aid in later design steps and prevent ambiguity.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Count words and run a simple regex to detect consecutive commas or
#           semicolons. If the check fails, adjust the template or request
#           clarification from the user.
# 
# -----------------------------------------------------------------------------
# 6. BULLET: Assign the finalized sentence to the `hypothesis_sentence` output field,
#   ensuring the string is returned exactly as produced.
#   Reason: This completes the node’s contract with downstream nodes.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Return the string via the node’s output dictionary or API response.
# -- END PRD --

from pydantic import BaseModel, Field


class FormulateHypothesisOutput(BaseModel):
    """Pydantic model for formulate_hypothesis node outputs."""
    hypothesis_sentence: str = Field(..., description="A single-sentence, testable hypothesis for the experiment")


def formulate_hypothesis(general_input: str, **kwargs) -> FormulateHypothesisOutput:
    """Generate a concise, testable hypothesis that encapsulates the expected relationship between the experiment's variables. The hypothesis must be expressed as a single, grammatically correct sentence.

    Args:
        general_input: General input string for the root node.
        **kwargs: Additional keyword arguments.

    Returns:
        FormulateHypothesisOutput: Object containing outputs for this node.
    """
    # TODO: Implement this function

    # Return stub output with placeholder values
    return FormulateHypothesisOutput(
        hypothesis_sentence="",
    )