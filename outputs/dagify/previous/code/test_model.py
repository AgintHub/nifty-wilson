# -- PRD --
# 1. BULLET: Extract the fine‑tuned model file path and test dataset path from the parent
#   node fine_tune_model's output, and validate that both files exist on disk
#   before proceeding.
#   Reason: Ensures that downstream evaluation has the necessary inputs and prevents
#           runtime failures due to missing files.
#   Impact: LOW
#   Complexity: LOW
#   Method: Use os.path.exists() to confirm both paths, raise informative error if
#           missing.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Load the fine‑tuned model into memory using the same deep‑learning framework
#   that produced it (e.g., PyTorch), set the model to evaluation mode, and
#   attach the tokenizer that was used during training.
#   Reason: Consistent model state and tokenization are crucial for accurate metric
#           computation.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: torch.load(model_file_path), instantiate model class, call model.eval(),
#           load tokenizer from stored config.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Read the test dataset file (JSONL, CSV, or TFRecord) and convert each example
#   into tokenized input IDs using the loaded tokenizer.
#   Reason: Tokenization must mirror training to preserve vocabulary alignment.
#   Impact: LOW
#   Complexity: LOW
#   Method: Iterate over file lines, apply tokenizer.encode_plus(...), collect
#           input_ids and attention_masks.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Create a PyTorch DataLoader (or equivalent) for the test set with a batch
#   size derived from the original configuration, shuffling disabled for
#   deterministic evaluation.
#   Reason: Batching improves inference throughput and memory usage.
#   Impact: LOW
#   Complexity: LOW
#   Method: torch.utils.data.DataLoader(dataset, batch_size=config.batch_size,
#           shuffle=False).
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Run a no‑gradient inference loop: for each batch, compute logits, calculate
#   cross‑entropy loss, derive predicted token sequences, and aggregate
#   correct predictions to compute accuracy.
#   Reason: Collects the raw data needed to compute both perplexity and accuracy.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: with torch.no_grad(): loss = criterion(logits.view(-1, vocab_size),
#           targets.view(-1)), accumulate loss sum, track correct
#           predictions by comparing argmax predictions to targets.
# 
# -----------------------------------------------------------------------------
# 6. BULLET: After processing all batches, compute overall metrics: accuracy as (correct /
#   total), perplexity as exp(total_loss / total_tokens), and populate
#   metric_names and metric_values lists in the same order.
#   Reason: Matches the specified output schema and provides interpretable results.
#   Impact: LOW
#   Complexity: LOW
#   Method: accuracy = correct / total_tokens; perplexity = math.exp(total_loss /
#           total_tokens); metric_names = ['perplexity', 'accuracy'];
#           metric_values = [perplexity, accuracy].
# 
# -----------------------------------------------------------------------------
# 7. BULLET: Set test_dataset_size to the total number of examples in the test set
#   (len(dataset)).
#   Reason: Required field in output for downstream reporting.
#   Impact: LOW
#   Complexity: LOW
#   Method: test_dataset_size = len(dataset).
# 
# -----------------------------------------------------------------------------
# 8. BULLET: Wrap the entire evaluation process in a try/except block; if any exception
#   occurs, set evaluation_successful to False and log the error stack trace.
#   Reason: Guarantees that the node signals failure rather than crashing the workflow.
#   Impact: LOW
#   Complexity: LOW
#   Method: try: <evaluation code> except Exception as e: evaluation_successful =
#           False; log error.
# 
# -----------------------------------------------------------------------------
# 9. BULLET: Determine within_expected_range by comparing each metric against pre‑defined
#   thresholds (e.g., perplexity <= 20.0, accuracy >= 0.75). If all
#   conditions are satisfied, set the flag to True; otherwise, False.
#   Reason: Provides a quick pass/fail indicator for model quality.
#   Impact: LOW
#   Complexity: LOW
#   Method: within_expected_range = (perplexity <= 20.0) and (accuracy >= 0.75).
# -- END PRD --

from pydantic import BaseModel, Field


class FineTuneModelOutput(BaseModel):
    """Pydantic model for fine_tune_model node outputs."""
    model_file_path: str = Field(..., description="Filesystem path to the fine\u2011tuned model checkpoint.")
    fine_tuning_successful: bool = Field(..., description="Indicates whether the fine\u2011tuning process completed without errors.")
    num_fine_tuning_epochs: int = Field(..., description="Number of epochs used during fine\u2011tuning.")
    final_training_loss: float = Field(..., description="Loss value on the training set after fine\u2011tuning.")
    final_validation_perplexity: float = Field(..., description="Perplexity on the validation set after fine\u2011tuning.")


class TestModelOutput(BaseModel):
    """Pydantic model for test_model node outputs."""
    metric_names: str = Field(..., description="Names of evaluation metrics computed on the test set, e.g., "perplexity", "accuracy".")
    metric_values: float = Field(..., description="Numeric values corresponding to each metric in metric_names, in the same order.")
    test_dataset_size: int = Field(..., description="Number of samples in the test dataset.")
    evaluation_successful: bool = Field(..., description="Whether the evaluation process completed without errors.")
    within_expected_range: bool = Field(..., description="True if all metrics fall within pre\u2011defined acceptable ranges.")


def test_model(fine_tune_model_input: FineTuneModelOutput, **kwargs) -> TestModelOutput:
    """This node evaluates a fine‑tuned language model against a held‑out test set, calculating key performance metrics and determining whether the model meets predefined quality thresholds.

    Args:
        fine_tune_model_input: Input from the 'fine_tune_model' node.
        **kwargs: Additional keyword arguments.

    Returns:
        TestModelOutput: Object containing outputs for this node.
    """
    # TODO: Implement this function

    # Return stub output with placeholder values
    return TestModelOutput(
        metric_names="",
        metric_values=0.0,
        test_dataset_size=0,
        evaluation_successful=False,
        within_expected_range=False,
    )