# -- PRD --
# 1. BULLET: Implement syntactic validation of each ticker using a regular expression that
#   enforces allowed characters and length limits.
#   Reason: Ensures only plausibly correct ticker symbols proceed to the external
#           lookup, reducing unnecessary API calls.
#   Impact: Filters out obviously malformed tickers early, improving performance and
#           lowering request volume to Yahoo Finance.
#   Complexity: LOW
#   Method: Define a regex pattern (e.g., `^[A-Z]{1,5}(\.[A-Z]{1,2})?$`) and apply it
#           to each ticker after stripping whitespace.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Verify each syntactically valid ticker against Yahoo Finance using the
#   `yfinance` library (or a direct HTTP request to the Yahoo Finance API)
#   and keep only those that return a non‑empty info dict.
#   Reason: Only tickers that exist on Yahoo Finance can be used downstream for price
#           retrieval and analysis.
#   Impact: Produces a reliable list of tradable symbols, preventing downstream
#           failures when fetching market data.
#   Complexity: MEDIUM
#   Method: Iterate over the filtered tickers, instantiate `yfinance.Ticker(ticker)`,
#           call `.info` or `.history(period="1d")`, and treat a successful
#           response as validation; handle rate‑limiting with exponential
#           back‑off and cache results for repeated symbols.
# -- END PRD --

from typing import List


def validate_tickers_yahoo_finance(candidate_tickers: str) -> List[str]:
    """
    Validates a list of ticker symbols for correct syntax and confirms their existence on Yahoo Finance, returning only the verified tickers.

    Args:
        candidate_tickers: Input parameter of type str

    Returns:
        List[str]: Output of type List[str]
    """
    raise NotImplementedError("This is a virtual stub node that needs to be implemented")
