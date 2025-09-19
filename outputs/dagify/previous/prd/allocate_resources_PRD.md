# allocate_resources PRD

## Description
Reserve the necessary hardware resources.


## Implementation Plan

### 1. Extract GPU requirement parameters from the configuration returned by load_configuration, using keys such as requested_gpu_count, requested_gpu_type, and memory_per_gpu. If any key is missing, fall back to sensible defaults (e.g., 1 V100, 16 GB).

| Category | Details |
| --- | --- |
| **Reason** | Explicitly capturing the user’s GPU preferences ensures deterministic allocation and avoids hard‑coded assumptions. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Parse the load_configuration output dictionary; use dict.get with default values; perform type validation and conversion to int/float. |

### 2. Validate that the requested number of GPUs is available on the target compute node or cluster by querying the system’s GPU inventory (e.g., `nvidia-smi --list-gpus` for local nodes, or the cluster scheduler API for cloud environments).

| Category | Details |
| --- | --- |
| **Reason** | Pre‑emptively detecting insufficiencies prevents runtime failures and resource contention. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Execute the appropriate inventory command via subprocess, or call the scheduler’s REST endpoint; parse the output to count free GPUs of the requested type; handle exceptions and timeouts. |

### 3. If the inventory check passes, request allocation of the specified GPUs using the platform’s resource allocation interface (e.g., Slurm `srun --gres=gpu:count`, Kubernetes GPU requests in Pod spec, or a direct CUDA context allocation for local runs).

| Category | Details |
| --- | --- |
| **Reason** | Actual resource reservation is required before model initialization to avoid oversubscription and to lock the GPUs for the training job. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | For cloud environments, construct the job submission JSON and POST to the cluster’s API; for local nodes, invoke CUDA driver calls (cuDeviceGetCount, cuCtxCreate) to lock GPUs; verify allocation status via API responses or CUDA error codes. |

### 4. Compute the total memory to be reported as `memory_gb` by multiplying the allocated GPU count by the per‑GPU memory (converted to gigabytes).

| Category | Details |
| --- | --- |
| **Reason** | Providing an aggregate memory figure simplifies downstream budgeting and monitoring. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use a simple arithmetic operation: memory_gb = gpu_count * memory_per_gpu; ensure result is float and round to two decimal places. |

### 5. Populate the output structure: set `gpu_count`, `gpu_type`, `memory_gb`, and determine `allocation_success` based on the success flags returned by the allocation API and any exceptions caught during the process.

| Category | Details |
| --- | --- |
| **Reason** | Accurately conveying allocation status is critical for error propagation to downstream nodes. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Create a dict with the four fields; if any step fails, set allocation_success to false and assign zeroes or empty strings for other fields; otherwise set true and the actual values. |

### 6. Log the allocation attempt with details such as timestamp, requested parameters, actual allocated GPUs, and any error messages, storing the log in a temporary file or returning it in a hidden side channel for auditing purposes.

| Category | Details |
| --- | --- |
| **Reason** | Traceability aids debugging and compliance with resource usage policies. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Format a JSON or plain‑text log entry; write to a file in /tmp or append to an in‑memory list; expose via an optional `allocation_log` output if the node interface allows. |
