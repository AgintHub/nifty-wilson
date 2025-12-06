# -- PRD --
# 1. BULLET: Parse the output of the parent node `choose_investment_strategy` to identify
#   the selected strategy category and its qualitative performance
#   benchmarks.
#   Reason: The risk and return targets must be calibrated to the chosen strategy;
#           hence we need the strategy name and any high‑level benchmark
#           references.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Read the `strategy_category` field from the parent’s output; if the
#           strategy includes a benchmark (e.g., S&P 500 for Long/Short
#           Equity), retrieve its historical annualized return, volatility,
#           and Sharpe ratio from a pre‑loaded database. Use these figures
#           as a baseline for target setting.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Define a target gross return that is 5% above the strategy’s historical mean
#   return, but capped at a realistic maximum of 30% to maintain credibility.
#   Reason: Setting targets modestly higher than historical performance provides
#           ambition without overpromising.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Calculate mean annual return (μ) from historical data; set `gross_return =
#           min(μ + 5, 30.0)`.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Set volatility to 20–30% higher than the strategy’s historical volatility to
#   account for future uncertainty, with an upper bound of 25% to avoid
#   extreme risk appetite.
#   Reason: Risk targets should reflect a conservative margin over past volatility
#           while ensuring the fund is not perceived as excessively risky.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Compute historical σ; set `volatility = min(σ * 1.2, 25.0)`.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Derive the Sharpe ratio target as the historical Sharpe ratio plus 0.1,
#   limited to a maximum of 2.0 to maintain realistic expectations.
#   Reason: Sharpe ratio is a key performance metric; a modest increase signals
#           performance improvement without being overly optimistic.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Retrieve historical Sharpe S; set `sharpe_ratio = min(S + 0.1, 2.0)`.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Define maximum drawdown as 50% of the historical peak‑to‑trough drawdown, but
#   not exceeding 45% to keep the target achievable.
#   Reason: Drawdown tolerance should be moderate; tying it to historical extremes
#           ensures realism.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Calculate historical D; set `max_drawdown = min(D * 0.5, 45.0)`.
# 
# -----------------------------------------------------------------------------
# 6. BULLET: Validate that the resulting target metrics are internally consistent:
#   volatility should be >= target gross return divided by Sharpe ratio, and
#   max_drawdown should be <= 3× volatility to avoid overly aggressive
#   targets.
#   Reason: Consistency checks prevent contradictory metrics that could mislead
#           stakeholders.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Perform the two checks; if either fails, adjust volatility downwards or
#           gross_return upwards within the defined bounds until all
#           conditions hold.
# 
# -----------------------------------------------------------------------------
# 7. BULLET: Format the four numerical outputs into a plain 4‑row table, rounding each
#   value to one decimal place and appending a percentage sign for clarity.
#   Reason: The prompt explicitly requests a table; formatting improves readability for
#           downstream nodes.
#   Impact: LOW
#   Complexity: LOW
#   Method: Generate a string: `| Metric | Target | |-------|--------| | Gross Return |
#           X.X% | | Volatility | Y.Y% | | Sharpe Ratio | Z.Z | | Max
#           Drawdown | W.W% |`.
# 
# -----------------------------------------------------------------------------
# 8. BULLET: Populate the JSON output structure with the computed float values (without
#   percentage signs) to satisfy the downstream node type requirements.
#   Reason: While the table is for human consumption, the programmatic output must be
#           in raw numeric form.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Assign `gross_return`, `volatility`, `sharpe_ratio`, and `max_drawdown` to
#           the JSON payload as floats.
# -- END PRD --

from pydantic import BaseModel, Field


class ChooseInvestmentStrategyOutput(BaseModel):
    """Pydantic model for choose_investment_strategy node outputs."""
    strategy_category: str = Field(..., description="Primary hedge fund strategy category selected (e.g., Long/Short Equity, Global Macro).")
    rationale: str = Field(..., description="One-sentence rationale explaining why this strategy best serves the fund objectives.")


class SetPerformanceAndRiskTargetsOutput(BaseModel):
    """Pydantic model for set_performance_and_risk_targets node outputs."""
    gross_return: float = Field(..., description="Target annual gross return expressed as a percentage (e.g., 15.0 for 15%).")
    volatility: float = Field(..., description="Target annual volatility (standard deviation) expressed as a percentage.")
    sharpe_ratio: float = Field(..., description="Target annual Sharpe ratio.")
    max_drawdown: float = Field(..., description="Target maximum annual drawdown expressed as a percentage.")


def set_performance_and_risk_targets(choose_investment_strategy_input: ChooseInvestmentStrategyOutput, **kwargs) -> SetPerformanceAndRiskTargetsOutput:
    """Quantify return and risk goals.

    Args:
        choose_investment_strategy_input: Input from the 'choose_investment_strategy' node.
        **kwargs: Additional keyword arguments.

    Returns:
        SetPerformanceAndRiskTargetsOutput: Object containing outputs for this node.
    """
    # TODO: Implement this function

    # Return stub output with placeholder values
    return SetPerformanceAndRiskTargetsOutput(
        gross_return=0.0,
        volatility=0.0,
        sharpe_ratio=0.0,
        max_drawdown=0.0,
    )