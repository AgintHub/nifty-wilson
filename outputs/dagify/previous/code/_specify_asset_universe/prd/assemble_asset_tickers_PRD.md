# assemble_asset_tickers PRD

## Description
Creates the final ordered list of asset ticker symbols from the provided validated tickers input.


## Implementation Plan

### 1. Parse the validated_tickers string into an array of individual ticker symbols.

| Category | Details |
| --- | --- |
| **Reason** | The upstream validator returns tickers as a single string; we need a structured list for further processing. |
| **Impact** | Enables downstream nodes to iterate over tickers reliably and prevents string‑handling bugs. |
| **Complexity** | LOW |
| **Method** | Split the string on commas and whitespace, trim each token, and filter out empty entries using Python's str.split and list comprehension. |

### 2. Deduplicate and sort the ticker list to ensure deterministic ordering.

| Category | Details |
| --- | --- |
| **Reason** | Duplicate symbols or nondeterministic order can cause inconsistent portfolio generation and cache misses. |
| **Impact** | Guarantees reproducible results across runs and simplifies comparison of generated portfolios. |
| **Complexity** | MEDIUM |
| **Method** | Convert the list to a set to remove duplicates, then back to a list and apply sorted() (or a custom alphabetical/sector‑based ordering if required). |

### 3. Validate final ticker format and raise a clear error if any symbol violates expected patterns.

| Category | Details |
| --- | --- |
| **Reason** | Even after upstream validation, malformed symbols could slip through due to edge‑case characters. |
| **Impact** | Prevents downstream API calls (e.g., Yahoo Finance) from failing unexpectedly, improving overall robustness. |
| **Complexity** | MEDIUM |
| **Method** | Use a regular expression such as ^[A-Z]{1,5}(\.[A-Z]{1,2})?$ to check each ticker; collect invalid entries and raise a ValueError with a descriptive message. |
