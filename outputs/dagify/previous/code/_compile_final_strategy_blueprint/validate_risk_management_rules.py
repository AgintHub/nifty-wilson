# -- PRD --
# 1. BULLET: Parse the `rules` string into a Python list of trimmed rule strings.
#   Reason: The shim receives rules as a raw string; converting to a list enables
#           reliable validation and downstream processing.
#   Impact: Ensures consistent data type for further checks and prevents malformed
#           inputs from propagating.
#   Complexity: LOW
#   Method: Use `json.loads` for JSON arrays; fallback to splitting on newlines; strip
#           whitespace from each element.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Validate that the rule count is between 3 and 5 inclusive.
#   Reason: Business logic requires a concise yet comprehensive set of risk controls.
#   Impact: Guarantees the strategy adheres to expected risk‑management granularity and
#           prevents over‑/under‑specification.
#   Complexity: LOW
#   Method: Check `len(rules_list)`; raise `ValueError` with a clear message if out of
#           bounds.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: If `has_stop_loss` is true, confirm at least one rule mentions a stop‑loss
#   and raise an error otherwise.
#   Reason: A stop‑loss is a critical safety mechanism for the strategy; its absence
#           when required is unacceptable.
#   Impact: Prevents deployment of strategies lacking essential protection, reducing
#           potential losses.
#   Complexity: MEDIUM
#   Method: Normalize `has_stop_loss` to a boolean; search the list for
#           case‑insensitive substrings like "stop‑loss" or "stop loss";
#           raise `ValueError` if not found.
# -- END PRD --

from typing import List


def validate_risk_management_rules(rules: str, has_stop_loss: str) -> List[str]:
    """
    Validates a list of risk‑management rules ensuring the correct count and mandatory stop‑loss inclusion, returning the sanitized list.

    Args:
        rules: Input parameter of type str
has_stop_loss: Input parameter of type str

    Returns:
        List[str]: Output of type List[str]
    """
    raise NotImplementedError("This is a virtual stub node that needs to be implemented")
