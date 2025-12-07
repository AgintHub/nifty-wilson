from ._create_launch_timeline.analyze_research_setup_timeline import analyze_research_setup_timeline
from ._create_launch_timeline.analyze_operational_setup_timeline import analyze_operational_setup_timeline
from ._create_launch_timeline.identify_resource_dependencies import identify_resource_dependencies
from ._create_launch_timeline.create_phased_implementation_plan import create_phased_implementation_plan
from ._create_launch_timeline.analyze_critical_path import analyze_critical_path
from ._create_launch_timeline.format_dependencies_list import format_dependencies_list

from pydantic import BaseModel, Field
from typing import List


class BuildResearchCapabilitiesOutput(BaseModel):
    """Pydantic model for build_research_capabilities node outputs."""
    research_infrastructure: str = Field(..., description="Description of the research infrastructure")
    research_tools: List[str] = Field(..., description="List of research tools used")
    data_analysis_frameworks: List[str] = Field(..., description="List of data analysis frameworks used")
    strategy_evaluation_criteria: List[str] = Field(..., description="List of strategy evaluation criteria")
    research_capital_requirements: List[float] = Field(..., description="List of research capital requirements")


class DesignPerformanceMeasurementOutput(BaseModel):
    """Pydantic model for design_performance_measurement node outputs."""
    trade_settlement_process: str = Field(..., description="Description of the trade settlement process")
    pl_calculation_method: str = Field(..., description="Method used for calculating P&L")
    risk_monitoring_frequency: str = Field(..., description="Frequency of risk monitoring")
    position_reconciliation_procedure: str = Field(..., description="Procedure for position reconciliation")
    regulatory_reporting_schedule: str = Field(..., description="Schedule for regulatory reporting")
    roles_and_responsibilities: str = Field(..., description="List of roles and responsibilities for operational workflows")


class CreateLaunchTimelineOutput(BaseModel):
    """Pydantic model for create_launch_timeline node outputs."""
    launch_timeline: str = Field(..., description="The 12-month launch timeline with specific milestones")
    dependencies: str = Field(..., description="List of dependencies for the launch timeline")
    critical_path: str = Field(..., description="List of critical paths for the launch timeline")


def create_launch_timeline(build_research_capabilities_input: BuildResearchCapabilitiesOutput, design_performance_measurement_input: DesignPerformanceMeasurementOutput, **kwargs) -> CreateLaunchTimelineOutput:
    """Develop phased implementation plan with milestones

    Args:
        build_research_capabilities_input: Input from the 'build_research_capabilities' node.
        design_performance_measurement_input: Input from the 'design_performance_measurement' node.
        **kwargs: Additional keyword arguments.

    Returns:
        CreateLaunchTimelineOutput: Object containing outputs for this node.
    """
    # Analyze research infrastructure requirements and timeline
    research_timeline: str = analyze_research_setup_timeline(
        infrastructure=build_research_capabilities_input.research_infrastructure,
        tools=build_research_capabilities_input.research_tools,
        frameworks=build_research_capabilities_input.data_analysis_frameworks
    )
    
    # Analyze operational setup requirements and timeline
    operational_timeline: str = analyze_operational_setup_timeline(
        settlement_process=design_performance_measurement_input.trade_settlement_process,
        pl_method=design_performance_measurement_input.pl_calculation_method,
        risk_monitoring=design_performance_measurement_input.risk_monitoring_frequency,
        reporting_schedule=design_performance_measurement_input.regulatory_reporting_schedule
    )
    
    # Identify capital and resource dependencies
    resource_dependencies: List[str] = identify_resource_dependencies(
        capital_requirements=build_research_capabilities_input.research_capital_requirements,
        roles=design_performance_measurement_input.roles_and_responsibilities
    )
    
    # Create integrated 12-month timeline with milestones
    integrated_timeline: str = create_phased_implementation_plan(
        research_timeline=research_timeline,
        operational_timeline=operational_timeline,
        evaluation_criteria=build_research_capabilities_input.strategy_evaluation_criteria
    )
    
    # Determine critical path and dependencies
    critical_path_analysis: str = analyze_critical_path(
        timeline=integrated_timeline,
        dependencies=resource_dependencies
    )
    
    # Format dependencies for output
    formatted_dependencies: str = format_dependencies_list(
        dependencies=resource_dependencies,
        reconciliation_procedure=design_performance_measurement_input.position_reconciliation_procedure
    )
    
    return CreateLaunchTimelineOutput(
        launch_timeline=integrated_timeline,
        dependencies=formatted_dependencies,
        critical_path=critical_path_analysis
    )