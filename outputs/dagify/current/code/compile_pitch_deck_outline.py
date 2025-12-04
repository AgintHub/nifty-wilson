# -- PRD --
# 1. BULLET: Verify that all required parent outputs are present and non‑empty before
#   proceeding.
#   Reason: Ensures that the downstream logic has the necessary data to construct
#           meaningful slide titles.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Programmatically check that `clarify_fund_objectives.objectives`,
#           `define_investor_profile.target_investor_segment`,
#           `choose_investment_strategy.strategy_category`,
#           `set_performance_and_risk_targets.gross_return`,
#           `draft_fee_structure.management_fee_percentage`, and
#           `design_risk_management_framework.risk_controls` exist and are
#           of the expected type.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Extract high‑level messaging elements from each parent output to identify
#   core narrative themes.
#   Reason: These themes directly inform the slide titles and ensure each title aligns
#           with the fund’s unique selling propositions.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Parse the list of objectives to select the top 3 most impactful bullets;
#           capture the strategy category and rationale; pull target gross
#           return, volatility, Sharpe ratio, and max drawdown; record the
#           fee structure summary; and compile the first 4 risk control
#           statements.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Define a canonical slide order based on investor deck best practices:
#   Introduction, Overview, Objectives, Strategy, Team, Edge, Performance,
#   Risk, Fees, Expected Returns.
#   Reason: A consistent sequence improves narrative flow and meets investor
#           expectations.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Use a hard‑coded list of 10 titles as a template, with placeholders for
#           dynamic terms.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Generate each slide title, inserting dynamic terms from parent data where
#   relevant (e.g., strategy category, target gross return, risk limit
#   keywords).
#   Reason: Personalized titles increase engagement and signal that the deck is
#           tailored to the fund’s specifics.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: String interpolation: replace `{strategy}` with the chosen strategy,
#           `{return}` with the gross return percentage, and `{risk}` with
#           the key risk control phrase.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Enforce title length constraints (≤ 7 words) and grammatical consistency (no
#   trailing punctuation, proper capitalization).
#   Reason: Short, punchy titles are easier to read and more visually appealing.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Token count per title, regex trimming of punctuation, title‑case
#           conversion.
# 
# -----------------------------------------------------------------------------
# 6. BULLET: Validate that the final list contains exactly ten unique titles.
#   Reason: Matches the specified output structure and prevents accidental duplication.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Count list length and check for duplicates via set comparison.
# 
# -----------------------------------------------------------------------------
# 7. BULLET: Package the validated list into the `slide_titles` output field and serialize
#   to JSON.
#   Reason: Ensures the node’s contract is fulfilled and downstream nodes can consume
#           the data.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Construct a dict with the key `slide_titles` mapping to the ordered list,
#           then use a JSON library to output.
# -- END PRD --

from pydantic import BaseModel, Field
from typing import List


class ClarifyFundObjectivesOutput(BaseModel):
    """Pydantic model for clarify_fund_objectives node outputs."""
    objectives: str = Field(..., description="Bullet list of the fund's core objectives, each item a concise statement.")
    objective_count: int = Field(..., description="Number of objective bullets provided.")


class DefineInvestorProfileOutput(BaseModel):
    """Pydantic model for define_investor_profile node outputs."""
    target_investor_segment: str = Field(..., description="Primary type of investor (e.g., family office, pension, high\u2011net\u2011worth individual)")
    typical_ticket_size_min: float = Field(..., description="Minimum typical investment amount in USD")
    typical_ticket_size_max: float = Field(..., description="Maximum typical investment amount in USD")
    risk_tolerance: str = Field(..., description="General risk tolerance level of target investors (e.g., high, moderate, low)")
    liquidity_preference: str = Field(..., description="Preferred liquidity horizon (e.g., short\u2011term, medium\u2011term, long\u2011term)")
    geographic_focus: str = Field(..., description="List of preferred geographic regions or markets for the investors")


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


class DraftFeeStructureOutput(BaseModel):
    """Pydantic model for draft_fee_structure node outputs."""
    management_fee_percentage: float = Field(..., description="Annual management fee expressed as a percentage of assets under management.")
    performance_fee_percentage: float = Field(..., description="Annual performance fee expressed as a percentage of profits above the hurdle rate.")
    hurdle_rate_percentage: float = Field(..., description="Minimum annual return threshold that must be exceeded before performance fees are charged.")
    summary_sentence: str = Field(..., description="Concise description of the fee structure in one or two sentences.")


class DesignRiskManagementFrameworkOutput(BaseModel):
    """Pydantic model for design_risk_management_framework node outputs."""
    risk_controls: List[str] = Field(..., description="List of core risk control statements aligned with the target metrics.")


class CompilePitchDeckOutlineOutput(BaseModel):
    """Pydantic model for compile_pitch_deck_outline node outputs."""
    slide_titles: str = Field(..., description="An ordered list of 10 slide titles, each representing a key component of the pitch deck such as objectives, strategy, team, edge, risk controls, fees, and expected returns.")


def compile_pitch_deck_outline(clarify_fund_objectives_input: ClarifyFundObjectivesOutput, define_investor_profile_input: DefineInvestorProfileOutput, choose_investment_strategy_input: ChooseInvestmentStrategyOutput, set_performance_and_risk_targets_input: SetPerformanceAndRiskTargetsOutput, draft_fee_structure_input: DraftFeeStructureOutput, design_risk_management_framework_input: DesignRiskManagementFrameworkOutput, **kwargs) -> CompilePitchDeckOutlineOutput:
    """Framework for fundraising presentation.

    Args:
        clarify_fund_objectives_input: Input from the 'clarify_fund_objectives' node.
        define_investor_profile_input: Input from the 'define_investor_profile' node.
        choose_investment_strategy_input: Input from the 'choose_investment_strategy' node.
        set_performance_and_risk_targets_input: Input from the 'set_performance_and_risk_targets' node.
        draft_fee_structure_input: Input from the 'draft_fee_structure' node.
        design_risk_management_framework_input: Input from the 'design_risk_management_framework' node.
        **kwargs: Additional keyword arguments.

    Returns:
        CompilePitchDeckOutlineOutput: Object containing outputs for this node.
    """
    # TODO: Implement this function

    # Return stub output with placeholder values
    return CompilePitchDeckOutlineOutput(
        slide_titles="",
    )