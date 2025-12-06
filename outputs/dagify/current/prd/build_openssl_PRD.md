# build_openssl PRD

## Description
Build the OpenSSL binaries from the source code that has been patched for known vulnerabilities and configured with security hardening flags. The build should generate the standard OpenSSL libraries and binaries, capture detailed logs, and record build metrics.


## Implementation Plan

### 1. 1. Retrieve the hardened configuration flags from the parent node's output (flags_applied) and merge them into the OpenSSL build command line using the `./config` script with `--enable-optimizations` and `--with-ssl-module` options. Ensure that each flag is prefixed with `-D` or `-f` as appropriate, and that the command line is constructed in a portable shell script that expands environment variables for the build host.

| Category | Details |
| --- | --- |
| **Reason** | Integrating the exact hardening flags ensures reproducibility and that the compiled binaries reflect the security posture defined by the parent node. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Parse the flags_applied list, iterate over each entry, concatenate them into a single string, and invoke `./config $FLAGS` followed by `make` and `make install`. Capture stdout/stderr to a log file. |

### 2. 2. Set up a clean build environment by creating a temporary directory (e.g., `/tmp/openssl_build_${TIMESTAMP}`) and copying the patched source code into it. This isolates the build from any pre‑existing artifacts and prevents side effects on the source tree.

| Category | Details |
| --- | --- |
| **Reason** | A clean environment eliminates hidden dependencies and ensures that the build results are deterministic. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use `mkdir -p` to create the directory, then `rsync -a` or `cp -r` to copy the source. Record the path in `build_artifacts_path`. |

### 3. 3. Execute the build process using `make -j$(nproc)` to parallelize compilation across all CPU cores. Redirect both stdout and stderr to a log file (`build.log`) and capture the start and end timestamps to compute `build_duration_seconds`.

| Category | Details |
| --- | --- |
| **Reason** | Parallel compilation maximizes performance while the log file provides a source of truth for debugging and audit. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Record `start_time=$(date +%s)` before invoking `make`, then `end_time=$(date +%s)` after completion. Compute duration as `build_duration_seconds=$((end_time - start_time))`. |

### 4. 4. After a successful `make install`, collect the names of the generated binary artifacts by listing the contents of the install prefix (`/usr/local/ssl/lib` or the configured prefix). Populate the `artifact_names` list with base filenames (e.g., `libssl.so.1.1`, `libcrypto.so.1.1`).

| Category | Details |
| --- | --- |
| **Reason** | Explicitly enumerating artifacts enables downstream nodes to reference them without hard‑coding paths. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use `ls -1 $PREFIX/lib` and filter for files matching `libssl.*` and `libcrypto.*`. Strip any version suffixes if required by downstream consumers. |

### 5. 5. Determine `build_success` by checking the exit status of the `make` command and verifying that no critical errors appear in the log (e.g., lines containing `error:` or `fatal:`). If any such errors are present, set `build_success` to `false` and include the relevant log excerpts in `build_log`.

| Category | Details |
| --- | --- |
| **Reason** | Accurate success flag is essential for conditional execution of downstream nodes (e.g., re‑run tests). |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Capture `$?` from the last command; parse `build.log` with `grep -i 'error\|fatal'`. If matches found, set `build_success=false`. |

### 6. 6. Write a concise summary of the build outcome to a metadata file (`build_metadata.json`) containing all output fields. This file will be consumed by downstream nodes to avoid re‑parsing logs.

| Category | Details |
| --- | --- |
| **Reason** | Centralizing output in a structured format simplifies data ingestion for subsequent processes. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use `jq` or a Python script to serialize the fields into JSON and write to `build_metadata.json`. |
