# compute_logic_completeness PRD

## Description
Evaluates whether the signal logic fully accounts for every identified indicator and provides complete decision pathways.


## Implementation Plan

### 1. Parse and normalize the three input strings into ordered sets of indicator names.

| Category | Details |
| --- | --- |
| **Reason** | Consistent data structures are required to compare coverage accurately. |
| **Impact** | Ensures that whitespace, case, or ordering differences do not cause false negatives in completeness checks. |
| **Complexity** | LOW |
| **Method** | Split each string on commas, trim whitespace, convert to lower‑case, and store in Python sets. |

### 2. Validate that every parent indicator appears in the used_indicators set.

| Category | Details |
| --- | --- |
| **Reason** | The core definition of completeness is that no identified indicator is omitted from the logic. |
| **Impact** | Detects missing indicators early, allowing downstream nodes to flag or abort the workflow. |
| **Complexity** | MEDIUM |
| **Method** | Compute the set difference parent_indicators − used_indicators; if non‑empty, mark completeness as False. |

### 3. Inspect signal_logic_steps to confirm explicit BUY, SELL, and NEUTRAL branches for each used indicator.

| Category | Details |
| --- | --- |
| **Reason** | A logic file may list indicators but still lack decision rules for some of them. |
| **Impact** | Guarantees that the algorithm can generate actionable signals for every indicator, preventing runtime gaps. |
| **Complexity** | HIGH |
| **Method** | If signal_logic_steps is JSON, deserialize it and verify that for each indicator there is at least one rule object containing a 'decision' field with values 'BUY', 'SELL', or 'HOLD'; otherwise, perform regex search for keywords (buy|sell|hold) linked to each indicator. |
