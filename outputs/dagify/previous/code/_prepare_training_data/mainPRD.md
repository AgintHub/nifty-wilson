# _prepare_training_data - Complete PRD Documentation

## Overview
PRDs for nodes in the '_prepare_training_data' module.

## Table of Contents

- [load_project_configuration](#load_project_configuration)

- [extract_data_sources](#extract_data_sources)

- [extract_metadata_requirements](#extract_metadata_requirements)

- [download_data_sources](#download_data_sources)

- [merge_data_sources](#merge_data_sources)

- [clean_text_data](#clean_text_data)

- [estimate_token_count](#estimate_token_count)

- [write_compressed_dataset](#write_compressed_dataset)

- [count_samples](#count_samples)

- [validate_processing_success](#validate_processing_success)



---

## load_project_configuration

### Description
Loads and validates project configuration from a JSON file whose path is specified by an environment variable, returning the configuration as a stringified dictionary.

### Implementation Plan

#### 1. Resolve the configuration file path from the provided environment variable.

| Category | Details |
| --- | --- |
| **Reason** | The shim must know where the configuration file resides. |
| **Impact** | Allows flexible deployment without hardcoding file locations. |
| **Complexity** | LOW |
| **Method** | Use `os.getenv(env_var)` and raise `KeyError` if missing. |

#### 2. Read and parse the JSON configuration file.

| Category | Details |
| --- | --- |
| **Reason** | Actual configuration data must be loaded for downstream processing. |
| **Impact** | Provides the raw configuration dictionary for validation. |
| **Complexity** | LOW |
| **Method** | Use `pathlib.Path.read_text()` to read the file and `json.loads()` to parse. |

#### 3. Validate the configuration against a Pydantic model and return a stringified JSON.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the configuration meets expected schema constraints before use. |
| **Impact** | Prevents runtime failures in downstream nodes that rely on correct config. |
| **Complexity** | MEDIUM |
| **Method** | Instantiate `ProjectConfigModel` with the parsed dict, call `.dict()`, and return `json.dumps()` of the validated data. |


---

## extract_data_sources

### Description
Extracts a list of data source identifiers from the provided configuration string for downstream data ingestion steps.

### Implementation Plan

#### 1. Parse the JSON configuration string into a Python dictionary.

| Category | Details |
| --- | --- |
| **Reason** | The configuration must be deserialized to access the data source entries. |
| **Impact** | Provides a structured data representation for reliable extraction. |
| **Complexity** | LOW |
| **Method** | Use `json.loads(config)` with exception handling to catch malformed JSON. |

#### 2. Retrieve and validate the 'data_sources' field as a list of strings.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that only valid source identifiers are passed downstream. |
| **Impact** | Prevents type errors and missing data in subsequent processing stages. |
| **Complexity** | LOW |
| **Method** | Check `isinstance(data['data_sources'], list)` and that each element is a string; otherwise return an empty list or raise a clear error. |

#### 3. Return the data sources as a comma‑separated string.

| Category | Details |
| --- | --- |
| **Reason** | The downstream node expects the output as a string list. |
| **Impact** | Provides a consistent, easily consumable output for the training pipeline. |
| **Complexity** | LOW |
| **Method** | Use `','.join(data_sources_list)` and return the resulting string. |


---

## extract_metadata_requirements

### Description
Extract and validate the metadata requirements section from a JSON configuration string for downstream processing.

### Implementation Plan

#### 1. Parse the `config` string as JSON and verify that it contains a `metadata_requirements` key of type object.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the input configuration is well‑formed and the required section is present. |
| **Impact** | Prevents downstream nodes from encountering missing or malformed data, reducing runtime failures. |
| **Complexity** | LOW |
| **Method** | Use `json.loads()` inside a try/except block, check for the key and type, and raise a clear ValueError if validation fails. |

#### 2. Normalize all keys in the extracted metadata dictionary by lowercasing and stripping surrounding whitespace.

| Category | Details |
| --- | --- |
| **Reason** | Provides a consistent key format for downstream processing regardless of input case or accidental spaces. |
| **Impact** | Avoids subtle bugs caused by key mismatches across nodes and simplifies lookup logic. |
| **Complexity** | LOW |
| **Method** | Apply a dictionary comprehension: `{k.strip().lower(): v for k, v in raw_metadata.items()}`. |

#### 3. Validate each metadata entry against a predefined schema that requires fields such as `type` and `required`.

| Category | Details |
| --- | --- |
| **Reason** | Guarantees that each requirement contains the necessary metadata to be usable by other components. |
| **Impact** | Improves data quality and ensures that downstream nodes receive complete information. |
| **Complexity** | MEDIUM |
| **Method** | Define a list of allowed keys per entry, iterate over the dictionary, and raise a descriptive error if any entry is missing required keys or has unsupported values. |


---

## download_data_sources

### Description
Downloads data from specified sources, verifies checksums, and applies retry logic.

### Implementation Plan

#### 1. Validate and parse input parameters, converting comma‑separated strings into usable lists and normalizing boolean flags.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the shim operates on correctly typed data and avoids downstream errors. |
| **Impact** | Improves robustness and makes debugging easier by providing clear error messages for malformed inputs. |
| **Complexity** | LOW |
| **Method** | Use Python's built‑in `str.split` for lists, and a helper that maps "true" / "false" to booleans; raise `ValueError` for invalid entries. |

#### 2. Implement the core download logic with retry and checksum verification using the `requests` library, `hashlib`, and the `backoff` library for exponential backoff.

| Category | Details |
| --- | --- |
| **Reason** | Handles network instability, ensures data integrity, and keeps the implementation maintainable. |
| **Impact** | Provides reliable data acquisition, reducing failures in downstream training steps. |
| **Complexity** | MEDIUM |
| **Method** | For each source, stream the content to a temporary file, compute SHA256 after download, compare to an optional checksum header or provided checksum file, and retry up to 5 times with exponential backoff on `ConnectionError` and `Timeout`. |

#### 3. Return a structured output that includes the list of file paths and echoes back all input flags to aid idempotency and debugging.

| Category | Details |
| --- | --- |
| **Reason** | Allows calling code to verify what was downloaded and the configuration used without re‑parsing arguments. |
| **Impact** | Simplifies orchestration in pipelines and enables easier unit testing of the shim. |
| **Complexity** | LOW |
| **Method** | Construct a dictionary with the required keys and serialize with `json.dumps` or return a plain Python dict as the shim result. |


---

## merge_data_sources

### Description
Creates a single consolidated data stream from multiple source files, with options to preserve order and eliminate duplicate entries.

### Implementation Plan

#### 1. Validate all input file paths for existence and readability before processing.

| Category | Details |
| --- | --- |
| **Reason** | Prevent runtime failures due to missing or inaccessible files. |
| **Impact** | Increases robustness and provides clear error messages early in the workflow. |
| **Complexity** | LOW |
| **Method** | Use `os.path.isfile` and `os.access` to check each file; raise `FileNotFoundError` or `PermissionError` with a descriptive message if validation fails. |

#### 2. Iterate over the input files, concatenating their contents into a single stream while optionally preserving order and deduplicating lines.

| Category | Details |
| --- | --- |
| **Reason** | Core functionality of the shim – ensuring the merged data is accurate and respects user preferences. |
| **Impact** | Produces a correctly ordered and deduplicated dataset for downstream processing. |
| **Complexity** | MEDIUM |
| **Method** | Open each file in text mode with UTF‑8 encoding. If `preserve_order` is true, read files sequentially as provided; if `remove_duplicates` is true, maintain a `set` of seen lines and skip repeats. Write each line to a temporary output file, flushing after each write to limit memory usage. |

#### 3. Write the consolidated data to a temporary file and return its path as the output.

| Category | Details |
| --- | --- |
| **Reason** | Provides a persistent, file‑based output that downstream nodes can consume without keeping the entire dataset in memory. |
| **Impact** | Reduces memory footprint and enables streaming of large datasets. |
| **Complexity** | LOW |
| **Method** | Use `tempfile.NamedTemporaryFile` with `delete=False` to create a writable file, write the merged lines, close the file, and return the absolute path. |


---

## clean_text_data

### Description
Cleans raw merged text data by normalizing Unicode, stripping HTML, collapsing whitespace, filtering non-ASCII characters, and removing empty lines, returning a list of cleaned lines.

### Implementation Plan

#### 1. Normalize Unicode and strip HTML using standard libraries such as `unicodedata` and `BeautifulSoup`.

| Category | Details |
| --- | --- |
| **Reason** | Ensures consistent character representation and removes markup that can interfere with downstream tokenization. |
| **Impact** | Reduces tokenization errors and eliminates unwanted HTML artifacts from the dataset. |
| **Complexity** | MEDIUM |
| **Method** | Apply `unicodedata.normalize('NFC', text)` for normalization and `BeautifulSoup(text, 'html.parser').get_text()` for HTML removal. |

#### 2. Collapse whitespace and filter non-ASCII characters using regular expressions and string filtering.

| Category | Details |
| --- | --- |
| **Reason** | Standardizes spacing and keeps only ASCII to simplify tokenization and reduce noise. |
| **Impact** | Improves memory efficiency and ensures uniform token counts across samples. |
| **Complexity** | LOW |
| **Method** | Use `re.sub(r'\s+', ' ', line)` to collapse whitespace and filter with `''.join(c for c in line if ord(c) < 128)`. |

#### 3. Remove empty lines after processing and package the results into a list.

| Category | Details |
| --- | --- |
| **Reason** | Eliminates redundant entries that can bloat the dataset and confuse downstream models. |
| **Impact** | Reduces dataset size and ensures consistent input format for subsequent steps. |
| **Complexity** | LOW |
| **Method** | Iterate over processed lines, use `line.strip()` and include only non-empty strings in the output list. |


---

## estimate_token_count

### Description
Calculates the total number of tokens in a cleaned text string using a lightweight tokenizer.

### Implementation Plan

#### 1. Tokenize the cleaned_lines string using the specified tokenizer and count the resulting tokens.

| Category | Details |
| --- | --- |
| **Reason** | Core functionality required to estimate token count. |
| **Impact** | Provides an accurate token count for downstream training data preparation. |
| **Complexity** | LOW |
| **Method** | Use Python's built-in string split for simple tokenizers or import nltk.tokenize.word_tokenize when tokenizer is 'nltk_word_tokenize'. |

#### 2. Validate the existence and compatibility of the requested tokenizer, falling back to a default split if unavailable.

| Category | Details |
| --- | --- |
| **Reason** | Ensures robustness against missing or unsupported tokenizer implementations. |
| **Impact** | Prevents runtime crashes and guarantees a token count is always returned. |
| **Complexity** | MEDIUM |
| **Method** | Dynamic import with importlib.util.find_spec and a try/except block; if import fails, use a simple whitespace split. |

#### 3. Process the cleaned text in a memory‑efficient way, handling large inputs by iterating over lines or streaming tokens.

| Category | Details |
| --- | --- |
| **Reason** | Large datasets can consume significant memory if fully tokenized at once. |
| **Impact** | Reduces peak memory usage and improves scalability for big training corpora. |
| **Complexity** | MEDIUM |
| **Method** | Split cleaned_lines into lines, then split each line into tokens and increment a counter, avoiding storage of the full token list. |


---

## write_compressed_dataset

### Description
Writes cleaned text data to a compressed file in the specified format and encoding, returning the path to the saved file.

### Implementation Plan

#### 1. Support multiple compression formats by dynamically selecting the appropriate Python module.

| Category | Details |
| --- | --- |
| **Reason** | Different downstream pipelines or storage systems may require specific compression algorithms. |
| **Impact** | Increases flexibility and compatibility with various consumers of the dataset. |
| **Complexity** | MEDIUM |
| **Method** | Map the `format` string to the corresponding module (`gzip`, `bz2`, `lzma`) and instantiate a writer via the module’s `open` function. |

#### 2. Stream the data to the compressed file in chunks to avoid high memory usage for large datasets.

| Category | Details |
| --- | --- |
| **Reason** | Training datasets can be many gigabytes; loading everything into memory would exceed typical system limits. |
| **Impact** | Reduces peak memory consumption and improves scalability. |
| **Complexity** | MEDIUM |
| **Method** | Iterate over `cleaned_lines` (split by newline if string) and write each line to the compressed file using the file object’s `write` method, optionally buffering lines in small batches. |

#### 3. Implement robust error handling and atomic file creation to guarantee data integrity.

| Category | Details |
| --- | --- |
| **Reason** | Partial writes or crashes could leave corrupted or incomplete files that downstream steps would incorrectly process. |
| **Impact** | Ensures reliability and clean cleanup on failure, preventing stale or corrupted artifacts. |
| **Complexity** | LOW |
| **Method** | Write to a temporary file first, then rename atomically to the intended output path inside a `try/except` block; delete the temp file on exception. |


---

## count_samples

### Description
Counts the number of samples in the provided cleaned text lines.

### Implementation Plan

#### 1. Parse the input string into individual lines and count non‑empty lines.

| Category | Details |
| --- | --- |
| **Reason** | Ensures accurate sample count by excluding empty or whitespace‑only lines. |
| **Impact** | Provides reliable sample metrics for downstream processing. |
| **Complexity** | LOW |
| **Method** | Use Python's `splitlines()` and a generator expression to iterate and filter. |

#### 2. Handle large input efficiently by streaming the string rather than loading it into memory entirely.

| Category | Details |
| --- | --- |
| **Reason** | Prevents memory exhaustion for massive datasets. |
| **Impact** | Improves scalability and performance in training pipelines. |
| **Complexity** | MEDIUM |
| **Method** | Implement a line‑by‑line iterator using `io.StringIO` or a generator that yields lines. |

#### 3. Validate input type and provide descriptive error messages for malformed data.

| Category | Details |
| --- | --- |
| **Reason** | Prevents silent failures and aids debugging. |
| **Impact** | Increases robustness and user confidence. |
| **Complexity** | LOW |
| **Method** | Check if `cleaned_lines` is a string; raise `TypeError` with a clear message otherwise. |


---

## validate_processing_success

### Description
Checks the integrity of the preprocessed dataset by verifying file existence, size, sample and token counts, and returns a boolean indicating success.

### Implementation Plan

#### 1. Verify that the output file exists and is not empty, ensuring the preprocessing step wrote data correctly.

| Category | Details |
| --- | --- |
| **Reason** | An absent or empty file indicates a failure in the data pipeline that must be caught early. |
| **Impact** | Prevents downstream nodes from operating on incomplete data, avoiding cascading failures and wasted compute. |
| **Complexity** | LOW |
| **Method** | Use `os.path.exists` and `os.path.getsize` to check file presence and size. |

#### 2. Compare the actual sample count in the dataset to the expected `sample_count` by reading the file and counting non-empty lines.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that the deduplication and merging steps produced the correct number of samples. |
| **Impact** | Detects mismatches that could corrupt training statistics and bias the model. |
| **Complexity** | MEDIUM |
| **Method** | Open the gzip file, iterate over lines, increment a counter, and compare to the expected value. |

#### 3. Recalculate token count using the same tokenizer as the preprocessing step and compare it to the provided `token_count`.

| Category | Details |
| --- | --- |
| **Reason** | Validates that the tokenization was performed consistently and that no data corruption altered token counts. |
| **Impact** | Guarantees that downstream training stages receive accurate token statistics, affecting loss calculation and learning dynamics. |
| **Complexity** | MEDIUM |
| **Method** | Load the tokenizer (e.g., `nltk.word_tokenize`), re-tokenize each line, sum token lengths, and compare to the expected count. |
