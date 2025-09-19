# write_compressed_dataset PRD

## Description
Writes cleaned text data to a compressed file in the specified format and encoding, returning the path to the saved file.


## Implementation Plan

### 1. Support multiple compression formats by dynamically selecting the appropriate Python module.

| Category | Details |
| --- | --- |
| **Reason** | Different downstream pipelines or storage systems may require specific compression algorithms. |
| **Impact** | Increases flexibility and compatibility with various consumers of the dataset. |
| **Complexity** | MEDIUM |
| **Method** | Map the `format` string to the corresponding module (`gzip`, `bz2`, `lzma`) and instantiate a writer via the module’s `open` function. |

### 2. Stream the data to the compressed file in chunks to avoid high memory usage for large datasets.

| Category | Details |
| --- | --- |
| **Reason** | Training datasets can be many gigabytes; loading everything into memory would exceed typical system limits. |
| **Impact** | Reduces peak memory consumption and improves scalability. |
| **Complexity** | MEDIUM |
| **Method** | Iterate over `cleaned_lines` (split by newline if string) and write each line to the compressed file using the file object’s `write` method, optionally buffering lines in small batches. |

### 3. Implement robust error handling and atomic file creation to guarantee data integrity.

| Category | Details |
| --- | --- |
| **Reason** | Partial writes or crashes could leave corrupted or incomplete files that downstream steps would incorrectly process. |
| **Impact** | Ensures reliability and clean cleanup on failure, preventing stale or corrupted artifacts. |
| **Complexity** | LOW |
| **Method** | Write to a temporary file first, then rename atomically to the intended output path inside a `try/except` block; delete the temp file on exception. |
