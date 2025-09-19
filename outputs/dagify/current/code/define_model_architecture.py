# -- PRD --
# 1. BULLET: Extract the vocabulary size and GPU allocation metrics from the outputs of
#   create_vocabulary and allocate_resources to serve as constraints for
#   architecture sizing.
#   Reason: The vocab_size dictates the size of the embedding matrix, while GPU memory
#           limits constrain hidden layer dimensionality and overall
#           parameter count.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Read 'vocab_size' from create_vocabulary output; read 'gpu_count',
#           'gpu_type', and 'memory_gb' from allocate_resources output;
#           store them in local variables for later calculations.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Compute an initial estimate of total trainable parameters using the
#   closed‑form formula for a transformer: params ≈ vocab_size * hidden_size
#   + 12 * number_of_layers * hidden_size^2 + ... and round to nearest
#   integer.
#   Reason: Having a parameter budget early helps validate that the chosen
#           hyper‑parameters fit within hardware constraints and guides
#           subsequent decisions.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Implement a helper function that accepts vocab_size, hidden_size,
#           number_of_layers, attention_heads and returns an integer
#           estimate; use the standard transformer parameter count formula
#           including embedding, layer norm, feed‑forward, and attention
#           projection terms.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Determine number_of_layers by balancing desired performance, convergence
#   speed, and available GPU memory: start from a baseline (e.g., 12 layers)
#   and increase until the estimated parameter count approaches but does not
#   exceed 90% of the GPU memory capacity per GPU.
#   Reason: Layer depth is a primary driver of model capacity; staying within memory
#           limits prevents out‑of‑memory failures during training.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Iteratively loop over candidate layer counts (e.g., 6, 12, 24, 36); for
#           each, compute total_parameters (from bullet 2) and compare
#           against memory_gb * gpu_count * 0.9 * 1024 (bytes). Select the
#           largest count that satisfies the constraint.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Select hidden_size such that the product hidden_size * number_of_layers *
#   hidden_size fits within the remaining memory after accounting for
#   embeddings and optimizer states; also enforce that hidden_size %
#   attention_heads == 0.
#   Reason: Hidden size directly scales the memory footprint of activations and
#           gradients; ensuring divisibility by attention_heads preserves
#           efficient attention implementation.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Compute the available memory per GPU in bytes; subtract memory needed for
#           embedding (vocab_size * hidden_size * 4 bytes) and optimizer
#           buffers (≈ 2 * hidden_size * number_of_layers * hidden_size).
#           Solve for hidden_size iteratively, checking divisibility by
#           candidate attention_heads (typically 8, 12, 16). Choose the
#           largest hidden_size that satisfies both constraints.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Set attention_heads by choosing a value that evenly divides hidden_size and
#   aligns with common transformer configurations (e.g., 8, 12, 16); default
#   to 12 if hidden_size >= 768 and <= 1024.
#   Reason: Standard head counts provide well‑tested scaling behavior and efficient GPU
#           utilization.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: If hidden_size >= 1024 use 16 heads; else if hidden_size >= 768 use 12
#           heads; otherwise use 8 heads; ensure hidden_size %
#           attention_heads == 0.
# 
# -----------------------------------------------------------------------------
# 6. BULLET: Define max_sequence_length based on the training data's longest sequence and
#   the memory budget; if unspecified, default to 512 or 1024 for larger
#   models.
#   Reason: Sequence length impacts memory linearly; setting a conservative default
#           avoids OOM during training while allowing longer inputs if
#           resources permit.
#   Impact: LOW
#   Complexity: LOW
#   Method: If the training configuration (from load_configuration) includes a
#           'max_sequence_length', use it; otherwise compute the maximum
#           token count across a sample of training examples; if that
#           exceeds 512 set to 1024, else set to 512.
# 
# -----------------------------------------------------------------------------
# 7. BULLET: Assemble the final output dictionary with all computed fields, ensuring that
#   total_parameters matches the estimate from bullet 2.
#   Reason: Providing a consistent, typed output is required for downstream nodes such
#           as initialize_model_weights.
#   Impact: LOW
#   Complexity: LOW
#   Method: Create a JSON object containing keys: model_type='Transformer',
#           number_of_layers, hidden_size, attention_heads, vocab_size,
#           max_sequence_length, total_parameters; cast all numeric values
#           to int where appropriate.
# -- END PRD --

from pydantic import BaseModel, Field


class CreateVocabularyOutput(BaseModel):
    """Pydantic model for create_vocabulary node outputs."""
    vocabulary: str = Field(..., description="List of unique tokens constituting the vocabulary.")
    token_frequencies: int = Field(..., description="Frequency count for each corresponding token in the vocabulary list.")
    vocab_size: int = Field(..., description="Total number of unique tokens in the vocabulary.")
    is_valid: bool = Field(..., description="Whether the vocabulary creation was successful.")


class AllocateResourcesOutput(BaseModel):
    """Pydantic model for allocate_resources node outputs."""
    gpu_count: int = Field(..., description="Number of GPUs allocated for training.")
    gpu_type: str = Field(..., description="Model or type of GPU allocated (e.g., V100, A100).")
    memory_gb: float = Field(..., description="Total GPU memory in gigabytes allocated.")
    allocation_success: bool = Field(..., description="Indicates whether the resource allocation was successful.")


class DefineModelArchitectureOutput(BaseModel):
    """Pydantic model for define_model_architecture node outputs."""
    model_type: str = Field(..., description="Name or type of the model architecture (e.g., 'Transformer').")
    number_of_layers: int = Field(..., description="Total number of transformer layers in the model.")
    hidden_size: int = Field(..., description="Dimensionality of each transformer hidden layer.")
    attention_heads: int = Field(..., description="Number of attention heads per transformer layer.")
    vocab_size: int = Field(..., description="Size of the vocabulary derived from the tokenized data.")
    max_sequence_length: int = Field(..., description="Maximum token sequence length supported by the model.")
    total_parameters: int = Field(..., description="Estimated total number of trainable parameters in the model.")


def define_model_architecture(create_vocabulary_input: CreateVocabularyOutput, allocate_resources_input: AllocateResourcesOutput, **kwargs) -> DefineModelArchitectureOutput:
    """Define the architecture and configuration of the large language model.

    Args:
        create_vocabulary_input: Input from the 'create_vocabulary' node.
        allocate_resources_input: Input from the 'allocate_resources' node.
        **kwargs: Additional keyword arguments.

    Returns:
        DefineModelArchitectureOutput: Object containing outputs for this node.
    """
    # TODO: Implement this function

    # Return stub output with placeholder values
    return DefineModelArchitectureOutput(
        model_type="",
        number_of_layers=0,
        hidden_size=0,
        attention_heads=0,
        vocab_size=0,
        max_sequence_length=0,
        total_parameters=0,
    )