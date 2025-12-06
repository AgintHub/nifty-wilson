# choose_legal_entity_type PRD

## Description
Identify legal structure for the hedge fund vehicle based on the chosen domicile, balancing regulatory fit, tax efficiency, and operational simplicity.


## Implementation Plan

### 1. Retrieve the jurisdiction value from the output of the parent node 'select_jurisdiction' and store it as a string variable.

| Category | Details |
| --- | --- |
| **Reason** | The jurisdiction drives the available legal entity options; retrieving it ensures the node works with the most current choice. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use a simple JSON path extraction: jurisdiction = parent_outputs['select_jurisdiction']['jurisdiction']. |

### 2. Create a jurisdiction‑entity compatibility lookup table that maps each jurisdiction to its commonly used hedge‑fund structures (e.g., Cayman → LP/LLC; Delaware → LP; Luxembourg → SICAV).

| Category | Details |
| --- | --- |
| **Reason** | Hard‑coding a small, curated table avoids expensive API calls and ensures quick, deterministic decision‑making. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Define a static dictionary in the node’s code: compat = { 'Cayman': ['LP', 'LLC'], 'Delaware': ['LP'], 'Luxembourg': ['SICAV'] }. |

### 3. Apply a priority ordering rule within each jurisdiction that ranks entities by regulatory simplicity, tax efficiency, and investor familiarity.

| Category | Details |
| --- | --- |
| **Reason** | A deterministic ranking ensures consistent outputs across runs and aligns with industry best practices. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Assign a scoring matrix (e.g., regulatory=3, tax=2, investor=1) and compute a weighted sum for each candidate; choose the one with the highest score. |

### 4. Select the top‑scoring entity type from the sorted list and assign it to the 'entity_type' output field.

| Category | Details |
| --- | --- |
| **Reason** | Directly mapping the highest score to output guarantees that the chosen structure is objectively justified. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | entity_type = sorted_entities[0]['type']. |

### 5. Construct a one‑sentence explanation that references the jurisdiction, chosen entity, and the primary justification (e.g., regulatory simplicity).

| Category | Details |
| --- | --- |
| **Reason** | A concise justification satisfies the prompt requirement and aids downstream nodes that rely on narrative context. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use string interpolation: explanation = f'{jurisdiction} offers a {entity_type} structure that combines {primary_reason} for hedge‑fund operations.' |

### 6. Validate that all output fields meet the defined data types: entity_type and jurisdiction as strings; explanation as a single‑sentence string; enforce type checks and raise descriptive errors if mismatched.

| Category | Details |
| --- | --- |
| **Reason** | Robust type validation prevents downstream failures and maintains data integrity throughout the DAG. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Implement a validation function that checks isinstance(field, str) and len(explanation.split('.')) == 1; log errors via a custom exception handler. |

### 7. Return the outputs in the exact order and structure specified by the output_schema to ensure compatibility with child nodes.

| Category | Details |
| --- | --- |
| **Reason** | Maintaining consistent output ordering simplifies integration with downstream logic and reduces debugging effort. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Wrap outputs in an OrderedDict: {'entity_type': entity_type, 'jurisdiction': jurisdiction, 'explanation': explanation}. |
