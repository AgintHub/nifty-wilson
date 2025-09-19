# _define_model_architecture - Complete PRD Documentation

## Overview
PRDs for nodes in the '_define_model_architecture' module.

## Table of Contents

- [determine_optimal_layers](#determine_optimal_layers)

- [calculate_optimal_hidden_size](#calculate_optimal_hidden_size)

- [determine_attention_heads](#determine_attention_heads)

- [determine_max_sequence_length](#determine_max_sequence_length)

- [compute_transformer_parameters](#compute_transformer_parameters)



---

## determine_optimal_layers

### Description
Determines the maximum number of transformer layers that can be accommodated on the specified GPUs without exceeding memory limits.

### Implementation Plan

#### 1. Compute per-layer memory requirement based on a standard transformer architecture assumption (e.g., hidden_size=768, float32 weights) and sum across all layers and GPUs to find the maximum layer count that fits within the provided memory budget.

| Category | Details |
| --- | --- |
| **Reason** | Accurate memory estimation is essential to prevent out‑of‑memory errors during training. |
| **Impact** | Ensures that the model architecture can be trained on the allocated hardware without runtime failures. |
| **Complexity** | MEDIUM |
| **Method** | Implement a Python routine that calculates memory per layer using the formula: layer_mem = (hidden_size * vocab_size * 4 + hidden_size * hidden_size * 4 * 2) bytes, multiply by number_of_layers, divide by (gpu_count * memory_gb * 1e9 / 4) to check fit; iterate from 1 up to a sensible maximum (e.g., 96) to find the largest layer count that satisfies the constraint. |

#### 2. Validate that the computed layer count is at least one and optionally cap it at a predefined maximum (e.g., 96) to avoid creating an unusable architecture.

| Category | Details |
| --- | --- |
| **Reason** | A model with zero layers is invalid and would break downstream logic. |
| **Impact** | Guarantees that the function always returns a viable configuration for the model. |
| **Complexity** | LOW |
| **Method** | After calculation, apply: if computed_layers < 1: set to 1; if computed_layers > MAX_LAYERS: set to MAX_LAYERS. |

#### 3. Return the resulting integer layer count as the function output, ensuring it is cast to int and handling any exceptional inputs gracefully.

| Category | Details |
| --- | --- |
| **Reason** | Downstream nodes expect an integer output; robust error handling prevents crashes. |
| **Impact** | Provides a clean, predictable output that integrates seamlessly with the rest of the pipeline. |
| **Complexity** | LOW |
| **Method** | Use Python's int() conversion and include try/except around parsing of inputs to default to safe values when inputs are malformed. |


---

## calculate_optimal_hidden_size

### Description
Computes the transformer hidden size that best fits GPU memory constraints and is divisible by the desired attention head count.

### Implementation Plan

#### 1. Derive a per‑GPU memory budget that subtracts a fixed overhead (e.g., 2 GB) and accounts for activation and optimizer buffers.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the hidden size calculation does not exceed available memory. |
| **Impact** | Prevents out‑of‑memory failures during training. |
| **Complexity** | LOW |
| **Method** | Implement a helper function that takes memory_gb and gpu_count, subtracts overhead, and returns available_memory_per_gpu in bytes. |

#### 2. Compute an initial hidden size estimate using a closed‑form expression based on the per‑GPU memory budget, number_of_layers, and a scaling factor for parameter and activation size.

| Category | Details |
| --- | --- |
| **Reason** | Provides a starting point that respects memory limits. |
| **Impact** | Reduces the need for iterative tuning and speeds up model configuration. |
| **Complexity** | MEDIUM |
| **Method** | Use the formula: hidden_size = floor(sqrt((available_memory_per_gpu * scaling_factor) / number_of_layers)). The scaling_factor can be empirically set (e.g., 2.5) to approximate parameter and activation memory. |

#### 3. Adjust the hidden size downwards until it is divisible by the desired attention head count (e.g., 8) and remains within the memory budget.

| Category | Details |
| --- | --- |
| **Reason** | Ensures compatibility with transformer attention mechanisms. |
| **Impact** | Guarantees efficient GPU utilization and aligns with standard architecture conventions. |
| **Complexity** | LOW |
| **Method** | Iteratively decrement hidden_size by 1 until hidden_size % attention_heads == 0 and recomputed memory usage <= available_memory_per_gpu. |


---

## determine_attention_heads

### Description
Calculates the optimal number of attention heads for a transformer based on its hidden size.

### Implementation Plan

#### 1. Parse the hidden_size string into an integer and validate it is positive.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the function operates on a numeric value and avoids runtime errors. |
| **Impact** | Prevents crashes and guarantees consistent input for head calculation. |
| **Complexity** | LOW |
| **Method** | Use int(hidden_size.strip()) and raise ValueError if conversion fails or if the value <= 0. |

#### 2. Determine the base head dimension (e.g., 64 or 128) that is most common for the target architecture and compute heads as hidden_size divided by that dimension, rounding down to the nearest integer.

| Category | Details |
| --- | --- |
| **Reason** | Aligns the head count with standard transformer configurations and ensures each head has an equal dimension. |
| **Impact** | Produces a valid head count that fits the model's computational graph and memory layout. |
| **Complexity** | LOW |
| **Method** | Set DEFAULT_HEAD_DIM = 64; heads = hidden_size // DEFAULT_HEAD_DIM; if heads == 0, fallback to 1. |

#### 3. If the chosen base dimension does not evenly divide hidden_size, provide an option to adjust the head dimension or raise an informative error for user correction.

| Category | Details |
| --- | --- |
| **Reason** | Maintains strict dimensional compatibility and informs users of necessary adjustments. |
| **Impact** | Avoids silent misconfigurations that could lead to runtime shape mismatches during training. |
| **Complexity** | MEDIUM |
| **Method** | Check hidden_size % DEFAULT_HEAD_DIM; if non-zero, either reduce DEFAULT_HEAD_DIM to the greatest divisor of hidden_size or raise an exception suggesting an alternative head dimension. |


---

## determine_max_sequence_length

### Description
Determines the maximum token sequence length for training based on the provided training configuration and GPU memory constraints.

### Implementation Plan

#### 1. Parse the JSON training configuration string safely and extract relevant hyperparameters such as batch size, hidden size, and any user‑supplied max sequence length.

| Category | Details |
| --- | --- |
| **Reason** | The shim must interpret user input and identify any explicit length constraints. |
| **Impact** | Ensures the function respects user overrides and prevents mis‑configuration. |
| **Complexity** | LOW |
| **Method** | Use Python's `json.loads` with exception handling to convert the string to a dictionary; validate required keys. |

#### 2. Compute a heuristic maximum sequence length when none is provided, scaling with available memory and typical transformer token‑embedding size.

| Category | Details |
| --- | --- |
| **Reason** | To provide a sensible default that fits within GPU memory limits while maintaining model performance. |
| **Impact** | Avoids out‑of‑memory crashes and balances compute resources with sequence modeling capability. |
| **Complexity** | MEDIUM |
| **Method** | Calculate the per‑token memory footprint (e.g., 4 bytes * hidden_size * 2 for forward/backward pass); divide remaining memory by this footprint and by a safety margin to get an estimated max length; clamp to practical bounds (e.g., 128–4096). |

#### 3. Validate the final sequence length against hard limits and raise a clear exception if the value is outside acceptable bounds.

| Category | Details |
| --- | --- |
| **Reason** | Prevents downstream components from receiving invalid configuration values. |
| **Impact** | Improves robustness and provides immediate feedback to the user. |
| **Complexity** | LOW |
| **Method** | Apply min/max checks against defined constants and raise `ValueError` with a descriptive message if violated. |


---

## compute_transformer_parameters

### Description
Computes the total number of trainable parameters for a transformer model based on vocab size, hidden size, number of layers, and attention heads.

### Implementation Plan

#### 1. Implement the exact transformer parameter count formula, including embeddings, positional encoding, attention weights, feed‑forward layers, and output projection, using integer arithmetic to avoid overflow.

| Category | Details |
| --- | --- |
| **Reason** | Accurate parameter estimation is essential for resource planning and model scaling decisions. |
| **Impact** | Provides reliable guidance for GPU allocation, memory budgeting, and training time predictions. |
| **Complexity** | MEDIUM |
| **Method** | Define a helper function that casts all inputs to ints, then compute using the standard equation:

```
params = vocab_size * hidden_size +
          number_of_layers * (
              2 * hidden_size * hidden_size +   // QKV projections
              hidden_size * hidden_size * 4 +   // FFN weights
              hidden_size * attention_heads +  // output projection
              2 * hidden_size                  // LayerNorm biases
          )
```
Use Python's built‑in integer type for arbitrary precision. |

#### 2. Validate and sanitize input strings, converting them to integers and handling invalid values gracefully.

| Category | Details |
| --- | --- |
| **Reason** | The node receives string inputs; incorrect values could crash downstream processes. |
| **Impact** | Ensures robustness, reduces runtime errors, and provides clear error messages to users. |
| **Complexity** | LOW |
| **Method** | Wrap conversions in a try/except block, returning a descriptive error object if parsing fails; otherwise proceed with the calculation. |

#### 3. Cache results for previously seen configurations to avoid recomputing identical parameter counts.

| Category | Details |
| --- | --- |
| **Reason** | In many pipelines the same model configuration is evaluated repeatedly, making caching a simple optimization. |
| **Impact** | Reduces latency and CPU usage for repeated calls, improving overall workflow performance. |
| **Complexity** | LOW |
| **Method** | Maintain an in‑memory dictionary keyed by a tuple `(vocab_size, hidden_size, number_of_layers, attention_heads)`; check the cache before performing the calculation and store new results afterwards. |
