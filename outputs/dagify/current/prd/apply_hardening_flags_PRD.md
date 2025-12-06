# apply_hardening_flags PRD

## Description
Set compilation flags to enhance security.


## Implementation Plan

### 1. Parse the output of integrate_patch to locate the root directory of the OpenSSL source tree. Search the patch_log_entries list for entries containing the pattern "Applied patch to" and extract the file path prefix; use this prefix as the source root for subsequent operations.

| Category | Details |
| --- | --- |
| **Reason** | The source tree must be identified before any build configuration can be modified. Parsing patch_log_entries ensures we are working on the exact codebase that received patches. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Implement a regular‑expression parser in Python that scans each log entry for "Applied patch to" and captures the directory path. Validate the existence of the extracted path with os.path.isdir; if multiple paths are found, prioritize the one with the deepest directory depth. |

### 2. Define a canonical list of hardening flags to be applied. Include -DOPENSSL_NO_ASM, -DOPENSSL_NO_EC, -fstack-protector-strong, -Wextra, -Werror, -fPIE, -pie, and -D_FORTIFY_SOURCE=2. Store this list in a variable named hardening_flags.

| Category | Details |
| --- | --- |
| **Reason** | A consistent set of flags guarantees reproducible security postures across builds and simplifies downstream verification. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Hard‑code the list as a Python list of strings. Ensure each flag is correctly escaped for shell execution. |

### 3. Export the hardening flags as environment variables CFLAGS and CXXFLAGS before invoking the OpenSSL configuration script. Concatenate the flags into a single string separated by spaces, then set os.environ['CFLAGS'] = os.environ['CXXFLAGS'] = ' '.join(hardening_flags).

| Category | Details |
| --- | --- |
| **Reason** | OpenSSL's ./config script inherits compiler flags from the environment, allowing us to inject hardening options without modifying the script itself. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use Python's os.environ to set the variables. Verify that the values are correctly set by printing os.environ['CFLAGS'] after assignment. |

### 4. Run the OpenSSL configuration command (./config --prefix=/opt/openssl --openssldir=/opt/openssl) within the source root directory, capturing its stdout and stderr. Ensure the command completes successfully before proceeding.

| Category | Details |
| --- | --- |
| **Reason** | The configuration step generates Makefiles that incorporate the environment‑supplied flags. Failure to configure indicates a problem with the flag syntax or environment setup. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Execute the command using subprocess.run with capture_output=True, check=True. If a CalledProcessError is raised, log the error and set success to False. |

### 5. Validate that the flags are present in the generated Makefile or config.h by grepping for each flag string. If any flag is missing, log a warning and set success to False.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that the build system actually received the hardening options; missing flags could undermine security objectives. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Read the Makefile (e.g., Makefile) and config.h into memory. For each flag in hardening_flags, use the in operator to check presence. Record any missing flags in a list. |

### 6. Populate the output fields: flags_applied = hardening_flags, flags_summary = a concatenated sentence describing the applied flags, and success = True if all validation steps passed, otherwise False.

| Category | Details |
| --- | --- |
| **Reason** | These outputs feed downstream nodes (build_openssl) and provide a clear audit trail for the hardening process. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Construct flags_summary as "Applied hardening flags: {}".format(', '.join(hardening_flags)). Return the three fields as a JSON object. |
