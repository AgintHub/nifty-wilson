# setup_environment PRD

## Description
Prepare the runtime environment for the workflow by ensuring that all required libraries are installed, appropriate system paths are configured, and environment variables are set for subsequent nodes.


## Implementation Plan

### 1. Create a dedicated Python virtual environment using `venv` to isolate dependencies and prevent clashes with system packages.

| Category | Details |
| --- | --- |
| **Reason** | Virtual environments isolate the workflow’s Python packages, ensuring reproducibility across different machines and preventing version conflicts. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use `python -m venv .venv`; activate with `. .venv/bin/activate`; verify activation by checking `sys.prefix`. |

### 2. Upgrade pip, setuptools, and wheel to the latest stable versions to guarantee compatibility with the latest package wheels.

| Category | Details |
| --- | --- |
| **Reason** | Older package managers can fail to install binary wheels, causing unnecessary compilation and longer setup times. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Run `pip install --upgrade pip setuptools wheel` and capture stdout/stderr for logging. |

### 3. Read a predefined `requirements.txt` (or similar manifest) located in the project root to obtain the exact list of required packages and their version constraints.

| Category | Details |
| --- | --- |
| **Reason** | Explicit version specifications prevent inadvertent upgrades that could break the workflow. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Open the file, parse lines ignoring comments, and construct a list of package specifiers. |

### 4. Install each package sequentially with pip, capturing the resolved version after installation to populate `installed_packages` and `installed_package_versions`.

| Category | Details |
| --- | --- |
| **Reason** | Sequential installation allows fine-grained error handling and precise logging of failures. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | For each specifier, execute `pip install <specifier>` via `subprocess.run`; parse `pip` output for the installed version; append to lists. |

### 5. Verify that each package is importable by attempting to import it after installation, marking the setup as failed if any import errors arise.

| Category | Details |
| --- | --- |
| **Reason** | Installation may succeed but the package could still be broken due to missing binary dependencies or Python version incompatibilities. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use `importlib.import_module`; catch `ImportError` and record error messages. |

### 6. Configure the `PATH` environment variable to include the `bin` directory of the virtual environment, ensuring executables from installed packages are discoverable.

| Category | Details |
| --- | --- |
| **Reason** | Certain packages expose CLI tools that must be available for later nodes (e.g., tokenizers, data preprocessors). |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Prepend `os.path.join(venv_path, 'bin')` to `os.environ['PATH']`. |

### 7. Set `PYTHONPATH` to include any project‑specific source directories that contain modules required by the workflow.

| Category | Details |
| --- | --- |
| **Reason** | Custom modules may reside outside the standard site‑packages path; this ensures Python can locate them. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Add `os.path.abspath('src')` or similar to `PYTHONPATH` using `os.environ['PYTHONPATH']`. |

### 8. Define essential environment variables (e.g., `CUDA_VISIBLE_DEVICES`, `OMP_NUM_THREADS`) based on configuration or system detection to control resource usage.

| Category | Details |
| --- | --- |
| **Reason** | Explicitly setting these variables improves reproducibility and avoids accidental over‑use of GPUs or CPU cores. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Detect available GPUs via `nvidia-smi` or `torch.cuda.is_available()`; set `CUDA_VISIBLE_DEVICES` accordingly. |

### 9. Aggregate all configuration actions into a comprehensive `setup_log` string, including timestamps, installed packages and versions, environment variable settings, and any errors encountered.

| Category | Details |
| --- | --- |
| **Reason** | A detailed log aids debugging, auditability, and future environment replication. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Append each step’s outcome to a list and `'
'.join(log_entries)`. |

### 10. Return `environment_ready=True` only if every step succeeded; otherwise set to `False` and populate `error_messages` (embedded in `setup_log`).

| Category | Details |
| --- | --- |
| **Reason** | Child nodes depend on a ready environment; propagating a clear failure flag prevents silent downstream failures. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Maintain a boolean flag `ready` that is set to `False` upon any exception; final output reflects this flag. |
