# normalize_strategy_type PRD

## Description
Normalizes a raw strategy_type string to a canonical lowercase identifier, handling synonyms, whitespace, and case variations.


## Implementation Plan

### 1. Create a synonym dictionary mapping known aliases (e.g., "MOM", "mom", "momentum") to their canonical form.

| Category | Details |
| --- | --- |
| **Reason** | Users may provide strategy names in various abbreviations or capitalizations, and a deterministic mapping is required for downstream rule selection. |
| **Impact** | Ensures consistent strategy identification across the pipeline, preventing mismatches in rule templates. |
| **Complexity** | LOW |
| **Method** | Define a static Python dict `synonym_map` and perform a lookup after normalizing the input to lower‑case and stripping whitespace. |

### 2. Sanitize the input by trimming leading/trailing whitespace and converting to lower case before lookup.

| Category | Details |
| --- | --- |
| **Reason** | Raw inputs often contain extra spaces or mixed‑case characters that would break direct dictionary matches. |
| **Impact** | Reduces false‑negative matches and eliminates the need for repetitive preprocessing elsewhere. |
| **Complexity** | LOW |
| **Method** | Apply `strategy_type.strip().lower()` prior to dictionary lookup; fallback to the stripped value if not found in the synonym map. |

### 3. Validate the normalized result against an allow‑list of supported strategies and raise a clear error if unsupported.

| Category | Details |
| --- | --- |
| **Reason** | Downstream nodes assume a known set of strategy identifiers; an invalid value would cause cascade failures. |
| **Impact** | Provides early, descriptive failure feedback, improving debuggability and system robustness. |
| **Complexity** | MEDIUM |
| **Method** | Maintain a set `VALID_STRATEGIES`; after normalization, check membership and raise `ValueError` with a helpful message if absent. |
