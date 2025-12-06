# verify_build_security PRD

## Description
Validate the security of the built binaries.


## Implementation Plan

### 1. Prepare the binary artifact path from the parent node build_openssl by reading its output field binary_artifacts_path, ensuring the path is absolute and accessible by the scanner environment.

| Category | Details |
| --- | --- |
| **Reason** | The scanner needs a concrete filesystem location to analyze; using the parent’s output guarantees consistency and avoids hard‑coding paths. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Read the JSON output of build_openssl, extract binary_artifacts_path, resolve relative paths using the working directory, and verify file existence with a filesystem check. |

### 2. Select a primary scanner tool (e.g., Snyk) and optionally a secondary tool (e.g., OPA) based on the project's security policy, then construct the corresponding CLI command with appropriate flags for binary scanning.

| Category | Details |
| --- | --- |
| **Reason** | Having a deterministic selection process ensures reproducibility and compliance with policy. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Define a configuration mapping of tool names to command templates; inject the binary path and any required authentication tokens. |

### 3. Execute the scanner command in a subprocess, capturing stdout, stderr, and the exit code, and enforce a timeout to prevent hanging scans.

| Category | Details |
| --- | --- |
| **Reason** | Subprocess execution isolates the scanner, while capturing outputs enables downstream parsing. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use Python’s subprocess.run with capture_output=True, text=True, and a timeout parameter; log the raw output for audit. |

### 4. Parse the scanner’s JSON or text report to extract the total vulnerability count and a list of vulnerability identifiers (CVE IDs or internal IDs).

| Category | Details |
| --- | --- |
| **Reason** | The raw output format varies per tool; robust parsing ensures accurate mapping to the required output fields. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | If JSON, load with json.loads; if text, use regex patterns to find CVE IDs and count entries; handle pagination or multiple sections. |

### 5. Determine the security_passed flag by evaluating the severity of each identified vulnerability; if any severity is marked Critical or High, set security_passed to False, else True.

| Category | Details |
| --- | --- |
| **Reason** | The business rule requires a binary pass/fail outcome based on criticality. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Map severity strings to a numeric ranking; iterate over the list of vulnerabilities, checking their severity field. |

### 6. Construct the final output JSON object with keys scan_tool_used, vulnerability_count, vulnerability_ids, and security_passed, ensuring type compliance (e.g., int, list of strings, bool).

| Category | Details |
| --- | --- |
| **Reason** | The downstream nodes expect a strict schema; type correctness prevents integration failures. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Populate a Python dict with the extracted values, cast to the correct types, and serialize with json.dumps. |

### 7. Validate the output against a JSON schema (matching the output_structure) and log any schema violations before returning the result.

| Category | Details |
| --- | --- |
| **Reason** | Schema validation catches accidental mismatches early, improving reliability. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use jsonschema.validate with the defined schema; capture ValidationError exceptions and include details in the log. |
