# -- PRD --
# 1. BULLET: 1. Verify that the parent node `choose_legal_entity_type` has executed
#   successfully and its output is available in the workflow context.
#   Reason: The node depends on legal entity selection; ensuring its output prevents
#           downstream failures.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Check the workflow state for a key named `choose_legal_entity_type`; if
#           missing, throw a descriptive error and halt execution.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: 2. Create a static list of service provider types exactly as specified in the
#   prompt: ['Prime Broker', 'Fund Administrator', 'Auditor', 'Legal
#   Counsel', 'Compliance Consultant', 'Custodian'].
#   Reason: The prompt requires a hard‑coded checklist without descriptive text; using
#           a static list guarantees consistency.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Instantiate the list in code, ensuring each element is a string with
#           title‑case formatting to match typical provider names.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: 3. Return the list as the value for the `service_providers` output field,
#   confirming the data type matches `PrimitiveType.LIST_STR`.
#   Reason: Proper type matching ensures downstream nodes consume the data without
#           conversion errors.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Assign the static list to a dictionary key `service_providers` and
#           serialize it if required by the workflow engine.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: 4. Include basic validation that the list length is exactly six elements,
#   matching the expected provider categories.
#   Reason: This guards against accidental changes to the hard‑coded list that could
#           break downstream logic.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Assert that `len(service_providers) == 6`; if not, raise a warning or
#           error.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: 5. Log the generated provider checklist for audit purposes, including a
#   timestamp and parent node reference.
#   Reason: Logging aids debugging and audit trails, especially when the list is used
#           by subsequent cost estimation and operations workflow nodes.
#   Impact: LOW
#   Complexity: LOW
#   Method: Use the workflow's logging facility to record the provider list and a
#           reference to the parent node.
# -- END PRD --

from pydantic import BaseModel, Field
from typing import List


class ChooseLegalEntityTypeOutput(BaseModel):
    """Pydantic model for choose_legal_entity_type node outputs."""
    entity_type: str = Field(..., description="The legal entity structure chosen for the hedge fund (e.g., LP, LLC, SICAV).")
    jurisdiction: str = Field(..., description="The jurisdiction where the fund vehicle is established.")
    explanation: str = Field(..., description="A concise, one\u2011sentence rationale for selecting this entity structure in the chosen jurisdiction.")


class ListServiceProvidersOutput(BaseModel):
    """Pydantic model for list_service_providers node outputs."""
    service_providers: List[str] = Field(..., description="Checklist of mandatory third-party service provider categories.")


def list_service_providers(choose_legal_entity_type_input: ChooseLegalEntityTypeOutput, **kwargs) -> ListServiceProvidersOutput:
    """Enumerate required third-party service provider categories.

    Args:
        choose_legal_entity_type_input: Input from the 'choose_legal_entity_type' node.
        **kwargs: Additional keyword arguments.

    Returns:
        ListServiceProvidersOutput: Object containing outputs for this node.
    """
    # TODO: Implement this function

    # Return stub output with placeholder values
    return ListServiceProvidersOutput(
        service_providers=[],
    )