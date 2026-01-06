# retrieve_doi_metadata PRD

## Description
Retrieve metadata associated with the given DOI from the Springer article library


## Implementation Plan

### 1. Validate the DOI string against the standard DOI regex pattern (10.\d{4,9}/[-._;()/:A-Z0-9]+) and return an error if it does not match.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that only syntactically correct DOIs are sent to the API, reducing unnecessary calls and potential errors. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use a compiled regular expression in Python; if match fails, log and return empty output. |

### 2. Retrieve the Springer API key from the environment variable SPRINGER_API_KEY; if missing, raise a configuration error.

| Category | Details |
| --- | --- |
| **Reason** | Springer’s metadata endpoint requires authenticated requests; missing the key would cause the request to fail. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use os.getenv('SPRINGER_API_KEY') in the runtime environment; validate that the string is non‑empty. |

### 3. Construct an HTTPS GET request to https://api.springer.com/metadata/01 with query parameters doi={doi}&format=json&api_key={api_key}.

| Category | Details |
| --- | --- |
| **Reason** | This URL is the official metadata service endpoint for Springer's REST API and returns JSON which is easy to parse. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use the requests library; set a timeout (e.g., 10s) and include headers 'Accept: application/json'. |

### 4. Handle HTTP errors: for status codes 4xx/5xx, log the error code and response body; for 429 (rate limit), retry with exponential back‑off up to 3 attempts.

| Category | Details |
| --- | --- |
| **Reason** | Robustness to network or API limits ensures the workflow does not fail abruptly. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Implement a retry loop; use time.sleep with back‑off; raise custom exception on final failure. |

### 5. Parse the JSON payload to extract the title (field 'title' or 'title[0]'), authors (field 'author' array; concatenate givenName and surname for each), publication date (combine 'publicationDate' components into YYYY-MM-DD, default missing month/day to '01'), and keywords (array of 'keyword' objects).

| Category | Details |
| --- | --- |
| **Reason** | Direct mapping from Springer's schema to the required output types preserves data integrity. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Iterate over JSON dict; handle optional fields with defaults; use list comprehensions. |

### 6. Normalize author names to title‑case full names and deduplicate entries before returning the authors list.

| Category | Details |
| --- | --- |
| **Reason** | Springer may provide duplicate or differently formatted author entries; deduplication prevents redundancy. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Apply str.title() and a set to remove duplicates. |

### 7. Return a JSON object conforming to the defined output structure; if any field is missing, populate with an empty string or empty list.

| Category | Details |
| --- | --- |
| **Reason** | Maintains contract with downstream nodes, avoiding schema violations. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Construct a dict with keys 'title', 'authors', 'publication_date', 'keywords'; use json.dumps for serialization if needed. |
