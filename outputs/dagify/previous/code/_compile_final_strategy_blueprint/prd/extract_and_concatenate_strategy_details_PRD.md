# extract_and_concatenate_strategy_details PRD

## Description
Combines the refined strategy summary and all adjustment sections into a single, well‑formatted narrative string.


## Implementation Plan

### 1. Concatenate the four input strings with section headings and line breaks to form a cohesive narrative.

| Category | Details |
| --- | --- |
| **Reason** | The downstream blueprint builder expects a single, human‑readable description that aggregates all refinement information. |
| **Impact** | Produces a clear, organized output that downstream nodes can embed directly into documentation and UI displays. |
| **Complexity** | LOW |
| **Method** | Implement a simple string‑formatting function using f‑strings or `str.join`, inserting headings like "Parameter Adjustments:" before each corresponding input. |

### 2. Validate each input is a non‑empty string and raise a descriptive ValueError if any are missing or invalid.

| Category | Details |
| --- | --- |
| **Reason** | Ensures data integrity; downstream processing assumes all sections are present and prevents obscure failures later in the pipeline. |
| **Impact** | Early detection of malformed inputs, leading to faster debugging and more reliable pipeline execution. |
| **Complexity** | MEDIUM |
| **Method** | Add a helper validation routine that checks `isinstance(x, str) and x.strip()` for each argument; wrap the concatenation in a try/except block to surface errors clearly. |

### 3. Enforce a maximum character length (e.g., 4000 chars) on the final output, truncating with an ellipsis if the limit is exceeded.

| Category | Details |
| --- | --- |
| **Reason** | The final blueprint may be stored or transmitted to services with token or payload limits. |
| **Impact** | Prevents downstream API calls from failing due to oversized payloads while preserving the most important information. |
| **Complexity** | MEDIUM |
| **Method** | After concatenation, compare `len(output)` to the limit; if exceeded, truncate each section proportionally or keep the leading portion and append "... (truncated)". |
