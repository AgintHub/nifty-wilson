# -- PRD --
# 1. BULLET: Detect and parse all placeholder tokens (e.g., {{strategy}},
#   {{max_drawdown}}) within each rule template.
#   Reason: Placeholders must be identified reliably before any substitution can occur.
#   Impact: Ensures that every dynamic element is accounted for, preventing incomplete
#           or malformed rules.
#   Complexity: MEDIUM
#   Method: Compile a regular expression like /\{\{([^}]+)\}\}/ to extract token names,
#           then store them in a set for each rule.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Map each detected placeholder to a concrete value based on the normalized
#   strategy type and replace it in the rule text.
#   Reason: The core purpose of the shim is to inject strategy‑specific parameters
#           (e.g., position sizing percentages) into generic templates.
#   Impact: Produces fully‑specified, actionable risk‑management rules that downstream
#           nodes can use without further processing.
#   Complexity: LOW
#   Method: Create a dictionary such as {"strategy": "momentum", "max_drawdown": "10%",
#           "stop_loss": "2%"} and perform string replacement using
#           Python's `re.sub` with a callback that looks up each token in
#           the dictionary.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Validate that no unresolved placeholders remain after substitution and raise
#   an informative error if any are found.
#   Reason: Unfilled placeholders indicate missing strategy data and could cause
#           downstream failures.
#   Impact: Improves robustness by catching configuration gaps early in the pipeline.
#   Complexity: LOW
#   Method: After substitution, run a second regex search for any remaining `{{.*}}`
#           patterns; if found, throw a `ValueError` listing the missing
#           tokens.
# -- END PRD --

from typing import List


def substitute_rule_placeholders(rules: str) -> List[str]:
    """
    Replaces strategy‑specific placeholder tokens in risk‑management rule templates with concrete values derived from the selected trading strategy.

    Args:
        rules: Input parameter of type str

    Returns:
        List[str]: Output of type List[str]
    """
    raise NotImplementedError("This is a virtual stub node that needs to be implemented")
