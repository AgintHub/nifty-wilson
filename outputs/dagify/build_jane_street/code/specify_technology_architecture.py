from ._specify_technology_architecture.analyze_strategy_requirements import analyze_strategy_requirements
from ._specify_technology_architecture.research_low_latency_systems import research_low_latency_systems
from ._specify_technology_architecture.identify_data_feeds import identify_data_feeds
from ._specify_technology_architecture.research_risk_management_systems import research_risk_management_systems
from ._specify_technology_architecture.document_connectivity_requirements import document_connectivity_requirements

from pydantic import BaseModel, Field
from typing import List


# -- PRD --
# 1. BULLET: Gather requirements from design_trading_strategies node
#   Reason: The technology architecture must support the trading strategies developed
#           in design_trading_strategies
#   Impact: HIGH
#   Complexity: HIGH
#   Method: Use the output structure of design_trading_strategies to inform the
#           technology architecture design
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Identify low-latency trading systems
#   Reason: Low-latency trading systems are critical for trading strategy execution
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Research and identify at least 3 low-latency trading systems
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Identify data feeds
#   Reason: Data feeds are essential for trading strategy execution
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Research and identify at least 3 data feeds
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Identify risk management systems
#   Reason: Risk management systems are critical for trading strategy execution
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Research and identify at least 3 risk management systems
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Document connectivity requirements
#   Reason: Connectivity requirements are essential for trading strategy execution
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Document at least 5 connectivity requirements
# -- END PRD --



class DesignTradingStrategiesOutput(BaseModel):
    """Pydantic model for design_trading_strategies node outputs."""
    trading_strategy_count: int = Field(..., description="Number of trading strategies developed")
    strategy_names: str = Field(..., description="List of trading strategy names")
    market_maker_strategies: bool = Field(..., description="Whether market making strategies are included")
    statistical_arbitrage_strategies: bool = Field(..., description="Whether statistical arbitrage strategies are included")
    options_trading_strategies: bool = Field(..., description="Whether options trading strategies are included")


class SpecifyTechnologyArchitectureOutput(BaseModel):
    """Pydantic model for specify_technology_architecture node outputs."""
    trading_systems: List[str] = Field(..., description="List of low-latency trading systems used")
    data_feeds: List[str] = Field(..., description="List of data feeds used for trading")
    risk_management_systems: List[str] = Field(..., description="List of risk management systems used for trading")
    connectivity_requirements: str = Field(..., description="Description of connectivity requirements for trading")


def specify_technology_architecture(design_trading_strategies_input: DesignTradingStrategiesOutput, **kwargs) -> SpecifyTechnologyArchitectureOutput:
    """Define high-level technology infrastructure requirements

    Args:
        design_trading_strategies_input: Input from the 'design_trading_strategies' node.
        **kwargs: Additional keyword arguments.

    Returns:
        SpecifyTechnologyArchitectureOutput: Object containing outputs for this node.
    """
    # Gather requirements from design_trading_strategies node
    strategy_requirements: dict = analyze_strategy_requirements(
        strategy_count=design_trading_strategies_input.trading_strategy_count,
        strategy_names=design_trading_strategies_input.strategy_names,
        has_market_maker=design_trading_strategies_input.market_maker_strategies,
        has_stat_arb=design_trading_strategies_input.statistical_arbitrage_strategies,
        has_options=design_trading_strategies_input.options_trading_strategies
    )
    
    # Identify low-latency trading systems based on strategy requirements
    trading_systems: List[str] = research_low_latency_systems(
        strategy_requirements=strategy_requirements,
        min_systems=3
    )
    
    # Identify appropriate data feeds for the trading strategies
    data_feeds: List[str] = identify_data_feeds(
        strategy_requirements=strategy_requirements,
        min_feeds=3
    )
    
    # Identify risk management systems suitable for the strategies
    risk_systems: List[str] = research_risk_management_systems(
        strategy_requirements=strategy_requirements,
        min_systems=3
    )
    
    # Document connectivity requirements
    connectivity_docs: str = document_connectivity_requirements(
        trading_systems=trading_systems,
        data_feeds=data_feeds,
        risk_systems=risk_systems,
        min_requirements=5
    )
    
    return SpecifyTechnologyArchitectureOutput(
        trading_systems=trading_systems,
        data_feeds=data_feeds,
        risk_management_systems=risk_systems,
        connectivity_requirements=connectivity_docs
    )