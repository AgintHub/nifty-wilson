# -- PRD --
# 1. BULLET: Create an exhaustive inventory of all potential market data providers
#   relevant to the intended asset classes (equities, futures, FX,
#   macro‑economic indicators, alternative data).
#   Reason: A complete provider list ensures no critical data source is overlooked,
#           which could impair signal generation or risk assessment.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Conduct desk research using vendor documentation, industry surveys, and
#           existing internal data catalogs; record provider name, URL, and
#           contact details in a spreadsheet.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: For each provider, classify the available data products into categories
#   (e.g., real‑time quotes, end‑of‑day bars, fundamentals, news, sentiment,
#   macro‑economics).
#   Reason: Categorization allows downstream mapping of technique inputs to the correct
#           data stream.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Create a matrix with rows = providers, columns = data categories; fill
#           cells with yes/no and short notes on coverage.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Capture technical attributes for every data product: granularity (tick,
#   1‑min, daily), update latency (ms, seconds, minutes), delivery method
#   (API, streaming, FTP), licensing model (subscription, per‑call,
#   open‑source), and cost (USD per month or per request).
#   Reason: These attributes directly affect feasibility, compliance, and budget
#           planning.
#   Impact: HIGH
#   Complexity: HIGH
#   Method: Extract specifications from provider datasheets or API reference docs;
#           store in a structured JSON schema for automated consumption.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Select the subset of providers and data products that satisfy the strategy’s
#   requirements for coverage, latency, and budget, and document them as the
#   final `market_data_sources` list.
#   Reason: Only the chosen sources will be integrated into the pipeline; a curated
#           list prevents scope creep.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Apply filter criteria (e.g., latency < 500 ms for high‑frequency, cost <
#           $5000/month) on the attribute matrix; output provider names as
#           a plain‑text list.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Identify analytical techniques needed to transform the selected data into
#   actionable signals, spanning four families: statistical & technical
#   indicators, machine‑learning models, sentiment & news analytics, and
#   macro‑factor regressions.
#   Reason: A taxonomy of techniques guides the development of the signal logic and
#           ensures coverage of all information dimensions.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Review academic literature, industry white‑papers, and internal expertise;
#           list each technique with a short definition.
# 
# -----------------------------------------------------------------------------
# 6. BULLET: For every technique, enumerate required inputs (specific data fields,
#   look‑back windows, transformation steps), estimate computational
#   complexity (O(N), O(N log N), or O(N^2)), and list software/library
#   dependencies (e.g., NumPy, pandas‑ta, TensorFlow, spaCy).
#   Reason: Explicit input‑dependency mapping prevents runtime failures and clarifies
#           resource budgeting.
#   Impact: HIGH
#   Complexity: HIGH
#   Method: Create a per‑technique specification table: Technique | Inputs | Complexity
#           | Dependencies; use Big‑O notation and tag required Python
#           packages.
# 
# -----------------------------------------------------------------------------
# 7. BULLET: Consolidate the technique names into the `analysis_techniques` output list,
#   preserving the same order as the specification table.
#   Reason: A clean, ordered list is required by downstream nodes
#           (identify_trading_indicators).
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Extract the ‘Technique’ column from the specification table and output as a
#           List[str].
# 
# -----------------------------------------------------------------------------
# 8. BULLET: Draft a concise `summary_note` that links each selected data source to the
#   techniques that consume it, highlights any licensing constraints (e.g.,
#   redistribution limits), and provides an estimate of CPU/GPU resources
#   needed for the full pipeline (e.g., 4‑core CPU, 16 GB RAM, optional GPU
#   for deep‑learning models).
#   Reason: The summary serves as a quick reference for architects and compliance
#           officers and satisfies the node’s output requirement.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Use a templated paragraph: "Data source X provides Y (granularity Z) which
#           feeds into technique A and B; licensing is …; anticipated
#           compute per day is …"; ensure length < 500 words.
# 
# -----------------------------------------------------------------------------
# 9. BULLET: Validate that all three output fields conform to their declared
#   PrimitiveTypes and that no duplicate entries exist in the lists.
#   Reason: Strict type compliance avoids downstream schema violations and simplifies
#           integration testing.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Run a Python validation script: assert isinstance(market_data_sources,
#           list) and all(isinstance(s, str) for s in market_data_sources),
#           similarly for analysis_techniques; ensure summary_note is a
#           str.
# 
# -----------------------------------------------------------------------------
# 10. BULLET: Package the three outputs into the final JSON payload as defined in
#   `output_structure` and return it to the orchestrator.
#   Reason: Proper packaging completes the node’s contract with the workflow engine.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Construct a dictionary with keys 'market_data_sources',
#           'analysis_techniques', 'summary_note' and serialize with
#           json.dumps() (if required by the platform).
# -- END PRD --

from pydantic import BaseModel, Field
from typing import List


class DefineMarketAnalysisOutput(BaseModel):
    """Pydantic model for define_market_analysis node outputs."""
    market_data_sources: List[str] = Field(..., description="Primary market data providers or platforms to be consumed (e.g., Bloomberg, Refinitiv, Quandl, Yahoo Finance, ICE Data Services).")
    analysis_techniques: List[str] = Field(..., description="Selected analytical methods, ranging from classic technical indicators to advanced sentiment and macro\u2011factor models.")
    summary_note: str = Field(..., description="A concise narrative linking the chosen data sources with the analysis techniques, emphasizing data fidelity, licensing considerations, and estimated computational resource requirements.")


def define_market_analysis(general_input: str, **kwargs) -> DefineMarketAnalysisOutput:
    """Develops a detailed blueprint of all external market data feeds and internal analytical methods that will be leveraged by the trading strategy.

    Args:
        general_input: General input string for the root node.
        **kwargs: Additional keyword arguments.

    Returns:
        DefineMarketAnalysisOutput: Object containing outputs for this node.
    """
    # TODO: Implement this function

    # Return stub output with placeholder values
    return DefineMarketAnalysisOutput(
        market_data_sources=[],
        analysis_techniques=[],
        summary_note="",
    )