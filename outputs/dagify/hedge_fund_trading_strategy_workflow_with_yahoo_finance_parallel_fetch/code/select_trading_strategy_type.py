from ._select_trading_strategy_type.classify_market_data_sources import classify_market_data_sources
from ._select_trading_strategy_type.map_techniques_to_archetypes import map_techniques_to_archetypes
from ._select_trading_strategy_type.compute_strategy_scores import compute_strategy_scores
from ._select_trading_strategy_type.select_top_strategy_with_tiebreaker import select_top_strategy_with_tiebreaker
from ._select_trading_strategy_type.generate_strategy_rationale import generate_strategy_rationale
from ._select_trading_strategy_type.validate_output_payload import validate_output_payload

from pydantic import BaseModel, Field
from typing import List


# -- PRD --
# 1. BULLET: Retrieve the complete output payload from the parent node
#   **define_market_analysis**, specifically the three fields:
#   `market_data_sources`, `analysis_techniques`, and `summary_note`.
#   Reason: All subsequent decision logic relies on an accurate, unaltered view of the
#           data ecosystem and analytical toolkit defined upstream.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Invoke the DAG runtime API to fetch the parent node's output JSON;
#           deserialize into native Python structures (list of strings for
#           sources and techniques, string for summary).
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Classify each entry in `market_data_sources` by data latency (real‑time vs
#   end‑of‑day), granularity (tick, minute, daily), and asset class coverage
#   (equities, futures, FX, commodities).
#   Reason: Strategy feasibility is heavily driven by the timeliness and granularity of
#           the underlying data; e.g., high‑frequency momentum requires
#           sub‑second latency.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Define a static taxonomy dictionary mapping known providers (e.g.,
#           Bloomberg, Yahoo Finance) to their latency/granularity
#           attributes; iterate over the list and build a structured
#           summary dictionary.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Map each technique listed in `analysis_techniques` to one or more canonical
#   strategy archetypes using a pre‑defined mapping matrix (e.g., "Moving
#   Average Crossover" → Momentum, "Bollinger Bands" → Mean Reversion,
#   "Factor Model" → Statistical Arbitrage).
#   Reason: Creating an explicit link between techniques and strategy families enables
#           systematic scoring rather than ad‑hoc intuition.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Maintain a JSON‑encoded mapping table; for each technique, lookup
#           corresponding archetype(s) and increment a counter in a
#           `strategy_score` dict.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Construct a weighted scoring model that evaluates candidate strategy types
#   (`momentum`, `mean_reversion`, `stat_arbitrage`, `sentiment_driven`,
#   etc.) on three axes: (1) Data Suitability (latency & granularity match),
#   (2) Technique Alignment (count of mapped techniques), (3) Cost/Licensing
#   Feasibility (derived from `summary_note` keywords such as "low cost" or
#   "premium").
#   Reason: A quantitative score reduces bias and provides a reproducible basis for
#           selection.
#   Impact: HIGH
#   Complexity: HIGH
#   Method: Assign axis weights (e.g., 0.4, 0.4, 0.2). For each candidate, compute:
#           data_score = sum(latency_match*weight_lat +
#           granularity_match*weight_gran), technique_score =
#           technique_counter * weight_tech, cost_score = 1 if summary_note
#           contains low‑cost indicator else 0. Multiply by axis weights
#           and sum to produce a final score.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Select the strategy type with the highest aggregated score; in case of a tie,
#   apply a deterministic tie‑breaker that prefers lower‑frequency strategies
#   (to honor typical end‑of‑day data availability from Yahoo Finance).
#   Reason: Ensures a single, repeatable output even when multiple strategies appear
#           equally viable.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Sort the `strategy_score` dictionary by value descending; if multiple
#           entries share the top score, order them by a predefined
#           precedence list ["momentum", "mean_reversion",
#           "stat_arbitrage", "sentiment_driven"].
# 
# -----------------------------------------------------------------------------
# 6. BULLET: Compose a one‑sentence `rationale` that references the most influential data
#   source and the dominant analysis technique driving the decision (e.g.,
#   "Momentum is selected because the high‑frequency daily price feed from
#   Bloomberg aligns with our Moving‑Average‑Crossover indicator set.")
#   Reason: The rationale must be concise yet traceable to the underlying analysis,
#           satisfying the output specification.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Identify the top‑scoring data source category and the highest‑frequency
#           technique from the mapping; interpolate into a template string.
# 
# -----------------------------------------------------------------------------
# 7. BULLET: Validate the final output payload against the declared `output_structure`:
#   ensure `strategy_type` is a non‑empty string drawn from the allowed
#   enumeration and `rationale` is a single‑sentence string (max 200
#   characters). Raise an error if validation fails.
#   Reason: Guarantees downstream nodes receive well‑formed inputs and prevents silent
#           propagation of errors.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Implement a lightweight schema validator (e.g., jsonschema) using the
#           `output_structure` definition; assert string types and
#           non‑emptiness; log descriptive error messages.
# -- END PRD --



class DefineMarketAnalysisOutput(BaseModel):
    """Pydantic model for define_market_analysis node outputs."""
    market_data_sources: List[str] = Field(..., description="Primary market data providers or platforms to be consumed (e.g., Bloomberg, Refinitiv, Quandl, Yahoo Finance, ICE Data Services).")
    analysis_techniques: List[str] = Field(..., description="Selected analytical methods, ranging from classic technical indicators to advanced sentiment and macro\u2011factor models.")
    summary_note: str = Field(..., description="A concise narrative linking the chosen data sources with the analysis techniques, emphasizing data fidelity, licensing considerations, and estimated computational resource requirements.")


class SelectTradingStrategyTypeOutput(BaseModel):
    """Pydantic model for select_trading_strategy_type node outputs."""
    strategy_type: str = Field(..., description="The chosen primary trading strategy type (e.g., "momentum", "mean reversion").")
    rationale: str = Field(..., description="A concise one\u2011sentence explanation of why this strategy type best fits the market analysis.")


def select_trading_strategy_type(define_market_analysis_input: DefineMarketAnalysisOutput, **kwargs) -> SelectTradingStrategyTypeOutput:
    """Determines the optimal primary trading strategy category based on the market analysis.

    Args:
        define_market_analysis_input: Input from the 'define_market_analysis' node.
        **kwargs: Additional keyword arguments.

    Returns:
        SelectTradingStrategyTypeOutput: Object containing outputs for this node.
    """
    # Extract inputs
    market_data_sources: List[str] = define_market_analysis_input.market_data_sources
    analysis_techniques: List[str] = define_market_analysis_input.analysis_techniques
    summary_note: str = define_market_analysis_input.summary_note
    
    # Classify data sources by latency, granularity, and asset class coverage
    data_classification: dict = classify_market_data_sources(sources=market_data_sources)
    
    # Map analysis techniques to strategy archetypes
    technique_mapping: dict = map_techniques_to_archetypes(techniques=analysis_techniques)
    
    # Build weighted scoring model for candidate strategies
    strategy_scores: dict = compute_strategy_scores(
        data_classification=data_classification,
        technique_mapping=technique_mapping,
        summary_note=summary_note
    )
    
    # Select strategy with highest score, applying tie-breaker if needed
    selected_strategy: str = select_top_strategy_with_tiebreaker(scores=strategy_scores)
    
    # Generate rationale based on dominant factors
    rationale_text: str = generate_strategy_rationale(
        selected_strategy=selected_strategy,
        data_classification=data_classification,
        technique_mapping=technique_mapping
    )
    
    # Validate output against schema requirements
    validate_output_payload(strategy_type=selected_strategy, rationale=rationale_text)
    
    return SelectTradingStrategyTypeOutput(
        strategy_type=selected_strategy,
        rationale=rationale_text
    )