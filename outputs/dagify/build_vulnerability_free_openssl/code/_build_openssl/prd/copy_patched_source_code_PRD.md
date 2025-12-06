# copy_patched_source_code PRD

## Description
Copies the patched OpenSSL source code to a destination directory for building.


## Implementation Plan

### 1. Validate the destination path exists and is writable before copying.

| Category | Details |
| --- | --- |
| **Reason** | Prevent silent failures and ensure the build environment is ready. |
| **Impact** | Reduces runtime errors and provides clear feedback to upstream nodes. |
| **Complexity** | LOW |
| **Method** | Check with os.path.isdir and os.access; if not valid, raise a descriptive exception. |

### 2. Copy all source files recursively while preserving file permissions and timestamps.

| Category | Details |
| --- | --- |
| **Reason** | Maintain the integrity of the patched code and build metadata. |
| **Impact** | Ensures reproducible builds and avoids permission-related build errors. |
| **Complexity** | MEDIUM |
| **Method** | Use shutil.copytree with a custom ignore function and shutil.copystat to preserve metadata. |

### 3. Handle any I/O errors gracefully and return a structured output indicating failure.

| Category | Details |
| --- | --- |
| **Reason** | Provide robust error handling for downstream nodes. |
| **Impact** | Improves reliability and debuggability of the overall build pipeline. |
| **Complexity** | LOW |
| **Method** | Wrap the copy logic in try/except, log the exception, and set output = f'Copy failed: {str(e)}'; return output. |
