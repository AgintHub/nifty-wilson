from ._choose_legal_structure.parse_business_requirements import parse_business_requirements
from ._choose_legal_structure.analyze_trading_firm_needs import analyze_trading_firm_needs
from ._choose_legal_structure.evaluate_legal_structures import evaluate_legal_structures
from ._choose_legal_structure.select_optimal_entity import select_optimal_entity
from ._choose_legal_structure.generate_tax_implications import generate_tax_implications
from ._choose_legal_structure.generate_liability_protection import generate_liability_protection
from ._choose_legal_structure.generate_operational_flexibility import generate_operational_flexibility
from ._choose_legal_structure.generate_structure_rationale import generate_structure_rationale

from pydantic import BaseModel, Field


class ChooseLegalStructureOutput(BaseModel):
    """Pydantic model for choose_legal_structure node outputs."""
    legal_entity: str = Field(..., description="The chosen legal entity structure (LLC, Corporation, Partnership)")
    tax_implications: str = Field(..., description="Brief description of tax implications")
    liability_protection: str = Field(..., description="Brief description of liability protection")
    operational_flexibility: str = Field(..., description="Brief description of operational flexibility")
    rationale: str = Field(..., description="Rationale for the chosen legal structure")


def choose_legal_structure(general_input: str, **kwargs) -> ChooseLegalStructureOutput:
    """Determine optimal corporate structure for the trading firm

    Args:
        general_input: General input string for the root node.
        **kwargs: Additional keyword arguments.

    Returns:
        ChooseLegalStructureOutput: Object containing outputs for this node.
    """
    # Parse and extract business requirements from input
    business_requirements: dict = parse_business_requirements(input_text=general_input, **kwargs)
    
    # Analyze trading firm characteristics and needs
    firm_characteristics: dict = analyze_trading_firm_needs(requirements=business_requirements)
    
    # Evaluate legal structure options against requirements
    structure_analysis: dict = evaluate_legal_structures(
        characteristics=firm_characteristics,
        options=["LLC", "Corporation", "Partnership"]
    )
    
    # Select optimal legal entity based on analysis
    optimal_entity: str = select_optimal_entity(analysis=structure_analysis)
    
    # Generate detailed implications for chosen structure
    tax_details: str = generate_tax_implications(entity=optimal_entity, characteristics=firm_characteristics)
    liability_details: str = generate_liability_protection(entity=optimal_entity)
    flexibility_details: str = generate_operational_flexibility(entity=optimal_entity)
    
    # Create rationale for the decision
    decision_rationale: str = generate_structure_rationale(
        chosen_entity=optimal_entity,
        analysis=structure_analysis,
        requirements=business_requirements
    )
    
    return ChooseLegalStructureOutput(
        legal_entity=optimal_entity,
        tax_implications=tax_details,
        liability_protection=liability_details,
        operational_flexibility=flexibility_details,
        rationale=decision_rationale
    )