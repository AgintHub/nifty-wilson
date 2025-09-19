from ._setup_environment.create_virtual_environment import create_virtual_environment
from ._setup_environment.activate_virtual_environment import activate_virtual_environment
from ._setup_environment.upgrade_package_managers import upgrade_package_managers
from ._setup_environment.read_requirements_file import read_requirements_file
from ._setup_environment.install_package_with_pip import install_package_with_pip
from ._setup_environment.verify_package_import import verify_package_import
from ._setup_environment.configure_path_environment import configure_path_environment
from ._setup_environment.configure_pythonpath import configure_pythonpath
from ._setup_environment.detect_and_configure_gpu_variables import detect_and_configure_gpu_variables
from ._setup_environment.configure_cpu_variables import configure_cpu_variables
from ._setup_environment.format_setup_log import format_setup_log

from pydantic import BaseModel, Field


# -- PRD --
# 1. BULLET: Create a dedicated Python virtual environment using `venv` to isolate
#   dependencies and prevent clashes with system packages.
#   Reason: Virtual environments isolate the workflow’s Python packages, ensuring
#           reproducibility across different machines and preventing
#           version conflicts.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Use `python -m venv .venv`; activate with `. .venv/bin/activate`; verify
#           activation by checking `sys.prefix`.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Upgrade pip, setuptools, and wheel to the latest stable versions to guarantee
#   compatibility with the latest package wheels.
#   Reason: Older package managers can fail to install binary wheels, causing
#           unnecessary compilation and longer setup times.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Run `pip install --upgrade pip setuptools wheel` and capture stdout/stderr
#           for logging.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Read a predefined `requirements.txt` (or similar manifest) located in the
#   project root to obtain the exact list of required packages and their
#   version constraints.
#   Reason: Explicit version specifications prevent inadvertent upgrades that could
#           break the workflow.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Open the file, parse lines ignoring comments, and construct a list of
#           package specifiers.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Install each package sequentially with pip, capturing the resolved version
#   after installation to populate `installed_packages` and
#   `installed_package_versions`.
#   Reason: Sequential installation allows fine-grained error handling and precise
#           logging of failures.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: For each specifier, execute `pip install <specifier>` via `subprocess.run`;
#           parse `pip` output for the installed version; append to lists.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Verify that each package is importable by attempting to import it after
#   installation, marking the setup as failed if any import errors arise.
#   Reason: Installation may succeed but the package could still be broken due to
#           missing binary dependencies or Python version
#           incompatibilities.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Use `importlib.import_module`; catch `ImportError` and record error
#           messages.
# 
# -----------------------------------------------------------------------------
# 6. BULLET: Configure the `PATH` environment variable to include the `bin` directory of
#   the virtual environment, ensuring executables from installed packages are
#   discoverable.
#   Reason: Certain packages expose CLI tools that must be available for later nodes
#           (e.g., tokenizers, data preprocessors).
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Prepend `os.path.join(venv_path, 'bin')` to `os.environ['PATH']`.
# 
# -----------------------------------------------------------------------------
# 7. BULLET: Set `PYTHONPATH` to include any project‑specific source directories that
#   contain modules required by the workflow.
#   Reason: Custom modules may reside outside the standard site‑packages path; this
#           ensures Python can locate them.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Add `os.path.abspath('src')` or similar to `PYTHONPATH` using
#           `os.environ['PYTHONPATH']`.
# 
# -----------------------------------------------------------------------------
# 8. BULLET: Define essential environment variables (e.g., `CUDA_VISIBLE_DEVICES`,
#   `OMP_NUM_THREADS`) based on configuration or system detection to control
#   resource usage.
#   Reason: Explicitly setting these variables improves reproducibility and avoids
#           accidental over‑use of GPUs or CPU cores.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Detect available GPUs via `nvidia-smi` or `torch.cuda.is_available()`; set
#           `CUDA_VISIBLE_DEVICES` accordingly.
# 
# -----------------------------------------------------------------------------
# 9. BULLET: Aggregate all configuration actions into a comprehensive `setup_log` string,
#   including timestamps, installed packages and versions, environment
#   variable settings, and any errors encountered.
#   Reason: A detailed log aids debugging, auditability, and future environment
#           replication.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Append each step’s outcome to a list and `' '.join(log_entries)`.
# 
# -----------------------------------------------------------------------------
# 10. BULLET: Return `environment_ready=True` only if every step succeeded; otherwise set
#   to `False` and populate `error_messages` (embedded in `setup_log`).
#   Reason: Child nodes depend on a ready environment; propagating a clear failure flag
#           prevents silent downstream failures.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Maintain a boolean flag `ready` that is set to `False` upon any exception;
#           final output reflects this flag.
# -- END PRD --



