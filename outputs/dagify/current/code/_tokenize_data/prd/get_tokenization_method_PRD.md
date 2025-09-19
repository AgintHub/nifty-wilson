# get_tokenization_method PRD

## Description
Retrieves the tokenization method to use, defaulting to BPE if not specified.


## Implementation Plan

### 1. Retrieve tokenization method from the environment variable `TOKENIZATION_METHOD` if set, otherwise use the provided default.

| Category | Details |
| --- | --- |
| **Reason** | Centralizes configuration for tokenization method across the pipeline. |
| **Impact** | Ensures consistent method usage, making debugging and reproducibility easier. |
| **Complexity** | LOW |
| **Method** | Use `os.getenv('TOKENIZATION_METHOD', default)` to fetch the value. |

### 2. Validate the retrieved method against a whitelist of supported methods (`bpe`, `sentencepiece`, `wordpiece`).

| Category | Details |
| --- | --- |
| **Reason** | Prevents downstream errors caused by unsupported or misspelled tokenization methods. |
| **Impact** | Provides immediate feedback to the user and stops execution with a clear error message if invalid. |
| **Complexity** | LOW |
| **Method** | Check membership in a set and raise a `ValueError` with an explanatory message if not valid. |

### 3. Log the chosen tokenization method for audit and debugging purposes.

| Category | Details |
| --- | --- |
| **Reason** | Enables traceability of decisions made by the system. |
| **Impact** | Facilitates troubleshooting and ensures transparency of the tokenization configuration. |
| **Complexity** | LOW |
| **Method** | Utilize the standard `logging` module to write an info‑level log entry with the chosen method. |
