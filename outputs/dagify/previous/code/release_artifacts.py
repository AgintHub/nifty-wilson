from ._release_artifacts.get_build_openssl_artifacts_path import get_build_openssl_artifacts_path
from ._release_artifacts.verify_directory_exists import verify_directory_exists
from ._release_artifacts.get_stable_release_tag import get_stable_release_tag
from ._release_artifacts.construct_tarball_path import construct_tarball_path
from ._release_artifacts.verify_file_exists import verify_file_exists
from ._release_artifacts.create_staging_directory import create_staging_directory
from ._release_artifacts.copy_binaries_to_staging import copy_binaries_to_staging
from ._release_artifacts.list_binary_files import list_binary_files
from ._release_artifacts.copy_source_tarball_to_staging import copy_source_tarball_to_staging
from ._release_artifacts.create_docs_staging_directory import create_docs_staging_directory
from ._release_artifacts.copy_documentation_to_staging import copy_documentation_to_staging
from ._release_artifacts.create_release_package import create_release_package
from ._release_artifacts.generate_release_tag import generate_release_tag
from ._release_artifacts.create_git_tag import create_git_tag
from ._release_artifacts.push_git_tag import push_git_tag
from ._release_artifacts.format_file_list_as_string import format_file_list_as_string

from pydantic import BaseModel, Field
from typing import List


# -- PRD --
# 1. BULLET: Retrieve the path to the compiled OpenSSL binaries from the build_openssl
#   output (stored in the environment or a known artifact directory) and
#   verify its existence.
#   Reason: The binaries are the core deliverable; ensuring they are present prevents
#           downstream packaging failures.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Use a file system check (e.g., os.path.isdir) and read the
#           binary_artifacts_path from the build_openssl artifact store.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Obtain the source tarball path from the collect_current_openssl_source output
#   (clone_path + "openssl-" + stable_release_tag + ".tar.gz") and confirm
#   the tarball exists.
#   Reason: Including the exact source code version is required for reproducibility and
#           compliance.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Construct the expected tarball filename using the stable_release_tag and
#           verify with os.path.isfile.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Gather the documentation files from the document_changes output:
#   changelog_entries, readme_updates, documentation_changes, and
#   security_findings_summary; copy them into a documentation directory
#   within the staging area.
#   Reason: All documentation updates must be bundled to reflect the applied patches
#           and hardening measures.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Create a temporary docs folder, write each entry to appropriate files
#           (e.g., CHANGELOG.md, README.md, INSTALL.md), and include
#           security_findings_summary as SECURITY.md.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Create a staging directory (e.g., /tmp/openssl_release_<timestamp>) and copy
#   the binaries, source tarball, and documentation into subdirectories
#   (bin/, src/, docs/).
#   Reason: Organizing artifacts in a clean layout simplifies archiving and version
#           control tagging.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Use shutil.copytree or rsync to replicate the directory structure, ensuring
#           permissions are preserved.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Package the staged directory into a compressed archive (e.g.,
#   openssl-<version>.tar.gz) and store the path in artifact_package_path.
#   Reason: A single archive is the standard distribution format for OpenSSL releases.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Invoke tar or zip via subprocess, handling errors and capturing the full
#           path.
# 
# -----------------------------------------------------------------------------
# 6. BULLET: Determine the release tag based on the stable_release_tag and the current
#   date (e.g., v<stable_release_tag>-release-<YYYYMMDD>) and create the tag
#   in the git repository using git tag -a.
#   Reason: A unique, descriptive tag is essential for traceability and downstream
#           consumption.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Use git command line via subprocess, and capture any output or errors.
# 
# -----------------------------------------------------------------------------
# 7. BULLET: Push the new tag to the remote repository (git push origin <tag>) and verify
#   the push succeeded.
#   Reason: Remote tagging makes the release visible to all stakeholders and CI
#           pipelines.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Execute git push and check the return code; log any failures.
# 
# -----------------------------------------------------------------------------
# 8. BULLET: Populate the output fields: artifact_package_path, release_tag,
#   documentation_files (list of docs copied), binary_files (list of binaries
#   copied), and set build_success to true if all previous steps succeeded,
#   otherwise false.
#   Reason: The downstream nodes require these structured outputs to continue the
#           workflow.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Aggregate paths and flags into a JSON object, handling exceptions to set
#           build_success appropriately.
# -- END PRD --



