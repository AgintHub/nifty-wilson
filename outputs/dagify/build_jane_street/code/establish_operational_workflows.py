from ._establish_operational_workflows.map_trade_settlement_workflow import map_trade_settlement_workflow
from ._establish_operational_workflows.create_settlement_process_documentation import create_settlement_process_documentation
from ._establish_operational_workflows.develop_pl_calculation_method import develop_pl_calculation_method
from ._establish_operational_workflows.create_risk_monitoring_framework import create_risk_monitoring_framework
from ._establish_operational_workflows.establish_position_reconciliation_procedure import establish_position_reconciliation_procedure
from ._establish_operational_workflows.create_regulatory_reporting_schedule import create_regulatory_reporting_schedule
from ._establish_operational_workflows.define_operational_roles_and_responsibilities import define_operational_roles_and_responsibilities

from pydantic import BaseModel, Field
from typing import List


# -- PRD --
# 1. BULLET: Define the trade settlement process, including the steps involved and the
#   systems used for trade execution and settlement.
#   Reason: A clear understanding of the trade settlement process is necessary to
#           ensure accurate and timely settlement of trades.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Use a structured approach to identify and document the trade settlement
#           process, including the use of workflow diagrams and process
#           mapping tools.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Determine the P&L calculation method, including the frequency of P&L
#   reporting and the methodology used for calculating P&L.
#   Reason: An accurate and timely P&L calculation is essential for risk management and
#           performance evaluation.
#   Impact: HIGH
#   Complexity: HIGH
#   Method: Develop and document a P&L calculation methodology that takes into account
#           all relevant financial and trading metrics, including but not
#           limited to, mark-to-market valuations, dividends, and interest
#           income.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Establish a risk monitoring frequency, including the schedule for risk
#   reporting and the parameters used for risk analysis.
#   Reason: Continuous risk monitoring is necessary to ensure the timely identification
#           and mitigation of potential risks.
#   Impact: HIGH
#   Complexity: HIGH
#   Method: Develop and document a risk monitoring framework that includes regular risk
#           reporting, stress testing, and scenario analysis, using tools
#           such as VaR models, scenario analysis, and stress testing.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Define the position reconciliation procedure, including the schedule for
#   position reconciliation and the methodology used for identifying and
#   resolving reconciliation discrepancies.
#   Reason: Accurate and timely position reconciliation is necessary to ensure
#           compliance with regulatory requirements and maintain accurate
#           trading records.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Develop and document a position reconciliation process that includes
#           regular position reporting, reconciliation analysis, and
#           discrepancy resolution, using tools such as automated position
#           reconciliation systems and manual reconciliation processes.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Establish a regulatory reporting schedule, including the frequency of
#   regulatory reporting and the content of regulatory reports.
#   Reason: Timely and accurate regulatory reporting is necessary to ensure compliance
#           with regulatory requirements and maintain a positive
#           relationship with regulatory authorities.
#   Impact: HIGH
#   Complexity: HIGH
#   Method: Develop and document a regulatory reporting framework that includes regular
#           reporting of trading activity, position holdings, and other
#           relevant financial metrics, using tools such as regulatory
#           reporting software and manual reporting processes.
# 
# -----------------------------------------------------------------------------
# 6. BULLET: Define the roles and responsibilities for operational workflows, including
#   the job descriptions, performance metrics, and training requirements for
#   operational personnel.
#   Reason: Clear and well-defined roles and responsibilities are necessary to ensure
#           effective and efficient operation of daily workflows.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Develop and document job descriptions, performance metrics, and training
#           requirements for operational personnel, using tools such as job
#           description templates, performance metrics frameworks, and
#           training manuals.
# -- END PRD --



class DesignRiskManagementFrameworkOutput(BaseModel):
    """Pydantic model for design_risk_management_framework node outputs."""
    position_size_limits: int = Field(..., description="List of position size limits by asset type")
    portfolio_concentration_metrics: float = Field(..., description="List of portfolio concentration metrics")
    var_limit: float = Field(..., description="Value-at-Risk (VaR) limit")
    drawdown_limit: float = Field(..., description="Drawdown limit")
    pre_trade_risk_measures: str = Field(..., description="List of pre-trade risk measures")
    post_trade_risk_measures: str = Field(..., description="List of post-trade risk measures")


class IdentifyPrimeBrokeragePartnersOutput(BaseModel):
    """Pydantic model for identify_prime_brokerage_partners node outputs."""
    prime_brokerage_partners: List[str] = Field(..., description="List of potential prime brokerage partners")
    execution_venues: List[str] = Field(..., description="List of potential execution venues")


