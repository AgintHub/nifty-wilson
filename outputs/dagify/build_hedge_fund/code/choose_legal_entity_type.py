# -- PRD --
# 1. BULLET: Retrieve the jurisdiction value from the output of the parent node
#   'select_jurisdiction' and store it as a string variable.
#   Reason: The jurisdiction drives the available legal entity options; retrieving it
#           ensures the node works with the most current choice.
#   Impact: LOW
#   Complexity: LOW
#   Method: Use a simple JSON path extraction: jurisdiction =
#           parent_outputs['select_jurisdiction']['jurisdiction'].
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Create a jurisdiction‑entity compatibility lookup table that maps each
#   jurisdiction to its commonly used hedge‑fund structures (e.g., Cayman →
#   LP/LLC; Delaware → LP; Luxembourg → SICAV).
#   Reason: Hard‑coding a small, curated table avoids expensive API calls and ensures
#           quick, deterministic decision‑making.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Define a static dictionary in the node’s code: compat = { 'Cayman': ['LP',
#           'LLC'], 'Delaware': ['LP'], 'Luxembourg': ['SICAV'] }.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Apply a priority ordering rule within each jurisdiction that ranks entities
#   by regulatory simplicity, tax efficiency, and investor familiarity.
#   Reason: A deterministic ranking ensures consistent outputs across runs and aligns
#           with industry best practices.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Assign a scoring matrix (e.g., regulatory=3, tax=2, investor=1) and compute
#           a weighted sum for each candidate; choose the one with the
#           highest score.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Select the top‑scoring entity type from the sorted list and assign it to the
#   'entity_type' output field.
#   Reason: Directly mapping the highest score to output guarantees that the chosen
#           structure is objectively justified.
#   Impact: LOW
#   Complexity: LOW
#   Method: entity_type = sorted_entities[0]['type'].
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Construct a one‑sentence explanation that references the jurisdiction, chosen
#   entity, and the primary justification (e.g., regulatory simplicity).
#   Reason: A concise justification satisfies the prompt requirement and aids
#           downstream nodes that rely on narrative context.
#   Impact: LOW
#   Complexity: LOW
#   Method: Use string interpolation: explanation = f'{jurisdiction} offers a
#           {entity_type} structure that combines {primary_reason} for
#           hedge‑fund operations.'
# 
# -----------------------------------------------------------------------------
# 6. BULLET: Validate that all output fields meet the defined data types: entity_type and
#   jurisdiction as strings; explanation as a single‑sentence string; enforce
#   type checks and raise descriptive errors if mismatched.
#   Reason: Robust type validation prevents downstream failures and maintains data
#           integrity throughout the DAG.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Implement a validation function that checks isinstance(field, str) and
#           len(explanation.split('.')) == 1; log errors via a custom
#           exception handler.
# 
# -----------------------------------------------------------------------------
# 7. BULLET: Return the outputs in the exact order and structure specified by the
#   output_schema to ensure compatibility with child nodes.
#   Reason: Maintaining consistent output ordering simplifies integration with
#           downstream logic and reduces debugging effort.
#   Impact: LOW
#   Complexity: LOW
#   Method: Wrap outputs in an OrderedDict: {'entity_type': entity_type,
#           'jurisdiction': jurisdiction, 'explanation': explanation}.
# -- END PRD --

from pydantic import BaseModel, Field


class SelectJurisdictionOutput(BaseModel):
    """Pydantic model for select_jurisdiction node outputs."""
    jurisdiction: str = Field(..., description="The selected fund domicile jurisdiction (e.g., Cayman, Delaware, Luxembourg).")
    pros: str = Field(..., description="A list of two key advantages of the selected jurisdiction.")
    cons: str = Field(..., description="A list of two key disadvantages of the selected jurisdiction.")
    rationale: str = Field(..., description="A concise one\u2011sentence explanation of why this jurisdiction was chosen.")


class ChooseLegalEntityTypeOutput(BaseModel):
    """Pydantic model for choose_legal_entity_type node outputs."""
    entity_type: str = Field(..., description="The legal entity structure chosen for the hedge fund (e.g., LP, LLC, SICAV).")
    jurisdiction: str = Field(..., description="The jurisdiction where the fund vehicle is established.")
    explanation: str = Field(..., description="A concise, one\u2011sentence rationale for selecting this entity structure in the chosen jurisdiction.")


def choose_legal_entity_type(select_jurisdiction_input: SelectJurisdictionOutput, **kwargs) -> ChooseLegalEntityTypeOutput:
    """Identify legal structure for the hedge fund vehicle based on the chosen domicile, balancing regulatory fit, tax efficiency, and operational simplicity.

    Args:
        select_jurisdiction_input: Input from the 'select_jurisdiction' node.
        **kwargs: Additional keyword arguments.

    Returns:
        ChooseLegalEntityTypeOutput: Object containing outputs for this node.
    """
    # TODO: Implement this function

    # Return stub output with placeholder values
    return ChooseLegalEntityTypeOutput(
        entity_type="",
        jurisdiction="",
        explanation="",
    )