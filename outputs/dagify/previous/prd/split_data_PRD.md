# split_data PRD

## Description
Split the preprocessed data into training, validation, and test sets.


## Implementation Plan

### 1. Validate the incoming preprocessed data path and metadata.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that downstream operations have the correct input files and that the data is ready for splitting. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use os.path.exists to confirm file existence; read a small sample (e.g., 100 lines) with pandas to verify CSV/JSON structure; log any discrepancies. |

### 2. Determine the total sample count from the metadata provided by prepare_training_data.

| Category | Details |
| --- | --- |
| **Reason** | The split ratios are applied relative to this count; accurate counting prevents off‑by‑one errors. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Read the `sample_count` field directly; if not provided, perform a streaming count of the file using a line counter for large datasets. |

### 3. Generate a reproducible random permutation of sample indices using the configured split_seed.

| Category | Details |
| --- | --- |
| **Reason** | A fixed seed guarantees that the same splits are produced across runs, aiding debugging and reproducibility. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Instantiate numpy.random.default_rng(split_seed) and generate an array of indices with rng.permutation(sample_count). |

### 4. Compute split boundaries based on standard ratios (e.g., 80/10/10) or user‑supplied ratios, ensuring that the sum equals 1.0 within tolerance.

| Category | Details |
| --- | --- |
| **Reason** | Flexible ratios accommodate different project requirements while preventing mis‑allocation of samples. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Validate split_ratios length is 3; round each ratio to 4 decimal places; compute cumulative sums; calculate integer boundaries using floor and adjust the last boundary to consume all samples. |

### 5. Slice the permutation array into training, validation, and test index lists based on the computed boundaries.

| Category | Details |
| --- | --- |
| **Reason** | Direct indexing preserves the randomness introduced by the permutation and avoids bias. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use numpy array slicing: train_idx = perm[:train_boundary]; val_idx = perm[train_boundary:val_boundary]; test_idx = perm[val_boundary:] |

### 6. Read the full preprocessed data file once and write three separate files using the derived indices.

| Category | Details |
| --- | --- |
| **Reason** | A single pass minimizes I/O overhead; writing separate files is required for subsequent training stages. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Open the source file with a buffered reader; for each line, write to the appropriate output file based on its line number; use multiprocessing or asyncio if file is >1GB to keep memory usage low. |

### 7. Record the sizes of each split by counting written lines or using the boundary indices.

| Category | Details |
| --- | --- |
| **Reason** | Accurate split sizes are essential for reporting and for downstream model training loops. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use the lengths of the index arrays (train_idx, val_idx, test_idx) to set train_set_size, validation_set_size, test_set_size. |

### 8. Construct filesystem paths for each split file within a dedicated `splits/` directory under the original data path.

| Category | Details |
| --- | --- |
| **Reason** | Consistent path organization simplifies downstream path discovery and versioning. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Join os.path.dirname(preprocessed_data_path) with 'splits' and generate filenames like train.tsv, val.tsv, test.tsv. |

### 9. Persist split metadata to a JSON manifest file alongside the split datasets.

| Category | Details |
| --- | --- |
| **Reason** | A manifest provides a single source of truth for split details, aiding reproducibility and audit trails. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Create a dict with all output fields; write to 'splits/manifest.json' using json.dump with indentation for readability. |

### 10. Validate that the sum of train, validation, and test sizes equals the original sample count, and that the split ratios match the expected values within a tolerance of ±0.01.

| Category | Details |
| --- | --- |
| **Reason** | Detects any off‑by‑one or rounding errors introduced during integer boundary calculation. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Assert sum of sizes == sample_count; compute actual_ratios = [train/total, val/total, test/total] and compare to split_ratios using numpy.isclose. |

### 11. Return all output fields in the exact order specified by the output structure, ensuring type compliance.

| Category | Details |
| --- | --- |
| **Reason** | The downstream nodes consume these fields; type mismatches can cause silent failures. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Construct a dict with keys matching output_structure; cast values to int, float, str, or list accordingly; perform final type validation. |
