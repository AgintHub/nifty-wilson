from ._verify_build_security.prepare_binary_artifact_path import prepare_binary_artifact_path
from ._verify_build_security.verify_path_accessible import verify_path_accessible
from ._verify_build_security.select_scanner_tool import select_scanner_tool
from ._verify_build_security.construct_scanner_command import construct_scanner_command
from ._verify_build_security.execute_scanner_subprocess import execute_scanner_subprocess
from ._verify_build_security.parse_scanner_output import parse_scanner_output
from ._verify_build_security.extract_vulnerability_ids import extract_vulnerability_ids
from ._verify_build_security.evaluate_security_passed import evaluate_security_passed
from ._verify_build_security.format_vulnerability_ids_as_string import format_vulnerability_ids_as_string
from ._verify_build_security.validate_output_schema import validate_output_schema

from pydantic import BaseModel, Field


# -- PRD --
# 1. BULLET: Prepare the binary artifact path from the parent node build_openssl by
#   reading its output field binary_artifacts_path, ensuring the path is
#   absolute and accessible by the scanner environment.
#   Reason: The scanner needs a concrete filesystem location to analyze; using the
#           parent’s output guarantees consistency and avoids hard‑coding
#           paths.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Read the JSON output of build_openssl, extract binary_artifacts_path,
#           resolve relative paths using the working directory, and verify
#           file existence with a filesystem check.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Select a primary scanner tool (e.g., Snyk) and optionally a secondary tool
#   (e.g., OPA) based on the project's security policy, then construct the
#   corresponding CLI command with appropriate flags for binary scanning.
#   Reason: Having a deterministic selection process ensures reproducibility and
#           compliance with policy.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Define a configuration mapping of tool names to command templates; inject
#           the binary path and any required authentication tokens.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Execute the scanner command in a subprocess, capturing stdout, stderr, and
#   the exit code, and enforce a timeout to prevent hanging scans.
#   Reason: Subprocess execution isolates the scanner, while capturing outputs enables
#           downstream parsing.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Use Python’s subprocess.run with capture_output=True, text=True, and a
#           timeout parameter; log the raw output for audit.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Parse the scanner’s JSON or text report to extract the total vulnerability
#   count and a list of vulnerability identifiers (CVE IDs or internal IDs).
#   Reason: The raw output format varies per tool; robust parsing ensures accurate
#           mapping to the required output fields.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: If JSON, load with json.loads; if text, use regex patterns to find CVE IDs
#           and count entries; handle pagination or multiple sections.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Determine the security_passed flag by evaluating the severity of each
#   identified vulnerability; if any severity is marked Critical or High, set
#   security_passed to False, else True.
#   Reason: The business rule requires a binary pass/fail outcome based on criticality.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Map severity strings to a numeric ranking; iterate over the list of
#           vulnerabilities, checking their severity field.
# 
# -----------------------------------------------------------------------------
# 6. BULLET: Construct the final output JSON object with keys scan_tool_used,
#   vulnerability_count, vulnerability_ids, and security_passed, ensuring
#   type compliance (e.g., int, list of strings, bool).
#   Reason: The downstream nodes expect a strict schema; type correctness prevents
#           integration failures.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Populate a Python dict with the extracted values, cast to the correct
#           types, and serialize with json.dumps.
# 
# -----------------------------------------------------------------------------
# 7. BULLET: Validate the output against a JSON schema (matching the output_structure) and
#   log any schema violations before returning the result.
#   Reason: Schema validation catches accidental mismatches early, improving
#           reliability.
#   Impact: LOW
#   Complexity: LOW
#   Method: Use jsonschema.validate with the defined schema; capture ValidationError
#           exceptions and include details in the log.
# -- END PRD --



class BuildOpensslOutput(BaseModel):
    """Pydantic model for build_openssl node outputs."""
    binary_artifacts_path: str = Field(..., description="Filesystem path to the directory containing compiled OpenSSL binaries.")
    build_success: bool = Field(..., description="Indicates whether the build completed without errors.")
    build_log: str = Field(..., description="Textual log of the build process.")
    artifact_names: str = Field(..., description="List of names of generated binary artifacts (e.g., libssl.so, libcrypto.so).")
    build_duration_seconds: int = Field(..., description="Total time taken for the build in seconds.")


class VerifyBuildSecurityOutput(BaseModel):
    """Pydantic model for verify_build_security node outputs."""
    scan_tool_used: str = Field(..., description="Name of the security scanner tool used (e.g., OPA, Snyk).")
    vulnerability_count: int = Field(..., description="Total number of vulnerabilities found by the scanner.")
    vulnerability_ids: str = Field(..., description="List of CVE IDs or internal identifiers for each detected vulnerability.")
    security_passed: bool = Field(..., description="True if no critical vulnerabilities were found; otherwise False.")


def verify_build_security(build_openssl_input: BuildOpensslOutput, **kwargs) -> VerifyBuildSecurityOutput:
    """Validate the security of the built binaries.

    Args:
        build_openssl_input: Input from the 'build_openssl' node.
        **kwargs: Additional keyword arguments.

    Returns:
        VerifyBuildSecurityOutput: Object containing outputs for this node.
    """
    # Prepare the binary artifact path from parent node output
    absolute_binary_path: str = prepare_binary_artifact_path(
        binary_artifacts_path=build_openssl_input.binary_artifacts_path
    )
    
    # Verify path accessibility
    verify_path_accessible(path=absolute_binary_path)
    
    # Select scanner tool and construct CLI command
    selected_tool: str = select_scanner_tool(security_policy=kwargs.get('security_policy', 'default'))
    scanner_command: list = construct_scanner_command(
        tool_name=selected_tool,
        binary_path=absolute_binary_path,
        auth_tokens=kwargs.get('auth_tokens', {})
    )
    
    # Execute scanner command with subprocess
    scan_result: dict = execute_scanner_subprocess(
        command=scanner_command,
        timeout=kwargs.get('scan_timeout', 300)
    )
    
    # Parse scanner output to extract vulnerabilities
    parsed_vulnerabilities: list = parse_scanner_output(
        raw_output=scan_result['stdout'],
        tool_name=selected_tool
    )
    
    # Extract vulnerability count and IDs
    vuln_count: int = len(parsed_vulnerabilities)
    vuln_ids: list = extract_vulnerability_ids(vulnerabilities=parsed_vulnerabilities)
    
    # Determine security_passed based on severity evaluation
    security_passed: bool = evaluate_security_passed(
        vulnerabilities=parsed_vulnerabilities
    )
    
    # Convert vulnerability IDs list to string format
    vuln_ids_str: str = format_vulnerability_ids_as_string(vulnerability_ids=vuln_ids)
    
    # Validate output against schema
    output_data: dict = {
        'scan_tool_used': selected_tool,
        'vulnerability_count': vuln_count,
        'vulnerability_ids': vuln_ids_str,
        'security_passed': security_passed
    }
    
    validate_output_schema(output_data=output_data)
    
    return VerifyBuildSecurityOutput(
        scan_tool_used=selected_tool,
        vulnerability_count=vuln_count,
        vulnerability_ids=vuln_ids_str,
        security_passed=security_passed
    )