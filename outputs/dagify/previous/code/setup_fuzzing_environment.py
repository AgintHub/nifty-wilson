from ._setup_fuzzing_environment.install_fuzzing_dependencies import install_fuzzing_dependencies
from ._setup_fuzzing_environment.clone_openssl_repository import clone_openssl_repository
from ._setup_fuzzing_environment.select_fuzzing_framework import select_fuzzing_framework
from ._setup_fuzzing_environment.generate_config_flags import generate_config_flags
from ._setup_fuzzing_environment.configure_openssl import configure_openssl
from ._setup_fuzzing_environment.compile_openssl_with_parallelism import compile_openssl_with_parallelism
from ._setup_fuzzing_environment.create_seed_directory import create_seed_directory
from ._setup_fuzzing_environment.extract_test_vectors_as_seeds import extract_test_vectors_as_seeds
from ._setup_fuzzing_environment.create_config_directory import create_config_directory
from ._setup_fuzzing_environment.write_framework_config_files import write_framework_config_files
from ._setup_fuzzing_environment.validate_fuzzing_setup import validate_fuzzing_setup

from pydantic import BaseModel, Field


# -- PRD --
# 1. BULLET: Install all required system packages and libraries for AFL and libFuzzer,
#   including clang, gcc, and the OpenSSL development headers.
#   Reason: Ensures that the build tools and dependencies needed for compiling OpenSSL
#           with fuzzing instrumentation are available.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Use package manager commands (apt-get, yum, brew) to install packages;
#           verify installation by checking versions.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Clone the latest OpenSSL source tree into a dedicated workspace and check out
#   the stable release tag.
#   Reason: Provides a clean, reproducible source base for building with fuzzing
#           support.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Run `git clone https://github.com/openssl/openssl` and `git checkout
#           <stable-tag>`; store the path for later steps.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Configure OpenSSL to enable fuzzing instrumentation by passing the
#   appropriate flags to the `./config` script (e.g., `-fuzzer` for AFL or
#   `-fsanitize=fuzzer` for libFuzzer).
#   Reason: Ensures that the compiled binaries are instrumented for memory safety and
#           crash detection.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Detect which framework is chosen (AFL or libFuzzer) and append the
#           corresponding compiler flags; run `./config` with these flags.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Compile the OpenSSL binaries using `make` with the `-j` flag to leverage
#   parallelism.
#   Reason: Produces the fuzzable binaries that will be used by the fuzzing framework.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Execute `make -j$(nproc)` and capture the build log; ensure build_success
#           is true.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Generate initial seed files by extracting the existing OpenSSL test vectors
#   (e.g., `testssl.sh` outputs) and converting them into binary format
#   suitable for AFL/libFuzzer.
#   Reason: Seeds provide the starting point for fuzzers to explore code paths.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Run OpenSSL's test suite with `--output-seeds` option if available;
#           otherwise, capture input streams from test cases and store them
#           as files.
# 
# -----------------------------------------------------------------------------
# 6. BULLET: Create a dedicated configuration directory (e.g., `/opt/fuzz-config`) and
#   store the framework-specific configuration files (e.g., `afl.cfg`,
#   `libfuzzer.cfg`).
#   Reason: Organizes all fuzzing settings for reproducibility and easy cleanup.
#   Impact: LOW
#   Complexity: LOW
#   Method: Use `mkdir -p` to create the directory; write minimal config files that
#           specify target binary path and seed directory.
# 
# -----------------------------------------------------------------------------
# 7. BULLET: Validate the fuzzing environment by running a short sanity check: invoke the
#   chosen fuzzing framework on a minimal OpenSSL command (e.g., `openssl
#   version`) with a single seed and ensure no immediate crashes or missing
#   binaries.
#   Reason: Catches configuration errors before full fuzzing sessions start.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Execute `afl-fuzz -i <seed-dir> -o <out-dir> -- openssl version` or `clang-
#           fuzzer <binary> <seed>` and inspect exit status.
# 
# -----------------------------------------------------------------------------
# 8. BULLET: Populate the output fields: list the configured frameworks, paths to
#   generated seed files, set `environment_ready` to true if all checks
#   passed, and record the `config_directory` path.
#   Reason: Ensures that downstream nodes receive the correct data to proceed with
#           fuzzing.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Programmatically collect file paths and boolean flags; serialize them into
#           the expected output structure.
# -- END PRD --



class SetupFuzzingEnvironmentOutput(BaseModel):
    """Pydantic model for setup_fuzzing_environment node outputs."""
    frameworks_configured: str = Field(..., description="List of fuzzing frameworks configured (e.g., AFL, libFuzzer).")
    seed_files: str = Field(..., description="Paths to the generated initial seed files used for fuzzing.")
    environment_ready: bool = Field(..., description="Indicates whether the fuzzing environment is fully set up and ready to run tests.")
    config_directory: str = Field(..., description="File system path to the directory containing fuzzing configuration files.")


def setup_fuzzing_environment(general_input: str, **kwargs) -> SetupFuzzingEnvironmentOutput:
    """Prepare the environment for fuzz testing.

    Args:
        general_input: General input string for the root node.
        **kwargs: Additional keyword arguments.

    Returns:
        SetupFuzzingEnvironmentOutput: Object containing outputs for this node.
    """
    # Install required system packages and libraries
    install_success: bool = install_fuzzing_dependencies(packages=["clang", "gcc", "libssl-dev", "afl++"])
    
    # Clone OpenSSL source tree
    openssl_path: str = clone_openssl_repository(workspace_dir="/tmp/fuzzing-workspace")
    
    # Determine fuzzing framework to use
    framework_choice: str = select_fuzzing_framework(preferred="AFL")
    
    # Configure OpenSSL with fuzzing instrumentation
    config_flags: str = generate_config_flags(framework=framework_choice)
    config_success: bool = configure_openssl(source_path=openssl_path, flags=config_flags)
    
    # Compile OpenSSL binaries
    build_success: bool = compile_openssl_with_parallelism(source_path=openssl_path)
    
    # Generate initial seed files from test vectors
    seed_directory: str = create_seed_directory(base_path="/tmp/fuzzing-seeds")
    seed_paths: str = extract_test_vectors_as_seeds(openssl_path=openssl_path, output_dir=seed_directory)
    
    # Create configuration directory
    config_dir: str = create_config_directory(path="/opt/fuzz-config")
    write_framework_config_files(config_dir=config_dir, framework=framework_choice, binary_path=openssl_path, seed_dir=seed_directory)
    
    # Validate fuzzing environment with sanity check
    validation_success: bool = validate_fuzzing_setup(framework=framework_choice, binary_path=openssl_path, seed_dir=seed_directory)
    
    # Determine if environment is fully ready
    environment_ready: bool = install_success and config_success and build_success and validation_success
    
    return SetupFuzzingEnvironmentOutput(
        frameworks_configured=framework_choice,
        seed_files=seed_paths,
        environment_ready=environment_ready,
        config_directory=config_dir
    )