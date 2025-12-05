from ._specify_asset_universe.extract_strategy_type import extract_strategy_type
from ._specify_asset_universe.create_strategy_asset_mapping import create_strategy_asset_mapping
from ._specify_asset_universe.lookup_strategy_mapping import lookup_strategy_mapping
from ._specify_asset_universe.generate_candidate_tickers import generate_candidate_tickers
from ._specify_asset_universe.validate_tickers_yahoo_finance import validate_tickers_yahoo_finance
from ._specify_asset_universe.assemble_asset_classes import assemble_asset_classes
from ._specify_asset_universe.assemble_asset_tickers import assemble_asset_tickers

from pydantic import BaseModel, Field
from typing import List


# -- PRD --
# 1. BULLET: Extract the `strategy_type` string from the output of
#   `select_trading_strategy_type` and store it in a local variable.
#   Reason: The chosen strategy type is the sole deterministic input that drives the
#           asset‑class mapping logic.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Parse the parent node JSON, read `strategy_type`, and validate that it is a
#           non‑empty string.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Define a static mapping table that links each supported `strategy_type` to a
#   prioritized list of compatible asset classes, based on quantitative
#   finance literature and industry best‑practice (e.g., "momentum" → ["US
#   equities", "ETF futures"], "mean reversion" → ["US equities", "FX spot"],
#   "stat‑arb" → ["US equities", "ETFs", "Options"]).
#   Reason: A deterministic mapping ensures reproducibility and removes ambiguity when
#           selecting asset classes.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Create a Python dict or JSON object; include comments citing sources such
#           as academic papers or Bloomberg research for each mapping.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Lookup the extracted `strategy_type` in the mapping table; if not found,
#   raise a clear validation error indicating an unsupported strategy.
#   Reason: Fail‑fast validation prevents downstream errors in back‑testing caused by
#           mismatched asset universes.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Use a try/except block; error message should include the invalid
#           `strategy_type` and list of supported keys.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: For each selected asset class, apply a rule‑based ticker selection algorithm:
#   - US equities → top 100 liquid stocks by average daily dollar volume from
#   the last 6 months (e.g., S&P 500 constituents + high‑cap mid‑caps).  -
#   Futures → front‑month continuous contracts for major indices,
#   commodities, and FX (e.g., ES, CL, GC, EUR=, JPY=).  - ETFs →
#   sector‑specific ETFs that best capture the factor exposure (e.g., XLK for
#   tech momentum).  - Commodities → physically deliverable contracts with
#   sufficient liquidity (e.g., WTI, Gold).
#   Reason: Rule‑based selection guarantees that the tickers are both tradable and
#           representative of the underlying asset class, aligning with the
#           strategy’s signal generation requirements.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Implement helper functions that query a static whitelist (hard‑coded lists)
#           or, if allowed, pull the latest constituents from a public API
#           (e.g., Wikipedia S&P 500 table). Ensure each list is
#           de‑duplicated and sorted alphabetically.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Validate each candidate ticker symbol for syntactic correctness (uppercase,
#   alphanumeric, optional suffix for futures contracts) and verify that it
#   exists on Yahoo Finance via a lightweight `yfinance.Ticker(ticker).info`
#   call; filter out any symbols that raise an exception or return empty
#   info.
#   Reason: Early validation avoids runtime failures in downstream data‑fetch nodes
#           (`fetch_stock_data_yahoo_data`).
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Iterate over the candidate list, perform a try/except around
#           `ticker.info['regularMarketPrice']`; keep only successful
#           symbols. Log any excluded tickers for audit.
# 
# -----------------------------------------------------------------------------
# 6. BULLET: Assemble the final `asset_classes` list (derived from the mapping step) and
#   the `asset_tickers` list (the validated, de‑duplicated ticker symbols).
#   Preserve the order: asset classes first as they appear in the mapping,
#   tickers sorted alphabetically within each class.
#   Reason: Consistent ordering simplifies downstream indexing and debugging,
#           especially when aligning tickers with fetched data frames.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Create two Python lists; use `sorted()` for tickers; concatenate
#           class‑specific ticker sub‑lists if needed.
# 
# -----------------------------------------------------------------------------
# 7. BULLET: Return a JSON object conforming exactly to the defined `output_structure`:
#   `asset_classes` as a List[str] and `asset_tickers` as a List[str].
#   Include a top‑level `success` flag in logs (not part of the schema) to
#   indicate whether the universe generation completed without errors.
#   Reason: Strict adherence to the schema guarantees compatibility with downstream
#           nodes that consume these fields.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Serialize the two lists using `json.dumps` ensuring no extra fields are
#           present; raise an exception only if serialization fails.
# -- END PRD --



class SelectTradingStrategyTypeOutput(BaseModel):
    """Pydantic model for select_trading_strategy_type node outputs."""
    strategy_type: str = Field(..., description="The chosen primary trading strategy type (e.g., "momentum", "mean reversion").")
    rationale: str = Field(..., description="A concise one\u2011sentence explanation of why this strategy type best fits the market analysis.")


class SpecifyAssetUniverseOutput(BaseModel):
    """Pydantic model for specify_asset_universe node outputs."""
    asset_classes: List[str] = Field(..., description="High\u2011level asset classes or instrument families to be traded (e.g., US equities, futures, commodities).")
    asset_tickers: List[str] = Field(..., description="Specific ticker symbols or contract identifiers selected from each asset class (e.g., AAPL, MSFT, ESZ2025).")


def specify_asset_universe(select_trading_strategy_type_input: SelectTradingStrategyTypeOutput, **kwargs) -> SpecifyAssetUniverseOutput:
    """Defines the full investable universe that aligns with the selected trading strategy.

    Args:
        select_trading_strategy_type_input: Input from the 'select_trading_strategy_type' node.
        **kwargs: Additional keyword arguments.

    Returns:
        SpecifyAssetUniverseOutput: Object containing outputs for this node.
    """
    # Extract the strategy type from input
    strategy_type: str = extract_strategy_type(input_data=select_trading_strategy_type_input)
    
    # Create static mapping table linking strategy types to asset classes
    strategy_mapping: dict = create_strategy_asset_mapping()
    
    # Lookup strategy type in mapping table with validation
    compatible_asset_classes: List[str] = lookup_strategy_mapping(strategy_type=strategy_type, mapping=strategy_mapping)
    
    # Generate candidate tickers for each selected asset class using rule-based selection
    candidate_tickers: List[str] = generate_candidate_tickers(asset_classes=compatible_asset_classes)
    
    # Validate ticker symbols for syntactic correctness and Yahoo Finance availability
    validated_tickers: List[str] = validate_tickers_yahoo_finance(candidate_tickers=candidate_tickers)
    
    # Assemble final lists with consistent ordering
    final_asset_classes: List[str] = assemble_asset_classes(asset_classes=compatible_asset_classes)
    final_asset_tickers: List[str] = assemble_asset_tickers(validated_tickers=validated_tickers)
    
    return SpecifyAssetUniverseOutput(
        asset_classes=final_asset_classes,
        asset_tickers=final_asset_tickers,
    )