# map_techniques_to_archetypes PRD

## Description
Maps a list of analysis technique identifiers to their corresponding strategy archetype classifications.


## Implementation Plan

### 1. Create a static lookup table that maps known analysis techniques to their corresponding strategy archetypes.

| Category | Details |
| --- | --- |
| **Reason** | A deterministic mapping ensures downstream strategy selection uses consistent archetype information. |
| **Impact** | Provides a reliable reference for translating techniques into strategy categories, reducing ambiguity in later scoring stages. |
| **Complexity** | MEDIUM |
| **Method** | Define a Python dictionary (or load from a YAML/JSON config) where keys are technique identifiers and values are archetype strings; support easy extension via external config files. |

### 2. Validate the incoming techniques list against the lookup table and handle unknown entries gracefully.

| Category | Details |
| --- | --- |
| **Reason** | Input validation prevents runtime errors and ensures only supported techniques are processed. |
| **Impact** | Improves robustness of the pipeline by catching unsupported techniques early and providing clear error messages. |
| **Complexity** | LOW |
| **Method** | Parse the input string into a Python list (using json.loads), iterate over each technique, check presence in the lookup dictionary, and raise a descriptive ValueError for any missing keys. |

### 3. Serialize the resulting technique‑to‑archetype mapping as a JSON string to match the expected output format.

| Category | Details |
| --- | --- |
| **Reason** | Downstream nodes expect the mapping payload as a stringified dictionary. |
| **Impact** | Ensures seamless data flow between nodes without type mismatches. |
| **Complexity** | LOW |
| **Method** | Construct a new dict containing only the validated techniques with their archetype values, then use json.dumps to produce the output string. |
