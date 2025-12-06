from ._build_openssl.create_clean_build_environment import create_clean_build_environment
from ._build_openssl.copy_patched_source_code import copy_patched_source_code
from ._build_openssl.format_hardening_flags import format_hardening_flags
from ._build_openssl.construct_config_command import construct_config_command
from ._build_openssl.execute_config_command import execute_config_command
from ._build_openssl.get_config_error_log import get_config_error_log
from ._build_openssl.get_current_timestamp import get_current_timestamp
from ._build_openssl.construct_parallel_make_command import construct_parallel_make_command
from ._build_openssl.execute_build_command import execute_build_command
from ._build_openssl.read_build_log_file import read_build_log_file
from ._build_openssl.check_for_critical_errors import check_for_critical_errors
from ._build_openssl.execute_make_install import execute_make_install
from ._build_openssl.get_install_prefix_path import get_install_prefix_path
from ._build_openssl.collect_binary_artifacts import collect_binary_artifacts
from ._build_openssl.write_build_metadata import write_build_metadata

from pydantic import BaseModel, Field
from typing import List


# -- PRD --
# 1. BULLET: 1. Retrieve the hardened configuration flags from the parent node's output
#   (flags_applied) and merge them into the OpenSSL build command line using
#   the `./config` script with `--enable-optimizations` and `--with-ssl-
#   module` options. Ensure that each flag is prefixed with `-D` or `-f` as
#   appropriate, and that the command line is constructed in a portable shell
#   script that expands environment variables for the build host.
#   Reason: Integrating the exact hardening flags ensures reproducibility and that the
#           compiled binaries reflect the security posture defined by the
#           parent node.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Parse the flags_applied list, iterate over each entry, concatenate them
#           into a single string, and invoke `./config $FLAGS` followed by
#           `make` and `make install`. Capture stdout/stderr to a log file.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: 2. Set up a clean build environment by creating a temporary directory (e.g.,
#   `/tmp/openssl_build_${TIMESTAMP}`) and copying the patched source code
#   into it. This isolates the build from any pre‑existing artifacts and
#   prevents side effects on the source tree.
#   Reason: A clean environment eliminates hidden dependencies and ensures that the
#           build results are deterministic.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Use `mkdir -p` to create the directory, then `rsync -a` or `cp -r` to copy
#           the source. Record the path in `build_artifacts_path`.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: 3. Execute the build process using `make -j$(nproc)` to parallelize
#   compilation across all CPU cores. Redirect both stdout and stderr to a
#   log file (`build.log`) and capture the start and end timestamps to
#   compute `build_duration_seconds`.
#   Reason: Parallel compilation maximizes performance while the log file provides a
#           source of truth for debugging and audit.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Record `start_time=$(date +%s)` before invoking `make`, then
#           `end_time=$(date +%s)` after completion. Compute duration as
#           `build_duration_seconds=$((end_time - start_time))`.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: 4. After a successful `make install`, collect the names of the generated
#   binary artifacts by listing the contents of the install prefix
#   (`/usr/local/ssl/lib` or the configured prefix). Populate the
#   `artifact_names` list with base filenames (e.g., `libssl.so.1.1`,
#   `libcrypto.so.1.1`).
#   Reason: Explicitly enumerating artifacts enables downstream nodes to reference them
#           without hard‑coding paths.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Use `ls -1 $PREFIX/lib` and filter for files matching `libssl.*` and
#           `libcrypto.*`. Strip any version suffixes if required by
#           downstream consumers.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: 5. Determine `build_success` by checking the exit status of the `make`
#   command and verifying that no critical errors appear in the log (e.g.,
#   lines containing `error:` or `fatal:`). If any such errors are present,
#   set `build_success` to `false` and include the relevant log excerpts in
#   `build_log`.
#   Reason: Accurate success flag is essential for conditional execution of downstream
#           nodes (e.g., re‑run tests).
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Capture `$?` from the last command; parse `build.log` with `grep -i
#           'error\|fatal'`. If matches found, set `build_success=false`.
# 
# -----------------------------------------------------------------------------
# 6. BULLET: 6. Write a concise summary of the build outcome to a metadata file
#   (`build_metadata.json`) containing all output fields. This file will be
#   consumed by downstream nodes to avoid re‑parsing logs.
#   Reason: Centralizing output in a structured format simplifies data ingestion for
#           subsequent processes.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Use `jq` or a Python script to serialize the fields into JSON and write to
#           `build_metadata.json`.
# -- END PRD --



