from ._setup_dynamic_testing_environment.create_build_directory import create_build_directory
from ._setup_dynamic_testing_environment.set_directory_permissions import set_directory_permissions
from ._setup_dynamic_testing_environment.get_required_packages import get_required_packages
from ._setup_dynamic_testing_environment.install_system_packages import install_system_packages
from ._setup_dynamic_testing_environment.format_installed_packages import format_installed_packages
from ._setup_dynamic_testing_environment.run_openssl_config import run_openssl_config
from ._setup_dynamic_testing_environment.capture_config_file_path import capture_config_file_path
from ._setup_dynamic_testing_environment.compile_test_binaries import compile_test_binaries
from ._setup_dynamic_testing_environment.locate_test_binaries import locate_test_binaries
from ._setup_dynamic_testing_environment.setup_environment_variables import setup_environment_variables
from ._setup_dynamic_testing_environment.format_environment_variables import format_environment_variables
from ._setup_dynamic_testing_environment.run_sanity_check_tests import run_sanity_check_tests
from ._setup_dynamic_testing_environment.evaluate_setup_success import evaluate_setup_success

from pydantic import BaseModel, Field


# -- PRD --
# 1. BULLET: Create a dedicated build directory under the source tree to isolate testing
#   artifacts, e.g., `build/test`. Ensure the directory is writable and has
#   appropriate permissions for the build user.
#   Reason: Isolation prevents cross-contamination with other build artifacts and
#           ensures reproducible results.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Use shell commands `mkdir -p` and `chmod` to set up the directory; verify
#           with `ls -ld`.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Install all required development packages (e.g., `make`, `gcc`, `perl`,
#   `openssl-devel`) using the system package manager, and capture the list
#   of installed packages for output.
#   Reason: Missing dependencies cause configuration or compilation failures, halting
#           the test setup.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Run `sudo apt-get install -y` (Debian/Ubuntu) or `sudo yum install -y`
#           (RHEL/CentOS) for each package; parse the output to populate
#           `installed_packages`.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Execute the OpenSSL configuration script with the `enable-tests` flag and any
#   additional test‑related options (e.g., `no-shared` for static builds).
#   Capture the generated `config` file path.
#   Reason: The `enable-tests` flag tells the build system to compile test binaries;
#           capturing the config file allows later verification.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Run `./config enable-tests` inside the source root; redirect stdout to a
#           temporary file and store its path as `config_file_path`.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Invoke `make` to compile all test binaries, specifying parallelism (e.g.,
#   `make -j$(nproc)`). Record the path to the resulting test binary
#   directory.
#   Reason: Compiling tests ensures they are up‑to‑date with the current source and
#           configuration.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Run `make -j$(nproc)`; upon success, locate the binaries under `build/test`
#           or `build/openssl` and set `test_binary_path`.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Set necessary environment variables for testing, such as `LD_LIBRARY_PATH`
#   pointing to the build's lib directory, and any OpenSSL-specific variables
#   (e.g., `OPENSSL_CONF`). Store these assignments in
#   `environment_variables`.
#   Reason: Environment variables control runtime behavior and ensure the test binaries
#           link against the correct libraries.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Export variables in the shell (`export VAR=value`) and capture them via
#           `env | grep VAR`.
# 
# -----------------------------------------------------------------------------
# 6. BULLET: Run a lightweight sanity check by executing a subset of tests (e.g., `make
#   test` with `-t` to run a few tests) and verify that all tests exit with
#   status 0.
#   Reason: A quick sanity check confirms that the environment is correctly configured
#           before full test runs.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Execute `make test` with a timeout; parse the exit code and set
#           `environment_setup_success` accordingly.
# 
# -----------------------------------------------------------------------------
# 7. BULLET: Populate the output fields: set `environment_setup_success` to `true` if all
#   previous steps succeeded; otherwise `false`. Include the list of
#   installed packages, config file path, test binary path, and environment
#   variable assignments.
#   Reason: Providing structured output enables downstream nodes to consume the setup
#           results reliably.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Serialize the collected data into a JSON or YAML format matching the
#           defined output schema.
# -- END PRD --



class SetupDynamicTestingEnvironmentOutput(BaseModel):
    """Pydantic model for setup_dynamic_testing_environment node outputs."""
    environment_setup_success: bool = Field(..., description="Indicates whether the environment was set up successfully.")
    installed_packages: str = Field(..., description="List of package names that were installed as part of the setup.")
    config_file_path: str = Field(..., description="Path to the configuration file generated for testing.")
    test_binary_path: str = Field(..., description="Path to the compiled test binaries.")
    environment_variables: str = Field(..., description="List of environment variable assignments used during testing.")


def setup_dynamic_testing_environment(general_input: str, **kwargs) -> SetupDynamicTestingEnvironmentOutput:
    """Prepare the environment for dynamic testing.

    Args:
        general_input: General input string for the root node.
        **kwargs: Additional keyword arguments.

    Returns:
        SetupDynamicTestingEnvironmentOutput: Object containing outputs for this node.
    """
    # Create dedicated build directory for testing
    build_dir_success: bool = create_build_directory(path="build/test")
    set_directory_permissions(path="build/test", permissions="755")
    
    # Install required development packages
    package_list: list = get_required_packages()
    installation_results: dict = install_system_packages(packages=package_list)
    installed_packages_str: str = format_installed_packages(results=installation_results)
    
    # Execute OpenSSL configuration with enable-tests flag
    config_result: dict = run_openssl_config(flags=["enable-tests"], additional_options=["no-shared"])
    config_file_path_str: str = capture_config_file_path(result=config_result)
    
    # Compile test binaries with make
    make_result: dict = compile_test_binaries(parallelism="-j$(nproc)")
    test_binary_path_str: str = locate_test_binaries(result=make_result, search_paths=["build/test", "build/openssl"])
    
    # Set up environment variables
    env_vars: dict = setup_environment_variables(lib_path="build/lib")
    environment_variables_str: str = format_environment_variables(env_vars=env_vars)
    
    # Run sanity check
    sanity_check_result: bool = run_sanity_check_tests(timeout=300)
    
    # Determine overall success
    overall_success: bool = evaluate_setup_success(
        build_dir=build_dir_success,
        packages=installation_results,
        config=config_result,
        compilation=make_result,
        sanity_check=sanity_check_result
    )
    
    return SetupDynamicTestingEnvironmentOutput(
        environment_setup_success=overall_success,
        installed_packages=installed_packages_str,
        config_file_path=config_file_path_str,
        test_binary_path=test_binary_path_str,
        environment_variables=environment_variables_str,
    )