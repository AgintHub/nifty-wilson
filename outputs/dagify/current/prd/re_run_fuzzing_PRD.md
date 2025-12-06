# re_run_fuzzing PRD

## Description
Re-run fuzz testing on the built OpenSSL binaries using the previously configured fuzzing environment. The run should match the duration of the initial fuzzing session and capture all crash information.


## Implementation Plan

### 1. Collect the binary artifacts path from build_openssl and the list of seed files and configured frameworks from setup_fuzzing_environment. Verify that environment_ready is true before proceeding.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that the fuzzing run uses the correct binaries and seed inputs, preventing false negatives or crashes due to missing data. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Read binary_artifacts_path, seed_files, and frameworks_configured from the parent node outputs. Perform a simple boolean check on environment_ready. |

### 2. Determine the fuzzing duration by reading the previous fuzzing_duration_seconds from the most recent fuzzing run metadata (stored in a shared state or configuration file). If unavailable, default to a pre‑defined safe duration (e.g., 2 hours).

| Category | Details |
| --- | --- |
| **Reason** | Maintains consistency with the original fuzzing session, enabling accurate comparison of results and impact analysis. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Query the shared state store (e.g., Redis, file system) for a key named "previous_fuzzing_duration_seconds". If the key does not exist, set duration_seconds = 7200. |

### 3. Execute the chosen fuzzing framework (e.g., AFL or libFuzzer) against each binary artifact using the collected seed files and the determined duration. Capture the complete stdout/stderr streams to a log file.

| Category | Details |
| --- | --- |
| **Reason** | Runs the fuzzing process in a controlled manner, ensuring that all inputs are processed and that logs are available for downstream analysis. |
| **Impact** | HIGH |
| **Complexity** | HIGH |
| **Method** | For each framework in frameworks_configured, construct the command line:
- AFL: "afl-fuzz -i <seed_dir> -o <output_dir> -t <duration_ms> -- <binary_path>"
- libFuzzer: "<binary_path> -fuzz_time=<duration_seconds> -runs=<seed_count>"
Use subprocess.run with capture_output=True, timeout=duration_seconds+300. Write the combined stdout/stderr to fuzzing_log. |

### 4. Parse the fuzzing_log to extract crash identifiers (e.g., hash of input causing crash) and the corresponding input file paths. Count unique crashes to populate crash_count and collect crash_examples.

| Category | Details |
| --- | --- |
| **Reason** | Transforms raw log data into structured output that can be consumed by the security report and other downstream nodes. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use regular expressions to locate lines matching "Crash detected" and extract the input file name. Store each unique input path in a set for crash_examples. crash_count = len(set). |

### 5. Set fuzzing_success to true if the fuzzing process exited with status 0 and no critical errors (e.g., segmentation faults of the fuzzing tool) were reported. Otherwise, set it to false.

| Category | Details |
| --- | --- |
| **Reason** | Provides a quick indicator of whether the fuzzing run was successful, enabling automated gating for the security report. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Check subprocess.returncode and scan fuzzing_log for keywords such as "Fatal error" or "Segmentation fault". Set fuzzing_success accordingly. |

### 6. Compute fuzzing_duration_seconds as the elapsed wall‑clock time between the start and end timestamps of the fuzzing process, rounded to the nearest second.

| Category | Details |
| --- | --- |
| **Reason** | Provides an objective measure of the runtime, which is required for the output structure and for comparing against the original run. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Record time.time() before and after subprocess execution; duration_seconds = int(end - start). |
