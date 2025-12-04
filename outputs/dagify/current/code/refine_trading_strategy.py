# -- PRD --
# 1. BULLET: Load the backtest output JSON produced by `backtest_trading_strategy` and
#   validate that `success` == true; if false, raise a controlled exception
#   and abort refinement with a clear error message.
#   Reason: Ensures the refinement cycle only runs on a clean, error‑free backtest,
#           preventing propagation of faulty data.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Parse JSON, check boolean flag, log detailed error using standard logging
#           library; wrap in try/catch to capture parsing exceptions.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Extract core performance metrics: `total_return`, `annualized_sharpe_ratio`,
#   `max_drawdown`, and `number_of_trades` from the backtest payload.
#   Reason: These metrics are the quantitative basis for evaluating whether the
#           strategy meets predefined investment objectives.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Map each field to a local variable; coerce types to float/int as defined in
#           the schema; store in a metrics dictionary.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Define target thresholds for each metric (e.g., Sharpe ≥ 1.2, max_drawdown ≤
#   0.15, total_return ≥ 0.10, trades between 30‑200) using a configurable
#   JSON/YAML file so that thresholds can be tuned without code changes.
#   Reason: Externalizing targets enables rapid experimentation and aligns the
#           refinement logic with portfolio manager expectations.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Read `refinement_targets.yaml` via `pyyaml`; fallback to hard‑coded
#           defaults if file missing; validate numeric ranges.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Compute a metric‑gap report by comparing each observed metric to its target,
#   categorizing gaps as `PASS`, `MARGINAL` (within 5% of target), or `FAIL`
#   (outside 5%). Store this classification for later decision logic.
#   Reason: Provides a systematic way to prioritize which aspects of the strategy need
#           adjustment.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Iterate over metric dictionary, calculate percent deviation, assign
#           categorical label; output a `gap_report` dict.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Perform a one‑factor sensitivity analysis for each tunable parameter,
#   indicator setting, and risk rule that was originally defined in
#   `develop_trading_signal_logic` and `define_risk_management_rules`. For
#   each factor, vary it ±10% (or a domain‑specific step) while holding
#   others constant, re‑run a lightweight backtest simulation using the same
#   price data (reuse the data preparation code from
#   `backtest_trading_strategy` but skip CSV I/O). Capture the resulting
#   metric changes.
#   Reason: Quantifies how each individual lever influences performance, identifying
#           high‑impact levers for adjustment.
#   Impact: HIGH
#   Complexity: HIGH
#   Method: Create a parameter grid; for each entry, clone the original strategy
#           object, modify the single field, call a simplified backtest
#           function (`simulate_backtest`) that returns the same metric
#           set; store results in a DataFrame for analysis.
# 
# -----------------------------------------------------------------------------
# 6. BULLET: Rank all factors by their sensitivity score defined as the absolute change in
#   Sharpe ratio multiplied by a weighting factor for drawdown and return
#   (e.g., `score = |ΔSharpe| * 0.5 + |ΔReturn| * 0.3 + |ΔDrawdown| * 0.2`).
#   Select the top‑3 factors where the metric gap is `FAIL` or `MARGINAL`.
#   Reason: Focuses refinement effort on the most influential levers that can close the
#           performance gaps.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Compute score per factor from sensitivity DataFrame, sort descending,
#           filter by gap classification.
# 
# -----------------------------------------------------------------------------
# 7. BULLET: Generate concrete adjustment proposals for the selected factors: for
#   parameters, propose the value that yielded the best Sharpe in the
#   sensitivity sweep; for indicators, adjust period lengths or thresholds to
#   the optimal values; for risk rules, tighten stop‑loss or modify
#   position‑size scaling factor as indicated by the analysis.
#   Reason: Provides data‑driven, actionable changes rather than heuristic guesses.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Extract the optimum value from the sensitivity DataFrame per factor; format
#           as bullet strings: `- Parameter XYZ: 0.05 → 0.08`.
# 
# -----------------------------------------------------------------------------
# 8. BULLET: Compose `parameter_adjustments`, `indicator_adjustments`, and
#   `risk_rule_adjustments` strings by concatenating the bullet points
#   generated in the previous step, preserving the order: parameters →
#   indicators → risk rules.
#   Reason: Ensures the output fields match the required schema and are human‑readable.
#   Impact: LOW
#   Complexity: LOW
#   Method: Join bullet list with newline characters; prepend a short header if desired
#           (e.g., "Adjusted Parameters:").
# 
# -----------------------------------------------------------------------------
# 9. BULLET: Draft `reasoning_for_adjustments` by linking each bullet to the specific
#   metric gap it addresses and citing the sensitivity score that motivated
#   the change. Use a structured paragraph format: "The Sharpe ratio fell
#   short of the 1.2 target (observed 0.95). Sensitivity analysis showed that
#   increasing the EMA period from 20 to 30 improved Sharpe by +0.18,
#   therefore the period was adjusted...".
#   Reason: Provides transparency and auditability for downstream stakeholders and for
#           the next refinement iteration.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Iterate over adjustment bullets, retrieve corresponding gap and score from
#           earlier dictionaries, concatenate explanatory sentences.
# 
# -----------------------------------------------------------------------------
# 10. BULLET: Assemble `refined_strategy_summary` that encapsulates the overall direction
#   of the refinement: mention which metric gaps were closed, any remaining
#   gaps, and a high‑level view of the new parameter/indicator/risk
#   configuration.
#   Reason: Serves as the executive‑level narrative for the downstream
#           `compile_final_strategy_blueprint` node.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Summarize metric changes (e.g., "Sharpe improved from 0.95 to 1.14"), list
#           the three key adjustments, and note any residual issues.
# 
# -----------------------------------------------------------------------------
# 11. BULLET: Validate that all output strings are non‑empty and conform to the expected
#   primitive types; if any field is empty, raise a validation error before
#   returning to enforce contract compliance.
#   Reason: Guarantees downstream nodes receive well‑formed data and prevents silent
#           failures.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Simple `if not field.strip(): raise ValueError` checks; unit‑test each
#           output field.
# -- END PRD --

