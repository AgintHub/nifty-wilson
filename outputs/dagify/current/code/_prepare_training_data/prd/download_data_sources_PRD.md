# download_data_sources PRD

## Description
Downloads data from specified sources, verifies checksums, and applies retry logic.


## Implementation Plan

### 1. Validate and parse input parameters, converting comma‑separated strings into usable lists and normalizing boolean flags.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the shim operates on correctly typed data and avoids downstream errors. |
| **Impact** | Improves robustness and makes debugging easier by providing clear error messages for malformed inputs. |
| **Complexity** | LOW |
| **Method** | Use Python's built‑in `str.split` for lists, and a helper that maps "true" / "false" to booleans; raise `ValueError` for invalid entries. |

### 2. Implement the core download logic with retry and checksum verification using the `requests` library, `hashlib`, and the `backoff` library for exponential backoff.

| Category | Details |
| --- | --- |
| **Reason** | Handles network instability, ensures data integrity, and keeps the implementation maintainable. |
| **Impact** | Provides reliable data acquisition, reducing failures in downstream training steps. |
| **Complexity** | MEDIUM |
| **Method** | For each source, stream the content to a temporary file, compute SHA256 after download, compare to an optional checksum header or provided checksum file, and retry up to 5 times with exponential backoff on `ConnectionError` and `Timeout`. |

### 3. Return a structured output that includes the list of file paths and echoes back all input flags to aid idempotency and debugging.

| Category | Details |
| --- | --- |
| **Reason** | Allows calling code to verify what was downloaded and the configuration used without re‑parsing arguments. |
| **Impact** | Simplifies orchestration in pipelines and enables easier unit testing of the shim. |
| **Complexity** | LOW |
| **Method** | Construct a dictionary with the required keys and serialize with `json.dumps` or return a plain Python dict as the shim result. |
