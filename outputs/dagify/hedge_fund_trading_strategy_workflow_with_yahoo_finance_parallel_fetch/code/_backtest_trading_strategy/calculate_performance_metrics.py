# -- PRD --
# 1. BULLET: Parse the incoming `equity_curve` string into a pandas Series of daily
#   portfolio values.
#   Reason: The shim receives the equity curve as a serialized string; converting it to
#           a numeric series is required for calculations.
#   Impact: Enables downstream vectorized operations for return, drawdown, and Sharpe
#           calculations.
#   Complexity: LOW
#   Method: Use `json.loads` or `ast.literal_eval` to convert the string to a list,
#           then create a `pd.Series` with a datetime index inferred from
#           the data.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Calculate total return, annualized Sharpe ratio (risk‑free rate = 0), maximum
#   drawdown, and the back‑test period start/end dates.
#   Reason: These metrics are the core performance indicators needed by the
#           `BacktestTradingStrategyOutput` model.
#   Impact: Provides the quantitative summary that downstream nodes and users rely on
#           for strategy evaluation.
#   Complexity: MEDIUM
#   Method: Compute daily returns via `pct_change()`, aggregate to total return, use
#           `np.mean` and `np.std` on annualized returns for Sharpe, derive
#           drawdown with a running max, and extract first/last dates from
#           the Series index.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Assemble the computed values and the parsed `number_of_trades` into a
#   JSON‑compatible dictionary and serialize it to a string for the `output`
#   field.
#   Reason: The shim contract expects a string representation of a dict, matching the
#           declared output type.
#   Impact: Ensures downstream Pydantic validation succeeds and the back‑test node can
#           unpack the metrics reliably.
#   Complexity: LOW
#   Method: Create a Python dict with keys `total_return`, `annualized_sharpe`,
#           `max_drawdown`, `period_start`, `period_end`,
#           `number_of_trades`; then `json.dumps` the dict to produce the
#           `output` string.
# -- END PRD --


def calculate_performance_metrics(equity_curve: str, number_of_trades: str) -> str:
    """
    Computes a dictionary of key back‑test performance metrics from a provided equity curve series and trade count.

    Args:
        equity_curve: Input parameter of type str
number_of_trades: Input parameter of type str

    Returns:
        str: Output of type dict
    """
    raise NotImplementedError("This is a virtual stub node that needs to be implemented")
