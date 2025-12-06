# -- PRD --
# 1. BULLET: Parse the input `service_providers` list from `list_service_providers` and
#   verify it contains the expected provider categories.
#   Reason: Ensures that downstream calculations use a valid and complete set of
#           provider types, preventing misalignment between expected and
#           actual inputs.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Use a simple validation step that checks for non‑empty string entries and
#           removes duplicates; log a warning if unexpected values are
#           found.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Define a static cost lookup table mapping each provider category to a
#   mid‑point annual fee based on industry benchmarks (e.g., prime broker
#   $200k, fund administrator $250k, auditor $80k, legal counsel $70k,
#   compliance consultant $60k, custodian $30k).
#   Reason: Provides a repeatable, auditable basis for cost estimation that reflects
#           realistic market rates for a mid‑size hedge fund.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Create a dictionary in code; source rates from recent industry reports
#           (e.g., Hedge Fund Research, Preqin) and adjust for currency if
#           needed.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: For each provider in the validated list, look up the corresponding fee in the
#   lookup table and append the provider name to `cost_items` and the fee to
#   `estimated_usd`.
#   Reason: Directly translates provider categories into concrete cost items and
#           amounts, ensuring output alignment with the required schema.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Iterate over `service_providers`, perform a dictionary lookup, and perform
#           error handling for missing keys by defaulting to a conservative
#           estimate.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Add overhead cost categories: office rent, utilities, and staff salaries;
#   estimate each using region‑adjusted benchmarks (e.g., office $120k, tech
#   infrastructure $150k, admin staff $200k).
#   Reason: Overhead is a significant portion of annual expenses and must be
#           represented to produce a realistic total cost.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Use a small supplemental table for overhead categories, ensuring
#           consistency with the provider lookup table.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Append the overhead categories to `cost_items` and their estimates to
#   `estimated_usd`.
#   Reason: Ensures the final cost lists include all necessary items for transparency
#           and completeness.
#   Impact: LOW
#   Complexity: LOW
#   Method: Extend the lists using the same loop mechanism used for providers.
# 
# -----------------------------------------------------------------------------
# 6. BULLET: Compute `total_estimated_annual_cost` by summing the numeric values in
#   `estimated_usd`.
#   Reason: Provides a single metric that will be used by downstream nodes (e.g.,
#           draft_fee_structure) for fee calibration.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Use a functional aggregate (e.g., `sum(estimated_usd)`) and cast to float.
# 
# -----------------------------------------------------------------------------
# 7. BULLET: Validate that the lengths of `cost_items` and `estimated_usd` match and that
#   all entries are non‑negative numbers before returning the output.
#   Reason: Ensures data integrity and prevents downstream errors caused by malformed
#           output.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Assert conditions; if validation fails, raise a descriptive exception or
#           return a structured error payload.
# -- END PRD --

from pydantic import BaseModel, Field
from typing import List


class ListServiceProvidersOutput(BaseModel):
    """Pydantic model for list_service_providers node outputs."""
    service_providers: List[str] = Field(..., description="Checklist of mandatory third-party service provider categories.")


class EstimateSetupAndOperatingCostsOutput(BaseModel):
    """Pydantic model for estimate_setup_and_operating_costs node outputs."""
    cost_items: List[str] = Field(..., description="List of cost item names, including each service provider and overhead categories.")
    estimated_usd: List[float] = Field(..., description="Corresponding estimated annual cost in USD for each item in cost_items.")
    total_estimated_annual_cost: float = Field(..., description="Sum of all estimated USD values, representing the total annual cost.")


def estimate_setup_and_operating_costs(list_service_providers_input: ListServiceProvidersOutput, **kwargs) -> EstimateSetupAndOperatingCostsOutput:
    """Rough cost model for fund setup and operations.

    Args:
        list_service_providers_input: Input from the 'list_service_providers' node.
        **kwargs: Additional keyword arguments.

    Returns:
        EstimateSetupAndOperatingCostsOutput: Object containing outputs for this node.
    """
    # TODO: Implement this function

    # Return stub output with placeholder values
    return EstimateSetupAndOperatingCostsOutput(
        cost_items=[],
        estimated_usd=[],
        total_estimated_annual_cost=0.0,
    )