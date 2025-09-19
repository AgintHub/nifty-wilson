# split_and_write_data_files PRD

## Description
Splits a pre‑processed data file into training, validation, and test files based on provided indices and writes each split to its designated path.


## Implementation Plan

### 1. Parse the stringified index lists into Python lists and convert them into sets for O(1) membership checks.

| Category | Details |
| --- | --- |
| **Reason** | Efficient lookup is required when processing potentially millions of rows. |
| **Impact** | Reduces runtime from O(n*m) to O(n) where n is the number of lines and m is the number of indices. |
| **Complexity** | MEDIUM |
| **Method** | Use `json.loads` or `ast.literal_eval` to convert the strings, then cast to `set`. |

### 2. Stream the source file line by line, using the line number to route each line to the appropriate output file.

| Category | Details |
| --- | --- |
| **Reason** | Avoids loading the entire dataset into memory, enabling scalability to large files. |
| **Impact** | Supports big‑data use cases and keeps memory footprint minimal. |
| **Complexity** | MEDIUM |
| **Method** | Open `source_path` with a `with open(...)` context manager, enumerate lines starting at 1, and write to the correct file based on set membership. |

### 3. After processing, verify that the number of written rows matches the expected split sizes and that no indices are duplicated or missing.

| Category | Details |
| --- | --- |
| **Reason** | Ensures data integrity and prevents silent errors in downstream training. |
| **Impact** | Provides early failure detection and reliable split metadata. |
| **Complexity** | LOW |
| **Method** | Maintain counters per split during writing, then compare against the lengths of the original index lists. |
