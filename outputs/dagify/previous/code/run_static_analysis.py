from ._run_static_analysis.validate_environment_prerequisites import validate_environment_prerequisites
from ._run_static_analysis.run_clang_tidy import run_clang_tidy
from ._run_static_analysis.run_cppcheck import run_cppcheck
from ._run_static_analysis.parse_clang_tidy_log import parse_clang_tidy_log
from ._run_static_analysis.parse_cppcheck_xml import parse_cppcheck_xml
from ._run_static_analysis.sort_issues_by_filename import sort_issues_by_filename
from ._run_static_analysis.determine_analysis_success import determine_analysis_success
from ._run_static_analysis.generate_analysis_report import generate_analysis_report
from ._run_static_analysis.format_issues_as_string import format_issues_as_string

from pydantic import BaseModel, Field


# -- PRD --
# 1. BULLET: Validate that the OpenSSL source tree is present at the path provided by
#   collect_current_openssl_source (clone_path) and that the analysis
#   environment is ready (environment_ready) before proceeding.
#   Reason: Ensures that the analysis tools have a valid source repository and a
#           correctly configured environment, preventing runtime errors.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Read clone_path from parent output; read environment_ready from
#           setup_static_analysis_environment; if false, abort with error
#           log.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Run clang-tidy on the entire source tree with the default OpenSSL coding
#   standards configuration, capturing its stdout and stderr streams to
#   temporary files.
#   Reason: clang-tidy provides detailed linting and potential security checks;
#           capturing streams allows later parsing.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Execute `clang-tidy -p build -j$(nproc) $(find . -name '*.c' -or -name
#           '*.cpp')`; redirect output to clang_tidy.log.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Run cppcheck on the same source tree using the `--enable=all` flag and
#   `--xml` output mode, directing the XML result to a separate file.
#   Reason: cppcheck complements clang-tidy by detecting a broader range of bugs and
#           potential security issues.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Execute `cppcheck --enable=all --xml --xml-version=2 . 2> cppcheck.xml`.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Parse clang_tidy.log to extract warnings and errors, normalizing each entry
#   into the format "file:line:column: severity: message" and populate
#   warnings_list and errors_list accordingly.
#   Reason: Standardized format simplifies downstream aggregation and reporting.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Use a regex pattern to match lines; filter by severity (warning/error);
#           append to respective lists.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Parse cppcheck.xml to extract warnings, errors, and security findings,
#   converting each XML element into a human‑readable string and adding them
#   to warnings_list, errors_list, and security_issues_list.
#   Reason: cppcheck’s XML output provides structured data that can be accurately
#           mapped to the required lists.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Use an XML parser (e.g., lxml) to iterate over <error> elements; extract
#           attributes (file, line, severity) and message; classify based
#           on severity.
# 
# -----------------------------------------------------------------------------
# 6. BULLET: Count the total number of warnings, errors, and security issues across both
#   tools and store the results in total_warnings, total_errors, and
#   total_security_issues.
#   Reason: Aggregated counts provide quick metrics for the security report.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Use len(warnings_list), len(errors_list), len(security_issues_list).
# 
# -----------------------------------------------------------------------------
# 7. BULLET: Determine analysis_success by checking that both clang-tidy and cppcheck exit
#   with code 0 and that no unexpected fatal errors were encountered during
#   parsing.
#   Reason: A boolean success flag simplifies downstream decision‑making in
#           generate_security_report.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Capture exit codes; if both are 0 and parsing succeeded, set
#           analysis_success = true.
# 
# -----------------------------------------------------------------------------
# 8. BULLET: Generate a comprehensive static analysis report file (e.g.,
#   analysis_report.md) that includes sections for warnings, errors, security
#   findings, and overall summary, and write its path to
#   analysis_report_path.
#   Reason: A human‑readable report aids developers in triaging issues.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Create markdown content with tables; write to file; store absolute path.
# 
# -----------------------------------------------------------------------------
# 9. BULLET: Return all output fields as defined in the output_structure, ensuring that
#   each list is sorted alphabetically by file name for consistency.
#   Reason: Consistent ordering makes downstream consumption deterministic.
#   Impact: LOW
#   Complexity: LOW
#   Method: Sort warnings_list, errors_list, security_issues_list before returning.
# -- END PRD --



class CollectCurrentOpensslSourceOutput(BaseModel):
    """Pydantic model for collect_current_openssl_source node outputs."""
    repository_url: str = Field(..., description="The URL of the OpenSSL repository that was cloned.")
    clone_path: str = Field(..., description="The absolute or relative path to the local directory where the source was cloned.")
    stable_release_tag: str = Field(..., description="The name of the latest stable release tag that was checked out.")
    commit_hash: str = Field(..., description="The full commit SHA of the source code that was cloned.")
    clone_success: bool = Field(..., description="True if the clone operation completed without errors, otherwise False.")


