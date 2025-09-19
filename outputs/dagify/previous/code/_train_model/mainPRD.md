# _train_model - Complete PRD Documentation

## Overview
PRDs for nodes in the '_train_model' module.

## Table of Contents

- [validate_inputs](#validate_inputs)

- [load_configuration](#load_configuration)

- [load_training_data](#load_training_data)

- [create_model_architecture](#create_model_architecture)

- [setup_optimizer](#setup_optimizer)

- [setup_lr_scheduler](#setup_lr_scheduler)

- [create_dataloader](#create_dataloader)

- [setup_loss_criterion](#setup_loss_criterion)

- [get_current_time](#get_current_time)

- [train_single_epoch](#train_single_epoch)

- [log_epoch_progress](#log_epoch_progress)

- [calculate_duration_minutes](#calculate_duration_minutes)

- [calculate_perplexity](#calculate_perplexity)

- [save_model_checkpoint](#save_model_checkpoint)

- [log_training_exception](#log_training_exception)

- [save_partial_checkpoint_if_possible](#save_partial_checkpoint_if_possible)



---

## validate_inputs

### Description
Checks that the training data file exists and that model initialization succeeded.

### Implementation Plan

#### 1. Check the existence and readability of the training data file at `train_data_path`.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that training data is available before proceeding with training. |
| **Impact** | Prevents runtime errors caused by missing or inaccessible data files. |
| **Complexity** | LOW |
| **Method** | Use `os.path.isfile()` and a temporary open/read attempt to verify file existence and read permission. |

#### 2. Validate that `initialization_success` is the string 'True' (case‑insensitive).

| Category | Details |
| --- | --- |
| **Reason** | Guarantees that model weights were properly initialized before training begins. |
| **Impact** | Avoids training on uninitialized or corrupted model parameters. |
| **Complexity** | LOW |
| **Method** | Normalize the string to lower case and compare against `'true'`. |

#### 3. Return a single boolean `output` that is True only if both checks pass.

| Category | Details |
| --- | --- |
| **Reason** | Provides a clear pass/fail signal to the calling training function. |
| **Impact** | Simplifies downstream control flow and error handling. |
| **Complexity** | LOW |
| **Method** | Combine the two boolean results with logical AND and return the result. |


---

## load_configuration

### Description
Loads and validates the training configuration from a YAML file and returns it as a dictionary.

### Implementation Plan

#### 1. Read the configuration file from the specified path, parse YAML, and validate against a pydantic model to enforce schema constraints.

| Category | Details |
| --- | --- |
| **Reason** | Ensures configuration integrity and prevents downstream failures due to malformed data. |
| **Impact** | Provides reliable configuration data, leading to predictable training behavior. |
| **Complexity** | MEDIUM |
| **Method** | Use pathlib to resolve the file path, yaml.safe_load to parse, and a pydantic BaseModel to validate the structure. |

#### 2. Cache the configuration in a module-level variable to avoid repeated disk I/O on subsequent calls.

| Category | Details |
| --- | --- |
| **Reason** | Improves performance by preventing redundant file reads. |
| **Impact** | Reduces latency for nodes that depend on configuration, especially in long-running pipelines. |
| **Complexity** | LOW |
| **Method** | Store the parsed dict in a global variable and return it on subsequent invocations. |

#### 3. Provide sensible default configuration values and fall back to them if the configuration file is missing or partially invalid.

| Category | Details |
| --- | --- |
| **Reason** | Allows the node to operate in environments where the config file is not present, such as local testing. |
| **Impact** | Enhances robustness and developer experience by avoiding hard failures. |
| **Complexity** | LOW |
| **Method** | Define a default configuration dict and merge it with parsed values using dict.update or pydantic's default handling. |


---

## load_training_data

### Description
Loads raw training data from the specified file, tokenizes it using the provided vocabulary, and returns a serialized dataset path for efficient downstream use.

### Implementation Plan

#### 1. Validate that both the training data file and vocabulary file exist and are readable before proceeding.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that downstream training does not fail due to missing or corrupted input files. |
| **Impact** | Prevents runtime errors and improves reliability of the training pipeline. |
| **Complexity** | LOW |
| **Method** | Use pathlib.Path to check existence and permission, raising informative errors if checks fail. |

#### 2. Load the raw training data, tokenize it using the vocabulary, and serialize the resulting token IDs into a temporary file (e.g., pickle or parquet) to avoid repeated expensive preprocessing.

| Category | Details |
| --- | --- |
| **Reason** | Tokenizing large datasets is computationally intensive; caching the result speeds up repeated runs and reduces memory pressure during training. |
| **Impact** | Significantly reduces startup time for training and provides a consistent input format for the DataLoader. |
| **Complexity** | MEDIUM |
| **Method** | Read the dataset with pandas or plain file streaming, map tokens via a vocabulary dict, convert to NumPy arrays, and use pickle or pyarrow to write a temporary file. |

#### 3. Return the path to the serialized dataset as the `output` field, allowing the train_model node to load it via a lightweight data loader without reprocessing the raw data.

| Category | Details |
| --- | --- |
| **Reason** | Decouples heavy preprocessing from the training loop and enables reusability across multiple training runs. |
| **Impact** | Streamlines the training pipeline and facilitates debugging by isolating data preparation. |
| **Complexity** | LOW |
| **Method** | After serialization, construct a Path object, convert to string, and return it in the output structure. |


---

## create_model_architecture

### Description
Generates a PyTorch model architecture string from an initialization method and configuration.

### Implementation Plan

#### 1. Parse the JSON `config` string into a dictionary and validate required hyperparameters.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that all necessary model parameters (e.g., layers, hidden sizes, activation functions) are present before construction. |
| **Impact** | Prevents runtime errors during model instantiation and provides clear feedback if configuration is incomplete. |
| **Complexity** | LOW |
| **Method** | Use Python's `json.loads` with a schema validator (e.g., `pydantic` or `jsonschema`) to enforce field presence and types. |

#### 2. Dynamically build the model using `torch.nn.ModuleList` or a custom `nn.Module` subclass based on the parsed configuration and apply the specified `initialization_method`.

| Category | Details |
| --- | --- |
| **Reason** | Allows flexibility to support multiple architectures (e.g., transformer, LSTM, CNN) and initialization schemes without hard‑coding each variant. |
| **Impact** | Enables plug‑in architecture changes at runtime while keeping training logic agnostic to the specific model implementation. |
| **Complexity** | MEDIUM |
| **Method** | Map configuration entries to corresponding PyTorch layers, construct them in order, and use initialization functions such as `torch.nn.init.xavier_uniform_` or custom random seed logic. |

#### 3. Return the architecture as a deterministic, human‑readable string (e.g., `repr(model)` or a custom serialization) and provide robust error handling for unsupported layers or initialization methods.

| Category | Details |
| --- | --- |
| **Reason** | Facilitates debugging and logging, and ensures callers receive a consistent output format. |
| **Impact** | Improves maintainability and traceability of model definitions across training pipelines. |
| **Complexity** | LOW |
| **Method** | Wrap the construction in a try/except block; on failure, raise a descriptive exception or return a placeholder string with error details. |


---

## setup_optimizer

### Description
Configures and returns a PyTorch optimizer for the provided model based on the supplied configuration dictionary.

### Implementation Plan

#### 1. Parse the `config` to determine the optimizer class (e.g., Adam, SGD) and extract hyperparameters such as learning rate and weight decay.

| Category | Details |
| --- | --- |
| **Reason** | The optimizer type and its hyperparameters dictate how the model learns during training. |
| **Impact** | Ensures that training uses the intended algorithm and settings, directly affecting convergence speed and final model quality. |
| **Complexity** | LOW |
| **Method** | Deserialize the `config` string to a dictionary, map the `optimizer_type` string to a torch.optim class via a predefined dictionary, and instantiate it with `lr` and `weight_decay` pulled from the config (using sensible defaults if keys are missing). |

#### 2. Validate that the supplied `model` has trainable parameters before optimizer creation.

| Category | Details |
| --- | --- |
| **Reason** | Attempting to create an optimizer for a model with no parameters would raise errors and halt training. |
| **Impact** | Adds robustness by preventing runtime exceptions during the training pipeline. |
| **Complexity** | LOW |
| **Method** | Deserialize the `model` string into a torch.nn.Module object, iterate over `model.parameters()`, and raise an informative error if the list is empty. |

#### 3. Return the initialized optimizer as a serialized string representation.

| Category | Details |
| --- | --- |
| **Reason** | The surrounding framework expects a string return value, which it will later deserialize for training. |
| **Impact** | Maintains consistency with the rest of the shim infrastructure and avoids type mismatches. |
| **Complexity** | LOW |
| **Method** | After constructing the optimizer, serialize it using a method such as `torch.save(optimizer.state_dict(), <path>)` followed by reading the file back into a string, or alternatively pickle the optimizer directly and encode it as base64. |


---

## setup_lr_scheduler

### Description
Creates and configures a learning rate scheduler for a given optimizer using settings from a configuration string.

### Implementation Plan

#### 1. Parse the config string into a dictionary and validate required fields such as scheduler_type and its parameters.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that the scheduler is constructed with correct and complete information. |
| **Impact** | Prevents runtime errors due to missing configuration and improves debugging clarity. |
| **Complexity** | MEDIUM |
| **Method** | Use json.loads or yaml.safe_load to convert the string, then check for mandatory keys and apply schema validation via pydantic or a simple dict schema. |

#### 2. Instantiate the appropriate PyTorch LR scheduler using getattr on torch.optim.lr_scheduler with the optimizer passed in.

| Category | Details |
| --- | --- |
| **Reason** | Leverages existing library implementations and keeps the shim lightweight. |
| **Impact** | Provides a ready-to-use scheduler that integrates seamlessly with the training loop. |
| **Complexity** | LOW |
| **Method** | Map scheduler_type to class name, retrieve class via getattr, and call it with optimizer and other parameters from config. |

#### 3. Return a descriptive string of the created scheduler and include error handling for unsupported scheduler types.

| Category | Details |
| --- | --- |
| **Reason** | Facilitates logging and troubleshooting by giving a human‑readable scheduler description. |
| **Impact** | Enables downstream nodes to record scheduler details without needing to inspect objects. |
| **Complexity** | LOW |
| **Method** | Wrap scheduler instantiation in try/except, and if a ValueError occurs, log and return an informative message. |


---

## create_dataloader

### Description
Creates a PyTorch DataLoader from the provided dataset using configuration parameters.

### Implementation Plan

#### 1. Parse the `config` JSON to extract DataLoader parameters such as `batch_size`, `shuffle`, `num_workers`, `pin_memory`, and `prefetch_factor`.

| Category | Details |
| --- | --- |
| **Reason** | These parameters dictate how the DataLoader batches and shuffles data, and control parallelism and GPU transfer efficiency. |
| **Impact** | Ensures the DataLoader is constructed with the exact user-specified behavior, improving reproducibility and performance. |
| **Complexity** | MEDIUM |
| **Method** | Use `json.loads` to parse the configuration string, validate required fields, and pass them as keyword arguments to `torch.utils.data.DataLoader`. |

#### 2. Load the dataset from `dataset` path using a lightweight loader that returns a PyTorch `Dataset` instance.

| Category | Details |
| --- | --- |
| **Reason** | The DataLoader requires a dataset object to iterate over. |
| **Impact** | Prevents runtime errors due to missing or malformed dataset inputs and provides a clear error message to the user. |
| **Complexity** | LOW |
| **Method** | Wrap the load logic in a try/except block, return a user-friendly error if loading fails. |

#### 3. Return the DataLoader as a string representation, for example using `repr` or a custom serialization.

| Category | Details |
| --- | --- |
| **Reason** | The node's output type is defined as `STR`, so a textual representation is required. |
| **Impact** | Allows downstream nodes to ingest the DataLoader without needing to handle complex object serialization. |
| **Complexity** | LOW |
| **Method** | After constructing the DataLoader, use `repr(dataloader)` or a JSON schema that captures essential attributes. |


---

## setup_loss_criterion

### Description
Sets up the loss criterion for training given the vocabulary size.

### Implementation Plan

#### 1. Validate that the provided vocab_size is a positive integer and convert it to an int for internal use.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that the criterion receives a valid vocabulary size, preventing runtime errors during loss calculation. |
| **Impact** | Prevents crashes and improves robustness of the training pipeline. |
| **Complexity** | LOW |
| **Method** | Use a try/except block to cast vocab_size to int and check if > 0; raise ValueError otherwise. |

#### 2. Instantiate a PyTorch CrossEntropyLoss criterion, optionally applying label smoothing if configured.

| Category | Details |
| --- | --- |
| **Reason** | Cross‑entropy is the standard loss for language modeling and supports optional label smoothing to improve generalization. |
| **Impact** | Provides a well‑tested loss function that can be swapped for alternatives in the future. |
| **Complexity** | MEDIUM |
| **Method** | Use torch.nn.CrossEntropyLoss(label_smoothing=CONFIG.get('label_smoothing', 0.0)) and store the resulting object. |

#### 3. Move the criterion to the appropriate device (CPU/GPU) based on the training configuration.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that loss computation is performed on the same device as model parameters, avoiding device mismatch errors. |
| **Impact** | Guarantees efficient training and prevents costly device transfer operations during forward passes. |
| **Complexity** | MEDIUM |
| **Method** | Retrieve device from a global config (e.g., device = torch.device(CONFIG['device'])) and call criterion.to(device). |


---

## get_current_time

### Description
Returns the current system time as a floating-point number representing seconds since the Unix epoch.

### Implementation Plan

#### 1. Implement the shim to call the standard library's `time.time()` function to retrieve a high-resolution Unix timestamp.

| Category | Details |
| --- | --- |
| **Reason** | Using the built-in time function guarantees cross-platform consistency and avoids external dependencies. |
| **Impact** | Provides a reliable, time-ordered numeric value for downstream nodes. |
| **Complexity** | LOW |
| **Method** | Import the `time` module and return `time.time()`. |

#### 2. Add a small wrapper to validate that the returned value is a float and handle any unexpected errors gracefully.

| Category | Details |
| --- | --- |
| **Reason** | Ensures robustness in case the underlying function raises an exception or returns an unexpected type. |
| **Impact** | Prevents crashes in dependent nodes by guaranteeing the correct output type. |
| **Complexity** | LOW |
| **Method** | Use a try/except block and cast to float; raise a custom exception if conversion fails. |

#### 3. Write unit tests to confirm that the shim returns a float and that the value is within a reasonable range around the current time.

| Category | Details |
| --- | --- |
| **Reason** | Automated testing provides confidence that the shim behaves correctly across environments. |
| **Impact** | Facilitates regression detection and documentation of expected behavior. |
| **Complexity** | LOW |
| **Method** | Use pytest to assert `isinstance(returned, float)` and that the value is within ±10 seconds of `time.time()` at test time. |


---

## train_single_epoch

### Description
Runs one training epoch using the provided model, dataloader, optimizer, criterion, and vocabulary size, returning epoch loss and accuracy metrics.

### Implementation Plan

#### 1. Validate input references and initialize device context before starting the epoch.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that all required components are available and on the correct computation device, preventing runtime errors. |
| **Impact** | Improves robustness and provides early failure signals for missing or incompatible inputs. |
| **Complexity** | LOW |
| **Method** | Implement a helper function that checks each input string against a registry or context dictionary, raises informative errors, and sets the device (CPU/GPU) via torch.device. |

#### 2. Perform forward pass, compute loss, execute backpropagation, and update model parameters within the epoch.

| Category | Details |
| --- | --- |
| **Reason** | Core training logic required to progress model weights and record performance. |
| **Impact** | Directly affects model convergence, training speed, and accuracy metrics returned. |
| **Complexity** | MEDIUM |
| **Method** | Use a standard PyTorch loop: `outputs = model(batch_inputs); loss = criterion(outputs, batch_labels); loss.backward(); optimizer.step(); optimizer.zero_grad();` and aggregate loss/accuracy per batch. |

#### 3. Aggregate epoch metrics into a serializable dictionary and return as a JSON string.

| Category | Details |
| --- | --- |
| **Reason** | Consistent output format enables downstream nodes to parse and use training metrics. |
| **Impact** | Facilitates automated logging, checkpointing, and potential early stopping logic. |
| **Complexity** | LOW |
| **Method** | Compute mean loss and accuracy over all batches, construct a Python dict, then serialize with `json.dumps` before assigning to the `output` field. |


---

## log_epoch_progress

### Description
Logs the progress of a training epoch, including epoch number and metrics.

### Implementation Plan

#### 1. Serialize the epoch metrics dictionary into a JSON string before logging.

| Category | Details |
| --- | --- |
| **Reason** | Ensures a consistent, machine‑readable representation that can be parsed later. |
| **Impact** | Provides reliable, structured logs that are easy to search and analyze. |
| **Complexity** | LOW |
| **Method** | Use the Python json.dumps function with sort_keys=True. |

#### 2. Implement thread‑safe logging to avoid interleaved log entries during parallel training.

| Category | Details |
| --- | --- |
| **Reason** | Multi‑threaded or multi‑process training may cause race conditions in the log output. |
| **Impact** | Maintains correct chronological order of log messages and prevents garbled logs. |
| **Complexity** | MEDIUM |
| **Method** | Leverage the built‑in logging module with a QueueHandler or use a thread‑synchronization lock around log calls. |

#### 3. Expose log level and output destination as configurable parameters.

| Category | Details |
| --- | --- |
| **Reason** | Different environments (development, CI, production) require varying verbosity and log destinations. |
| **Impact** | Allows flexible debugging and integration with external monitoring systems. |
| **Complexity** | MEDIUM |
| **Method** | Wrap the logging call in a function that reads configuration from a JSON/YAML file or environment variables, and set up appropriate handlers (StreamHandler, FileHandler). |


---

## calculate_duration_minutes

### Description
Calculates the elapsed time in minutes between two ISO 8601 timestamp strings.

### Implementation Plan

#### 1. Parse the ISO 8601 timestamp strings into timezone‑aware datetime objects using Python's `datetime.fromisoformat` or `dateutil.parser.isoparse`.

| Category | Details |
| --- | --- |
| **Reason** | Accurate time calculations require proper handling of time zones and formatting nuances. |
| **Impact** | Ensures the function works reliably across different locales and clock settings, preventing off‑by‑one minute errors. |
| **Complexity** | LOW |
| **Method** | Use `datetime.fromisoformat(start_time)` and `datetime.fromisoformat(end_time)`; fall back to `dateutil.parser.isoparse` if timezone offset is missing. |

#### 2. Compute the time difference by subtracting the start datetime from the end datetime and converting the resulting `timedelta` to minutes with `total_seconds() / 60`.

| Category | Details |
| --- | --- |
| **Reason** | Directly provides the duration in the desired unit (minutes) with floating‑point precision. |
| **Impact** | Provides a precise duration value that can be used for logging, monitoring, or metric reporting in training workflows. |
| **Complexity** | LOW |
| **Method** | Use `delta = end_dt - start_dt; minutes = delta.total_seconds() / 60.0`. |

#### 3. Validate input order and handle errors by raising a `ValueError` if the end time precedes the start time or if parsing fails.

| Category | Details |
| --- | --- |
| **Reason** | Prevent silent failures and make debugging easier when timestamps are incorrect. |
| **Impact** | Improves robustness and debuggability of the training pipeline, ensuring accurate duration metrics. |
| **Complexity** | MEDIUM |
| **Method** | Wrap parsing and subtraction in a try/except block; if `end_dt < start_dt` raise `ValueError('end_time must be after start_time')`. |


---

## calculate_perplexity

### Description
Calculates the perplexity from a given loss value.

### Implementation Plan

#### 1. Validate and convert the loss input from string to float.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the loss value is numeric and prevents runtime errors. |
| **Impact** | Prevents crashes and provides clear error handling for non-numeric inputs. |
| **Complexity** | LOW |
| **Method** | Use Python's `float()` in a try/except block, returning an error message or raising a ValueError if conversion fails. |

#### 2. Compute the perplexity using the mathematical exponential function.

| Category | Details |
| --- | --- |
| **Reason** | Perplexity is defined as exp(loss) in language modeling contexts. |
| **Impact** | Produces an accurate metric for evaluating model performance. |
| **Complexity** | LOW |
| **Method** | Import `math` and apply `math.exp(loss_float)` to obtain the perplexity. |

#### 3. Return the computed perplexity as a float output.

| Category | Details |
| --- | --- |
| **Reason** | Conforms to the expected output structure and allows downstream nodes to consume the metric. |
| **Impact** | Ensures consistent data flow and type safety in the pipeline. |
| **Complexity** | LOW |
| **Method** | Wrap the result in a dictionary with key 'output' and include the original 'loss' key for reference. |


---

## save_model_checkpoint

### Description
Saves a trained model checkpoint to disk and returns the path to the checkpoint file.

### Implementation Plan

#### 1. Implement robust model serialization using framework-specific APIs (e.g., torch.save, tf.train.Saver) and store the checkpoint in a directory defined by the configuration.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the model can be reloaded for inference or further training. |
| **Impact** | Provides persistence of training results and allows reproducibility. |
| **Complexity** | MEDIUM |
| **Method** | Use the model's native save method with a file path constructed from config['checkpoint_dir'] and a unique filename incorporating epoch and loss; handle serialization errors with try/except. |

#### 2. Validate input parameters and configuration values before saving, including checking directory existence and write permissions.

| Category | Details |
| --- | --- |
| **Reason** | Prevents runtime failures and data corruption. |
| **Impact** | Improves reliability and user feedback for misconfiguration. |
| **Complexity** | LOW |
| **Method** | Parse config string to dict, verify 'checkpoint_dir' exists or create it with os.makedirs, and confirm read/write access using os.access. |

#### 3. Log the checkpoint operation details and return the absolute file path, handling partial failures by returning an empty string or a standardized error marker.

| Category | Details |
| --- | --- |
| **Reason** | Provides auditability and clear failure signaling for downstream nodes. |
| **Impact** | Facilitates debugging and ensures that the system can detect and react to save failures. |
| **Complexity** | LOW |
| **Method** | Use the logging module to record the path and status, and wrap the save in a try/except that logs exceptions and returns '' on error. |


---

## log_training_exception

### Description
Logs a training exception by capturing its stack trace and returns a formatted string of the exception details.

### Implementation Plan

#### 1. Extract and format the exception details with stack trace.

| Category | Details |
| --- | --- |
| **Reason** | Providing a human‑readable error message is essential for debugging training failures. |
| **Impact** | Ensures developers can quickly identify the cause of failures without inspecting logs manually. |
| **Complexity** | LOW |
| **Method** | Use Python's `traceback.format_exception` to convert the exception and its traceback into a single string. |

#### 2. Log the formatted exception to the application log.

| Category | Details |
| --- | --- |
| **Reason** | Persisting error information is critical for audit trails and long‑term monitoring. |
| **Impact** | Enables automatic alerting systems to detect training crashes and facilitates root cause analysis. |
| **Complexity** | LOW |
| **Method** | Configure a logger using Python's `logging` module and write the formatted message at the ERROR level. |

#### 3. Return the formatted exception string as the shim's output.

| Category | Details |
| --- | --- |
| **Reason** | The downstream system expects a string response to indicate the error condition. |
| **Impact** | Allows calling code to log or display the error message without additional processing. |
| **Complexity** | LOW |
| **Method** | Set the `output` field of the returned dictionary to the formatted string; keep the original exception string in the `exception` field. |


---

## save_partial_checkpoint_if_possible

### Description
Attempts to save a partial model checkpoint when training fails, returning the path to the checkpoint or an empty string if saving fails.

### Implementation Plan

#### 1. Validate that the model supports serialization and is not None.

| Category | Details |
| --- | --- |
| **Reason** | Prevents runtime errors during checkpoint creation. |
| **Impact** | Ensures that only serializable models proceed to checkpointing, maintaining stability. |
| **Complexity** | LOW |
| **Method** | Check for the presence of a 'state_dict' method or use isinstance(model, torch.nn.Module); if absent, log error and return empty string. |

#### 2. Serialize the model state and optimizer state to a uniquely named file in a safe temporary directory.

| Category | Details |
| --- | --- |
| **Reason** | Preserves training progress and allows future resumption. |
| **Impact** | Provides a recoverable snapshot that can be used to continue training after an interruption. |
| **Complexity** | MEDIUM |
| **Method** | Use torch.save({"model_state": model.state_dict(), "optimizer_state": optimizer.state_dict()}, path) where path includes a timestamp and a UUID; ensure the directory exists. |

#### 3. Implement robust error handling and cleanup to avoid corrupted checkpoints.

| Category | Details |
| --- | --- |
| **Reason** | Guarantees consistency of checkpoint files even when exceptions occur. |
| **Impact** | Prevents orphaned or partially written files from misleading subsequent training attempts. |
| **Complexity** | LOW |
| **Method** | Wrap the save operation in try/except; on exception, delete any partially written file and return an empty string. |
