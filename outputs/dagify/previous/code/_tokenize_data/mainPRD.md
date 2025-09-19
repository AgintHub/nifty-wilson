# _tokenize_data - Complete PRD Documentation

## Overview
PRDs for nodes in the '_tokenize_data' module.

## Table of Contents

- [load_text_file](#load_text_file)

- [get_tokenization_method](#get_tokenization_method)

- [create_huggingface_tokenizer](#create_huggingface_tokenizer)

- [train_tokenizer](#train_tokenizer)

- [tokenize_text_lines](#tokenize_text_lines)

- [extract_unique_tokens](#extract_unique_tokens)

- [create_sorted_vocabulary](#create_sorted_vocabulary)

- [save_tokenizer](#save_tokenizer)

- [validate_tokenization_results](#validate_tokenization_results)

- [format_tokenized_texts](#format_tokenized_texts)

- [format_vocabulary](#format_vocabulary)



---

## load_text_file

### Description
Loads the specified text file and returns its contents as a list of strings.

### Implementation Plan

#### 1. Validate that the provided file path exists and is a regular file before attempting to read.

| Category | Details |
| --- | --- |
| **Reason** | Prevent runtime errors from nonexistent or inaccessible files. |
| **Impact** | Improves robustness and provides clear error messages to downstream nodes. |
| **Complexity** | LOW |
| **Method** | Use pathlib.Path to check existence and file type; raise a descriptive exception if validation fails. |

#### 2. Open the file using UTF‑8 encoding with error handling (e.g., `errors='replace'`) and read all lines into memory.

| Category | Details |
| --- | --- |
| **Reason** | Ensure consistent text decoding and avoid crashes on malformed bytes. |
| **Impact** | Guarantees that downstream tokenization receives valid strings. |
| **Complexity** | LOW |
| **Method** | Call `open(file_path, 'r', encoding='utf-8', errors='replace')` and use `.readlines()`. |

#### 3. Return a list of stripped lines, optionally discarding empty lines, and expose the original file path in the output structure.

| Category | Details |
| --- | --- |
| **Reason** | Provide clean data for tokenization and maintain traceability of the source file. |
| **Impact** | Reduces noise in tokenization and aids debugging. |
| **Complexity** | LOW |
| **Method** | Use a list comprehension such as `[line.rstrip('\n') for line in file]` and include `file_path` in the returned dictionary. |


---

## get_tokenization_method

### Description
Retrieves the tokenization method to use, defaulting to BPE if not specified.

### Implementation Plan

#### 1. Retrieve tokenization method from the environment variable `TOKENIZATION_METHOD` if set, otherwise use the provided default.

| Category | Details |
| --- | --- |
| **Reason** | Centralizes configuration for tokenization method across the pipeline. |
| **Impact** | Ensures consistent method usage, making debugging and reproducibility easier. |
| **Complexity** | LOW |
| **Method** | Use `os.getenv('TOKENIZATION_METHOD', default)` to fetch the value. |

#### 2. Validate the retrieved method against a whitelist of supported methods (`bpe`, `sentencepiece`, `wordpiece`).

| Category | Details |
| --- | --- |
| **Reason** | Prevents downstream errors caused by unsupported or misspelled tokenization methods. |
| **Impact** | Provides immediate feedback to the user and stops execution with a clear error message if invalid. |
| **Complexity** | LOW |
| **Method** | Check membership in a set and raise a `ValueError` with an explanatory message if not valid. |

#### 3. Log the chosen tokenization method for audit and debugging purposes.

| Category | Details |
| --- | --- |
| **Reason** | Enables traceability of decisions made by the system. |
| **Impact** | Facilitates troubleshooting and ensures transparency of the tokenization configuration. |
| **Complexity** | LOW |
| **Method** | Utilize the standard `logging` module to write an info‑level log entry with the chosen method. |


---

## create_huggingface_tokenizer

### Description
Creates a Hugging Face tokenizer instance based on the specified method and returns it as a serialized string.

### Implementation Plan

#### 1. Map the provided method string to the appropriate Hugging Face tokenizer class.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that the correct tokenizer implementation is instantiated based on the requested method. |
| **Impact** | Provides flexibility for different tokenization strategies (BPE, WordPiece, SentencePiece, etc.) without changing the shim interface. |
| **Complexity** | MEDIUM |
| **Method** | Create a lookup dictionary mapping method names to classes (e.g., {'bpe': ByteLevelBPETokenizer, 'wordpiece': WordPieceTokenizer}) and use it to retrieve the class. |

#### 2. Instantiate the tokenizer, handling both pretrained and freshly-trained scenarios.

| Category | Details |
| --- | --- |
| **Reason** | The shim must support creating tokenizers that either load existing models or are initialized from scratch. |
| **Impact** | Allows downstream nodes to use a tokenizer that is ready for training or inference. |
| **Complexity** | MEDIUM |
| **Method** | If the method indicates a pretrained model (e.g., starts with 'pretrained:'), call the class's `from_pretrained` method; otherwise, use the default constructor and optionally configure training parameters. |

#### 3. Serialize the tokenizer instance to a JSON string for return.

| Category | Details |
| --- | --- |
| **Reason** | The shim’s output must be a primitive string so it can be stored or passed between nodes. |
| **Impact** | Facilitates persistence and transfer of tokenizer configuration across steps in the workflow. |
| **Complexity** | LOW |
| **Method** | Use the tokenizer's `save_pretrained` to a temporary directory and read the config files (e.g., tokenizer_config.json) back into a string, or use the tokenizer's `serialize()` method if available. |


---

## train_tokenizer

### Description
Trains a tokenizer on a text corpus and returns the training result along with tokenizer, file path, and vocabulary size.

### Implementation Plan

#### 1. Validate that the supplied file path exists and is readable before initiating training.

| Category | Details |
| --- | --- |
| **Reason** | Prevent runtime failures and provide clear error feedback if the corpus file is missing or inaccessible. |
| **Impact** | Ensures early detection of I/O issues, improving reliability of the training pipeline. |
| **Complexity** | LOW |
| **Method** | Use `os.path.isfile` and `os.access` to check existence and read permissions; raise a descriptive exception if checks fail. |

#### 2. Configure and invoke the tokenizer training using the Hugging Face `tokenizers` library with the specified vocabulary size.

| Category | Details |
| --- | --- |
| **Reason** | The core functionality of the shim is to perform training; correct configuration ensures the tokenizer behaves as expected. |
| **Impact** | Produces a tokenizer model that can be reused downstream, affecting all subsequent tokenization steps. |
| **Complexity** | MEDIUM |
| **Method** | Instantiate a `tokenizers.Trainer` (e.g., `BpeTrainer`) with `vocab_size`; load the tokenizer via `tokenizers.Tokenizer.from_file`; call `tokenizer.train(files=[file_path], trainer=trainer)`. |

#### 3. Persist the trained tokenizer to disk and return a structured response containing the tokenizer identifier, file path, and vocabulary size.

| Category | Details |
| --- | --- |
| **Reason** | Storing the tokenizer allows reuse across nodes and sessions; returning structured data facilitates integration with downstream steps. |
| **Impact** | Adds reproducibility and traceability to the workflow, while enabling downstream nodes to load the tokenizer directly. |
| **Complexity** | MEDIUM |
| **Method** | Call `tokenizer.save(output_path)` to write the model; construct the output dictionary with the provided parameters and a status message (e.g., "Training completed successfully"). |


---

## tokenize_text_lines

### Description
The shim tokenizes each line of text using a provided tokenizer, returning a list of tokenized strings.

### Implementation Plan

#### 1. Implement the tokenization loop that applies the tokenizer’s `encode` or `batch_encode_plus` method to each text line, collecting the resulting token string representations.

| Category | Details |
| --- | --- |
| **Reason** | Ensures every input line is processed into tokens for downstream modeling. |
| **Impact** | Provides a consistent tokenized corpus for training or inference. |
| **Complexity** | MEDIUM |
| **Method** | Use `tokenizer.encode(line, add_special_tokens=True)` inside a list comprehension or a for-loop, converting token IDs to string with `tokenizer.convert_ids_to_tokens`. |

#### 2. Handle unknown tokens and special tokens by configuring the tokenizer with appropriate vocabulary and adding any missing special tokens before tokenization.

| Category | Details |
| --- | --- |
| **Reason** | Prevents tokenization errors and ensures special tokens are consistently represented. |
| **Impact** | Improves robustness and consistency across different datasets. |
| **Complexity** | LOW |
| **Method** | Invoke `tokenizer.add_tokens(['<unk>', '<pad>', '<s>', '</s>'])` and set `tokenizer.special_tokens_map` accordingly. |

#### 3. Return the list of tokenized strings directly, without converting to a single concatenated string or embedding structure, to maintain compatibility with downstream components.

| Category | Details |
| --- | --- |
| **Reason** | Keeps the output format simple and predictable for subsequent processing steps. |
| **Impact** | Avoids unnecessary serialization overhead and simplifies downstream parsing. |
| **Complexity** | LOW |
| **Method** | Ensure the function returns the list object as is (`return tokenized_texts_list`). |


---

## extract_unique_tokens

### Description
Extracts a set of unique tokens from a string of tokenized texts.

### Implementation Plan

#### 1. Parse the input string into individual tokens using whitespace and newline delimiters.

| Category | Details |
| --- | --- |
| **Reason** | Token extraction requires identifying individual token boundaries. |
| **Impact** | Ensures that all tokens are correctly considered for uniqueness. |
| **Complexity** | LOW |
| **Method** | Use Python's `str.split()` with default whitespace handling or split on `\n` and `\s+` to cover multi-line inputs. |

#### 2. Build a set of unique tokens from the parsed list to automatically deduplicate entries.

| Category | Details |
| --- | --- |
| **Reason** | Sets guarantee uniqueness and offer efficient membership checks. |
| **Impact** | Reduces memory footprint and computation time when handling large vocabularies. |
| **Complexity** | LOW |
| **Method** | Iterate over the token list and add each token to a Python `set` instance. |

#### 3. Return the unique tokens as a deterministic comma-separated string, sorted alphabetically for consistency.

| Category | Details |
| --- | --- |
| **Reason** | A consistent, sorted string format simplifies downstream consumption and testing. |
| **Impact** | Provides a stable output that can be parsed or displayed without ambiguity. |
| **Complexity** | LOW |
| **Method** | Apply `sorted()` to the set, then join with `', '` to form the output string. |


---

## create_sorted_vocabulary

### Description
Converts a string of unique tokens into a deterministically sorted list of tokens.

### Implementation Plan

#### 1. Parse the input string into individual tokens by splitting on commas and stripping whitespace, then deduplicate by converting to a set.

| Category | Details |
| --- | --- |
| **Reason** | The input is a raw string; parsing is required to obtain individual tokens and deduplication ensures uniqueness before sorting. |
| **Impact** | Provides a clean, duplicate-free collection of tokens for consistent sorting and downstream consumption. |
| **Complexity** | LOW |
| **Method** | Use Python's `str.split(',')` followed by `strip()` on each element, and convert the resulting list to a `set` to remove duplicates. |

#### 2. Sort the deduplicated token set lexicographically to produce a deterministic order.

| Category | Details |
| --- | --- |
| **Reason** | Deterministic ordering is necessary for reproducible tokenization pipelines and model consistency. |
| **Impact** | Guarantees that the same set of tokens always results in the same vocabulary order, facilitating caching and version control. |
| **Complexity** | LOW |
| **Method** | Apply Python's built-in `sorted()` function on the set, which returns a list sorted in ascending lexicographical order. |

#### 3. Return the sorted list as the `output` field of the shim's result.

| Category | Details |
| --- | --- |
| **Reason** | The downstream nodes expect a list of tokens to build the vocabulary and compute its size. |
| **Impact** | Ensures correct data type and structure for subsequent processing steps, preventing type errors. |
| **Complexity** | LOW |
| **Method** | Simply return the list obtained from the sorting step; no additional transformation is required. |


---

## save_tokenizer

### Description
Persists a trained tokenizer model to a specified file path for future reuse.

### Implementation Plan

#### 1. Validate the provided output path and ensure write permissions before attempting to serialize or write the tokenizer.

| Category | Details |
| --- | --- |
| **Reason** | Prevents runtime errors due to invalid directories or insufficient permissions. |
| **Impact** | Improves reliability and provides early error feedback to the caller. |
| **Complexity** | LOW |
| **Method** | Use `pathlib.Path` to check existence, create parent directories if missing, and verify write permissions via `os.access` or try‑except on write attempt. |

#### 2. Serialize the tokenizer into a portable format (e.g., JSON) and write it to the specified file path.

| Category | Details |
| --- | --- |
| **Reason** | Creates a reusable, human‑readable representation of the tokenizer for deployment or future loading. |
| **Impact** | Enables consistent tokenizer loading across environments and simplifies versioning. |
| **Complexity** | MEDIUM |
| **Method** | If the tokenizer is a HuggingFace instance, call `tokenizer.save_pretrained(output_path)`; otherwise convert to a dictionary via `tokenizer.get_vocab()` or similar and use `json.dump`. Capture the serialized string for the `tokenizer` output field. |

#### 3. Return a clear success message along with the serialized tokenizer string and the used output path.

| Category | Details |
| --- | --- |
| **Reason** | Provides immediate feedback to downstream processes and aids in debugging. |
| **Impact** | Facilitates confirmation of successful persistence and assists with traceability. |
| **Complexity** | LOW |
| **Method** | Construct a message such as `"Tokenizer successfully saved to {output_path}"` and return it in the `output` field; include the JSON string and path in their respective fields. |


---

## validate_tokenization_results

### Description
Validate that the tokenized texts and vocabulary are consistent and correctly sized.

### Implementation Plan

#### 1. Parse the comma‑separated input strings into Python lists and convert the vocab_size string to an integer for accurate comparison.

| Category | Details |
| --- | --- |
| **Reason** | The shim receives all inputs as strings; proper parsing is essential for subsequent validation steps. |
| **Impact** | Ensures that data types align with validation logic, preventing type errors during set operations. |
| **Complexity** | LOW |
| **Method** | Use str.split(',') to split strings, strip whitespace, and int() conversion for vocab_size. |

#### 2. Validate that every token in each tokenized text exists in the vocabulary set and that the reported vocab_size matches the actual unique token count.

| Category | Details |
| --- | --- |
| **Reason** | Guarantees the integrity of the tokenization process and catches any mismatches that could corrupt downstream training. |
| **Impact** | Prevents training failures due to inconsistent tokenization and provides immediate feedback to the pipeline. |
| **Complexity** | MEDIUM |
| **Method** | Create a set from the vocabulary list, iterate through tokenized_texts to check membership, and compare len(set) with vocab_size. |

#### 3. Generate a concise result string summarizing the validation outcome, listing any missing tokens, duplicate entries, or size mismatches, and return it as the output field.

| Category | Details |
| --- | --- |
| **Reason** | Clear reporting enables users to quickly identify and rectify tokenization issues. |
| **Impact** | Improves transparency and debuggability of the tokenization step within the ML pipeline. |
| **Complexity** | LOW |
| **Method** | Build a list of anomaly messages, join them with line breaks, and if no anomalies, return "Validation succeeded". |


---

## format_tokenized_texts

### Description
Converts a list of tokenized text strings into a single newline‑separated string for downstream use.

### Implementation Plan

#### 1. Validate that the input is a list of strings and sanitize each element to ensure UTF‑8 compliance.

| Category | Details |
| --- | --- |
| **Reason** | Prevents type errors and encoding issues when concatenating strings. |
| **Impact** | Guarantees that the function can handle malformed inputs without raising exceptions, improving robustness. |
| **Complexity** | LOW |
| **Method** | Use `isinstance(tokenized_texts, list)` and iterate with a list comprehension that casts each item to `str` with `.encode('utf-8', errors='replace').decode('utf-8')`. |

#### 2. Join the list into a single string separated by newline characters, optionally prefixing each line with a line number for debugging purposes.

| Category | Details |
| --- | --- |
| **Reason** | Provides a clear, human‑readable representation of tokenized data that downstream nodes can parse easily. |
| **Impact** | Simplifies downstream processing and logging, and makes debugging easier when inspecting the formatted output. |
| **Complexity** | MEDIUM |
| **Method** | Use `'
'.join(tokenized_texts)` to concatenate the list; to add line numbers, create a generator like `f"{i+1}: {token}" for i, token in enumerate(tokenized_texts)` before joining. |


---

## format_vocabulary

### Description
Converts a list of unique tokens into a deterministic, sorted, space‑delimited string for downstream use.

### Implementation Plan

#### 1. Parse the input JSON string to a Python list and validate it contains only strings.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the input format is correct before processing. |
| **Impact** | Prevents downstream errors caused by malformed input. |
| **Complexity** | LOW |
| **Method** | Use `json.loads(vocabulary)` and iterate to confirm each element is of type `str`. |

#### 2. Remove duplicates, sort the tokens, and join them into a single space‑delimited string.

| Category | Details |
| --- | --- |
| **Reason** | Provides deterministic ordering and eliminates redundancy for reproducible downstream pipelines. |
| **Impact** | Guarantees consistency across runs and simplifies comparison or diff operations. |
| **Complexity** | LOW |
| **Method** | Convert to `set()` to deduplicate, then `sorted()` for order, finally `' '.join(sorted_set)`. |

#### 3. Stream the formatting operation to avoid high memory usage for very large vocabularies.

| Category | Details |
| --- | --- |
| **Reason** | Prevents OOM errors when handling vocabularies with millions of tokens. |
| **Impact** | Enables the shim to operate on large datasets without requiring excessive RAM. |
| **Complexity** | MEDIUM |
| **Method** | Use a generator expression with `str.join` or write the output incrementally to a temporary file and read back as a string. |
