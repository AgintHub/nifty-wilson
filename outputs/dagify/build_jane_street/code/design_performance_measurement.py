from ._design_performance_measurement.define_performance_metrics import define_performance_metrics
from ._design_performance_measurement.create_measurement_framework import create_measurement_framework
from ._design_performance_measurement.enhance_settlement_with_performance_tracking import enhance_settlement_with_performance_tracking
from ._design_performance_measurement.integrate_performance_measurement_with_pl import integrate_performance_measurement_with_pl
from ._design_performance_measurement.optimize_monitoring_frequency_for_performance import optimize_monitoring_frequency_for_performance
from ._design_performance_measurement.add_performance_validation_to_reconciliation import add_performance_validation_to_reconciliation
from ._design_performance_measurement.create_performance_reporting_schedule import create_performance_reporting_schedule
from ._design_performance_measurement.define_performance_measurement_roles import define_performance_measurement_roles

from pydantic import BaseModel, Field


class EstablishOperationalWorkflowsOutput(BaseModel):
    """Pydantic model for establish_operational_workflows node outputs."""
    trade_settlement_process: str = Field(..., description="Description of the trade settlement process")
    pl_calculation_method: str = Field(..., description="Method used for calculating P&L")
    risk_monitoring_frequency: str = Field(..., description="Frequency of risk monitoring")
    position_reconciliation_procedure: str = Field(..., description="Procedure for position reconciliation")
    regulatory_reporting_schedule: str = Field(..., description="Schedule for regulatory reporting")
    roles_and_responsibilities: str = Field(..., description="List of roles and responsibilities for operational workflows")


class DesignPerformanceMeasurementOutput(BaseModel):
    """Pydantic model for design_performance_measurement node outputs."""
    trade_settlement_process: str = Field(..., description="Description of the trade settlement process")
    pl_calculation_method: str = Field(..., description="Method used for calculating P&L")
    risk_monitoring_frequency: str = Field(..., description="Frequency of risk monitoring")
    position_reconciliation_procedure: str = Field(..., description="Procedure for position reconciliation")
    regulatory_reporting_schedule: str = Field(..., description="Schedule for regulatory reporting")
    roles_and_responsibilities: str = Field(..., description="List of roles and responsibilities for operational workflows")


def design_performance_measurement(establish_operational_workflows_input: EstablishOperationalWorkflowsOutput, **kwargs) -> DesignPerformanceMeasurementOutput:
    """Create systems for tracking and analyzing trading performance

    Args:
        establish_operational_workflows_input: Input from the 'establish_operational_workflows' node.
        **kwargs: Additional keyword arguments.

    Returns:
        DesignPerformanceMeasurementOutput: Object containing outputs for this node.
    """
    # Design performance measurement systems based on established operational workflows
    performance_metrics: list = define_performance_metrics(
        pl_method=establish_operational_workflows_input.pl_calculation_method,
        risk_frequency=establish_operational_workflows_input.risk_monitoring_frequency
    )
    
    measurement_framework: dict = create_measurement_framework(
        metrics=performance_metrics,
        settlement_process=establish_operational_workflows_input.trade_settlement_process
    )
    
    enhanced_settlement_process: str = enhance_settlement_with_performance_tracking(
        base_process=establish_operational_workflows_input.trade_settlement_process,
        framework=measurement_framework
    )
    
    performance_enabled_pl_method: str = integrate_performance_measurement_with_pl(
        pl_method=establish_operational_workflows_input.pl_calculation_method,
        measurement_system=measurement_framework
    )
    
    performance_monitoring_frequency: str = optimize_monitoring_frequency_for_performance(
        current_frequency=establish_operational_workflows_input.risk_monitoring_frequency,
        performance_requirements=performance_metrics
    )
    
    enhanced_reconciliation: str = add_performance_validation_to_reconciliation(
        base_procedure=establish_operational_workflows_input.position_reconciliation_procedure,
        performance_framework=measurement_framework
    )
    
    performance_reporting_schedule: str = create_performance_reporting_schedule(
        regulatory_schedule=establish_operational_workflows_input.regulatory_reporting_schedule,
        performance_metrics=performance_metrics
    )
    
    performance_roles: str = define_performance_measurement_roles(
        base_roles=establish_operational_workflows_input.roles_and_responsibilities,
        measurement_framework=measurement_framework
    )
    
    return DesignPerformanceMeasurementOutput(
        trade_settlement_process=enhanced_settlement_process,
        pl_calculation_method=performance_enabled_pl_method,
        risk_monitoring_frequency=performance_monitoring_frequency,
        position_reconciliation_procedure=enhanced_reconciliation,
        regulatory_reporting_schedule=performance_reporting_schedule,
        roles_and_responsibilities=performance_roles
    )