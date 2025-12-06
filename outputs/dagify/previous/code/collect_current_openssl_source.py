from ._collect_current_openssl_source.validate_git_installation import validate_git_installation
from ._collect_current_openssl_source.validate_network_connectivity import validate_network_connectivity
from ._collect_current_openssl_source.create_temporary_directory import create_temporary_directory
from ._collect_current_openssl_source.clone_repository import clone_repository
from ._collect_current_openssl_source.cleanup_directory import cleanup_directory
from ._collect_current_openssl_source.fetch_all_tags import fetch_all_tags
from ._collect_current_openssl_source.get_repository_tags import get_repository_tags
from ._collect_current_openssl_source.find_latest_stable_tag import find_latest_stable_tag
from ._collect_current_openssl_source.checkout_tag import checkout_tag
from ._collect_current_openssl_source.get_commit_hash import get_commit_hash
from ._collect_current_openssl_source.log_error import log_error

from pydantic import BaseModel, Field


# -- PRD --
# 1. BULLET: Validate the execution environment by checking that Git is installed and the
#   network can reach the OpenSSL repository URL (e.g.,
#   https://github.com/openssl/openssl).
#   Reason: Ensures that subsequent clone operations will not fail due to missing tools
#           or network issues.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Use `git --version` to confirm Git availability; perform a DNS lookup or a
#           simple `curl -I` request to the repository URL to verify
#           connectivity. Log any failures and abort with `clone_success =
#           False` if the checks fail.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Create a temporary working directory (e.g., /tmp/openssl_clone_<timestamp>)
#   and clone the repository into it using `git clone <repository_url>
#   <clone_path>`.
#   Reason: Isolates the source retrieval from other system files and provides a clean
#           workspace.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Use `os.makedirs` with `exist_ok=True` to create the directory, then invoke
#           `subprocess.run(['git', 'clone', repository_url, clone_path],
#           check=True, capture_output=True)` to perform the clone. Capture
#           any errors to set `clone_success` appropriately.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Retrieve all tags from the cloned repository and determine the latest stable
#   release tag by filtering tags that match the semantic version pattern
#   `v[0-9]+.[0-9]+.[0-9]+` and selecting the highest version.
#   Reason: OpenSSL stable releases follow a semantic versioning scheme; selecting the
#           most recent ensures the source is up‑to‑date.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Run `git fetch --tags` to ensure all tags are present. Use `git tag` to
#           list tags, then apply a regex to filter semantic versions. Sort
#           the filtered list using `packaging.version.parse` (or similar)
#           to compare versions, and pick the maximum as
#           `stable_release_tag`. Handle cases where no matching tag is
#           found by logging an error and setting `clone_success = False`.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Checkout the identified stable release tag using `git checkout
#   tags/<stable_release_tag>` to ensure the working tree reflects the exact
#   commit of that release.
#   Reason: Guarantees that the source code corresponds to the stable tag rather than
#           the default branch.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Execute `subprocess.run(['git', 'checkout', f'tags/{stable_release_tag}'],
#           cwd=clone_path, check=True, capture_output=True)`. Verify the
#           checkout succeeded by checking the return code.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Obtain the full commit SHA of the checked‑out source using `git rev-parse
#   HEAD` and store it as `commit_hash`.
#   Reason: Provides an immutable identifier for the exact source state, useful for
#           reproducibility.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Run `subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=clone_path,
#           check=True, capture_output=True, text=True)` and strip the
#           output to get the SHA.
# 
# -----------------------------------------------------------------------------
# 6. BULLET: Populate the output fields `repository_url`, `clone_path`,
#   `stable_release_tag`, `commit_hash`, and set `clone_success` to True if
#   all previous steps succeeded without exceptions.
#   Reason: Ensures the node returns a well‑defined, typed payload for downstream
#           consumers.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Wrap the entire process in a try/except block; on success, assign the
#           collected values to a dictionary matching the output schema. On
#           any exception, log the error, set `clone_success = False`, and
#           populate the remaining fields with `None` or empty strings as
#           appropriate.
# 
# -----------------------------------------------------------------------------
# 7. BULLET: If `clone_success` is False, clean up the temporary directory to avoid
#   orphaned files on the filesystem.
#   Reason: Prevents disk clutter and potential security issues from incomplete clones.
#   Impact: LOW
#   Complexity: LOW
#   Method: Use `shutil.rmtree(clone_path, ignore_errors=True)` to delete the directory
#           when the clone operation failed.
# -- END PRD --



