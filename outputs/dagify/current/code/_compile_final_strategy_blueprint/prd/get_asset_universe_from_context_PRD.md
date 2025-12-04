# get_asset_universe_from_context PRD

## Description
Extracts the list of tradable asset identifiers from the execution context supplied to the node.


## Implementation Plan

### 1. Read the asset universe from a well‑known key (e.g., `asset_universe`) within **kwargs** and return it directly.

| Category | Details |
| --- | --- |
| **Reason** | The downstream `compile_final_strategy_blueprint` node requires this list to build the final blueprint. |
| **Impact** | Provides a deterministic source of tradable symbols, preventing missing‑data errors later in the pipeline. |
| **Complexity** | LOW |
| **Method** | Implement a simple dictionary lookup: `asset_tickers = kwargs.get('asset_universe', [])`; if the key is absent, return an empty list or raise a clear exception. |

### 2. Validate the extracted list to ensure all entries are non‑empty strings and that the list contains unique symbols.

| Category | Details |
| --- | --- |
| **Reason** | Invalid or duplicated tickers can cause back‑testing failures and inaccurate risk calculations. |
| **Impact** | Guarantees data integrity for all downstream components that iterate over the asset universe. |
| **Complexity** | MEDIUM |
| **Method** | Iterate over the list, strip whitespace, filter out falsy values, and use a `set` to detect duplicates; raise a `ValueError` with a helpful message if validation fails. |

### 3. Accept flexible input formats (list, comma‑separated string, or JSON‑encoded string) and normalize them to a `List[str]`.

| Category | Details |
| --- | --- |
| **Reason** | Different upstream nodes or user‑provided contexts may supply the universe in varied representations. |
| **Impact** | Increases robustness and reduces coupling, allowing the shim to be reused across multiple workflows. |
| **Complexity** | MEDIUM |
| **Method** | Detect the type of the retrieved value: if `list`, use as‑is; if `str`, split on commas and strip spaces; if JSON‑parsable, `json.loads` to a list; then apply the validation logic from the previous bullet. |
