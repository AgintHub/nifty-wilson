from ._document_changes.validate_security_report_data import validate_security_report_data
from ._document_changes.format_changelog_entries import format_changelog_entries
from ._document_changes.identify_readme_sections import identify_readme_sections
from ._document_changes.create_readme_updates import create_readme_updates
from ._document_changes.update_documentation_files import update_documentation_files
from ._document_changes.compile_applied_patches import compile_applied_patches
from ._document_changes.extract_hardening_flags import extract_hardening_flags
from ._document_changes.generate_security_findings_summary import generate_security_findings_summary
from ._document_changes.write_documentation_changes import write_documentation_changes
from ._document_changes.validate_write_operations import validate_write_operations
from ._document_changes.log_error_details import log_error_details

from pydantic import BaseModel, Field
from typing import List


# -- PRD --
# 1. BULLET: Collect all relevant data from the generate_security_report node's output
#   fields (applied_patches, hardening_measures, security_issues_list,
#   overall_recommendations, risk_rating).
#   Reason: The documentation update requires a comprehensive view of what was fixed,
#           which hardening was applied, and what security findings remain.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Read the JSON payload of generate_security_report, map each field to a
#           local variable, and perform validation (e.g., ensure lists are
#           not empty).
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Generate changelog_entries by formatting each applied patch and hardening
#   measure into a standard changelog entry (e.g., "[CVE-2023-1234] Fixed
#   memory corruption; added -fstack-protector-strong flag").
#   Reason: A consistent changelog format aids traceability and downstream tooling.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Iterate over applied_patches and hardening_flags, concatenate strings with
#           appropriate prefixes, and store the result in
#           changelog_entries.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Identify README sections that need updates (e.g., SECURITY, HACKING, INSTALL)
#   by scanning the current README for headings using regex patterns.
#   Reason: Targeted updates prevent unnecessary modifications and preserve existing
#           content.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Load README.md, apply regex r'^(##+)\s*(SECURITY|INSTALL|HACKING)\s*$' to
#           capture relevant sections.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Create readme_updates entries by inserting security findings summary and
#   hardening flag notes into the identified sections, preserving original
#   formatting.
#   Reason: Ensures that users are aware of critical security changes without breaking
#           README syntax.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Use a templating engine (e.g., Jinja2) to replace placeholders or append
#           text after the section header.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: For each documentation file listed in documentation_changes (e.g., INSTALL,
#   CONTRIBUTING), locate the file, read its contents, and append a brief
#   note summarizing applied patches and hardening flags.
#   Reason: Maintains consistency across all project documentation.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Iterate over file paths, open each file in append mode, and write a
#           formatted note.
# 
# -----------------------------------------------------------------------------
# 6. BULLET: Compile applied_patches list directly from
#   generate_security_report.applied_patches, ensuring no duplicates and
#   sorting alphabetically.
#   Reason: A clean list is required for downstream release notes and artifact
#           packaging.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Convert to a set to remove duplicates, then sort.
# 
# -----------------------------------------------------------------------------
# 7. BULLET: Compile hardening_flags list by extracting
#   generate_security_report.hardening_measures, filtering for compiler flag
#   patterns (e.g., stringsfstack-protector-strong'), and normalizing syntax.
#   Reason: Clear flag listing assists developers and auditors.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Use string matching or regex to isolate flag tokens.
# 
# -----------------------------------------------------------------------------
# 8. BULLET: Generate security_findings_summary by concatenating the first sentence of
#   each entry in generate_security_report.static_analysis_findings and
#   dynamic_test_results, prefixed with "Static analysis: " and "Dynamic
#   tests: ".
#   Reason: Provides a concise overview for README and release notes.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Parse lists, extract first sentences, and format.
# 
# -----------------------------------------------------------------------------
# 9. BULLET: Write all generated entries back to the appropriate files: prepend
#   changelog_entries to CHANGELOG.md, insert readme_updates into README.md,
#   and write documentation_changes notes to their respective files.
#   Reason: Persisting changes ensures the repository reflects the latest security
#           posture.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Use file I/O with atomic write operations (e.g., write to temp file then
#           rename) to avoid corruption.
# 
# -----------------------------------------------------------------------------
# 10. BULLET: Validate that all write operations succeeded by checking file existence, file
#   size > 0, and optionally computing a SHA-256 checksum before and after
#   writing.
#   Reason: Guarantees the integrity of the documentation update process.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Use os.path.exists, os.path.getsize, and hashlib.sha256.
# 
# -----------------------------------------------------------------------------
# 11. BULLET: Set document_changes_success flag to true if all validations pass; otherwise
#   set to false and log detailed error messages for each failed step.
#   Reason: Clear success indicator for downstream nodes (e.g., release_artifacts).
#   Impact: HIGH
#   Complexity: LOW
#   Method: Wrap the entire process in a try/except block and update the flag
#           accordingly.
# -- END PRD --



