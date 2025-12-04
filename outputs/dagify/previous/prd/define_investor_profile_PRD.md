# define_investor_profile PRD

## Description
Describes the target investor segment for the hedge fund by extracting and synthesising investor characteristics from the fund’s strategic objectives.


## Implementation Plan

### 1. Parse the objectives list from clarify_fund_objectives to extract investment purpose and target return profile.

| Category | Details |
| --- | --- |
| **Reason** | The investor segment must align with the fund’s stated purpose and return expectations. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use a rule‑based NLP extractor to identify keywords such as 'institutional', 'family office', 'high‑return', 'long‑term', and map them to a predefined investor archetype table. |

### 2. Match the extracted archetype to a base investor profile template that includes default ranges for ticket size, risk tolerance, liquidity, and geographic focus.

| Category | Details |
| --- | --- |
| **Reason** | Standard templates provide consistent ranges that can be fine‑tuned against objectives. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Maintain a JSON dictionary of archetypes → template values; perform a lookup by archetype name. |

### 3. Refine ticket size bounds by quantifying the fund’s target AUM and expected capital raise timeline from clarify_fund_objectives.

| Category | Details |
| --- | --- |
| **Reason** | Ticket sizes must be realistic given the fundraising window and target AUM. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Apply formula: min_ticket = 0.05 * target_AUM, max_ticket = 0.20 * target_AUM, clamp values to realistic market ranges ($1M‑$100M). |

### 4. Determine risk tolerance level by evaluating the strategy’s volatility target from set_performance_and_risk_targets.

| Category | Details |
| --- | --- |
| **Reason** | Risk tolerance must be compatible with strategy risk metrics. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Map volatility percentage ranges to risk labels: <10% → low, 10–20% → moderate, >20% → high. |

### 5. Infer liquidity preference from the fund’s investment horizon specified in choose_investment_strategy and set_performance_and_risk_targets.

| Category | Details |
| --- | --- |
| **Reason** | Liquidity preference must match the strategy’s holding period. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | If strategy is long/short equity with 1‑2 year horizon → long‑term; if global macro with 3‑6 month horizon → medium‑term. |

### 6. Select geographic focus by correlating the fund’s domicile (choose_legal_entity_type/jurisdiction) and the target markets identified in define_asset_universe.

| Category | Details |
| --- | --- |
| **Reason** | Investors are more comfortable investing in familiar or aligned geographies. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Create a list of regions present in asset_universe; prioritize regions that match jurisdiction tax advantages and regulatory familiarity. |

### 7. Validate all numeric outputs against realistic industry benchmarks (e.g., typical family office ticket size between $5M and $50M).

| Category | Details |
| --- | --- |
| **Reason** | Ensures the profile is credible and market‑consistent. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Compare computed ranges to benchmark table; if outliers exist, adjust using a safety factor of 0.8–1.2. |

### 8. Compile the final profile record in the required output structure, ensuring type consistency (floats for ticket sizes, list of strings for geographic focus).

| Category | Details |
| --- | --- |
| **Reason** | Conforms to downstream node expectations and prevents type errors. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Serialize values into JSON; cast numeric strings to float; ensure geographic_focus is an array of strings. |
