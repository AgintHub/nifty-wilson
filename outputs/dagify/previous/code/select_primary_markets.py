from ._select_primary_markets.analyze_trading_philosophy import analyze_trading_philosophy
from ._select_primary_markets.research_candidate_markets import research_candidate_markets
from ._select_primary_markets.assess_market_liquidity import assess_market_liquidity
from ._select_primary_markets.analyze_regulatory_environment import analyze_regulatory_environment
from ._select_primary_markets.analyze_competitive_landscape import analyze_competitive_landscape
from ._select_primary_markets.score_markets import score_markets
from ._select_primary_markets.select_top_markets import select_top_markets
from ._select_primary_markets.generate_market_selection_reasoning import generate_market_selection_reasoning
from ._select_primary_markets.compile_liquidity_risk_assessment import compile_liquidity_risk_assessment
from ._select_primary_markets.summarize_regulatory_environment import summarize_regulatory_environment
from ._select_primary_markets.summarize_competitive_landscape import summarize_competitive_landscape

from pydantic import BaseModel, Field
from typing import List


class DefineCoreTradingPhilosophyOutput(BaseModel):
    """Pydantic model for define_core_trading_philosophy node outputs."""
    core_trading_philosophy: List[str] = Field(..., description="The core trading philosophy for Jane Street")


class SelectPrimaryMarketsOutput(BaseModel):
    """Pydantic model for select_primary_markets node outputs."""
    primary_markets: List[str] = Field(..., description="List of selected primary markets and exchanges")
    market_selection_reasoning: str = Field(..., description="Rationale for selecting each primary market and exchange")
    liquidity_risk_assessment: str = Field(..., description="Assessment of liquidity risk in each selected market")
    regulatory_environment: str = Field(..., description="Overview of regulatory requirements and implications for each selected market")
    competitive_landscape: str = Field(..., description="Analysis of competitive landscape in each selected market")


def select_primary_markets(define_core_trading_philosophy_input: DefineCoreTradingPhilosophyOutput, **kwargs) -> SelectPrimaryMarketsOutput:
    """Identify initial markets and exchanges for trading operations

    Args:
        define_core_trading_philosophy_input: Input from the 'define_core_trading_philosophy' node.
        **kwargs: Additional keyword arguments.

    Returns:
        SelectPrimaryMarketsOutput: Object containing outputs for this node.
    """
    # Analyze core trading philosophy to determine market alignment
    philosophy_analysis: dict = analyze_trading_philosophy(philosophy=define_core_trading_philosophy_input.core_trading_philosophy)
    
    # Research and identify potential markets based on philosophy alignment
    candidate_markets: List[str] = research_candidate_markets(philosophy_requirements=philosophy_analysis)
    
    # Evaluate liquidity characteristics of each candidate market
    liquidity_data: dict = assess_market_liquidity(markets=candidate_markets)
    
    # Analyze regulatory environment for each market
    regulatory_analysis: dict = analyze_regulatory_environment(markets=candidate_markets)
    
    # Evaluate competitive landscape in each market
    competition_analysis: dict = analyze_competitive_landscape(markets=candidate_markets)
    
    # Score and rank markets based on all criteria
    market_scores: dict = score_markets(liquidity=liquidity_data, regulation=regulatory_analysis, competition=competition_analysis, philosophy=philosophy_analysis)
    
    # Select top markets based on scoring
    selected_markets: List[str] = select_top_markets(market_scores=market_scores, max_markets=5)
    
    # Generate comprehensive reasoning for market selection
    selection_reasoning: str = generate_market_selection_reasoning(selected_markets=selected_markets, scores=market_scores)
    
    # Compile liquidity risk assessment for selected markets
    liquidity_assessment: str = compile_liquidity_risk_assessment(markets=selected_markets, liquidity_data=liquidity_data)
    
    # Summarize regulatory environment for selected markets
    regulatory_summary: str = summarize_regulatory_environment(markets=selected_markets, regulatory_data=regulatory_analysis)
    
    # Summarize competitive landscape for selected markets
    competitive_summary: str = summarize_competitive_landscape(markets=selected_markets, competition_data=competition_analysis)
    
    return SelectPrimaryMarketsOutput(
        primary_markets=selected_markets,
        market_selection_reasoning=selection_reasoning,
        liquidity_risk_assessment=liquidity_assessment,
        regulatory_environment=regulatory_summary,
        competitive_landscape=competitive_summary
    )