# log_backtest_error PRD

## Description
Logs a backtest exception and returns a string representation of the error.


## Implementation Plan

### 1. Capture the exception and convert it into a detailed, human‑readable string using the traceback module.

| Category | Details |
| --- | --- |
| **Reason** | Backtest failures need a full stack trace to diagnose the root cause. |
| **Impact** | Provides developers with precise diagnostic information, reducing time to fix bugs. |
| **Complexity** | LOW |
| **Method** | Import `traceback` and call `traceback.format_exception` on the exception object to produce a multi‑line string. |

### 2. Persist the formatted error message to a centralized logging system (e.g., Python `logging` with a file or cloud handler).

| Category | Details |
| --- | --- |
| **Reason** | Transient console output is lost after execution; persistent logs are required for audit and post‑mortem analysis. |
| **Impact** | Creates an audit trail of backtest failures, enabling trend analysis and compliance reporting. |
| **Complexity** | MEDIUM |
| **Method** | Configure a `logging.Logger` with a rotating file handler or integrate with existing logging infrastructure, then log the error at `ERROR` level. |

### 3. Return the formatted error string as the shim's output while ensuring no sensitive internal details are leaked.

| Category | Details |
| --- | --- |
| **Reason** | Downstream nodes expect a string output; sanitizing prevents accidental exposure of confidential data. |
| **Impact** | Allows the calling backtest node to handle the failure gracefully and report a clean status to users. |
| **Complexity** | LOW |
| **Method** | Optionally truncate or mask sensitive paths in the traceback, then return the final string from the function. |
