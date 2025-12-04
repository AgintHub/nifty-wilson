# _specify_asset_universe - Complete PRD Documentation

## Overview
PRDs for nodes in the '_specify_asset_universe' module.

## Table of Contents

- [extract_strategy_type](#extract_strategy_type)

- [create_strategy_asset_mapping](#create_strategy_asset_mapping)

- [lookup_strategy_mapping](#lookup_strategy_mapping)

- [generate_candidate_tickers](#generate_candidate_tickers)

- [validate_tickers_yahoo_finance](#validate_tickers_yahoo_finance)

- [assemble_asset_classes](#assemble_asset_classes)

- [assemble_asset_tickers](#assemble_asset_tickers)



---

## extract_strategy_type

### Description
Extracts the strategy_type field from a SelectTradingStrategyTypeOutput object and returns it as a string.

### Implementation Plan

#### 1. Parse the input_data JSON string into a Python object and safely retrieve the `strategy_type` attribute.

| Category | Details |
| --- | --- |
| **Reason** | The shim receives data as a raw string; parsing is required to access structured fields. |
| **Impact** | Ensures downstream nodes receive a clean, correctly‑typed strategy identifier. |
| **Complexity** | LOW |
| **Method** | Use `json.loads` to deserialize the string, then access `obj["strategy_type"]` with a fallback default or raise a clear ValueError if missing. |

#### 2. Validate that the extracted strategy_type is a non‑empty string and belongs to an allowed set of strategy identifiers.

| Category | Details |
| --- | --- |
| **Reason** | Invalid or misspelled strategy types would break later mapping logic. |
| **Impact** | Prevents runtime errors in `create_strategy_asset_mapping` and improves overall pipeline robustness. |
| **Complexity** | MEDIUM |
| **Method** | Define an immutable list of supported strategies (e.g., ["momentum", "mean_reversion", "arbitrage"]). After extraction, check `isinstance(value, str) and value.strip() and value in SUPPORTED_STRATEGIES`; raise a custom `InvalidStrategyError` if the check fails. |


---

## create_strategy_asset_mapping

### Description
Returns a static dictionary mapping each trading strategy type to a list of compatible asset classes.

### Implementation Plan

#### 1. Define a hard‑coded dictionary that lists supported strategy types and their associated asset classes.

| Category | Details |
| --- | --- |
| **Reason** | Provides a deterministic source for downstream asset‑universe selection. |
| **Impact** | Ensures consistent mapping across runs and simplifies debugging. |
| **Complexity** | LOW |
| **Method** | Create a Python dict literal inside the function and return it directly; optionally load the same structure from a static JSON file for easier future updates. |

#### 2. Validate the requested strategy type against the keys of the mapping.

| Category | Details |
| --- | --- |
| **Reason** | Prevents look‑ups of undefined strategies and surfaces user errors early. |
| **Impact** | Raises a clear exception for unsupported strategies, avoiding downstream failures in asset‑class lookup. |
| **Complexity** | MEDIUM |
| **Method** | Implement a check that raises a ValueError with a descriptive message when the supplied strategy_type is not present in the dictionary. |

#### 3. Allow the mapping to be overridden via an external configuration file supplied through kwargs.

| Category | Details |
| --- | --- |
| **Reason** | Enables addition of new strategies without modifying code. |
| **Impact** | Improves maintainability and adaptability to evolving market regimes. |
| **Complexity** | MEDIUM |
| **Method** | If kwargs contains a 'config_path', load the JSON file into a dict and merge/override the default mapping; fall back to the hard‑coded default when no file is provided. |


---

## lookup_strategy_mapping

### Description
Retrieves the list of asset classes that correspond to a given trading strategy type using a provided mapping.

### Implementation Plan

#### 1. Validate that `strategy_type` is a non‑empty string and that `mapping` can be parsed as valid JSON.

| Category | Details |
| --- | --- |
| **Reason** | Prevents runtime failures caused by malformed inputs and ensures the function receives data in the expected format. |
| **Impact** | Raises clear errors early, improving debugging and stability of the pipeline. |
| **Complexity** | LOW |
| **Method** | Use `isinstance` checks for the string and `json.loads` with try/except to verify JSON structure. |

#### 2. Parse the `mapping` JSON into a Python dict and retrieve the asset class list for the given `strategy_type`.

| Category | Details |
| --- | --- |
| **Reason** | Core functionality of the shim – mapping the strategy to its compatible asset classes. |
| **Impact** | Provides downstream nodes with the correct list of asset classes aligned to the chosen strategy. |
| **Complexity** | LOW |
| **Method** | Convert JSON via `json.loads`, then use `dict.get(strategy_type)`; raise a descriptive `KeyError` if the key is missing. |

#### 3. Normalize the retrieved list to ensure all elements are strings and return it as the `output` field.

| Category | Details |
| --- | --- |
| **Reason** | Downstream Pydantic models expect a `List[str]`; type consistency avoids validation errors later. |
| **Impact** | Guarantees type safety and consistent ordering for subsequent processing steps. |
| **Complexity** | LOW |
| **Method** | Apply a list comprehension ` [str(item) for item in result] ` and return the list in the response structure. |


---

## generate_candidate_tickers

### Description
Generates a list of candidate ticker symbols for the provided high‑level asset classes using predefined selection rules.

### Implementation Plan

#### 1. Create a static mapping of asset classes to exemplar ticker lists based on industry standards and historical liquidity.

| Category | Details |
| --- | --- |
| **Reason** | Provides deterministic, reproducible candidates without external data dependencies. |
| **Impact** | Ensures the downstream validation step receives a well‑formed, realistic set of tickers for each class. |
| **Complexity** | LOW |
| **Method** | Define a Python dictionary where keys are normalized asset class strings and values are pre‑curated lists of ticker symbols; load this dictionary at module import. |

#### 2. Implement a rule‑engine that selects a subset of tickers per class (e.g., top N by market cap or most‑traded contracts).

| Category | Details |
| --- | --- |
| **Reason** | Limits the number of candidates to a manageable size while preserving relevance to the chosen strategy. |
| **Impact** | Reduces computational load for later validation and improves signal‑to‑noise ratio for strategy design. |
| **Complexity** | MEDIUM |
| **Method** | Use pandas to sort the predefined ticker list by a stored metric (market cap, volume) and slice the top K entries; expose K as a configurable parameter. |

#### 3. Normalize and validate ticker format (uppercase, no spaces, correct suffixes) before returning.

| Category | Details |
| --- | --- |
| **Reason** | Prevents downstream errors when interfacing with data providers such as Yahoo Finance. |
| **Impact** | Improves robustness of the pipeline by catching malformed symbols early. |
| **Complexity** | LOW |
| **Method** | Apply regex checks and string manipulation (e.g., str.upper(), replace spaces) on each ticker; raise warnings for any that fail the pattern. |


---

## validate_tickers_yahoo_finance

### Description
Validates a list of ticker symbols for correct syntax and confirms their existence on Yahoo Finance, returning only the verified tickers.

### Implementation Plan

#### 1. Implement syntactic validation of each ticker using a regular expression that enforces allowed characters and length limits.

| Category | Details |
| --- | --- |
| **Reason** | Ensures only plausibly correct ticker symbols proceed to the external lookup, reducing unnecessary API calls. |
| **Impact** | Filters out obviously malformed tickers early, improving performance and lowering request volume to Yahoo Finance. |
| **Complexity** | LOW |
| **Method** | Define a regex pattern (e.g., `^[A-Z]{1,5}(\.[A-Z]{1,2})?$`) and apply it to each ticker after stripping whitespace. |

#### 2. Verify each syntactically valid ticker against Yahoo Finance using the `yfinance` library (or a direct HTTP request to the Yahoo Finance API) and keep only those that return a non‑empty info dict.

| Category | Details |
| --- | --- |
| **Reason** | Only tickers that exist on Yahoo Finance can be used downstream for price retrieval and analysis. |
| **Impact** | Produces a reliable list of tradable symbols, preventing downstream failures when fetching market data. |
| **Complexity** | MEDIUM |
| **Method** | Iterate over the filtered tickers, instantiate `yfinance.Ticker(ticker)`, call `.info` or `.history(period="1d")`, and treat a successful response as validation; handle rate‑limiting with exponential back‑off and cache results for repeated symbols. |


---

## assemble_asset_classes

### Description
Assembles, deduplicates, and orders the final list of asset class identifiers for the selected trading strategy.

### Implementation Plan

#### 1. Parse the input string into a list, trim whitespace, and remove empty entries.

| Category | Details |
| --- | --- |
| **Reason** | Raw user‑provided strings may contain irregular spacing or stray commas that would corrupt downstream processing. |
| **Impact** | Ensures downstream nodes receive a clean list, preventing errors in ticker generation and validation. |
| **Complexity** | LOW |
| **Method** | Split the string on commas, strip each element, and filter out falsy values using standard Python list comprehensions. |

#### 2. Deduplicate the list while preserving a deterministic order (e.g., alphabetical).

| Category | Details |
| --- | --- |
| **Reason** | Duplicate asset classes can cause redundant work and ambiguous ordering; a stable order is required for reproducibility. |
| **Impact** | Provides a unique, predictable sequence of asset classes, simplifying caching and testing. |
| **Complexity** | MEDIUM |
| **Method** | Convert the list to a set to drop duplicates, then sort the set alphabetically before returning. |

#### 3. Validate each asset class against an allowed‑asset‑class whitelist.

| Category | Details |
| --- | --- |
| **Reason** | Only recognized asset classes should be passed to later nodes to avoid downstream lookup failures. |
| **Impact** | Filters out unsupported classes early, reducing downstream errors and improving overall system reliability. |
| **Complexity** | MEDIUM |
| **Method** | Maintain a constant list or dictionary of permitted asset class strings and filter the sorted list accordingly, logging any removals. |


---

## assemble_asset_tickers

### Description
Creates the final ordered list of asset ticker symbols from the provided validated tickers input.

### Implementation Plan

#### 1. Parse the validated_tickers string into an array of individual ticker symbols.

| Category | Details |
| --- | --- |
| **Reason** | The upstream validator returns tickers as a single string; we need a structured list for further processing. |
| **Impact** | Enables downstream nodes to iterate over tickers reliably and prevents string‑handling bugs. |
| **Complexity** | LOW |
| **Method** | Split the string on commas and whitespace, trim each token, and filter out empty entries using Python's str.split and list comprehension. |

#### 2. Deduplicate and sort the ticker list to ensure deterministic ordering.

| Category | Details |
| --- | --- |
| **Reason** | Duplicate symbols or nondeterministic order can cause inconsistent portfolio generation and cache misses. |
| **Impact** | Guarantees reproducible results across runs and simplifies comparison of generated portfolios. |
| **Complexity** | MEDIUM |
| **Method** | Convert the list to a set to remove duplicates, then back to a list and apply sorted() (or a custom alphabetical/sector‑based ordering if required). |

#### 3. Validate final ticker format and raise a clear error if any symbol violates expected patterns.

| Category | Details |
| --- | --- |
| **Reason** | Even after upstream validation, malformed symbols could slip through due to edge‑case characters. |
| **Impact** | Prevents downstream API calls (e.g., Yahoo Finance) from failing unexpectedly, improving overall robustness. |
| **Complexity** | MEDIUM |
| **Method** | Use a regular expression such as ^[A-Z]{1,5}(\.[A-Z]{1,2})?$ to check each ticker; collect invalid entries and raise a ValueError with a descriptive message. |
