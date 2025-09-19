# -- PRD --
# 1. BULLET: Parse the project configuration to obtain data source definitions and
#   metadata requirements.
#   Reason: Using the configuration ensures that the node knows where to fetch data and
#           what constraints to apply, reducing hard‑coding and increasing
#           reproducibility.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Load the YAML/JSON config file specified by the environment, extract
#           `data_path` and `data_sources` fields, and validate that each
#           entry contains a `url` or `local_path` along with optional
#           `checksum`.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Download or copy all specified data sources, performing checksum verification
#   and retry logic where necessary.
#   Reason: Guarantees the integrity and availability of raw data, which is critical
#           for a high‑quality training corpus.
#   Impact: HIGH
#   Complexity: HIGH
#   Method: Use `requests` for HTTP(S) downloads, `shutil.copyfile` for local copies,
#           verify SHA‑256 checksums, and implement exponential back‑off
#           for transient failures.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Merge data from multiple sources into a single stream, removing exact
#   duplicate lines while preserving source order for provenance.
#   Reason: Avoids redundancy that could bias the model, yet keeps source traceability
#           for debugging.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Iterate through each file, yield lines to a `set` to track seen hashes,
#           write unique lines to a temporary output file.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Perform comprehensive text cleaning: normalize Unicode, strip HTML tags,
#   collapse whitespace, remove non‑ASCII characters beyond a defined
#   threshold, and filter out empty lines.
#   Reason: Cleaner data reduces noise in the tokenization step and improves model
#           generalization.
#   Impact: HIGH
#   Complexity: HIGH
#   Method: Use `unicodedata.normalize('NFKC')`, `html5lib` for tag removal, regular
#           expressions for whitespace collapse, and a configurable
#           `allowed_char_set` filter.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Estimate the token count using a lightweight tokenizer (e.g., NLTK's
#   `word_tokenize`) to avoid a full tokenization pass during preprocessing.
#   Reason: Provides an early metric for dataset size without incurring the full cost
#           of subword tokenization.
#   Impact: LOW
#   Complexity: LOW
#   Method: Apply `nltk.word_tokenize` to each cleaned line, count tokens, and
#           aggregate counts.
# 
# -----------------------------------------------------------------------------
# 6. BULLET: Write the cleaned lines to a compressed UTF‑8 file (e.g., Gzip) to reduce
#   disk usage and speed up downstream I/O.
#   Reason: Compressed storage conserves space and speeds up data loading for later
#           steps.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Open a `gzip.open` file in write mode, stream cleaned lines as UTF‑8
#           encoded bytes, and close the handle gracefully.
# 
# -----------------------------------------------------------------------------
# 7. BULLET: Populate the output structure: compute `sample_count`, `token_count`, set
#   `is_valid` based on success flags, and expose the final file path.
#   Reason: These metadata fields are required by downstream nodes and enable
#           validation checks before training.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Count the number of written lines for `sample_count`, use the token counter
#           from step 5 for `token_count`, and set `is_valid` to true if no
#           errors were encountered.
# -- END PRD --

from pydantic import BaseModel, Field


class PrepareTrainingDataOutput(BaseModel):
    """Pydantic model for prepare_training_data node outputs."""
    preprocessed_data_path: str = Field(..., description="File system path to the preprocessed training dataset")
    sample_count: int = Field(..., description="Total number of training samples in the dataset")
    token_count: int = Field(..., description="Total number of tokens after preprocessing")
    is_valid: bool = Field(..., description="Indicates whether the preprocessing was successful and the dataset is ready for further steps")


def prepare_training_data(general_input: str, **kwargs) -> PrepareTrainingDataOutput:
    """Collect and preprocess the dataset for training the language model.

    Args:
        general_input: General input string for the root node.
        **kwargs: Additional keyword arguments.

    Returns:
        PrepareTrainingDataOutput: Object containing outputs for this node.
    """
    # TODO: Implement this function

    # Return stub output with placeholder values
    return PrepareTrainingDataOutput(
        preprocessed_data_path="",
        sample_count=0,
        token_count=0,
        is_valid=False,
    )