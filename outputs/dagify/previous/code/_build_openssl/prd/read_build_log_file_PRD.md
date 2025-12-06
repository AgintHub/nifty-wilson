# read_build_log_file PRD

## Description
Reads the complete build log from the given build directory and returns it as a string.


## Implementation Plan

### 1. Validate that `build_dir` exists and contains a readable log file before attempting to read.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that the shim does not fail silently due to missing paths or files. |
| **Impact** | Provides clear error handling and prevents downstream failures in the build pipeline. |
| **Complexity** | LOW |
| **Method** | Use `pathlib.Path(build_dir).is_dir()` and `Path(...).joinpath('build.log').is_file()` to verify existence; raise a descriptive exception if checks fail. |

### 2. Read the log file contents using efficient I/O, handling large files by streaming if necessary.

| Category | Details |
| --- | --- |
| **Reason** | Large build logs can consume significant memory; streaming avoids loading the entire file into RAM at once. |
| **Impact** | Improves scalability and reduces memory footprint for builds with extensive logs. |
| **Complexity** | MEDIUM |
| **Method** | Use `Path(...).open('r', encoding='utf-8')` and read in chunks (e.g., 64KB) appending to a list of strings, then join; fallback to `read_text()` for smaller files. |

### 3. Return the concatenated log content as the `output` field, ensuring any Unicode errors are handled gracefully.

| Category | Details |
| --- | --- |
| **Reason** | Build logs may contain non‑ASCII characters; handling them prevents crashes during processing. |
| **Impact** | Guarantees that the shim provides a clean, usable string for downstream nodes. |
| **Complexity** | LOW |
| **Method** | Wrap the read operation in a try/except block, decode with `errors='replace'` or `errors='ignore'` as appropriate, and assign the result to the `output` key. |
