# -- PRD --
# 1. BULLET: Extract and validate all numeric inputs from the two dependency outputs,
#   converting them to floats and ensuring they are non‑negative.
#   Reason: Ensures data integrity before any calculations; prevents type‑mismatch
#           errors that would cascade to the final fee percentages.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Parse JSON, cast strings to float, apply `>= 0` checks, and log any
#           anomalies.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Calculate `hurdle_rate_percentage` by setting a base hurdle of 5 % absolute
#   return, but increase it to 5 % of the target gross return when the gross
#   target is below 10 %. Cap the hurdle at 8 % to keep the structure
#   attractive.
#   Reason: Balances incentive alignment with risk‑adjusted return expectations while
#           keeping the hurdle realistic for the chosen strategy.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Apply formula: `hurdle = min(8.0, max(5.0, gross_return * 0.5))` where
#           `gross_return` is from `set_performance_and_risk_targets`.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Determine `management_fee_percentage` by first normalizing the total annual
#   cost against a reference AUM of 100 M USD. If the cost ratio exceeds 3 %
#   of AUM, set the fee to 2 %; otherwise set it to 1.5 %.
#   Reason: Guarantees that management fees will cover operating expenses while
#           remaining competitive relative to industry averages.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Compute `cost_ratio = total_estimated_annual_cost / 100_000_000 * 100`;
#           then apply conditional assignment.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Set `performance_fee_percentage` to 20 % if the target Sharpe ratio is ≥ 1.0,
#   otherwise 25 %. If the target maximum drawdown exceeds 25 %, increase the
#   fee to 30 %.
#   Reason: Aligns performance incentives with the risk‑return profile: lower risk
#           yields a more attractive fee, whereas higher risk commands a
#           premium.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Implement nested conditional logic using the Sharpe ratio and maximum
#           drawdown values from `set_performance_and_risk_targets`.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Construct a `summary_sentence` that succinctly states the management fee,
#   performance fee, and hurdle rate, limiting the output to no more than two
#   sentences.
#   Reason: Directly satisfies the prompt’s requirement for a concise summary.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Template string interpolation: "Our fund charges a {m_fee:.1f}% management
#           fee, {p_fee:.1f}% performance fee above a {hurdle:.1f}%
#           hurdle."
# -- END PRD --

from pydantic import BaseModel, Field
from typing import List


class SetPerformanceAndRiskTargetsOutput(BaseModel):
    """Pydantic model for set_performance_and_risk_targets node outputs."""
    gross_return: float = Field(..., description="Target annual gross return expressed as a percentage (e.g., 15.0 for 15%).")
    volatility: float = Field(..., description="Target annual volatility (standard deviation) expressed as a percentage.")
    sharpe_ratio: float = Field(..., description="Target annual Sharpe ratio.")
    max_drawdown: float = Field(..., description="Target maximum annual drawdown expressed as a percentage.")


class EstimateSetupAndOperatingCostsOutput(BaseModel):
    """Pydantic model for estimate_setup_and_operating_costs node outputs."""
    cost_items: List[str] = Field(..., description="List of cost item names, including each service provider and overhead categories.")
    estimated_usd: List[float] = Field(..., description="Corresponding estimated annual cost in USD for each item in cost_items.")
    total_estimated_annual_cost: float = Field(..., description="Sum of all estimated USD values, representing the total annual cost.")


class DraftFeeStructureOutput(BaseModel):
    """Pydantic model for draft_fee_structure node outputs."""
    management_fee_percentage: float = Field(..., description="Annual management fee expressed as a percentage of assets under management.")
    performance_fee_percentage: float = Field(..., description="Annual performance fee expressed as a percentage of profits above the hurdle rate.")
    hurdle_rate_percentage: float = Field(..., description="Minimum annual return threshold that must be exceeded before performance fees are charged.")
    summary_sentence: str = Field(..., description="Concise description of the fee structure in one or two sentences.")


def draft_fee_structure(set_performance_and_risk_targets_input: SetPerformanceAndRiskTargetsOutput, estimate_setup_and_operating_costs_input: EstimateSetupAndOperatingCostsOutput, **kwargs) -> DraftFeeStructureOutput:
    """Set management and performance fee levels.

    Args:
        set_performance_and_risk_targets_input: Input from the 'set_performance_and_risk_targets' node.
        estimate_setup_and_operating_costs_input: Input from the 'estimate_setup_and_operating_costs' node.
        **kwargs: Additional keyword arguments.

    Returns:
        DraftFeeStructureOutput: Object containing outputs for this node.
    """
    # TODO: Implement this function

    # Return stub output with placeholder values
    return DraftFeeStructureOutput(
        management_fee_percentage=0.0,
        performance_fee_percentage=0.0,
        hurdle_rate_percentage=0.0,
        summary_sentence="",
    )