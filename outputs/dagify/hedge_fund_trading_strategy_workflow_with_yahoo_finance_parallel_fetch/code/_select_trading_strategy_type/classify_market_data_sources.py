# -- PRD --
# 1. BULLET: Create a static lookup table that maps known data providers to their typical
#   latency, granularity, and asset‑class coverage.
#   Reason: The downstream strategy scoring relies on accurate, pre‑defined
#           characteristics for each source.
#   Impact: Enables deterministic classification and reduces the need for external API
#           calls at runtime.
#   Complexity: MEDIUM
#   Method: Define a Python dictionary (or JSON file) keyed by provider name; populate
#           it with curated metadata from documentation or industry
#           resources; load it lazily within the shim.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Parse the incoming `sources` string, validate each entry, and apply fallback
#   logic for unknown providers.
#   Reason: Inputs may come in various formats or include unregistered sources; robust
#           handling prevents crashes later in the pipeline.
#   Impact: Ensures the shim always returns a well‑formed classification map, improving
#           reliability of downstream nodes.
#   Complexity: LOW
#   Method: Use `json.loads` to convert the string to a list; iterate over items,
#           lookup in the static table, and for missing entries assign a
#           default classification (e.g., latency: "unknown", granularity:
#           "unknown", asset_classes: []).
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Serialize the resulting classification dictionary back to a JSON string for
#   the `output` field.
#   Reason: Downstream nodes expect a string payload; JSON provides a portable,
#           language‑agnostic representation.
#   Impact: Standardizes data exchange format, facilitating easy deserialization by
#           later nodes.
#   Complexity: LOW
#   Method: Use `json.dumps` with `ensure_ascii=False` to convert the dictionary to a
#           string; optionally sort keys for deterministic output.
# -- END PRD --


def classify_market_data_sources(sources: str) -> str:
    """
    Classifies a list of market data sources into categories such as latency, granularity, and asset‑class coverage.

    Args:
        sources: Input parameter of type str

    Returns:
        str: Output of type dict
    """
    raise NotImplementedError("This is a virtual stub node that needs to be implemented")
