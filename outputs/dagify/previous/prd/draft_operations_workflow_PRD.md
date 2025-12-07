# draft_operations_workflow PRD

## Description
Map core trade and post-trade operational steps, assigning each lifecycle stage to its primary responsible party.


## Implementation Plan

### 1. Extract the trade lifecycle step names from the fixed prompt template to ensure consistency across all downstream nodes.

| Category | Details |
| --- | --- |
| **Reason** | Guarantees that the output list order matches the expected sequence for later mapping and validation. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Store the steps as a constant array in code; validate against the prompt to catch typos. |

### 2. Parse `define_asset_universe` output to verify the strategy’s asset class coverage before assigning responsibilities.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that execution and settlement responsibilities align with the specific instruments (e.g., equities vs futures). |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Deserialize the `assets` list; if any asset class requires a specialized custodian or prime broker, flag it for later mapping. |

### 3. Parse `list_service_providers` output to create a lookup of available third‑party service provider categories.

| Category | Details |
| --- | --- |
| **Reason** | Facilitates accurate assignment of confirmation, settlement, and reconciliation to external providers. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Transform the provider list into a dictionary mapping provider type to role name. |

### 4. Parse `design_risk_management_framework` output to identify risk control owners.

| Category | Details |
| --- | --- |
| **Reason** | Positions such as 'Risk Management System' or 'Compliance Officer' may take on monitoring responsibilities for steps like confirmation and settlement. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Extract risk control descriptors; map any that explicitly mention operational oversight to the responsible parties list. |

### 5. Create a mapping table that pairs each lifecycle step to its default responsible party based on industry best practice and parent node outputs.

| Category | Details |
| --- | --- |
| **Reason** | Provides a reproducible rule set that can be reused for different strategies or jurisdictions. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Define a static mapping: idea generation → GP, order entry → Internal Ops (OMS), execution → GP/Prime Broker, confirmation → Prime Broker, settlement → Fund Administrator, reconciliation → Internal Ops. |

### 6. Augment the default mapping with overrides derived from the provider and risk control lookups.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that if the strategy requires a specialized prime broker or an external reconciler, the assignment reflects that reality. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Iterate over the provider list; if a provider type matches a lifecycle step, replace the default party with the provider name. |

### 7. Validate that each responsible party string is one of the allowed set {"GP", "Prime Broker", "Fund Administrator", "Internal Ops", "Custodian", "Auditor"}.

| Category | Details |
| --- | --- |
| **Reason** | Prevents downstream validation errors when the workflow is used to generate staffing plans or tech stacks. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use a set membership check and raise an informative error if an unexpected value is encountered. |

### 8. Align the final `responsible_parties` array length with `trade_lifecycle_steps` length, ensuring 1:1 correspondence.

| Category | Details |
| --- | --- |
| **Reason** | Maintains data integrity and prevents misalignment in downstream nodes such as hiring plan or tech stack. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Assert that both lists have identical length; if not, log an error and halt execution. |

### 9. Output the `trade_lifecycle_steps` and `responsible_parties` arrays in the exact order required by the node’s output schema.

| Category | Details |
| --- | --- |
| **Reason** | Guarantees that downstream nodes receive data in the expected structure without additional reordering. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Serialize the two lists to JSON arrays and return as node output. |

### 10. Include unit tests that verify mapping correctness for at least two different asset universes and provider configurations.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that future changes to parent nodes do not break the workflow mapping logic. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Mock parent node outputs; assert expected `responsible_parties` for known inputs. |
