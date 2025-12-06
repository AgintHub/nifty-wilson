# re_run_dynamic_tests PRD

## Description
Re-run dynamic tests on the built binaries.


## Implementation Plan

### 1. Validate that the dynamic testing environment was successfully set up by checking the `environment_setup_success` flag from `setup_dynamic_testing_environment` output. If false, abort and log the error.

| Category | Details |
| --- | --- |
| **Reason** | Ensures prerequisite environment is ready before test execution, preventing false negatives. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Read the boolean flag from the parent node's JSON output; if false, raise an exception and exit. |

### 2. Locate the compiled test binaries using the `test_binary_path` field from `setup_dynamic_testing_environment`. Verify the path exists and is executable.

| Category | Details |
| --- | --- |
| **Reason** | Dynamic tests must be run against the correct binaries; path validation avoids runtime errors. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use filesystem checks (`os.path.isfile` and `os.access` with execute permission) in the execution script. |

### 3. Determine the test suite name by inspecting the test binary name or by reading a configuration file (e.g., `config_file_path`). Store this as `test_suite_name`.

| Category | Details |
| --- | --- |
| **Reason** | Provides a clear identifier for the output record, facilitating traceability. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Parse the binary filename or read a known config key; assign to the output field. |

### 4. Execute the test suite using the appropriate command (e.g., `./test` or `make test`) with a timeout that covers the expected runtime. Capture stdout and stderr streams.

| Category | Details |
| --- | --- |
| **Reason** | Runs the actual dynamic tests and collects raw results for parsing. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Spawn a subprocess with `subprocess.run`, redirecting output to pipes; enforce timeout via `timeout` parameter. |

### 5. Parse the captured logs to count total, passed, and failed tests. Use regular expressions or a test framework parser (e.g., `pytest` XML report) to extract counts.

| Category | Details |
| --- | --- |
| **Reason** | Accurate aggregation of test results is essential for downstream reporting. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Apply regex patterns to match lines like "TOTAL: X", "PASSED: Y", "FAILED: Z"; fallback to XML parsing if available. |

### 6. Extract detailed failure information (error messages, stack traces, test identifiers) and store them in the `failure_details` list. Limit the size to avoid excessive payloads.

| Category | Details |
| --- | --- |
| **Reason** | Provides actionable data for debugging and for inclusion in the security report. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Iterate over failed test entries, capture relevant log snippets, and append to a list. |

### 7. Measure the total duration of the test run by recording the start and end timestamps. Convert to seconds with floating‑point precision and store in `test_duration_seconds`.

| Category | Details |
| --- | --- |
| **Reason** | Duration metrics help assess performance regressions and test suite size. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use `time.monotonic()` before and after execution; compute difference. |

### 8. Set the `tests_passed_successfully` flag to true only if `failed_tests` equals zero; otherwise set to false.

| Category | Details |
| --- | --- |
| **Reason** | Provides a quick boolean indicator for downstream nodes that may skip further steps if tests fail. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Simple conditional check after parsing counts. |

### 9. Assemble all extracted data into a JSON object matching the defined output structure and emit it as the node's result.

| Category | Details |
| --- | --- |
| **Reason** | Ensures downstream nodes receive data in the expected format for further processing. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Create a dictionary with keys matching the output fields and serialize with `json.dumps`. |

### 10. Implement robust error handling: if any step fails (e.g., binary not found, test execution error), capture the exception message, log it, and return a partial result with `tests_passed_successfully` set to false.

| Category | Details |
| --- | --- |
| **Reason** | Prevents the entire workflow from crashing due to a single failure and provides diagnostic information. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Wrap execution logic in try/except blocks; use structured logging. |
