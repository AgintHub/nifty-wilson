# estimate_setup_and_operating_costs PRD

## Description
Rough cost model for fund setup and operations.


## Implementation Plan

### 1. Parse the input `service_providers` list from `list_service_providers` and verify it contains the expected provider categories.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that downstream calculations use a valid and complete set of provider types, preventing misalignment between expected and actual inputs. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use a simple validation step that checks for non‑empty string entries and removes duplicates; log a warning if unexpected values are found. |

### 2. Define a static cost lookup table mapping each provider category to a mid‑point annual fee based on industry benchmarks (e.g., prime broker $200k, fund administrator $250k, auditor $80k, legal counsel $70k, compliance consultant $60k, custodian $30k).

| Category | Details |
| --- | --- |
| **Reason** | Provides a repeatable, auditable basis for cost estimation that reflects realistic market rates for a mid‑size hedge fund. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Create a dictionary in code; source rates from recent industry reports (e.g., Hedge Fund Research, Preqin) and adjust for currency if needed. |

### 3. For each provider in the validated list, look up the corresponding fee in the lookup table and append the provider name to `cost_items` and the fee to `estimated_usd`.

| Category | Details |
| --- | --- |
| **Reason** | Directly translates provider categories into concrete cost items and amounts, ensuring output alignment with the required schema. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Iterate over `service_providers`, perform a dictionary lookup, and perform error handling for missing keys by defaulting to a conservative estimate. |

### 4. Add overhead cost categories: office rent, utilities, and staff salaries; estimate each using region‑adjusted benchmarks (e.g., office $120k, tech infrastructure $150k, admin staff $200k).

| Category | Details |
| --- | --- |
| **Reason** | Overhead is a significant portion of annual expenses and must be represented to produce a realistic total cost. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use a small supplemental table for overhead categories, ensuring consistency with the provider lookup table. |

### 5. Append the overhead categories to `cost_items` and their estimates to `estimated_usd`.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the final cost lists include all necessary items for transparency and completeness. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Extend the lists using the same loop mechanism used for providers. |

### 6. Compute `total_estimated_annual_cost` by summing the numeric values in `estimated_usd`.

| Category | Details |
| --- | --- |
| **Reason** | Provides a single metric that will be used by downstream nodes (e.g., draft_fee_structure) for fee calibration. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use a functional aggregate (e.g., `sum(estimated_usd)`) and cast to float. |

### 7. Validate that the lengths of `cost_items` and `estimated_usd` match and that all entries are non‑negative numbers before returning the output.

| Category | Details |
| --- | --- |
| **Reason** | Ensures data integrity and prevents downstream errors caused by malformed output. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Assert conditions; if validation fails, raise a descriptive exception or return a structured error payload. |
