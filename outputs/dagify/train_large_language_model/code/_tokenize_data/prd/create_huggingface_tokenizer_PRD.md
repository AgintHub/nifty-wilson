# create_huggingface_tokenizer PRD

## Description
Creates a Hugging Face tokenizer instance based on the specified method and returns it as a serialized string.


## Implementation Plan

### 1. Map the provided method string to the appropriate Hugging Face tokenizer class.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that the correct tokenizer implementation is instantiated based on the requested method. |
| **Impact** | Provides flexibility for different tokenization strategies (BPE, WordPiece, SentencePiece, etc.) without changing the shim interface. |
| **Complexity** | MEDIUM |
| **Method** | Create a lookup dictionary mapping method names to classes (e.g., {'bpe': ByteLevelBPETokenizer, 'wordpiece': WordPieceTokenizer}) and use it to retrieve the class. |

### 2. Instantiate the tokenizer, handling both pretrained and freshly-trained scenarios.

| Category | Details |
| --- | --- |
| **Reason** | The shim must support creating tokenizers that either load existing models or are initialized from scratch. |
| **Impact** | Allows downstream nodes to use a tokenizer that is ready for training or inference. |
| **Complexity** | MEDIUM |
| **Method** | If the method indicates a pretrained model (e.g., starts with 'pretrained:'), call the class's `from_pretrained` method; otherwise, use the default constructor and optionally configure training parameters. |

### 3. Serialize the tokenizer instance to a JSON string for return.

| Category | Details |
| --- | --- |
| **Reason** | The shim’s output must be a primitive string so it can be stored or passed between nodes. |
| **Impact** | Facilitates persistence and transfer of tokenizer configuration across steps in the workflow. |
| **Complexity** | LOW |
| **Method** | Use the tokenizer's `save_pretrained` to a temporary directory and read the config files (e.g., tokenizer_config.json) back into a string, or use the tokenizer's `serialize()` method if available. |
