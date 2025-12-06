from ._design_data_infrastructure.design_comprehensive_data_architecture import design_comprehensive_data_architecture
from ._design_data_infrastructure.plan_realtime_market_data_feeds import plan_realtime_market_data_feeds
from ._design_data_infrastructure.design_historical_data_storage import design_historical_data_storage
from ._design_data_infrastructure.identify_alternative_data_sources import identify_alternative_data_sources
from ._design_data_infrastructure.design_data_processing_pipelines import design_data_processing_pipelines
from ._design_data_infrastructure.design_research_data_systems import design_research_data_systems
from ._design_data_infrastructure.determine_technology_requirements import determine_technology_requirements

from pydantic import BaseModel, Field
from typing import List


class SpecifyTechnologyArchitectureOutput(BaseModel):
    """Pydantic model for specify_technology_architecture node outputs."""
    trading_systems: List[str] = Field(..., description="List of low-latency trading systems used")
    data_feeds: List[str] = Field(..., description="List of data feeds used for trading")
    risk_management_systems: List[str] = Field(..., description="List of risk management systems used for trading")
    connectivity_requirements: str = Field(..., description="Description of connectivity requirements for trading")


class DesignDataInfrastructureOutput(BaseModel):
    """Pydantic model for design_data_infrastructure node outputs."""
    data_infrastructure_design: str = Field(..., description="Detailed description of the data infrastructure design")
    market_data_feeds: str = Field(..., description="List of real-time market data feeds")
    historical_data_storage: str = Field(..., description="Description of the historical data storage system")
    alternative_data_sources: str = Field(..., description="List of alternative data sources considered")
    data_processing_pipelines: str = Field(..., description="Description of the data processing pipelines")
    research_data_systems: str = Field(..., description="Description of the research data systems")
    technology_requirements: str = Field(..., description="List of technology requirements for the data infrastructure")


def design_data_infrastructure(specify_technology_architecture_input: SpecifyTechnologyArchitectureOutput, **kwargs) -> DesignDataInfrastructureOutput:
    """Plan market data and research data systems

    Args:
        specify_technology_architecture_input: Input from the 'specify_technology_architecture' node.
        **kwargs: Additional keyword arguments.

    Returns:
        DesignDataInfrastructureOutput: Object containing outputs for this node.
    """
    # Extract trading systems and data requirements from architecture input
    trading_systems: List[str] = specify_technology_architecture_input.trading_systems
    existing_data_feeds: List[str] = specify_technology_architecture_input.data_feeds
    connectivity_reqs: str = specify_technology_architecture_input.connectivity_requirements
    
    # Design comprehensive data infrastructure based on trading requirements
    infrastructure_design: str = design_comprehensive_data_architecture(
        trading_systems=trading_systems,
        connectivity_requirements=connectivity_reqs
    )
    
    # Plan real-time market data feeds for trading systems
    market_feeds: str = plan_realtime_market_data_feeds(
        existing_feeds=existing_data_feeds,
        trading_systems=trading_systems
    )
    
    # Design historical data storage system for backtesting and analysis
    historical_storage: str = design_historical_data_storage(
        data_feeds=existing_data_feeds,
        performance_requirements=connectivity_reqs
    )
    
    # Identify alternative data sources for enhanced trading strategies
    alt_data_sources: str = identify_alternative_data_sources(
        trading_systems=trading_systems
    )
    
    # Design data processing pipelines for real-time and batch processing
    processing_pipelines: str = design_data_processing_pipelines(
        market_feeds=market_feeds,
        alternative_sources=alt_data_sources
    )
    
    # Plan research data systems for strategy development
    research_systems: str = design_research_data_systems(
        historical_storage=historical_storage,
        alternative_data=alt_data_sources
    )
    
    # Determine technology requirements for the complete data infrastructure
    tech_requirements: str = determine_technology_requirements(
        infrastructure_design=infrastructure_design,
        processing_pipelines=processing_pipelines,
        connectivity_requirements=connectivity_reqs
    )
    
    return DesignDataInfrastructureOutput(
        data_infrastructure_design=infrastructure_design,
        market_data_feeds=market_feeds,
        historical_data_storage=historical_storage,
        alternative_data_sources=alt_data_sources,
        data_processing_pipelines=processing_pipelines,
        research_data_systems=research_systems,
        technology_requirements=tech_requirements
    )