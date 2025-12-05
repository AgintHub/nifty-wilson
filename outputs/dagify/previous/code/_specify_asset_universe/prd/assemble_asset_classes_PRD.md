# assemble_asset_classes PRD

## Description
Assembles, deduplicates, and orders the final list of asset class identifiers for the selected trading strategy.


## Implementation Plan

### 1. Parse the input string into a list, trim whitespace, and remove empty entries.

| Category | Details |
| --- | --- |
| **Reason** | Raw user‑provided strings may contain irregular spacing or stray commas that would corrupt downstream processing. |
| **Impact** | Ensures downstream nodes receive a clean list, preventing errors in ticker generation and validation. |
| **Complexity** | LOW |
| **Method** | Split the string on commas, strip each element, and filter out falsy values using standard Python list comprehensions. |

### 2. Deduplicate the list while preserving a deterministic order (e.g., alphabetical).

| Category | Details |
| --- | --- |
| **Reason** | Duplicate asset classes can cause redundant work and ambiguous ordering; a stable order is required for reproducibility. |
| **Impact** | Provides a unique, predictable sequence of asset classes, simplifying caching and testing. |
| **Complexity** | MEDIUM |
| **Method** | Convert the list to a set to drop duplicates, then sort the set alphabetically before returning. |

### 3. Validate each asset class against an allowed‑asset‑class whitelist.

| Category | Details |
| --- | --- |
| **Reason** | Only recognized asset classes should be passed to later nodes to avoid downstream lookup failures. |
| **Impact** | Filters out unsupported classes early, reducing downstream errors and improving overall system reliability. |
| **Complexity** | MEDIUM |
| **Method** | Maintain a constant list or dictionary of permitted asset class strings and filter the sorted list accordingly, logging any removals. |
