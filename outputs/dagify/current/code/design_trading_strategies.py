from ._design_trading_strategies.extract_market_making_principles import extract_market_making_principles
from ._design_trading_strategies.rank_markets_by_strategy_type import rank_markets_by_strategy_type
from ._design_trading_strategies.develop_market_making_strategies import develop_market_making_strategies
from ._design_trading_strategies.develop_statistical_arbitrage_strategies import develop_statistical_arbitrage_strategies
from ._design_trading_strategies.develop_options_trading_strategies import develop_options_trading_strategies
from ._design_trading_strategies.validate_strategies_against_philosophy import validate_strategies_against_philosophy
from ._design_trading_strategies.generate_strategy_names import generate_strategy_names
from ._design_trading_strategies.format_strategy_names_as_string import format_strategy_names_as_string
from ._design_trading_strategies.document_and_store_strategies import document_and_store_strategies

from pydantic import BaseModel, Field
from typing import List


# -- PRD --
# 1. BULLET: Extract relevant market making principles from the core trading philosophy
#   defined in the define_core_trading_philosophy node.
#   Reason: This will help in developing market making strategies aligned with the core
#           philosophy.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Use natural language processing techniques to extract key points from the
#           core trading philosophy document. Then, use the extracted key
#           points to develop market making strategies.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Select the most suitable primary markets and exchanges for each trading
#   strategy based on the market selection reasoning provided by the
#   select_primary_markets node.
#   Reason: This will ensure that each trading strategy is aligned with the selected
#           markets and exchanges.
#   Impact: HIGH
#   Complexity: HIGH
#   Method: Use the market selection reasoning from the select_primary_markets node to
#           rank the primary markets and exchanges for each trading
#           strategy. Then, select the top-ranked markets and exchanges for
#           each strategy.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Develop four to six quantitative trading strategies using the selected
#   primary markets and exchanges, and focus on market making, statistical
#   arbitrage, and options trading approaches.
#   Reason: This will provide a diverse set of trading strategies aligned with the core
#           philosophy and suitable for the selected markets.
#   Impact: HIGH
#   Complexity: HIGH
#   Method: Use programming languages such as Python or C++ to develop the trading
#           strategies. Use quantitative finance libraries such as QuantLib
#           or PyAlgoTrade to implement the strategies. Ensure that each
#           strategy is thoroughly backtested and validated before
#           implementation.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Document and store each developed trading strategy along with its details,
#   such as market making principles, statistical arbitrage approaches, and
#   options trading strategies.
#   Reason: This will facilitate future reference and improvement of the trading
#           strategies.
#   Impact: LOW
#   Complexity: LOW
#   Method: Use a version control system such as Git to store and manage the trading
#           strategy documentation and code. Use a database or data storage
#           system such as MySQL or MongoDB to store the strategy details.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Review and finalize the developed trading strategies to ensure they meet the
#   core philosophy and are aligned with the selected markets and exchanges.
#   Reason: This will ensure that the trading strategies are effective and sustainable.
#   Impact: HIGH
#   Complexity: HIGH
#   Method: Use the core trading philosophy document as a reference to review and
#           finalize each trading strategy. Ensure that each strategy is
#           thoroughly validated and tested before implementation.
# -- END PRD --



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


class DesignTradingStrategiesOutput(BaseModel):
    """Pydantic model for design_trading_strategies node outputs."""
    trading_strategy_count: int = Field(..., description="Number of trading strategies developed")
    strategy_names: str = Field(..., description="List of trading strategy names")
    market_maker_strategies: bool = Field(..., description="Whether market making strategies are included")
    statistical_arbitrage_strategies: bool = Field(..., description="Whether statistical arbitrage strategies are included")
    options_trading_strategies: bool = Field(..., description="Whether options trading strategies are included")


def design_trading_strategies(define_core_trading_philosophy_input: DefineCoreTradingPhilosophyOutput, select_primary_markets_input: SelectPrimaryMarketsOutput, **kwargs) -> DesignTradingStrategiesOutput:
    """Develop specific quantitative trading strategies

    Args:
        define_core_trading_philosophy_input: Input from the 'define_core_trading_philosophy' node.
        select_primary_markets_input: Input from the 'select_primary_markets' node.
        **kwargs: Additional keyword arguments.

    Returns:
        DesignTradingStrategiesOutput: Object containing outputs for this node.
    """
    # Extract market making principles from core trading philosophy
    market_making_principles: List[str] = extract_market_making_principles(
        philosophy=define_core_trading_philosophy_input.core_trading_philosophy
    )
    
    # Rank and select markets for each strategy type based on selection reasoning
    market_rankings: dict = rank_markets_by_strategy_type(
        markets=select_primary_markets_input.primary_markets,
        selection_reasoning=select_primary_markets_input.market_selection_reasoning,
        liquidity_assessment=select_primary_markets_input.liquidity_risk_assessment
    )
    
    # Develop market making strategies
    market_maker_strategies: List[dict] = develop_market_making_strategies(
        principles=market_making_principles,
        selected_markets=market_rankings.get("market_making", []),
        regulatory_env=select_primary_markets_input.regulatory_environment
    )
    
    # Develop statistical arbitrage strategies
    stat_arb_strategies: List[dict] = develop_statistical_arbitrage_strategies(
        philosophy=define_core_trading_philosophy_input.core_trading_philosophy,
        selected_markets=market_rankings.get("statistical_arbitrage", []),
        competitive_landscape=select_primary_markets_input.competitive_landscape
    )
    
    # Develop options trading strategies
    options_strategies: List[dict] = develop_options_trading_strategies(
        philosophy=define_core_trading_philosophy_input.core_trading_philosophy,
        selected_markets=market_rankings.get("options_trading", []),
        liquidity_assessment=select_primary_markets_input.liquidity_risk_assessment
    )
    
    # Combine all strategies and validate against core philosophy
    all_strategies: List[dict] = market_maker_strategies + stat_arb_strategies + options_strategies
    validated_strategies: List[dict] = validate_strategies_against_philosophy(
        strategies=all_strategies,
        core_philosophy=define_core_trading_philosophy_input.core_trading_philosophy
    )
    
    # Generate strategy names and documentation
    strategy_names_list: List[str] = generate_strategy_names(strategies=validated_strategies)
    strategy_names_str: str = format_strategy_names_as_string(names=strategy_names_list)
    
    # Document and store strategies
    document_and_store_strategies(
        strategies=validated_strategies,
        documentation_format="comprehensive",
        storage_system="version_controlled"
    )
    
    # Determine strategy counts and types
    total_count: int = len(validated_strategies)
    has_market_maker: bool = len(market_maker_strategies) > 0
    has_stat_arb: bool = len(stat_arb_strategies) > 0
    has_options: bool = len(options_strategies) > 0
    
    return DesignTradingStrategiesOutput(
        trading_strategy_count=total_count,
        strategy_names=strategy_names_str,
        market_maker_strategies=has_market_maker,
        statistical_arbitrage_strategies=has_stat_arb,
        options_trading_strategies=has_options
    )