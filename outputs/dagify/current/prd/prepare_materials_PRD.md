# prepare_materials PRD

## Description
Prepare the necessary materials and equipment required for the experiment based on the design specifications.


## Implementation Plan

### 1. Retrieve the full design_experiment output and deserialize the JSON into an in-memory object.

| Category | Details |
| --- | --- |
| **Reason** | The design_experiment output contains the experiment variables and protocol which dictate material requirements. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use a JSON parser to load design_experiment JSON into a dictionary or a typed data class. Validate all required keys exist. |

### 2. Map each measurement method and dependent variable to its specific instrument or consumable (e.g., a pH meter for pH measurement).

| Category | Details |
| --- | --- |
| **Reason** | Accurately linking measurement needs to physical items ensures no gaps in equipment. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Implement a lookup table (dictionary) mapping variable names to instrument/consumable types. Apply fallback rules for unspecified variables. |

### 3. Enumerate required reagents, chemicals, and labware by cross-referencing independent variables, dependent variables, and sample size.

| Category | Details |
| --- | --- |
| **Reason** | The quantity of consumables depends on how many samples and repetitions are planned. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | For each sample unit, multiply reagent volumes by sample_size. Add safety margins (e.g., +10%). Use unit conversion functions to standardize measurements. |

### 4. Validate availability of each item by querying the laboratory inventory system (or a static inventory list).

| Category | Details |
| --- | --- |
| **Reason** | Prevents delays during execution due to missing items. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Call an inventory API or read a CSV of available items. If an item is out of stock, flag a warning and suggest an alternative or reorder. |

### 5. Calculate the cost of each item by multiplying the unit price by the required quantity.

| Category | Details |
| --- | --- |
| **Reason** | Provides a financial estimate needed for budgeting. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Store unit prices in a price catalog dictionary. Perform arithmetic operations and sum totals. Round to two decimal places. |

### 6. Aggregate all items, quantities, and costs into the required_items, quantities, and total_cost output fields.

| Category | Details |
| --- | --- |
| **Reason** | Organizes data into the defined output structure for downstream nodes. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Append each item, quantity, and cost to respective lists; compute total_cost as sum of item costs. |

### 7. Set is_prepared to True only after confirming all items are available, quantities match calculations, and cost estimate is finalized.

| Category | Details |
| --- | --- |
| **Reason** | Guarantees that the experiment will not halt due to missing resources. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | If any availability check fails or quantity mismatch occurs, set is_prepared to False and record details in preparation_notes. |

### 8. Compile a detailed preparation_notes string that logs any substitutions, special handling instructions, or procurement actions taken.

| Category | Details |
| --- | --- |
| **Reason** | Provides traceability and context for future troubleshooting. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Concatenate status messages from prior steps, include timestamps, and format as a multiline string. |
