from ._apply_hardening_flags.parse_source_root_from_patch_logs import parse_source_root_from_patch_logs
from ._apply_hardening_flags.validate_source_root_exists import validate_source_root_exists
from ._apply_hardening_flags.export_flags_to_environment import export_flags_to_environment
from ._apply_hardening_flags.run_openssl_config_command import run_openssl_config_command
from ._apply_hardening_flags.validate_flags_in_build_files import validate_flags_in_build_files

from pydantic import BaseModel, Field
from typing import List


# -- PRD --
# 1. BULLET: Parse the output of integrate_patch to locate the root directory of the
#   OpenSSL source tree. Search the patch_log_entries list for entries
#   containing the pattern "Applied patch to" and extract the file path
#   prefix; use this prefix as the source root for subsequent operations.
#   Reason: The source tree must be identified before any build configuration can be
#           modified. Parsing patch_log_entries ensures we are working on
#           the exact codebase that received patches.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Implement a regular‑expression parser in Python that scans each log entry
#           for "Applied patch to" and captures the directory path.
#           Validate the existence of the extracted path with
#           os.path.isdir; if multiple paths are found, prioritize the one
#           with the deepest directory depth.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Define a canonical list of hardening flags to be applied. Include
#   -DOPENSSL_NO_ASM, -DOPENSSL_NO_EC, -fstack-protector-strong, -Wextra,
#   -Werror, -fPIE, -pie, and -D_FORTIFY_SOURCE=2. Store this list in a
#   variable named hardening_flags.
#   Reason: A consistent set of flags guarantees reproducible security postures across
#           builds and simplifies downstream verification.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Hard‑code the list as a Python list of strings. Ensure each flag is
#           correctly escaped for shell execution.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Export the hardening flags as environment variables CFLAGS and CXXFLAGS
#   before invoking the OpenSSL configuration script. Concatenate the flags
#   into a single string separated by spaces, then set os.environ['CFLAGS'] =
#   os.environ['CXXFLAGS'] = ' '.join(hardening_flags).
#   Reason: OpenSSL's ./config script inherits compiler flags from the environment,
#           allowing us to inject hardening options without modifying the
#           script itself.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Use Python's os.environ to set the variables. Verify that the values are
#           correctly set by printing os.environ['CFLAGS'] after
#           assignment.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Run the OpenSSL configuration command (./config --prefix=/opt/openssl
#   --openssldir=/opt/openssl) within the source root directory, capturing
#   its stdout and stderr. Ensure the command completes successfully before
#   proceeding.
#   Reason: The configuration step generates Makefiles that incorporate the
#           environment‑supplied flags. Failure to configure indicates a
#           problem with the flag syntax or environment setup.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Execute the command using subprocess.run with capture_output=True,
#           check=True. If a CalledProcessError is raised, log the error
#           and set success to False.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Validate that the flags are present in the generated Makefile or config.h by
#   grepping for each flag string. If any flag is missing, log a warning and
#   set success to False.
#   Reason: Ensures that the build system actually received the hardening options;
#           missing flags could undermine security objectives.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Read the Makefile (e.g., Makefile) and config.h into memory. For each flag
#           in hardening_flags, use the in operator to check presence.
#           Record any missing flags in a list.
# 
# -----------------------------------------------------------------------------
# 6. BULLET: Populate the output fields: flags_applied = hardening_flags, flags_summary =
#   a concatenated sentence describing the applied flags, and success = True
#   if all validation steps passed, otherwise False.
#   Reason: These outputs feed downstream nodes (build_openssl) and provide a clear
#           audit trail for the hardening process.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Construct flags_summary as "Applied hardening flags: {}".format(',
#           '.join(hardening_flags)). Return the three fields as a JSON
#           object.
# -- END PRD --



class IntegratePatchOutput(BaseModel):
    """Pydantic model for integrate_patch node outputs."""
    patched_cve_ids: List[str] = Field(..., description="List of CVE IDs for which patches were successfully applied.")
    patch_success_count: int = Field(..., description="Number of patches that compiled and were applied without errors.")
    patch_failure_count: int = Field(..., description="Number of patches that failed to compile or apply.")
    overall_patch_success: bool = Field(..., description="True if all patches compiled successfully, False otherwise.")
    patch_log_entries: List[str] = Field(..., description="Log entries capturing the outcome of each patch application attempt.")


class ApplyHardeningFlagsOutput(BaseModel):
    """Pydantic model for apply_hardening_flags node outputs."""
    flags_applied: List[str] = Field(..., description="List of compilation flags applied to enable security hardening.")
    flags_summary: str = Field(..., description="Human-readable summary of the applied hardening options.")
    success: bool = Field(..., description="Indicates whether the flags were successfully integrated into the build configuration.")


def apply_hardening_flags(integrate_patch_input: IntegratePatchOutput, **kwargs) -> ApplyHardeningFlagsOutput:
    """Set compilation flags to enhance security.

    Args:
        integrate_patch_input: Input from the 'integrate_patch' node.
        **kwargs: Additional keyword arguments.

    Returns:
        ApplyHardeningFlagsOutput: Object containing outputs for this node.
    """
    # Parse the patch log entries to locate the OpenSSL source root directory
    source_root: str = parse_source_root_from_patch_logs(patch_log_entries=integrate_patch_input.patch_log_entries)
    
    # Validate that the extracted source root exists
    root_exists: bool = validate_source_root_exists(source_root=source_root)
    if not root_exists:
        return ApplyHardeningFlagsOutput(
            flags_applied=[],
            flags_summary="Failed to locate valid OpenSSL source root directory",
            success=False
        )
    
    # Define the canonical hardening flags
    hardening_flags: List[str] = [
        "-DOPENSSL_NO_ASM",
        "-DOPENSSL_NO_EC", 
        "-fstack-protector-strong",
        "-Wextra",
        "-Werror",
        "-fPIE",
        "-pie",
        "-D_FORTIFY_SOURCE=2"
    ]
    
    # Export hardening flags as environment variables
    env_setup_success: bool = export_flags_to_environment(flags=hardening_flags)
    if not env_setup_success:
        return ApplyHardeningFlagsOutput(
            flags_applied=hardening_flags,
            flags_summary="Failed to set environment variables for hardening flags",
            success=False
        )
    
    # Run the OpenSSL configuration command
    config_success: bool = run_openssl_config_command(source_root=source_root)
    if not config_success:
        return ApplyHardeningFlagsOutput(
            flags_applied=hardening_flags,
            flags_summary="OpenSSL configuration command failed",
            success=False
        )
    
    # Validate that flags are present in generated Makefile and config.h
    validation_success: bool = validate_flags_in_build_files(source_root=source_root, flags=hardening_flags)
    
    # Generate flags summary
    flags_summary: str = f"Applied hardening flags: {', '.join(hardening_flags)}"
    
    return ApplyHardeningFlagsOutput(
        flags_applied=hardening_flags,
        flags_summary=flags_summary,
        success=validation_success
    )