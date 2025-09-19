# calculate_optimal_hidden_size PRD

## Description
Computes the transformer hidden size that best fits GPU memory constraints and is divisible by the desired attention head count.


## Implementation Plan

### 1. Derive a per‑GPU memory budget that subtracts a fixed overhead (e.g., 2 GB) and accounts for activation and optimizer buffers.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the hidden size calculation does not exceed available memory. |
| **Impact** | Prevents out‑of‑memory failures during training. |
| **Complexity** | LOW |
| **Method** | Implement a helper function that takes memory_gb and gpu_count, subtracts overhead, and returns available_memory_per_gpu in bytes. |

### 2. Compute an initial hidden size estimate using a closed‑form expression based on the per‑GPU memory budget, number_of_layers, and a scaling factor for parameter and activation size.

| Category | Details |
| --- | --- |
| **Reason** | Provides a starting point that respects memory limits. |
| **Impact** | Reduces the need for iterative tuning and speeds up model configuration. |
| **Complexity** | MEDIUM |
| **Method** | Use the formula: hidden_size = floor(sqrt((available_memory_per_gpu * scaling_factor) / number_of_layers)). The scaling_factor can be empirically set (e.g., 2.5) to approximate parameter and activation memory. |

### 3. Adjust the hidden size downwards until it is divisible by the desired attention head count (e.g., 8) and remains within the memory budget.

| Category | Details |
| --- | --- |
| **Reason** | Ensures compatibility with transformer attention mechanisms. |
| **Impact** | Guarantees efficient GPU utilization and aligns with standard architecture conventions. |
| **Complexity** | LOW |
| **Method** | Iteratively decrement hidden_size by 1 until hidden_size % attention_heads == 0 and recomputed memory usage <= available_memory_per_gpu. |
