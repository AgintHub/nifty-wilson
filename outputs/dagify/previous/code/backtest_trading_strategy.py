# -- PRD --
# 1. BULLET: Parse the CSV strings from **fetch_stock_data_yahoo_data** into pandas
#   DataFrames, enforce UTC DatetimeIndex, and ensure columns are exactly
#   ['Open','High','Low','Close','Adj Close','Volume'].
#   Reason: Standardizing data format guarantees downstream calculations operate on a
#           consistent schema and eliminates hidden timezone bugs.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Use pandas.read_csv with StringIO, set parse_dates=True,
#           date_parser=pd.to_datetime, tz='UTC'; validate column order
#           with assert statements.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Create a master business‑day calendar covering the intersection of all ticker
#   date ranges; reindex each ticker DataFrame onto this calendar,
#   forward‑fill missing values, and drop leading rows with any NaN after
#   alignment.
#   Reason: Aligning on a common index is essential for accurate signal evaluation and
#           portfolio aggregation across assets.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Determine min(max_start_date) and max(min_end_date) across tickers;
#           generate pandas.bdate_range; for each DataFrame,
#           df.reindex(master_index, method='ffill'); drop rows where any
#           ticker still has NaN using df.dropna(how='any').
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Translate **develop_trading_signal_logic.signal_logic_steps** into an
#   executable Python function that takes a unified DataFrame (rows=dates,
#   columns=multi‑index ticker/field) and returns a DataFrame of position
#   intents (+1 for long, -1 for short, 0 for flat) per ticker per day.
#   Reason: A deterministic, vectorised signal function enables fast daily evaluation
#           and facilitates later backtesting loops.
#   Impact: HIGH
#   Complexity: HIGH
#   Method: Parse the list of textual rules (e.g., "If SMA_20 > SMA_50 then BUY") into
#           pandas boolean masks; combine masks per ticker; store results
#           in a DataFrame called `signals` with same index as price data.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Implement an execution engine that iterates over the chronologically ordered
#   dates, compares current positions to previous day's signals, generates
#   trade orders, applies configurable commission (default 0.001 per trade)
#   and slippage (default 0.0005 price offset), and updates cash and holdings
#   accordingly.
#   Reason: Simulating realistic trading costs and order execution is crucial for
#           credible performance metrics.
#   Impact: HIGH
#   Complexity: HIGH
#   Method: Maintain variables: cash, holdings dict, portfolio_value series; for each
#           date: identify changed signals, compute trade size =
#           (available_capital * allocation_per_asset) / price; subtract
#           commission = trade_size * commission_rate; adjust fill price =
#           price * (1 + slippage * sign); update holdings and cash.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Construct the daily equity curve by summing cash plus market value of all
#   holdings (position * close price) after each day's execution; store
#   results in a pandas Series `equity_curve` indexed by date.
#   Reason: The equity curve is the basis for all downstream performance statistics.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: equity_curve[date] = cash + sum(holdings[ticker] * close_price[ticker] for
#           each ticker).
# 
# -----------------------------------------------------------------------------
# 6. BULLET: Calculate performance metrics: total_return = (final_equity /
#   initial_capital) - 1; daily_returns = equity_curve.pct_change().dropna();
#   annualized_sharpe = sqrt(252) * mean(daily_returns) / std(daily_returns);
#   max_drawdown = max( (peak - trough)/peak ) using a rolling max;
#   number_of_trades = count of executed orders; backtest_period_start/end =
#   first/last date of equity_curve.
#   Reason: These metrics provide a standardized quantification of risk‑adjusted
#           returns and trade activity.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Use numpy and pandas functions: np.sqrt(252), equity_curve.cummax() for
#           drawdown calculation, and simple integer counter for trades.
# 
# -----------------------------------------------------------------------------
# 7. BULLET: Wrap the entire pipeline in a try/except block; on any exception set
#   `success=False`, log the exception message to a dedicated log string, and
#   populate output fields with NaN/zero defaults; otherwise set
#   `success=True`.
#   Reason: Robust error handling ensures the node returns a well‑defined output even
#           when upstream data is malformed.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Use Python's try: ... except Exception as e: success=False;
#           log_message=str(e); assign default values; finally return the
#           output dictionary.
# -- END PRD --

from pydantic import BaseModel, Field
from typing import List


