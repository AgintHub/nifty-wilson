from ._define_capital_requirements.calculate_regulatory_minimums import calculate_regulatory_minimums
from ._define_capital_requirements.calculate_trading_capital_needs import calculate_trading_capital_needs
from ._define_capital_requirements.calculate_operational_expenses import calculate_operational_expenses
from ._define_capital_requirements.calculate_weighted_average_initial_capital import calculate_weighted_average_initial_capital
from ._define_capital_requirements.calculate_weighted_average_ongoing_capital import calculate_weighted_average_ongoing_capital
from ._define_capital_requirements.generate_capital_breakdown import generate_capital_breakdown

from pydantic import BaseModel, Field


# -- PRD --
# 1. BULLET: Implement the calculation of initial capital requirements using the
#   regulatory minimums, trading capital needs, and operational expenses.
#   Reason: This approach provides the most accurate calculation of initial capital
#           requirements
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Use a weighted average of the regulatory minimums, trading capital needs,
#           and operational expenses to calculate the initial capital
#           requirements.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Implement the calculation of ongoing capital needs using the trading capital
#   needs and operational expenses.
#   Reason: This approach provides the most accurate calculation of ongoing capital
#           needs
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Use a weighted average of the trading capital needs and operational
#           expenses to calculate the ongoing capital needs.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Implement the breakdown of capital requirements by category using the
#   regulatory minimums, trading capital needs, and operational expenses.
#   Reason: This approach provides the most accurate breakdown of capital requirements
#           by category
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Use a weighted average of the regulatory minimums, trading capital needs,
#           and operational expenses to calculate the breakdown of capital
#           requirements by category.
# -- END PRD --



class IdentifyRegulatoryRequirementsOutput(BaseModel):
    """Pydantic model for identify_regulatory_requirements node outputs."""
    regulatory_requirements: str = Field(..., description="List of key regulatory requirements")
    entity_type: str = Field(..., description="Type of entity for the trading firm (LLC, Corporation, etc.)")
    selected_markets: str = Field(..., description="List of selected primary markets")


class DesignRiskManagementFrameworkOutput(BaseModel):
    """Pydantic model for design_risk_management_framework node outputs."""
    position_size_limits: int = Field(..., description="List of position size limits by asset type")
    portfolio_concentration_metrics: float = Field(..., description="List of portfolio concentration metrics")
    var_limit: float = Field(..., description="Value-at-Risk (VaR) limit")
    drawdown_limit: float = Field(..., description="Drawdown limit")
    pre_trade_risk_measures: str = Field(..., description="List of pre-trade risk measures")
    post_trade_risk_measures: str = Field(..., description="List of post-trade risk measures")


class DefineCapitalRequirementsOutput(BaseModel):
    """Pydantic model for define_capital_requirements node outputs."""
    initial_capital_requirements: float = Field(..., description="Initial capital requirements")
    ongoing_capital_needs: float = Field(..., description="Ongoing capital needs")
    capital_breakdown: str = Field(..., description="Breakdown of capital requirements by category")


def define_capital_requirements(identify_regulatory_requirements_input: IdentifyRegulatoryRequirementsOutput, design_risk_management_framework_input: DesignRiskManagementFrameworkOutput, **kwargs) -> DefineCapitalRequirementsOutput:
    """Calculate initial and ongoing capital needs

    Args:
        identify_regulatory_requirements_input: Input from the 'identify_regulatory_requirements' node.
        design_risk_management_framework_input: Input from the 'design_risk_management_framework' node.
        **kwargs: Additional keyword arguments.

    Returns:
        DefineCapitalRequirementsOutput: Object containing outputs for this node.
    """
    # Calculate regulatory minimum capital requirements
    regulatory_minimums: float = calculate_regulatory_minimums(
        entity_type=identify_regulatory_requirements_input.entity_type,
        selected_markets=identify_regulatory_requirements_input.selected_markets,
        regulatory_requirements=identify_regulatory_requirements_input.regulatory_requirements
    )
    
    # Calculate trading capital needs based on risk framework
    trading_capital_needs: float = calculate_trading_capital_needs(
        position_size_limits=design_risk_management_framework_input.position_size_limits,
        var_limit=design_risk_management_framework_input.var_limit,
        drawdown_limit=design_risk_management_framework_input.drawdown_limit
    )
    
    # Calculate operational expenses
    operational_expenses: float = calculate_operational_expenses(
        entity_type=identify_regulatory_requirements_input.entity_type,
        selected_markets=identify_regulatory_requirements_input.selected_markets
    )
    
    # Calculate initial capital requirements using weighted average
    initial_capital: float = calculate_weighted_average_initial_capital(
        regulatory_minimums=regulatory_minimums,
        trading_capital_needs=trading_capital_needs,
        operational_expenses=operational_expenses
    )
    
    # Calculate ongoing capital needs using weighted average
    ongoing_capital: float = calculate_weighted_average_ongoing_capital(
        trading_capital_needs=trading_capital_needs,
        operational_expenses=operational_expenses
    )
    
    # Generate capital breakdown by category
    breakdown: str = generate_capital_breakdown(
        regulatory_minimums=regulatory_minimums,
        trading_capital_needs=trading_capital_needs,
        operational_expenses=operational_expenses
    )
    
    return DefineCapitalRequirementsOutput(
        initial_capital_requirements=initial_capital,
        ongoing_capital_needs=ongoing_capital,
        capital_breakdown=breakdown
    )