# persist_split_metadata PRD

## Description
Persists split dataset metadata—including sizes, ratios, seed, and file paths—to a JSON manifest file.


## Implementation Plan

### 1. Validate all input parameters for correct types and logical consistency (e.g., train_size + val_size + test_size equals total sample count).

| Category | Details |
| --- | --- |
| **Reason** | Prevent corrupt metadata and ensure downstream components receive accurate information. |
| **Impact** | Guarantees that the JSON manifest reflects the actual split sizes, improving data integrity. |
| **Complexity** | LOW |
| **Method** | Perform simple type checks and arithmetic validation before any file operations. |

### 2. Serialize the metadata dictionary to a JSON file located alongside the original data file (e.g., `<original_data_path>_split_manifest.json`).

| Category | Details |
| --- | --- |
| **Reason** | Storing metadata in a dedicated manifest file allows easy retrieval and reproducibility. |
| **Impact** | Provides a clear, machine-readable record of the split configuration that can be reused by downstream processes. |
| **Complexity** | MEDIUM |
| **Method** | Use Python's `pathlib` to construct the manifest path, then write the dictionary with `json.dump` ensuring UTF‑8 encoding. |

### 3. Implement robust error handling for I/O failures and JSON serialization errors, returning a descriptive error message in the `output` field.

| Category | Details |
| --- | --- |
| **Reason** | Graceful failure handling avoids silent crashes and aids debugging. |
| **Impact** | Improves system reliability and provides clear feedback to users or orchestration tools. |
| **Complexity** | LOW |
| **Method** | Wrap file operations in a try/except block catching `OSError` and `json.JSONDecodeError`, and set `output` to an informative error string. |
