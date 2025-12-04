# deduplicate_indicators PRD

## Description
Removes duplicate indicator names from the input list while preserving their original order.


## Implementation Plan

### 1. Implement order‑preserving deduplication by iterating through the list and adding unseen items to the result.

| Category | Details |
| --- | --- |
| **Reason** | The downstream trading‑logic nodes require a unique set of indicators but must respect the order defined by the user or upstream node. |
| **Impact** | Prevents redundant processing of the same indicator and ensures deterministic rule generation. |
| **Complexity** | LOW |
| **Method** | Loop over the input list, maintain a `seen` set, and append an item to the output list only if it is not already in `seen`. |

### 2. Normalize and clean each indicator string (trim whitespace, handle case‑insensitivity) before duplicate checking while returning the original casing of the first occurrence.

| Category | Details |
| --- | --- |
| **Reason** | User‑provided indicator names may contain extra spaces or varied casing, leading to false negatives in duplicate detection. |
| **Impact** | Improves robustness, avoids accidental duplicates, and maintains user‑intended naming conventions. |
| **Complexity** | MEDIUM |
| **Method** | Strip whitespace with `str.strip()`, compare using a lower‑cased version for membership in `seen`, but store the original string in the output list. |

### 3. Validate input type and raise a clear `TypeError` if the provided `indicators` argument is not a list of strings.

| Category | Details |
| --- | --- |
| **Reason** | Early validation catches programming errors and provides actionable feedback to developers. |
| **Impact** | Reduces runtime exceptions later in the pipeline and simplifies debugging. |
| **Complexity** | LOW |
| **Method** | Use `isinstance(indicators, list)` and `all(isinstance(i, str) for i in indicators)` checks; raise `TypeError` with an explanatory message on failure. |
