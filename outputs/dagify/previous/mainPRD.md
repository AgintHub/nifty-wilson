# build_hedge_fund - Complete PRD Documentation

## Overview
PRDs for nodes in the 'build_hedge_fund' module.

## Table of Contents

- [choose_investment_strategy](#choose_investment_strategy)

- [choose_legal_entity_type](#choose_legal_entity_type)

- [clarify_fund_objectives](#clarify_fund_objectives)

- [compile_pitch_deck_outline](#compile_pitch_deck_outline)

- [create_hiring_plan](#create_hiring_plan)

- [define_asset_universe](#define_asset_universe)

- [define_investor_profile](#define_investor_profile)

- [define_technology_stack](#define_technology_stack)

- [design_compliance_program](#design_compliance_program)

- [design_risk_management_framework](#design_risk_management_framework)

- [develop_timeline_and_milestones](#develop_timeline_and_milestones)

- [draft_fee_structure](#draft_fee_structure)

- [draft_operations_workflow](#draft_operations_workflow)

- [estimate_setup_and_operating_costs](#estimate_setup_and_operating_costs)

- [identify_regulatory_requirements](#identify_regulatory_requirements)

- [list_service_providers](#list_service_providers)

- [outline_governance_structure](#outline_governance_structure)

- [produce_final_fund_plan_summary](#produce_final_fund_plan_summary)

- [select_jurisdiction](#select_jurisdiction)

- [set_performance_and_risk_targets](#set_performance_and_risk_targets)



---

## choose_investment_strategy

### Description
Identify the high-level investment strategy category.

### Implementation Plan

#### 1. Retrieve the list of core objectives from the output of `clarify_fund_objectives` and confirm the list is non-empty.

| Category | Details |
| --- | --- |
| **Reason** | The strategy choice must be grounded in the fund’s stated objectives; an empty list would invalidate further logic. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Parse the JSON output, access the `objectives` array, and assert its length > 0; if empty, raise a validation error. |

#### 2. Apply keyword extraction to each objective to capture thematic words (e.g., 'growth', 'liquidity', 'global markets').

| Category | Details |
| --- | --- |
| **Reason** | Keywords provide a structured representation of objectives that can be matched against strategy descriptors. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Use a lightweight NLP library (e.g., spaCy or NLTK) to perform part-of-speech tagging and extract nouns/adjectives; optionally employ TF‑IDF scoring to weight unique terms. |

#### 3. Define a mapping table of candidate strategy categories to characteristic keyword sets.

| Category | Details |
| --- | --- |
| **Reason** | A formal mapping enables objective‑to‑strategy translation via keyword overlap. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Create a JSON object where keys are strategy names and values are arrays of associated keywords, e.g., {'Long/Short Equity': ['equity', 'beta', 'alpha'], 'Global Macro': ['macro', 'interest', 'currency']} |

#### 4. Score each strategy by counting keyword matches between the aggregated objective keywords and each strategy’s keyword set, optionally weighting by keyword frequency.

| Category | Details |
| --- | --- |
| **Reason** | A quantitative score provides an objective basis for selecting the best fit strategy. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | For each strategy, iterate over its keyword set, increment a counter when the keyword appears in the objective keyword list; normalize by total number of keywords to produce a score. |

#### 5. Identify the strategy with the highest score; in case of a tie, apply a deterministic tie‑breaker such as alphabetical order or a predefined priority hierarchy.

| Category | Details |
| --- | --- |
| **Reason** | Ensures a single, reproducible output strategy. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use a max‑function on the score dictionary; if multiple keys share the maximum, sort keys alphabetically and pick the first. |

#### 6. Construct a concise, single‑sentence rationale that links the top strategy’s key characteristics to the most salient objective themes.

| Category | Details |
| --- | --- |
| **Reason** | The rationale must explain the alignment in a digestible format for stakeholders. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Select the two highest‑frequency objective themes, insert them into a template such as "We choose {strategy} because it targets {theme1} and {theme2} objectives." |

#### 7. Validate that the rationale contains only one sentence and no excessive technical jargon, truncating if necessary.

| Category | Details |
| --- | --- |
| **Reason** | Keeps the output concise and readable, matching the specification. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Split the string on period characters; assert length == 1; if more, collapse into a single sentence using a summarization or string truncation technique. |

#### 8. Return the final `strategy_category` and `rationale` values as specified in the output structure.

| Category | Details |
| --- | --- |
| **Reason** | Completes the node by producing the required fields for downstream nodes. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Serialize the two strings into a JSON object matching the `output_structure` schema. |


---

## choose_legal_entity_type

### Description
Identify legal structure for the hedge fund vehicle based on the chosen domicile, balancing regulatory fit, tax efficiency, and operational simplicity.

### Implementation Plan

#### 1. Retrieve the jurisdiction value from the output of the parent node 'select_jurisdiction' and store it as a string variable.

| Category | Details |
| --- | --- |
| **Reason** | The jurisdiction drives the available legal entity options; retrieving it ensures the node works with the most current choice. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use a simple JSON path extraction: jurisdiction = parent_outputs['select_jurisdiction']['jurisdiction']. |

#### 2. Create a jurisdiction‑entity compatibility lookup table that maps each jurisdiction to its commonly used hedge‑fund structures (e.g., Cayman → LP/LLC; Delaware → LP; Luxembourg → SICAV).

| Category | Details |
| --- | --- |
| **Reason** | Hard‑coding a small, curated table avoids expensive API calls and ensures quick, deterministic decision‑making. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Define a static dictionary in the node’s code: compat = { 'Cayman': ['LP', 'LLC'], 'Delaware': ['LP'], 'Luxembourg': ['SICAV'] }. |

#### 3. Apply a priority ordering rule within each jurisdiction that ranks entities by regulatory simplicity, tax efficiency, and investor familiarity.

| Category | Details |
| --- | --- |
| **Reason** | A deterministic ranking ensures consistent outputs across runs and aligns with industry best practices. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Assign a scoring matrix (e.g., regulatory=3, tax=2, investor=1) and compute a weighted sum for each candidate; choose the one with the highest score. |

#### 4. Select the top‑scoring entity type from the sorted list and assign it to the 'entity_type' output field.

| Category | Details |
| --- | --- |
| **Reason** | Directly mapping the highest score to output guarantees that the chosen structure is objectively justified. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | entity_type = sorted_entities[0]['type']. |

#### 5. Construct a one‑sentence explanation that references the jurisdiction, chosen entity, and the primary justification (e.g., regulatory simplicity).

| Category | Details |
| --- | --- |
| **Reason** | A concise justification satisfies the prompt requirement and aids downstream nodes that rely on narrative context. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use string interpolation: explanation = f'{jurisdiction} offers a {entity_type} structure that combines {primary_reason} for hedge‑fund operations.' |

#### 6. Validate that all output fields meet the defined data types: entity_type and jurisdiction as strings; explanation as a single‑sentence string; enforce type checks and raise descriptive errors if mismatched.

| Category | Details |
| --- | --- |
| **Reason** | Robust type validation prevents downstream failures and maintains data integrity throughout the DAG. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Implement a validation function that checks isinstance(field, str) and len(explanation.split('.')) == 1; log errors via a custom exception handler. |

#### 7. Return the outputs in the exact order and structure specified by the output_schema to ensure compatibility with child nodes.

| Category | Details |
| --- | --- |
| **Reason** | Maintaining consistent output ordering simplifies integration with downstream logic and reduces debugging effort. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Wrap outputs in an OrderedDict: {'entity_type': entity_type, 'jurisdiction': jurisdiction, 'explanation': explanation}. |


---

## clarify_fund_objectives

### Description
Produce a bullet list of the hedge fund's core objectives.

### Implementation Plan

#### 1. Parse the prompt to identify the instruction that the output must be a concise bullet list limited to no more than eight items.

| Category | Details |
| --- | --- |
| **Reason** | Ensures compliance with the explicit format constraints given in the prompt. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use a simple regex or string split to detect the keyword "max 8 bullets" and set a variable max_bullets = 8. |

#### 2. Extract the key thematic areas from the prompt: investment purpose, competitive edge, and long‑term vision.

| Category | Details |
| --- | --- |
| **Reason** | These are the only domains the objective bullets may reference; omitting them guarantees focus. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Tokenise the prompt, identify noun phrases, and map them to the three themes. |

#### 3. Generate objective statements using a template engine that inserts a short clause for each theme, ensuring each statement is self‑contained and does not mention strategy details.

| Category | Details |
| --- | --- |
| **Reason** | Keeps the content objective‑only while ensuring clarity and brevity. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Define template patterns such as "Achieve a net annual return of X% through disciplined risk management." and iterate over themes to produce up to max_bullets. |

#### 4. Trim or expand the list to exactly the number of bullets desired: if more than 8 statements are generated, merge or prune the least essential ones; if fewer than 8, add a generic objective about scalability or stakeholder engagement.

| Category | Details |
| --- | --- |
| **Reason** | Guarantees compliance with the maximum bullet count while covering all required domains. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Implement a loop that checks list length and applies merge rules (e.g., combine related clauses) or appends a predefined filler objective. |

#### 5. Count the final number of bullets and store in `objective_count`.

| Category | Details |
| --- | --- |
| **Reason** | The output schema requires a numeric count for downstream nodes. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use len(objectives) in the target language. |

#### 6. Return the `objectives` list and `objective_count` as a JSON object matching the specified output structure.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the node's output can be consumed by dependent nodes such as `choose_investment_strategy`. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Serialize the data using a standard JSON encoder. |


---

## compile_pitch_deck_outline

### Description
Framework for fundraising presentation.

### Implementation Plan

#### 1. Verify that all required parent outputs are present and non‑empty before proceeding.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that the downstream logic has the necessary data to construct meaningful slide titles. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Programmatically check that `clarify_fund_objectives.objectives`, `define_investor_profile.target_investor_segment`, `choose_investment_strategy.strategy_category`, `set_performance_and_risk_targets.gross_return`, `draft_fee_structure.management_fee_percentage`, and `design_risk_management_framework.risk_controls` exist and are of the expected type. |

#### 2. Extract high‑level messaging elements from each parent output to identify core narrative themes.

| Category | Details |
| --- | --- |
| **Reason** | These themes directly inform the slide titles and ensure each title aligns with the fund’s unique selling propositions. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Parse the list of objectives to select the top 3 most impactful bullets; capture the strategy category and rationale; pull target gross return, volatility, Sharpe ratio, and max drawdown; record the fee structure summary; and compile the first 4 risk control statements. |

#### 3. Define a canonical slide order based on investor deck best practices: Introduction, Overview, Objectives, Strategy, Team, Edge, Performance, Risk, Fees, Expected Returns.

| Category | Details |
| --- | --- |
| **Reason** | A consistent sequence improves narrative flow and meets investor expectations. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use a hard‑coded list of 10 titles as a template, with placeholders for dynamic terms. |

#### 4. Generate each slide title, inserting dynamic terms from parent data where relevant (e.g., strategy category, target gross return, risk limit keywords).

| Category | Details |
| --- | --- |
| **Reason** | Personalized titles increase engagement and signal that the deck is tailored to the fund’s specifics. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | String interpolation: replace `{strategy}` with the chosen strategy, `{return}` with the gross return percentage, and `{risk}` with the key risk control phrase. |

#### 5. Enforce title length constraints (≤ 7 words) and grammatical consistency (no trailing punctuation, proper capitalization).

| Category | Details |
| --- | --- |
| **Reason** | Short, punchy titles are easier to read and more visually appealing. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Token count per title, regex trimming of punctuation, title‑case conversion. |

#### 6. Validate that the final list contains exactly ten unique titles.

| Category | Details |
| --- | --- |
| **Reason** | Matches the specified output structure and prevents accidental duplication. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Count list length and check for duplicates via set comparison. |

#### 7. Package the validated list into the `slide_titles` output field and serialize to JSON.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the node’s contract is fulfilled and downstream nodes can consume the data. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Construct a dict with the key `slide_titles` mapping to the ordered list, then use a JSON library to output. |


---

## create_hiring_plan

### Description
Determine initial staffing requirements for the hedge fund launch.

### Implementation Plan

#### 1. Parse the input JSON from draft_operations_workflow to extract the two arrays: trade_lifecycle_steps and responsible_parties.

| Category | Details |
| --- | --- |
| **Reason** | These arrays provide the foundation for identifying which operational stages lack sufficient internal coverage. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use a JSON parser to map each step to its responsible party; store in a dictionary step_to_party. |

#### 2. Create a reference list of standard internal operational roles (e.g., Portfolio Analyst, Execution Trader, Risk Manager, Operations Coordinator, Compliance Officer, Fund Administrator Liaison, IT Systems Specialist, Finance & Accounting Lead).

| Category | Details |
| --- | --- |
| **Reason** | Having a pool of role templates streamlines role selection and ensures coverage of all workflow gaps. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Consult industry best‑practice staffing matrices for hedge funds and encode the list in a static array. |

#### 3. Identify workflow gaps by comparing each responsible_party with the internal role pool; if a party is 'GP' or an external provider (Prime Broker, Fund Admin, etc.), flag that step as a gap.

| Category | Details |
| --- | --- |
| **Reason** | Gap identification directly informs which positions must be filled internally. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Iterate over step_to_party; for each party that is not a core internal role, record the step as a gap in gap_list. |

#### 4. Map each identified gap to the most appropriate internal role from the reference list, ensuring that the role’s core responsibility covers the step’s function.

| Category | Details |
| --- | --- |
| **Reason** | Accurate mapping guarantees that responsibilities are neither duplicated nor omitted. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use a rule table: e.g., idea generation -> Portfolio Analyst, order entry -> Execution Trader, execution -> Execution Trader, confirmation -> Operations Coordinator, settlement -> Fund Administrator Liaison, reconciliation -> Risk Manager. Adjust for multiple gaps if necessary. |

#### 5. Limit the final list to a maximum of eight positions by prioritizing roles that cover multiple gaps or by consolidating closely related responsibilities (e.g., combining Compliance Officer with Operations Coordinator if resources are tight).

| Category | Details |
| --- | --- |
| **Reason** | The node constraint of 8 positions requires efficient role consolidation without losing critical coverage. |
| **Impact** | HIGH |
| **Complexity** | HIGH |
| **Method** | Score each role by the number of gaps it covers; select top N roles until reaching 8 or all gaps are addressed. |

#### 6. Generate the one-line responsibility description for each selected position by summarizing the mapped step(s) and the core duties of the role, e.g., "Lead execution of all equity orders, ensuring timely trade capture and reconciliation."

| Category | Details |
| --- | --- |
| **Reason** | Clear, concise responsibilities aid in hiring, performance management, and stakeholder communication. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Template strings per role: '{role}: {responsibility}' where responsibility is a concatenation of step names covered. |

#### 7. Populate the output fields: position_titles (list of role names), responsibility_descriptions (aligned list of responsibility strings), gap_alignment (list of corresponding trade_lifecycle_step names), and total_positions (integer count).

| Category | Details |
| --- | --- |
| **Reason** | Ensures compliance with the node’s specified output structure. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Construct parallel arrays; verify lengths match; compute total_positions as array length. |

#### 8. Validate that total_positions does not exceed 8; if it does, revisit role consolidation step to remove the least critical role, re‑generate responsibilities, and update the arrays accordingly.

| Category | Details |
| --- | --- |
| **Reason** | Guarantees node constraint compliance and avoids downstream errors. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Loop until len(position_titles) <= 8; use a priority threshold based on role seniority or gap coverage count. |


---

## define_asset_universe

### Description
Enumerate tradable assets and instruments for the selected hedge fund strategy.

### Implementation Plan

#### 1. Extract the `strategy_category` string from the output of the parent node `choose_investment_strategy`.

| Category | Details |
| --- | --- |
| **Reason** | The asset universe depends directly on the chosen strategy, so the first step is to acquire this value for subsequent lookup. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Access the parent node’s output dictionary via the execution engine’s dependency graph API; store the string in a local variable called `strategy`. |

#### 2. Validate the extracted `strategy` against a predefined whitelist of accepted strategy categories (e.g., "Long/Short Equity", "Global Macro", "Event‑Driven", "Statistical Arbitrage", "Fixed Income Arbitrage"). Reject or raise an error if the strategy is not in the whitelist.

| Category | Details |
| --- | --- |
| **Reason** | Ensures downstream asset mapping is defined and prevents mis‑specification. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Maintain a constant `VALID_STRATEGIES` list; use a simple membership test (`strategy in VALID_STRATEGIES`). |

#### 3. Lookup the canonical asset list for the validated strategy from a static mapping dictionary where keys are strategy names and values are ordered lists of asset classes/instruments (e.g., {'Long/Short Equity': ['US Large‑Cap Equities', 'UK FTSE 100', 'NASDAQ 100', 'S&P 500 Futures'], 'Global Macro': ['USD/EUR FX', 'US Treasury 10‑yr Futures', 'Gold Spot', 'Crude Oil WTI Futures']}).

| Category | Details |
| --- | --- |
| **Reason** | Provides a consistent, curated universe that aligns with industry best practices for each strategy type. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Implement the mapping as a Python dictionary (`STRATEGY_ASSET_MAP`) and retrieve with `STRATEGY_ASSET_MAP[strategy]`. |

#### 4. Enforce the maximum list size of 10 items: if the retrieved list has more than 10 elements, select the top‑10 based on a predetermined priority metric (e.g., liquidity volume, market capitalization, or default order defined in the mapping).

| Category | Details |
| --- | --- |
| **Reason** | Complies with the specification that the list must not exceed 10 items while preserving the most relevant instruments. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | If `len(asset_list) > 10`, slice the first 10 elements (`asset_list = asset_list[:10]`). If custom priority is required, apply a weighted sorting function before slicing. |

#### 5. Construct the output structure: assign the finalized asset list to the `assets` field and set `asset_count` to the length of the list.

| Category | Details |
| --- | --- |
| **Reason** | Provides the exact output format expected by downstream nodes. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Return a dictionary: `{'assets': asset_list, 'asset_count': len(asset_list)}`. |


---

## define_investor_profile

### Description
Describes the target investor segment for the hedge fund by extracting and synthesising investor characteristics from the fund’s strategic objectives.

### Implementation Plan

#### 1. Parse the objectives list from clarify_fund_objectives to extract investment purpose and target return profile.

| Category | Details |
| --- | --- |
| **Reason** | The investor segment must align with the fund’s stated purpose and return expectations. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use a rule‑based NLP extractor to identify keywords such as 'institutional', 'family office', 'high‑return', 'long‑term', and map them to a predefined investor archetype table. |

#### 2. Match the extracted archetype to a base investor profile template that includes default ranges for ticket size, risk tolerance, liquidity, and geographic focus.

| Category | Details |
| --- | --- |
| **Reason** | Standard templates provide consistent ranges that can be fine‑tuned against objectives. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Maintain a JSON dictionary of archetypes → template values; perform a lookup by archetype name. |

#### 3. Refine ticket size bounds by quantifying the fund’s target AUM and expected capital raise timeline from clarify_fund_objectives.

| Category | Details |
| --- | --- |
| **Reason** | Ticket sizes must be realistic given the fundraising window and target AUM. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Apply formula: min_ticket = 0.05 * target_AUM, max_ticket = 0.20 * target_AUM, clamp values to realistic market ranges ($1M‑$100M). |

#### 4. Determine risk tolerance level by evaluating the strategy’s volatility target from set_performance_and_risk_targets.

| Category | Details |
| --- | --- |
| **Reason** | Risk tolerance must be compatible with strategy risk metrics. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Map volatility percentage ranges to risk labels: <10% → low, 10–20% → moderate, >20% → high. |

#### 5. Infer liquidity preference from the fund’s investment horizon specified in choose_investment_strategy and set_performance_and_risk_targets.

| Category | Details |
| --- | --- |
| **Reason** | Liquidity preference must match the strategy’s holding period. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | If strategy is long/short equity with 1‑2 year horizon → long‑term; if global macro with 3‑6 month horizon → medium‑term. |

#### 6. Select geographic focus by correlating the fund’s domicile (choose_legal_entity_type/jurisdiction) and the target markets identified in define_asset_universe.

| Category | Details |
| --- | --- |
| **Reason** | Investors are more comfortable investing in familiar or aligned geographies. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Create a list of regions present in asset_universe; prioritize regions that match jurisdiction tax advantages and regulatory familiarity. |

#### 7. Validate all numeric outputs against realistic industry benchmarks (e.g., typical family office ticket size between $5M and $50M).

| Category | Details |
| --- | --- |
| **Reason** | Ensures the profile is credible and market‑consistent. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Compare computed ranges to benchmark table; if outliers exist, adjust using a safety factor of 0.8–1.2. |

#### 8. Compile the final profile record in the required output structure, ensuring type consistency (floats for ticket sizes, list of strings for geographic focus).

| Category | Details |
| --- | --- |
| **Reason** | Conforms to downstream node expectations and prevents type errors. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Serialize values into JSON; cast numeric strings to float; ensure geographic_focus is an array of strings. |


---

## define_technology_stack

### Description
Specify technology tools supporting operations.

### Implementation Plan

#### 1. Parse the parent node’s trade_lifecycle_steps into a local array, preserving order to maintain alignment with responsible parties.

| Category | Details |
| --- | --- |
| **Reason** | The output must reflect the exact sequence defined in the operations workflow. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use a simple list comprehension or copy operation; no transformation needed beyond preserving sequence. |

#### 2. Create a mapping dictionary that pairs each lifecycle step with its standard industry technology counterpart (e.g., Idea Generation → Strategy Analytics Platform, Order Entry → OMS, Execution → EMS, Confirmation → Confirmation System, Settlement → Custody & Clearing Platform, Reconciliation → Reconciliation Engine).

| Category | Details |
| --- | --- |
| **Reason** | Standardized pairings reduce ambiguity and ensure consistency with common hedge‑fund practice. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Define a static map in code; validate against a reference guide such as the Hedge Fund Operations Playbook (HFOP) or proprietary firm templates. |

#### 3. For each step, verify that the selected tech component satisfies the risk control requirements from the design_risk_management_framework node (e.g., risk limits, VaR calculations).

| Category | Details |
| --- | --- |
| **Reason** | Technology must support the quantitative controls defined elsewhere to avoid compliance gaps. |
| **Impact** | HIGH |
| **Complexity** | HIGH |
| **Method** | Cross‑reference risk_controls list; flag any mismatch; adjust component selection to include risk‑monitoring modules (e.g., embed risk engine into OMS). |

#### 4. If the parent node’s responsible_party for a step is an external provider (e.g., Prime Broker for Execution), append a note in tech_components indicating that the component will be accessed via the provider’s interface rather than an internal installation.

| Category | Details |
| --- | --- |
| **Reason** | Clarifies ownership and integration points for later implementation. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Append a string qualifier such as 'PrimeBroker EMS' to the component entry. |

#### 5. Generate two aligned lists: ops_steps (from the parsed workflow) and tech_components (from the mapping), ensuring array lengths match exactly.

| Category | Details |
| --- | --- |
| **Reason** | The output schema demands parallel arrays; any mismatch triggers downstream errors. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | After mapping, perform a length check; raise an exception or log error if lengths diverge. |

#### 6. Normalize component names to a consistent naming convention (e.g., Vendor‑Specific or Standardized Nomenclature) to aid in procurement and vendor management.

| Category | Details |
| --- | --- |
| **Reason** | Consistent naming avoids confusion during vendor selection and contract negotiations. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Apply a title‑case transformation; if vendor is unknown, use a placeholder like 'Custom OMS'. |

#### 7. Output the final two lists in JSON format, matching the defined output structure, and include a brief comment or placeholder for future versioning.

| Category | Details |
| --- | --- |
| **Reason** | Maintains compatibility with downstream nodes and allows easy integration with CI/CD pipelines. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Serialize using a JSON library; wrap lists under their respective keys. |

#### 8. Validate the output against a unit test that compares it against an expected reference for a sample workflow (e.g., Idea Generation, Order Entry, Execution, Confirmation, Settlement, Reconciliation).

| Category | Details |
| --- | --- |
| **Reason** | Ensures correctness and guards against regressions in future edits. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Create a pytest function that asserts equality of ops_steps and tech_components to predetermined values. |

#### 9. Document any assumptions about vendor availability or proprietary solutions, noting them in a side comment block for future reference.

| Category | Details |
| --- | --- |
| **Reason** | Transparency supports audit trails and future upgrades. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Embed comments in the code or add metadata key in output JSON. |


---

## design_compliance_program

### Description
Create compliance policies aligned with regulations and risk.

### Implementation Plan

#### 1. Validate and normalize the incoming lists: confirm that `compliance_requirements` is a list of strings and that `risk_controls` is a list of strings; strip whitespace, collapse duplicate entries, and ensure no empty strings are present.

| Category | Details |
| --- | --- |
| **Reason** | Ensures downstream mapping logic receives clean, deterministic inputs, reducing error risk in the mapping step. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use Python list comprehensions with `.strip()` and `set()` to deduplicate, then convert back to list; raise a validation error if types are incorrect. |

#### 2. Create a keyword-to-policy dictionary that maps common regulatory requirement themes (e.g., "recordkeeping", "conflict of interest", "cybersecurity", "AML") to internal policy names, drawing from the existing `risk_controls` list and a predefined compliance policy catalog.

| Category | Details |
| --- | --- |
| **Reason** | Provides a deterministic rule‑based foundation for the mapping, enabling consistent policy assignment across similar regulations. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Define a static dict in code; supplement with a lookup in `risk_controls` where applicable; for policies not in risk_controls, reference a compliance policy catalog file. |

#### 3. For each requirement in `compliance_requirements`, perform a fuzzy keyword match against the dictionary keys using Levenshtein distance or a simple case‑insensitive substring check; if a match is found, assign the corresponding policy reference; otherwise, default to a generic "Compliance Procedure" policy.

| Category | Details |
| --- | --- |
| **Reason** | Balances precision and flexibility, capturing variations in wording while ensuring every requirement gets a policy reference. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use Python's `difflib.get_close_matches` or `fuzzywuzzy` to compute similarity; threshold set to 0.8 for substring matches; fallback to generic policy. |

#### 4. Cross‑reference the assigned policy references with the `risk_controls` list to ensure that each policy is supported by a corresponding risk control; if a policy is missing a risk control, log a warning and append the policy to the `policy_references` list for review.

| Category | Details |
| --- | --- |
| **Reason** | Guarantees alignment between compliance obligations and risk management controls, a key governance requirement. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Iterate through `policy_references`, check membership in `risk_controls`; if absent, write to a diagnostics log. |

#### 5. Count the number of mapped pairs, set `mapping_count` to that integer, and compare lengths of `compliance_requirements` and `policy_references` to compute `is_consistent` as a Boolean flag.

| Category | Details |
| --- | --- |
| **Reason** | Provides a quick integrity check for downstream consumers of this node (e.g., the final summary). |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Python `len()` on each list; `is_consistent = len(compliance_requirements) == len(policy_references)`. |

#### 6. Return the structured output dictionary matching the specified `output_structure` order, ensuring the lists maintain original requirement order for traceability.

| Category | Details |
| --- | --- |
| **Reason** | Preserves order so that downstream nodes can correlate requirements to policies by index, simplifying auditing. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Construct a dict with keys in order, serialize to JSON or return as a Python dict; no transformation needed beyond previous steps. |


---

## design_risk_management_framework

### Description
Outline quantitative and qualitative risk controls.

### Implementation Plan

#### 1. Collect the numerical performance and risk targets from the parent node, specifically the annual gross return, volatility, Sharpe ratio, and maximum drawdown percentages, and store them in local variables.

| Category | Details |
| --- | --- |
| **Reason** | These metrics serve as the reference points for calibrating each risk control to the fund’s strategic objectives. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Parse JSON output of 'set_performance_and_risk_targets', assign values to variables: gross_return, volatility, sharpe_ratio, max_drawdown. |

#### 2. Define a position limit rule that caps the total exposure per trade as a fixed percentage of the total AUM, calculated as 5% of the target gross return divided by the target Sharpe ratio, rounded to the nearest 0.5%.

| Category | Details |
| --- | --- |
| **Reason** | Position limits prevent over‑concentration and tie exposure to expected risk‑adjusted performance. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Compute limit = round((gross_return / sharpe_ratio) * 0.05, 2). Ensure the result is expressed as a percentage of AUM. |

#### 3. Set a VaR limit at the 95% confidence level equal to 1% of the portfolio value, scaled by the square root of the target volatility to reflect expected market swings.

| Category | Details |
| --- | --- |
| **Reason** | VaR limits quantify potential loss within a confidence interval and are directly linked to volatility expectations. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | VaR_limit = 0.01 * sqrt(volatility) * portfolio_value. Format as a percentage of AUM. |

#### 4. Implement a stop‑loss rule that triggers an exit when a single trade’s unrealized loss exceeds 2% of its position size, or 1% of the total portfolio if the trade volatility exceeds the target volatility by more than 50%.

| Category | Details |
| --- | --- |
| **Reason** | Stop‑losses protect against unexpected adverse moves and adapt to trade‑specific risk. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Use trade‑level volatility estimate to adjust the stop threshold; apply the higher of the two percentage triggers. |

#### 5. Establish a liquidity threshold requiring that at least 20% of the portfolio remain in highly liquid instruments, ensuring the fund can meet liquidity demands within the maximum drawdown window.

| Category | Details |
| --- | --- |
| **Reason** | Liquidity thresholds safeguard against forced sales during stressed market conditions. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Maintain a separate liquid asset buffer; monitor daily liquidity ratio against the 20% benchmark. |

#### 6. Compile the formulated controls into a single list of string statements, each clearly referencing the associated metric and percentage, and assign this list to the 'risk_controls' output field.

| Category | Details |
| --- | --- |
| **Reason** | The final output must adhere to the defined output structure and provide a consumable risk control summary for downstream nodes. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Concatenate formatted strings: e.g., "Position limit: ≤ X% of AUM", "VaR limit: 95% VaR ≤ 1% of portfolio", etc.; set risk_controls = [list of strings]. |


---

## develop_timeline_and_milestones

### Description
Create phased schedule leading to fund launch.

### Implementation Plan

#### 1. Validate parent node outputs by confirming that each required field exists, is non‑null, and matches its declared type. Abort if any validation fails to prevent downstream errors.

| Category | Details |
| --- | --- |
| **Reason** | Ensures data integrity before constructing the timeline; prevents type errors when accessing list indices. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Implement type checks and None checks; log errors with descriptive messages. |

#### 2. Derive milestone counts from parent outputs: use `len(create_hiring_plan.total_positions)` for hiring span, `len(define_technology_stack.ops_steps)` for tech rollout, and `len(draft_operations_workflow.trade_lifecycle_steps)` for ops workflow finalization. Use `len(compile_pitch_deck_outline.slide_titles)` for pitch deck completion.

| Category | Details |
| --- | --- |
| **Reason** | Binds the schedule directly to concrete deliverables produced earlier, ensuring realistic pacing. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Apply Python `len()` to each list; store counts in local variables. |

#### 3. Assign baseline months to major deliverables: regulatory filing in month 2, pitch deck completion in month 4, service provider onboarding in months 3‑4, hiring over `total_positions` months starting month 3, ops workflow finalization in month 5, tech deployment over `ops_steps` months starting month 6, capital raise in month 9, and final go‑live in month 12.

| Category | Details |
| --- | --- |
| **Reason** | Provides a high‑level scaffold that respects typical industry timelines while incorporating data‑driven durations. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use conditional logic to adjust month indices if counts exceed allocated windows; store month assignments in a dictionary. |

#### 4. Generate each monthly milestone description by concatenating the month number with a human‑readable action string. For example, "Month 2: File regulatory registration with the jurisdictional authority.".

| Category | Details |
| --- | --- |
| **Reason** | Keeps the output format consistent and machine‑parseable for downstream nodes. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Loop over months 1‑12, using `f"Month {i}: {description}"` and append to a list. |

#### 5. Determine `final_go_live_month` by setting it to the last month with a non‑empty milestone. If all milestones complete by month 12, set to 12; otherwise adjust accordingly.

| Category | Details |
| --- | --- |
| **Reason** | Aligns go‑live month with the latest scheduled activity to avoid premature launch. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Identify the maximum month index used in the milestone dictionary. |

#### 6. Compute `overall_status` by verifying that every milestone month value is less than or equal to `final_go_live_month`. Return True if all are satisfied, otherwise False.

| Category | Details |
| --- | --- |
| **Reason** | Provides a quick pass/fail indicator for schedule feasibility. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Iterate over milestone months and compare against `final_go_live_month`; set flag accordingly. |

#### 7. Return the outputs in the defined order: `monthly_milestones`, `final_go_live_month`, `overall_status`. Ensure that the list of strings is sorted chronologically.

| Category | Details |
| --- | --- |
| **Reason** | Matches the output schema expected by downstream nodes and prevents re‑ordering errors. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Construct a dictionary with keys in the specified order and serialize to JSON. |


---

## draft_fee_structure

### Description
Set management and performance fee levels.

### Implementation Plan

#### 1. Extract and validate all numeric inputs from the two dependency outputs, converting them to floats and ensuring they are non‑negative.

| Category | Details |
| --- | --- |
| **Reason** | Ensures data integrity before any calculations; prevents type‑mismatch errors that would cascade to the final fee percentages. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Parse JSON, cast strings to float, apply `>= 0` checks, and log any anomalies. |

#### 2. Calculate `hurdle_rate_percentage` by setting a base hurdle of 5 % absolute return, but increase it to 5 % of the target gross return when the gross target is below 10 %. Cap the hurdle at 8 % to keep the structure attractive.

| Category | Details |
| --- | --- |
| **Reason** | Balances incentive alignment with risk‑adjusted return expectations while keeping the hurdle realistic for the chosen strategy. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Apply formula: `hurdle = min(8.0, max(5.0, gross_return * 0.5))` where `gross_return` is from `set_performance_and_risk_targets`. |

#### 3. Determine `management_fee_percentage` by first normalizing the total annual cost against a reference AUM of 100 M USD. If the cost ratio exceeds 3 % of AUM, set the fee to 2 %; otherwise set it to 1.5 %.

| Category | Details |
| --- | --- |
| **Reason** | Guarantees that management fees will cover operating expenses while remaining competitive relative to industry averages. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Compute `cost_ratio = total_estimated_annual_cost / 100_000_000 * 100`; then apply conditional assignment. |

#### 4. Set `performance_fee_percentage` to 20 % if the target Sharpe ratio is ≥ 1.0, otherwise 25 %. If the target maximum drawdown exceeds 25 %, increase the fee to 30 %.

| Category | Details |
| --- | --- |
| **Reason** | Aligns performance incentives with the risk‑return profile: lower risk yields a more attractive fee, whereas higher risk commands a premium. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Implement nested conditional logic using the Sharpe ratio and maximum drawdown values from `set_performance_and_risk_targets`. |

#### 5. Construct a `summary_sentence` that succinctly states the management fee, performance fee, and hurdle rate, limiting the output to no more than two sentences.

| Category | Details |
| --- | --- |
| **Reason** | Directly satisfies the prompt’s requirement for a concise summary. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Template string interpolation: "Our fund charges a {m_fee:.1f}% management fee, {p_fee:.1f}% performance fee above a {hurdle:.1f}% hurdle." |


---

## draft_operations_workflow

### Description
Map core trade and post-trade operational steps, assigning each lifecycle stage to its primary responsible party.

### Implementation Plan

#### 1. Extract the trade lifecycle step names from the fixed prompt template to ensure consistency across all downstream nodes.

| Category | Details |
| --- | --- |
| **Reason** | Guarantees that the output list order matches the expected sequence for later mapping and validation. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Store the steps as a constant array in code; validate against the prompt to catch typos. |

#### 2. Parse `define_asset_universe` output to verify the strategy’s asset class coverage before assigning responsibilities.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that execution and settlement responsibilities align with the specific instruments (e.g., equities vs futures). |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Deserialize the `assets` list; if any asset class requires a specialized custodian or prime broker, flag it for later mapping. |

#### 3. Parse `list_service_providers` output to create a lookup of available third‑party service provider categories.

| Category | Details |
| --- | --- |
| **Reason** | Facilitates accurate assignment of confirmation, settlement, and reconciliation to external providers. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Transform the provider list into a dictionary mapping provider type to role name. |

#### 4. Parse `design_risk_management_framework` output to identify risk control owners.

| Category | Details |
| --- | --- |
| **Reason** | Positions such as 'Risk Management System' or 'Compliance Officer' may take on monitoring responsibilities for steps like confirmation and settlement. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Extract risk control descriptors; map any that explicitly mention operational oversight to the responsible parties list. |

#### 5. Create a mapping table that pairs each lifecycle step to its default responsible party based on industry best practice and parent node outputs.

| Category | Details |
| --- | --- |
| **Reason** | Provides a reproducible rule set that can be reused for different strategies or jurisdictions. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Define a static mapping: idea generation → GP, order entry → Internal Ops (OMS), execution → GP/Prime Broker, confirmation → Prime Broker, settlement → Fund Administrator, reconciliation → Internal Ops. |

#### 6. Augment the default mapping with overrides derived from the provider and risk control lookups.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that if the strategy requires a specialized prime broker or an external reconciler, the assignment reflects that reality. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Iterate over the provider list; if a provider type matches a lifecycle step, replace the default party with the provider name. |

#### 7. Validate that each responsible party string is one of the allowed set {"GP", "Prime Broker", "Fund Administrator", "Internal Ops", "Custodian", "Auditor"}.

| Category | Details |
| --- | --- |
| **Reason** | Prevents downstream validation errors when the workflow is used to generate staffing plans or tech stacks. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use a set membership check and raise an informative error if an unexpected value is encountered. |

#### 8. Align the final `responsible_parties` array length with `trade_lifecycle_steps` length, ensuring 1:1 correspondence.

| Category | Details |
| --- | --- |
| **Reason** | Maintains data integrity and prevents misalignment in downstream nodes such as hiring plan or tech stack. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Assert that both lists have identical length; if not, log an error and halt execution. |

#### 9. Output the `trade_lifecycle_steps` and `responsible_parties` arrays in the exact order required by the node’s output schema.

| Category | Details |
| --- | --- |
| **Reason** | Guarantees that downstream nodes receive data in the expected structure without additional reordering. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Serialize the two lists to JSON arrays and return as node output. |

#### 10. Include unit tests that verify mapping correctness for at least two different asset universes and provider configurations.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that future changes to parent nodes do not break the workflow mapping logic. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Mock parent node outputs; assert expected `responsible_parties` for known inputs. |


---

## estimate_setup_and_operating_costs

### Description
Rough cost model for fund setup and operations.

### Implementation Plan

#### 1. Parse the input `service_providers` list from `list_service_providers` and verify it contains the expected provider categories.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that downstream calculations use a valid and complete set of provider types, preventing misalignment between expected and actual inputs. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use a simple validation step that checks for non‑empty string entries and removes duplicates; log a warning if unexpected values are found. |

#### 2. Define a static cost lookup table mapping each provider category to a mid‑point annual fee based on industry benchmarks (e.g., prime broker $200k, fund administrator $250k, auditor $80k, legal counsel $70k, compliance consultant $60k, custodian $30k).

| Category | Details |
| --- | --- |
| **Reason** | Provides a repeatable, auditable basis for cost estimation that reflects realistic market rates for a mid‑size hedge fund. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Create a dictionary in code; source rates from recent industry reports (e.g., Hedge Fund Research, Preqin) and adjust for currency if needed. |

#### 3. For each provider in the validated list, look up the corresponding fee in the lookup table and append the provider name to `cost_items` and the fee to `estimated_usd`.

| Category | Details |
| --- | --- |
| **Reason** | Directly translates provider categories into concrete cost items and amounts, ensuring output alignment with the required schema. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Iterate over `service_providers`, perform a dictionary lookup, and perform error handling for missing keys by defaulting to a conservative estimate. |

#### 4. Add overhead cost categories: office rent, utilities, and staff salaries; estimate each using region‑adjusted benchmarks (e.g., office $120k, tech infrastructure $150k, admin staff $200k).

| Category | Details |
| --- | --- |
| **Reason** | Overhead is a significant portion of annual expenses and must be represented to produce a realistic total cost. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use a small supplemental table for overhead categories, ensuring consistency with the provider lookup table. |

#### 5. Append the overhead categories to `cost_items` and their estimates to `estimated_usd`.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the final cost lists include all necessary items for transparency and completeness. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Extend the lists using the same loop mechanism used for providers. |

#### 6. Compute `total_estimated_annual_cost` by summing the numeric values in `estimated_usd`.

| Category | Details |
| --- | --- |
| **Reason** | Provides a single metric that will be used by downstream nodes (e.g., draft_fee_structure) for fee calibration. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use a functional aggregate (e.g., `sum(estimated_usd)`) and cast to float. |

#### 7. Validate that the lengths of `cost_items` and `estimated_usd` match and that all entries are non‑negative numbers before returning the output.

| Category | Details |
| --- | --- |
| **Reason** | Ensures data integrity and prevents downstream errors caused by malformed output. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Assert conditions; if validation fails, raise a descriptive exception or return a structured error payload. |


---

## identify_regulatory_requirements

### Description
Outline key regulatory filings and registrations.

### Implementation Plan

#### 1. Parse the parent node's output to extract the legal entity type and jurisdiction, normalizing the jurisdiction string to a canonical form (e.g., 'United States' → 'US', 'United Kingdom' → 'UK') and converting the entity type to a standard abbreviation (e.g., 'Limited Liability Company' → 'LLC').

| Category | Details |
| --- | --- |
| **Reason** | Accurate key extraction ensures that subsequent lookup operations target the correct regulatory mapping table, preventing misspellings and case‑sensitivity errors that would otherwise lead to missing or incorrect filings. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Implement a helper function that trims whitespace, converts to lowercase, and applies a predefined mapping dictionary for known jurisdiction names and entity type synonyms. Log any unknown values for audit. |

#### 2. Use a pre‑defined lookup table that maps each combination of jurisdiction and entity type to a tuple of (filing_name, governing_body). The table should cover the most common structures (LP, LLC, SICAV, partnership) and jurisdictions (US, UK, Cayman, Luxembourg, Delaware). For example, in the US an LLC or LP is required to register with the SEC via Form ADV; in the UK a UK‑based LP must register with the FCA; in Cayman a fund must register with the Cayman Islands Monetary Authority and may need to file with the Cayman Islands Securities Investment Business Licensing Authority if trading securities; in Luxembourg a SICAV must register with the CSSF.

| Category | Details |
| --- | --- |
| **Reason** | Centralizing regulatory requirements in a lookup table allows for deterministic and repeatable outputs, making the PRD easier to maintain and extend when new jurisdictions or entity types are added. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Create a nested dictionary such as `REG_REQUIREMENTS[jurisdiction][entity_type] = {'filing': 'SEC Form ADV', 'body': 'SEC'}`. Populate this dictionary with at least 8–10 jurisdiction–entity combinations. Include a default fallback that returns empty lists with a warning if the combination is not found. |

#### 3. Generate the final output lists by iterating over the lookup result for the identified combination. Return two aligned lists: `filing_names` containing the filing titles and `governing_bodies` containing the corresponding regulatory authority names. If the lookup returns no data, emit empty lists and optionally log an error to alert the user of missing regulatory information.

| Category | Details |
| --- | --- |
| **Reason** | Aligning the two output arrays ensures downstream nodes (e.g., design_compliance_program) can map each filing to a compliance requirement without ambiguity. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use a simple list comprehension: `filings = [entry['filing'] for entry in results]` and `bodies = [entry['body'] for entry in results]`. Wrap in a try/except block to capture and log any unexpected key errors. |


---

## list_service_providers

### Description
Enumerate required third-party service provider categories.

### Implementation Plan

#### 1. 1. Verify that the parent node `choose_legal_entity_type` has executed successfully and its output is available in the workflow context.

| Category | Details |
| --- | --- |
| **Reason** | The node depends on legal entity selection; ensuring its output prevents downstream failures. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Check the workflow state for a key named `choose_legal_entity_type`; if missing, throw a descriptive error and halt execution. |

#### 2. 2. Create a static list of service provider types exactly as specified in the prompt: ['Prime Broker', 'Fund Administrator', 'Auditor', 'Legal Counsel', 'Compliance Consultant', 'Custodian'].

| Category | Details |
| --- | --- |
| **Reason** | The prompt requires a hard‑coded checklist without descriptive text; using a static list guarantees consistency. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Instantiate the list in code, ensuring each element is a string with title‑case formatting to match typical provider names. |

#### 3. 3. Return the list as the value for the `service_providers` output field, confirming the data type matches `PrimitiveType.LIST_STR`.

| Category | Details |
| --- | --- |
| **Reason** | Proper type matching ensures downstream nodes consume the data without conversion errors. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Assign the static list to a dictionary key `service_providers` and serialize it if required by the workflow engine. |

#### 4. 4. Include basic validation that the list length is exactly six elements, matching the expected provider categories.

| Category | Details |
| --- | --- |
| **Reason** | This guards against accidental changes to the hard‑coded list that could break downstream logic. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Assert that `len(service_providers) == 6`; if not, raise a warning or error. |

#### 5. 5. Log the generated provider checklist for audit purposes, including a timestamp and parent node reference.

| Category | Details |
| --- | --- |
| **Reason** | Logging aids debugging and audit trails, especially when the list is used by subsequent cost estimation and operations workflow nodes. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use the workflow's logging facility to record the provider list and a reference to the parent node. |


---

## outline_governance_structure

### Description
Define internal governance roles and duties for the hedge fund, limited to a maximum of five roles. Each role should have a concise one‑sentence duty description.

### Implementation Plan

#### 1. Extract the entity type from the parent node choose_legal_entity_type and use it to decide whether a formal Board of Directors is required.

| Category | Details |
| --- | --- |
| **Reason** | The need for a Board is contingent on the legal structure (e.g., an LLC may not have a board while an LP typically has one). |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Parse the 'entity_type' field; if it is 'LP' or 'LLC', set board_needed=True; otherwise board_needed=False. |

#### 2. Create an ordered list of role names starting with GP and Investment Manager, then append Board if board_needed is True, followed by Compliance Officer and Advisory Committee, ensuring the list does not exceed five items.

| Category | Details |
| --- | --- |
| **Reason** | Maintaining a predictable order facilitates mapping duties to roles and ensures compliance with the 5‑role limit. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Instantiate role_names = ['GP', 'Investment Manager']; if board_needed: role_names.append('Board'); role_names.extend(['Compliance Officer', 'Advisory Committee']); truncate to first 5 elements. |

#### 3. Define a concise one‑sentence duty for each role using domain‑specific language: GP – oversees overall fund strategy; Investment Manager – executes trades and manages portfolio risk; Board – approves major strategy shifts and oversight; Compliance Officer – ensures regulatory compliance; Advisory Committee – provides industry insights.

| Category | Details |
| --- | --- |
| **Reason** | Clear, brief duties align with typical hedge fund governance practices and satisfy the prompt’s one‑sentence constraint. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Map role names to duty strings via a dictionary; then produce role_duties list in the same order as role_names. |

#### 4. Validate that the lengths of role_names and role_duties match; if not, truncate or adjust duties accordingly.

| Category | Details |
| --- | --- |
| **Reason** | Ensuring output consistency prevents downstream errors in later nodes that may consume this data. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Check len(role_names) == len(role_duties); if mismatch, raise an error or log warning and align them. |

#### 5. Return the role_names and role_duties arrays exactly as specified in the output structure, with no extraneous whitespace or formatting.

| Category | Details |
| --- | --- |
| **Reason** | Strict adherence to output schema guarantees seamless integration with downstream nodes. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Serialize lists into JSON-compatible arrays; trim strings; ensure no newlines inside duty descriptions. |


---

## produce_final_fund_plan_summary

### Description
Generate an all-in, concise executive summary of the hedge fund plan by integrating key outputs from the compliance program, pitch deck outline, and launch timeline.

### Implementation Plan

#### 1. Acquire the full output payloads from the three parent nodes: the compliance checklist, the 10-slide pitch deck outline, and the 12‑month timeline.

| Category | Details |
| --- | --- |
| **Reason** | These three inputs contain all the required context (strategy, structure, risk controls, operations milestones, and regulatory alignment) needed to craft an accurate summary. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Deserialize JSON objects returned by the parent nodes and store the fields: compliance_requirements, policy_references, slide_titles, monthly_milestones, final_go_live_month, overall_status. |

#### 2. Map each key summary element to the most relevant parent data: strategy → first slide title (or slide labeled ‘Strategy’); structure → slide labeled ‘Structure’; risk → any slide containing ‘Risk’ plus the compliance checklist; operations → slide titled ‘Operations’ plus monthly_milestones; fees → slide titled ‘Fees’ (or infer from slide list if present); timeline → final_go_live_month and a brief summary of monthly milestones.

| Category | Details |
| --- | --- |
| **Reason** | Direct mapping guarantees that the summary references explicit, validated content rather than inferred or ambiguous data. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Iterate through slide_titles and use string matching (case‑insensitive) to locate target keywords. For risk, concatenate compliance_requirements into a short list. For operations, generate a bullet summarizing the overall timeline status. |

#### 3. Construct a first draft of the executive summary using short, declarative sentences and bullet points, ensuring each paragraph/point covers one of the six focus areas: strategy, structure, risk, operations, fees, timeline.

| Category | Details |
| --- | --- |
| **Reason** | Bullet or short paragraph format is mandated by the prompt and improves readability for executive stakeholders. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Employ a template engine (e.g., Jinja2 or a simple string format) that inserts mapped content into predefined sentence structures. Keep each section under 50 words to provide a buffer before the final word count check. |

#### 4. Count words in the drafted summary. If the word count exceeds 400, iteratively prune or condense the longest sections (usually risk or operations) by removing non‑essential adjectives or phrases until the limit is met.

| Category | Details |
| --- | --- |
| **Reason** | The word limit is strict; exceeding it invalidates the output, so an automated check and adjustment loop is necessary. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Split the summary string by whitespace to obtain an array of words. If length > 400, identify sections with the highest word count using regex or string index ranges, then remove the longest 5–10 words per iteration. Re‑count until within limit. |

#### 5. Validate that the compliance mapping is consistent: if is_consistent is false, append a brief disclaimer noting potential gaps between regulatory requirements and internal policies.

| Category | Details |
| --- | --- |
| **Reason** | Stakeholders need to be aware of compliance alignment status; a missing disclaimer could misrepresent the fund’s readiness. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Check the boolean flag is_consistent from design_compliance_program. If false, add a sentence such as: “Note: The current compliance‑policy mapping shows an outstanding gap requiring remediation.” |

#### 6. Append a final sentence summarizing the go‑live status: e.g., “The fund is slated to go live in Month X, contingent upon the completion of all regulatory and operational milestones.”

| Category | Details |
| --- | --- |
| **Reason** | This ties the summary back to the concrete launch timeline, reinforcing the practical readiness of the plan. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Insert final sentence using final_go_live_month and overall_status; if overall_status is false, prepend “Pending completion of the following milestones: …” derived from monthly_milestones where the description indicates incomplete status. |

#### 7. Return the finalized executive_summary string and compute the final word_count integer for the JSON payload.

| Category | Details |
| --- | --- |
| **Reason** | These are the required output fields; they must be in the exact format to satisfy downstream nodes. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Package the summary string and word count into a JSON object with keys executive_summary and word_count, ensuring correct data types (str and int). |


---

## select_jurisdiction

### Description
Pick fund domicile and note rationale.

### Implementation Plan

#### 1. Validate the input by confirming that the 'objectives' field from clarify_fund_objectives is a non‑empty list of strings.

| Category | Details |
| --- | --- |
| **Reason** | Ensures we have the correct data type before proceeding with jurisdiction evaluation. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use a type‑check utility; if not list, raise a validation error. |

#### 2. Create an internal criteria matrix mapping each objective to a jurisdiction‑relevant factor (e.g., tax neutrality, regulatory burden, investor familiarity).

| Category | Details |
| --- | --- |
| **Reason** | Translates abstract objectives into concrete evaluation metrics. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Apply a lookup table: for each objective, assign a score weight (1–5) to factors; document the mapping in a JSON structure. |

#### 3. Instantiate a candidate jurisdiction pool: Cayman Islands, Delaware (USA), and Luxembourg.

| Category | Details |
| --- | --- |
| **Reason** | These are the most common domiciles for hedge funds and cover the main regulatory and tax regimes. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Define a static list in code; no external calls needed. |

#### 4. For each jurisdiction, compute a weighted score by multiplying each factor’s weight by the jurisdiction’s performance on that factor (e.g., 5 for tax‑neutrality, 3 for regulatory clarity).

| Category | Details |
| --- | --- |
| **Reason** | Provides a quantitative basis for comparison. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Implement a nested loop: outer over jurisdictions, inner over factors; sum weighted scores; store in a dictionary. |

#### 5. Select the jurisdiction with the highest aggregate score; if tied, prefer the one with lower tax burden.

| Category | Details |
| --- | --- |
| **Reason** | Ensures an objective, reproducible selection process. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use a simple max‑by‑key function; apply tie‑breaker logic. |

#### 6. Generate two concise pros and two cons by mapping the top positive and negative attributes of the chosen jurisdiction to the evaluation criteria.

| Category | Details |
| --- | --- |
| **Reason** | Aligns the pros/cons with the fund’s objectives, making the rationale transparent. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Select the two highest‑scoring positive factors as pros; pick two lowest‑scoring negative factors as cons; format each as a short sentence. |

#### 7. Craft a single‑sentence rationale summarizing the decision, highlighting how the chosen jurisdiction best satisfies the core objectives.

| Category | Details |
| --- | --- |
| **Reason** | Provides a clear, actionable justification for downstream nodes. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Combine the jurisdiction name with a phrase like "best balances tax neutrality and regulatory flexibility to meet objective X". |

#### 8. Populate the output structure fields: set jurisdiction to the selected name; assign pros and cons lists; insert rationale string.

| Category | Details |
| --- | --- |
| **Reason** | Converts internal variables into the node’s defined output format. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Map variables to the corresponding keys; ensure list types are correctly typed as PrimitiveType.LIST_STR. |


---

## set_performance_and_risk_targets

### Description
Quantify return and risk goals.

### Implementation Plan

#### 1. Parse the output of the parent node `choose_investment_strategy` to identify the selected strategy category and its qualitative performance benchmarks.

| Category | Details |
| --- | --- |
| **Reason** | The risk and return targets must be calibrated to the chosen strategy; hence we need the strategy name and any high‑level benchmark references. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Read the `strategy_category` field from the parent’s output; if the strategy includes a benchmark (e.g., S&P 500 for Long/Short Equity), retrieve its historical annualized return, volatility, and Sharpe ratio from a pre‑loaded database. Use these figures as a baseline for target setting. |

#### 2. Define a target gross return that is 5% above the strategy’s historical mean return, but capped at a realistic maximum of 30% to maintain credibility.

| Category | Details |
| --- | --- |
| **Reason** | Setting targets modestly higher than historical performance provides ambition without overpromising. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Calculate mean annual return (μ) from historical data; set `gross_return = min(μ + 5, 30.0)`. |

#### 3. Set volatility to 20–30% higher than the strategy’s historical volatility to account for future uncertainty, with an upper bound of 25% to avoid extreme risk appetite.

| Category | Details |
| --- | --- |
| **Reason** | Risk targets should reflect a conservative margin over past volatility while ensuring the fund is not perceived as excessively risky. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Compute historical σ; set `volatility = min(σ * 1.2, 25.0)`. |

#### 4. Derive the Sharpe ratio target as the historical Sharpe ratio plus 0.1, limited to a maximum of 2.0 to maintain realistic expectations.

| Category | Details |
| --- | --- |
| **Reason** | Sharpe ratio is a key performance metric; a modest increase signals performance improvement without being overly optimistic. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Retrieve historical Sharpe S; set `sharpe_ratio = min(S + 0.1, 2.0)`. |

#### 5. Define maximum drawdown as 50% of the historical peak‑to‑trough drawdown, but not exceeding 45% to keep the target achievable.

| Category | Details |
| --- | --- |
| **Reason** | Drawdown tolerance should be moderate; tying it to historical extremes ensures realism. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Calculate historical D; set `max_drawdown = min(D * 0.5, 45.0)`. |

#### 6. Validate that the resulting target metrics are internally consistent: volatility should be >= target gross return divided by Sharpe ratio, and max_drawdown should be <= 3× volatility to avoid overly aggressive targets.

| Category | Details |
| --- | --- |
| **Reason** | Consistency checks prevent contradictory metrics that could mislead stakeholders. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Perform the two checks; if either fails, adjust volatility downwards or gross_return upwards within the defined bounds until all conditions hold. |

#### 7. Format the four numerical outputs into a plain 4‑row table, rounding each value to one decimal place and appending a percentage sign for clarity.

| Category | Details |
| --- | --- |
| **Reason** | The prompt explicitly requests a table; formatting improves readability for downstream nodes. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Generate a string: `| Metric | Target |
|-------|--------|
| Gross Return | X.X% |
| Volatility | Y.Y% |
| Sharpe Ratio | Z.Z |
| Max Drawdown | W.W% |`. |

#### 8. Populate the JSON output structure with the computed float values (without percentage signs) to satisfy the downstream node type requirements.

| Category | Details |
| --- | --- |
| **Reason** | While the table is for human consumption, the programmatic output must be in raw numeric form. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Assign `gross_return`, `volatility`, `sharpe_ratio`, and `max_drawdown` to the JSON payload as floats. |