class SetupStaticAnalysisEnvironmentOutput(BaseModel):
    """Pydantic model for setup_static_analysis_environment node outputs."""
    installed_tools: str = Field(..., description="Names of static analysis tools installed in the environment.")
    configuration_success: bool = Field(..., description="Whether the configuration of the tools succeeded without errors.")
    environment_ready: bool = Field(..., description="Indicates if the environment is fully ready for static code analysis runs.")


class RunStaticAnalysisOutput(BaseModel):
    """Pydantic model for run_static_analysis node outputs."""
    total_warnings: int = Field(..., description="Total number of warnings detected by the static analysis tools.")
    total_errors: int = Field(..., description="Total number of errors detected by the static analysis tools.")
    total_security_issues: int = Field(..., description="Total number of potential security issues identified.")
    warnings_list: str = Field(..., description="List of warning messages with file names and line numbers.")
    errors_list: str = Field(..., description="List of error messages with file names and line numbers.")
    security_issues_list: str = Field(..., description="List of security issue descriptions with file names and line numbers.")
    analysis_success: bool = Field(..., description="Indicates whether the static analysis completed without fatal failures.")
    analysis_report_path: str = Field(..., description="File system path to the generated static analysis report file.")


def run_static_analysis(collect_current_openssl_source_input: CollectCurrentOpensslSourceOutput, setup_static_analysis_environment_input: SetupStaticAnalysisEnvironmentOutput, **kwargs) -> RunStaticAnalysisOutput:
    """Perform static analysis on the OpenSSL source code.

    Args:
        collect_current_openssl_source_input: Input from the 'collect_current_openssl_source' node.
        setup_static_analysis_environment_input: Input from the 'setup_static_analysis_environment' node.
        **kwargs: Additional keyword arguments.

    Returns:
        RunStaticAnalysisOutput: Object containing outputs for this node.
    """
    # Validate prerequisites before proceeding
    validate_environment_prerequisites(
        clone_path=collect_current_openssl_source_input.clone_path,
        environment_ready=setup_static_analysis_environment_input.environment_ready
    )
    
    # Run clang-tidy on the source tree
    clang_tidy_exit_code: int = run_clang_tidy(
        source_path=collect_current_openssl_source_input.clone_path,
        output_file="clang_tidy.log"
    )
    
    # Run cppcheck on the source tree
    cppcheck_exit_code: int = run_cppcheck(
        source_path=collect_current_openssl_source_input.clone_path,
        output_file="cppcheck.xml"
    )
    
    # Parse clang-tidy log file to extract warnings and errors
    clang_warnings: list = []
    clang_errors: list = []
    parse_clang_tidy_log(
        log_file="clang_tidy.log",
        warnings_list=clang_warnings,
        errors_list=clang_errors
    )
    
    # Parse cppcheck XML to extract warnings, errors, and security issues
    cppcheck_warnings: list = []
    cppcheck_errors: list = []
    cppcheck_security: list = []
    parse_cppcheck_xml(
        xml_file="cppcheck.xml",
        warnings_list=cppcheck_warnings,
        errors_list=cppcheck_errors,
        security_issues_list=cppcheck_security
    )
    
    # Combine results from both tools
    all_warnings: list = clang_warnings + cppcheck_warnings
    all_errors: list = clang_errors + cppcheck_errors
    all_security_issues: list = cppcheck_security
    
    # Sort results alphabetically by file name for consistency
    sorted_warnings: list = sort_issues_by_filename(issues_list=all_warnings)
    sorted_errors: list = sort_issues_by_filename(issues_list=all_errors)
    sorted_security: list = sort_issues_by_filename(issues_list=all_security_issues)
    
    # Count totals
    total_warnings_count: int = len(sorted_warnings)
    total_errors_count: int = len(sorted_errors)
    total_security_count: int = len(sorted_security)
    
    # Determine analysis success based on tool exit codes
    analysis_success_flag: bool = determine_analysis_success(
        clang_tidy_exit_code=clang_tidy_exit_code,
        cppcheck_exit_code=cppcheck_exit_code
    )
    
    # Generate comprehensive analysis report
    report_path: str = generate_analysis_report(
        warnings=sorted_warnings,
        errors=sorted_errors,
        security_issues=sorted_security,
        total_warnings=total_warnings_count,
        total_errors=total_errors_count,
        total_security=total_security_count
    )
    
    # Convert lists to formatted strings
    warnings_string: str = format_issues_as_string(issues_list=sorted_warnings)
    errors_string: str = format_issues_as_string(issues_list=sorted_errors)
    security_string: str = format_issues_as_string(issues_list=sorted_security)
    
    return RunStaticAnalysisOutput(
        total_warnings=total_warnings_count,
        total_errors=total_errors_count,
        total_security_issues=total_security_count,
        warnings_list=warnings_string,
        errors_list=errors_string,
        security_issues_list=security_string,
        analysis_success=analysis_success_flag,
        analysis_report_path=report_path
    )