from ._initialize_model_weights.validate_architecture_config import validate_architecture_config
from ._initialize_model_weights.create_model_from_architecture import create_model_from_architecture
from ._initialize_model_weights.determine_initialization_strategy import determine_initialization_strategy
from ._initialize_model_weights.apply_weight_initialization import apply_weight_initialization
from ._initialize_model_weights.calculate_trainable_parameters import calculate_trainable_parameters
from ._initialize_model_weights.generate_architecture_signature import generate_architecture_signature
from ._initialize_model_weights.log_initialization_error import log_initialization_error

from pydantic import BaseModel, Field


# -- PRD --
# 1. BULLET: Retrieve the architecture configuration from the `define_model_architecture`
#   output, ensuring that all required fields (model_type, number_of_layers,
#   hidden_size, attention_heads, vocab_size, max_sequence_length,
#   total_parameters) are present and valid.
#   Reason: The initialization routine must be informed of the exact architecture to
#           construct the model correctly. Missing or malformed inputs
#           would cause construction failures or inconsistent parameter
#           counts.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Read the JSON payload from the parent node; perform type validation and
#           range checks (e.g., positive integers for sizes).
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Instantiate the model using a framework‑agnostic factory (e.g., a custom
#   `ModelBuilder` that accepts the architecture dict and returns a PyTorch
#   `nn.Module` or TensorFlow `tf.keras.Model`).
#   Reason: Abstracting the model construction decouples initialization from the
#           underlying deep learning library, facilitating future swaps or
#           extensions.
#   Impact: HIGH
#   Complexity: HIGH
#   Method: Implement a mapping from `model_type` to a builder class; within the
#           builder, create transformer layers with the specified hidden
#           size, attention heads, and positional embeddings; use the vocab
#           size for the embedding matrix.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Determine the initialization strategy by inspecting a configuration flag
#   (e.g., `use_pretrained`, `pretrained_path`) that may be passed via an
#   optional environment variable or a separate config node; default to
#   Xavier/Glorot uniform if no pretrained weights are provided.
#   Reason: Choosing an appropriate strategy ensures good convergence behaviour; using
#           pretrained weights can drastically reduce training time and
#           improve final performance.
#   Impact: MEDIUM
#   Complexity: MEDIUM
#   Method: Parse environment variables with a fallback; if `pretrained_path` exists,
#           load state_dict from that path; otherwise apply Xavier
#           initialization to all linear and embedding layers.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Apply the chosen initialization across all trainable parameters: for each
#   module, if it is a `Linear`, `Conv1D`, or `Embedding`, invoke the
#   corresponding weight initialization function; for biases,
#   zero‑initialize.
#   Reason: Uniformly initializing all parameters avoids biasing the network and
#           promotes symmetric learning dynamics.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Iterate over `model.modules()`; use `torch.nn.init.xavier_uniform_` for
#           weights and `torch.nn.init.zeros_` for biases; wrap in a
#           try/except to catch any unsupported module types.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Calculate the total number of trainable parameters by summing the `numel()`
#   of every parameter with `requires_grad=True` in the model.
#   Reason: Providing an accurate parameter count is essential for logging, debugging,
#           and ensuring that the model matches the architecture
#           specification.
#   Impact: LOW
#   Complexity: LOW
#   Method: Use a generator expression: `sum(p.numel() for p in model.parameters() if
#           p.requires_grad)`.
# 
# -----------------------------------------------------------------------------
# 6. BULLET: Generate a deterministic `architecture_signature` by serializing the sorted
#   architecture dictionary into a JSON string and hashing it with SHA‑256.
#   Reason: The signature serves as a unique fingerprint of the model configuration,
#           useful for versioning, caching, and ensuring reproducibility.
#   Impact: LOW
#   Complexity: LOW
#   Method: Serialize with `json.dumps(arch_dict, sort_keys=True)`; compute hash via
#           `hashlib.sha256()`; encode as hex string.
# 
# -----------------------------------------------------------------------------
# 7. BULLET: Return the output bundle with `initialization_success=True` if all steps
#   complete without unhandled exceptions; otherwise set to `False` and
#   provide a meaningful error message in the logs.
#   Reason: Explicit success flag enables downstream nodes to conditionally proceed or
#           trigger fallback workflows.
#   Impact: LOW
#   Complexity: LOW
#   Method: Wrap the entire initialization in a try/except; on exception, log the
#           traceback and set success flag to False.
# -- END PRD --



class DefineModelArchitectureOutput(BaseModel):
    """Pydantic model for define_model_architecture node outputs."""
    model_type: str = Field(..., description="Name or type of the model architecture (e.g., 'Transformer').")
    number_of_layers: int = Field(..., description="Total number of transformer layers in the model.")
    hidden_size: int = Field(..., description="Dimensionality of each transformer hidden layer.")
    attention_heads: int = Field(..., description="Number of attention heads per transformer layer.")
    vocab_size: int = Field(..., description="Size of the vocabulary derived from the tokenized data.")
    max_sequence_length: int = Field(..., description="Maximum token sequence length supported by the model.")
    total_parameters: int = Field(..., description="Estimated total number of trainable parameters in the model.")


class InitializeModelWeightsOutput(BaseModel):
    """Pydantic model for initialize_model_weights node outputs."""
    initialization_success: bool = Field(..., description="Whether the weight initialization completed successfully")
    num_parameters: int = Field(..., description="Total number of trainable parameters in the model")
    initialization_method: str = Field(..., description="Method used for weight initialization (e.g., 'random', 'xavier', 'pretrained')")
    architecture_signature: str = Field(..., description="Hash or unique string representing the model architecture configuration")


def initialize_model_weights(define_model_architecture_input: DefineModelArchitectureOutput, **kwargs) -> InitializeModelWeightsOutput:
    """Initialize the weights of the defined model architecture.

    Args:
        define_model_architecture_input: Input from the 'define_model_architecture' node.
        **kwargs: Additional keyword arguments.

    Returns:
        InitializeModelWeightsOutput: Object containing outputs for this node.
    """
    try:
        # Validate architecture configuration
        validated_config: dict = validate_architecture_config(architecture=define_model_architecture_input)
        
        # Instantiate the model using framework-agnostic factory
        model = create_model_from_architecture(config=validated_config)
        
        # Determine initialization strategy from config/environment
        init_strategy: str = determine_initialization_strategy(**kwargs)
        
        # Apply chosen initialization across all trainable parameters
        apply_weight_initialization(model=model, strategy=init_strategy)
        
        # Calculate total number of trainable parameters
        total_params: int = calculate_trainable_parameters(model=model)
        
        # Generate deterministic architecture signature
        signature: str = generate_architecture_signature(config=validated_config)
        
        return InitializeModelWeightsOutput(
            initialization_success=True,
            num_parameters=total_params,
            initialization_method=init_strategy,
            architecture_signature=signature
        )
        
    except Exception as e:
        # Log error and return failure state
        log_initialization_error(error=e)
        
        return InitializeModelWeightsOutput(
            initialization_success=False,
            num_parameters=0,
            initialization_method="failed",
            architecture_signature=""
        )