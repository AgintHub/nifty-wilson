# generate_proposal_ids PRD

## Description
Generates unique, deterministic identifiers for symbolic regression proposals from given expressions.


## Implementation Plan

### 1. Parse the expressions into a format that can be processed by a deterministic identifier generation algorithm.

| Category | Details |
| --- | --- |
| **Reason** | This step is necessary to establish a consistent relationship between expressions and identifiers. |
| **Impact** | Failure to correctly parse expressions may result in incorrect or inconsistent identifiers. |
| **Complexity** | MEDIUM |
| **Method** | Use a library such as `ast` in Python to parse the expressions into an abstract syntax tree, which can then be used to generate identifiers. |

### 2. Implement a deterministic algorithm that generates unique identifiers from the parsed expressions.

| Category | Details |
| --- | --- |
| **Reason** | This step is necessary to ensure that the identifiers are consistent and reproducible. |
| **Impact** | Using a non-deterministic algorithm may result in identifiers that are not reproducible across different runs. |
| **Complexity** | HIGH |
| **Method** | Use a library such as `hashlib` in Python to generate a unique hash for each expression, which can then be used as the identifier. |
