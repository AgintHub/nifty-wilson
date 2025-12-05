# -- PRD --
# 1. BULLET: Extract the entity type from the parent node choose_legal_entity_type and use
#   it to decide whether a formal Board of Directors is required.
#   Reason: The need for a Board is contingent on the legal structure (e.g., an LLC may
#           not have a board while an LP typically has one).
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Parse the 'entity_type' field; if it is 'LP' or 'LLC', set
#           board_needed=True; otherwise board_needed=False.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Create an ordered list of role names starting with GP and Investment Manager,
#   then append Board if board_needed is True, followed by Compliance Officer
#   and Advisory Committee, ensuring the list does not exceed five items.
#   Reason: Maintaining a predictable order facilitates mapping duties to roles and
#           ensures compliance with the 5‑role limit.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Instantiate role_names = ['GP', 'Investment Manager']; if board_needed:
#           role_names.append('Board'); role_names.extend(['Compliance
#           Officer', 'Advisory Committee']); truncate to first 5 elements.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Define a concise one‑sentence duty for each role using domain‑specific
#   language: GP – oversees overall fund strategy; Investment Manager –
#   executes trades and manages portfolio risk; Board – approves major
#   strategy shifts and oversight; Compliance Officer – ensures regulatory
#   compliance; Advisory Committee – provides industry insights.
#   Reason: Clear, brief duties align with typical hedge fund governance practices and
#           satisfy the prompt’s one‑sentence constraint.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Map role names to duty strings via a dictionary; then produce role_duties
#           list in the same order as role_names.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Validate that the lengths of role_names and role_duties match; if not,
#   truncate or adjust duties accordingly.
#   Reason: Ensuring output consistency prevents downstream errors in later nodes that
#           may consume this data.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Check len(role_names) == len(role_duties); if mismatch, raise an error or
#           log warning and align them.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Return the role_names and role_duties arrays exactly as specified in the
#   output structure, with no extraneous whitespace or formatting.
#   Reason: Strict adherence to output schema guarantees seamless integration with
#           downstream nodes.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Serialize lists into JSON-compatible arrays; trim strings; ensure no
#           newlines inside duty descriptions.
# -- END PRD --

from pydantic import BaseModel, Field
from typing import List


class ChooseLegalEntityTypeOutput(BaseModel):
    """Pydantic model for choose_legal_entity_type node outputs."""
    entity_type: str = Field(..., description="The legal entity structure chosen for the hedge fund (e.g., LP, LLC, SICAV).")
    jurisdiction: str = Field(..., description="The jurisdiction where the fund vehicle is established.")
    explanation: str = Field(..., description="A concise, one\u2011sentence rationale for selecting this entity structure in the chosen jurisdiction.")


class OutlineGovernanceStructureOutput(BaseModel):
    """Pydantic model for outline_governance_structure node outputs."""
    role_names: List[str] = Field(..., description="Names of governance roles (e.g., GP, investment manager, board) up to five.")
    role_duties: List[str] = Field(..., description="One\u2011line duties for each role, corresponding to role_names in order.")


def outline_governance_structure(choose_legal_entity_type_input: ChooseLegalEntityTypeOutput, **kwargs) -> OutlineGovernanceStructureOutput:
    """Define internal governance roles and duties for the hedge fund, limited to a maximum of five roles. Each role should have a concise one‑sentence duty description.

    Args:
        choose_legal_entity_type_input: Input from the 'choose_legal_entity_type' node.
        **kwargs: Additional keyword arguments.

    Returns:
        OutlineGovernanceStructureOutput: Object containing outputs for this node.
    """
    # TODO: Implement this function

    # Return stub output with placeholder values
    return OutlineGovernanceStructureOutput(
        role_names=[],
        role_duties=[],
    )