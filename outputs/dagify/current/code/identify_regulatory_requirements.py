# -- PRD --
# 1. BULLET: Parse the parent node's output to extract the legal entity type and
#   jurisdiction, normalizing the jurisdiction string to a canonical form
#   (e.g., 'United States' → 'US', 'United Kingdom' → 'UK') and converting
#   the entity type to a standard abbreviation (e.g., 'Limited Liability
#   Company' → 'LLC').
#   Reason: Accurate key extraction ensures that subsequent lookup operations target
#           the correct regulatory mapping table, preventing misspellings
#           and case‑sensitivity errors that would otherwise lead to
#           missing or incorrect filings.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Implement a helper function that trims whitespace, converts to lowercase,
#           and applies a predefined mapping dictionary for known
#           jurisdiction names and entity type synonyms. Log any unknown
#           values for audit.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Use a pre‑defined lookup table that maps each combination of jurisdiction and
#   entity type to a tuple of (filing_name, governing_body). The table should
#   cover the most common structures (LP, LLC, SICAV, partnership) and
#   jurisdictions (US, UK, Cayman, Luxembourg, Delaware). For example, in the
#   US an LLC or LP is required to register with the SEC via Form ADV; in the
#   UK a UK‑based LP must register with the FCA; in Cayman a fund must
#   register with the Cayman Islands Monetary Authority and may need to file
#   with the Cayman Islands Securities Investment Business Licensing
#   Authority if trading securities; in Luxembourg a SICAV must register with
#   the CSSF.
#   Reason: Centralizing regulatory requirements in a lookup table allows for
#           deterministic and repeatable outputs, making the PRD easier to
#           maintain and extend when new jurisdictions or entity types are
#           added.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Create a nested dictionary such as
#           `REG_REQUIREMENTS[jurisdiction][entity_type] = {'filing': 'SEC
#           Form ADV', 'body': 'SEC'}`. Populate this dictionary with at
#           least 8–10 jurisdiction–entity combinations. Include a default
#           fallback that returns empty lists with a warning if the
#           combination is not found.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Generate the final output lists by iterating over the lookup result for the
#   identified combination. Return two aligned lists: `filing_names`
#   containing the filing titles and `governing_bodies` containing the
#   corresponding regulatory authority names. If the lookup returns no data,
#   emit empty lists and optionally log an error to alert the user of missing
#   regulatory information.
#   Reason: Aligning the two output arrays ensures downstream nodes (e.g.,
#           design_compliance_program) can map each filing to a compliance
#           requirement without ambiguity.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Use a simple list comprehension: `filings = [entry['filing'] for entry in
#           results]` and `bodies = [entry['body'] for entry in results]`.
#           Wrap in a try/except block to capture and log any unexpected
#           key errors.
# -- END PRD --

from pydantic import BaseModel, Field
from typing import List


class ChooseLegalEntityTypeOutput(BaseModel):
    """Pydantic model for choose_legal_entity_type node outputs."""
    entity_type: str = Field(..., description="The legal entity structure chosen for the hedge fund (e.g., LP, LLC, SICAV).")
    jurisdiction: str = Field(..., description="The jurisdiction where the fund vehicle is established.")
    explanation: str = Field(..., description="A concise, one\u2011sentence rationale for selecting this entity structure in the chosen jurisdiction.")


class IdentifyRegulatoryRequirementsOutput(BaseModel):
    """Pydantic model for identify_regulatory_requirements node outputs."""
    filing_names: List[str] = Field(..., description="List of required filings or registrations for the selected legal entity and jurisdiction.")
    governing_bodies: List[str] = Field(..., description="List of governing body names associated with each filing or registration.")


def identify_regulatory_requirements(choose_legal_entity_type_input: ChooseLegalEntityTypeOutput, **kwargs) -> IdentifyRegulatoryRequirementsOutput:
    """Outline key regulatory filings and registrations.

    Args:
        choose_legal_entity_type_input: Input from the 'choose_legal_entity_type' node.
        **kwargs: Additional keyword arguments.

    Returns:
        IdentifyRegulatoryRequirementsOutput: Object containing outputs for this node.
    """
    # TODO: Implement this function

    # Return stub output with placeholder values
    return IdentifyRegulatoryRequirementsOutput(
        filing_names=[],
        governing_bodies=[],
    )