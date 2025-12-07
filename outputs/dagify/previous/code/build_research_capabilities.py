from ._build_research_capabilities.analyze_data_infrastructure_requirements import analyze_data_infrastructure_requirements
from ._build_research_capabilities.build_research_infrastructure_description import build_research_infrastructure_description
from ._build_research_capabilities.select_research_tools import select_research_tools
from ._build_research_capabilities.select_data_analysis_frameworks import select_data_analysis_frameworks
from ._build_research_capabilities.define_strategy_evaluation_criteria import define_strategy_evaluation_criteria
from ._build_research_capabilities.calculate_research_capital_requirements import calculate_research_capital_requirements

from pydantic import BaseModel, Field
from typing import List


# -- PRD --
# 1. BULLET: Identify the research infrastructure requirements based on the data
#   infrastructure design and trading strategy needs.
#   Reason: This will ensure that the research infrastructure meets the needs of the
#           trading strategies and can support the required research
#           activities.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Review the output of the design_data_infrastructure node and identify the
#           key components required for the research infrastructure. Use
#           this information to select the appropriate research tools and
#           data analysis frameworks.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Develop a list of research tools and data analysis frameworks to support the
#   research activities.
#   Reason: This will ensure that the necessary tools and frameworks are available to
#           support the research activities.
#   Impact: LOW
#   Complexity: LOW
#   Method: Conduct research to identify the most suitable research tools and data
#           analysis frameworks for the research activities. Use this
#           information to compile a list of the selected tools and
#           frameworks.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Define the strategy evaluation criteria based on the research infrastructure
#   and trading strategy needs.
#   Reason: This will ensure that the strategy evaluation criteria are consistent with
#           the research infrastructure and can support the evaluation of
#           the trading strategies.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Review the output of the research_infrastructure node and identify the key
#           components that are relevant to the trading strategies. Use
#           this information to develop a list of strategy evaluation
#           criteria.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Determine the research capital requirements based on the research
#   infrastructure and trading strategy needs.
#   Reason: This will ensure that the research capital requirements are consistent with
#           the research infrastructure and can support the research
#           activities.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Review the output of the research_infrastructure node and identify the key
#           components that are relevant to the research activities. Use
#           this information to estimate the research capital requirements.
# -- END PRD --



class DesignDataInfrastructureOutput(BaseModel):
    """Pydantic model for design_data_infrastructure node outputs."""
    data_infrastructure_design: str = Field(..., description="Detailed description of the data infrastructure design")
    market_data_feeds: str = Field(..., description="List of real-time market data feeds")
    historical_data_storage: str = Field(..., description="Description of the historical data storage system")
    alternative_data_sources: str = Field(..., description="List of alternative data sources considered")
    data_processing_pipelines: str = Field(..., description="Description of the data processing pipelines")
    research_data_systems: str = Field(..., description="Description of the research data systems")
    technology_requirements: str = Field(..., description="List of technology requirements for the data infrastructure")


class CreateHiringStrategyOutput(BaseModel):
    """Pydantic model for create_hiring_strategy node outputs."""
    role_requirements: List[str] = Field(..., description="List of role requirements for quantitative researchers, software engineers, and traders")
    compensation_structure: str = Field(..., description="Description of compensation structure for key roles")
    recruitment_approach: str = Field(..., description="Description of recruitment approach for key roles")
    target_hiring_numbers: List[int] = Field(..., description="List of target hiring numbers for key roles")


class BuildResearchCapabilitiesOutput(BaseModel):
    """Pydantic model for build_research_capabilities node outputs."""
    research_infrastructure: str = Field(..., description="Description of the research infrastructure")
    research_tools: List[str] = Field(..., description="List of research tools used")
    data_analysis_frameworks: List[str] = Field(..., description="List of data analysis frameworks used")
    strategy_evaluation_criteria: List[str] = Field(..., description="List of strategy evaluation criteria")
    research_capital_requirements: List[float] = Field(..., description="List of research capital requirements")


def build_research_capabilities(design_data_infrastructure_input: DesignDataInfrastructureOutput, create_hiring_strategy_input: CreateHiringStrategyOutput, **kwargs) -> BuildResearchCapabilitiesOutput:
    """Establish quantitative research and strategy development processes

    Args:
        design_data_infrastructure_input: Input from the 'design_data_infrastructure' node.
        create_hiring_strategy_input: Input from the 'create_hiring_strategy' node.
        **kwargs: Additional keyword arguments.

    Returns:
        BuildResearchCapabilitiesOutput: Object containing outputs for this node.
    """
    # Identify research infrastructure requirements based on data infrastructure design
    infrastructure_requirements: List[str] = analyze_data_infrastructure_requirements(
        data_infrastructure_design=design_data_infrastructure_input.data_infrastructure_design,
        technology_requirements=design_data_infrastructure_input.technology_requirements,
        research_data_systems=design_data_infrastructure_input.research_data_systems
    )
    
    # Build research infrastructure description from requirements
    research_infrastructure_desc: str = build_research_infrastructure_description(
        requirements=infrastructure_requirements,
        role_requirements=create_hiring_strategy_input.role_requirements
    )
    
    # Develop list of research tools and data analysis frameworks
    selected_research_tools: List[str] = select_research_tools(
        infrastructure_requirements=infrastructure_requirements,
        data_processing_pipelines=design_data_infrastructure_input.data_processing_pipelines
    )
    
    selected_frameworks: List[str] = select_data_analysis_frameworks(
        infrastructure_requirements=infrastructure_requirements,
        alternative_data_sources=design_data_infrastructure_input.alternative_data_sources
    )
    
    # Define strategy evaluation criteria based on research infrastructure
    evaluation_criteria: List[str] = define_strategy_evaluation_criteria(
        research_infrastructure=research_infrastructure_desc,
        research_tools=selected_research_tools,
        data_analysis_frameworks=selected_frameworks
    )
    
    # Determine research capital requirements
    capital_requirements: List[float] = calculate_research_capital_requirements(
        research_infrastructure=research_infrastructure_desc,
        research_tools=selected_research_tools,
        target_hiring_numbers=create_hiring_strategy_input.target_hiring_numbers,
        compensation_structure=create_hiring_strategy_input.compensation_structure
    )
    
    return BuildResearchCapabilitiesOutput(
        research_infrastructure=research_infrastructure_desc,
        research_tools=selected_research_tools,
        data_analysis_frameworks=selected_frameworks,
        strategy_evaluation_criteria=evaluation_criteria,
        research_capital_requirements=capital_requirements
    )