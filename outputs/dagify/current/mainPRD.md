# train_large_language_model - Complete PRD Documentation

## Overview
PRDs for nodes in the 'train_large_language_model' module.

## Table of Contents

- [allocate_resources](#allocate_resources)

- [create_vocabulary](#create_vocabulary)

- [define_model_architecture](#define_model_architecture)

- [evaluate_model](#evaluate_model)

- [fine_tune_model](#fine_tune_model)

- [initialize_model_weights](#initialize_model_weights)

- [load_configuration](#load_configuration)

- [prepare_training_data](#prepare_training_data)

- [setup_environment](#setup_environment)

- [split_data](#split_data)

- [test_model](#test_model)

- [tokenize_data](#tokenize_data)

- [train_model](#train_model)



---

## allocate_resources

### Description
Reserve the necessary hardware resources.

### Implementation Plan

#### 1. Extract GPU requirement parameters from the configuration returned by load_configuration, using keys such as requested_gpu_count, requested_gpu_type, and memory_per_gpu. If any key is missing, fall back to sensible defaults (e.g., 1 V100, 16 GB).

| Category | Details |
| --- | --- |
| **Reason** | Explicitly capturing the user’s GPU preferences ensures deterministic allocation and avoids hard‑coded assumptions. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Parse the load_configuration output dictionary; use dict.get with default values; perform type validation and conversion to int/float. |

#### 2. Validate that the requested number of GPUs is available on the target compute node or cluster by querying the system’s GPU inventory (e.g., `nvidia-smi --list-gpus` for local nodes, or the cluster scheduler API for cloud environments).

| Category | Details |
| --- | --- |
| **Reason** | Pre‑emptively detecting insufficiencies prevents runtime failures and resource contention. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Execute the appropriate inventory command via subprocess, or call the scheduler’s REST endpoint; parse the output to count free GPUs of the requested type; handle exceptions and timeouts. |

#### 3. If the inventory check passes, request allocation of the specified GPUs using the platform’s resource allocation interface (e.g., Slurm `srun --gres=gpu:count`, Kubernetes GPU requests in Pod spec, or a direct CUDA context allocation for local runs).

| Category | Details |
| --- | --- |
| **Reason** | Actual resource reservation is required before model initialization to avoid oversubscription and to lock the GPUs for the training job. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | For cloud environments, construct the job submission JSON and POST to the cluster’s API; for local nodes, invoke CUDA driver calls (cuDeviceGetCount, cuCtxCreate) to lock GPUs; verify allocation status via API responses or CUDA error codes. |

#### 4. Compute the total memory to be reported as `memory_gb` by multiplying the allocated GPU count by the per‑GPU memory (converted to gigabytes).

| Category | Details |
| --- | --- |
| **Reason** | Providing an aggregate memory figure simplifies downstream budgeting and monitoring. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use a simple arithmetic operation: memory_gb = gpu_count * memory_per_gpu; ensure result is float and round to two decimal places. |

#### 5. Populate the output structure: set `gpu_count`, `gpu_type`, `memory_gb`, and determine `allocation_success` based on the success flags returned by the allocation API and any exceptions caught during the process.

| Category | Details |
| --- | --- |
| **Reason** | Accurately conveying allocation status is critical for error propagation to downstream nodes. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Create a dict with the four fields; if any step fails, set allocation_success to false and assign zeroes or empty strings for other fields; otherwise set true and the actual values. |

#### 6. Log the allocation attempt with details such as timestamp, requested parameters, actual allocated GPUs, and any error messages, storing the log in a temporary file or returning it in a hidden side channel for auditing purposes.

| Category | Details |
| --- | --- |
| **Reason** | Traceability aids debugging and compliance with resource usage policies. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Format a JSON or plain‑text log entry; write to a file in /tmp or append to an in‑memory list; expose via an optional `allocation_log` output if the node interface allows. |


---

## create_vocabulary

### Description
Creates a unique token list (vocabulary) from the tokenized training data, records token frequencies, and validates the result.

### Implementation Plan

#### 1. Aggregate all tokenized sentences into a single flat list of tokens.

| Category | Details |
| --- | --- |
| **Reason** | A flat list enables efficient frequency counting and eliminates per-sentence overhead. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use a list comprehension: `[token for sentence in tokenized_texts for token in sentence.split()]` or equivalent depending on token format. |

#### 2. Count the occurrence of each token using a collections.Counter.

| Category | Details |
| --- | --- |
| **Reason** | Counter provides a fast, memory‑efficient frequency map directly from the token stream. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Instantiate `freq_counter = Counter(all_tokens)`; this yields a dict-like mapping token -> count. |

#### 3. Apply a minimum frequency threshold (e.g., 2 or 5) to filter out extremely rare tokens.

| Category | Details |
| --- | --- |
| **Reason** | Low‑frequency tokens inflate vocab size without contributing much learning signal and may cause OOV issues. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Construct a filtered dict: `{t: c for t, c in freq_counter.items() if c >= min_freq}`; expose `min_freq` as a configurable parameter. |

#### 4. Sort the remaining tokens by descending frequency to produce the final vocabulary list.

| Category | Details |
| --- | --- |
| **Reason** | Ordering by frequency allows optional truncation for sub‑vocabularies and facilitates reproducibility. |
| **Impact** | LOW |
| **Complexity** | MEDIUM |
| **Method** | Use `sorted_tokens = sorted(filtered_tokens.keys(), key=lambda t: filtered_tokens[t], reverse=True)`. |

#### 5. Create two aligned lists: `vocabulary` (sorted token list) and `token_frequencies` (corresponding counts).

| Category | Details |
| --- | --- |
| **Reason** | Outputs must maintain index alignment for downstream consumption. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | List comprehension: `token_frequencies = [filtered_tokens[token] for token in sorted_tokens]`. |

#### 6. Compute `vocab_size` as the length of the vocabulary list.

| Category | Details |
| --- | --- |
| **Reason** | Provides an easily consumable metric for architecture definition. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Set `vocab_size = len(vocabulary)`. |

#### 7. Validate the result: `is_valid` should be True if `vocab_size` > 0; otherwise False.

| Category | Details |
| --- | --- |
| **Reason** | Ensures downstream nodes do not operate on an empty or corrupted vocabulary. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use a simple conditional: `is_valid = vocab_size > 0`. |

#### 8. Package all four outputs into the specified data structure and log metadata for debugging.

| Category | Details |
| --- | --- |
| **Reason** | Debug logs aid reproducibility and quick fault isolation. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Create a dict: `output = { 'vocabulary': vocabulary, 'token_frequencies': token_frequencies, 'vocab_size': vocab_size, 'is_valid': is_valid }`; optionally log `f"vocab_size={vocab_size}, unique_tokens={len(filtered_tokens)}"`. |

#### 9. Return the output structure exactly as defined, ensuring type consistency.

| Category | Details |
| --- | --- |
| **Reason** | Strict type adherence prevents downstream type errors. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use type annotations or runtime checks (e.g., `assert isinstance(vocabulary, list)`), then return the dict. |


---

## define_model_architecture

### Description
Define the architecture and configuration of the large language model.

### Implementation Plan

#### 1. Extract the vocabulary size and GPU allocation metrics from the outputs of create_vocabulary and allocate_resources to serve as constraints for architecture sizing.

| Category | Details |
| --- | --- |
| **Reason** | The vocab_size dictates the size of the embedding matrix, while GPU memory limits constrain hidden layer dimensionality and overall parameter count. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Read 'vocab_size' from create_vocabulary output; read 'gpu_count', 'gpu_type', and 'memory_gb' from allocate_resources output; store them in local variables for later calculations. |

#### 2. Compute an initial estimate of total trainable parameters using the closed‑form formula for a transformer: params ≈ vocab_size * hidden_size + 12 * number_of_layers * hidden_size^2 + ... and round to nearest integer.

| Category | Details |
| --- | --- |
| **Reason** | Having a parameter budget early helps validate that the chosen hyper‑parameters fit within hardware constraints and guides subsequent decisions. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Implement a helper function that accepts vocab_size, hidden_size, number_of_layers, attention_heads and returns an integer estimate; use the standard transformer parameter count formula including embedding, layer norm, feed‑forward, and attention projection terms. |

#### 3. Determine number_of_layers by balancing desired performance, convergence speed, and available GPU memory: start from a baseline (e.g., 12 layers) and increase until the estimated parameter count approaches but does not exceed 90% of the GPU memory capacity per GPU.

| Category | Details |
| --- | --- |
| **Reason** | Layer depth is a primary driver of model capacity; staying within memory limits prevents out‑of‑memory failures during training. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Iteratively loop over candidate layer counts (e.g., 6, 12, 24, 36); for each, compute total_parameters (from bullet 2) and compare against memory_gb * gpu_count * 0.9 * 1024 (bytes). Select the largest count that satisfies the constraint. |

#### 4. Select hidden_size such that the product hidden_size * number_of_layers * hidden_size fits within the remaining memory after accounting for embeddings and optimizer states; also enforce that hidden_size % attention_heads == 0.

| Category | Details |
| --- | --- |
| **Reason** | Hidden size directly scales the memory footprint of activations and gradients; ensuring divisibility by attention_heads preserves efficient attention implementation. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Compute the available memory per GPU in bytes; subtract memory needed for embedding (vocab_size * hidden_size * 4 bytes) and optimizer buffers (≈ 2 * hidden_size * number_of_layers * hidden_size). Solve for hidden_size iteratively, checking divisibility by candidate attention_heads (typically 8, 12, 16). Choose the largest hidden_size that satisfies both constraints. |

#### 5. Set attention_heads by choosing a value that evenly divides hidden_size and aligns with common transformer configurations (e.g., 8, 12, 16); default to 12 if hidden_size >= 768 and <= 1024.

| Category | Details |
| --- | --- |
| **Reason** | Standard head counts provide well‑tested scaling behavior and efficient GPU utilization. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | If hidden_size >= 1024 use 16 heads; else if hidden_size >= 768 use 12 heads; otherwise use 8 heads; ensure hidden_size % attention_heads == 0. |

#### 6. Define max_sequence_length based on the training data's longest sequence and the memory budget; if unspecified, default to 512 or 1024 for larger models.

| Category | Details |
| --- | --- |
| **Reason** | Sequence length impacts memory linearly; setting a conservative default avoids OOM during training while allowing longer inputs if resources permit. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | If the training configuration (from load_configuration) includes a 'max_sequence_length', use it; otherwise compute the maximum token count across a sample of training examples; if that exceeds 512 set to 1024, else set to 512. |

#### 7. Assemble the final output dictionary with all computed fields, ensuring that total_parameters matches the estimate from bullet 2.

| Category | Details |
| --- | --- |
| **Reason** | Providing a consistent, typed output is required for downstream nodes such as initialize_model_weights. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Create a JSON object containing keys: model_type='Transformer', number_of_layers, hidden_size, attention_heads, vocab_size, max_sequence_length, total_parameters; cast all numeric values to int where appropriate. |


---

## evaluate_model

### Description
Evaluate the trained language model on the validation set, producing key metrics such as perplexity, accuracy, cross‑entropy loss, and the number of samples evaluated.

### Implementation Plan

#### 1. Retrieve the trained model checkpoint path from the parent node 'train_model' output 'model_path', and the validation dataset path from the global DAG context (split_data output 'validation_data_path').

| Category | Details |
| --- | --- |
| **Reason** | The evaluation requires direct access to the trained weights and the validation data; both paths are produced upstream. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Parse the JSON responses of 'train_model' and 'split_data', store the paths in local variables for subsequent loading. |

#### 2. Load the model checkpoint into memory using the same framework used for training (e.g., PyTorch or TensorFlow).

| Category | Details |
| --- | --- |
| **Reason** | Consistent framework usage guarantees that the model state dict matches the architecture. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use `torch.load(model_path)` or equivalent, then instantiate the model with `define_model_architecture` parameters and call `load_state_dict`. |

#### 3. Instantiate a DataLoader for the validation set with `batch_size` matching the training configuration (from 'load_configuration' output 'batch_size') and `shuffle=False`.

| Category | Details |
| --- | --- |
| **Reason** | Consistent batch sizing ensures comparable memory usage and allows deterministic evaluation. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Read the validation dataset file, apply the same tokenization and padding logic used during training, and wrap it in a `torch.utils.data.DataLoader`. |

#### 4. Set the model to evaluation mode (`model.eval()`) and disable gradient computation (`torch.no_grad()` or `tf.GradientTape(persistent=False)`), then iterate over the DataLoader to compute logits for each batch.

| Category | Details |
| --- | --- |
| **Reason** | Evaluation must be free of gradient tracking to save memory and avoid unintended weight updates. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Wrap the inference loop in a context manager that suppresses gradients. |

#### 5. For each batch, compute the cross‑entropy loss using the framework's loss function, accumulate total loss and number of samples, and compute per‑sample predictions to determine accuracy.

| Category | Details |
| --- | --- |
| **Reason** | Accurate metrics require summing loss over all samples and comparing predictions to true labels. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use `torch.nn.functional.cross_entropy(logits, labels, reduction='sum')` and `torch.argmax(logits, dim=-1)` for predictions. |

#### 6. After processing all batches, compute the average cross‑entropy loss (`total_loss / validation_samples`).

| Category | Details |
| --- | --- |
| **Reason** | Average loss provides a single scalar reflecting overall model performance. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Simple arithmetic division. |

#### 7. Compute perplexity as `exp(average_loss)` ensuring numerical stability by clipping the loss to a reasonable range before exponentiation.

| Category | Details |
| --- | --- |
| **Reason** | Perplexity is the exponentiated loss; clipping avoids overflow errors. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use `math.exp(min(max(average_loss, -50), 50))`. |

#### 8. Calculate accuracy as `(correct_predictions / validation_samples) * 100` to express it as a percentage.

| Category | Details |
| --- | --- |
| **Reason** | Accuracy gives an interpretable measure of correct predictions. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Maintain a counter of correct predictions during batch processing. |

#### 9. Return the four metrics (`perplexity`, `accuracy`, `cross_entropy_loss`, `validation_samples`) in the exact order and types specified by the output structure, serializing them as JSON.

| Category | Details |
| --- | --- |
| **Reason** | Strict adherence to the schema guarantees downstream nodes receive correctly typed data. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use a dictionary and `json.dumps` to serialize. |


---

## fine_tune_model

### Description
Fine‑tune the base language model using a task‑specific dataset to improve downstream performance. The node consumes evaluation metrics from the base model and produces a fine‑tuned checkpoint along with training statistics.

### Implementation Plan

#### 1. Validate the evaluate_model input: ensure that `perplexity`, `accuracy`, `cross_entropy_loss`, and `validation_samples` are present and of type float/int. If any are missing or NaN, abort fine‑tuning with `fine_tuning_successful = false` and log an error.

| Category | Details |
| --- | --- |
| **Reason** | Early validation prevents downstream failures due to corrupted or incomplete metrics. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Implement a simple schema check using Python type hints and `math.isnan` for floats; raise a descriptive exception if validation fails. |

#### 2. Retrieve the path to the trained model checkpoint. Prefer the environment variable `MODEL_PATH`; if unset, fall back to a hard‑coded path from the project configuration (`model_output_path`). Verify that the file exists before proceeding.

| Category | Details |
| --- | --- |
| **Reason** | Fine‑tuning requires the base weights; ensuring the checkpoint is available avoids runtime errors. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use `os.getenv` with a default, then `os.path.isfile`; if not found, emit a warning and set `fine_tuning_successful = false`. |

#### 3. Load the downstream fine‑tuning dataset from a configuration parameter (e.g., `fine_tune_dataset_path`). If the path is relative, resolve it against the project root. Use a data loader that yields batches of tokenized inputs and labels suitable for the task (e.g., classification or sequence labeling).

| Category | Details |
| --- | --- |
| **Reason** | Task‑specific data is needed for supervised fine‑tuning and may differ in format from the pretraining corpus. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Instantiate a `torch.utils.data.Dataset` subclass that reads the file, tokenizes using the same tokenizer used in pretraining, and returns tensors. Cache the dataset to avoid repeated I/O. |

#### 4. Set fine‑tuning hyperparameters: epoch count (`fine_tune_epochs`), learning rate (`fine_tune_lr`), batch size (`fine_tune_batch_size`). Use default values from the configuration if not explicitly overridden, but allow command‑line overrides via environment variables for flexibility.

| Category | Details |
| --- | --- |
| **Reason** | Hyperparameter flexibility lets the user adapt the fine‑tuning to the size of the downstream dataset. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Read from a dedicated `fine_tune_config.json` file; use `argparse`‑style precedence (env > config > defaults). |

#### 5. Initialize the model for fine‑tuning: load the base checkpoint into the same architecture, optionally replacing the final classification head with a task‑specific head if the downstream task differs from pretraining (e.g., add a `nn.Linear` for NER).

| Category | Details |
| --- | --- |
| **Reason** | Task‑specific heads enable the model to produce predictions aligned with the target labels. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use HuggingFace `AutoModelForSequenceClassification` or `AutoModelForTokenClassification` depending on task; if the head differs, call `model.resize_token_embeddings` and reinitialize the new head with Xavier uniform. |

#### 6. Define the optimizer and scheduler: use AdamW with weight decay, and a linear scheduler with warmup proportional to `fine_tune_epochs`. Tie the learning rate to the base training rate scaled by a fine‑tune factor (e.g., 0.1).

| Category | Details |
| --- | --- |
| **Reason** | AdamW with warmup stabilizes fine‑tuning and prevents catastrophic forgetting. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Instantiate `torch.optim.AdamW` with `weight_decay=0.01`; create `get_linear_schedule_with_warmup` from `transformers` library. |

#### 7. Implement the training loop: for each epoch, iterate over the fine‑tuning data loader, compute loss, perform back‑propagation, update parameters, and record training loss. After each epoch, evaluate on the validation split (derived from the same fine‑tune dataset) to compute perplexity using the same metric as the base evaluation.

| Category | Details |
| --- | --- |
| **Reason** | Capturing per‑epoch metrics enables monitoring and early stopping decisions. |
| **Impact** | HIGH |
| **Complexity** | HIGH |
| **Method** | Use `torch.no_grad()` for validation; compute perplexity as `torch.exp(torch.mean(loss))`. Store the best epoch based on lowest validation perplexity. |

#### 8. Implement early stopping: if validation perplexity does not improve for `patience` consecutive epochs (default 3), terminate training early to save compute.

| Category | Details |
| --- | --- |
| **Reason** | Prevents over‑fitting and reduces unnecessary compute time. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Maintain a counter of non‑improvement epochs; break loop when threshold exceeded. |

#### 9. After training, compute the final training loss as the average loss over the last epoch and the final validation perplexity from the best epoch. Save the fine‑tuned model checkpoint to a new path derived from the project output directory (e.g., `model_output_path/fine_tuned_checkpoint.pt`).

| Category | Details |
| --- | --- |
| **Reason** | Providing concrete metrics allows downstream nodes to assess fine‑tuning quality. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Call `model.save_pretrained()` for HuggingFace models or `torch.save` for plain state_dicts. |

#### 10. Populate the output fields: set `model_file_path` to the saved checkpoint path, `fine_tuning_successful = true`, `num_fine_tuning_epochs` to the number of epochs actually run, `final_training_loss` to the last epoch average loss, and `final_validation_perplexity` to the best validation perplexity.

| Category | Details |
| --- | --- |
| **Reason** | All required outputs must be deterministically derived from the fine‑tuning process. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Construct a dictionary mapping the output keys to the computed values and return it. |

#### 11. Log all key events (start, per‑epoch metrics, early stop, final status) to a log file located alongside the checkpoint for traceability.

| Category | Details |
| --- | --- |
| **Reason** | Logging aids debugging and audit trails for ML pipelines. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use Python's `logging` module with a file handler; format logs in JSON for downstream ingestion. |


---

## initialize_model_weights

### Description
Initialize the weights of the defined model architecture.

### Implementation Plan

#### 1. Retrieve the architecture configuration from the `define_model_architecture` output, ensuring that all required fields (model_type, number_of_layers, hidden_size, attention_heads, vocab_size, max_sequence_length, total_parameters) are present and valid.

| Category | Details |
| --- | --- |
| **Reason** | The initialization routine must be informed of the exact architecture to construct the model correctly. Missing or malformed inputs would cause construction failures or inconsistent parameter counts. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Read the JSON payload from the parent node; perform type validation and range checks (e.g., positive integers for sizes). |

#### 2. Instantiate the model using a framework‑agnostic factory (e.g., a custom `ModelBuilder` that accepts the architecture dict and returns a PyTorch `nn.Module` or TensorFlow `tf.keras.Model`).

| Category | Details |
| --- | --- |
| **Reason** | Abstracting the model construction decouples initialization from the underlying deep learning library, facilitating future swaps or extensions. |
| **Impact** | HIGH |
| **Complexity** | HIGH |
| **Method** | Implement a mapping from `model_type` to a builder class; within the builder, create transformer layers with the specified hidden size, attention heads, and positional embeddings; use the vocab size for the embedding matrix. |

#### 3. Determine the initialization strategy by inspecting a configuration flag (e.g., `use_pretrained`, `pretrained_path`) that may be passed via an optional environment variable or a separate config node; default to Xavier/Glorot uniform if no pretrained weights are provided.

| Category | Details |
| --- | --- |
| **Reason** | Choosing an appropriate strategy ensures good convergence behaviour; using pretrained weights can drastically reduce training time and improve final performance. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Parse environment variables with a fallback; if `pretrained_path` exists, load state_dict from that path; otherwise apply Xavier initialization to all linear and embedding layers. |

#### 4. Apply the chosen initialization across all trainable parameters: for each module, if it is a `Linear`, `Conv1D`, or `Embedding`, invoke the corresponding weight initialization function; for biases, zero‑initialize.

| Category | Details |
| --- | --- |
| **Reason** | Uniformly initializing all parameters avoids biasing the network and promotes symmetric learning dynamics. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Iterate over `model.modules()`; use `torch.nn.init.xavier_uniform_` for weights and `torch.nn.init.zeros_` for biases; wrap in a try/except to catch any unsupported module types. |

#### 5. Calculate the total number of trainable parameters by summing the `numel()` of every parameter with `requires_grad=True` in the model.

| Category | Details |
| --- | --- |
| **Reason** | Providing an accurate parameter count is essential for logging, debugging, and ensuring that the model matches the architecture specification. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use a generator expression: `sum(p.numel() for p in model.parameters() if p.requires_grad)`. |

#### 6. Generate a deterministic `architecture_signature` by serializing the sorted architecture dictionary into a JSON string and hashing it with SHA‑256.

| Category | Details |
| --- | --- |
| **Reason** | The signature serves as a unique fingerprint of the model configuration, useful for versioning, caching, and ensuring reproducibility. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Serialize with `json.dumps(arch_dict, sort_keys=True)`; compute hash via `hashlib.sha256()`; encode as hex string. |

#### 7. Return the output bundle with `initialization_success=True` if all steps complete without unhandled exceptions; otherwise set to `False` and provide a meaningful error message in the logs.

| Category | Details |
| --- | --- |
| **Reason** | Explicit success flag enables downstream nodes to conditionally proceed or trigger fallback workflows. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Wrap the entire initialization in a try/except; on exception, log the traceback and set success flag to False. |


---

## load_configuration

### Description
Read and validate project configuration.

### Implementation Plan

#### 1. Locate the configuration file using an environment variable set by the setup_environment node (e.g., CONFIG_PATH). Verify the file exists and is readable before proceeding.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the workflow starts with a valid source of configuration and avoids file-not-found errors later. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use pathlib.Path to check existence and read permissions; if missing, record a descriptive error. |

#### 2. Parse the configuration file as YAML or JSON into a Python dictionary, catching and reporting any syntax errors.

| Category | Details |
| --- | --- |
| **Reason** | Parsing errors can lead to silent failures; capturing them early improves debuggability. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Employ `yaml.safe_load` for YAML or `json.load` for JSON; use try/except blocks to capture `YAMLError` or `JSONDecodeError`. |

#### 3. Define a schema for required fields (max_epochs, batch_size, learning_rate, data_path, model_output_path, config_version, project_name) with their expected types and acceptable ranges.

| Category | Details |
| --- | --- |
| **Reason** | A schema centralizes validation logic and ensures consistency across runs. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Create a dictionary mapping field names to validation lambdas or use jsonschema for declarative validation. |

#### 4. Validate each required field against the schema: check presence, type, and logical constraints (e.g., epochs > 0, learning_rate > 0, paths are absolute). Collect any violations into the error_messages list.

| Category | Details |
| --- | --- |
| **Reason** | Field-level validation guarantees that downstream nodes receive well-formed data. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Iterate over schema entries; for each field, apply lambda; append descriptive messages for failures. |

#### 5. Validate filesystem paths: ensure data_path exists and is readable, and model_output_path is writable (create directory if it doesn't exist). Record path-related errors.

| Category | Details |
| --- | --- |
| **Reason** | Runtime errors during training often stem from missing or inaccessible paths; pre-empting them avoids costly failures. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use pathlib to check `is_file()` or `exists()` and `is_dir()`. Attempt to create output directory with `mkdir(parents=True, exist_ok=True)`; catch PermissionError. |

#### 6. Determine the overall configuration validity: set config_valid to True only if no error_messages were recorded; otherwise False.

| Category | Details |
| --- | --- |
| **Reason** | A clear validity flag simplifies downstream decision logic. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Set `config_valid = len(error_messages) == 0`. |

#### 7. If config_valid is true, extract validated values into the corresponding output fields; otherwise, populate numeric fields with None or default sentinel values.

| Category | Details |
| --- | --- |
| **Reason** | Consistent output structure is required for downstream nodes regardless of validation outcome. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use dictionary lookups; for missing keys in error case, assign None or 0 and document the decision in the log. |

#### 8. Return a structured JSON object containing all output fields, ensuring each matches the declared PrimitiveType and includes a clear description of any defaulted or error values.

| Category | Details |
| --- | --- |
| **Reason** | Strict type adherence guarantees compatibility with the typed workflow engine. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Serialize a dict with keys matching output_structure; validate types before returning. |


---

## prepare_training_data

### Description
Collect and preprocess the dataset for training the language model.

### Implementation Plan

#### 1. Parse the project configuration to obtain data source definitions and metadata requirements.

| Category | Details |
| --- | --- |
| **Reason** | Using the configuration ensures that the node knows where to fetch data and what constraints to apply, reducing hard‑coding and increasing reproducibility. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Load the YAML/JSON config file specified by the environment, extract `data_path` and `data_sources` fields, and validate that each entry contains a `url` or `local_path` along with optional `checksum`. |

#### 2. Download or copy all specified data sources, performing checksum verification and retry logic where necessary.

| Category | Details |
| --- | --- |
| **Reason** | Guarantees the integrity and availability of raw data, which is critical for a high‑quality training corpus. |
| **Impact** | HIGH |
| **Complexity** | HIGH |
| **Method** | Use `requests` for HTTP(S) downloads, `shutil.copyfile` for local copies, verify SHA‑256 checksums, and implement exponential back‑off for transient failures. |

#### 3. Merge data from multiple sources into a single stream, removing exact duplicate lines while preserving source order for provenance.

| Category | Details |
| --- | --- |
| **Reason** | Avoids redundancy that could bias the model, yet keeps source traceability for debugging. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Iterate through each file, yield lines to a `set` to track seen hashes, write unique lines to a temporary output file. |

#### 4. Perform comprehensive text cleaning: normalize Unicode, strip HTML tags, collapse whitespace, remove non‑ASCII characters beyond a defined threshold, and filter out empty lines.

| Category | Details |
| --- | --- |
| **Reason** | Cleaner data reduces noise in the tokenization step and improves model generalization. |
| **Impact** | HIGH |
| **Complexity** | HIGH |
| **Method** | Use `unicodedata.normalize('NFKC')`, `html5lib` for tag removal, regular expressions for whitespace collapse, and a configurable `allowed_char_set` filter. |

#### 5. Estimate the token count using a lightweight tokenizer (e.g., NLTK's `word_tokenize`) to avoid a full tokenization pass during preprocessing.

| Category | Details |
| --- | --- |
| **Reason** | Provides an early metric for dataset size without incurring the full cost of subword tokenization. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Apply `nltk.word_tokenize` to each cleaned line, count tokens, and aggregate counts. |

#### 6. Write the cleaned lines to a compressed UTF‑8 file (e.g., Gzip) to reduce disk usage and speed up downstream I/O.

| Category | Details |
| --- | --- |
| **Reason** | Compressed storage conserves space and speeds up data loading for later steps. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Open a `gzip.open` file in write mode, stream cleaned lines as UTF‑8 encoded bytes, and close the handle gracefully. |

#### 7. Populate the output structure: compute `sample_count`, `token_count`, set `is_valid` based on success flags, and expose the final file path.

| Category | Details |
| --- | --- |
| **Reason** | These metadata fields are required by downstream nodes and enable validation checks before training. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Count the number of written lines for `sample_count`, use the token counter from step 5 for `token_count`, and set `is_valid` to true if no errors were encountered. |


---

## setup_environment

### Description
Prepare the runtime environment for the workflow by ensuring that all required libraries are installed, appropriate system paths are configured, and environment variables are set for subsequent nodes.

### Implementation Plan

#### 1. Create a dedicated Python virtual environment using `venv` to isolate dependencies and prevent clashes with system packages.

| Category | Details |
| --- | --- |
| **Reason** | Virtual environments isolate the workflow’s Python packages, ensuring reproducibility across different machines and preventing version conflicts. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use `python -m venv .venv`; activate with `. .venv/bin/activate`; verify activation by checking `sys.prefix`. |

#### 2. Upgrade pip, setuptools, and wheel to the latest stable versions to guarantee compatibility with the latest package wheels.

| Category | Details |
| --- | --- |
| **Reason** | Older package managers can fail to install binary wheels, causing unnecessary compilation and longer setup times. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Run `pip install --upgrade pip setuptools wheel` and capture stdout/stderr for logging. |

#### 3. Read a predefined `requirements.txt` (or similar manifest) located in the project root to obtain the exact list of required packages and their version constraints.

| Category | Details |
| --- | --- |
| **Reason** | Explicit version specifications prevent inadvertent upgrades that could break the workflow. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Open the file, parse lines ignoring comments, and construct a list of package specifiers. |

#### 4. Install each package sequentially with pip, capturing the resolved version after installation to populate `installed_packages` and `installed_package_versions`.

| Category | Details |
| --- | --- |
| **Reason** | Sequential installation allows fine-grained error handling and precise logging of failures. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | For each specifier, execute `pip install <specifier>` via `subprocess.run`; parse `pip` output for the installed version; append to lists. |

#### 5. Verify that each package is importable by attempting to import it after installation, marking the setup as failed if any import errors arise.

| Category | Details |
| --- | --- |
| **Reason** | Installation may succeed but the package could still be broken due to missing binary dependencies or Python version incompatibilities. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use `importlib.import_module`; catch `ImportError` and record error messages. |

#### 6. Configure the `PATH` environment variable to include the `bin` directory of the virtual environment, ensuring executables from installed packages are discoverable.

| Category | Details |
| --- | --- |
| **Reason** | Certain packages expose CLI tools that must be available for later nodes (e.g., tokenizers, data preprocessors). |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Prepend `os.path.join(venv_path, 'bin')` to `os.environ['PATH']`. |

#### 7. Set `PYTHONPATH` to include any project‑specific source directories that contain modules required by the workflow.

| Category | Details |
| --- | --- |
| **Reason** | Custom modules may reside outside the standard site‑packages path; this ensures Python can locate them. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Add `os.path.abspath('src')` or similar to `PYTHONPATH` using `os.environ['PYTHONPATH']`. |

#### 8. Define essential environment variables (e.g., `CUDA_VISIBLE_DEVICES`, `OMP_NUM_THREADS`) based on configuration or system detection to control resource usage.

| Category | Details |
| --- | --- |
| **Reason** | Explicitly setting these variables improves reproducibility and avoids accidental over‑use of GPUs or CPU cores. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Detect available GPUs via `nvidia-smi` or `torch.cuda.is_available()`; set `CUDA_VISIBLE_DEVICES` accordingly. |

#### 9. Aggregate all configuration actions into a comprehensive `setup_log` string, including timestamps, installed packages and versions, environment variable settings, and any errors encountered.

| Category | Details |
| --- | --- |
| **Reason** | A detailed log aids debugging, auditability, and future environment replication. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Append each step’s outcome to a list and `'
'.join(log_entries)`. |

#### 10. Return `environment_ready=True` only if every step succeeded; otherwise set to `False` and populate `error_messages` (embedded in `setup_log`).

| Category | Details |
| --- | --- |
| **Reason** | Child nodes depend on a ready environment; propagating a clear failure flag prevents silent downstream failures. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Maintain a boolean flag `ready` that is set to `False` upon any exception; final output reflects this flag. |


---

## split_data

### Description
Split the preprocessed data into training, validation, and test sets.

### Implementation Plan

#### 1. Validate the incoming preprocessed data path and metadata.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that downstream operations have the correct input files and that the data is ready for splitting. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use os.path.exists to confirm file existence; read a small sample (e.g., 100 lines) with pandas to verify CSV/JSON structure; log any discrepancies. |

#### 2. Determine the total sample count from the metadata provided by prepare_training_data.

| Category | Details |
| --- | --- |
| **Reason** | The split ratios are applied relative to this count; accurate counting prevents off‑by‑one errors. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Read the `sample_count` field directly; if not provided, perform a streaming count of the file using a line counter for large datasets. |

#### 3. Generate a reproducible random permutation of sample indices using the configured split_seed.

| Category | Details |
| --- | --- |
| **Reason** | A fixed seed guarantees that the same splits are produced across runs, aiding debugging and reproducibility. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Instantiate numpy.random.default_rng(split_seed) and generate an array of indices with rng.permutation(sample_count). |

#### 4. Compute split boundaries based on standard ratios (e.g., 80/10/10) or user‑supplied ratios, ensuring that the sum equals 1.0 within tolerance.

| Category | Details |
| --- | --- |
| **Reason** | Flexible ratios accommodate different project requirements while preventing mis‑allocation of samples. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Validate split_ratios length is 3; round each ratio to 4 decimal places; compute cumulative sums; calculate integer boundaries using floor and adjust the last boundary to consume all samples. |

#### 5. Slice the permutation array into training, validation, and test index lists based on the computed boundaries.

| Category | Details |
| --- | --- |
| **Reason** | Direct indexing preserves the randomness introduced by the permutation and avoids bias. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use numpy array slicing: train_idx = perm[:train_boundary]; val_idx = perm[train_boundary:val_boundary]; test_idx = perm[val_boundary:] |

#### 6. Read the full preprocessed data file once and write three separate files using the derived indices.

| Category | Details |
| --- | --- |
| **Reason** | A single pass minimizes I/O overhead; writing separate files is required for subsequent training stages. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Open the source file with a buffered reader; for each line, write to the appropriate output file based on its line number; use multiprocessing or asyncio if file is >1GB to keep memory usage low. |

#### 7. Record the sizes of each split by counting written lines or using the boundary indices.

| Category | Details |
| --- | --- |
| **Reason** | Accurate split sizes are essential for reporting and for downstream model training loops. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use the lengths of the index arrays (train_idx, val_idx, test_idx) to set train_set_size, validation_set_size, test_set_size. |

#### 8. Construct filesystem paths for each split file within a dedicated `splits/` directory under the original data path.

| Category | Details |
| --- | --- |
| **Reason** | Consistent path organization simplifies downstream path discovery and versioning. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Join os.path.dirname(preprocessed_data_path) with 'splits' and generate filenames like train.tsv, val.tsv, test.tsv. |

#### 9. Persist split metadata to a JSON manifest file alongside the split datasets.

| Category | Details |
| --- | --- |
| **Reason** | A manifest provides a single source of truth for split details, aiding reproducibility and audit trails. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Create a dict with all output fields; write to 'splits/manifest.json' using json.dump with indentation for readability. |

#### 10. Validate that the sum of train, validation, and test sizes equals the original sample count, and that the split ratios match the expected values within a tolerance of ±0.01.

| Category | Details |
| --- | --- |
| **Reason** | Detects any off‑by‑one or rounding errors introduced during integer boundary calculation. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Assert sum of sizes == sample_count; compute actual_ratios = [train/total, val/total, test/total] and compare to split_ratios using numpy.isclose. |

#### 11. Return all output fields in the exact order specified by the output structure, ensuring type compliance.

| Category | Details |
| --- | --- |
| **Reason** | The downstream nodes consume these fields; type mismatches can cause silent failures. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Construct a dict with keys matching output_structure; cast values to int, float, str, or list accordingly; perform final type validation. |


---

## test_model

### Description
This node evaluates a fine‑tuned language model against a held‑out test set, calculating key performance metrics and determining whether the model meets predefined quality thresholds.

### Implementation Plan

#### 1. Extract the fine‑tuned model file path and test dataset path from the parent node fine_tune_model's output, and validate that both files exist on disk before proceeding.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that downstream evaluation has the necessary inputs and prevents runtime failures due to missing files. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use os.path.exists() to confirm both paths, raise informative error if missing. |

#### 2. Load the fine‑tuned model into memory using the same deep‑learning framework that produced it (e.g., PyTorch), set the model to evaluation mode, and attach the tokenizer that was used during training.

| Category | Details |
| --- | --- |
| **Reason** | Consistent model state and tokenization are crucial for accurate metric computation. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | torch.load(model_file_path), instantiate model class, call model.eval(), load tokenizer from stored config. |

#### 3. Read the test dataset file (JSONL, CSV, or TFRecord) and convert each example into tokenized input IDs using the loaded tokenizer.

| Category | Details |
| --- | --- |
| **Reason** | Tokenization must mirror training to preserve vocabulary alignment. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Iterate over file lines, apply tokenizer.encode_plus(...), collect input_ids and attention_masks. |

#### 4. Create a PyTorch DataLoader (or equivalent) for the test set with a batch size derived from the original configuration, shuffling disabled for deterministic evaluation.

| Category | Details |
| --- | --- |
| **Reason** | Batching improves inference throughput and memory usage. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | torch.utils.data.DataLoader(dataset, batch_size=config.batch_size, shuffle=False). |

#### 5. Run a no‑gradient inference loop: for each batch, compute logits, calculate cross‑entropy loss, derive predicted token sequences, and aggregate correct predictions to compute accuracy.

| Category | Details |
| --- | --- |
| **Reason** | Collects the raw data needed to compute both perplexity and accuracy. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | with torch.no_grad(): loss = criterion(logits.view(-1, vocab_size), targets.view(-1)), accumulate loss sum, track correct predictions by comparing argmax predictions to targets. |

#### 6. After processing all batches, compute overall metrics: accuracy as (correct / total), perplexity as exp(total_loss / total_tokens), and populate metric_names and metric_values lists in the same order.

| Category | Details |
| --- | --- |
| **Reason** | Matches the specified output schema and provides interpretable results. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | accuracy = correct / total_tokens; perplexity = math.exp(total_loss / total_tokens); metric_names = ['perplexity', 'accuracy']; metric_values = [perplexity, accuracy]. |

#### 7. Set test_dataset_size to the total number of examples in the test set (len(dataset)).

| Category | Details |
| --- | --- |
| **Reason** | Required field in output for downstream reporting. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | test_dataset_size = len(dataset). |

#### 8. Wrap the entire evaluation process in a try/except block; if any exception occurs, set evaluation_successful to False and log the error stack trace.

| Category | Details |
| --- | --- |
| **Reason** | Guarantees that the node signals failure rather than crashing the workflow. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | try: <evaluation code> except Exception as e: evaluation_successful = False; log error. |

#### 9. Determine within_expected_range by comparing each metric against pre‑defined thresholds (e.g., perplexity <= 20.0, accuracy >= 0.75). If all conditions are satisfied, set the flag to True; otherwise, False.

| Category | Details |
| --- | --- |
| **Reason** | Provides a quick pass/fail indicator for model quality. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | within_expected_range = (perplexity <= 20.0) and (accuracy >= 0.75). |


---

## tokenize_data

### Description
Tokenize the prepared training data into subwords or tokens.

### Implementation Plan

#### 1. Read the preprocessed dataset file from `preprocessed_data_path` provided by the parent node and load it into memory as a list of raw text lines.

| Category | Details |
| --- | --- |
| **Reason** | Ensuring the input is available in a consistent format is critical before any tokenization logic can be applied. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use `open(file_path, 'r', encoding='utf-8')` and `read().splitlines()` to create a list of strings. |

#### 2. Select the tokenization algorithm based on a configuration flag (`tokenization_method`) passed via environment variables or a config file (default to 'BPE' if unspecified).

| Category | Details |
| --- | --- |
| **Reason** | Providing flexibility allows the workflow to adapt to different subword strategies without code changes. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Read env variable `TOKENIZATION_METHOD` with fallback to 'bpe'. Normalize to lower case for consistency. |

#### 3. Instantiate the chosen tokenizer using the HuggingFace Tokenizers library (`tokenizers.Tokenizer` with `BPE` or `WordPiece` models). Configure essential options: case sensitivity, unknown token handling, and pre-tokenizer to split on whitespace.

| Category | Details |
| --- | --- |
| **Reason** | HuggingFace Tokenizers offers highly efficient, C++-backed implementations suitable for large corpora. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | For BPE: `Tokenizer.from_pretrained('bert-base-uncased', use_fast=True)` and adjust `tokenizer.pre_tokenizer` to `Whitespace()`. For WordPiece: use `tokenizer.from_pretrained('bert-base-uncased')` and set `tokenizer.pre_tokenizer` to `Whitespace()`. Configure `tokenizer.post_processor` to add special tokens if required. |

#### 4. Train the tokenizer on the loaded text corpus by invoking `tokenizer.train(files=...)` with a specified vocabulary size (e.g., 32,000) and optional special tokens (`[CLS]`, `[SEP]`, `[UNK]`, `[PAD]`).

| Category | Details |
| --- | --- |
| **Reason** | Training builds a subword vocabulary tailored to the dataset, improving tokenization quality and downstream model performance. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Pass `files=[preprocessed_data_path]` and set `vocab_size` and `min_frequency` parameters. Capture training logs for reproducibility. |

#### 5. Apply the trained tokenizer to every line in the corpus, converting each raw text string into a list of token IDs and then back to token strings using `tokenizer.decode`. Store these token strings in `tokenized_texts` as space‑separated tokens.

| Category | Details |
| --- | --- |
| **Reason** | Converting to token strings preserves readability for downstream processes like vocabulary extraction and allows easier debugging. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Iterate over the text list: `for line in text_list: tokens = tokenizer.encode(line).tokens; tokenized_texts.append(' '.join(tokens))`. |

#### 6. Aggregate all tokens from `tokenized_texts` into a Python set to deduplicate and extract the unique vocabulary.

| Category | Details |
| --- | --- |
| **Reason** | Using a set guarantees uniqueness efficiently, which is critical for building a correct vocabulary list. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Initialize an empty set and update it with `set.update(tokens.split())` for each entry in `tokenized_texts`. |

#### 7. Convert the set of unique tokens into a sorted list and assign it to the `vocabulary` output. Compute `vocab_size` as the length of this list.

| Category | Details |
| --- | --- |
| **Reason** | Sorting provides deterministic ordering which aids reproducibility of downstream steps (e.g., creating embeddings). |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use `vocabulary = sorted(list(unique_tokens))` and `vocab_size = len(vocabulary)`. |

#### 8. Persist the tokenizer model and vocabulary to disk for later reuse in the `create_vocabulary` node (e.g., `tokenizer.save('tokenizer.json')`).

| Category | Details |
| --- | --- |
| **Reason** | Storing the trained tokenizer ensures consistency between tokenization and vocabulary creation steps, preventing accidental drift. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Call `tokenizer.save('tokenizer.json')` after training. |

#### 9. Validate that `vocab_size` matches the length of the `vocabulary` list and that `tokenized_texts` is non-empty; log any anomalies and raise an exception if validation fails.

| Category | Details |
| --- | --- |
| **Reason** | Early validation catches data pipeline issues before they propagate to later stages like training. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Implement assertion checks and structured logging via the `logging` module. |


---

## train_model

### Description
This node performs supervised training of the language model on the split training dataset, applying gradient descent to reduce the training loss. It also records key metrics (loss, perplexity, accuracy) and saves the trained model checkpoint.

### Implementation Plan

#### 1. Validate parent inputs and set up training environment.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that training does not proceed with missing or corrupted data, preventing downstream failures. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Check that split_data.train_data_path exists and is readable; confirm initialize_model_weights.initialization_success is True. Log any failures and set training_status=False immediately. |

#### 2. Load the training data from the file system into an efficient in‑memory representation.

| Category | Details |
| --- | --- |
| **Reason** | Allows batched processing without disk I/O bottlenecks during training. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Use a lightweight parser (e.g., TensorFlow's tf.data.TextLineDataset or PyTorch's Dataset) to read the tokenized text file line by line, converting each line into a tensor of token IDs using the vocabulary built in create_vocabulary. Store the result in a PyTorch Dataset that returns `(input_ids, target_ids)` pairs. |

#### 3. Instantiate the model architecture based on the parameters provided by initialize_model_weights (or via a configuration file).

| Category | Details |
| --- | --- |
| **Reason** | Creates a clean, correctly sized model ready for training. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Retrieve model_type, number_of_layers, hidden_size, attention_heads, and vocab_size from a persisted architecture file or from environment variables set by define_model_architecture. Construct a `torch.nn.Module` subclass (e.g., a Transformer) using `nn.TransformerEncoderLayer` repeated `number_of_layers` times, with `hidden_size` and `attention_heads`. Initialize weights using the method specified in initialize_model_weights.initialization_method. |

#### 4. Prepare the optimizer and learning‑rate scheduler according to load_configuration hyperparameters.

| Category | Details |
| --- | --- |
| **Reason** | Ensures consistency between training configuration and execution. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Instantiate an AdamW optimizer with learning_rate from load_configuration. Use a `StepLR` scheduler that decays the learning rate every `config['decay_step']` epochs by factor `config['decay_gamma']`. |

#### 5. Wrap the dataset in a DataLoader with the batch_size from load_configuration, using `torch.utils.data.DataLoader`.

| Category | Details |
| --- | --- |
| **Reason** | Provides shuffling, batching, and parallel loading. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Create DataLoader(dataset, batch_size=config['batch_size'], shuffle=True, num_workers=4, pin_memory=True). |

#### 6. Implement the training loop: iterate over epochs and batches, compute loss, backpropagate, and update model weights.

| Category | Details |
| --- | --- |
| **Reason** | Core of the training process that optimizes model parameters. |
| **Impact** | HIGH |
| **Complexity** | HIGH |
| **Method** | For each epoch in range(max_epochs):
  set model.train();
  for batch in dataloader:
    inputs, targets = batch
    outputs = model(inputs)
    loss = criterion(outputs.view(-1, vocab_size), targets.view(-1))
    optimizer.zero_grad()
    loss.backward()
    optimizer.step();
  scheduler.step();
  record epoch_loss += loss.item() * batch_size. |

#### 7. Compute epoch‑level metrics: loss average, perplexity (`exp(loss)`), and accuracy.

| Category | Details |
| --- | --- |
| **Reason** | Provides diagnostic information for each epoch and final metrics for the output. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | After the inner loop, calculate `epoch_loss / total_examples`. Perplexity is `math.exp(epoch_loss / total_examples)` capped at a reasonable value to avoid overflow. Accuracy is computed by comparing `outputs.argmax(dim=-1)` with `targets` and summing correct predictions. |

#### 8. Measure and record training duration.

| Category | Details |
| --- | --- |
| **Reason** | Necessary for reporting training performance and resource budgeting. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Wrap the entire epoch loop in `time.time()` start/stop calls, compute `(stop - start) / 60` to get minutes. |

#### 9. Save the trained model checkpoint to disk.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the trained model can be reused by downstream nodes such as evaluate_model. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use `torch.save(model.state_dict(), output_path)` where output_path is constructed from load_configuration.model_output_path + '/final_model.pt'. Include metadata such as training_epochs, final_loss, etc. |

#### 10. Set the output fields according to the defined structure.

| Category | Details |
| --- | --- |
| **Reason** | Matches the expected output schema of the node. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Create a dictionary with keys final_loss, final_perplexity, training_accuracy, training_epochs, training_duration_minutes, model_path, training_status. Populate each with the computed values; set training_status=True if no exceptions were raised. |

#### 11. Implement robust exception handling and graceful failure reporting.

| Category | Details |
| --- | --- |
| **Reason** | Prevents the entire DAG from crashing on transient errors and provides clear diagnostics. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Wrap the training loop in a try/except block. On exception, log the traceback, set training_status=False, and optionally write a partial checkpoint if possible. Ensure that even in failure, the node returns a consistent output structure. |
