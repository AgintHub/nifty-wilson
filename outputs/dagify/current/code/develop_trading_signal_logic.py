from ._develop_trading_signal_logic.fetch_parent_indicators import fetch_parent_indicators
from ._develop_trading_signal_logic.deduplicate_indicators import deduplicate_indicators
from ._develop_trading_signal_logic.create_indicator_definitions_registry import create_indicator_definitions_registry
from ._develop_trading_signal_logic.validate_indicators_exist import validate_indicators_exist
from ._develop_trading_signal_logic.define_buy_rule import define_buy_rule
from ._develop_trading_signal_logic.define_sell_rule import define_sell_rule
from ._develop_trading_signal_logic.define_hold_rule import define_hold_rule
from ._develop_trading_signal_logic.assemble_signal_logic_steps import assemble_signal_logic_steps
from ._develop_trading_signal_logic.generate_summary import generate_summary
from ._develop_trading_signal_logic.compute_logic_completeness import compute_logic_completeness
from ._develop_trading_signal_logic.handle_signal_logic_generation_error import handle_signal_logic_generation_error

from pydantic import BaseModel, Field
from typing import List


# -- PRD --
# 1. BULLET: Fetch the `indicators` list from the output of the
#   `identify_trading_indicators` node and store it in a local variable
#   `parent_indicators`.
#   Reason: Provides the authoritative source of which technical measures the strategy
#           is allowed to use.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Execute a JSON read of the parent node's output; assert the field exists
#           and is a non‑empty List[str]; raise a meaningful error if
#           missing.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Deduplicate `parent_indicators` while preserving order and assign the result
#   to `used_indicators`.
#   Reason: Ensures deterministic behaviour and matches the required output field
#           exactly.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Iterate through `parent_indicators`, add each unique entry to a new list;
#           use a set for O(1) membership checks.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Create a registry (dictionary) named `indicator_definitions` that maps each
#   indicator name to a pre‑defined calculation template, default parameters,
#   and signal direction (e.g., bullish when value > threshold).
#   Reason: Encapsulates domain expertise for each technical indicator, making later
#           rule composition straightforward and auditable.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Populate the dictionary manually for common indicators (e.g., SMA, EMA,
#           RSI, MACD, Bollinger Bands). Include keys: `calc_expression`,
#           `lookback`, `upper_thresh`, `lower_thresh`, `type`
#           (trend/momentum/volatility).
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Validate that every entry in `used_indicators` exists in
#   `indicator_definitions`; if any are missing, abort with a clear message
#   listing unsupported indicators.
#   Reason: Prevents runtime failures during back‑test when an undefined indicator
#           would be referenced.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Loop over `used_indicators`; raise Exception if `indicator not in
#           indicator_definitions`.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Define the primary BUY rule: combine one or more bullish conditions using
#   logical AND/OR as dictated by typical strategy patterns (e.g., SMA_fast >
#   SMA_slow AND RSI < 30).
#   Reason: Establishes the core entry logic which must be explicit and deterministic.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: For each indicator, substitute its `calc_expression` into a templated
#           condition string; concatenate conditions with `and`/`or` based
#           on a configurable `combination_map` (hard‑coded for this PRD).
# 
# -----------------------------------------------------------------------------
# 6. BULLET: Define the primary SELL rule: mirror the BUY rule but with opposite (bearish)
#   thresholds (e.g., SMA_fast < SMA_slow OR RSI > 70).
#   Reason: Provides an equally clear exit logic, ensuring symmetric treatment of
#           opposite market signals.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Reuse `indicator_definitions` with opposite threshold values; generate
#           condition strings analogous to BUY rule.
# 
# -----------------------------------------------------------------------------
# 7. BULLET: Define a NEUTRAL/HOLD rule that activates when neither BUY nor SELL
#   conditions are satisfied; this rule typically results in maintaining the
#   current position.
#   Reason: Guarantees that every possible market state maps to a deterministic output
#           (BUY, SELL, or HOLD).
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Create a third step: `else: HOLD` and document it as a logical fallback.
# 
# -----------------------------------------------------------------------------
# 8. BULLET: Assemble the three rule strings into an ordered list `signal_logic_steps`
#   following the sequence: 1) BUY condition, 2) SELL condition, 3) HOLD
#   fallback.
#   Reason: Matches the required output format and provides an intuitive, readable rule
#           set for downstream consumption.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Create a List[str] where each element is a plain‑English description of the
#           condition plus the action (e.g., "If SMA_20 > SMA_50 AND RSI <
#           30 → BUY").
# 
# -----------------------------------------------------------------------------
# 9. BULLET: Generate the `summary` field: a concise paragraph (≤ 3 sentences) that
#   outlines the overall methodology (indicator combination, hierarchy, risk
#   overlay), key decision pathways (BUY → SELL → HOLD), and any built‑in
#   risk‑management overlay (e.g., maximum exposure check).
#   Reason: Provides stakeholders with a quick high‑level view of the signal engine
#           without digging into the step list.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Compose a string using f‑string interpolation of the indicator set and rule
#           count; mention deterministic nature and that all indicators are
#           used.
# 
# -----------------------------------------------------------------------------
# 10. BULLET: Compute `is_logic_complete` as `True` only if (a) every indicator in
#   `parent_indicators` appears in `used_indicators` and (b) BUY, SELL, and
#   HOLD branches are all explicitly defined in `signal_logic_steps`;
#   otherwise set to `False`.
#   Reason: Explicitly signals to downstream nodes whether the signal definition is
#           exhaustive, enabling error‑handling before back‑testing.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Boolean check: `all(i in used_indicators for i in parent_indicators) and
#           len(signal_logic_steps) == 3`.
# 
# -----------------------------------------------------------------------------
# 11. BULLET: Package the four outputs (`signal_logic_steps`, `used_indicators`, `summary`,
#   `is_logic_complete`) into a JSON object matching the declared
#   `output_structure` and return it.
#   Reason: Conforms to the workflow contract so that subsequent nodes can reliably
#           consume the data.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Serialize the constructed Python dict using `json.dumps` with
#           ensure_ascii=False; no extra fields.
# 
# -----------------------------------------------------------------------------
# 12. BULLET: Include defensive error handling: if any step fails (e.g., missing indicator
#   definition, malformed parameter), raise a descriptive exception so that
#   the orchestrator can capture the failure and mark downstream `success`
#   flags accordingly.
#   Reason: Improves robustness of the pipeline and aids debugging in production.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Wrap the entire generation logic in a try/except block; on exception, log
#           the stack trace and re‑raise a custom
#           `SignalLogicGenerationError`.
# -- END PRD --