class GenerateSecurityReportOutput(BaseModel):
    """Pydantic model for generate_security_report node outputs."""
    identified_issues: str = Field(..., description="List of identified security issues, including CVE IDs and brief descriptions.")
    applied_patches: str = Field(..., description="List of applied patches or fixes, identified by CVE IDs or patch names.")
    hardening_measures: str = Field(..., description="List of hardening options applied, such as compiler flags and configuration settings.")
    static_analysis_findings: str = Field(..., description="Summary of findings from static analysis, including warnings and errors.")
    dynamic_test_results: str = Field(..., description="Outcome of dynamic tests, e.g., 'all tests passed', '3 failures', etc.")
    fuzzing_crashes: int = Field(..., description="Number of crashes detected during fuzz testing.")
    overall_recommendations: str = Field(..., description="Recommendations for future maintenance and mitigation.")
    risk_rating: str = Field(..., description="Overall risk rating of the build (e.g., Low, Medium, High).")


class DocumentChangesOutput(BaseModel):
    """Pydantic model for document_changes node outputs."""
    changelog_entries: List[str] = Field(..., description="Lines added to the changelog reflecting applied patches and hardening measures.")
    readme_updates: List[str] = Field(..., description="Sections of the README that were updated to include new security information.")
    documentation_changes: List[str] = Field(..., description="Other documentation files (e.g., INSTALL, CONTRIBUTING) that were modified.")
    applied_patches: List[str] = Field(..., description="List of CVE IDs for which patches were applied.")
    hardening_flags: List[str] = Field(..., description="Compilation hardening flags used in the build.")
    security_findings_summary: str = Field(..., description="Summary of security findings extracted from the security report.")
    document_changes_success: bool = Field(..., description="Indicates whether the documentation update process completed successfully.")


def document_changes(generate_security_report_input: GenerateSecurityReportOutput, **kwargs) -> DocumentChangesOutput:
    """Document all changes made to the OpenSSL project.

    Args:
        generate_security_report_input: Input from the 'generate_security_report' node.
        **kwargs: Additional keyword arguments.

    Returns:
        DocumentChangesOutput: Object containing outputs for this node.
    """
    try:
        # Collect and validate all relevant data from security report
        validated_data: dict = validate_security_report_data(security_report=generate_security_report_input)
        
        # Generate changelog entries from applied patches and hardening measures
        changelog_entries: List[str] = format_changelog_entries(
            patches=validated_data['applied_patches'],
            hardening=validated_data['hardening_measures']
        )
        
        # Identify README sections that need updates using regex patterns
        readme_sections: List[str] = identify_readme_sections(readme_path="README.md")
        
        # Create readme updates with security findings and hardening notes
        readme_updates: List[str] = create_readme_updates(
            sections=readme_sections,
            security_findings=validated_data['static_analysis_findings'],
            hardening_flags=validated_data['hardening_measures']
        )
        
        # Update documentation files with security summary notes
        documentation_changes: List[str] = update_documentation_files(
            patches=validated_data['applied_patches'],
            hardening_flags=validated_data['hardening_measures']
        )
        
        # Compile clean applied patches list without duplicates
        applied_patches_clean: List[str] = compile_applied_patches(
            patches=validated_data['applied_patches']
        )
        
        # Extract and normalize hardening flags from measures
        hardening_flags_clean: List[str] = extract_hardening_flags(
            measures=validated_data['hardening_measures']
        )
        
        # Generate security findings summary from static and dynamic results
        security_findings_summary: str = generate_security_findings_summary(
            static_findings=validated_data['static_analysis_findings'],
            dynamic_results=validated_data['dynamic_test_results']
        )
        
        # Write all generated entries back to appropriate files
        write_success: bool = write_documentation_changes(
            changelog_entries=changelog_entries,
            readme_updates=readme_updates,
            documentation_changes=documentation_changes
        )
        
        # Validate that all write operations succeeded
        validation_success: bool = validate_write_operations(
            files=['CHANGELOG.md', 'README.md'] + documentation_changes
        )
        
        # Set success flag based on all operations
        document_changes_success: bool = write_success and validation_success
        
    except Exception as e:
        # Log error and set failure state
        log_error_details(error=e, operation="document_changes")
        document_changes_success = False
        changelog_entries = []
        readme_updates = []
        documentation_changes = []
        applied_patches_clean = []
        hardening_flags_clean = []
        security_findings_summary = ""
    
    return DocumentChangesOutput(
        changelog_entries=changelog_entries,
        readme_updates=readme_updates,
        documentation_changes=documentation_changes,
        applied_patches=applied_patches_clean,
        hardening_flags=hardening_flags_clean,
        security_findings_summary=security_findings_summary,
        document_changes_success=document_changes_success,
    )