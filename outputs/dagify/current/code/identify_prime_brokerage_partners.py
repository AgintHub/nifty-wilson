# -- PRD --
# 1. BULLET: Define the evaluation criteria for prime brokerage partners and execution
#   venues
#   Reason: To ensure that the prime brokerage partners and execution venues are
#           selected based on their capabilities and fit for Jane Street's
#           trading operations
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Use a weighted scoring system to evaluate the prime brokerage partners and
#           execution venues based on factors like execution quality,
#           technology connectivity, margin rates, and counterparty risk
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Research and identify potential prime brokerage partners and execution venues
#   Reason: To gather information about the prime brokerage partners and execution
#           venues and assess their capabilities and fit for Jane Street's
#           trading operations
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Use online research tools and databases to identify potential prime
#           brokerage partners and execution venues, and contact them to
#           gather more information
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Assess the prime brokerage partners and execution venues based on the
#   evaluation criteria
#   Reason: To determine the potential prime brokerage partners and execution venues
#           that best fit Jane Street's trading operations
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Use a weighted scoring system to assess the prime brokerage partners and
#           execution venues based on factors like execution quality,
#           technology connectivity, margin rates, and counterparty risk
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Select the prime brokerage partners and execution venues
#   Reason: To identify the prime brokerage partners and execution venues that best fit
#           Jane Street's trading operations
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Select the prime brokerage partners and execution venues that received the
#           highest scores in the assessment
# -- END PRD --

from pydantic import BaseModel, Field
from typing import List


class SelectPrimaryMarketsOutput(BaseModel):
    """Pydantic model for select_primary_markets node outputs."""
    primary_markets: List[str] = Field(..., description="List of selected primary markets and exchanges")
    market_selection_reasoning: str = Field(..., description="Rationale for selecting each primary market and exchange")
    liquidity_risk_assessment: str = Field(..., description="Assessment of liquidity risk in each selected market")
    regulatory_environment: str = Field(..., description="Overview of regulatory requirements and implications for each selected market")
    competitive_landscape: str = Field(..., description="Analysis of competitive landscape in each selected market")


class DefineCapitalRequirementsOutput(BaseModel):
    """Pydantic model for define_capital_requirements node outputs."""
    initial_capital_requirements: float = Field(..., description="Initial capital requirements")
    ongoing_capital_needs: float = Field(..., description="Ongoing capital needs")
    capital_breakdown: str = Field(..., description="Breakdown of capital requirements by category")


class IdentifyPrimeBrokeragePartnersOutput(BaseModel):
    """Pydantic model for identify_prime_brokerage_partners node outputs."""
    prime_brokerage_partners: List[str] = Field(..., description="List of potential prime brokerage partners")
    execution_venues: List[str] = Field(..., description="List of potential execution venues")


def identify_prime_brokerage_partners(select_primary_markets_input: SelectPrimaryMarketsOutput, define_capital_requirements_input: DefineCapitalRequirementsOutput, **kwargs) -> IdentifyPrimeBrokeragePartnersOutput:
    """Select prime brokers and execution venues

    Args:
        select_primary_markets_input: Input from the 'select_primary_markets' node.
        define_capital_requirements_input: Input from the 'define_capital_requirements' node.
        **kwargs: Additional keyword arguments.

    Returns:
        IdentifyPrimeBrokeragePartnersOutput: Object containing outputs for this node.
    """
    # TODO: Implement this function

    # Return stub output with placeholder values
    return IdentifyPrimeBrokeragePartnersOutput(
        prime_brokerage_partners=[],
        execution_venues=[],
    )