from ._load_configuration.locate_config_file_from_environment import locate_config_file_from_environment
from ._load_configuration.verify_file_exists_and_readable import verify_file_exists_and_readable
from ._load_configuration.parse_config_file import parse_config_file
from ._load_configuration.define_config_validation_schema import define_config_validation_schema
from ._load_configuration.validate_config_fields import validate_config_fields
from ._load_configuration.validate_filesystem_paths import validate_filesystem_paths

from pydantic import BaseModel, Field


# -- PRD --
# 1. BULLET: Locate the configuration file using an environment variable set by the
#   setup_environment node (e.g., CONFIG_PATH). Verify the file exists and is
#   readable before proceeding.
#   Reason: Ensures the workflow starts with a valid source of configuration and avoids
#           file-not-found errors later.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Use pathlib.Path to check existence and read permissions; if missing,
#           record a descriptive error.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Parse the configuration file as YAML or JSON into a Python dictionary,
#   catching and reporting any syntax errors.
#   Reason: Parsing errors can lead to silent failures; capturing them early improves
#           debuggability.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Employ `yaml.safe_load` for YAML or `json.load` for JSON; use try/except
#           blocks to capture `YAMLError` or `JSONDecodeError`.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Define a schema for required fields (max_epochs, batch_size, learning_rate,
#   data_path, model_output_path, config_version, project_name) with their
#   expected types and acceptable ranges.
#   Reason: A schema centralizes validation logic and ensures consistency across runs.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Create a dictionary mapping field names to validation lambdas or use
#           jsonschema for declarative validation.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Validate each required field against the schema: check presence, type, and
#   logical constraints (e.g., epochs > 0, learning_rate > 0, paths are
#   absolute). Collect any violations into the error_messages list.
#   Reason: Field-level validation guarantees that downstream nodes receive well-formed
#           data.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Iterate over schema entries; for each field, apply lambda; append
#           descriptive messages for failures.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Validate filesystem paths: ensure data_path exists and is readable, and
#   model_output_path is writable (create directory if it doesn't exist).
#   Record path-related errors.
#   Reason: Runtime errors during training often stem from missing or inaccessible
#           paths; pre-empting them avoids costly failures.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Use pathlib to check `is_file()` or `exists()` and `is_dir()`. Attempt to
#           create output directory with `mkdir(parents=True,
#           exist_ok=True)`; catch PermissionError.
# 
# -----------------------------------------------------------------------------
# 6. BULLET: Determine the overall configuration validity: set config_valid to True only
#   if no error_messages were recorded; otherwise False.
#   Reason: A clear validity flag simplifies downstream decision logic.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Set `config_valid = len(error_messages) == 0`.
# 
# -----------------------------------------------------------------------------
# 7. BULLET: If config_valid is true, extract validated values into the corresponding
#   output fields; otherwise, populate numeric fields with None or default
#   sentinel values.
#   Reason: Consistent output structure is required for downstream nodes regardless of
#           validation outcome.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Use dictionary lookups; for missing keys in error case, assign None or 0
#           and document the decision in the log.
# 
# -----------------------------------------------------------------------------
# 8. BULLET: Return a structured JSON object containing all output fields, ensuring each
#   matches the declared PrimitiveType and includes a clear description of
#   any defaulted or error values.
#   Reason: Strict type adherence guarantees compatibility with the typed workflow
#           engine.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Serialize a dict with keys matching output_structure; validate types before
#           returning.
# -- END PRD --



class SetupEnvironmentOutput(BaseModel):
    """Pydantic model for setup_environment node outputs."""
    environment_ready: bool = Field(..., description="Whether the environment was set up successfully.")
    installed_packages: str = Field(..., description="List of package names that were installed during setup.")
    installed_package_versions: str = Field(..., description="Corresponding package versions for installed packages.")
    configured_paths: str = Field(..., description="List of system paths that were configured (e.g., PATH, PYTHONPATH).")
    environment_variables: str = Field(..., description="List of environment variable names that were set.")
    setup_log: str = Field(..., description="A log string summarizing the setup process.")


class LoadConfigurationOutput(BaseModel):
    """Pydantic model for load_configuration node outputs."""
    config_valid: bool = Field(..., description="Whether the configuration passed validation checks")
    error_messages: str = Field(..., description="List of validation error messages, empty if config_valid is true")
    max_epochs: int = Field(..., description="Number of training epochs specified in the configuration")
    batch_size: int = Field(..., description="Batch size for training specified in the configuration")
    learning_rate: float = Field(..., description="Learning rate for optimizer as specified in the configuration")
    data_path: str = Field(..., description="File system path to the training data")
    model_output_path: str = Field(..., description="File system path where the trained model checkpoints will be stored")
    config_version: str = Field(..., description="Version identifier for the configuration file")
    project_name: str = Field(..., description="Name of the project as defined in the configuration")


def load_configuration(setup_environment_input: SetupEnvironmentOutput, **kwargs) -> LoadConfigurationOutput:
    """Read and validate project configuration.

    Args:
        setup_environment_input: Input from the 'setup_environment' node.
        **kwargs: Additional keyword arguments.

    Returns:
        LoadConfigurationOutput: Object containing outputs for this node.
    """
    # Locate and verify configuration file
    config_file_path: str = locate_config_file_from_environment()
    file_accessible: bool = verify_file_exists_and_readable(path=config_file_path)
    
    error_messages = []
    
    if not file_accessible:
        error_messages.append("Configuration file not found or not readable")
        return LoadConfigurationOutput(
            config_valid=False,
            error_messages=", ".join(error_messages),
            max_epochs=0,
            batch_size=0,
            learning_rate=0.0,
            data_path="",
            model_output_path="",
            config_version="",
            project_name=""
        )
    
    # Parse configuration file
    config_dict: dict = parse_config_file(file_path=config_file_path, error_list=error_messages)
    
    if not config_dict:
        return LoadConfigurationOutput(
            config_valid=False,
            error_messages=", ".join(error_messages),
            max_epochs=0,
            batch_size=0,
            learning_rate=0.0,
            data_path="",
            model_output_path="",
            config_version="",
            project_name=""
        )
    
    # Define validation schema
    validation_schema: dict = define_config_validation_schema()
    
    # Validate required fields against schema
    validate_config_fields(config_dict=config_dict, schema=validation_schema, error_list=error_messages)
    
    # Validate filesystem paths
    validate_filesystem_paths(config_dict=config_dict, error_list=error_messages)
    
    # Determine overall configuration validity
    config_valid: bool = len(error_messages) == 0
    
    # Extract validated values or use defaults
    if config_valid:
        max_epochs: int = config_dict.get("max_epochs", 0)
        batch_size: int = config_dict.get("batch_size", 0)
        learning_rate: float = config_dict.get("learning_rate", 0.0)
        data_path: str = config_dict.get("data_path", "")
        model_output_path: str = config_dict.get("model_output_path", "")
        config_version: str = config_dict.get("config_version", "")
        project_name: str = config_dict.get("project_name", "")
    else:
        max_epochs = 0
        batch_size = 0
        learning_rate = 0.0
        data_path = ""
        model_output_path = ""
        config_version = ""
        project_name = ""
    
    return LoadConfigurationOutput(
        config_valid=config_valid,
        error_messages=", ".join(error_messages),
        max_epochs=max_epochs,
        batch_size=batch_size,
        learning_rate=learning_rate,
        data_path=data_path,
        model_output_path=model_output_path,
        config_version=config_version,
        project_name=project_name
    )