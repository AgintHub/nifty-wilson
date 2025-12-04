# list_service_providers PRD

## Description
Enumerate required third-party service provider categories.


## Implementation Plan

### 1. 1. Verify that the parent node `choose_legal_entity_type` has executed successfully and its output is available in the workflow context.

| Category | Details |
| --- | --- |
| **Reason** | The node depends on legal entity selection; ensuring its output prevents downstream failures. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Check the workflow state for a key named `choose_legal_entity_type`; if missing, throw a descriptive error and halt execution. |

### 2. 2. Create a static list of service provider types exactly as specified in the prompt: ['Prime Broker', 'Fund Administrator', 'Auditor', 'Legal Counsel', 'Compliance Consultant', 'Custodian'].

| Category | Details |
| --- | --- |
| **Reason** | The prompt requires a hard‑coded checklist without descriptive text; using a static list guarantees consistency. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Instantiate the list in code, ensuring each element is a string with title‑case formatting to match typical provider names. |

### 3. 3. Return the list as the value for the `service_providers` output field, confirming the data type matches `PrimitiveType.LIST_STR`.

| Category | Details |
| --- | --- |
| **Reason** | Proper type matching ensures downstream nodes consume the data without conversion errors. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Assign the static list to a dictionary key `service_providers` and serialize it if required by the workflow engine. |

### 4. 4. Include basic validation that the list length is exactly six elements, matching the expected provider categories.

| Category | Details |
| --- | --- |
| **Reason** | This guards against accidental changes to the hard‑coded list that could break downstream logic. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Assert that `len(service_providers) == 6`; if not, raise a warning or error. |

### 5. 5. Log the generated provider checklist for audit purposes, including a timestamp and parent node reference.

| Category | Details |
| --- | --- |
| **Reason** | Logging aids debugging and audit trails, especially when the list is used by subsequent cost estimation and operations workflow nodes. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use the workflow's logging facility to record the provider list and a reference to the parent node. |
