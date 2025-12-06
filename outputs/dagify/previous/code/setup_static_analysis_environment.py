from ._setup_static_analysis_environment.install_static_analysis_tools import install_static_analysis_tools
from ._setup_static_analysis_environment.verify_tool_installations import verify_tool_installations
from ._setup_static_analysis_environment.create_configuration_directory import create_configuration_directory
from ._setup_static_analysis_environment.generate_clang_tidy_config import generate_clang_tidy_config
from ._setup_static_analysis_environment.write_config_file import write_config_file
from ._setup_static_analysis_environment.generate_cppcheck_config import generate_cppcheck_config
from ._setup_static_analysis_environment.set_environment_variables import set_environment_variables
from ._setup_static_analysis_environment.run_clang_tidy_dryrun import run_clang_tidy_dryrun
from ._setup_static_analysis_environment.run_cppcheck_dryrun import run_cppcheck_dryrun
from ._setup_static_analysis_environment.parse_validation_output import parse_validation_output
from ._setup_static_analysis_environment.adjust_configuration_files import adjust_configuration_files

from pydantic import BaseModel, Field


# -- PRD --
# 1. BULLET: Use a package manager (e.g., apt, yum, brew) to install clang-tidy and
#   cppcheck, ensuring the latest stable versions are retrieved and any
#   required dependencies (e.g., libclang) are met.
#   Reason: Installing tools via the system package manager guarantees compatibility
#           with the host OS and simplifies future updates.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Run `sudo apt-get install -y clang-tidy cppcheck` on Debian/Ubuntu, or the
#           equivalent commands for other distros; verify installation by
#           checking the version output.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Create a dedicated configuration directory (e.g.,
#   `~/.config/openssl/static_analysis`) and place a `clang-tidy`
#   configuration file (`.clang-tidy`) that enforces OpenSSL coding standards
#   (e.g., `-warnings-as-errors`, `-header-filter=.*`), and a `cppcheck`
#   configuration file (`cppcheck.cfg`) with appropriate `--enable=all` and
#   `--inconclusive` flags.
#   Reason: Centralizing configuration files allows consistent enforcement across all
#           analysis runs and makes it easy to revert or adjust standards.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Generate the files using templated content from OpenSSL's style guide;
#           place them in the configuration directory and set environment
#           variables `CLANG_TIDY_CONFIG` and `CPPCHECK_CONFIG` to point to
#           these files.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Validate the configuration by running a dry‑run analysis on a small subset of
#   the OpenSSL source tree (e.g., `clang-tidy -p build --config-file=.clang-
#   tidy src/ssl/*.c` and `cppcheck --config=cppcheck.cfg src/ssl/*.c`),
#   capturing any errors or warnings that indicate misconfiguration.
#   Reason: A dry‑run ensures that the tools are correctly interpreting the
#           configuration and that the environment is ready for full
#           analysis.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Parse the output for fatal errors; if any are found, adjust the
#           configuration files accordingly and repeat until no fatal
#           errors remain.
# -- END PRD --



class SetupStaticAnalysisEnvironmentOutput(BaseModel):
    """Pydantic model for setup_static_analysis_environment node outputs."""
    installed_tools: str = Field(..., description="Names of static analysis tools installed in the environment.")
    configuration_success: bool = Field(..., description="Whether the configuration of the tools succeeded without errors.")
    environment_ready: bool = Field(..., description="Indicates if the environment is fully ready for static code analysis runs.")


def setup_static_analysis_environment(general_input: str, **kwargs) -> SetupStaticAnalysisEnvironmentOutput:
    """Prepare the environment for static code analysis.

    Args:
        general_input: General input string for the root node.
        **kwargs: Additional keyword arguments.

    Returns:
        SetupStaticAnalysisEnvironmentOutput: Object containing outputs for this node.
    """
    # Install clang-tidy and cppcheck using package manager
    installed_tools_list: list = install_static_analysis_tools(tools=["clang-tidy", "cppcheck"])
    
    # Verify installations by checking versions
    installation_success: bool = verify_tool_installations(tools=installed_tools_list)
    
    # Create configuration directory
    config_dir_path: str = create_configuration_directory(path="~/.config/openssl/static_analysis")
    
    # Generate and place clang-tidy configuration file
    clang_tidy_config: str = generate_clang_tidy_config(openssl_standards=True, warnings_as_errors=True)
    write_config_file(content=clang_tidy_config, path=f"{config_dir_path}/.clang-tidy")
    
    # Generate and place cppcheck configuration file
    cppcheck_config: str = generate_cppcheck_config(enable_all=True, inconclusive=True)
    write_config_file(content=cppcheck_config, path=f"{config_dir_path}/cppcheck.cfg")
    
    # Set environment variables
    set_environment_variables(clang_tidy_config=f"{config_dir_path}/.clang-tidy", cppcheck_config=f"{config_dir_path}/cppcheck.cfg")
    
    # Perform dry-run validation on small OpenSSL subset
    clang_tidy_errors: list = run_clang_tidy_dryrun(config_file=f"{config_dir_path}/.clang-tidy", source_path="src/ssl/*.c")
    cppcheck_errors: list = run_cppcheck_dryrun(config_file=f"{config_dir_path}/cppcheck.cfg", source_path="src/ssl/*.c")
    
    # Parse and analyze validation results
    fatal_errors: bool = parse_validation_output(clang_errors=clang_tidy_errors, cppcheck_errors=cppcheck_errors)
    
    # Adjust configuration if needed
    config_success: bool = True
    if fatal_errors:
        config_success = adjust_configuration_files(config_dir=config_dir_path, errors=clang_tidy_errors + cppcheck_errors)
    
    # Determine overall environment readiness
    environment_ready: bool = installation_success and config_success and not fatal_errors
    
    return SetupStaticAnalysisEnvironmentOutput(
        installed_tools=", ".join(installed_tools_list),
        configuration_success=config_success,
        environment_ready=environment_ready
    )