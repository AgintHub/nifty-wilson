from ._run_fuzzing.log_error import log_error
from ._run_fuzzing.select_preferred_framework import select_preferred_framework
from ._run_fuzzing.construct_binary_path import construct_binary_path
from ._run_fuzzing.verify_binary_exists import verify_binary_exists
from ._run_fuzzing.create_temp_directory import create_temp_directory
from ._run_fuzzing.get_current_timestamp import get_current_timestamp
from ._run_fuzzing.launch_fuzzing_tool import launch_fuzzing_tool
from ._run_fuzzing.calculate_duration_seconds import calculate_duration_seconds
from ._run_fuzzing.get_log_file_path import get_log_file_path
from ._run_fuzzing.parse_crash_data import parse_crash_data
from ._run_fuzzing.count_unexpected_behaviors import count_unexpected_behaviors
from ._run_fuzzing.check_run_success import check_run_success
from ._run_fuzzing.cleanup_temp_directory import cleanup_temp_directory

from pydantic import BaseModel, Field
from typing import List


# -- PRD --
# 1. BULLET: Validate that the fuzzing environment is fully ready by checking the
#   'environment_ready' flag from 'setup_fuzzing_environment'. If false,
#   abort the run and set 'successful_run' to false.
#   Reason: Ensures that all required tools (e.g., AFL, libFuzzer) and dependencies are
#           installed before execution.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Read the boolean flag from the parent node's output; if false, log an error
#           and terminate the process.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Determine the fuzzing framework to use by selecting the first entry from
#   'frameworks_configured' (prefer libFuzzer over AFL if both are present).
#   Reason: Standardizes the fuzzing approach and avoids ambiguity when multiple
#           frameworks are configured.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Access the list from the parent output; apply a simple conditional
#           selection.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Construct the path to the compiled OpenSSL binaries by appending 'build' to
#   the 'clone_path' from 'collect_current_openssl_source'. Verify that the
#   binaries exist before proceeding.
#   Reason: Ensures that fuzzing is performed on the correct binaries rather than
#           source files.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Concatenate strings to form the expected build directory; use filesystem
#           checks (e.g., os.path.isdir) to confirm existence.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Create a temporary directory for storing crash inputs and logs, using a
#   unique timestamped name to avoid collisions with previous runs.
#   Reason: Provides isolation between fuzzing sessions and makes post‑processing
#           easier.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Use the 'tempfile' module or shell 'mktemp' to generate a unique directory.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Launch the fuzzing tool with arguments that include the path to the seed
#   files from 'seed_files', the target binary directory, and a predefined
#   timeout (e.g., 3600 seconds). Capture stdout and stderr to a log file in
#   the temporary directory.
#   Reason: Runs the fuzzing engine while collecting all relevant output for analysis.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Construct a command line string; invoke via subprocess.run with timeout and
#           redirect output to a log file.
# 
# -----------------------------------------------------------------------------
# 6. BULLET: Parse the fuzzing log file to extract crash identifiers by hashing the crash
#   input files (e.g., using SHA‑256) and collect the first line of each
#   crash stack trace as the description.
#   Reason: Produces deterministic identifiers that can be used for later triage.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Read the log file line by line; for each crash block, locate the input file
#           path, read its contents, compute hash, and extract the relevant
#           trace lines.
# 
# -----------------------------------------------------------------------------
# 7. BULLET: Count the number of unexpected behaviors by scanning the log for keywords
#   such as 'crash', 'hang', 'assert', and 'timeout'. Increment a counter for
#   each occurrence.
#   Reason: Provides a quantitative measure of fuzzing effectiveness.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Use regular expressions or simple string matching over the log content.
# 
# -----------------------------------------------------------------------------
# 8. BULLET: Determine 'successful_run' by checking the exit code of the fuzzing process;
#   a non‑zero exit code indicates a fatal error during execution.
#   Reason: Captures whether the fuzzing process completed normally.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Inspect the 'returncode' attribute from the subprocess result.
# 
# -----------------------------------------------------------------------------
# 9. BULLET: Calculate 'total_duration_seconds' by recording the start and end timestamps
#   of the fuzzing run and computing the difference in seconds.
#   Reason: Provides a precise measurement of runtime for reporting.
#   Impact: LOW
#   Complexity: LOW
#   Method: Use time.time() before and after the subprocess call; subtract to obtain
#           duration.
# 
# -----------------------------------------------------------------------------
# 10. BULLET: Assemble the final output dictionary with keys 'crash_ids',
#   'crash_descriptions', 'unexpected_behavior_count', 'successful_run', and
#   'total_duration_seconds', ensuring each matches the defined types.
#   Reason: Produces the structured result required by downstream nodes.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Populate a Python dict with the collected values; cast to appropriate types
#           (e.g., int, bool).
# 
# -----------------------------------------------------------------------------
# 11. BULLET: Clean up the temporary directory (remove crash inputs and logs) unless a
#   debugging flag is set, to conserve disk space.
#   Reason: Prevents accumulation of large log files over multiple runs.
#   Impact: LOW
#   Complexity: LOW
#   Method: Use shutil.rmtree on the temporary path; guard with a debug mode check.
# -- END PRD --



