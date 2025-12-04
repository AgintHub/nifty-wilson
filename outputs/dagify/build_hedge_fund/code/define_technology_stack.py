# -- PRD --
# 1. BULLET: Parse the parent node’s trade_lifecycle_steps into a local array, preserving
#   order to maintain alignment with responsible parties.
#   Reason: The output must reflect the exact sequence defined in the operations
#           workflow.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Use a simple list comprehension or copy operation; no transformation needed
#           beyond preserving sequence.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Create a mapping dictionary that pairs each lifecycle step with its standard
#   industry technology counterpart (e.g., Idea Generation → Strategy
#   Analytics Platform, Order Entry → OMS, Execution → EMS, Confirmation →
#   Confirmation System, Settlement → Custody & Clearing Platform,
#   Reconciliation → Reconciliation Engine).
#   Reason: Standardized pairings reduce ambiguity and ensure consistency with common
#           hedge‑fund practice.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Define a static map in code; validate against a reference guide such as the
#           Hedge Fund Operations Playbook (HFOP) or proprietary firm
#           templates.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: For each step, verify that the selected tech component satisfies the risk
#   control requirements from the design_risk_management_framework node
#   (e.g., risk limits, VaR calculations).
#   Reason: Technology must support the quantitative controls defined elsewhere to
#           avoid compliance gaps.
#   Impact: HIGH
#   Complexity: HIGH
#   Method: Cross‑reference risk_controls list; flag any mismatch; adjust component
#           selection to include risk‑monitoring modules (e.g., embed risk
#           engine into OMS).
# 
# -----------------------------------------------------------------------------
# 4. BULLET: If the parent node’s responsible_party for a step is an external provider
#   (e.g., Prime Broker for Execution), append a note in tech_components
#   indicating that the component will be accessed via the provider’s
#   interface rather than an internal installation.
#   Reason: Clarifies ownership and integration points for later implementation.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Append a string qualifier such as 'PrimeBroker EMS' to the component entry.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Generate two aligned lists: ops_steps (from the parsed workflow) and
#   tech_components (from the mapping), ensuring array lengths match exactly.
#   Reason: The output schema demands parallel arrays; any mismatch triggers downstream
#           errors.
#   Impact: HIGH
#   Complexity: LOW
#   Method: After mapping, perform a length check; raise an exception or log error if
#           lengths diverge.
# 
# -----------------------------------------------------------------------------
# 6. BULLET: Normalize component names to a consistent naming convention (e.g.,
#   Vendor‑Specific or Standardized Nomenclature) to aid in procurement and
#   vendor management.
#   Reason: Consistent naming avoids confusion during vendor selection and contract
#           negotiations.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Apply a title‑case transformation; if vendor is unknown, use a placeholder
#           like 'Custom OMS'.
# 
# -----------------------------------------------------------------------------
# 7. BULLET: Output the final two lists in JSON format, matching the defined output
#   structure, and include a brief comment or placeholder for future
#   versioning.
#   Reason: Maintains compatibility with downstream nodes and allows easy integration
#           with CI/CD pipelines.
#   Impact: LOW
#   Complexity: LOW
#   Method: Serialize using a JSON library; wrap lists under their respective keys.
# 
# -----------------------------------------------------------------------------
# 8. BULLET: Validate the output against a unit test that compares it against an expected
#   reference for a sample workflow (e.g., Idea Generation, Order Entry,
#   Execution, Confirmation, Settlement, Reconciliation).
#   Reason: Ensures correctness and guards against regressions in future edits.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Create a pytest function that asserts equality of ops_steps and
#           tech_components to predetermined values.
# 
# -----------------------------------------------------------------------------
# 9. BULLET: Document any assumptions about vendor availability or proprietary solutions,
#   noting them in a side comment block for future reference.
#   Reason: Transparency supports audit trails and future upgrades.
#   Impact: LOW
#   Complexity: LOW
#   Method: Embed comments in the code or add metadata key in output JSON.
# -- END PRD --

from pydantic import BaseModel, Field
from typing import List


class DraftOperationsWorkflowOutput(BaseModel):
    """Pydantic model for draft_operations_workflow node outputs."""
    trade_lifecycle_steps: str = Field(..., description="Ordered list of trade lifecycle steps: idea generation, order entry, execution, confirmation, settlement, reconciliation.")
    responsible_parties: str = Field(..., description="Primary responsible party for each lifecycle step, aligned with trade_lifecycle_steps. Use values like 'GP', 'Prime Broker', 'Fund Administrator', 'Internal Ops'.")


class DefineTechnologyStackOutput(BaseModel):
    """Pydantic model for define_technology_stack node outputs."""
    ops_steps: List[str] = Field(..., description="List of operational steps in the trade lifecycle (e.g., idea generation, order entry, execution, confirmation, settlement, reconciliation).")
    tech_components: List[str] = Field(..., description="Corresponding technology component for each operational step (e.g., OMS, EMS, risk management system). The order aligns with ops_steps.")


def define_technology_stack(draft_operations_workflow_input: DraftOperationsWorkflowOutput, **kwargs) -> DefineTechnologyStackOutput:
    """Specify technology tools supporting operations.

    Args:
        draft_operations_workflow_input: Input from the 'draft_operations_workflow' node.
        **kwargs: Additional keyword arguments.

    Returns:
        DefineTechnologyStackOutput: Object containing outputs for this node.
    """
    # TODO: Implement this function

    # Return stub output with placeholder values
    return DefineTechnologyStackOutput(
        ops_steps=[],
        tech_components=[],
    )