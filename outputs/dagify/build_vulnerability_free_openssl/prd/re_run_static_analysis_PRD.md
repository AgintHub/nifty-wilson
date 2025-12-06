# re_run_static_analysis PRD

## Description
Re-run static analysis on the built OpenSSL binaries, capturing warnings, errors, and security findings, and produce a detailed report.


## Implementation Plan

### 1. Validate that the static analysis environment is fully prepared by checking the `environment_ready` flag from the `setup_static_analysis_environment` node. If the flag is false, abort the run and log an error indicating missing tools or misconfiguration.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that clang-tidy and cppcheck are installed and configured correctly before execution, preventing false negatives and wasted compute. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Read the `environment_ready` boolean from the parent node’s output; if false, raise an exception and terminate the task. |

### 2. Retrieve the path to the compiled OpenSSL binaries from the `build_openssl` node’s `binary_artifacts_path` output. Verify that the directory exists and contains at least one executable or shared library.

| Category | Details |
| --- | --- |
| **Reason** | Static analysis tools operate on compiled artifacts; locating them correctly is essential for accurate analysis. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use filesystem API to confirm existence of `binary_artifacts_path`; list files and filter for `.so`, `.dll`, `.exe`, or ELF binaries. |

### 3. Run clang-tidy on each binary artifact by invoking `clang-tidy -p <compile_commands.json> <binary>` and capture its stdout and stderr. Store the raw output in a temporary file for later parsing.

| Category | Details |
| --- | --- |
| **Reason** | clang-tidy provides fine‑grained linting and security checks; its output includes warnings, errors, and potential vulnerabilities. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Generate or locate `compile_commands.json` in the build directory; loop over binaries, execute clang-tidy via subprocess, redirect output to `clang_tidy.log`. |

### 4. Run cppcheck on the same set of binaries using `cppcheck --enable=all --xml <binary> 2> cppcheck.xml`. Parse the XML to extract warnings, errors, and security issues (e.g., `CWE` tags).

| Category | Details |
| --- | --- |
| **Reason** | cppcheck complements clang-tidy by detecting a broader range of C/C++ issues, including memory leaks and buffer overflows. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Execute cppcheck via subprocess, redirect XML output to `cppcheck.xml`; use an XML parser to count `<error>` and `<warning>` elements and extract CWE identifiers. |

### 5. Aggregate the results from clang-tidy and cppcheck: sum the warning counts, sum the error counts, and merge the security finding lists while eliminating duplicates.

| Category | Details |
| --- | --- |
| **Reason** | Combining outputs from both tools yields a comprehensive view of static analysis results. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Read the temporary log files, use regular expressions to count occurrences, and append findings to a set to deduplicate. |

### 6. Determine `analysis_passed` by evaluating whether `errors_count` is zero and `security_findings` is empty. If either condition fails, set `analysis_passed` to false; otherwise true.

| Category | Details |
| --- | --- |
| **Reason** | Provides a clear pass/fail indicator for downstream processes such as the security report generation. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Simple boolean logic: `analysis_passed = (errors_count == 0) and (len(security_findings) == 0)`. |

### 7. Generate a structured static analysis report file in JSON format at a predefined location (e.g., `reports/static_analysis_report.json`). Include all output fields (`warnings_count`, `errors_count`, `security_findings`, `analysis_passed`, `report_path`).

| Category | Details |
| --- | --- |
| **Reason** | Persisting the report enables traceability, auditability, and consumption by downstream nodes such as `generate_security_report`. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Create a dictionary with the output fields, serialize to JSON, and write to disk; set `report_path` to the file’s absolute path. |

### 8. Return the populated output fields (`warnings_count`, `errors_count`, `security_findings`, `analysis_passed`, `report_path`) as the node’s result, ensuring they match the defined output structure types.

| Category | Details |
| --- | --- |
| **Reason** | Conforms to the DAG’s contract, allowing dependent nodes to consume the data without type mismatches. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Construct a response object with the exact keys and types, and emit it via the workflow engine’s API. |
