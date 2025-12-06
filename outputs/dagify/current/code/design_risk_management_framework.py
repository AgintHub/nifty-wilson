from ._design_risk_management_framework.analyze_trading_strategies import analyze_trading_strategies
from ._design_risk_management_framework.calculate_position_size_limits import calculate_position_size_limits
from ._design_risk_management_framework.determine_concentration_metrics import determine_concentration_metrics
from ._design_risk_management_framework.calculate_var_limits import calculate_var_limits
from ._design_risk_management_framework.establish_drawdown_limits import establish_drawdown_limits
from ._design_risk_management_framework.define_pre_trade_risk_measures import define_pre_trade_risk_measures
from ._design_risk_management_framework.define_post_trade_risk_measures import define_post_trade_risk_measures

from pydantic import BaseModel, Field


class DesignTradingStrategiesOutput(BaseModel):
    """Pydantic model for design_trading_strategies node outputs."""
    trading_strategy_count: int = Field(..., description="Number of trading strategies developed")
    strategy_names: str = Field(..., description="List of trading strategy names")
    market_maker_strategies: bool = Field(..., description="Whether market making strategies are included")
    statistical_arbitrage_strategies: bool = Field(..., description="Whether statistical arbitrage strategies are included")
    options_trading_strategies: bool = Field(..., description="Whether options trading strategies are included")


class DesignRiskManagementFrameworkOutput(BaseModel):
    """Pydantic model for design_risk_management_framework node outputs."""
    position_size_limits: int = Field(..., description="List of position size limits by asset type")
    portfolio_concentration_metrics: float = Field(..., description="List of portfolio concentration metrics")
    var_limit: float = Field(..., description="Value-at-Risk (VaR) limit")
    drawdown_limit: float = Field(..., description="Drawdown limit")
    pre_trade_risk_measures: str = Field(..., description="List of pre-trade risk measures")
    post_trade_risk_measures: str = Field(..., description="List of post-trade risk measures")


def design_risk_management_framework(design_trading_strategies_input: DesignTradingStrategiesOutput, **kwargs) -> DesignRiskManagementFrameworkOutput:
    """Establish comprehensive risk controls and limits

    Args:
        design_trading_strategies_input: Input from the 'design_trading_strategies' node.
        **kwargs: Additional keyword arguments.

    Returns:
        DesignRiskManagementFrameworkOutput: Object containing outputs for this node.
    """
    # Analyze trading strategies to determine appropriate risk controls
    strategy_analysis: dict = analyze_trading_strategies(
        strategy_count=design_trading_strategies_input.trading_strategy_count,
        strategy_names=design_trading_strategies_input.strategy_names,
        has_market_maker=design_trading_strategies_input.market_maker_strategies,
        has_stat_arb=design_trading_strategies_input.statistical_arbitrage_strategies,
        has_options=design_trading_strategies_input.options_trading_strategies
    )
    
    # Calculate position size limits based on strategy types
    position_limits: int = calculate_position_size_limits(
        strategy_analysis=strategy_analysis,
        strategy_types={
            'market_maker': design_trading_strategies_input.market_maker_strategies,
            'stat_arb': design_trading_strategies_input.statistical_arbitrage_strategies,
            'options': design_trading_strategies_input.options_trading_strategies
        }
    )
    
    # Determine portfolio concentration metrics
    concentration_metrics: float = determine_concentration_metrics(
        strategy_count=design_trading_strategies_input.trading_strategy_count,
        strategy_diversity=strategy_analysis
    )
    
    # Set VaR limits based on strategy risk profiles
    var_limit_value: float = calculate_var_limits(
        strategy_analysis=strategy_analysis,
        portfolio_metrics=concentration_metrics
    )
    
    # Establish drawdown limits
    drawdown_limit_value: float = establish_drawdown_limits(
        strategy_types=strategy_analysis,
        var_limit=var_limit_value
    )
    
    # Define pre-trade risk measures
    pre_trade_measures: str = define_pre_trade_risk_measures(
        strategy_analysis=strategy_analysis,
        position_limits=position_limits
    )
    
    # Define post-trade risk measures
    post_trade_measures: str = define_post_trade_risk_measures(
        strategy_analysis=strategy_analysis,
        var_limit=var_limit_value,
        drawdown_limit=drawdown_limit_value
    )
    
    return DesignRiskManagementFrameworkOutput(
        position_size_limits=position_limits,
        portfolio_concentration_metrics=concentration_metrics,
        var_limit=var_limit_value,
        drawdown_limit=drawdown_limit_value,
        pre_trade_risk_measures=pre_trade_measures,
        post_trade_risk_measures=post_trade_measures,
    )