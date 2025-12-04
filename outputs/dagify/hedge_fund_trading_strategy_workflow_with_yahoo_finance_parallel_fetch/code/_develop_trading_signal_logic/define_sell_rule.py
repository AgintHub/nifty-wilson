# -- PRD --
# 1. BULLET: Parse and validate the `indicators` and `definitions` inputs, ensuring every
#   indicator appears in the definitions map.
#   Reason: Prevent runtime errors caused by missing or malformed definitions and
#           guarantee that the rule can be built reliably.
#   Impact: Raises early, clear validation errors; downstream logic receives only
#           verified data, improving robustness.
#   Complexity: MEDIUM
#   Method: Deserialize `definitions` from JSON, split `indicators` on commas, trim
#           whitespace, then cross‑check each indicator against the
#           dictionary; throw a custom `InvalidIndicatorError` on mismatch.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Translate each indicator into a logical predicate using its definition and
#   combine them into a cohesive sell‑rule expression.
#   Reason: The core purpose of the shim is to turn raw technical specifications into
#           an executable decision clause.
#   Impact: Produces a deterministic, readable rule (e.g., "IF RSI > 70 AND MACD < 0
#           THEN SELL") that can be consumed by downstream trading‑engine
#           nodes.
#   Complexity: HIGH
#   Method: Iterate over the ordered indicator list, fetch its definition, apply a
#           template engine (e.g., Jinja2) to render each predicate, then
#           join predicates with logical operators defined in a
#           configurable strategy (default AND).
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Validate the final rule string for syntactic correctness and return it in the
#   `output` field.
#   Reason: Even a correctly assembled string may contain syntax errors (unbalanced
#           brackets, missing operators) that would break execution later.
#   Impact: Ensures that the downstream `assemble_signal_logic_steps` receives a rule
#           that can be parsed/executed without failure.
#   Complexity: LOW
#   Method: Run a lightweight grammar check using a regular expression or a simple
#           parser library (e.g., `pyparsing`) to confirm the rule follows
#           the pattern "IF <condition> THEN SELL"; if validation passes,
#           assign to `output`, else raise `RuleSyntaxError`.
# -- END PRD --


def define_sell_rule(indicators: str, definitions: str) -> str:
    """
    Generates a deterministic sell‑signal rule string based on provided indicator names and their technical definitions.

    Args:
        indicators: Input parameter of type str
definitions: Input parameter of type str

    Returns:
        str: Output of type str
    """
    raise NotImplementedError("This is a virtual stub node that needs to be implemented")