class CollectCurrentOpensslSourceOutput(BaseModel):
    """Pydantic model for collect_current_openssl_source node outputs."""
    repository_url: str = Field(..., description="The URL of the OpenSSL repository that was cloned.")
    clone_path: str = Field(..., description="The absolute or relative path to the local directory where the source was cloned.")
    stable_release_tag: str = Field(..., description="The name of the latest stable release tag that was checked out.")
    commit_hash: str = Field(..., description="The full commit SHA of the source code that was cloned.")
    clone_success: bool = Field(..., description="True if the clone operation completed without errors, otherwise False.")


def collect_current_openssl_source(general_input: str, **kwargs) -> CollectCurrentOpensslSourceOutput:
    """Fetch the most recent OpenSSL source code from the official repository.

    Args:
        general_input: General input string for the root node.
        **kwargs: Additional keyword arguments.

    Returns:
        CollectCurrentOpensslSourceOutput: Object containing outputs for this node.
    """
    try:
        # Validate execution environment
        git_available: bool = validate_git_installation()
        repository_url: str = "https://github.com/openssl/openssl"
        network_reachable: bool = validate_network_connectivity(url=repository_url)
        
        if not git_available or not network_reachable:
            return CollectCurrentOpensslSourceOutput(
                repository_url=repository_url,
                clone_path="",
                stable_release_tag="",
                commit_hash="",
                clone_success=False,
            )
        
        # Create temporary working directory and clone repository
        clone_path: str = create_temporary_directory(prefix="openssl_clone")
        clone_result: bool = clone_repository(repository_url=repository_url, clone_path=clone_path)
        
        if not clone_result:
            cleanup_directory(path=clone_path)
            return CollectCurrentOpensslSourceOutput(
                repository_url=repository_url,
                clone_path="",
                stable_release_tag="",
                commit_hash="",
                clone_success=False,
            )
        
        # Fetch tags and determine latest stable release
        fetch_all_tags(clone_path=clone_path)
        all_tags: list = get_repository_tags(clone_path=clone_path)
        stable_release_tag: str = find_latest_stable_tag(tags=all_tags)
        
        if not stable_release_tag:
            cleanup_directory(path=clone_path)
            return CollectCurrentOpensslSourceOutput(
                repository_url=repository_url,
                clone_path="",
                stable_release_tag="",
                commit_hash="",
                clone_success=False,
            )
        
        # Checkout the stable release tag
        checkout_success: bool = checkout_tag(clone_path=clone_path, tag=stable_release_tag)
        
        if not checkout_success:
            cleanup_directory(path=clone_path)
            return CollectCurrentOpensslSourceOutput(
                repository_url=repository_url,
                clone_path="",
                stable_release_tag="",
                commit_hash="",
                clone_success=False,
            )
        
        # Get commit hash
        commit_hash: str = get_commit_hash(clone_path=clone_path)
        
        return CollectCurrentOpensslSourceOutput(
            repository_url=repository_url,
            clone_path=clone_path,
            stable_release_tag=stable_release_tag,
            commit_hash=commit_hash,
            clone_success=True,
        )
        
    except Exception as e:
        log_error(error=e, context="collect_current_openssl_source")
        if 'clone_path' in locals():
            cleanup_directory(path=clone_path)
        
        return CollectCurrentOpensslSourceOutput(
            repository_url=repository_url if 'repository_url' in locals() else "",
            clone_path="",
            stable_release_tag="",
            commit_hash="",
            clone_success=False,
        )