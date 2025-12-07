from ._compile_business_plan.parse_launch_timeline import parse_launch_timeline
from ._compile_business_plan.analyze_dependencies import analyze_dependencies
from ._compile_business_plan.analyze_critical_path import analyze_critical_path
from ._compile_business_plan.generate_executive_summary import generate_executive_summary
from ._compile_business_plan.compile_market_opportunity import compile_market_opportunity
from ._compile_business_plan.generate_competitive_advantage import generate_competitive_advantage
from ._compile_business_plan.create_financial_projections import create_financial_projections
from ._compile_business_plan.build_implementation_roadmap import build_implementation_roadmap
from ._compile_business_plan.calculate_total_words import calculate_total_words

from pydantic import BaseModel, Field


class CreateLaunchTimelineOutput(BaseModel):
    """Pydantic model for create_launch_timeline node outputs."""
    launch_timeline: str = Field(..., description="The 12-month launch timeline with specific milestones")
    dependencies: str = Field(..., description="List of dependencies for the launch timeline")
    critical_path: str = Field(..., description="List of critical paths for the launch timeline")


class CompileBusinessPlanOutput(BaseModel):
    """Pydantic model for compile_business_plan node outputs."""
    executive_summary: str = Field(..., description="Summary of the business plan")
    market_opportunity: str = Field(..., description="Summary of the market opportunity")
    competitive_advantage: str = Field(..., description="Summary of the competitive advantage")
    financial_projections: str = Field(..., description="Summary of the financial projections")
    implementation_roadmap: str = Field(..., description="Summary of the implementation roadmap")
    total_words: int = Field(..., description="Total number of words in the business plan")


def compile_business_plan(create_launch_timeline_input: CreateLaunchTimelineOutput, **kwargs) -> CompileBusinessPlanOutput:
    """Synthesize all elements into comprehensive business plan

    Args:
        create_launch_timeline_input: Input from the 'create_launch_timeline' node.
        **kwargs: Additional keyword arguments.

    Returns:
        CompileBusinessPlanOutput: Object containing outputs for this node.
    """
    # Extract timeline data and dependencies
    timeline_data: dict = parse_launch_timeline(timeline=create_launch_timeline_input.launch_timeline)
    dependency_analysis: dict = analyze_dependencies(dependencies=create_launch_timeline_input.dependencies)
    critical_path_analysis: dict = analyze_critical_path(critical_path=create_launch_timeline_input.critical_path)
    
    # Generate executive summary
    executive_summary: str = generate_executive_summary(
        timeline_data=timeline_data,
        dependencies=dependency_analysis,
        critical_path=critical_path_analysis
    )
    
    # Compile market opportunity section
    market_opportunity: str = compile_market_opportunity(
        timeline_milestones=timeline_data,
        additional_context=kwargs
    )
    
    # Generate competitive advantage section
    competitive_advantage: str = generate_competitive_advantage(
        implementation_timeline=timeline_data,
        dependencies=dependency_analysis
    )
    
    # Create financial projections
    financial_projections: str = create_financial_projections(
        timeline=timeline_data,
        critical_path=critical_path_analysis,
        dependencies=dependency_analysis
    )
    
    # Build implementation roadmap
    implementation_roadmap: str = build_implementation_roadmap(
        launch_timeline=create_launch_timeline_input.launch_timeline,
        dependencies=create_launch_timeline_input.dependencies,
        critical_path=create_launch_timeline_input.critical_path
    )
    
    # Calculate total word count
    total_words: int = calculate_total_words(
        sections=[
            executive_summary,
            market_opportunity,
            competitive_advantage,
            financial_projections,
            implementation_roadmap
        ]
    )
    
    return CompileBusinessPlanOutput(
        executive_summary=executive_summary,
        market_opportunity=market_opportunity,
        competitive_advantage=competitive_advantage,
        financial_projections=financial_projections,
        implementation_roadmap=implementation_roadmap,
        total_words=total_words,
    )