class DevelopComplianceProgramOutput(BaseModel):
    """Pydantic model for develop_compliance_program node outputs."""
    compliance_program_documents: str = Field(..., description="List of documents included in the compliance program")
    trade_surveillance_policies: str = Field(..., description="List of trade surveillance policies implemented")
    recordKeepingPolicies: str = Field(..., description="List of record keeping policies implemented")
    riskReportingPolicies: str = Field(..., description="List of risk reporting policies implemented")
    regulatoryCommunicationsPolicies: str = Field(..., description="List of regulatory communications policies implemented")


class EstablishOperationalWorkflowsOutput(BaseModel):
    """Pydantic model for establish_operational_workflows node outputs."""
    trade_settlement_process: str = Field(..., description="Description of the trade settlement process")
    pl_calculation_method: str = Field(..., description="Method used for calculating P&L")
    risk_monitoring_frequency: str = Field(..., description="Frequency of risk monitoring")
    position_reconciliation_procedure: str = Field(..., description="Procedure for position reconciliation")
    regulatory_reporting_schedule: str = Field(..., description="Schedule for regulatory reporting")
    roles_and_responsibilities: str = Field(..., description="List of roles and responsibilities for operational workflows")


def establish_operational_workflows(design_risk_management_framework_input: DesignRiskManagementFrameworkOutput, identify_prime_brokerage_partners_input: IdentifyPrimeBrokeragePartnersOutput, develop_compliance_program_input: DevelopComplianceProgramOutput, **kwargs) -> EstablishOperationalWorkflowsOutput:
    """Design daily operational processes and procedures

    Args:
        design_risk_management_framework_input: Input from the 'design_risk_management_framework' node.
        identify_prime_brokerage_partners_input: Input from the 'identify_prime_brokerage_partners' node.
        develop_compliance_program_input: Input from the 'develop_compliance_program' node.
        **kwargs: Additional keyword arguments.

    Returns:
        EstablishOperationalWorkflowsOutput: Object containing outputs for this node.
    """
    # Define trade settlement process with workflow mapping
    settlement_workflow_steps: List[str] = map_trade_settlement_workflow(
        prime_brokers=identify_prime_brokerage_partners_input.prime_brokerage_partners,
        execution_venues=identify_prime_brokerage_partners_input.execution_venues
    )
    trade_settlement_process: str = create_settlement_process_documentation(
        workflow_steps=settlement_workflow_steps
    )
    
    # Develop P&L calculation methodology
    pl_methodology: str = develop_pl_calculation_method(
        var_limit=design_risk_management_framework_input.var_limit,
        drawdown_limit=design_risk_management_framework_input.drawdown_limit,
        portfolio_metrics=design_risk_management_framework_input.portfolio_concentration_metrics
    )
    
    # Establish risk monitoring framework and frequency
    risk_framework: str = create_risk_monitoring_framework(
        pre_trade_measures=design_risk_management_framework_input.pre_trade_risk_measures,
        post_trade_measures=design_risk_management_framework_input.post_trade_risk_measures,
        var_limit=design_risk_management_framework_input.var_limit
    )
    
    # Define position reconciliation procedures
    reconciliation_process: str = establish_position_reconciliation_procedure(
        compliance_docs=develop_compliance_program_input.compliance_program_documents,
        record_keeping_policies=develop_compliance_program_input.recordKeepingPolicies
    )
    
    # Create regulatory reporting schedule
    reporting_schedule: str = create_regulatory_reporting_schedule(
        risk_reporting_policies=develop_compliance_program_input.riskReportingPolicies,
        regulatory_communications=develop_compliance_program_input.regulatoryCommunicationsPolicies,
        trade_surveillance=develop_compliance_program_input.trade_surveillance_policies
    )
    
    # Define roles and responsibilities for operational personnel
    operational_roles: str = define_operational_roles_and_responsibilities(
        settlement_process=trade_settlement_process,
        pl_method=pl_methodology,
        risk_framework=risk_framework,
        reconciliation_procedure=reconciliation_process
    )
    
    return EstablishOperationalWorkflowsOutput(
        trade_settlement_process=trade_settlement_process,
        pl_calculation_method=pl_methodology,
        risk_monitoring_frequency=risk_framework,
        position_reconciliation_procedure=reconciliation_process,
        regulatory_reporting_schedule=reporting_schedule,
        roles_and_responsibilities=operational_roles
    )