from ._integrate_patch.parse_vulnerability_data import parse_vulnerability_data
from ._integrate_patch.retrieve_or_generate_patch import retrieve_or_generate_patch
from ._integrate_patch.apply_patch_to_source import apply_patch_to_source
from ._integrate_patch.compile_patched_source import compile_patched_source
from ._integrate_patch.create_patch_log_entry import create_patch_log_entry

from pydantic import BaseModel, Field
from typing import List


# -- PRD --
# 1. BULLET: Parse the parent node output to extract the list of CVE IDs, descriptions,
#   and severity levels, storing them in a structured in for iteration.
#   Reason: Having a clean, in-memory representation of the vulnerability data enables
#           deterministic patch selection and application.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Use JSON or CSV parsing libraries; create a list of dictionaries with keys
#           'cve_id', 'description', 'severity'.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: For each CVE ID, query the National Vulnerability Database (NVD) or vendor
#   patch repository to locate the official patch file (e.g., a diff or
#   tarball). If no official patch exists, construct a custom fix based on
#   the vulnerability description and CVE CVSS score.
#   Reason: Ensures that the most authoritative fix is applied; custom fixes are
#           fallback for unpatched issues.
#   Impact: HIGH
#   Complexity: HIGH
#   Method: Automate HTTP GET requests to NVD API; parse response for patch URLs; for
#           custom fixes, use a templated patch generator that applies
#           standard mitigations (e.g., disabling vulnerable functions,
#           adding bounds checks).
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Apply the retrieved or generated patch to the OpenSSL source tree using 'git
#   apply' or 'patch -p1', capturing any application errors in a log entry.
#   Reason: Standard patching tools provide reliable application and error reporting.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Execute shell commands via subprocess, redirect stdout/stderr to a log
#           string; record success/failure per CVE.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: After patch application, attempt to compile the affected source files (or the
#   entire project if necessary) using the same build configuration as the
#   downstream build step, and capture the compiler output.
#   Reason: Verification of compilation ensures that the patch does not break the
#           build.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Run 'make -j$(nproc)' or the appropriate build command; parse exit code and
#           compiler warnings/errors; log the result.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: If compilation succeeds, record the CVE ID in 'patched_cve_ids' and increment
#   'patch_success_count'; otherwise, increment 'patch_failure_count' and log
#   the failure details.
#   Reason: Accurate bookkeeping of success/failure is required for downstream metrics
#           and decision making.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Update counters and lists in the in-memory data structure; format log
#           entries with CVE ID and outcome.
# 
# -----------------------------------------------------------------------------
# 6. BULLET: After processing all CVEs, set 'overall_patch_success' to true only if
#   'patch_failure_count' is zero, otherwise false.
#   Reason: Provides a quick boolean indicator for downstream nodes (e.g., hardening
#           flags) to decide whether to proceed.
#   Impact: LOW
#   Complexity: LOW
#   Method: Simple boolean comparison; assign to output field.
# 
# -----------------------------------------------------------------------------
# 7. BULLET: Aggregate all individual log entries into the 'patch_log_entries' list,
#   ensuring each entry includes timestamp, CVE ID, patch source
#   (official/custom), application result, and compilation status.
#   Reason: A detailed log is essential for auditability and debugging.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Use datetime formatting; concatenate strings; store as list.
# 
# -----------------------------------------------------------------------------
# 8. BULLET: Return the final structured output containing 'patched_cve_ids',
#   'patch_success_count', 'patch_failure_count', 'overall_patch_success',
#   and 'patch_log_entries' as per the defined output schema.
#   Reason: Conforms to the downstream node expectations and enables automated
#           consumption.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Serialize the data structure to JSON or pass as a dictionary; ensure type
#           alignment.
# -- END PRD --



class IdentifyKnownVulnerabilitiesOutput(BaseModel):
    """Pydantic model for identify_known_vulnerabilities node outputs."""
    cve_ids: str = Field(..., description="List of CVE identifiers for each identified vulnerability.")
    cve_descriptions: str = Field(..., description="Brief textual description of each CVE.")
    severity_levels: str = Field(..., description="Severity level of each CVE (e.g., Low, Medium, High, Critical).")


class IntegratePatchOutput(BaseModel):
    """Pydantic model for integrate_patch node outputs."""
    patched_cve_ids: List[str] = Field(..., description="List of CVE IDs for which patches were successfully applied.")
    patch_success_count: int = Field(..., description="Number of patches that compiled and were applied without errors.")
    patch_failure_count: int = Field(..., description="Number of patches that failed to compile or apply.")
    overall_patch_success: bool = Field(..., description="True if all patches compiled successfully, False otherwise.")
    patch_log_entries: List[str] = Field(..., description="Log entries capturing the outcome of each patch application attempt.")


def integrate_patch(identify_known_vulnerabilities_input: IdentifyKnownVulnerabilitiesOutput, **kwargs) -> IntegratePatchOutput:
    """Apply fixes for known vulnerabilities to the source code.

    Args:
        identify_known_vulnerabilities_input: Input from the 'identify_known_vulnerabilities' node.
        **kwargs: Additional keyword arguments.

    Returns:
        IntegratePatchOutput: Object containing outputs for this node.
    """
    # Parse the parent node output to extract vulnerability data
    vulnerability_data: List[dict] = parse_vulnerability_data(
        cve_ids=identify_known_vulnerabilities_input.cve_ids,
        descriptions=identify_known_vulnerabilities_input.cve_descriptions,
        severity_levels=identify_known_vulnerabilities_input.severity_levels
    )
    
    # Initialize tracking variables
    patched_cve_ids: List[str] = []
    patch_success_count: int = 0
    patch_failure_count: int = 0
    patch_log_entries: List[str] = []
    
    # Process each CVE
    for vulnerability in vulnerability_data:
        cve_id: str = vulnerability['cve_id']
        description: str = vulnerability['description']
        severity: str = vulnerability['severity']
        
        # Query for official patch or generate custom fix
        patch_info: dict = retrieve_or_generate_patch(
            cve_id=cve_id,
            description=description,
            severity=severity
        )
        
        # Apply the patch to the source tree
        patch_result: dict = apply_patch_to_source(
            patch_data=patch_info['patch_data'],
            patch_source=patch_info['source']
        )
        
        # Attempt compilation to verify patch success
        compilation_result: dict = compile_patched_source(
            build_config=kwargs.get('build_config', 'default')
        )
        
        # Record the outcome
        if patch_result['success'] and compilation_result['success']:
            patched_cve_ids.append(cve_id)
            patch_success_count += 1
        else:
            patch_failure_count += 1
        
        # Create log entry for this CVE
        log_entry: str = create_patch_log_entry(
            cve_id=cve_id,
            patch_source=patch_info['source'],
            patch_result=patch_result,
            compilation_result=compilation_result
        )
        patch_log_entries.append(log_entry)
    
    # Determine overall success
    overall_patch_success: bool = patch_failure_count == 0
    
    return IntegratePatchOutput(
        patched_cve_ids=patched_cve_ids,
        patch_success_count=patch_success_count,
        patch_failure_count=patch_failure_count,
        overall_patch_success=overall_patch_success,
        patch_log_entries=patch_log_entries
    )