class DevelopTradingSignalLogicOutput(BaseModel):
    """Pydantic model for develop_trading_signal_logic node outputs."""
    signal_logic_steps: List[str] = Field(..., description="Step\u2011by\u2011step outline of the logical rules that convert indicator readings into concrete BUY or SELL signals.")
    used_indicators: List[str] = Field(..., description="Explicit list of technical indicator names (as provided by the parent node) that are employed in the signal generation algorithm.")
    summary: str = Field(..., description="A concise executive summary describing the overall methodology, key decision pathways, and any risk\u2011management overlays.")
    is_logic_complete: bool = Field(..., description="Flag indicating whether the signal logic accounts for all identified indicators and fully defines buy, sell, and neutral decision branches.")


class SpecifyAssetUniverseOutput(BaseModel):
    """Pydantic model for specify_asset_universe node outputs."""
    asset_classes: List[str] = Field(..., description="High\u2011level asset classes or instrument families to be traded (e.g., US equities, futures, commodities).")
    asset_tickers: List[str] = Field(..., description="Specific ticker symbols or contract identifiers selected from each asset class (e.g., AAPL, MSFT, ESZ2025).")


class FetchStockDataYahooDataOutput(BaseModel):
    """Pydantic model for fetch_stock_data_yahoo_data node outputs."""
    tickers: List[str] = Field(..., description="Ordered list of ticker symbols for which historical data was fetched.")
    data_csv: List[str] = Field(..., description="CSV\u2011formatted string of the OHLCV data for each ticker, preserving dates as the index; list order matches `tickers`.")
    record_counts: List[int] = Field(..., description="Number of rows (trading days) retrieved for each ticker, aligned with the order of `tickers`.")


class FetchStockDataYahooStatusOutput(BaseModel):
    """Pydantic model for fetch_stock_data_yahoo_status node outputs."""
    retrieval_success: bool = Field(..., description="Indicates whether the data download from Yahoo Finance completed without errors for all requested tickers.")
    retrieval_message: str = Field(..., description="A concise human\u2011readable confirmation or error summary describing the overall retrieval outcome.")


class BacktestTradingStrategyOutput(BaseModel):
    """Pydantic model for backtest_trading_strategy node outputs."""
    total_return: float = Field(..., description="Cumulative return of the strategy over the backtest period, expressed as a decimal (e.g., 0.12 for 12%).")
    annualized_sharpe_ratio: float = Field(..., description="Annualized Sharpe ratio of the strategy, assuming a risk\u2011free rate of 0%.")
    max_drawdown: float = Field(..., description="Maximum drawdown observed during the backtest, expressed as a decimal.")
    number_of_trades: int = Field(..., description="Total count of executed trades (both entries and exits) throughout the backtest.")
    backtest_period_start: str = Field(..., description="ISO\u2011format start date of the backtest period (YYYY\u2011MM\u2011DD).")
    backtest_period_end: str = Field(..., description="ISO\u2011format end date of the backtest period (YYYY\u2011MM\u2011DD).")
    success: bool = Field(..., description="True if the backtest completed without errors; false otherwise.")


def backtest_trading_strategy(develop_trading_signal_logic_input: DevelopTradingSignalLogicOutput, specify_asset_universe_input: SpecifyAssetUniverseOutput, fetch_stock_data_yahoo_data_input: FetchStockDataYahooDataOutput, fetch_stock_data_yahoo_status_input: FetchStockDataYahooStatusOutput, **kwargs) -> BacktestTradingStrategyOutput:
    """Performs a rigorous, production‑grade backtest of the fully specified trading strategy using the fetched Yahoo Finance data, the asset universe, and the signal generation logic.

    Args:
        develop_trading_signal_logic_input: Input from the 'develop_trading_signal_logic' node.
        specify_asset_universe_input: Input from the 'specify_asset_universe' node.
        fetch_stock_data_yahoo_data_input: Input from the 'fetch_stock_data_yahoo_data' node.
        fetch_stock_data_yahoo_status_input: Input from the 'fetch_stock_data_yahoo_status' node.
        **kwargs: Additional keyword arguments.

    Returns:
        BacktestTradingStrategyOutput: Object containing outputs for this node.
    """
    # TODO: Implement this function

    # Return stub output with placeholder values
    return BacktestTradingStrategyOutput(
        total_return=0.0,
        annualized_sharpe_ratio=0.0,
        max_drawdown=0.0,
        number_of_trades=0,
        backtest_period_start="",
        backtest_period_end="",
        success=False,
    )