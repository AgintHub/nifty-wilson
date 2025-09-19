# -- PRD --
# 1. BULLET: Validate the incoming preprocessed data path and metadata.
#   Reason: Ensures that downstream operations have the correct input files and that
#           the data is ready for splitting.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Use os.path.exists to confirm file existence; read a small sample (e.g.,
#           100 lines) with pandas to verify CSV/JSON structure; log any
#           discrepancies.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Determine the total sample count from the metadata provided by
#   prepare_training_data.
#   Reason: The split ratios are applied relative to this count; accurate counting
#           prevents off‑by‑one errors.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Read the `sample_count` field directly; if not provided, perform a
#           streaming count of the file using a line counter for large
#           datasets.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Generate a reproducible random permutation of sample indices using the
#   configured split_seed.
#   Reason: A fixed seed guarantees that the same splits are produced across runs,
#           aiding debugging and reproducibility.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Instantiate numpy.random.default_rng(split_seed) and generate an array of
#           indices with rng.permutation(sample_count).
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Compute split boundaries based on standard ratios (e.g., 80/10/10) or
#   user‑supplied ratios, ensuring that the sum equals 1.0 within tolerance.
#   Reason: Flexible ratios accommodate different project requirements while preventing
#           mis‑allocation of samples.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Validate split_ratios length is 3; round each ratio to 4 decimal places;
#           compute cumulative sums; calculate integer boundaries using
#           floor and adjust the last boundary to consume all samples.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Slice the permutation array into training, validation, and test index lists
#   based on the computed boundaries.
#   Reason: Direct indexing preserves the randomness introduced by the permutation and
#           avoids bias.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Use numpy array slicing: train_idx = perm[:train_boundary]; val_idx =
#           perm[train_boundary:val_boundary]; test_idx =
#           perm[val_boundary:]
# 
# -----------------------------------------------------------------------------
# 6. BULLET: Read the full preprocessed data file once and write three separate files
#   using the derived indices.
#   Reason: A single pass minimizes I/O overhead; writing separate files is required
#           for subsequent training stages.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Open the source file with a buffered reader; for each line, write to the
#           appropriate output file based on its line number; use
#           multiprocessing or asyncio if file is >1GB to keep memory usage
#           low.
# 
# -----------------------------------------------------------------------------
# 7. BULLET: Record the sizes of each split by counting written lines or using the
#   boundary indices.
#   Reason: Accurate split sizes are essential for reporting and for downstream model
#           training loops.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Use the lengths of the index arrays (train_idx, val_idx, test_idx) to set
#           train_set_size, validation_set_size, test_set_size.
# 
# -----------------------------------------------------------------------------
# 8. BULLET: Construct filesystem paths for each split file within a dedicated `splits/`
#   directory under the original data path.
#   Reason: Consistent path organization simplifies downstream path discovery and
#           versioning.
#   Impact: LOW
#   Complexity: LOW
#   Method: Join os.path.dirname(preprocessed_data_path) with 'splits' and generate
#           filenames like train.tsv, val.tsv, test.tsv.
# 
# -----------------------------------------------------------------------------
# 9. BULLET: Persist split metadata to a JSON manifest file alongside the split datasets.
#   Reason: A manifest provides a single source of truth for split details, aiding
#           reproducibility and audit trails.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Create a dict with all output fields; write to 'splits/manifest.json' using
#           json.dump with indentation for readability.
# 
# -----------------------------------------------------------------------------
# 10. BULLET: Validate that the sum of train, validation, and test sizes equals the
#   original sample count, and that the split ratios match the expected
#   values within a tolerance of ±0.01.
#   Reason: Detects any off‑by‑one or rounding errors introduced during integer
#           boundary calculation.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Assert sum of sizes == sample_count; compute actual_ratios = [train/total,
#           val/total, test/total] and compare to split_ratios using
#           numpy.isclose.
# 
# -----------------------------------------------------------------------------
# 11. BULLET: Return all output fields in the exact order specified by the output
#   structure, ensuring type compliance.
#   Reason: The downstream nodes consume these fields; type mismatches can cause silent
#           failures.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Construct a dict with keys matching output_structure; cast values to int,
#           float, str, or list accordingly; perform final type validation.
# -- END PRD --

from pydantic import BaseModel, Field


class PrepareTrainingDataOutput(BaseModel):
    """Pydantic model for prepare_training_data node outputs."""
    preprocessed_data_path: str = Field(..., description="File system path to the preprocessed training dataset")
    sample_count: int = Field(..., description="Total number of training samples in the dataset")
    token_count: int = Field(..., description="Total number of tokens after preprocessing")
    is_valid: bool = Field(..., description="Indicates whether the preprocessing was successful and the dataset is ready for further steps")


class SplitDataOutput(BaseModel):
    """Pydantic model for split_data node outputs."""
    train_set_size: int = Field(..., description="Number of examples in the training set")
    validation_set_size: int = Field(..., description="Number of examples in the validation set")
    test_set_size: int = Field(..., description="Number of examples in the test set")
    train_data_path: str = Field(..., description="Filesystem path to the training dataset file")
    validation_data_path: str = Field(..., description="Filesystem path to the validation dataset file")
    test_data_path: str = Field(..., description="Filesystem path to the test dataset file")
    split_ratios: float = Field(..., description="Ratios used for splitting the data, in order [train, validation, test]")
    split_seed: int = Field(..., description="Random seed used for reproducibility during splitting")


def split_data(prepare_training_data_input: PrepareTrainingDataOutput, **kwargs) -> SplitDataOutput:
    """Split the preprocessed data into training, validation, and test sets.

    Args:
        prepare_training_data_input: Input from the 'prepare_training_data' node.
        **kwargs: Additional keyword arguments.

    Returns:
        SplitDataOutput: Object containing outputs for this node.
    """
    # TODO: Implement this function

    # Return stub output with placeholder values
    return SplitDataOutput(
        train_set_size=0,
        validation_set_size=0,
        test_set_size=0,
        train_data_path="",
        validation_data_path="",
        test_data_path="",
        split_ratios=0.0,
        split_seed=0,
    )