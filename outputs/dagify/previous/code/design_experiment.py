# -- PRD --
# 1. BULLET: 1️⃣ Extract the single-sentence hypothesis from the parent node
#   *formulate_hypothesis* and assign it to the `hypothesis` field.
#   Reason: Ensures the hypothesis is directly inherited and not re-formulated,
#           maintaining consistency across the workflow.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Parse the parent output `hypothesis_sentence`, trim whitespace, and store
#           as `hypothesis`.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: 2️⃣ Identify all factors relevant to the research objective that can be
#   intentionally manipulated by the experimenter; list them in the
#   `independent_variables` field.
#   Reason: Independent variables are the key drivers that the experiment will test,
#           directly affecting the outcome.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Apply a knowledge‑base lookup of standard experimental variables for the
#           domain; filter by relevance; ensure at least two distinct
#           levels per variable to allow statistical analysis.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: 3️⃣ For each independent variable, determine the measurable outcome(s) it is
#   expected to influence; compile these into the `dependent_variables` list.
#   Reason: Dependent variables represent the experiment’s outcomes, enabling
#           quantitative evaluation of the hypothesis.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Map each independent variable to its theoretical effect using causal
#           diagrams; cross‑check with the hypothesis statement; avoid
#           duplication.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: 4️⃣ Enumerate all environmental or procedural factors that must remain
#   constant across trials to prevent confounding; place them in
#   `control_variables`.
#   Reason: Controls isolate the effect of independent variables, ensuring validity.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: List temperature, humidity, equipment calibration, operator, timing, and
#           any other potentially influencing factors; confirm via a
#           design-of-experiments checklist.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: 5️⃣ For each dependent variable, specify the measurement instrument or
#   protocol (e.g., spectrophotometer reading, time‑to‑completion, survey
#   score) and store the description in `measurement_methods`.
#   Reason: Clear measurement methods enable reproducibility and data integrity.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Match each dependent variable with an appropriate instrument from the
#           domain’s standard equipment list; document calibration steps
#           and unit conventions.
# 
# -----------------------------------------------------------------------------
# 6. BULLET: 6️⃣ Calculate the required `sample_size` using a power analysis that
#   incorporates the expected effect size, alpha level (commonly 0.05),
#   desired power (commonly 0.8), and the number of independent variables.
#   Reason: Adequate sample size ensures statistical validity and mitigates Type II
#           error.
#   Impact: HIGH
#   Complexity: HIGH
#   Method: Employ a statistical software API (e.g., G*Power, scipy.stats) with effect
#           size from pilot data or literature; round up to nearest
#           integer; enforce a minimum threshold (e.g., 30 per group) if
#           calculation yields low numbers.
# 
# -----------------------------------------------------------------------------
# 7. BULLET: 7️⃣ Draft a comprehensive `experimental_protocol` string that sequences the
#   experiment from preparation to data capture, including safety checks,
#   randomization, blinding (if applicable), and data logging procedures.
#   Reason: A detailed protocol guarantees consistency across multiple trials and
#           operators.
#   Impact: HIGH
#   Complexity: HIGH
#   Method: Structure the protocol in numbered paragraphs: (1) Setup, (2) Calibration,
#           (3) Randomization of treatment groups, (4) Execution steps for
#           each trial, (5) Data recording, (6) Decontamination, (7) Safety
#           checks. Embed placeholders for variable values (e.g.,
#           `{{temperature}}`).
# 
# -----------------------------------------------------------------------------
# 8. BULLET: 8️⃣ Validate the design by performing a quick risk assessment and ensuring
#   all safety protocols are feasible within the defined experimental
#   setting.
#   Reason: Prevents experiment abortion due to oversight of safety or regulatory
#           compliance.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Cross‑reference the protocol with institutional safety guidelines; flag any
#           missing PPE or hazard mitigation steps.
# 
# -----------------------------------------------------------------------------
# 9. BULLET: 9️⃣ Review the entire output dictionary for type consistency and completeness
#   before returning it to the workflow engine.
#   Reason: Type mismatches would cause downstream node failures.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Automate a schema validation routine: assert `hypothesis` is string,
#           `independent_variables` is list of strings, etc.; generate
#           error logs for missing fields.
# -- END PRD --

from pydantic import BaseModel, Field


class FormulateHypothesisOutput(BaseModel):
    """Pydantic model for formulate_hypothesis node outputs."""
    hypothesis_sentence: str = Field(..., description="A single-sentence, testable hypothesis for the experiment")


class DesignExperimentOutput(BaseModel):
    """Pydantic model for design_experiment node outputs."""
    hypothesis: str = Field(..., description="The testable hypothesis to be examined")
    independent_variables: str = Field(..., description="List of variables that will be manipulated in the experiment")
    dependent_variables: str = Field(..., description="List of variables that will be measured as outcomes")
    control_variables: str = Field(..., description="List of variables that will be held constant to avoid confounding effects")
    measurement_methods: str = Field(..., description="Methods or instruments used to quantify each dependent variable")
    sample_size: int = Field(..., description="Number of experimental units or trials to be performed")
    experimental_protocol: str = Field(..., description="Step\u2011by\u2011step description of how the experiment will be executed")


def design_experiment(formulate_hypothesis_input: FormulateHypothesisOutput, **kwargs) -> DesignExperimentOutput:
    """Design the experiment to test the hypothesis

    Args:
        formulate_hypothesis_input: Input from the 'formulate_hypothesis' node.
        **kwargs: Additional keyword arguments.

    Returns:
        DesignExperimentOutput: Object containing outputs for this node.
    """
    # TODO: Implement this function

    # Return stub output with placeholder values
    return DesignExperimentOutput(
        hypothesis="",
        independent_variables="",
        dependent_variables="",
        control_variables="",
        measurement_methods="",
        sample_size=0,
        experimental_protocol="",
    )