# write_build_metadata PRD

## Description
Writes a build metadata file in the specified build directory with information about the build outcome, duration, and produced artifacts.


## Implementation Plan

### 1. Serialize build metadata (success, duration, artifacts) to a JSON file within the build directory.

| Category | Details |
| --- | --- |
| **Reason** | Persistent storage of build results is essential for auditing, reproducibility, and downstream analysis. |
| **Impact** | Provides a reliable source of truth for the build outcome, enabling automated reporting and debugging. |
| **Complexity** | LOW |
| **Method** | Use Python's json.dump to write a dictionary containing the fields to a file named 'build_metadata.json'. |

### 2. Perform the write atomically by first writing to a temporary file and then renaming it to the target filename.

| Category | Details |
| --- | --- |
| **Reason** | Prevents partial or corrupted metadata files in case of crashes or interruptions during the write operation. |
| **Impact** | Ensures that any consumer of the metadata file always reads a complete and valid JSON document. |
| **Complexity** | MEDIUM |
| **Method** | Write to 'build_metadata.json.tmp' and then call os.replace('build_metadata.json.tmp', 'build_metadata.json') to atomically replace the target file. |

### 3. Return a concise status string (e.g., 'metadata_written' or 'write_failed') as the output field.

| Category | Details |
| --- | --- |
| **Reason** | Downstream nodes need a clear signal indicating whether the metadata was successfully persisted. |
| **Impact** | Facilitates control flow decisions and error handling in the build pipeline. |
| **Complexity** | LOW |
| **Method** | Set the output variable to the status string after the atomic write and include it in the returned response. |