class SetupEnvironmentOutput(BaseModel):
    """Pydantic model for setup_environment node outputs."""
    environment_ready: bool = Field(..., description="Whether the environment was set up successfully.")
    installed_packages: str = Field(..., description="List of package names that were installed during setup.")
    installed_package_versions: str = Field(..., description="Corresponding package versions for installed packages.")
    configured_paths: str = Field(..., description="List of system paths that were configured (e.g., PATH, PYTHONPATH).")
    environment_variables: str = Field(..., description="List of environment variable names that were set.")
    setup_log: str = Field(..., description="A log string summarizing the setup process.")


def setup_environment(general_input: str, **kwargs) -> SetupEnvironmentOutput:
    """Prepare the runtime environment for the workflow by ensuring that all required libraries are installed, appropriate system paths are configured, and environment variables are set for subsequent nodes.

    Args:
        general_input: General input string for the root node.
        **kwargs: Additional keyword arguments.

    Returns:
        SetupEnvironmentOutput: Object containing outputs for this node.
    """
    # Initialize tracking variables
    environment_ready: bool = True
    log_entries: list = []
    installed_packages_list: list = []
    installed_versions_list: list = []
    configured_paths_list: list = []
    environment_vars_list: list = []
    
    try:
        # Create virtual environment
        venv_path: str = create_virtual_environment()
        log_entries.append(f"Created virtual environment at {venv_path}")
        
        # Activate virtual environment
        activation_success: bool = activate_virtual_environment(venv_path=venv_path)
        if not activation_success:
            environment_ready = False
            log_entries.append("Failed to activate virtual environment")
        
        # Upgrade pip, setuptools, wheel
        upgrade_result: dict = upgrade_package_managers()
        log_entries.append(f"Upgraded package managers: {upgrade_result}")
        
        # Read requirements.txt
        package_specifiers: list = read_requirements_file(file_path="requirements.txt")
        log_entries.append(f"Read {len(package_specifiers)} package requirements")
        
        # Install packages sequentially
        for specifier in package_specifiers:
            install_result: dict = install_package_with_pip(package_specifier=specifier)
            if install_result["success"]:
                installed_packages_list.append(install_result["package_name"])
                installed_versions_list.append(install_result["version"])
                log_entries.append(f"Installed {install_result['package_name']} {install_result['version']}")
            else:
                environment_ready = False
                log_entries.append(f"Failed to install {specifier}: {install_result['error']}")
        
        # Verify package imports
        for package_name in installed_packages_list:
            import_success: bool = verify_package_import(package_name=package_name)
            if not import_success:
                environment_ready = False
                log_entries.append(f"Failed to import {package_name}")
        
        # Configure PATH environment variable
        path_config_result: str = configure_path_environment(venv_path=venv_path)
        configured_paths_list.append(path_config_result)
        log_entries.append(f"Configured PATH: {path_config_result}")
        
        # Set PYTHONPATH
        pythonpath_result: str = configure_pythonpath()
        configured_paths_list.append(pythonpath_result)
        log_entries.append(f"Configured PYTHONPATH: {pythonpath_result}")
        
        # Set essential environment variables
        gpu_config: dict = detect_and_configure_gpu_variables()
        for var_name, var_value in gpu_config.items():
            environment_vars_list.append(var_name)
            log_entries.append(f"Set {var_name}={var_value}")
        
        cpu_config: dict = configure_cpu_variables()
        for var_name, var_value in cpu_config.items():
            environment_vars_list.append(var_name)
            log_entries.append(f"Set {var_name}={var_value}")
        
    except Exception as e:
        environment_ready = False
        log_entries.append(f"Setup failed with error: {str(e)}")
    
    # Aggregate results
    setup_log_final: str = format_setup_log(log_entries=log_entries)
    
    return SetupEnvironmentOutput(
        environment_ready=environment_ready,
        installed_packages=",".join(installed_packages_list),
        installed_package_versions=",".join(installed_versions_list),
        configured_paths=",".join(configured_paths_list),
        environment_variables=",".join(environment_vars_list),
        setup_log=setup_log_final,
    )