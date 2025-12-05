# select_jurisdiction PRD

## Description
Pick fund domicile and note rationale.


## Implementation Plan

### 1. Validate the input by confirming that the 'objectives' field from clarify_fund_objectives is a non‑empty list of strings.

| Category | Details |
| --- | --- |
| **Reason** | Ensures we have the correct data type before proceeding with jurisdiction evaluation. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use a type‑check utility; if not list, raise a validation error. |

### 2. Create an internal criteria matrix mapping each objective to a jurisdiction‑relevant factor (e.g., tax neutrality, regulatory burden, investor familiarity).

| Category | Details |
| --- | --- |
| **Reason** | Translates abstract objectives into concrete evaluation metrics. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Apply a lookup table: for each objective, assign a score weight (1–5) to factors; document the mapping in a JSON structure. |

### 3. Instantiate a candidate jurisdiction pool: Cayman Islands, Delaware (USA), and Luxembourg.

| Category | Details |
| --- | --- |
| **Reason** | These are the most common domiciles for hedge funds and cover the main regulatory and tax regimes. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Define a static list in code; no external calls needed. |

### 4. For each jurisdiction, compute a weighted score by multiplying each factor’s weight by the jurisdiction’s performance on that factor (e.g., 5 for tax‑neutrality, 3 for regulatory clarity).

| Category | Details |
| --- | --- |
| **Reason** | Provides a quantitative basis for comparison. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Implement a nested loop: outer over jurisdictions, inner over factors; sum weighted scores; store in a dictionary. |

### 5. Select the jurisdiction with the highest aggregate score; if tied, prefer the one with lower tax burden.

| Category | Details |
| --- | --- |
| **Reason** | Ensures an objective, reproducible selection process. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use a simple max‑by‑key function; apply tie‑breaker logic. |

### 6. Generate two concise pros and two cons by mapping the top positive and negative attributes of the chosen jurisdiction to the evaluation criteria.

| Category | Details |
| --- | --- |
| **Reason** | Aligns the pros/cons with the fund’s objectives, making the rationale transparent. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Select the two highest‑scoring positive factors as pros; pick two lowest‑scoring negative factors as cons; format each as a short sentence. |

### 7. Craft a single‑sentence rationale summarizing the decision, highlighting how the chosen jurisdiction best satisfies the core objectives.

| Category | Details |
| --- | --- |
| **Reason** | Provides a clear, actionable justification for downstream nodes. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Combine the jurisdiction name with a phrase like "best balances tax neutrality and regulatory flexibility to meet objective X". |

### 8. Populate the output structure fields: set jurisdiction to the selected name; assign pros and cons lists; insert rationale string.

| Category | Details |
| --- | --- |
| **Reason** | Converts internal variables into the node’s defined output format. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Map variables to the corresponding keys; ensure list types are correctly typed as PrimitiveType.LIST_STR. |