class IdentifyTradingIndicatorsOutput(BaseModel):
    """Pydantic model for identify_trading_indicators node outputs."""
    indicators: List[str] = Field(..., description="List of technical indicator or signal names that will be applied in the chosen trading strategy.")
    indicator_count: int = Field(..., description="Total number of indicators listed in the "indicators" field.")


class DevelopTradingSignalLogicOutput(BaseModel):
    """Pydantic model for develop_trading_signal_logic node outputs."""
    signal_logic_steps: List[str] = Field(..., description="Step\u2011by\u2011step outline of the logical rules that convert indicator readings into concrete BUY or SELL signals.")
    used_indicators: List[str] = Field(..., description="Explicit list of technical indicator names (as provided by the parent node) that are employed in the signal generation algorithm.")
    summary: str = Field(..., description="A concise executive summary describing the overall methodology, key decision pathways, and any risk\u2011management overlays.")
    is_logic_complete: bool = Field(..., description="Flag indicating whether the signal logic accounts for all identified indicators and fully defines buy, sell, and neutral decision branches.")


def develop_trading_signal_logic(identify_trading_indicators_input: IdentifyTradingIndicatorsOutput, **kwargs) -> DevelopTradingSignalLogicOutput:
    """Transforms the set of technical indicators identified for the chosen strategy into a deterministic, production‑grade algorithm that emits precise buy and sell signals.

    Args:
        identify_trading_indicators_input: Input from the 'identify_trading_indicators' node.
        **kwargs: Additional keyword arguments.

    Returns:
        DevelopTradingSignalLogicOutput: Object containing outputs for this node.
    """
    try:
        # Fetch the indicators list from the parent node output
        parent_indicators: List[str] = fetch_parent_indicators(input_data=identify_trading_indicators_input)
        
        # Deduplicate indicators while preserving order
        used_indicators: List[str] = deduplicate_indicators(indicators=parent_indicators)
        
        # Create indicator definitions registry
        indicator_definitions: dict = create_indicator_definitions_registry()
        
        # Validate all indicators exist in definitions
        validate_indicators_exist(indicators=used_indicators, definitions=indicator_definitions)
        
        # Define primary BUY rule
        buy_rule: str = define_buy_rule(indicators=used_indicators, definitions=indicator_definitions)
        
        # Define primary SELL rule
        sell_rule: str = define_sell_rule(indicators=used_indicators, definitions=indicator_definitions)
        
        # Define NEUTRAL/HOLD rule
        hold_rule: str = define_hold_rule()
        
        # Assemble signal logic steps in order
        signal_logic_steps: List[str] = assemble_signal_logic_steps(
            buy_rule=buy_rule, 
            sell_rule=sell_rule, 
            hold_rule=hold_rule
        )
        
        # Generate summary
        summary: str = generate_summary(
            indicators=used_indicators, 
            logic_steps=signal_logic_steps
        )
        
        # Compute logic completeness
        is_logic_complete: bool = compute_logic_completeness(
            parent_indicators=parent_indicators,
            used_indicators=used_indicators,
            signal_logic_steps=signal_logic_steps
        )
        
        return DevelopTradingSignalLogicOutput(
            signal_logic_steps=signal_logic_steps,
            used_indicators=used_indicators,
            summary=summary,
            is_logic_complete=is_logic_complete
        )
        
    except Exception as e:
        handle_signal_logic_generation_error(error=e)
        raise