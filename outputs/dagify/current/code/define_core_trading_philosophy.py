from ._define_core_trading_philosophy.analyze_market_context import analyze_market_context
from ._define_core_trading_philosophy.establish_risk_management_framework import establish_risk_management_framework
from ._define_core_trading_philosophy.define_analytical_approach import define_analytical_approach
from ._define_core_trading_philosophy.establish_execution_philosophy import establish_execution_philosophy
from ._define_core_trading_philosophy.synthesize_trading_philosophy import synthesize_trading_philosophy
from ._define_core_trading_philosophy.validate_philosophy_coherence import validate_philosophy_coherence

from pydantic import BaseModel, Field
from typing import List


class DefineCoreTradingPhilosophyOutput(BaseModel):
    """Pydantic model for define_core_trading_philosophy node outputs."""
    core_trading_philosophy: List[str] = Field(..., description="The core trading philosophy for Jane Street")


def define_core_trading_philosophy(general_input: str, **kwargs) -> DefineCoreTradingPhilosophyOutput:
    """Establish fundamental principles for quantitative trading approach

    Args:
        general_input: General input string for the root node.
        **kwargs: Additional keyword arguments.

    Returns:
        DefineCoreTradingPhilosophyOutput: Object containing outputs for this node.
    """
    # Extract key trading principles from input context
    market_context: dict = analyze_market_context(input_data=general_input)
    
    # Define fundamental quantitative trading principles
    risk_management_principles: List[str] = establish_risk_management_framework(context=market_context)
    
    # Establish data-driven decision making principles
    analytical_principles: List[str] = define_analytical_approach(market_data=market_context)
    
    # Create technology and execution principles
    execution_principles: List[str] = establish_execution_philosophy(trading_context=market_context)
    
    # Combine all philosophy components into coherent framework
    combined_philosophy: List[str] = synthesize_trading_philosophy(
        risk_principles=risk_management_principles,
        analytical_principles=analytical_principles, 
        execution_principles=execution_principles
    )
    
    # Validate and refine the core philosophy
    refined_philosophy: List[str] = validate_philosophy_coherence(philosophy=combined_philosophy)
    
    return DefineCoreTradingPhilosophyOutput(
        core_trading_philosophy=refined_philosophy
    )