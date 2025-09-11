# -- PRD --
# 1. BULLET: Validate that all materials and equipment are prepared by checking the
#   `is_prepared` flag from the `prepare_materials` output. If the flag is
#   false, abort the experiment, set `experiment_completed` to false, and
#   record a safety compliance failure.
#   Reason: Ensures that the experiment only proceeds when the required resources are
#           available, preventing equipment failures and safety incidents.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Implement a pre‑execution check: if !is_prepared then set
#           experiment_completed = false, safety_compliance = false, exit
#           loop.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Parse the experimental protocol string from the `design_experiment` output
#   into a list of executable steps. Store each step in an array
#   `protocol_steps` for sequential iteration.
#   Reason: The protocol must be broken down into actionable operations that the system
#           can iterate over.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Use a simple delimiter (e.g., newline or semicolon) to split the protocol,
#           trim whitespace, and validate step syntax against a known
#           schema.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Initialize empty collections for `observations` and `anomaly_descriptions`,
#   and set boolean flags `safety_compliance` and `data_collection_status` to
#   true. Assign the trial number from `design_experiment.sample_size` if it
#   represents a run index, or default to 1 if not provided.
#   Reason: Establishes baseline state before experiment execution, allowing clear
#           tracking of changes.
#   Impact: LOW
#   Complexity: LOW
#   Method: Set trial_number = design_experiment.sample_size or 1; initialize arrays.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Iterate over each step in `protocol_steps`. For each step, perform the
#   defined action (e.g., add reagent, adjust temperature, record
#   measurement) and capture a timestamped observation note.
#   Reason: Sequential execution is essential to maintain experimental integrity.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Implement a loop: for step in protocol_steps: execute_step(step); append
#           observation = f'{timestamp}: {step_result}'.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: During step execution, continuously monitor safety compliance against a
#   predefined safety checklist (e.g., PPE usage, containment integrity,
#   emergency procedures). If any violation is detected, set
#   `safety_compliance` to false, log a detailed anomaly description, and
#   abort remaining steps.
#   Reason: Safety must be enforced at all times; early abort prevents escalation of
#           hazards.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Embed safety checks within each `execute_step` call; use a rule engine or
#           conditional checks to flag violations.
# 
# -----------------------------------------------------------------------------
# 6. BULLET: After each step, increment `observation_count` by one, append the observation
#   to the `observations` list, and check if the data collected for that step
#   meets quality criteria (e.g., range checks).
#   Reason: Accurate observation recording is necessary for downstream data analysis.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Use simple counters and append operations; perform range checks against
#           expected min/max values.
# 
# -----------------------------------------------------------------------------
# 7. BULLET: If an unexpected event occurs—such as equipment failure, measurement
#   out‑of‑range, or time lag—set `anomalies_detected` to true and append a
#   descriptive message to `anomaly_descriptions`.
#   Reason: Anomalies may influence data validity and should be transparently reported.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Wrap critical operations in try/catch blocks; on exception, capture
#           exception message and context.
# 
# -----------------------------------------------------------------------------
# 8. BULLET: After all steps have been processed, set `experiment_completed` to true if no
#   fatal safety violations occurred, otherwise leave it false.
#   Reason: Completion flag is required to determine if the experiment was fully
#           executed.
#   Impact: LOW
#   Complexity: LOW
#   Method: Check safety_compliance flag; if true then experiment_completed = true.
# 
# -----------------------------------------------------------------------------
# 9. BULLET: Determine `data_collection_status` by verifying that the number of collected
#   data points matches the expected count defined in
#   `design_experiment.sample_size`. If mismatch, set
#   `data_collection_status` to false.
#   Reason: Ensures that the experiment produced a complete dataset for analysis.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Compare observation_count with sample_size; if equal, status = true.
# 
# -----------------------------------------------------------------------------
# 10. BULLET: Return the constructed output dictionary containing all eight fields,
#   ensuring correct data types (bool, int, List[str]) and that all lists are
#   in the order of execution.
#   Reason: A consistent and typed output is required for downstream nodes.
#   Impact: LOW
#   Complexity: LOW
#   Method: Package variables into a dict: {"experiment_completed":...,
#           "safety_compliance":..., ...}; serialize as JSON.
# -- END PRD --

from pydantic import BaseModel, Field
from typing import List


class DesignExperimentOutput(BaseModel):
    """Pydantic model for design_experiment node outputs."""
    hypothesis: str = Field(..., description="The testable hypothesis to be examined")
    independent_variables: str = Field(..., description="List of variables that will be manipulated in the experiment")
    dependent_variables: str = Field(..., description="List of variables that will be measured as outcomes")
    control_variables: str = Field(..., description="List of variables that will be held constant to avoid confounding effects")
    measurement_methods: str = Field(..., description="Methods or instruments used to quantify each dependent variable")
    sample_size: int = Field(..., description="Number of experimental units or trials to be performed")
    experimental_protocol: str = Field(..., description="Step\u2011by\u2011step description of how the experiment will be executed")


class PrepareMaterialsOutput(BaseModel):
    """Pydantic model for prepare_materials node outputs."""
    required_items: List[str] = Field(..., description="Names of all materials and equipment items required for the experiment")
    quantities: List[int] = Field(..., description="Quantities of each corresponding item listed in required_items")
    total_cost: float = Field(..., description="Estimated total cost of all prepared items")
    is_prepared: bool = Field(..., description="Whether all items have been successfully prepared and ready for use")
    preparation_notes: str = Field(..., description="Any additional notes or remarks about the preparation process")


class ConductExperimentOutput(BaseModel):
    """Pydantic model for conduct_experiment node outputs."""
    experiment_completed: bool = Field(..., description="Indicates if the experiment was carried out to completion")
    safety_compliance: bool = Field(..., description="Indicates whether all required safety protocols were followed")
    observation_count: int = Field(..., description="Number of observations recorded during the experiment")
    observations: List[str] = Field(..., description="Textual notes of each observation")
    anomalies_detected: bool = Field(..., description="Indicates if any anomalies were encountered")
    anomaly_descriptions: List[str] = Field(..., description="Descriptions of each anomaly encountered, if any")
    trial_number: int = Field(..., description="The trial number or batch identifier for this run")
    data_collection_status: bool = Field(..., description="Whether data collection was successfully performed")


def conduct_experiment(design_experiment_input: DesignExperimentOutput, prepare_materials_input: PrepareMaterialsOutput, **kwargs) -> ConductExperimentOutput:
    """This node executes the laboratory or field experiment as specified in the design and preparation steps. It must follow the experimental protocol, enforce safety checks, log observations and anomalies, and signal whether data collection succeeded.

    Args:
        design_experiment_input: Input from the 'design_experiment' node.
        prepare_materials_input: Input from the 'prepare_materials' node.
        **kwargs: Additional keyword arguments.

    Returns:
        ConductExperimentOutput: Object containing outputs for this node.
    """
    # TODO: Implement this function

    # Return stub output with placeholder values
    return ConductExperimentOutput(
        experiment_completed=False,
        safety_compliance=False,
        observation_count=0,
        observations=[],
        anomalies_detected=False,
        anomaly_descriptions=[],
        trial_number=0,
        data_collection_status=False,
    )