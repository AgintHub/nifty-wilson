# -- PRD --
# 1. BULLET: Extract the `strategy_type` string from the output of the parent node
#   **select_trading_strategy_type** and normalize it to lower‑case for
#   deterministic matching.
#   Reason: A normalized strategy identifier eliminates case‑sensitivity bugs and
#           enables reliable rule‑selection logic.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Read the JSON field `strategy_type`, apply `.strip().lower()`; store the
#           result in a variable `strategy`. Raise a clear error if the
#           field is missing or empty.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Create a static mapping dictionary where each possible `strategy_type` (e.g.,
#   "momentum", "mean reversion", "statistical arbitrage", "trend following")
#   maps to a pre‑validated list of 3‑5 risk‑management rule templates.
#   Reason: A deterministic mapping guarantees reproducible rule generation and aligns
#           risk controls with the underlying tactical logic of each
#           strategy.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Define a Python dict `RULE_TEMPLATES = { 'momentum': [ 'Limit position size
#           to X% of portfolio equity per ticker.', 'Set a trailing
#           stop‑loss at Y% below entry price.', 'Cap daily portfolio
#           turnover at Z% of total equity.', 'Restrict maximum drawdown to
#           D% of peak equity.', 'Allocate no more than N% of capital to
#           any single sector.' ], ... }`. Ensure each list contains
#           between 3 and 5 items and includes at least one stop‑loss rule.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Select the appropriate rule list from `RULE_TEMPLATES` using the normalized
#   `strategy` key; if the key is absent, fall back to a generic baseline
#   rule set and log a warning.
#   Reason: Fallback handling prevents the workflow from failing for unexpected
#           strategy strings while still providing sensible risk controls.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Use `rules = RULE_TEMPLATES.get(strategy, RULE_TEMPLATES['generic'])`.
#           Store the selected list in `selected_rules`.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Iterate over `selected_rules` and perform placeholder substitution for any
#   strategy‑specific parameters (e.g., replace X, Y, Z, D, N with concrete
#   numeric values derived from typical industry standards or configurable
#   constants).
#   Reason: Dynamic substitution turns abstract templates into actionable, concrete
#           rules ready for downstream consumption.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Define a constants dict `DEFAULTS = { 'X': '2%', 'Y': '5%', 'Z': '15%',
#           'D': '10%', 'N': '20%' }`. For each rule string, replace each
#           placeholder token using regex `re.sub(r'\bX\b', DEFAULTS['X'],
#           rule)` etc.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Compute `rule_count` as `len(selected_rules)` and verify that it lies within
#   the required range [3,5]; raise a validation exception if not.
#   Reason: Enforcing the rule‑count constraint ensures compliance with the node's
#           output contract and downstream expectations.
#   Impact: HIGH
#   Complexity: LOW
#   Method: If `rule_count < 3 or rule_count > 5`: `raise ValueError('Risk‑management
#           rule count must be between 3 and 5.')`.
# 
# -----------------------------------------------------------------------------
# 6. BULLET: Determine `has_stop_loss` by scanning the finalized rule strings for the
#   substring "stop‑loss" (case‑insensitive). Set the boolean accordingly.
#   Reason: Explicit detection of a stop‑loss rule is required for the `has_stop_loss`
#           output field.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: `has_stop_loss = any('stop-loss' in rule.lower() for rule in
#           selected_rules)`.
# 
# -----------------------------------------------------------------------------
# 7. BULLET: Assemble the final output payload: `risk_management_rules` = `selected_rules`
#   (preserve order), `rule_count` = computed integer, `has_stop_loss` =
#   boolean flag; serialize to the expected JSON schema.
#   Reason: A single, well‑structured payload enables downstream nodes (e.g.,
#           **compile_final_strategy_blueprint**) to consume the data
#           without additional transformation.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Create a dict `{ 'risk_management_rules': selected_rules, 'rule_count':
#           rule_count, 'has_stop_loss': has_stop_loss }` and return it as
#           the node's response.
# 
# -----------------------------------------------------------------------------
# 8. BULLET: Log a concise human‑readable summary containing the selected strategy, the
#   generated rules, `rule_count`, and `has_stop_loss` for auditability.
#   Reason: Transparent logging aids debugging and provides traceability for compliance
#           reviews.
#   Impact: LOW
#   Complexity: LOW
#   Method: Use the platform logger: `logger.info(f"Strategy: {strategy}; Rules:
#           {selected_rules}; Count: {rule_count}; Stop‑Loss present:
#           {has_stop_loss}")`.
# -- END PRD --

from pydantic import BaseModel, Field
from typing import List


class SelectTradingStrategyTypeOutput(BaseModel):
    """Pydantic model for select_trading_strategy_type node outputs."""
    strategy_type: str = Field(..., description="The chosen primary trading strategy type (e.g., \"momentum\", \"mean reversion\").")
    rationale: str = Field(..., description="A concise one\u2011sentence explanation of why this strategy type best fits the market analysis.")


class DefineRiskManagementRulesOutput(BaseModel):
    """Pydantic model for define_risk_management_rules node outputs."""
    risk_management_rules: List[str] = Field(..., description="Bullet\u2011point list (3\u20115 items) detailing the concrete risk\u2011management rules such as position sizing, stop\u2011loss, max drawdown, etc.")
    rule_count: int = Field(..., description="The total number of risk\u2011management rules provided (must be between 3 and 5).")
    has_stop_loss: bool = Field(..., description="True if the list includes an explicit stop\u2011loss rule; otherwise false.")


def define_risk_management_rules(select_trading_strategy_type_input: SelectTradingStrategyTypeOutput, **kwargs) -> DefineRiskManagementRulesOutput:
    """Establishes a rigorous, quantitative risk‑management framework that translates the chosen trading strategy into actionable safeguards.

    Args:
        select_trading_strategy_type_input: Input from the 'select_trading_strategy_type' node.
        **kwargs: Additional keyword arguments.

    Returns:
        DefineRiskManagementRulesOutput: Object containing outputs for this node.
    """
    # TODO: Implement this function

    # Return stub output with placeholder values
    return DefineRiskManagementRulesOutput(
        risk_management_rules=[],
        rule_count=0,
        has_stop_loss=False,
    )