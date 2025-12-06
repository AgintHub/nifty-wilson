from ._integrate_refined_proposals_into_framework.initialize_integration_log import initialize_integration_log
from ._integrate_refined_proposals_into_framework.validate_equation_syntax import validate_equation_syntax
from ._integrate_refined_proposals_into_framework.get_syntax_validation_error import get_syntax_validation_error
from ._integrate_refined_proposals_into_framework.log_validation_failure import log_validation_failure
from ._integrate_refined_proposals_into_framework.validate_against_constraints import validate_against_constraints
from ._integrate_refined_proposals_into_framework.log_constraint_failure import log_constraint_failure
from ._integrate_refined_proposals_into_framework.build_symbolic_model import build_symbolic_model
from ._integrate_refined_proposals_into_framework.get_model_build_error import get_model_build_error
from ._integrate_refined_proposals_into_framework.log_build_failure import log_build_failure
from ._integrate_refined_proposals_into_framework.generate_unique_model_id import generate_unique_model_id
from ._integrate_refined_proposals_into_framework.register_model_in_framework import register_model_in_framework
from ._integrate_refined_proposals_into_framework.get_registration_error import get_registration_error
from ._integrate_refined_proposals_into_framework.log_registration_failure import log_registration_failure
from ._integrate_refined_proposals_into_framework.get_model_string_representation import get_model_string_representation
from ._integrate_refined_proposals_into_framework.log_successful_integration import log_successful_integration
from ._integrate_refined_proposals_into_framework.compile_integration_log import compile_integration_log

from pydantic import BaseModel, Field
from typing import List


# -- PRD --
# 1. BULLET: Retrieve the `refined_proposals` list from the parent node and initialize an
#   empty list `integrated_proposals`.
#   Reason: Establish a working container for the processed equations.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Direct list assignment and initialization.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: For each equation string in `refined_proposals`, perform syntactic validation
#   using the framework’s parser to ensure the expression is tree‑compliant
#   and free of undefined variables.
#   Reason: Guarantees that only syntactically valid equations proceed to integration,
#           preventing downstream failures.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Apply the framework’s `parse_expression` API; catch and log parsing errors.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Cross‑check each validated equation against the framework’s constraint set
#   (e.g., variable names, allowed operators) derived from
#   `define_symbolic_regression_objective`.
#   Reason: Enforces domain constraints specified in the objective definition, ensuring
#           model feasibility.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Iterate over constraint list, flag mismatches, and record a validation
#           status.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Transform each validated string into an internal `SymbolicModel` object by
#   invoking the framework’s `build_model` routine, capturing metadata such
#   as complexity score and operator counts.
#   Reason: Converts raw text into an executable model representation for later use in
#           training/testing.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Call `framework.build_model(eq_str)`; store returned object in a registry.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Register each `SymbolicModel` instance in the framework’s global model
#   registry under a unique identifier (e.g., UUID or proposal ID).
#   Reason: Allows the framework and downstream nodes (e.g., testing) to reference the
#           integrated models consistently.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Use `framework.register_model(model_obj, id)` with collision handling.
# 
# -----------------------------------------------------------------------------
# 6. BULLET: After all proposals are processed, compile a summary: count of successful
#   integrations, any failures, and overall status flag based on whether any
#   model failed validation or registration.
#   Reason: Provides a concise, machine‑readable result for downstream nodes.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Aggregate boolean flags and counts; set `integration_success` accordingly.
# 
# -----------------------------------------------------------------------------
# 7. BULLET: Generate a human‑readable `integration_log` capturing timestamps, number of
#   proposals, validation errors, registration steps, and a short
#   success/failure message.
#   Reason: Facilitates debugging, audit trails, and stakeholder communication.
#   Impact: LOW
#   Complexity: LOW
#   Method: String concatenation using a formatted log template.
# 
# -----------------------------------------------------------------------------
# 8. BULLET: If any proposal failed validation, record the specific reason and exclude it
#   from `integrated_proposals`; otherwise, include the fully registered
#   model’s string representation.
#   Reason: Ensures the output list reflects only usable models and prevents downstream
#           errors.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Conditional appending based on validation flag.
# 
# -----------------------------------------------------------------------------
# 9. BULLET: Return the final outputs: `integrated_proposals` (list of strings),
#   `integration_success` (bool), `integrated_count` (int), and
#   `integration_log` (string).
#   Reason: Completes the node’s contract per the defined output structure.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Direct assignment to output fields before returning.
# -- END PRD --



