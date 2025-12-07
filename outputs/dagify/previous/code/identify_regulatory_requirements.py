from ._identify_regulatory_requirements.format_markets_list import format_markets_list
from ._identify_regulatory_requirements.conduct_regulatory_research import conduct_regulatory_research
from ._identify_regulatory_requirements.map_regulatory_requirements import map_regulatory_requirements
from ._identify_regulatory_requirements.document_regulatory_obligations import document_regulatory_obligations

from pydantic import BaseModel, Field
from typing import List


# -- PRD --
# 1. BULLET: Use the output from 'choose_legal_structure' to determine the type of entity
#   for the trading firm
#   Reason: The legal entity structure will impact the regulatory requirements for the
#           trading firm
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Select the 'entity_type' value from the 'choose_legal_structure' output
#           structure
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Use the output from 'select_primary_markets' to determine the selected
#   primary markets
#   Reason: The selected primary markets will impact the regulatory requirements for
#           the trading firm
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Select the 'selected_markets' value from the 'select_primary_markets'
#           output structure
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Use regulatory research and data to map out the key regulatory requirements
#   for the trading firm
#   Reason: Regulatory requirements can be complex and vary by jurisdiction
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Consult with regulatory experts and conduct research to identify the key
#           regulatory requirements
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Document the key regulatory requirements and their corresponding obligations
#   Reason: Compliance obligations must be clearly understood and documented
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Create a comprehensive report outlining the key regulatory requirements and
#           their corresponding obligations
# -- END PRD --



class ChooseLegalStructureOutput(BaseModel):
    """Pydantic model for choose_legal_structure node outputs."""
    legal_entity: str = Field(..., description="The chosen legal entity structure (LLC, Corporation, Partnership)")
    tax_implications: str = Field(..., description="Brief description of tax implications")
    liability_protection: str = Field(..., description="Brief description of liability protection")
    operational_flexibility: str = Field(..., description="Brief description of operational flexibility")
    rationale: str = Field(..., description="Rationale for the chosen legal structure")


class SelectPrimaryMarketsOutput(BaseModel):
    """Pydantic model for select_primary_markets node outputs."""
    primary_markets: List[str] = Field(..., description="List of selected primary markets and exchanges")
    market_selection_reasoning: str = Field(..., description="Rationale for selecting each primary market and exchange")
    liquidity_risk_assessment: str = Field(..., description="Assessment of liquidity risk in each selected market")
    regulatory_environment: str = Field(..., description="Overview of regulatory requirements and implications for each selected market")
    competitive_landscape: str = Field(..., description="Analysis of competitive landscape in each selected market")


class IdentifyRegulatoryRequirementsOutput(BaseModel):
    """Pydantic model for identify_regulatory_requirements node outputs."""
    regulatory_requirements: str = Field(..., description="List of key regulatory requirements")
    entity_type: str = Field(..., description="Type of entity for the trading firm (LLC, Corporation, etc.)")
    selected_markets: str = Field(..., description="List of selected primary markets")


def identify_regulatory_requirements(choose_legal_structure_input: ChooseLegalStructureOutput, select_primary_markets_input: SelectPrimaryMarketsOutput, **kwargs) -> IdentifyRegulatoryRequirementsOutput:
    """Map out regulatory registrations and compliance obligations

    Args:
        choose_legal_structure_input: Input from the 'choose_legal_structure' node.
        select_primary_markets_input: Input from the 'select_primary_markets' node.
        **kwargs: Additional keyword arguments.

    Returns:
        IdentifyRegulatoryRequirementsOutput: Object containing outputs for this node.
    """
    # Extract entity type from choose_legal_structure output
    entity_type: str = choose_legal_structure_input.legal_entity
    
    # Extract selected markets from select_primary_markets output
    selected_markets_list: List[str] = select_primary_markets_input.primary_markets
    selected_markets: str = format_markets_list(markets=selected_markets_list)
    
    # Conduct regulatory research based on entity type and markets
    regulatory_data: dict = conduct_regulatory_research(
        entity_type=entity_type,
        markets=selected_markets_list
    )
    
    # Map regulatory requirements for the trading firm
    mapped_requirements: dict = map_regulatory_requirements(
        entity_type=entity_type,
        markets=selected_markets_list,
        regulatory_data=regulatory_data
    )
    
    # Document the key regulatory requirements and obligations
    formatted_requirements: str = document_regulatory_obligations(
        requirements=mapped_requirements,
        entity_type=entity_type,
        markets=selected_markets_list
    )
    
    return IdentifyRegulatoryRequirementsOutput(
        regulatory_requirements=formatted_requirements,
        entity_type=entity_type,
        selected_markets=selected_markets
    )