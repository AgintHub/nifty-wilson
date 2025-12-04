# generate_summary PRD

## Description
Generates a concise executive summary describing the trading methodology based on provided indicators and logic steps


## Implementation Plan

### 1. Validate and normalize the `indicators` and `logic_steps` inputs.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the shim receives well‑formed data and prevents downstream formatting errors. |
| **Impact** | Reduces runtime failures and guarantees consistent prompt construction. |
| **Complexity** | LOW |
| **Method** | Strip whitespace, join list inputs into a single comma‑separated string, and escape any special characters that could break the prompt template. |

### 2. Construct a deterministic prompt that injects the normalized inputs into a predefined summary template.

| Category | Details |
| --- | --- |
| **Reason** | A stable prompt yields reproducible, high‑quality summaries from the language model. |
| **Impact** | Improves reliability of the generated summary and makes unit‑testing straightforward. |
| **Complexity** | MEDIUM |
| **Method** | Use Python f‑strings or Jinja2 templating to embed `{{indicators}}` and `{{logic_steps}}` into the prompt defined above, then send the prompt to the LLM via the existing inference client. |

### 3. Post‑process the LLM response to enforce length limits and plain‑text output.

| Category | Details |
| --- | --- |
| **Reason** | Consumers of the summary expect a succinct, unformatted string without markdown or extra whitespace. |
| **Impact** | Guarantees downstream nodes receive a clean, predictable summary string. |
| **Complexity** | LOW |
| **Method** | Trim the response, truncate to 150 words if necessary, and strip any surrounding markdown markers before returning the `output` field. |
