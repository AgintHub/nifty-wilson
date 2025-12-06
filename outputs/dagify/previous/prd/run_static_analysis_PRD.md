# run_static_analysis PRD

## Description
Perform static analysis on the OpenSSL source code.


## Implementation Plan

### 1. Validate that the OpenSSL source tree is present at the path provided by collect_current_openssl_source (clone_path) and that the analysis environment is ready (environment_ready) before proceeding.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that the analysis tools have a valid source repository and a correctly configured environment, preventing runtime errors. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Read clone_path from parent output; read environment_ready from setup_static_analysis_environment; if false, abort with error log. |

### 2. Run clang-tidy on the entire source tree with the default OpenSSL coding standards configuration, capturing its stdout and stderr streams to temporary files.

| Category | Details |
| --- | --- |
| **Reason** | clang-tidy provides detailed linting and potential security checks; capturing streams allows later parsing. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Execute `clang-tidy -p build -j$(nproc) $(find . -name '*.c' -or -name '*.cpp')`; redirect output to clang_tidy.log. |

### 3. Run cppcheck on the same source tree using the `--enable=all` flag and `--xml` output mode, directing the XML result to a separate file.

| Category | Details |
| --- | --- |
| **Reason** | cppcheck complements clang-tidy by detecting a broader range of bugs and potential security issues. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Execute `cppcheck --enable=all --xml --xml-version=2 . 2> cppcheck.xml`. |

### 4. Parse clang_tidy.log to extract warnings and errors, normalizing each entry into the format "file:line:column: severity: message" and populate warnings_list and errors_list accordingly.

| Category | Details |
| --- | --- |
| **Reason** | Standardized format simplifies downstream aggregation and reporting. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Use a regex pattern to match lines; filter by severity (warning/error); append to respective lists. |

### 5. Parse cppcheck.xml to extract warnings, errors, and security findings, converting each XML element into a human‑readable string and adding them to warnings_list, errors_list, and security_issues_list.

| Category | Details |
| --- | --- |
| **Reason** | cppcheck’s XML output provides structured data that can be accurately mapped to the required lists. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Use an XML parser (e.g., lxml) to iterate over <error> elements; extract attributes (file, line, severity) and message; classify based on severity. |

### 6. Count the total number of warnings, errors, and security issues across both tools and store the results in total_warnings, total_errors, and total_security_issues.

| Category | Details |
| --- | --- |
| **Reason** | Aggregated counts provide quick metrics for the security report. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use len(warnings_list), len(errors_list), len(security_issues_list). |

### 7. Determine analysis_success by checking that both clang-tidy and cppcheck exit with code 0 and that no unexpected fatal errors were encountered during parsing.

| Category | Details |
| --- | --- |
| **Reason** | A boolean success flag simplifies downstream decision‑making in generate_security_report. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Capture exit codes; if both are 0 and parsing succeeded, set analysis_success = true. |

### 8. Generate a comprehensive static analysis report file (e.g., analysis_report.md) that includes sections for warnings, errors, security findings, and overall summary, and write its path to analysis_report_path.

| Category | Details |
| --- | --- |
| **Reason** | A human‑readable report aids developers in triaging issues. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Create markdown content with tables; write to file; store absolute path. |

### 9. Return all output fields as defined in the output_structure, ensuring that each list is sorted alphabetically by file name for consistency.

| Category | Details |
| --- | --- |
| **Reason** | Consistent ordering makes downstream consumption deterministic. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Sort warnings_list, errors_list, security_issues_list before returning. |
