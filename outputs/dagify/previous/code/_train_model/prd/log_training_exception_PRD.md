# log_training_exception PRD

## Description
Logs a training exception by capturing its stack trace and returns a formatted string of the exception details.


## Implementation Plan

### 1. Extract and format the exception details with stack trace.

| Category | Details |
| --- | --- |
| **Reason** | Providing a human‑readable error message is essential for debugging training failures. |
| **Impact** | Ensures developers can quickly identify the cause of failures without inspecting logs manually. |
| **Complexity** | LOW |
| **Method** | Use Python's `traceback.format_exception` to convert the exception and its traceback into a single string. |

### 2. Log the formatted exception to the application log.

| Category | Details |
| --- | --- |
| **Reason** | Persisting error information is critical for audit trails and long‑term monitoring. |
| **Impact** | Enables automatic alerting systems to detect training crashes and facilitates root cause analysis. |
| **Complexity** | LOW |
| **Method** | Configure a logger using Python's `logging` module and write the formatted message at the ERROR level. |

### 3. Return the formatted exception string as the shim's output.

| Category | Details |
| --- | --- |
| **Reason** | The downstream system expects a string response to indicate the error condition. |
| **Impact** | Allows calling code to log or display the error message without additional processing. |
| **Complexity** | LOW |
| **Method** | Set the `output` field of the returned dictionary to the formatted string; keep the original exception string in the `exception` field. |
