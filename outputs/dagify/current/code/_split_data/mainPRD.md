# _split_data - Complete PRD Documentation

## Overview
PRDs for nodes in the '_split_data' module.

## Table of Contents

- [validate_data_path_and_metadata](#validate_data_path_and_metadata)

- [get_sample_count](#get_sample_count)

- [get_split_ratios_from_config](#get_split_ratios_from_config)

- [get_split_seed_from_config](#get_split_seed_from_config)

- [validate_split_ratios](#validate_split_ratios)

- [generate_random_permutation](#generate_random_permutation)

- [compute_split_boundaries](#compute_split_boundaries)

- [slice_permutation_by_boundaries](#slice_permutation_by_boundaries)

- [construct_split_file_paths](#construct_split_file_paths)

- [split_and_write_data_files](#split_and_write_data_files)

- [persist_split_metadata](#persist_split_metadata)

- [validate_split_results](#validate_split_results)



---

## validate_data_path_and_metadata

### Description
Validate that the data path exists and is readable, and that the supplied metadata conforms to the expected structure.

### Implementation Plan

#### 1. Check that the data path exists and is a readable file using `pathlib.Path`.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the downstream processes can locate and access the data. |
| **Impact** | Prevents runtime errors during data reading and splitting. |
| **Complexity** | LOW |
| **Method** | Use `Path(data_path).is_file()` and handle exceptions to return a descriptive error message. |

#### 2. Validate that the metadata is a valid Pydantic model instance or a dict that can be parsed into the expected model.

| Category | Details |
| --- | --- |
| **Reason** | Guarantees that required fields (e.g., sample count, token count) are present and correctly typed. |
| **Impact** | Catches data schema mismatches early, reducing downstream failures. |
| **Complexity** | MEDIUM |
| **Method** | Attempt to parse `metadata` with the relevant Pydantic model using `parse_obj` and capture validation errors. |

#### 3. Return a unified success message or detailed error information encapsulated as a plain string.

| Category | Details |
| --- | --- |
| **Reason** | Provides a clear, consistent interface for callers to interpret validation results. |
| **Impact** | Simplifies error handling in higher-level nodes and improves debugging visibility. |
| **Complexity** | LOW |
| **Method** | If validation passes, return `'Success'`; otherwise, return the concatenated error messages from the previous steps. |


---

## get_sample_count

### Description
Retrieves the total sample count from the provided training data metadata.

### Implementation Plan

#### 1. Validate that the metadata contains a `sample_count` attribute of type integer.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that the shim receives valid input before proceeding. |
| **Impact** | Prevents downstream failures caused by missing or malformed data. |
| **Complexity** | LOW |
| **Method** | Use `hasattr` and `isinstance(metadata.sample_count, int)` checks. |

#### 2. Return the `sample_count` value as the output.

| Category | Details |
| --- | --- |
| **Reason** | This is the core functionality required by downstream nodes. |
| **Impact** | Provides the necessary numeric value for data splitting logic. |
| **Complexity** | LOW |
| **Method** | Simple return statement: `return metadata.sample_count`. |

#### 3. Raise a descriptive `ValueError` if the `sample_count` attribute is missing or not an integer.

| Category | Details |
| --- | --- |
| **Reason** | Robust error handling improves reliability and debuggability. |
| **Impact** | Allows the system to fail fast with clear diagnostics. |
| **Complexity** | LOW |
| **Method** | Implement a conditional raise: `raise ValueError("Missing or invalid sample_count in metadata")`. |


---

## get_split_ratios_from_config

### Description
Retrieves the train, validation, and test split ratios from the provided configuration kwargs.

### Implementation Plan

#### 1. Parse the kwargs string into a dictionary and extract the 'split_ratios' key, ensuring it is a list of three floats summing to 1.0 within a tolerance.

| Category | Details |
| --- | --- |
| **Reason** | The shim must reliably retrieve the split configuration for downstream processing. |
| **Impact** | Prevents configuration errors from propagating to the split logic, ensuring reproducible dataset splits. |
| **Complexity** | MEDIUM |
| **Method** | Use `json.loads` to decode the string, then validate the presence and format of the key, checking length, numeric types, and that the sum of the list elements equals 1.0 ± 1e-6. |

#### 2. Return the extracted list of floats as the shim output.

| Category | Details |
| --- | --- |
| **Reason** | The downstream node expects a list of split ratios. |
| **Impact** | Provides the correct data type and value for subsequent split operations. |
| **Complexity** | LOW |
| **Method** | Simply return the validated list. |

#### 3. Raise a descriptive `ValueError` if the 'split_ratios' key is missing, malformed, or does not satisfy the sum constraint.

| Category | Details |
| --- | --- |
| **Reason** | Robust error handling is essential to surface misconfigurations early. |
| **Impact** | Avoids silent failures and makes debugging configuration issues straightforward. |
| **Complexity** | LOW |
| **Method** | Implement guard clauses that check for key existence and value validity, raising `ValueError` with clear error messages. |


---

## get_split_seed_from_config

### Description
Retrieves the split seed integer from the provided configuration parameters.

### Implementation Plan

#### 1. Parse the kwargs JSON string into a dictionary.

| Category | Details |
| --- | --- |
| **Reason** | Allows access to configuration values. |
| **Impact** | Enables dynamic extraction of the split seed. |
| **Complexity** | LOW |
| **Method** | Use Python's json.loads to convert the string into a dict. |

#### 2. Validate that the 'split_seed' key exists and is an integer.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the seed is present and correctly typed for reproducible splitting. |
| **Impact** | Prevents downstream errors caused by missing or malformed seed values. |
| **Complexity** | LOW |
| **Method** | Check for the key in the dict and use isinstance(value, int); raise ValueError if invalid. |

#### 3. Provide a default seed (e.g., 42) when the key is missing or invalid.

| Category | Details |
| --- | --- |
| **Reason** | Guarantees deterministic behavior even when configuration is incomplete. |
| **Impact** | Maintains reproducibility without requiring explicit seed in every config. |
| **Complexity** | LOW |
| **Method** | Return 42 if validation fails or key absent. |


---

## validate_split_ratios

### Description
Validates that the given split ratios list sums to 1.0 within a specified tolerance.

### Implementation Plan

#### 1. Parse the input string into a numeric list and compute the sum, ensuring it equals 1.0 within a tolerance of 1e-6.

| Category | Details |
| --- | --- |
| **Reason** | The split ratios must represent a valid probability distribution. |
| **Impact** | Prevents downstream errors caused by incorrect data partitioning. |
| **Complexity** | LOW |
| **Method** | Use json.loads to parse, sum the list, and compare to 1.0 with an epsilon. |

#### 2. If the sum deviates slightly due to floating‑point rounding, normalize the ratios by dividing each element by the computed sum.

| Category | Details |
| --- | --- |
| **Reason** | Allows tolerant handling of minor numeric inaccuracies while preserving relative proportions. |
| **Impact** | Ensures robustness of the splitter without manual adjustment. |
| **Complexity** | LOW |
| **Method** | Apply list comprehension: [x / total for x in ratios] and replace the original list. |

#### 3. Return a standardized output string ('Valid') or raise a ValueError with a clear message if validation fails.

| Category | Details |
| --- | --- |
| **Reason** | Provides a deterministic contract for downstream nodes to consume. |
| **Impact** | Guarantees consistent error handling across the pipeline. |
| **Complexity** | LOW |
| **Method** | If sum is within tolerance, return 'Valid'; otherwise, raise ValueError(f"Split ratios must sum to 1.0, got {total}"). |


---

## generate_random_permutation

### Description
Creates a reproducible random permutation of sample indices for data splitting.

### Implementation Plan

#### 1. Use a seeded random generator (e.g., NumPy's `default_rng` or Python's `random`) to produce a permutation array of size `sample_count`.

| Category | Details |
| --- | --- |
| **Reason** | A deterministic and high‑quality random permutation is required for reproducible data splits. |
| **Impact** | Ensures that subsequent splits are consistent across runs, facilitating reproducibility and debugging. |
| **Complexity** | LOW |
| **Method** | Instantiate `rng = np.random.default_rng(seed)` and call `rng.permutation(sample_count)`. |

#### 2. Validate that `sample_count` is a positive integer and `seed` is an integer; raise informative errors if not.

| Category | Details |
| --- | --- |
| **Reason** | Robust input validation prevents silent failures and mis‑configured splits. |
| **Impact** | Improves reliability and makes debugging easier by providing clear error messages. |
| **Complexity** | LOW |
| **Method** | Add simple type and value checks at the beginning of the function, using `isinstance` and value bounds. |

#### 3. Convert the NumPy array result to a plain Python list before returning to avoid downstream serialization issues.

| Category | Details |
| --- | --- |
| **Reason** | Standard library types are serializable and easier to consume in other parts of the pipeline. |
| **Impact** | Guarantees compatibility with JSON serialization and downstream tools expecting native Python lists. |
| **Complexity** | LOW |
| **Method** | Use `permutation.tolist()` before returning. |


---

## compute_split_boundaries

### Description
Computes integer split boundaries for training, validation, and test sets based on total sample count and split ratios.

### Implementation Plan

#### 1. Validate that `sample_count` is a positive integer and `ratios` is a list of floats summing to 1.0 within a small tolerance.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the function receives valid numeric inputs before performing calculations. |
| **Impact** | Prevents runtime errors and guarantees meaningful split boundaries. |
| **Complexity** | LOW |
| **Method** | Parse the string inputs into integers and floats; use `abs(sum(ratios) - 1.0) < 1e-6` for tolerance. |

#### 2. Compute cumulative split counts by multiplying `sample_count` with each ratio and casting to integers, then adjust for any rounding error to ensure the sum equals `sample_count`.

| Category | Details |
| --- | --- |
| **Reason** | Accurate boundaries are critical for balanced dataset splits. |
| **Impact** | Guarantees that no samples are lost or duplicated across splits. |
| **Complexity** | MEDIUM |
| **Method** | Use a loop to calculate each boundary: `boundary = int(round(sample_count * cumulative_ratio))`; after computing all boundaries, adjust the last boundary to `sample_count` if necessary. |

#### 3. Return the computed boundaries as a tuple `(train_boundary, val_boundary)` for downstream slicing.

| Category | Details |
| --- | --- |
| **Reason** | Provides a clear and consistent API for the `split_data` node. |
| **Impact** | Enables deterministic slicing of the shuffled permutation indices. |
| **Complexity** | LOW |
| **Method** | Return a Python tuple of the two boundary integers; optionally wrap in a JSON-serializable string if required by the shim interface. |


---

## slice_permutation_by_boundaries

### Description
Slices a shuffled permutation of dataset indices into training, validation, and test sets based on specified boundary indices.

### Implementation Plan

#### 1. Validate input types and boundary values to ensure they are integers and within the range of the permutation length.

| Category | Details |
| --- | --- |
| **Reason** | Guarantees correct slice indices and prevents runtime errors. |
| **Impact** | Improves robustness and reliability of the split operation. |
| **Complexity** | LOW |
| **Method** | Use isinstance checks and compare boundaries against len(permutation) before slicing. |

#### 2. Slice the permutation using efficient Python list slicing to create training, validation, and test index lists.

| Category | Details |
| --- | --- |
| **Reason** | Leverages built-in slice semantics for optimal performance. |
| **Impact** | Reduces memory overhead and execution time, especially for large datasets. |
| **Complexity** | LOW |
| **Method** | Return permutation[:train_boundary], permutation[train_boundary:val_boundary], permutation[val_boundary:] directly. |

#### 3. Return the sliced index lists as a JSON string for consistency with downstream node expectations.

| Category | Details |
| --- | --- |
| **Reason** | Standardizes output format across the pipeline. |
| **Impact** | Facilitates easier parsing and logging of split results. |
| **Complexity** | LOW |
| **Method** | Use json.dumps to serialize [train_indices, val_indices, test_indices] or return a tuple if the pipeline accepts Python objects. |


---

## construct_split_file_paths

### Description
Constructs file system paths for the training, validation, and test split files based on the original preprocessed data file path.

### Implementation Plan

#### 1. Derive base directory and filenames by appending '_train', '_validation', and '_test' to the original data file name before the extension.

| Category | Details |
| --- | --- |
| **Reason** | Ensures a clear, consistent naming scheme that is directly linked to the source data. |
| **Impact** | Provides immediately recognizable paths for downstream processing and logging. |
| **Complexity** | LOW |
| **Method** | Use pathlib to split the stem and suffix of original_data_path, then construct new filenames and join them with the parent directory. |

#### 2. Resolve relative paths to absolute ones and create parent directories if they do not exist to avoid file write errors.

| Category | Details |
| --- | --- |
| **Reason** | Robust file I/O requires that the filesystem locations are valid and writable. |
| **Impact** | Prevents runtime errors during split_and_write_data_files and ensures portability across environments. |
| **Complexity** | MEDIUM |
| **Method** | Use os.path.abspath on each constructed path and os.makedirs with exist_ok=True for the parent directories. |

#### 3. Validate that none of the target split paths already exist; if they do, append a numeric suffix or raise an informative error.

| Category | Details |
| --- | --- |
| **Reason** | Prevents accidental overwrite of existing split files and preserves data integrity. |
| **Impact** | Adds safety to the splitting pipeline and makes debugging easier. |
| **Complexity** | MEDIUM |
| **Method** | Use os.path.exists to check each path, and if a conflict is found, increment a numeric suffix until an unused path is obtained or raise a ValueError with a clear message. |


---

## split_and_write_data_files

### Description
Splits a pre‑processed data file into training, validation, and test files based on provided indices and writes each split to its designated path.

### Implementation Plan

#### 1. Parse the stringified index lists into Python lists and convert them into sets for O(1) membership checks.

| Category | Details |
| --- | --- |
| **Reason** | Efficient lookup is required when processing potentially millions of rows. |
| **Impact** | Reduces runtime from O(n*m) to O(n) where n is the number of lines and m is the number of indices. |
| **Complexity** | MEDIUM |
| **Method** | Use `json.loads` or `ast.literal_eval` to convert the strings, then cast to `set`. |

#### 2. Stream the source file line by line, using the line number to route each line to the appropriate output file.

| Category | Details |
| --- | --- |
| **Reason** | Avoids loading the entire dataset into memory, enabling scalability to large files. |
| **Impact** | Supports big‑data use cases and keeps memory footprint minimal. |
| **Complexity** | MEDIUM |
| **Method** | Open `source_path` with a `with open(...)` context manager, enumerate lines starting at 1, and write to the correct file based on set membership. |

#### 3. After processing, verify that the number of written rows matches the expected split sizes and that no indices are duplicated or missing.

| Category | Details |
| --- | --- |
| **Reason** | Ensures data integrity and prevents silent errors in downstream training. |
| **Impact** | Provides early failure detection and reliable split metadata. |
| **Complexity** | LOW |
| **Method** | Maintain counters per split during writing, then compare against the lengths of the original index lists. |


---

## persist_split_metadata

### Description
Persists split dataset metadata—including sizes, ratios, seed, and file paths—to a JSON manifest file.

### Implementation Plan

#### 1. Validate all input parameters for correct types and logical consistency (e.g., train_size + val_size + test_size equals total sample count).

| Category | Details |
| --- | --- |
| **Reason** | Prevent corrupt metadata and ensure downstream components receive accurate information. |
| **Impact** | Guarantees that the JSON manifest reflects the actual split sizes, improving data integrity. |
| **Complexity** | LOW |
| **Method** | Perform simple type checks and arithmetic validation before any file operations. |

#### 2. Serialize the metadata dictionary to a JSON file located alongside the original data file (e.g., `<original_data_path>_split_manifest.json`).

| Category | Details |
| --- | --- |
| **Reason** | Storing metadata in a dedicated manifest file allows easy retrieval and reproducibility. |
| **Impact** | Provides a clear, machine-readable record of the split configuration that can be reused by downstream processes. |
| **Complexity** | MEDIUM |
| **Method** | Use Python's `pathlib` to construct the manifest path, then write the dictionary with `json.dump` ensuring UTF‑8 encoding. |

#### 3. Implement robust error handling for I/O failures and JSON serialization errors, returning a descriptive error message in the `output` field.

| Category | Details |
| --- | --- |
| **Reason** | Graceful failure handling avoids silent crashes and aids debugging. |
| **Impact** | Improves system reliability and provides clear feedback to users or orchestration tools. |
| **Complexity** | LOW |
| **Method** | Wrap file operations in a try/except block catching `OSError` and `json.JSONDecodeError`, and set `output` to an informative error string. |


---

## validate_split_results

### Description
Validates that the split sizes match the original count and expected ratios.

### Implementation Plan

#### 1. Check that the sum of train, validation, and test sizes equals the original sample count.

| Category | Details |
| --- | --- |
| **Reason** | Ensures no data is lost or duplicated during splitting. |
| **Impact** | Guarantees data integrity for downstream training and evaluation. |
| **Complexity** | LOW |
| **Method** | Convert all size strings to integers, sum them, and compare with the original count; raise an informative ValueError if they differ. |

#### 2. Validate that the actual split ratios derived from the sizes match the expected ratios within a tolerance.

| Category | Details |
| --- | --- |
| **Reason** | Guarantees that the splits reflect the intended proportions. |
| **Impact** | Prevents skewed training/validation/test distributions that could bias model performance. |
| **Complexity** | MEDIUM |
| **Method** | Parse the expected_ratios string into a list of floats, compute actual ratios using the sizes, then compare each ratio to the expected value using an epsilon threshold (e.g., 1e-3); raise a ValueError on mismatch. |

#### 3. Return a human‑readable status string summarizing the validation outcome.

| Category | Details |
| --- | --- |
| **Reason** | Provides clear feedback to users and downstream nodes. |
| **Impact** | Improves usability and debugging by exposing validation results. |
| **Complexity** | LOW |
| **Method** | If all checks pass, set `output` to "Validation succeeded."; otherwise include error details. |
