# -- PRD --
# 1. BULLET: Implement a market scoring system to evaluate the performance of each market
#   based on their liquidity, regulatory requirements, and competitive
#   landscape.
#   Reason: A well-designed scoring system is necessary to accurately determine the
#           top-performing markets.
#   Impact: The market scoring system will significantly affect the accuracy of the top
#           market selection.
#   Complexity: HIGH
#   Method: Use machine learning algorithms to train a model that predicts market
#           performance based on historical data and market
#           characteristics.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Design a ranking algorithm to select the top markets based on their scores
#   and the specified maximum number of markets.
#   Reason: A ranking algorithm is necessary to ensure that the top markets are
#           selected accurately based on their scores.
#   Impact: The ranking algorithm will affect the final selection of top markets.
#   Complexity: MEDIUM
#   Method: Use a stable sorting algorithm such as QuickSort or MergeSort to rank the
#           markets based on their scores.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Implement input validation to ensure that the market scores and maximum
#   number of markets are provided correctly.
#   Reason: Input validation is necessary to prevent errors and exceptions during the
#           execution of the node.
#   Impact: Input validation will prevent errors and exceptions that can lead to system
#           crashes or unexpected behavior.
#   Complexity: LOW
#   Method: Use type hinting and input validation libraries such as Pydantic to ensure
#           that the input parameters are provided correctly.
# -- END PRD --

from typing import List


def select_top_markets(market_scores: str, max_markets: str) -> List[str]:
    """
    Selects the top-performing markets based on their scores and a specified maximum number of markets.

    Args:
        market_scores: Input parameter of type str
max_markets: Input parameter of type str

    Returns:
        List[str]: Output of type List[str]
    """
    raise NotImplementedError("This is a virtual stub node that needs to be implemented")
