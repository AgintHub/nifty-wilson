# -- PRD --
# 1. BULLET: Implement the tokenization loop that applies the tokenizer’s `encode` or
#   `batch_encode_plus` method to each text line, collecting the resulting
#   token string representations.
#   Reason: Ensures every input line is processed into tokens for downstream modeling.
#   Impact: Provides a consistent tokenized corpus for training or inference.
#   Complexity: MEDIUM
#   Method: Use `tokenizer.encode(line, add_special_tokens=True)` inside a list
#           comprehension or a for-loop, converting token IDs to string
#           with `tokenizer.convert_ids_to_tokens`.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Handle unknown tokens and special tokens by configuring the tokenizer with
#   appropriate vocabulary and adding any missing special tokens before
#   tokenization.
#   Reason: Prevents tokenization errors and ensures special tokens are consistently
#           represented.
#   Impact: Improves robustness and consistency across different datasets.
#   Complexity: LOW
#   Method: Invoke `tokenizer.add_tokens(['<unk>', '<pad>', '<s>', '</s>'])` and set
#           `tokenizer.special_tokens_map` accordingly.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Return the list of tokenized strings directly, without converting to a single
#   concatenated string or embedding structure, to maintain compatibility
#   with downstream components.
#   Reason: Keeps the output format simple and predictable for subsequent processing
#           steps.
#   Impact: Avoids unnecessary serialization overhead and simplifies downstream
#           parsing.
#   Complexity: LOW
#   Method: Ensure the function returns the list object as is (`return
#           tokenized_texts_list`).
# -- END PRD --

from typing import List


def tokenize_text_lines(tokenizer: str, text_lines: str) -> List[str]:
    """
    The shim tokenizes each line of text using a provided tokenizer, returning a list of tokenized strings.

    Args:
        tokenizer: Input parameter of type str
text_lines: Input parameter of type str

    Returns:
        List[str]: Output of type list[str]
    """
    raise NotImplementedError("This is a virtual stub node that needs to be implemented")
