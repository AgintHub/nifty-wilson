from ._run_dynamic_tests.validate_environment_setup import validate_environment_setup
from ._run_dynamic_tests.log_environment_error import log_environment_error
from ._run_dynamic_tests.change_directory_to_source_root import change_directory_to_source_root
from ._run_dynamic_tests.execute_test_binary import execute_test_binary
from ._run_dynamic_tests.parse_test_output import parse_test_output
from ._run_dynamic_tests.extract_failed_test_cases import extract_failed_test_cases
from ._run_dynamic_tests.extract_crash_logs import extract_crash_logs
from ._run_dynamic_tests.generate_test_summary import generate_test_summary

from pydantic import BaseModel, Field


# -- PRD --
# 1. BULLET: Validate that the dynamic testing environment was successfully set up by
#   checking the `environment_setup_success` flag from
#   `setup_dynamic_testing_environment` and ensuring the `test_binary_path`
#   points to an existing executable.
#   Reason: Early validation prevents wasted effort if the environment is
#           misconfigured.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Read the JSON output of `setup_dynamic_testing_environment`; if
#           `environment_setup_success` is false or `test_binary_path` does
#           not exist, abort and log an error.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Navigate to the cloned OpenSSL source root directory using the `clone_path`
#   from `collect_current_openssl_source`.
#   Reason: All test binaries are relative to the source root, so correct path context
#           is essential.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Execute `cd <clone_path>` in a shell; capture the working directory for
#           subsequent commands.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Execute the test suite by running the compiled test binary located at
#   `test_binary_path` with appropriate flags (e.g., `./test -v` for verbose
#   output). Capture both stdout and stderr into temporary files.
#   Reason: Running the test binary directly ensures that all unit and integration
#           tests are executed as intended.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Use `subprocess.run` in Python or a shell script to invoke
#           `<test_binary_path> -v`; redirect output to `test_output.txt`
#           and `test_error.txt`.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Parse the test output to compute `total_tests_run`, `tests_passed`,
#   `tests_failed`, and `crash_count` using regular expressions that match
#   patterns like "[PASS]", "[FAIL]", and "[CRASH]".
#   Reason: Accurate counting is required to populate the PRD fields correctly.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Read `test_output.txt`; for each line, if it contains "[PASS]" increment
#           `tests_passed`; if "[FAIL]" increment `tests_failed` and record
#           the test identifier; if "[CRASH]" increment `crash_count` and
#           capture the crash log snippet.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Aggregate the failed test identifiers into the `failed_test_cases` list and
#   collect crash log excerpts into the `crash_logs` list.
#   Reason: These lists provide detailed failure diagnostics for the security report.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Append each failed test name to a Python list; for crashes, store the
#           relevant lines from `test_error.txt` that contain stack traces
#           or error messages.
# 
# -----------------------------------------------------------------------------
# 6. BULLET: Construct a concise `test_summary` string that includes the total number of
#   tests, pass/fail ratio, and crash count, formatted for readability.
#   Reason: A summary enables quick assessment of test health without sifting through
#           logs.
#   Impact: LOW
#   Complexity: LOW
#   Method: Use string formatting: "Ran {total} tests: {passed} passed, {failed}
#           failed, {crashes} crashes."
# -- END PRD --



class CollectCurrentOpensslSourceOutput(BaseModel):
    """Pydantic model for collect_current_openssl_source node outputs."""
    repository_url: str = Field(..., description="The URL of the OpenSSL repository that was cloned.")
    clone_path: str = Field(..., description="The absolute or relative path to the local directory where the source was cloned.")
    stable_release_tag: str = Field(..., description="The name of the latest stable release tag that was checked out.")
    commit_hash: str = Field(..., description="The full commit SHA of the source code that was cloned.")
    clone_success: bool = Field(..., description="True if the clone operation completed without errors, otherwise False.")


class SetupDynamicTestingEnvironmentOutput(BaseModel):
    """Pydantic model for setup_dynamic_testing_environment node outputs."""
    environment_setup_success: bool = Field(..., description="Indicates whether the environment was set up successfully.")
    installed_packages: str = Field(..., description="List of package names that were installed as part of the setup.")
    config_file_path: str = Field(..., description="Path to the configuration file generated for testing.")
    test_binary_path: str = Field(..., description="Path to the compiled test binaries.")
    environment_variables: str = Field(..., description="List of environment variable assignments used during testing.")


class RunDynamicTestsOutput(BaseModel):
    """Pydantic model for run_dynamic_tests node outputs."""
    total_tests_run: int = Field(..., description="Total number of tests executed.")
    tests_passed: int = Field(..., description="Number of tests that passed.")
    tests_failed: int = Field(..., description="Number of tests that failed.")
    crash_count: int = Field(..., description="Number of crashes observed during testing.")
    failed_test_cases: str = Field(..., description="List of identifiers or names of tests that failed.")
    crash_logs: str = Field(..., description="List of crash log excerpts or identifiers.")
    test_summary: str = Field(..., description="Brief summary of test results.")


def run_dynamic_tests(collect_current_openssl_source_input: CollectCurrentOpensslSourceOutput, setup_dynamic_testing_environment_input: SetupDynamicTestingEnvironmentOutput, **kwargs) -> RunDynamicTestsOutput:
    """Execute dynamic tests on the OpenSSL source code.

    Args:
        collect_current_openssl_source_input: Input from the 'collect_current_openssl_source' node.
        setup_dynamic_testing_environment_input: Input from the 'setup_dynamic_testing_environment' node.
        **kwargs: Additional keyword arguments.

    Returns:
        RunDynamicTestsOutput: Object containing outputs for this node.
    """
    # Validate environment setup and test binary path
    validation_result: bool = validate_environment_setup(
        environment_success=setup_dynamic_testing_environment_input.environment_setup_success,
        test_binary_path=setup_dynamic_testing_environment_input.test_binary_path
    )
    
    if not validation_result:
        log_environment_error(error="Environment validation failed")
        return RunDynamicTestsOutput(
            total_tests_run=0,
            tests_passed=0,
            tests_failed=0,
            crash_count=0,
            failed_test_cases="Environment setup failed",
            crash_logs="",
            test_summary="Test execution aborted due to environment issues"
        )
    
    # Navigate to source root directory
    working_directory: str = change_directory_to_source_root(
        clone_path=collect_current_openssl_source_input.clone_path
    )
    
    # Execute test suite and capture output
    test_execution_result: dict = execute_test_binary(
        test_binary_path=setup_dynamic_testing_environment_input.test_binary_path,
        working_directory=working_directory
    )
    
    # Parse test output for counts and results
    test_counts: dict = parse_test_output(
        stdout_content=test_execution_result["stdout"],
        stderr_content=test_execution_result["stderr"]
    )
    
    # Aggregate failed test cases
    failed_tests: list = extract_failed_test_cases(
        test_output=test_execution_result["stdout"]
    )
    
    # Collect crash logs
    crash_log_excerpts: list = extract_crash_logs(
        stderr_content=test_execution_result["stderr"]
    )
    
    # Generate test summary
    summary: str = generate_test_summary(
        total_tests=test_counts["total"],
        passed_tests=test_counts["passed"],
        failed_tests=test_counts["failed"],
        crash_count=test_counts["crashes"]
    )
    
    return RunDynamicTestsOutput(
        total_tests_run=test_counts["total"],
        tests_passed=test_counts["passed"],
        tests_failed=test_counts["failed"],
        crash_count=test_counts["crashes"],
        failed_test_cases=", ".join(failed_tests),
        crash_logs="\n".join(crash_log_excerpts),
        test_summary=summary
    )