class RefineSelectedProposalsOutput(BaseModel):
    """Pydantic model for refine_selected_proposals node outputs."""
    refined_proposals: List[str] = Field(..., description="List of symbolic regression expressions that have been refined.")
    accuracy_improvement: float = Field(..., description="Absolute improvement in predictive accuracy compared to the original top proposals.")
    complexity_change: int = Field(..., description="Net change in model complexity (negative indicates simplification, positive indicates added complexity).")
    interpretability_score: float = Field(..., description="Overall interpretability score of the refined proposals on a scale from 0.0 (least interpretable) to 1.0 (most interpretable).")


class IntegrateRefinedProposalsIntoFrameworkOutput(BaseModel):
    """Pydantic model for integrate_refined_proposals_into_framework node outputs."""
    integrated_proposals: List[str] = Field(..., description="List of symbolic regression equations integrated into the framework.")
    integration_success: bool = Field(..., description="Whether the integration process completed successfully.")
    integrated_count: int = Field(..., description="Number of proposals integrated into the framework.")
    integration_log: str = Field(..., description="Log or summary of the integration process.")


def integrate_refined_proposals_into_framework(refine_selected_proposals_input: RefineSelectedProposalsOutput, **kwargs) -> IntegrateRefinedProposalsIntoFrameworkOutput:
    """Take the list of refined symbolic regression expressions, validate and adapt them to the framework's internal representation, register them for future use, and produce a concise integration log.

    Args:
        refine_selected_proposals_input: Input from the 'refine_selected_proposals' node.
        **kwargs: Additional keyword arguments.

    Returns:
        IntegrateRefinedProposalsIntoFrameworkOutput: Object containing outputs for this node.
    """
    # Retrieve the refined proposals list and initialize working container
    refined_proposals: List[str] = refine_selected_proposals_input.refined_proposals
    integrated_proposals: List[str] = []
    
    # Initialize tracking variables
    successful_integrations: int = 0
    validation_failures: List[str] = []
    registration_failures: List[str] = []
    
    # Start integration log
    log_entries: List[str] = initialize_integration_log(proposal_count=len(refined_proposals))
    
    # Process each equation string in refined_proposals
    for equation_str in refined_proposals:
        # Perform syntactic validation using framework's parser
        is_syntactically_valid: bool = validate_equation_syntax(equation=equation_str)
        
        if not is_syntactically_valid:
            validation_error: str = get_syntax_validation_error(equation=equation_str)
            validation_failures.append(validation_error)
            log_validation_failure(log_entries=log_entries, equation=equation_str, error=validation_error)
            continue
            
        # Cross-check against framework's constraint set
        constraint_validation_result: dict = validate_against_constraints(equation=equation_str)
        
        if not constraint_validation_result["is_valid"]:
            constraint_error: str = constraint_validation_result["error"]
            validation_failures.append(constraint_error)
            log_constraint_failure(log_entries=log_entries, equation=equation_str, error=constraint_error)
            continue
            
        # Transform validated string into SymbolicModel object
        symbolic_model: object = build_symbolic_model(equation_str=equation_str)
        
        if symbolic_model is None:
            build_error: str = get_model_build_error(equation=equation_str)
            validation_failures.append(build_error)
            log_build_failure(log_entries=log_entries, equation=equation_str, error=build_error)
            continue
            
        # Register SymbolicModel instance in framework's global registry
        unique_id: str = generate_unique_model_id()
        registration_success: bool = register_model_in_framework(model=symbolic_model, model_id=unique_id)
        
        if not registration_success:
            registration_error: str = get_registration_error(model_id=unique_id)
            registration_failures.append(registration_error)
            log_registration_failure(log_entries=log_entries, equation=equation_str, error=registration_error)
            continue
            
        # Include successfully integrated model in output
        model_string_representation: str = get_model_string_representation(model=symbolic_model)
        integrated_proposals.append(model_string_representation)
        successful_integrations += 1
        log_successful_integration(log_entries=log_entries, equation=equation_str, model_id=unique_id)
    
    # Compile summary and determine overall success
    total_failures: int = len(validation_failures) + len(registration_failures)
    integration_success: bool = total_failures == 0 and successful_integrations > 0
    
    # Generate final integration log
    final_log: str = compile_integration_log(
        log_entries=log_entries,
        successful_count=successful_integrations,
        total_count=len(refined_proposals),
        validation_failures=validation_failures,
        registration_failures=registration_failures,
        overall_success=integration_success
    )
    
    return IntegrateRefinedProposalsIntoFrameworkOutput(
        integrated_proposals=integrated_proposals,
        integration_success=integration_success,
        integrated_count=successful_integrations,
        integration_log=final_log
    )