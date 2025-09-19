# create_vocabulary PRD

## Description
Creates a unique token list (vocabulary) from the tokenized training data, records token frequencies, and validates the result.


## Implementation Plan

### 1. Aggregate all tokenized sentences into a single flat list of tokens.

| Category | Details |
| --- | --- |
| **Reason** | A flat list enables efficient frequency counting and eliminates per-sentence overhead. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use a list comprehension: `[token for sentence in tokenized_texts for token in sentence.split()]` or equivalent depending on token format. |

### 2. Count the occurrence of each token using a collections.Counter.

| Category | Details |
| --- | --- |
| **Reason** | Counter provides a fast, memory‑efficient frequency map directly from the token stream. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Instantiate `freq_counter = Counter(all_tokens)`; this yields a dict-like mapping token -> count. |

### 3. Apply a minimum frequency threshold (e.g., 2 or 5) to filter out extremely rare tokens.

| Category | Details |
| --- | --- |
| **Reason** | Low‑frequency tokens inflate vocab size without contributing much learning signal and may cause OOV issues. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Construct a filtered dict: `{t: c for t, c in freq_counter.items() if c >= min_freq}`; expose `min_freq` as a configurable parameter. |

### 4. Sort the remaining tokens by descending frequency to produce the final vocabulary list.

| Category | Details |
| --- | --- |
| **Reason** | Ordering by frequency allows optional truncation for sub‑vocabularies and facilitates reproducibility. |
| **Impact** | LOW |
| **Complexity** | MEDIUM |
| **Method** | Use `sorted_tokens = sorted(filtered_tokens.keys(), key=lambda t: filtered_tokens[t], reverse=True)`. |

### 5. Create two aligned lists: `vocabulary` (sorted token list) and `token_frequencies` (corresponding counts).

| Category | Details |
| --- | --- |
| **Reason** | Outputs must maintain index alignment for downstream consumption. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | List comprehension: `token_frequencies = [filtered_tokens[token] for token in sorted_tokens]`. |

### 6. Compute `vocab_size` as the length of the vocabulary list.

| Category | Details |
| --- | --- |
| **Reason** | Provides an easily consumable metric for architecture definition. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Set `vocab_size = len(vocabulary)`. |

### 7. Validate the result: `is_valid` should be True if `vocab_size` > 0; otherwise False.

| Category | Details |
| --- | --- |
| **Reason** | Ensures downstream nodes do not operate on an empty or corrupted vocabulary. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use a simple conditional: `is_valid = vocab_size > 0`. |

### 8. Package all four outputs into the specified data structure and log metadata for debugging.

| Category | Details |
| --- | --- |
| **Reason** | Debug logs aid reproducibility and quick fault isolation. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Create a dict: `output = { 'vocabulary': vocabulary, 'token_frequencies': token_frequencies, 'vocab_size': vocab_size, 'is_valid': is_valid }`; optionally log `f"vocab_size={vocab_size}, unique_tokens={len(filtered_tokens)}"`. |

### 9. Return the output structure exactly as defined, ensuring type consistency.

| Category | Details |
| --- | --- |
| **Reason** | Strict type adherence prevents downstream type errors. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use type annotations or runtime checks (e.g., `assert isinstance(vocabulary, list)`), then return the dict. |
