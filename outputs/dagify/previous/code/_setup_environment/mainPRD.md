# _setup_environment - Complete PRD Documentation

## Overview
PRDs for nodes in the '_setup_environment' module.

## Table of Contents

- [create_virtual_environment](#create_virtual_environment)

- [activate_virtual_environment](#activate_virtual_environment)

- [upgrade_package_managers](#upgrade_package_managers)

- [read_requirements_file](#read_requirements_file)

- [install_package_with_pip](#install_package_with_pip)

- [verify_package_import](#verify_package_import)

- [configure_path_environment](#configure_path_environment)

- [configure_pythonpath](#configure_pythonpath)

- [detect_and_configure_gpu_variables](#detect_and_configure_gpu_variables)

- [configure_cpu_variables](#configure_cpu_variables)

- [format_setup_log](#format_setup_log)



---

## create_virtual_environment

### Description
Creates a Python virtual environment and returns its filesystem path.

### Implementation Plan

#### 1. Initialize the virtual environment using Python's built‑in venv module inside a freshly created temporary directory.

| Category | Details |
| --- | --- |
| **Reason** | Ensures a clean, isolated environment with the standard venv structure. |
| **Impact** | Provides a reliable base for installing packages and configuring system paths. |
| **Complexity** | MEDIUM |
| **Method** | Use tempfile.mkdtemp to create a unique directory, then call venv.EnvBuilder(system_site_packages=False).create(env_dir) to set up the environment. |

#### 2. Return the absolute path of the created environment directory.

| Category | Details |
| --- | --- |
| **Reason** | Downstream nodes need this path to activate the venv and adjust PATH/PYTHONPATH. |
| **Impact** | Enables consistent reference and manipulation of the environment across the workflow. |
| **Complexity** | LOW |
| **Method** | Store the path in a variable and return it directly as a string. |

#### 3. Implement robust error handling that captures and reports any failures during venv creation.

| Category | Details |
| --- | --- |
| **Reason** | Prevents silent failures and aids debugging during workflow execution. |
| **Impact** | Improves reliability and provides clear failure messages to users. |
| **Complexity** | MEDIUM |
| **Method** | Wrap the creation logic in a try/except block; on exception, raise a RuntimeError with the exception message, and optionally clean up any partially created directories. |


---

## activate_virtual_environment

### Description
Activates a Python virtual environment at the specified path and returns a boolean indicating success.

### Implementation Plan

#### 1. Validate that the provided venv_path exists and contains the expected activation scripts.

| Category | Details |
| --- | --- |
| **Reason** | Avoid attempting to activate a non‑existent or incomplete virtual environment. |
| **Impact** | Prevents runtime errors and provides early failure feedback to the caller. |
| **Complexity** | LOW |
| **Method** | Use os.path.isdir and os.path.isfile to check the existence of the venv directory and key files like bin/activate (POSIX) or Scripts/activate.bat (Windows). |

#### 2. Prepend the virtual environment's bin/Scripts directory to the PATH and set PYTHONHOME to the venv path so that subsequent subprocesses use the correct interpreter.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that all commands executed after activation use the environment’s Python and libraries. |
| **Impact** | Guarantees consistent dependency resolution and eliminates conflicts with system packages. |
| **Complexity** | MEDIUM |
| **Method** | Modify os.environ['PATH'] and os.environ['PYTHONHOME'] within the current process, using the appropriate subdirectory for the detected OS. |

#### 3. Verify activation by invoking the venv’s python interpreter with a simple command and comparing the reported executable path.

| Category | Details |
| --- | --- |
| **Reason** | Provides a reliable test that the environment is truly active and functional. |
| **Impact** | Detects misconfigurations such as missing `activate` scripts or incorrect PATH ordering. |
| **Complexity** | MEDIUM |
| **Method** | Run subprocess.run([venv_python_path, "-c", "import sys;print(sys.executable)"]) and confirm that the output matches venv_python_path. |


---

## upgrade_package_managers

### Description
Upgrades pip, setuptools, and wheel in the current Python environment and returns a dictionary summarizing the upgrade results.

### Implementation Plan

#### 1. Determine the active Python interpreter and ensure all upgrade commands are executed within the current virtual environment.

| Category | Details |
| --- | --- |
| **Reason** | Guarantees upgrades affect the intended environment rather than a system-wide installation. |
| **Impact** | Prevents accidental upgrades of global packages and ensures reproducibility. |
| **Complexity** | LOW |
| **Method** | Use `sys.executable` to locate the interpreter and invoke `subprocess.run` with `-m pip` to upgrade packages. |

#### 2. Sequentially upgrade pip, setuptools, and wheel via subprocess, capturing stdout, stderr, and return codes for each.

| Category | Details |
| --- | --- |
| **Reason** | Allows precise error detection for each package and ensures upgrades are applied in a controlled order. |
| **Impact** | Provides reliable upgrade status and clear failure messages for downstream nodes. |
| **Complexity** | MEDIUM |
| **Method** | Call `subprocess.run(['pip', 'install', '--upgrade', package], capture_output=True, text=True, check=False)` for each package, parse the exit code, and extract the new version from stdout when successful. |

#### 3. Aggregate upgrade results into a JSON-serializable dictionary and return it as a string.

| Category | Details |
| --- | --- |
| **Reason** | The caller expects a string representation of the result for logging and further processing. |
| **Impact** | Enables easy parsing and logging of upgrade outcomes by other nodes. |
| **Complexity** | LOW |
| **Method** | Construct a dict with keys 'pip', 'setuptools', 'wheel'; each maps to a dict with 'success', 'new_version' (if applicable), and 'error' (if any). Use `json.dumps` to convert the dict to a string for the output. |


---

## read_requirements_file

### Description
Reads a requirements.txt file and returns a list of package specifiers.

### Implementation Plan

#### 1. Validate input file path and handle I/O errors gracefully.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the shim does not crash when the file is missing or unreadable, providing clear diagnostics. |
| **Impact** | Improves reliability and debuggability of the environment setup process. |
| **Complexity** | LOW |
| **Method** | Use `os.path.exists` and `try/except` around `open` to catch `FileNotFoundError` and `IOError`, returning an empty list or propagating a descriptive exception. |

#### 2. Parse the file line‑by‑line, stripping whitespace and ignoring comments.

| Category | Details |
| --- | --- |
| **Reason** | Accurately extracts only the intended package specifiers, preventing accidental installation of comment lines. |
| **Impact** | Ensures that only valid packages are passed to the installer, avoiding runtime failures. |
| **Complexity** | MEDIUM |
| **Method** | Iterate over `readlines()`, use `strip()` to remove whitespace, skip lines where `line.lstrip().startswith('#')`, and collect non‑empty lines. |

#### 3. Return the specifiers as a list in their original order.

| Category | Details |
| --- | --- |
| **Reason** | Preserves the order of package installation as defined by the user, which can be important for dependency resolution. |
| **Impact** | Maintains deterministic installation behavior across different runs and environments. |
| **Complexity** | LOW |
| **Method** | Append each cleaned line directly to a Python list and return that list. |


---

## install_package_with_pip

### Description
Installs a Python package via pip and returns installation result information.

### Implementation Plan

#### 1. Execute pip installation via a subprocess, capturing stdout/stderr and exit code.

| Category | Details |
| --- | --- |
| **Reason** | To actually install the package and gather installation status. |
| **Impact** | The target package will be installed into the active environment and its result reported. |
| **Complexity** | MEDIUM |
| **Method** | Use `subprocess.run(['pip', 'install', package_specifier, '--quiet'], capture_output=True, text=True)`; check `returncode`; on success parse output of `pip show package_name` to determine installed version. |

#### 2. Ensure the installation occurs within the current virtual environment or isolated context.

| Category | Details |
| --- | --- |
| **Reason** | Prevent polluting the global Python environment and ensure reproducibility. |
| **Impact** | Packages are installed only in the intended environment, making downstream steps reliable. |
| **Complexity** | LOW |
| **Method** | Rely on the environment being activated before the shim runs; optionally pass `--target` or use `env={'PYTHONPATH': ...}` if needed. |

#### 3. Return a consistently formatted JSON string containing success, package_name, version, and error information.

| Category | Details |
| --- | --- |
| **Reason** | Standardized output allows other nodes to parse results reliably. |
| **Impact** | Simplifies downstream error handling and reporting. |
| **Complexity** | LOW |
| **Method** | Create a dictionary `{ 'success': bool, 'package_name': str, 'version': str, 'error': str or None }` and serialize it with `json.dumps`. |


---

## verify_package_import

### Description
Checks whether a specified Python package can be imported successfully.

### Implementation Plan

#### 1. Attempt to import the package using importlib.import_module inside a try/except block.

| Category | Details |
| --- | --- |
| **Reason** | Directly tests the ability to load the package, which is the primary function of this shim. |
| **Impact** | Provides a quick success/failure signal to downstream nodes that rely on the package being available. |
| **Complexity** | LOW |
| **Method** | Use `importlib.import_module(package_name)` within a try block; if an ImportError or Exception occurs, return False. |

#### 2. Verify the module spec with importlib.util.find_spec before importing to handle packages that may be namespace packages or require special resolution.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that the package exists in the current environment and is discoverable, reducing false negatives caused by missing subpackages. |
| **Impact** | Improves reliability of the import check, especially in complex project structures or when using virtual environments. |
| **Complexity** | MEDIUM |
| **Method** | Call `spec = importlib.util.find_spec(package_name)`; if spec is None, return False; otherwise proceed with import. |

#### 3. Return a clean boolean value and log any error messages for debugging purposes.

| Category | Details |
| --- | --- |
| **Reason** | The node must provide deterministic output and aid troubleshooting when the import fails. |
| **Impact** | Downstream nodes can react to import failures, and developers can trace the root cause from logs. |
| **Complexity** | LOW |
| **Method** | Wrap the import logic in a try/except block, log the exception message (e.g., via the `logging` module), and return False on failure. |


---

## configure_path_environment

### Description
Configures the system PATH to include the bin directory of the specified virtual environment and returns the updated PATH string.

### Implementation Plan

#### 1. Determine the absolute path to the virtual environment's executable directory (e.g., 'venv_path/bin' on Unix or 'venv_path/Scripts' on Windows) and prepend it to the current PATH.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that the virtual environment's Python and pip executables are prioritized over system-wide versions. |
| **Impact** | Guarantees that subsequent package installations and executions use the correct interpreter and tools. |
| **Complexity** | LOW |
| **Method** | Use os.path.join with platform-specific directory names and os.environ.get('PATH') to construct the new PATH string. |

#### 2. Validate the presence of key executables (python, pip) within the newly added directory using shutil.which or a similar lookup.

| Category | Details |
| --- | --- |
| **Reason** | Detects misconfigurations early, preventing runtime errors during package installation or script execution. |
| **Impact** | Provides immediate feedback if the virtual environment's bin directory is missing or misnamed, improving reliability. |
| **Complexity** | LOW |
| **Method** | Call shutil.which('python') and shutil.which('pip') after updating PATH; if either returns None, raise a descriptive exception. |

#### 3. Return the finalized PATH string so downstream nodes can record or apply it as needed.

| Category | Details |
| --- | --- |
| **Reason** | Allows the calling workflow to store or further manipulate the configured PATH. |
| **Impact** | Ensures consistent environment propagation across subsequent nodes. |
| **Complexity** | LOW |
| **Method** | Simply return the constructed PATH string; no additional transformations required. |


---

## configure_pythonpath

### Description
Sets the PYTHONPATH environment variable to include the virtual environment’s site-packages and any custom directories.

### Implementation Plan

#### 1. Retrieve the virtual environment's `site-packages` path and any custom directories from configuration.

| Category | Details |
| --- | --- |
| **Reason** | The PYTHONPATH must point to all directories where Python packages can be found. |
| **Impact** | Ensures that imported modules are located correctly during runtime. |
| **Complexity** | LOW |
| **Method** | Use `sysconfig.get_paths()['purelib']` to locate site-packages inside the virtual environment and read a config file or environment variable for custom directories. |

#### 2. Validate that each path exists and is readable, removing any invalid entries.

| Category | Details |
| --- | --- |
| **Reason** | Invalid paths can cause import errors and obscure debugging information. |
| **Impact** | Improves reliability of the runtime environment and provides clear error messages if a path is missing. |
| **Complexity** | MEDIUM |
| **Method** | Iterate over the list of paths, use `os.path.isdir` and `os.access` to check existence and permissions, log warnings for missing paths. |

#### 3. Construct and return a colon‑separated string of the validated paths, ensuring the string is platform‑compatible.

| Category | Details |
| --- | --- |
| **Reason** | The runtime requires a single string to be set in the `PYTHONPATH` environment variable. |
| **Impact** | Produces a clean, reproducible environment variable that can be exported or used by downstream processes. |
| **Complexity** | LOW |
| **Method** | Join the validated path list using `os.pathsep` and return the result; optionally prepend the current `PYTHONPATH` if it exists. |


---

## detect_and_configure_gpu_variables

### Description
Detects GPU presence and configures environment variables to enable GPU support in the runtime environment.

### Implementation Plan

#### 1. Detect GPU availability by checking both PyTorch and system-level CUDA tools.

| Category | Details |
| --- | --- |
| **Reason** | Ensuring accurate detection is crucial for configuring the correct environment variables. |
| **Impact** | Provides reliable information for downstream nodes to decide whether to use GPU or fall back to CPU. |
| **Complexity** | LOW |
| **Method** | Use `torch.cuda.is_available()` for PyTorch; if unavailable, execute `nvidia-smi -L` via subprocess and parse the output. |

#### 2. Set GPU-specific environment variables such as CUDA_VISIBLE_DEVICES, PYTORCH_CUDA_ALLOC_CONF, and TF_GPU_ALLOCATOR based on detection results.

| Category | Details |
| --- | --- |
| **Reason** | These variables control which GPU devices are exposed and how memory is allocated, directly affecting performance. |
| **Impact** | Enables fine-grained control over GPU usage, reducing memory fragmentation and preventing unintended device selection. |
| **Complexity** | MEDIUM |
| **Method** | Build a dictionary mapping variable names to appropriate values (e.g., "0" for CUDA_VISIBLE_DEVICES) and return it serialized as JSON. |

#### 3. Provide a graceful fallback by returning an empty dictionary or CPU-specific variables when no GPU is detected.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the node does not fail on systems without GPUs and maintains compatibility with CPU-only workflows. |
| **Impact** | Prevents runtime errors and allows the same node to be reused across heterogeneous environments. |
| **Complexity** | LOW |
| **Method** | If GPU detection fails, populate the dictionary with variables like `CUDA_VISIBLE_DEVICES=''` and log the fallback. |


---

## configure_cpu_variables

### Description
Sets CPU‑related environment variables such as OMP_NUM_THREADS, MKL_NUM_THREADS, and NUMEXPR_NUM_THREADS based on the system’s CPU count and returns them as a JSON string.

### Implementation Plan

#### 1. Determine the number of logical CPU cores and set OMP_NUM_THREADS, MKL_NUM_THREADS, and NUMEXPR_NUM_THREADS accordingly.

| Category | Details |
| --- | --- |
| **Reason** | These variables control the thread parallelism for many numerical libraries and can dramatically affect performance. |
| **Impact** | Ensures that CPU‑intensive workloads use an optimal number of threads, improving throughput and avoiding oversubscription. |
| **Complexity** | LOW |
| **Method** | Use `multiprocessing.cpu_count()` to fetch the core count and assign it to the three variables via `os.environ`. |

#### 2. Respect existing environment variable overrides by checking for pre‑set values before modifying them.

| Category | Details |
| --- | --- |
| **Reason** | Users or upstream configurations may intentionally set specific thread counts for compatibility or testing. |
| **Impact** | Preserves user intent while still providing sensible defaults when variables are unset. |
| **Complexity** | LOW |
| **Method** | Query `os.getenv()` for each variable and only set it if the result is None. |

#### 3. Return the configured variables as a JSON string for downstream nodes.

| Category | Details |
| --- | --- |
| **Reason** | The consuming workflow expects a string representation of the configuration dictionary. |
| **Impact** | Provides a consistent, machine‑readable output that can be easily parsed by subsequent nodes. |
| **Complexity** | LOW |
| **Method** | Collect the variables into a Python dict and use `json.dumps()` to serialize it. |


---

## format_setup_log

### Description
Formats a list of setup log entries into a single human‑readable summary string.

### Implementation Plan

#### 1. Parse the raw log entries string into individual lines, trimming whitespace and ignoring empty lines.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that the input is clean and each entry is a distinct element for further processing. |
| **Impact** | Provides a reliable dataset for formatting and avoids formatting artifacts caused by extraneous whitespace. |
| **Complexity** | LOW |
| **Method** | Use Python's `splitlines()` followed by `strip()` on each line and filter out empty strings. |

#### 2. Format the parsed entries into a human‑readable summary string, preserving order and adding clear delimiters or bullet points.

| Category | Details |
| --- | --- |
| **Reason** | Creates an output that is easy to read and interpret by users and downstream systems. |
| **Impact** | Improves usability of the setup log and facilitates troubleshooting. |
| **Complexity** | LOW |
| **Method** | Join the cleaned lines with newline characters and optionally prefix each with a dash or number, then return the resulting string. |

#### 3. Validate input type and handle edge cases such as empty logs or excessively long entries.

| Category | Details |
| --- | --- |
| **Reason** | Ensures robustness and prevents runtime errors when the function is used with unexpected data. |
| **Impact** | Guarantees consistent behavior and prevents crashes or malformed outputs. |
| **Complexity** | MEDIUM |
| **Method** | Check that `log_entries` is a string; if empty, return a default message like 'No log entries available'; truncate entries that exceed a predefined length and log a warning. |