from pydantic import BaseModel, Field


class BacktestTradingStrategyOutput(BaseModel):
    """Pydantic model for backtest_trading_strategy node outputs."""
    total_return: float = Field(..., description="Cumulative return of the strategy over the backtest period, expressed as a decimal (e.g., 0.12 for 12%).")
    annualized_sharpe_ratio: float = Field(..., description="Annualized Sharpe ratio of the strategy, assuming a risk\u2011free rate of 0%.")
    max_drawdown: float = Field(..., description="Maximum drawdown observed during the backtest, expressed as a decimal.")
    number_of_trades: int = Field(..., description="Total count of executed trades (both entries and exits) throughout the backtest.")
    backtest_period_start: str = Field(..., description="ISO\u2011format start date of the backtest period (YYYY\u2011MM\u2011DD).")
    backtest_period_end: str = Field(..., description="ISO\u2011format end date of the backtest period (YYYY\u2011MM\u2011DD).")
    success: bool = Field(..., description="True if the backtest completed without errors; false otherwise.")


class RefineTradingStrategyOutput(BaseModel):
    """Pydantic model for refine_trading_strategy node outputs."""
    refined_strategy_summary: str = Field(..., description="A concise narrative summarizing the refined trading strategy, highlighting adjusted parameters, indicator configurations, and risk\u2011management rules.")
    parameter_adjustments: str = Field(..., description="Bullet\u2011point list detailing each model parameter that was changed, including old and new values.")
    indicator_adjustments: str = Field(..., description="Bullet\u2011point list of technical indicator modifications, specifying the indicator name, previous settings, and revised settings.")
    risk_rule_adjustments: str = Field(..., description="Bullet\u2011point list of risk\u2011management rule changes (e.g., position sizing, stop\u2011loss/take\u2011profit levels) with before/after values.")
    reasoning_for_adjustments: str = Field(..., description="A thorough explanation linking each adjustment to the observed backtest shortcomings and the results of the sensitivity analysis.")


def refine_trading_strategy(backtest_trading_strategy_input: BacktestTradingStrategyOutput, **kwargs) -> RefineTradingStrategyOutput:
    """Iteratively enhances the quantitative trading strategy by performing a data‑driven, statistically rigorous refinement cycle.

    Args:
        backtest_trading_strategy_input: Input from the 'backtest_trading_strategy' node.
        **kwargs: Additional keyword arguments.

    Returns:
        RefineTradingStrategyOutput: Object containing outputs for this node.
    """
    # TODO: Implement this function

    # Return stub output with placeholder values
    return RefineTradingStrategyOutput(
        refined_strategy_summary="",
        parameter_adjustments="",
        indicator_adjustments="",
        risk_rule_adjustments="",
        reasoning_for_adjustments="",
    )