# extract_test_vectors_as_seeds PRD

## Description
Extracts OpenSSL test vector files from the source tree and converts them into initial seed inputs suitable for fuzz testing, saving them to a specified directory.


## Implementation Plan

### 1. Locate and parse OpenSSL test vector files from the given source directory.

| Category | Details |
| --- | --- |
| **Reason** | Test vectors provide structured, valid inputs that represent realistic use cases and edge cases for the library, making them ideal as seed inputs for fuzzers. |
| **Impact** | This ensures the fuzzing campaign begins with meaningful, valid inputs, increasing the likelihood of uncovering bugs with minimal noise. |
| **Complexity** | MEDIUM |
| **Method** | Recursively scan source directories for files with recognized test vector extensions or names, then parse and extract raw data using file format-specific parsers or conversion utilities. |

### 2. Convert extracted test vectors into individual seed files, placing them in the designated output directory with a clear and consistent naming scheme.

| Category | Details |
| --- | --- |
| **Reason** | Fuzzers require seed inputs as discrete files; organizing them correctly enables easy management and reuse during fuzzing runs. |
| **Impact** | Facilitates efficient fuzzing initialization with well-organized and accessible seed inputs, improving fuzzing throughput and result reproducibility. |
| **Complexity** | LOW |
| **Method** | Write each extracted test vector as a separate file, using either raw binary or appropriately encoded formats, ensuring file permissions and directory exist before writing. |

### 3. Return a consolidated string listing the paths to all generated seed files for downstream consumption.

| Category | Details |
| --- | --- |
| **Reason** | Downstream nodes require a list of seed file locations to configure and start fuzzing sessions accurately. |
| **Impact** | Smooth integration with subsequent fuzzing setup steps, enabling automated workflows without manual intervention. |
| **Complexity** | LOW |
| **Method** | Aggregate all seed file paths into a single string separated by newlines or another delimiter, and return it as the shim output. |
