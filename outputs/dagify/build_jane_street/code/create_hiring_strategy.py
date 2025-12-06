from ._create_hiring_strategy.analyze_technology_skill_requirements import analyze_technology_skill_requirements
from ._create_hiring_strategy.analyze_strategy_skill_requirements import analyze_strategy_skill_requirements
from ._create_hiring_strategy.combine_role_requirements import combine_role_requirements
from ._create_hiring_strategy.design_compensation_structure import design_compensation_structure
from ._create_hiring_strategy.create_recruitment_approach import create_recruitment_approach
from ._create_hiring_strategy.calculate_hiring_targets import calculate_hiring_targets

from pydantic import BaseModel, Field
from typing import List


class SpecifyTechnologyArchitectureOutput(BaseModel):
    """Pydantic model for specify_technology_architecture node outputs."""
    trading_systems: List[str] = Field(..., description="List of low-latency trading systems used")
    data_feeds: List[str] = Field(..., description="List of data feeds used for trading")
    risk_management_systems: List[str] = Field(..., description="List of risk management systems used for trading")
    connectivity_requirements: str = Field(..., description="Description of connectivity requirements for trading")


class DesignTradingStrategiesOutput(BaseModel):
    """Pydantic model for design_trading_strategies node outputs."""
    trading_strategy_count: int = Field(..., description="Number of trading strategies developed")
    strategy_names: str = Field(..., description="List of trading strategy names")
    market_maker_strategies: bool = Field(..., description="Whether market making strategies are included")
    statistical_arbitrage_strategies: bool = Field(..., description="Whether statistical arbitrage strategies are included")
    options_trading_strategies: bool = Field(..., description="Whether options trading strategies are included")


class CreateHiringStrategyOutput(BaseModel):
    """Pydantic model for create_hiring_strategy node outputs."""
    role_requirements: List[str] = Field(..., description="List of role requirements for quantitative researchers, software engineers, and traders")
    compensation_structure: str = Field(..., description="Description of compensation structure for key roles")
    recruitment_approach: str = Field(..., description="Description of recruitment approach for key roles")
    target_hiring_numbers: List[int] = Field(..., description="List of target hiring numbers for key roles")


def create_hiring_strategy(specify_technology_architecture_input: SpecifyTechnologyArchitectureOutput, design_trading_strategies_input: DesignTradingStrategiesOutput, **kwargs) -> CreateHiringStrategyOutput:
    """Plan talent acquisition for key roles

    Args:
        specify_technology_architecture_input: Input from the 'specify_technology_architecture' node.
        design_trading_strategies_input: Input from the 'design_trading_strategies' node.
        **kwargs: Additional keyword arguments.

    Returns:
        CreateHiringStrategyOutput: Object containing outputs for this node.
    """
    # Analyze technology stack to determine skill requirements
    tech_skill_requirements: List[str] = analyze_technology_skill_requirements(
        trading_systems=specify_technology_architecture_input.trading_systems,
        data_feeds=specify_technology_architecture_input.data_feeds,
        risk_management_systems=specify_technology_architecture_input.risk_management_systems,
        connectivity_requirements=specify_technology_architecture_input.connectivity_requirements
    )
    
    # Analyze trading strategies to determine role requirements
    strategy_skill_requirements: List[str] = analyze_strategy_skill_requirements(
        strategy_count=design_trading_strategies_input.trading_strategy_count,
        strategy_names=design_trading_strategies_input.strategy_names,
        has_market_making=design_trading_strategies_input.market_maker_strategies,
        has_statistical_arbitrage=design_trading_strategies_input.statistical_arbitrage_strategies,
        has_options_trading=design_trading_strategies_input.options_trading_strategies
    )
    
    # Combine requirements from both inputs
    combined_requirements: List[str] = combine_role_requirements(
        tech_requirements=tech_skill_requirements,
        strategy_requirements=strategy_skill_requirements
    )
    
    # Design compensation structure based on roles and market standards
    compensation_plan: str = design_compensation_structure(
        role_requirements=combined_requirements,
        market_data=get_market_compensation_data()
    )
    
    # Create recruitment approach strategy
    recruitment_strategy: str = create_recruitment_approach(
        role_requirements=combined_requirements,
        compensation_structure=compensation_plan
    )
    
    # Calculate target hiring numbers based on strategy complexity and technology needs
    hiring_targets: List[int] = calculate_hiring_targets(
        strategy_count=design_trading_strategies_input.trading_strategy_count,
        technology_complexity=len(specify_technology_architecture_input.trading_systems),
        role_requirements=combined_requirements
    )
    
    return CreateHiringStrategyOutput(
        role_requirements=combined_requirements,
        compensation_structure=compensation_plan,
        recruitment_approach=recruitment_strategy,
        target_hiring_numbers=hiring_targets
    )