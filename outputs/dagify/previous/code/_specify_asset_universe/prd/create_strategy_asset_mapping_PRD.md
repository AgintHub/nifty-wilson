# create_strategy_asset_mapping PRD

## Description
Returns a static dictionary mapping each trading strategy type to a list of compatible asset classes.


## Implementation Plan

### 1. Define a hard‑coded dictionary that lists supported strategy types and their associated asset classes.

| Category | Details |
| --- | --- |
| **Reason** | Provides a deterministic source for downstream asset‑universe selection. |
| **Impact** | Ensures consistent mapping across runs and simplifies debugging. |
| **Complexity** | LOW |
| **Method** | Create a Python dict literal inside the function and return it directly; optionally load the same structure from a static JSON file for easier future updates. |

### 2. Validate the requested strategy type against the keys of the mapping.

| Category | Details |
| --- | --- |
| **Reason** | Prevents look‑ups of undefined strategies and surfaces user errors early. |
| **Impact** | Raises a clear exception for unsupported strategies, avoiding downstream failures in asset‑class lookup. |
| **Complexity** | MEDIUM |
| **Method** | Implement a check that raises a ValueError with a descriptive message when the supplied strategy_type is not present in the dictionary. |

### 3. Allow the mapping to be overridden via an external configuration file supplied through kwargs.

| Category | Details |
| --- | --- |
| **Reason** | Enables addition of new strategies without modifying code. |
| **Impact** | Improves maintainability and adaptability to evolving market regimes. |
| **Complexity** | MEDIUM |
| **Method** | If kwargs contains a 'config_path', load the JSON file into a dict and merge/override the default mapping; fall back to the hard‑coded default when no file is provided. |
