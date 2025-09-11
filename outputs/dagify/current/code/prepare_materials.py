# -- PRD --
# 1. BULLET: Retrieve the full design_experiment output and deserialize the JSON into an
#   in-memory object.
#   Reason: The design_experiment output contains the experiment variables and protocol
#           which dictate material requirements.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Use a JSON parser to load design_experiment JSON into a dictionary or a
#           typed data class. Validate all required keys exist.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Map each measurement method and dependent variable to its specific instrument
#   or consumable (e.g., a pH meter for pH measurement).
#   Reason: Accurately linking measurement needs to physical items ensures no gaps in
#           equipment.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Implement a lookup table (dictionary) mapping variable names to
#           instrument/consumable types. Apply fallback rules for
#           unspecified variables.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Enumerate required reagents, chemicals, and labware by cross-referencing
#   independent variables, dependent variables, and sample size.
#   Reason: The quantity of consumables depends on how many samples and repetitions are
#           planned.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: For each sample unit, multiply reagent volumes by sample_size. Add safety
#           margins (e.g., +10%). Use unit conversion functions to
#           standardize measurements.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Validate availability of each item by querying the laboratory inventory
#   system (or a static inventory list).
#   Reason: Prevents delays during execution due to missing items.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Call an inventory API or read a CSV of available items. If an item is out
#           of stock, flag a warning and suggest an alternative or reorder.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Calculate the cost of each item by multiplying the unit price by the required
#   quantity.
#   Reason: Provides a financial estimate needed for budgeting.
#   Impact: LOW
#   Complexity: LOW
#   Method: Store unit prices in a price catalog dictionary. Perform arithmetic
#           operations and sum totals. Round to two decimal places.
# 
# -----------------------------------------------------------------------------
# 6. BULLET: Aggregate all items, quantities, and costs into the required_items,
#   quantities, and total_cost output fields.
#   Reason: Organizes data into the defined output structure for downstream nodes.
#   Impact: LOW
#   Complexity: LOW
#   Method: Append each item, quantity, and cost to respective lists; compute
#           total_cost as sum of item costs.
# 
# -----------------------------------------------------------------------------
# 7. BULLET: Set is_prepared to True only after confirming all items are available,
#   quantities match calculations, and cost estimate is finalized.
#   Reason: Guarantees that the experiment will not halt due to missing resources.
#   Impact: HIGH
#   Complexity: LOW
#   Method: If any availability check fails or quantity mismatch occurs, set
#           is_prepared to False and record details in preparation_notes.
# 
# -----------------------------------------------------------------------------
# 8. BULLET: Compile a detailed preparation_notes string that logs any substitutions,
#   special handling instructions, or procurement actions taken.
#   Reason: Provides traceability and context for future troubleshooting.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Concatenate status messages from prior steps, include timestamps, and
#           format as a multiline string.
# -- END PRD --

from pydantic import BaseModel, Field
from typing import List


class DesignExperimentOutput(BaseModel):
    """Pydantic model for design_experiment node outputs."""
    hypothesis: str = Field(..., description="The testable hypothesis to be examined")
    independent_variables: str = Field(..., description="List of variables that will be manipulated in the experiment")
    dependent_variables: str = Field(..., description="List of variables that will be measured as outcomes")
    control_variables: str = Field(..., description="List of variables that will be held constant to avoid confounding effects")
    measurement_methods: str = Field(..., description="Methods or instruments used to quantify each dependent variable")
    sample_size: int = Field(..., description="Number of experimental units or trials to be performed")
    experimental_protocol: str = Field(..., description="Step\u2011by\u2011step description of how the experiment will be executed")


class PrepareMaterialsOutput(BaseModel):
    """Pydantic model for prepare_materials node outputs."""
    required_items: List[str] = Field(..., description="Names of all materials and equipment items required for the experiment")
    quantities: List[int] = Field(..., description="Quantities of each corresponding item listed in required_items")
    total_cost: float = Field(..., description="Estimated total cost of all prepared items")
    is_prepared: bool = Field(..., description="Whether all items have been successfully prepared and ready for use")
    preparation_notes: str = Field(..., description="Any additional notes or remarks about the preparation process")


def prepare_materials(design_experiment_input: DesignExperimentOutput, **kwargs) -> PrepareMaterialsOutput:
    """Prepare the necessary materials and equipment required for the experiment based on the design specifications.

    Args:
        design_experiment_input: Input from the 'design_experiment' node.
        **kwargs: Additional keyword arguments.

    Returns:
        PrepareMaterialsOutput: Object containing outputs for this node.
    """
    # TODO: Implement this function

    # Return stub output with placeholder values
    return PrepareMaterialsOutput(
        required_items=[],
        quantities=[],
        total_cost=0.0,
        is_prepared=False,
        preparation_notes="",
    )