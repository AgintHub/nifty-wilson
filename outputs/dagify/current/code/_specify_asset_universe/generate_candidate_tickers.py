# -- PRD --
# 1. BULLET: Create a static mapping of asset classes to exemplar ticker lists based on
#   industry standards and historical liquidity.
#   Reason: Provides deterministic, reproducible candidates without external data
#           dependencies.
#   Impact: Ensures the downstream validation step receives a well‑formed, realistic
#           set of tickers for each class.
#   Complexity: LOW
#   Method: Define a Python dictionary where keys are normalized asset class strings
#           and values are pre‑curated lists of ticker symbols; load this
#           dictionary at module import.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Implement a rule‑engine that selects a subset of tickers per class (e.g., top
#   N by market cap or most‑traded contracts).
#   Reason: Limits the number of candidates to a manageable size while preserving
#           relevance to the chosen strategy.
#   Impact: Reduces computational load for later validation and improves
#           signal‑to‑noise ratio for strategy design.
#   Complexity: MEDIUM
#   Method: Use pandas to sort the predefined ticker list by a stored metric (market
#           cap, volume) and slice the top K entries; expose K as a
#           configurable parameter.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Normalize and validate ticker format (uppercase, no spaces, correct suffixes)
#   before returning.
#   Reason: Prevents downstream errors when interfacing with data providers such as
#           Yahoo Finance.
#   Impact: Improves robustness of the pipeline by catching malformed symbols early.
#   Complexity: LOW
#   Method: Apply regex checks and string manipulation (e.g., str.upper(), replace
#           spaces) on each ticker; raise warnings for any that fail the
#           pattern.
# -- END PRD --

from typing import List


def generate_candidate_tickers(asset_classes: str) -> List[str]:
    """
    Generates a list of candidate ticker symbols for the provided high‑level asset classes using predefined selection rules.

    Args:
        asset_classes: Input parameter of type str

    Returns:
        List[str]: Output of type List[str]
    """
    raise NotImplementedError("This is a virtual stub node that needs to be implemented")
