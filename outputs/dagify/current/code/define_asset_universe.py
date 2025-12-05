# -- PRD --
# 1. BULLET: Extract the `strategy_category` string from the output of the parent node
#   `choose_investment_strategy`.
#   Reason: The asset universe depends directly on the chosen strategy, so the first
#           step is to acquire this value for subsequent lookup.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Access the parent node’s output dictionary via the execution engine’s
#           dependency graph API; store the string in a local variable
#           called `strategy`.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Validate the extracted `strategy` against a predefined whitelist of accepted
#   strategy categories (e.g., "Long/Short Equity", "Global Macro",
#   "Event‑Driven", "Statistical Arbitrage", "Fixed Income Arbitrage").
#   Reject or raise an error if the strategy is not in the whitelist.
#   Reason: Ensures downstream asset mapping is defined and prevents mis‑specification.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Maintain a constant `VALID_STRATEGIES` list; use a simple membership test
#           (`strategy in VALID_STRATEGIES`).
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Lookup the canonical asset list for the validated strategy from a static
#   mapping dictionary where keys are strategy names and values are ordered
#   lists of asset classes/instruments (e.g., {'Long/Short Equity': ['US
#   Large‑Cap Equities', 'UK FTSE 100', 'NASDAQ 100', 'S&P 500 Futures'],
#   'Global Macro': ['USD/EUR FX', 'US Treasury 10‑yr Futures', 'Gold Spot',
#   'Crude Oil WTI Futures']}).
#   Reason: Provides a consistent, curated universe that aligns with industry best
#           practices for each strategy type.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Implement the mapping as a Python dictionary (`STRATEGY_ASSET_MAP`) and
#           retrieve with `STRATEGY_ASSET_MAP[strategy]`.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Enforce the maximum list size of 10 items: if the retrieved list has more
#   than 10 elements, select the top‑10 based on a predetermined priority
#   metric (e.g., liquidity volume, market capitalization, or default order
#   defined in the mapping).
#   Reason: Complies with the specification that the list must not exceed 10 items
#           while preserving the most relevant instruments.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: If `len(asset_list) > 10`, slice the first 10 elements (`asset_list =
#           asset_list[:10]`). If custom priority is required, apply a
#           weighted sorting function before slicing.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Construct the output structure: assign the finalized asset list to the
#   `assets` field and set `asset_count` to the length of the list.
#   Reason: Provides the exact output format expected by downstream nodes.
#   Impact: LOW
#   Complexity: LOW
#   Method: Return a dictionary: `{'assets': asset_list, 'asset_count':
#           len(asset_list)}`.
# -- END PRD --

from pydantic import BaseModel, Field
from typing import List


class ChooseInvestmentStrategyOutput(BaseModel):
    """Pydantic model for choose_investment_strategy node outputs."""
    strategy_category: str = Field(..., description="Primary hedge fund strategy category selected (e.g., Long/Short Equity, Global Macro).")
    rationale: str = Field(..., description="One-sentence rationale explaining why this strategy best serves the fund objectives.")


class DefineAssetUniverseOutput(BaseModel):
    """Pydantic model for define_asset_universe node outputs."""
    assets: List[str] = Field(..., description="List of asset classes and specific instruments that the strategy will trade")
    asset_count: int = Field(..., description="Number of items included in the assets list (should be \u226410)")


def define_asset_universe(choose_investment_strategy_input: ChooseInvestmentStrategyOutput, **kwargs) -> DefineAssetUniverseOutput:
    """Enumerate tradable assets and instruments for the selected hedge fund strategy.

    Args:
        choose_investment_strategy_input: Input from the 'choose_investment_strategy' node.
        **kwargs: Additional keyword arguments.

    Returns:
        DefineAssetUniverseOutput: Object containing outputs for this node.
    """
    # TODO: Implement this function

    # Return stub output with placeholder values
    return DefineAssetUniverseOutput(
        assets=[],
        asset_count=0,
    )