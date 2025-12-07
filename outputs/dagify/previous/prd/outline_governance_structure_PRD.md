# outline_governance_structure PRD

## Description
Define internal governance roles and duties for the hedge fund, limited to a maximum of five roles. Each role should have a concise one‑sentence duty description.


## Implementation Plan

### 1. Extract the entity type from the parent node choose_legal_entity_type and use it to decide whether a formal Board of Directors is required.

| Category | Details |
| --- | --- |
| **Reason** | The need for a Board is contingent on the legal structure (e.g., an LLC may not have a board while an LP typically has one). |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Parse the 'entity_type' field; if it is 'LP' or 'LLC', set board_needed=True; otherwise board_needed=False. |

### 2. Create an ordered list of role names starting with GP and Investment Manager, then append Board if board_needed is True, followed by Compliance Officer and Advisory Committee, ensuring the list does not exceed five items.

| Category | Details |
| --- | --- |
| **Reason** | Maintaining a predictable order facilitates mapping duties to roles and ensures compliance with the 5‑role limit. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Instantiate role_names = ['GP', 'Investment Manager']; if board_needed: role_names.append('Board'); role_names.extend(['Compliance Officer', 'Advisory Committee']); truncate to first 5 elements. |

### 3. Define a concise one‑sentence duty for each role using domain‑specific language: GP – oversees overall fund strategy; Investment Manager – executes trades and manages portfolio risk; Board – approves major strategy shifts and oversight; Compliance Officer – ensures regulatory compliance; Advisory Committee – provides industry insights.

| Category | Details |
| --- | --- |
| **Reason** | Clear, brief duties align with typical hedge fund governance practices and satisfy the prompt’s one‑sentence constraint. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Map role names to duty strings via a dictionary; then produce role_duties list in the same order as role_names. |

### 4. Validate that the lengths of role_names and role_duties match; if not, truncate or adjust duties accordingly.

| Category | Details |
| --- | --- |
| **Reason** | Ensuring output consistency prevents downstream errors in later nodes that may consume this data. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Check len(role_names) == len(role_duties); if mismatch, raise an error or log warning and align them. |

### 5. Return the role_names and role_duties arrays exactly as specified in the output structure, with no extraneous whitespace or formatting.

| Category | Details |
| --- | --- |
| **Reason** | Strict adherence to output schema guarantees seamless integration with downstream nodes. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Serialize lists into JSON-compatible arrays; trim strings; ensure no newlines inside duty descriptions. |
