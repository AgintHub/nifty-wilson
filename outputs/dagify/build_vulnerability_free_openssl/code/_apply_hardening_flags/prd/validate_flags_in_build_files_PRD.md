# validate_flags_in_build_files PRD

## Description
Validates that a list of hardening flags are correctly applied in the OpenSSL build files located at the given source root.


## Implementation Plan

### 1. Parse the OpenSSL build files (Makefile, config.h) from the provided source_root directory to extract their content.

| Category | Details |
| --- | --- |
| **Reason** | The validation requires access to the actual files where flags are defined. |
| **Impact** | Ensures that the shim operates on the correct file set, preventing false negatives. |
| **Complexity** | MEDIUM |
| **Method** | Use Python's pathlib to locate Makefile and config.h, then read their contents into memory. |

### 2. Search the extracted file contents for each flag in the provided list using regular expressions or substring matching.

| Category | Details |
| --- | --- |
| **Reason** | To determine whether each hardening flag has been correctly applied. |
| **Impact** | Provides the core validation logic that determines the boolean output. |
| **Complexity** | LOW |
| **Method** | Iterate over the split `flags` string, applying a regex pattern that matches the flag as a whole word in the file texts. |

### 3. Return a boolean result indicating whether all flags were found in the build files.

| Category | Details |
| --- | --- |
| **Reason** | The downstream node requires a simple success/failure signal. |
| **Impact** | Enables conditional execution of subsequent steps (e.g., applying hardening flags). |
| **Complexity** | LOW |
| **Method** | Collect the results of the flag checks into a list, then return `all(results)`. |