class DocumentChangesOutput(BaseModel):
    """Pydantic model for document_changes node outputs."""
    changelog_entries: List[str] = Field(..., description="Lines added to the changelog reflecting applied patches and hardening measures.")
    readme_updates: List[str] = Field(..., description="Sections of the README that were updated to include new security information.")
    documentation_changes: List[str] = Field(..., description="Other documentation files (e.g., INSTALL, CONTRIBUTING) that were modified.")
    applied_patches: List[str] = Field(..., description="List of CVE IDs for which patches were applied.")
    hardening_flags: List[str] = Field(..., description="Compilation hardening flags used in the build.")
    security_findings_summary: str = Field(..., description="Summary of security findings extracted from the security report.")
    document_changes_success: bool = Field(..., description="Indicates whether the documentation update process completed successfully.")


class ReleaseArtifactsOutput(BaseModel):
    """Pydantic model for release_artifacts node outputs."""
    artifact_package_path: str = Field(..., description="File system path to the packaged release artifacts.")
    release_tag: str = Field(..., description="The version control tag assigned to this release.")
    documentation_files: str = Field(..., description="List of documentation files included in the release.")
    binary_files: str = Field(..., description="List of binary files included in the release.")
    build_success: bool = Field(..., description="Indicates whether the packaging and tagging succeeded.")


def release_artifacts(document_changes_input: DocumentChangesOutput, **kwargs) -> ReleaseArtifactsOutput:
    """Prepare and publish the final OpenSSL release by bundling binaries, source, and documentation, then creating a version control tag.

    Args:
        document_changes_input: Input from the 'document_changes' node.
        **kwargs: Additional keyword arguments.

    Returns:
        ReleaseArtifactsOutput: Object containing outputs for this node.
    """
    # Retrieve and verify compiled OpenSSL binaries path
    binary_artifacts_path: str = get_build_openssl_artifacts_path()
    binaries_exist: bool = verify_directory_exists(path=binary_artifacts_path)
    
    if not binaries_exist:
        return ReleaseArtifactsOutput(
            artifact_package_path="",
            release_tag="",
            documentation_files="",
            binary_files="",
            build_success=False,
        )
    
    # Obtain and verify source tarball path
    stable_release_tag: str = get_stable_release_tag()
    source_tarball_path: str = construct_tarball_path(tag=stable_release_tag)
    tarball_exists: bool = verify_file_exists(path=source_tarball_path)
    
    if not tarball_exists:
        return ReleaseArtifactsOutput(
            artifact_package_path="",
            release_tag="",
            documentation_files="",
            binary_files="",
            build_success=False,
        )
    
    # Create staging directory with timestamp
    staging_directory: str = create_staging_directory()
    
    # Copy binaries to staging area
    binary_staging_path: str = copy_binaries_to_staging(source=binary_artifacts_path, staging_dir=staging_directory)
    binary_files_list: List[str] = list_binary_files(path=binary_staging_path)
    
    # Copy source tarball to staging area
    copy_source_tarball_to_staging(source=source_tarball_path, staging_dir=staging_directory)
    
    # Create documentation directory and copy documentation files
    docs_staging_path: str = create_docs_staging_directory(staging_dir=staging_directory)
    documentation_files_list: List[str] = copy_documentation_to_staging(
        changelog_entries=document_changes_input.changelog_entries,
        readme_updates=document_changes_input.readme_updates,
        documentation_changes=document_changes_input.documentation_changes,
        security_findings_summary=document_changes_input.security_findings_summary,
        docs_dir=docs_staging_path
    )
    
    # Package staging directory into compressed archive
    package_path: str = create_release_package(staging_dir=staging_directory, version=stable_release_tag)
    package_success: bool = verify_file_exists(path=package_path)
    
    if not package_success:
        return ReleaseArtifactsOutput(
            artifact_package_path="",
            release_tag="",
            documentation_files="",
            binary_files="",
            build_success=False,
        )
    
    # Create release tag based on stable_release_tag and current date
    release_tag: str = generate_release_tag(base_tag=stable_release_tag)
    tag_created: bool = create_git_tag(tag=release_tag)
    
    if not tag_created:
        return ReleaseArtifactsOutput(
            artifact_package_path=package_path,
            release_tag="",
            documentation_files="",
            binary_files="",
            build_success=False,
        )
    
    # Push tag to remote repository
    push_success: bool = push_git_tag(tag=release_tag)
    
    if not push_success:
        return ReleaseArtifactsOutput(
            artifact_package_path=package_path,
            release_tag=release_tag,
            documentation_files="",
            binary_files="",
            build_success=False,
        )
    
    # Format output lists as strings
    formatted_docs: str = format_file_list_as_string(files=documentation_files_list)
    formatted_binaries: str = format_file_list_as_string(files=binary_files_list)
    
    # Return successful output with all artifacts
    return ReleaseArtifactsOutput(
        artifact_package_path=package_path,
        release_tag=release_tag,
        documentation_files=formatted_docs,
        binary_files=formatted_binaries,
        build_success=True,
    )