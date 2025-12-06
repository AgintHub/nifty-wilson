from ._develop_compliance_program.analyze_regulatory_requirements import analyze_regulatory_requirements
from ._develop_compliance_program.develop_trade_surveillance_policies import develop_trade_surveillance_policies
from ._develop_compliance_program.develop_record_keeping_policies import develop_record_keeping_policies
from ._develop_compliance_program.develop_risk_reporting_policies import develop_risk_reporting_policies
from ._develop_compliance_program.develop_regulatory_communications_policies import develop_regulatory_communications_policies
from ._develop_compliance_program.map_policies_to_requirements import map_policies_to_requirements
from ._develop_compliance_program.generate_compliance_program_documents import generate_compliance_program_documents

from pydantic import BaseModel, Field


# -- PRD --
# 1. BULLET: Review and analyze the regulatory requirements output from
#   identify_regulatory_requirements to understand the requirements for trade
#   surveillance, record keeping, risk reporting, and regulatory
#   communications.
#   Reason: This step allows us to understand the specific requirements and tailor our
#           compliance program accordingly.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Use data ingestion methods to gather regulatory requirements. Analyze and
#           parse the data to identify key requirements.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Develop a comprehensive compliance program incorporating policies for trade
#   surveillance, record keeping, risk reporting, and regulatory
#   communications.
#   Reason: This step ensures that our compliance program addresses all necessary
#           regulatory requirements.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Use policy development frameworks to create policies. Map each policy to
#           specific regulatory requirements.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Map each policy to specific regulatory requirements output from
#   identify_regulatory_requirements.
#   Reason: This step ensures that our compliance program meets all regulatory
#           requirements.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Use data mapping methods to link policy outputs to regulatory requirements.
#           Verify that each policy meets the corresponding requirement.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Output the comprehensive compliance program documents including trade
#   surveillance, record keeping, risk reporting, and regulatory
#   communications policies.
#   Reason: This step completes the compliance program creation process.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Use document generation methods to create the compliance program documents.
#           Include all relevant policies and mapped regulatory
#           requirements.
# -- END PRD --



class IdentifyRegulatoryRequirementsOutput(BaseModel):
    """Pydantic model for identify_regulatory_requirements node outputs."""
    regulatory_requirements: str = Field(..., description="List of key regulatory requirements")
    entity_type: str = Field(..., description="Type of entity for the trading firm (LLC, Corporation, etc.)")
    selected_markets: str = Field(..., description="List of selected primary markets")


class DevelopComplianceProgramOutput(BaseModel):
    """Pydantic model for develop_compliance_program node outputs."""
    compliance_program_documents: str = Field(..., description="List of documents included in the compliance program")
    trade_surveillance_policies: str = Field(..., description="List of trade surveillance policies implemented")
    recordKeepingPolicies: str = Field(..., description="List of record keeping policies implemented")
    riskReportingPolicies: str = Field(..., description="List of risk reporting policies implemented")
    regulatoryCommunicationsPolicies: str = Field(..., description="List of regulatory communications policies implemented")


def develop_compliance_program(identify_regulatory_requirements_input: IdentifyRegulatoryRequirementsOutput, **kwargs) -> DevelopComplianceProgramOutput:
    """Create policies and procedures for regulatory compliance

    Args:
        identify_regulatory_requirements_input: Input from the 'identify_regulatory_requirements' node.
        **kwargs: Additional keyword arguments.

    Returns:
        DevelopComplianceProgramOutput: Object containing outputs for this node.
    """
    # Review and analyze the regulatory requirements
    parsed_requirements: dict = analyze_regulatory_requirements(
        regulatory_requirements=identify_regulatory_requirements_input.regulatory_requirements,
        entity_type=identify_regulatory_requirements_input.entity_type,
        selected_markets=identify_regulatory_requirements_input.selected_markets
    )
    
    # Develop trade surveillance policies
    trade_surveillance_policies: str = develop_trade_surveillance_policies(
        requirements=parsed_requirements,
        entity_type=identify_regulatory_requirements_input.entity_type,
        markets=identify_regulatory_requirements_input.selected_markets
    )
    
    # Develop record keeping policies
    record_keeping_policies: str = develop_record_keeping_policies(
        requirements=parsed_requirements,
        entity_type=identify_regulatory_requirements_input.entity_type
    )
    
    # Develop risk reporting policies
    risk_reporting_policies: str = develop_risk_reporting_policies(
        requirements=parsed_requirements,
        markets=identify_regulatory_requirements_input.selected_markets
    )
    
    # Develop regulatory communications policies
    regulatory_communications_policies: str = develop_regulatory_communications_policies(
        requirements=parsed_requirements,
        entity_type=identify_regulatory_requirements_input.entity_type
    )
    
    # Map each policy to specific regulatory requirements
    policy_mapping: dict = map_policies_to_requirements(
        trade_surveillance=trade_surveillance_policies,
        record_keeping=record_keeping_policies,
        risk_reporting=risk_reporting_policies,
        regulatory_communications=regulatory_communications_policies,
        requirements=parsed_requirements
    )
    
    # Generate comprehensive compliance program documents
    compliance_documents: str = generate_compliance_program_documents(
        trade_surveillance_policies=trade_surveillance_policies,
        record_keeping_policies=record_keeping_policies,
        risk_reporting_policies=risk_reporting_policies,
        regulatory_communications_policies=regulatory_communications_policies,
        policy_mapping=policy_mapping
    )
    
    return DevelopComplianceProgramOutput(
        compliance_program_documents=compliance_documents,
        trade_surveillance_policies=trade_surveillance_policies,
        recordKeepingPolicies=record_keeping_policies,
        riskReportingPolicies=risk_reporting_policies,
        regulatoryCommunicationsPolicies=regulatory_communications_policies
    )