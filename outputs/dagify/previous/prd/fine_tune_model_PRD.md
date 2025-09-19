# fine_tune_model PRD

## Description
Fine‑tune the base language model using a task‑specific dataset to improve downstream performance. The node consumes evaluation metrics from the base model and produces a fine‑tuned checkpoint along with training statistics.


## Implementation Plan

### 1. Validate the evaluate_model input: ensure that `perplexity`, `accuracy`, `cross_entropy_loss`, and `validation_samples` are present and of type float/int. If any are missing or NaN, abort fine‑tuning with `fine_tuning_successful = false` and log an error.

| Category | Details |
| --- | --- |
| **Reason** | Early validation prevents downstream failures due to corrupted or incomplete metrics. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Implement a simple schema check using Python type hints and `math.isnan` for floats; raise a descriptive exception if validation fails. |

### 2. Retrieve the path to the trained model checkpoint. Prefer the environment variable `MODEL_PATH`; if unset, fall back to a hard‑coded path from the project configuration (`model_output_path`). Verify that the file exists before proceeding.

| Category | Details |
| --- | --- |
| **Reason** | Fine‑tuning requires the base weights; ensuring the checkpoint is available avoids runtime errors. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use `os.getenv` with a default, then `os.path.isfile`; if not found, emit a warning and set `fine_tuning_successful = false`. |

### 3. Load the downstream fine‑tuning dataset from a configuration parameter (e.g., `fine_tune_dataset_path`). If the path is relative, resolve it against the project root. Use a data loader that yields batches of tokenized inputs and labels suitable for the task (e.g., classification or sequence labeling).

| Category | Details |
| --- | --- |
| **Reason** | Task‑specific data is needed for supervised fine‑tuning and may differ in format from the pretraining corpus. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Instantiate a `torch.utils.data.Dataset` subclass that reads the file, tokenizes using the same tokenizer used in pretraining, and returns tensors. Cache the dataset to avoid repeated I/O. |

### 4. Set fine‑tuning hyperparameters: epoch count (`fine_tune_epochs`), learning rate (`fine_tune_lr`), batch size (`fine_tune_batch_size`). Use default values from the configuration if not explicitly overridden, but allow command‑line overrides via environment variables for flexibility.

| Category | Details |
| --- | --- |
| **Reason** | Hyperparameter flexibility lets the user adapt the fine‑tuning to the size of the downstream dataset. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Read from a dedicated `fine_tune_config.json` file; use `argparse`‑style precedence (env > config > defaults). |

### 5. Initialize the model for fine‑tuning: load the base checkpoint into the same architecture, optionally replacing the final classification head with a task‑specific head if the downstream task differs from pretraining (e.g., add a `nn.Linear` for NER).

| Category | Details |
| --- | --- |
| **Reason** | Task‑specific heads enable the model to produce predictions aligned with the target labels. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use HuggingFace `AutoModelForSequenceClassification` or `AutoModelForTokenClassification` depending on task; if the head differs, call `model.resize_token_embeddings` and reinitialize the new head with Xavier uniform. |

### 6. Define the optimizer and scheduler: use AdamW with weight decay, and a linear scheduler with warmup proportional to `fine_tune_epochs`. Tie the learning rate to the base training rate scaled by a fine‑tune factor (e.g., 0.1).

| Category | Details |
| --- | --- |
| **Reason** | AdamW with warmup stabilizes fine‑tuning and prevents catastrophic forgetting. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Instantiate `torch.optim.AdamW` with `weight_decay=0.01`; create `get_linear_schedule_with_warmup` from `transformers` library. |

### 7. Implement the training loop: for each epoch, iterate over the fine‑tuning data loader, compute loss, perform back‑propagation, update parameters, and record training loss. After each epoch, evaluate on the validation split (derived from the same fine‑tune dataset) to compute perplexity using the same metric as the base evaluation.

| Category | Details |
| --- | --- |
| **Reason** | Capturing per‑epoch metrics enables monitoring and early stopping decisions. |
| **Impact** | HIGH |
| **Complexity** | HIGH |
| **Method** | Use `torch.no_grad()` for validation; compute perplexity as `torch.exp(torch.mean(loss))`. Store the best epoch based on lowest validation perplexity. |

### 8. Implement early stopping: if validation perplexity does not improve for `patience` consecutive epochs (default 3), terminate training early to save compute.

| Category | Details |
| --- | --- |
| **Reason** | Prevents over‑fitting and reduces unnecessary compute time. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Maintain a counter of non‑improvement epochs; break loop when threshold exceeded. |

### 9. After training, compute the final training loss as the average loss over the last epoch and the final validation perplexity from the best epoch. Save the fine‑tuned model checkpoint to a new path derived from the project output directory (e.g., `model_output_path/fine_tuned_checkpoint.pt`).

| Category | Details |
| --- | --- |
| **Reason** | Providing concrete metrics allows downstream nodes to assess fine‑tuning quality. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Call `model.save_pretrained()` for HuggingFace models or `torch.save` for plain state_dicts. |

### 10. Populate the output fields: set `model_file_path` to the saved checkpoint path, `fine_tuning_successful = true`, `num_fine_tuning_epochs` to the number of epochs actually run, `final_training_loss` to the last epoch average loss, and `final_validation_perplexity` to the best validation perplexity.

| Category | Details |
| --- | --- |
| **Reason** | All required outputs must be deterministically derived from the fine‑tuning process. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Construct a dictionary mapping the output keys to the computed values and return it. |

### 11. Log all key events (start, per‑epoch metrics, early stop, final status) to a log file located alongside the checkpoint for traceability.

| Category | Details |
| --- | --- |
| **Reason** | Logging aids debugging and audit trails for ML pipelines. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use Python's `logging` module with a file handler; format logs in JSON for downstream ingestion. |