class ApplyHardeningFlagsOutput(BaseModel):
    """Pydantic model for apply_hardening_flags node outputs."""
    flags_applied: List[str] = Field(..., description="List of compilation flags applied to enable security hardening.")
    flags_summary: str = Field(..., description="Human-readable summary of the applied hardening options.")
    success: bool = Field(..., description="Indicates whether the flags were successfully integrated into the build configuration.")


class BuildOpensslOutput(BaseModel):
    """Pydantic model for build_openssl node outputs."""
    binary_artifacts_path: str = Field(..., description="Filesystem path to the directory containing compiled OpenSSL binaries.")
    build_success: bool = Field(..., description="Indicates whether the build completed without errors.")
    build_log: str = Field(..., description="Textual log of the build process.")
    artifact_names: str = Field(..., description="List of names of generated binary artifacts (e.g., libssl.so, libcrypto.so).")
    build_duration_seconds: int = Field(..., description="Total time taken for the build in seconds.")


def build_openssl(apply_hardening_flags_input: ApplyHardeningFlagsOutput, **kwargs) -> BuildOpensslOutput:
    """Build the OpenSSL binaries from the source code that has been patched for known vulnerabilities and configured with security hardening flags. The build should generate the standard OpenSSL libraries and binaries, capture detailed logs, and record build metrics.

    Args:
        apply_hardening_flags_input: Input from the 'apply_hardening_flags' node.
        **kwargs: Additional keyword arguments.

    Returns:
        BuildOpensslOutput: Object containing outputs for this node.
    """
    # Create clean build environment
    build_directory: str = create_clean_build_environment()
    copy_patched_source_code(destination=build_directory)
    
    # Prepare hardening flags for build configuration
    formatted_flags: str = format_hardening_flags(flags=apply_hardening_flags_input.flags_applied)
    
    # Configure OpenSSL with hardening flags
    config_command: str = construct_config_command(flags=formatted_flags)
    config_success: bool = execute_config_command(command=config_command, build_dir=build_directory)
    
    if not config_success:
        error_log: str = get_config_error_log()
        return BuildOpensslOutput(
            binary_artifacts_path=build_directory,
            build_success=False,
            build_log=error_log,
            artifact_names="",
            build_duration_seconds=0
        )
    
    # Execute parallel build process
    start_timestamp: int = get_current_timestamp()
    make_command: str = construct_parallel_make_command()
    build_exit_code: int = execute_build_command(command=make_command, build_dir=build_directory)
    end_timestamp: int = get_current_timestamp()
    
    # Calculate build duration
    duration: int = end_timestamp - start_timestamp
    
    # Capture build logs
    full_build_log: str = read_build_log_file(build_dir=build_directory)
    
    # Determine build success
    has_critical_errors: bool = check_for_critical_errors(log_content=full_build_log)
    build_succeeded: bool = (build_exit_code == 0) and not has_critical_errors
    
    if build_succeeded:
        # Execute make install
        install_success: bool = execute_make_install(build_dir=build_directory)
        if not install_success:
            build_succeeded = False
    
    # Collect artifact information
    artifacts_path: str = get_install_prefix_path()
    artifact_list: str = collect_binary_artifacts(install_prefix=artifacts_path) if build_succeeded else ""
    
    # Write metadata file
    write_build_metadata(build_dir=build_directory, success=build_succeeded, duration=duration, artifacts=artifact_list)
    
    return BuildOpensslOutput(
        binary_artifacts_path=artifacts_path,
        build_success=build_succeeded,
        build_log=full_build_log,
        artifact_names=artifact_list,
        build_duration_seconds=duration
    )