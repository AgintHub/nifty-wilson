# configure_llm_for_proposal_generation PRD

## Description
Configure all necessary LLM parameters and templates to produce symbolic regression proposals that respect the defined objective, constraints, and data schema.


## Implementation Plan

### 1. Parse the parent output to extract the objective description, target variable, feature variables, constraints, performance metrics, and dataset description.

| Category | Details |
| --- | --- |
| **Reason** | These elements inform the LLM configuration and prompt template to ensure proposals align with the task. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use JSON parsing and schema validation to map parent fields to local variables, ensuring no required field is missing. |

### 2. Select a default model name based on the target language and available API endpoints; fallback to a safe open‑source model if the preferred one is unavailable.

| Category | Details |
| --- | --- |
| **Reason** | Model choice directly affects proposal quality and latency. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Define a priority list (e.g., ["gpt-4o", "llama-3.1", "openai-gpt-3.5"]), query availability via the provider SDK, and choose the first available model. |

### 3. Determine the temperature setting by balancing exploration and precision; default to 0.2 for symbolic regression to favor deterministic, interpretable formulas.

| Category | Details |
| --- | --- |
| **Reason** | Lower temperature reduces randomness, producing more stable symbolic expressions suitable for downstream evaluation. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | If constraints specify strict compliance, enforce temperature ≤ 0.3; otherwise use a heuristic based on the complexity of feature_variables. |

### 4. Compute max_tokens by estimating the typical length of symbolic expressions from past runs and adding a buffer; use a formula such as max_tokens = 2 * (number_of_features * 5).

| Category | Details |
| --- | --- |
| **Reason** | Ensures enough token space for complex expressions without wasting resources. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Implement a lightweight estimator that counts tokens for a sample expression and scales accordingly. |

### 5. Construct a prompt_template that injects the objective and dataset description, and includes placeholders for the model to output a single symbolic expression per sample. The template should be JSON‑serializable and contain a clear instruction section.

| Category | Details |
| --- | --- |
| **Reason** | A well‑structured template reduces hallucinations and improves the LLM's focus on symbolic content. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Define the template as a Python multiline string with `{objective}`, `{data_description}`, and `{target_variable}` placeholders. Wrap instructions in a JSON object with keys "instruction" and "input" for compatibility with many LLM APIs. |

### 6. Generate an input_schema string that describes the expected JSON input the LLM will receive during generation. Include fields for feature_variables, target_variable, and constraints, with data types and example values.

| Category | Details |
| --- | --- |
| **Reason** | Providing a concrete schema guides the LLM in generating syntactically correct expressions and aids downstream validation. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Serialize a Python dictionary to pretty‑printed JSON and embed it in the prompt_template or provide it as a separate configuration field. |

### 7. Decide the number of proposals (num_proposals) by evaluating the size of the feature set and the evaluation budget; default to 10 proposals for moderate feature sizes, scaling up to 20 if computational resources allow.

| Category | Details |
| --- | --- |
| **Reason** | More proposals increase the chance of finding high‑quality formulas but consume more API calls. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Implement a rule: if len(feature_variables) > 10 then num_proposals = 20 else num_proposals = 10; allow overrides via an optional configuration flag. |