class CollectCurrentOpensslSourceOutput(BaseModel):
    """Pydantic model for collect_current_openssl_source node outputs."""
    repository_url: str = Field(..., description="The URL of the OpenSSL repository that was cloned.")
    clone_path: str = Field(..., description="The absolute or relative path to the local directory where the source was cloned.")
    stable_release_tag: str = Field(..., description="The name of the latest stable release tag that was checked out.")
    commit_hash: str = Field(..., description="The full commit SHA of the source code that was cloned.")
    clone_success: bool = Field(..., description="True if the clone operation completed without errors, otherwise False.")


class SetupFuzzingEnvironmentOutput(BaseModel):
    """Pydantic model for setup_fuzzing_environment node outputs."""
    frameworks_configured: str = Field(..., description="List of fuzzing frameworks configured (e.g., AFL, libFuzzer).")
    seed_files: str = Field(..., description="Paths to the generated initial seed files used for fuzzing.")
    environment_ready: bool = Field(..., description="Indicates whether the fuzzing environment is fully set up and ready to run tests.")
    config_directory: str = Field(..., description="File system path to the directory containing fuzzing configuration files.")


class RunFuzzingOutput(BaseModel):
    """Pydantic model for run_fuzzing node outputs."""
    crash_ids: List[str] = Field(..., description="Identifiers (e.g., hashes) for each crash observed during fuzzing.")
    crash_descriptions: List[str] = Field(..., description="Brief textual description of each crash, including affected function or module.")
    unexpected_behavior_count: int = Field(..., description="Total number of unexpected behaviors (e.g., crashes, hangs, assertion failures) detected.")
    successful_run: bool = Field(..., description="True if fuzzing completed without fatal errors; otherwise False.")
    total_duration_seconds: int = Field(..., description="Total runtime of the fuzzing session in seconds.")


def run_fuzzing(collect_current_openssl_source_input: CollectCurrentOpensslSourceOutput, setup_fuzzing_environment_input: SetupFuzzingEnvironmentOutput, **kwargs) -> RunFuzzingOutput:
    """Perform fuzz testing on the OpenSSL source code by invoking a configured fuzzing framework (e.g., AFL or libFuzzer) on the compiled binaries generated from the cloned source. The process must run for a specified time window, capture all crash inputs and unexpected events, and produce a structured summary of results.

    Args:
        collect_current_openssl_source_input: Input from the 'collect_current_openssl_source' node.
        setup_fuzzing_environment_input: Input from the 'setup_fuzzing_environment' node.
        **kwargs: Additional keyword arguments.

    Returns:
        RunFuzzingOutput: Object containing outputs for this node.
    """
    # Validate environment is ready
    if not setup_fuzzing_environment_input.environment_ready:
        log_error(message="Environment not ready, aborting fuzzing run")
        return RunFuzzingOutput(
            crash_ids=[],
            crash_descriptions=[],
            unexpected_behavior_count=0,
            successful_run=False,
            total_duration_seconds=0
        )
    
    # Select fuzzing framework
    selected_framework: str = select_preferred_framework(frameworks=setup_fuzzing_environment_input.frameworks_configured)
    
    # Construct binary path and verify
    binary_path: str = construct_binary_path(clone_path=collect_current_openssl_source_input.clone_path)
    binary_exists: bool = verify_binary_exists(binary_path=binary_path)
    
    if not binary_exists:
        log_error(message=f"Binary path {binary_path} does not exist")
        return RunFuzzingOutput(
            crash_ids=[],
            crash_descriptions=[],
            unexpected_behavior_count=0,
            successful_run=False,
            total_duration_seconds=0
        )
    
    # Create temporary directory
    temp_directory: str = create_temp_directory(prefix="fuzzing_run")
    
    # Record start time
    start_time: float = get_current_timestamp()
    
    # Launch fuzzing tool
    fuzzing_result: dict = launch_fuzzing_tool(
        framework=selected_framework,
        binary_path=binary_path,
        seed_files=setup_fuzzing_environment_input.seed_files,
        temp_directory=temp_directory,
        timeout_seconds=3600
    )
    
    # Record end time and calculate duration
    end_time: float = get_current_timestamp()
    total_duration: int = calculate_duration_seconds(start_time=start_time, end_time=end_time)
    
    # Parse log file for crashes
    log_file_path: str = get_log_file_path(temp_directory=temp_directory)
    crash_data: dict = parse_crash_data(log_file_path=log_file_path)
    crash_ids: List[str] = crash_data.get("crash_ids", [])
    crash_descriptions: List[str] = crash_data.get("crash_descriptions", [])
    
    # Count unexpected behaviors
    behavior_count: int = count_unexpected_behaviors(log_file_path=log_file_path)
    
    # Determine if run was successful
    run_successful: bool = check_run_success(exit_code=fuzzing_result.get("exit_code", -1))
    
    # Clean up temporary directory
    cleanup_temp_directory(temp_directory=temp_directory, debug_mode=kwargs.get("debug_mode", False))
    
    return RunFuzzingOutput(
        crash_ids=crash_ids,
        crash_descriptions=crash_descriptions,
        unexpected_behavior_count=behavior_count,
        successful_run=run_successful,
        total_duration_seconds=total_duration
    )