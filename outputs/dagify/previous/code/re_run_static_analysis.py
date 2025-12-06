from ._re_run_static_analysis.validate_environment_ready import validate_environment_ready
from ._re_run_static_analysis.verify_binary_artifacts import verify_binary_artifacts
from ._re_run_static_analysis.locate_compile_commands import locate_compile_commands
from ._re_run_static_analysis.run_clang_tidy import run_clang_tidy
from ._re_run_static_analysis.run_cppcheck import run_cppcheck
from ._re_run_static_analysis.parse_clang_tidy_warnings import parse_clang_tidy_warnings
from ._re_run_static_analysis.parse_clang_tidy_errors import parse_clang_tidy_errors
from ._re_run_static_analysis.extract_clang_security_findings import extract_clang_security_findings
from ._re_run_static_analysis.parse_cppcheck_warnings import parse_cppcheck_warnings
from ._re_run_static_analysis.parse_cppcheck_errors import parse_cppcheck_errors
from ._re_run_static_analysis.extract_cppcheck_security_findings import extract_cppcheck_security_findings
from ._re_run_static_analysis.merge_security_findings import merge_security_findings
from ._re_run_static_analysis.generate_static_analysis_report import generate_static_analysis_report
from ._re_run_static_analysis.serialize_security_findings import serialize_security_findings

from pydantic import BaseModel, Field


# -- PRD --
# 1. BULLET: Validate that the static analysis environment is fully prepared by checking
#   the `environment_ready` flag from the `setup_static_analysis_environment`
#   node. If the flag is false, abort the run and log an error indicating
#   missing tools or misconfiguration.
#   Reason: Ensures that clang-tidy and cppcheck are installed and configured correctly
#           before execution, preventing false negatives and wasted
#           compute.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Read the `environment_ready` boolean from the parent node’s output; if
#           false, raise an exception and terminate the task.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Retrieve the path to the compiled OpenSSL binaries from the `build_openssl`
#   node’s `binary_artifacts_path` output. Verify that the directory exists
#   and contains at least one executable or shared library.
#   Reason: Static analysis tools operate on compiled artifacts; locating them
#           correctly is essential for accurate analysis.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Use filesystem API to confirm existence of `binary_artifacts_path`; list
#           files and filter for `.so`, `.dll`, `.exe`, or ELF binaries.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Run clang-tidy on each binary artifact by invoking `clang-tidy -p
#   <compile_commands.json> <binary>` and capture its stdout and stderr.
#   Store the raw output in a temporary file for later parsing.
#   Reason: clang-tidy provides fine‑grained linting and security checks; its output
#           includes warnings, errors, and potential vulnerabilities.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Generate or locate `compile_commands.json` in the build directory; loop
#           over binaries, execute clang-tidy via subprocess, redirect
#           output to `clang_tidy.log`.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Run cppcheck on the same set of binaries using `cppcheck --enable=all --xml
#   <binary> 2> cppcheck.xml`. Parse the XML to extract warnings, errors, and
#   security issues (e.g., `CWE` tags).
#   Reason: cppcheck complements clang-tidy by detecting a broader range of C/C++
#           issues, including memory leaks and buffer overflows.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Execute cppcheck via subprocess, redirect XML output to `cppcheck.xml`; use
#           an XML parser to count `<error>` and `<warning>` elements and
#           extract CWE identifiers.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Aggregate the results from clang-tidy and cppcheck: sum the warning counts,
#   sum the error counts, and merge the security finding lists while
#   eliminating duplicates.
#   Reason: Combining outputs from both tools yields a comprehensive view of static
#           analysis results.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Read the temporary log files, use regular expressions to count occurrences,
#           and append findings to a set to deduplicate.
# 
# -----------------------------------------------------------------------------
# 6. BULLET: Determine `analysis_passed` by evaluating whether `errors_count` is zero and
#   `security_findings` is empty. If either condition fails, set
#   `analysis_passed` to false; otherwise true.
#   Reason: Provides a clear pass/fail indicator for downstream processes such as the
#           security report generation.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Simple boolean logic: `analysis_passed = (errors_count == 0) and
#           (len(security_findings) == 0)`.
# 
# -----------------------------------------------------------------------------
# 7. BULLET: Generate a structured static analysis report file in JSON format at a
#   predefined location (e.g., `reports/static_analysis_report.json`).
#   Include all output fields (`warnings_count`, `errors_count`,
#   `security_findings`, `analysis_passed`, `report_path`).
#   Reason: Persisting the report enables traceability, auditability, and consumption
#           by downstream nodes such as `generate_security_report`.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Create a dictionary with the output fields, serialize to JSON, and write to
#           disk; set `report_path` to the file’s absolute path.
# 
# -----------------------------------------------------------------------------
# 8. BULLET: Return the populated output fields (`warnings_count`, `errors_count`,
#   `security_findings`, `analysis_passed`, `report_path`) as the node’s
#   result, ensuring they match the defined output structure types.
#   Reason: Conforms to the DAG’s contract, allowing dependent nodes to consume the
#           data without type mismatches.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Construct a response object with the exact keys and types, and emit it via
#           the workflow engine’s API.
# -- END PRD --



