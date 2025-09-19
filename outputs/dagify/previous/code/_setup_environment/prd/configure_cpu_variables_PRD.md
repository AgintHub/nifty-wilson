# configure_cpu_variables PRD

## Description
Sets CPU‑related environment variables such as OMP_NUM_THREADS, MKL_NUM_THREADS, and NUMEXPR_NUM_THREADS based on the system’s CPU count and returns them as a JSON string.


## Implementation Plan

### 1. Determine the number of logical CPU cores and set OMP_NUM_THREADS, MKL_NUM_THREADS, and NUMEXPR_NUM_THREADS accordingly.

| Category | Details |
| --- | --- |
| **Reason** | These variables control the thread parallelism for many numerical libraries and can dramatically affect performance. |
| **Impact** | Ensures that CPU‑intensive workloads use an optimal number of threads, improving throughput and avoiding oversubscription. |
| **Complexity** | LOW |
| **Method** | Use `multiprocessing.cpu_count()` to fetch the core count and assign it to the three variables via `os.environ`. |

### 2. Respect existing environment variable overrides by checking for pre‑set values before modifying them.

| Category | Details |
| --- | --- |
| **Reason** | Users or upstream configurations may intentionally set specific thread counts for compatibility or testing. |
| **Impact** | Preserves user intent while still providing sensible defaults when variables are unset. |
| **Complexity** | LOW |
| **Method** | Query `os.getenv()` for each variable and only set it if the result is None. |

### 3. Return the configured variables as a JSON string for downstream nodes.

| Category | Details |
| --- | --- |
| **Reason** | The consuming workflow expects a string representation of the configuration dictionary. |
| **Impact** | Provides a consistent, machine‑readable output that can be easily parsed by subsequent nodes. |
| **Complexity** | LOW |
| **Method** | Collect the variables into a Python dict and use `json.dumps()` to serialize it. |
