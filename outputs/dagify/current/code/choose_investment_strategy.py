# -- PRD --
# 1. BULLET: Retrieve the list of core objectives from the output of
#   `clarify_fund_objectives` and confirm the list is non-empty.
#   Reason: The strategy choice must be grounded in the fund’s stated objectives; an
#           empty list would invalidate further logic.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Parse the JSON output, access the `objectives` array, and assert its length
#           > 0; if empty, raise a validation error.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Apply keyword extraction to each objective to capture thematic words (e.g.,
#   'growth', 'liquidity', 'global markets').
#   Reason: Keywords provide a structured representation of objectives that can be
#           matched against strategy descriptors.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Use a lightweight NLP library (e.g., spaCy or NLTK) to perform part-of-
#           speech tagging and extract nouns/adjectives; optionally employ
#           TF‑IDF scoring to weight unique terms.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Define a mapping table of candidate strategy categories to characteristic
#   keyword sets.
#   Reason: A formal mapping enables objective‑to‑strategy translation via keyword
#           overlap.
#   Impact: LOW
#   Complexity: LOW
#   Method: Create a JSON object where keys are strategy names and values are arrays of
#           associated keywords, e.g., {'Long/Short Equity': ['equity',
#           'beta', 'alpha'], 'Global Macro': ['macro', 'interest',
#           'currency']}
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Score each strategy by counting keyword matches between the aggregated
#   objective keywords and each strategy’s keyword set, optionally weighting
#   by keyword frequency.
#   Reason: A quantitative score provides an objective basis for selecting the best fit
#           strategy.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: For each strategy, iterate over its keyword set, increment a counter when
#           the keyword appears in the objective keyword list; normalize by
#           total number of keywords to produce a score.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Identify the strategy with the highest score; in case of a tie, apply a
#   deterministic tie‑breaker such as alphabetical order or a predefined
#   priority hierarchy.
#   Reason: Ensures a single, reproducible output strategy.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Use a max‑function on the score dictionary; if multiple keys share the
#           maximum, sort keys alphabetically and pick the first.
# 
# -----------------------------------------------------------------------------
# 6. BULLET: Construct a concise, single‑sentence rationale that links the top strategy’s
#   key characteristics to the most salient objective themes.
#   Reason: The rationale must explain the alignment in a digestible format for
#           stakeholders.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Select the two highest‑frequency objective themes, insert them into a
#           template such as "We choose {strategy} because it targets
#           {theme1} and {theme2} objectives."
# 
# -----------------------------------------------------------------------------
# 7. BULLET: Validate that the rationale contains only one sentence and no excessive
#   technical jargon, truncating if necessary.
#   Reason: Keeps the output concise and readable, matching the specification.
#   Impact: LOW
#   Complexity: LOW
#   Method: Split the string on period characters; assert length == 1; if more,
#           collapse into a single sentence using a summarization or string
#           truncation technique.
# 
# -----------------------------------------------------------------------------
# 8. BULLET: Return the final `strategy_category` and `rationale` values as specified in
#   the output structure.
#   Reason: Completes the node by producing the required fields for downstream nodes.
#   Impact: LOW
#   Complexity: LOW
#   Method: Serialize the two strings into a JSON object matching the
#           `output_structure` schema.
# -- END PRD --

from pydantic import BaseModel, Field


class ClarifyFundObjectivesOutput(BaseModel):
    """Pydantic model for clarify_fund_objectives node outputs."""
    objectives: str = Field(..., description="Bullet list of the fund's core objectives, each item a concise statement.")
    objective_count: int = Field(..., description="Number of objective bullets provided.")


class ChooseInvestmentStrategyOutput(BaseModel):
    """Pydantic model for choose_investment_strategy node outputs."""
    strategy_category: str = Field(..., description="Primary hedge fund strategy category selected (e.g., Long/Short Equity, Global Macro).")
    rationale: str = Field(..., description="One-sentence rationale explaining why this strategy best serves the fund objectives.")


def choose_investment_strategy(clarify_fund_objectives_input: ClarifyFundObjectivesOutput, **kwargs) -> ChooseInvestmentStrategyOutput:
    """Identify the high-level investment strategy category.

    Args:
        clarify_fund_objectives_input: Input from the 'clarify_fund_objectives' node.
        **kwargs: Additional keyword arguments.

    Returns:
        ChooseInvestmentStrategyOutput: Object containing outputs for this node.
    """
    # TODO: Implement this function

    # Return stub output with placeholder values
    return ChooseInvestmentStrategyOutput(
        strategy_category="",
        rationale="",
    )