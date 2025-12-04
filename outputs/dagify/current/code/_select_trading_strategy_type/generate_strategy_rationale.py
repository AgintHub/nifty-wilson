# -- PRD --
# 1. BULLET: Parse and validate the three input strings (selected_strategy,
#   data_classification, technique_mapping) ensuring they are present and
#   non‑empty.
#   Reason: Invalid or missing inputs would cause downstream errors and produce
#           nonsensical rationales.
#   Impact: Prevents runtime failures and guarantees that the rationale is based on
#           reliable data.
#   Complexity: LOW
#   Method: Implement simple conditional checks; raise a ValueError with a clear
#           message if any input is missing or empty.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Construct the rationale using a rule‑based template that incorporates the
#   dominant factors extracted from data_classification and
#   technique_mapping.
#   Reason: A deterministic template ensures consistent, explainable output while still
#           reflecting the key characteristics of the inputs.
#   Impact: Produces a human‑readable, context‑aware justification that can be audited
#           or displayed to end users.
#   Complexity: MEDIUM
#   Method: Create a mapping of strategy types to template fragments; deserialize the
#           JSON‑like strings, identify the most influential classification
#           (e.g., low latency) and technique (e.g., sentiment analysis),
#           and interpolate them into the template using Python f‑strings
#           or the `format` method.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Return a dictionary containing the generated rationale as `output` together
#   with the original input fields.
#   Reason: The node contract expects both the rationale and the original context for
#           downstream nodes.
#   Impact: Ensures downstream compatibility and allows other nodes to reuse the input
#           data without recomputation.
#   Complexity: LOW
#   Method: Assemble the result dict with keys `output`, `selected_strategy`,
#           `data_classification`, and `technique_mapping` and return it.
# -- END PRD --


def generate_strategy_rationale(selected_strategy: str, data_classification: str, technique_mapping: str) -> str:
    """
    Generates a concise rationale explaining why the selected trading strategy is optimal given the data classification and technique mapping.

    Args:
        selected_strategy: Input parameter of type str
data_classification: Input parameter of type str
technique_mapping: Input parameter of type str

    Returns:
        str: Output of type str
    """
    raise NotImplementedError("This is a virtual stub node that needs to be implemented")
