# prepare_training_data PRD

## Description
Collect and preprocess the dataset for training the language model.


## Implementation Plan

### 1. Parse the project configuration to obtain data source definitions and metadata requirements.

| Category | Details |
| --- | --- |
| **Reason** | Using the configuration ensures that the node knows where to fetch data and what constraints to apply, reducing hard‑coding and increasing reproducibility. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Load the YAML/JSON config file specified by the environment, extract `data_path` and `data_sources` fields, and validate that each entry contains a `url` or `local_path` along with optional `checksum`. |

### 2. Download or copy all specified data sources, performing checksum verification and retry logic where necessary.

| Category | Details |
| --- | --- |
| **Reason** | Guarantees the integrity and availability of raw data, which is critical for a high‑quality training corpus. |
| **Impact** | HIGH |
| **Complexity** | HIGH |
| **Method** | Use `requests` for HTTP(S) downloads, `shutil.copyfile` for local copies, verify SHA‑256 checksums, and implement exponential back‑off for transient failures. |

### 3. Merge data from multiple sources into a single stream, removing exact duplicate lines while preserving source order for provenance.

| Category | Details |
| --- | --- |
| **Reason** | Avoids redundancy that could bias the model, yet keeps source traceability for debugging. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Iterate through each file, yield lines to a `set` to track seen hashes, write unique lines to a temporary output file. |

### 4. Perform comprehensive text cleaning: normalize Unicode, strip HTML tags, collapse whitespace, remove non‑ASCII characters beyond a defined threshold, and filter out empty lines.

| Category | Details |
| --- | --- |
| **Reason** | Cleaner data reduces noise in the tokenization step and improves model generalization. |
| **Impact** | HIGH |
| **Complexity** | HIGH |
| **Method** | Use `unicodedata.normalize('NFKC')`, `html5lib` for tag removal, regular expressions for whitespace collapse, and a configurable `allowed_char_set` filter. |

### 5. Estimate the token count using a lightweight tokenizer (e.g., NLTK's `word_tokenize`) to avoid a full tokenization pass during preprocessing.

| Category | Details |
| --- | --- |
| **Reason** | Provides an early metric for dataset size without incurring the full cost of subword tokenization. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Apply `nltk.word_tokenize` to each cleaned line, count tokens, and aggregate counts. |

### 6. Write the cleaned lines to a compressed UTF‑8 file (e.g., Gzip) to reduce disk usage and speed up downstream I/O.

| Category | Details |
| --- | --- |
| **Reason** | Compressed storage conserves space and speeds up data loading for later steps. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Open a `gzip.open` file in write mode, stream cleaned lines as UTF‑8 encoded bytes, and close the handle gracefully. |

### 7. Populate the output structure: compute `sample_count`, `token_count`, set `is_valid` based on success flags, and expose the final file path.

| Category | Details |
| --- | --- |
| **Reason** | These metadata fields are required by downstream nodes and enable validation checks before training. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Count the number of written lines for `sample_count`, use the token counter from step 5 for `token_count`, and set `is_valid` to true if no errors were encountered. |
