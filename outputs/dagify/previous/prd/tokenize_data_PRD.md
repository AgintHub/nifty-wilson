# tokenize_data PRD

## Description
Tokenize the prepared training data into subwords or tokens.


## Implementation Plan

### 1. Read the preprocessed dataset file from `preprocessed_data_path` provided by the parent node and load it into memory as a list of raw text lines.

| Category | Details |
| --- | --- |
| **Reason** | Ensuring the input is available in a consistent format is critical before any tokenization logic can be applied. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use `open(file_path, 'r', encoding='utf-8')` and `read().splitlines()` to create a list of strings. |

### 2. Select the tokenization algorithm based on a configuration flag (`tokenization_method`) passed via environment variables or a config file (default to 'BPE' if unspecified).

| Category | Details |
| --- | --- |
| **Reason** | Providing flexibility allows the workflow to adapt to different subword strategies without code changes. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Read env variable `TOKENIZATION_METHOD` with fallback to 'bpe'. Normalize to lower case for consistency. |

### 3. Instantiate the chosen tokenizer using the HuggingFace Tokenizers library (`tokenizers.Tokenizer` with `BPE` or `WordPiece` models). Configure essential options: case sensitivity, unknown token handling, and pre-tokenizer to split on whitespace.

| Category | Details |
| --- | --- |
| **Reason** | HuggingFace Tokenizers offers highly efficient, C++-backed implementations suitable for large corpora. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | For BPE: `Tokenizer.from_pretrained('bert-base-uncased', use_fast=True)` and adjust `tokenizer.pre_tokenizer` to `Whitespace()`. For WordPiece: use `tokenizer.from_pretrained('bert-base-uncased')` and set `tokenizer.pre_tokenizer` to `Whitespace()`. Configure `tokenizer.post_processor` to add special tokens if required. |

### 4. Train the tokenizer on the loaded text corpus by invoking `tokenizer.train(files=...)` with a specified vocabulary size (e.g., 32,000) and optional special tokens (`[CLS]`, `[SEP]`, `[UNK]`, `[PAD]`).

| Category | Details |
| --- | --- |
| **Reason** | Training builds a subword vocabulary tailored to the dataset, improving tokenization quality and downstream model performance. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Pass `files=[preprocessed_data_path]` and set `vocab_size` and `min_frequency` parameters. Capture training logs for reproducibility. |

### 5. Apply the trained tokenizer to every line in the corpus, converting each raw text string into a list of token IDs and then back to token strings using `tokenizer.decode`. Store these token strings in `tokenized_texts` as space‑separated tokens.

| Category | Details |
| --- | --- |
| **Reason** | Converting to token strings preserves readability for downstream processes like vocabulary extraction and allows easier debugging. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Iterate over the text list: `for line in text_list: tokens = tokenizer.encode(line).tokens; tokenized_texts.append(' '.join(tokens))`. |

### 6. Aggregate all tokens from `tokenized_texts` into a Python set to deduplicate and extract the unique vocabulary.

| Category | Details |
| --- | --- |
| **Reason** | Using a set guarantees uniqueness efficiently, which is critical for building a correct vocabulary list. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Initialize an empty set and update it with `set.update(tokens.split())` for each entry in `tokenized_texts`. |

### 7. Convert the set of unique tokens into a sorted list and assign it to the `vocabulary` output. Compute `vocab_size` as the length of this list.

| Category | Details |
| --- | --- |
| **Reason** | Sorting provides deterministic ordering which aids reproducibility of downstream steps (e.g., creating embeddings). |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use `vocabulary = sorted(list(unique_tokens))` and `vocab_size = len(vocabulary)`. |

### 8. Persist the tokenizer model and vocabulary to disk for later reuse in the `create_vocabulary` node (e.g., `tokenizer.save('tokenizer.json')`).

| Category | Details |
| --- | --- |
| **Reason** | Storing the trained tokenizer ensures consistency between tokenization and vocabulary creation steps, preventing accidental drift. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Call `tokenizer.save('tokenizer.json')` after training. |

### 9. Validate that `vocab_size` matches the length of the `vocabulary` list and that `tokenized_texts` is non-empty; log any anomalies and raise an exception if validation fails.

| Category | Details |
| --- | --- |
| **Reason** | Early validation catches data pipeline issues before they propagate to later stages like training. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Implement assertion checks and structured logging via the `logging` module. |