class BuildOpensslOutput(BaseModel):
    """Pydantic model for build_openssl node outputs."""
    binary_artifacts_path: str = Field(..., description="Filesystem path to the directory containing compiled OpenSSL binaries.")
    build_success: bool = Field(..., description="Indicates whether the build completed without errors.")
    build_log: str = Field(..., description="Textual log of the build process.")
    artifact_names: str = Field(..., description="List of names of generated binary artifacts (e.g., libssl.so, libcrypto.so).")
    build_duration_seconds: int = Field(..., description="Total time taken for the build in seconds.")


class SetupStaticAnalysisEnvironmentOutput(BaseModel):
    """Pydantic model for setup_static_analysis_environment node outputs."""
    installed_tools: str = Field(..., description="Names of static analysis tools installed in the environment.")
    configuration_success: bool = Field(..., description="Whether the configuration of the tools succeeded without errors.")
    environment_ready: bool = Field(..., description="Indicates if the environment is fully ready for static code analysis runs.")


class ReRunStaticAnalysisOutput(BaseModel):
    """Pydantic model for re_run_static_analysis node outputs."""
    warnings_count: int = Field(..., description="Number of warnings identified by the static analysis tools.")
    errors_count: int = Field(..., description="Number of errors identified by the static analysis tools.")
    security_findings: str = Field(..., description="List of security-related findings or vulnerabilities reported.")
    analysis_passed: bool = Field(..., description="True if no critical errors or security findings were detected; otherwise False.")
    report_path: str = Field(..., description="File path to the generated static analysis report document.")


def re_run_static_analysis(build_openssl_input: BuildOpensslOutput, setup_static_analysis_environment_input: SetupStaticAnalysisEnvironmentOutput, **kwargs) -> ReRunStaticAnalysisOutput:
    """Re-run static analysis on the built OpenSSL binaries, capturing warnings, errors, and security findings, and produce a detailed report.

    Args:
        build_openssl_input: Input from the 'build_openssl' node.
        setup_static_analysis_environment_input: Input from the 'setup_static_analysis_environment' node.
        **kwargs: Additional keyword arguments.

    Returns:
        ReRunStaticAnalysisOutput: Object containing outputs for this node.
    """
    # Validate that the static analysis environment is ready
    validate_environment_ready(environment_ready=setup_static_analysis_environment_input.environment_ready)
    
    # Verify binary artifacts path exists and contains executables
    binary_files: list = verify_binary_artifacts(binary_path=build_openssl_input.binary_artifacts_path)
    
    # Generate or locate compile_commands.json for clang-tidy
    compile_commands_path: str = locate_compile_commands(build_path=build_openssl_input.binary_artifacts_path)
    
    # Run clang-tidy on binary artifacts
    clang_tidy_output: str = run_clang_tidy(binaries=binary_files, compile_commands=compile_commands_path)
    
    # Run cppcheck on binary artifacts
    cppcheck_output: str = run_cppcheck(binaries=binary_files)
    
    # Parse clang-tidy results
    clang_warnings: int = parse_clang_tidy_warnings(output=clang_tidy_output)
    clang_errors: int = parse_clang_tidy_errors(output=clang_tidy_output)
    clang_security_findings: list = extract_clang_security_findings(output=clang_tidy_output)
    
    # Parse cppcheck results
    cpp_warnings: int = parse_cppcheck_warnings(xml_output=cppcheck_output)
    cpp_errors: int = parse_cppcheck_errors(xml_output=cppcheck_output)
    cpp_security_findings: list = extract_cppcheck_security_findings(xml_output=cppcheck_output)
    
    # Aggregate results from both tools
    total_warnings: int = clang_warnings + cpp_warnings
    total_errors: int = clang_errors + cpp_errors
    combined_security_findings: list = merge_security_findings(clang_findings=clang_security_findings, cpp_findings=cpp_security_findings)
    
    # Determine if analysis passed
    analysis_passed: bool = (total_errors == 0) and (len(combined_security_findings) == 0)
    
    # Generate structured report in JSON format
    report_file_path: str = generate_static_analysis_report(
        warnings_count=total_warnings,
        errors_count=total_errors,
        security_findings=combined_security_findings,
        analysis_passed=analysis_passed
    )
    
    # Convert security findings list to string for output model
    security_findings_str: str = serialize_security_findings(findings=combined_security_findings)
    
    return ReRunStaticAnalysisOutput(
        warnings_count=total_warnings,
        errors_count=total_errors,
        security_findings=security_findings_str,
        analysis_passed=analysis_passed,
        report_path=report_file_path
    )