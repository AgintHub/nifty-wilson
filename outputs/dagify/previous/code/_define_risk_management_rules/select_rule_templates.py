# -- PRD --
# 1. BULLET: Parse and validate the `templates` JSON string into a dictionary mapping
#   strategy names to lists of rule strings.
#   Reason: The shim receives the templates as a serialized string; converting it to a
#           usable data structure is essential for reliable lookup.
#   Impact: Prevents runtime errors caused by malformed JSON and ensures subsequent
#           lookup operations have a correct source.
#   Complexity: LOW
#   Method: Use `json.loads` with exception handling to convert the string to a dict;
#           raise a clear ValueError if parsing fails.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Retrieve the rule list for the given `strategy` key, falling back to a
#   generic default list when the strategy is not present.
#   Reason: Not every strategy may have a dedicated template; a fallback guarantees the
#           function always returns a valid list of rules.
#   Impact: Ensures the downstream risk‑management node always receives a non‑empty
#           rule set, preserving pipeline continuity.
#   Complexity: LOW
#   Method: Perform a dict `get` lookup: `selected = templates_dict.get(strategy,
#           templates_dict.get('default', []))`.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Return the selected rule list as the `output` field while echoing the
#   original inputs for traceability.
#   Reason: The function’s contract requires returning the rule list together with the
#           inputs to enable downstream logging and debugging.
#   Impact: Facilitates auditability and makes the shim’s output compatible with the
#           Pydantic model expectations of the calling node.
#   Complexity: LOW
#   Method: Construct a dict `{ "output": selected, "strategy": strategy, "templates":
#           templates }` and let the framework serialize it.
# -- END PRD --

from typing import List


def select_rule_templates(strategy: str, templates: str) -> List[str]:
    """
    Selects and returns a list of rule template strings that correspond to the provided trading strategy.

    Args:
        strategy: Input parameter of type str
templates: Input parameter of type str

    Returns:
        List[str]: Output of type List[str]
    """
    raise NotImplementedError("This is a virtual stub node that needs to be implemented")
