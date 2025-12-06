# release_artifacts PRD

## Description
Prepare and publish the final OpenSSL release by bundling binaries, source, and documentation, then creating a version control tag.


## Implementation Plan

### 1. Retrieve the path to the compiled OpenSSL binaries from the build_openssl output (stored in the environment or a known artifact directory) and verify its existence.

| Category | Details |
| --- | --- |
| **Reason** | The binaries are the core deliverable; ensuring they are present prevents downstream packaging failures. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use a file system check (e.g., os.path.isdir) and read the binary_artifacts_path from the build_openssl artifact store. |

### 2. Obtain the source tarball path from the collect_current_openssl_source output (clone_path + "openssl-" + stable_release_tag + ".tar.gz") and confirm the tarball exists.

| Category | Details |
| --- | --- |
| **Reason** | Including the exact source code version is required for reproducibility and compliance. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Construct the expected tarball filename using the stable_release_tag and verify with os.path.isfile. |

### 3. Gather the documentation files from the document_changes output: changelog_entries, readme_updates, documentation_changes, and security_findings_summary; copy them into a documentation directory within the staging area.

| Category | Details |
| --- | --- |
| **Reason** | All documentation updates must be bundled to reflect the applied patches and hardening measures. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Create a temporary docs folder, write each entry to appropriate files (e.g., CHANGELOG.md, README.md, INSTALL.md), and include security_findings_summary as SECURITY.md. |

### 4. Create a staging directory (e.g., /tmp/openssl_release_<timestamp>) and copy the binaries, source tarball, and documentation into subdirectories (bin/, src/, docs/).

| Category | Details |
| --- | --- |
| **Reason** | Organizing artifacts in a clean layout simplifies archiving and version control tagging. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use shutil.copytree or rsync to replicate the directory structure, ensuring permissions are preserved. |

### 5. Package the staged directory into a compressed archive (e.g., openssl-<version>.tar.gz) and store the path in artifact_package_path.

| Category | Details |
| --- | --- |
| **Reason** | A single archive is the standard distribution format for OpenSSL releases. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Invoke tar or zip via subprocess, handling errors and capturing the full path. |

### 6. Determine the release tag based on the stable_release_tag and the current date (e.g., v<stable_release_tag>-release-<YYYYMMDD>) and create the tag in the git repository using git tag -a.

| Category | Details |
| --- | --- |
| **Reason** | A unique, descriptive tag is essential for traceability and downstream consumption. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use git command line via subprocess, and capture any output or errors. |

### 7. Push the new tag to the remote repository (git push origin <tag>) and verify the push succeeded.

| Category | Details |
| --- | --- |
| **Reason** | Remote tagging makes the release visible to all stakeholders and CI pipelines. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Execute git push and check the return code; log any failures. |

### 8. Populate the output fields: artifact_package_path, release_tag, documentation_files (list of docs copied), binary_files (list of binaries copied), and set build_success to true if all previous steps succeeded, otherwise false.

| Category | Details |
| --- | --- |
| **Reason** | The downstream nodes require these structured outputs to continue the workflow. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Aggregate paths and flags into a JSON object, handling exceptions to set build_success appropriately. |
