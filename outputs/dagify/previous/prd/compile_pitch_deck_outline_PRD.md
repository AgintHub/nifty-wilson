# compile_pitch_deck_outline PRD

## Description
Framework for fundraising presentation.


## Implementation Plan

### 1. Verify that all required parent outputs are present and non‑empty before proceeding.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that the downstream logic has the necessary data to construct meaningful slide titles. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Programmatically check that `clarify_fund_objectives.objectives`, `define_investor_profile.target_investor_segment`, `choose_investment_strategy.strategy_category`, `set_performance_and_risk_targets.gross_return`, `draft_fee_structure.management_fee_percentage`, and `design_risk_management_framework.risk_controls` exist and are of the expected type. |

### 2. Extract high‑level messaging elements from each parent output to identify core narrative themes.

| Category | Details |
| --- | --- |
| **Reason** | These themes directly inform the slide titles and ensure each title aligns with the fund’s unique selling propositions. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Parse the list of objectives to select the top 3 most impactful bullets; capture the strategy category and rationale; pull target gross return, volatility, Sharpe ratio, and max drawdown; record the fee structure summary; and compile the first 4 risk control statements. |

### 3. Define a canonical slide order based on investor deck best practices: Introduction, Overview, Objectives, Strategy, Team, Edge, Performance, Risk, Fees, Expected Returns.

| Category | Details |
| --- | --- |
| **Reason** | A consistent sequence improves narrative flow and meets investor expectations. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use a hard‑coded list of 10 titles as a template, with placeholders for dynamic terms. |

### 4. Generate each slide title, inserting dynamic terms from parent data where relevant (e.g., strategy category, target gross return, risk limit keywords).

| Category | Details |
| --- | --- |
| **Reason** | Personalized titles increase engagement and signal that the deck is tailored to the fund’s specifics. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | String interpolation: replace `{strategy}` with the chosen strategy, `{return}` with the gross return percentage, and `{risk}` with the key risk control phrase. |

### 5. Enforce title length constraints (≤ 7 words) and grammatical consistency (no trailing punctuation, proper capitalization).

| Category | Details |
| --- | --- |
| **Reason** | Short, punchy titles are easier to read and more visually appealing. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Token count per title, regex trimming of punctuation, title‑case conversion. |

### 6. Validate that the final list contains exactly ten unique titles.

| Category | Details |
| --- | --- |
| **Reason** | Matches the specified output structure and prevents accidental duplication. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Count list length and check for duplicates via set comparison. |

### 7. Package the validated list into the `slide_titles` output field and serialize to JSON.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the node’s contract is fulfilled and downstream nodes can consume the data. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Construct a dict with the key `slide_titles` mapping to the ordered list, then use a JSON library to output. |
