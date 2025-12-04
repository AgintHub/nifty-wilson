# -- PRD --
# 1. BULLET: Extract the full refined‑strategy payload from the
#   **refine_trading_strategy** node – specifically the fields
#   `refined_strategy_summary`, `parameter_adjustments`,
#   `indicator_adjustments`, and `risk_rule_adjustments` – and concatenate
#   them into a single, coherent technical description for
#   `refined_strategy_details`.
#   Reason: The refined strategy details must capture all final rule‑level changes
#           (parameters, indicators, risk tweaks) in an easily readable
#           format for developers and reviewers.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Parse each string field, strip any leading/trailing whitespace, and join
#           sections using clear headings (e.g., "## Parameter
#           Adjustments"). Ensure bullet‑point consistency by prefixing
#           each adjustment with a dash. Preserve original numeric
#           precision.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Read the `risk_management_rules` list from the
#   **define_risk_management_rules** node and verify that the list length is
#   between 3 and 5 items and that at least one rule contains the keyword
#   "stop‑loss" (ensuring `has_stop_loss` is true).
#   Reason: Compliance with the specification guarantees a disciplined risk‑control
#           framework and satisfies downstream validation checks.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Iterate over the list, count elements, and perform a case‑insensitive
#           search for the substring "stop‑loss". Raise a clear error
#           message if constraints are violated.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Obtain the asset‑universe ticker list from the **specify_asset_universe**
#   node – field `asset_tickers` – and assign it to the output field
#   `asset_universe`.
#   Reason: Although not a direct dependency in the DAG, the blueprint must expose the
#           exact symbols that will be traded; pulling them from the
#           asset‑universe node ensures source‑of‑truth consistency.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Reference the global execution context to read `asset_tickers`. Validate
#           that each ticker is a non‑empty string and deduplicate any
#           accidental repeats.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Craft the `blueprint_summary` string by merging (a) the strategic intent
#   described in `refined_strategy_summary`, (b) the market thesis inferred
#   from the chosen strategy type, and (c) quantitative targets (e.g., target
#   annualized Sharpe > 1.5, max drawdown < 10%). Include a one‑sentence
#   operational cadence (e.g., "Daily end‑of‑day signal generation and
#   execution").
#   Reason: Stakeholders need a concise executive overview that communicates why the
#           strategy is pursued and what performance benchmarks are
#           expected.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Use a template: ``` [Strategy Name] – [Market Thesis] Target
#           Return‑to‑Risk: [target ratio] Operational Cadence: [frequency]
#           ``` Populate placeholders from the refined summary and, when
#           necessary, from back‑test metrics (available upstream).
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Generate an `Implementation Checklist` as a plain‑text bullet list (not part
#   of the explicit output fields but useful for internal documentation)
#   covering: data ingestion, signal computation, risk‑rule enforcement,
#   order routing, position monitoring, logging, and periodic performance
#   review.
#   Reason: A checklist ensures that every component required for production deployment
#           is accounted for and can be handed off to engineering teams.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Create a static list of 7‑8 items, each prefixed with "- ". Store it as an
#           internal variable that can be optionally appended to the
#           `blueprint_summary` if desired.
# 
# -----------------------------------------------------------------------------
# 6. BULLET: Validate final output types: ensure `blueprint_summary` and
#   `refined_strategy_details` are strings, `risk_management_rules` is a list
#   of strings, and `asset_universe` is a list of strings. Throw descriptive
#   exceptions for any mismatch.
#   Reason: Strict type compliance prevents downstream runtime errors and aligns with
#           the platform's schema enforcement.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Perform isinstance checks; for list elements, iterate and assert
#           isinstance(item, str).
# 
# -----------------------------------------------------------------------------
# 7. BULLET: Serialize the four output fields into the node's response JSON adhering
#   exactly to the defined `output_structure` order.
#   Reason: Correct serialization is required for the orchestration engine to route the
#           data to subsequent nodes.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Construct a Python dict with keys matching the field names and feed it to
#           the platform's `return` routine.
# -- END PRD --

from pydantic import BaseModel, Field
from typing import List


class RefineTradingStrategyOutput(BaseModel):
    """Pydantic model for refine_trading_strategy node outputs."""
    refined_strategy_summary: str = Field(..., description="A concise narrative summarizing the refined trading strategy, highlighting adjusted parameters, indicator configurations, and risk\u2011management rules.")
    parameter_adjustments: str = Field(..., description="Bullet\u2011point list detailing each model parameter that was changed, including old and new values.")
    indicator_adjustments: str = Field(..., description="Bullet\u2011point list of technical indicator modifications, specifying the indicator name, previous settings, and revised settings.")
    risk_rule_adjustments: str = Field(..., description="Bullet\u2011point list of risk\u2011management rule changes (e.g., position sizing, stop\u2011loss/take\u2011profit levels) with before/after values.")
    reasoning_for_adjustments: str = Field(..., description="A thorough explanation linking each adjustment to the observed backtest shortcomings and the results of the sensitivity analysis.")


class DefineRiskManagementRulesOutput(BaseModel):
    """Pydantic model for define_risk_management_rules node outputs."""
    risk_management_rules: List[str] = Field(..., description="Bullet\u2011point list (3\u20115 items) detailing the concrete risk\u2011management rules such as position sizing, stop\u2011loss, max drawdown, etc.")
    rule_count: int = Field(..., description="The total number of risk\u2011management rules provided (must be between 3 and 5).")
    has_stop_loss: bool = Field(..., description="True if the list includes an explicit stop\u2011loss rule; otherwise false.")


class CompileFinalStrategyBlueprintOutput(BaseModel):
    """Pydantic model for compile_final_strategy_blueprint node outputs."""
    blueprint_summary: str = Field(..., description="High\u2011level narrative summarizing the strategy\u2019s purpose, market thesis, target return\u2011to\u2011risk ratio, and operational cadence.")
    refined_strategy_details: str = Field(..., description="Technical description of the final entry/exit rules, indicator settings, parameter values, and any conditional logic after back\u2011testing refinement.")
    risk_management_rules: List[str] = Field(..., description="Bullet\u2011point list (3\u20115 items) of risk controls such as position sizing formulas, stop\u2011loss/take\u2011profit levels, max draw\u2011down limits, and portfolio exposure caps.")
    asset_universe: List[str] = Field(..., description="Complete list of tradable symbols, ticker codes, or asset\u2011class identifiers that constitute the strategy\u2019s trading scope.")


def compile_final_strategy_blueprint(refine_trading_strategy_input: RefineTradingStrategyOutput, define_risk_management_rules_input: DefineRiskManagementRulesOutput, **kwargs) -> CompileFinalStrategyBlueprintOutput:
    """Synthesizes the refined trading logic, rigorously defined risk‑management policies, and the designated asset universe into a single, end‑to‑end blueprint ready for implementation, back‑testing, and deployment.

    Args:
        refine_trading_strategy_input: Input from the 'refine_trading_strategy' node.
        define_risk_management_rules_input: Input from the 'define_risk_management_rules' node.
        **kwargs: Additional keyword arguments.

    Returns:
        CompileFinalStrategyBlueprintOutput: Object containing outputs for this node.
    """
    # TODO: Implement this function

    # Return stub output with placeholder values
    return CompileFinalStrategyBlueprintOutput(
        blueprint_summary="",
        refined_strategy_details="",
        risk_management_rules=[],
        asset_universe=[],
    )