# extract_relevant_data_from_article PRD

## Description
Extract relevant data related to thermal conductivity of boron from the article retrieved using the DOI


## Implementation Plan

### 1. Validate DOI input and retrieve full article text (PDF or HTML) using the DOI provided by the parent node. Use the Crossref or SpringerLink API to obtain a direct download link, then download the PDF with requests and handle HTTP status codes and retry logic.

| Category | Details |
| --- | --- |
| **Reason** | Ensures we have the exact document referenced in the metadata before proceeding with extraction. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use requests.get with timeout and retries; for PDF, stream binary content and write to temporary file; for HTML, use BeautifulSoup to capture article body. |

### 2. Extract raw text from the downloaded PDF using a robust extraction library such as PyMuPDF (fitz) or PDFminer.six, preserving paragraph structure. Clean the extracted text by normalizing whitespace, removing footnotes and figure captions that are irrelevant to methodology or results.

| Category | Details |
| --- | --- |
| **Reason** | Accurate text extraction is critical for downstream pattern matching and NLP parsing. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Open PDF with fitz.open, iterate pages, use page.get_text('text'); post‑process with regex to collapse multiple newlines; filter out lines containing page numbers or headers. |

### 3. Identify the section(s) pertaining to thermal conductivity of boron by searching for key phrases such as "thermal conductivity", "boron", "κ", "kappa", and combining them with proximity constraints (within 5–10 words). Use a simple keyword search first, then refine with spaCy’s sentence boundary detection to isolate the relevant paragraph(s).

| Category | Details |
| --- | --- |
| **Reason** | Targeted extraction reduces noise and ensures the subsequent numeric extraction focuses on the correct data. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Use spaCy English model to split text into sentences; apply a regex to detect sentences containing all required keywords; return the first matching block as the ‘results block’. |

### 4. Parse the methodology description by extracting the paragraph(s) immediately preceding the results block. Look for cues such as "Experimental method", "Measurement procedure", or "Computational model". Concatenate these sentences into a single paragraph for the output field "methodology_description".

| Category | Details |
| --- | --- |
| **Reason** | Captures the experimental/computational setup directly from the authors, which is needed for later comparison. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Back‑track from the results block index; collect contiguous sentences until a heading or blank line; join with spaces; apply a length cutoff to avoid overly verbose text. |

### 5. Extract the thermal conductivity value by searching the results block for numeric patterns followed by units "W/mK" or "W/(m·K)". Use a regex such as `([-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)\s*W/mK` and cast the captured string to float. If multiple values appear, prioritize the first numeric value that also appears with a temperature context.

| Category | Details |
| --- | --- |
| **Reason** | Provides a reliable numeric value while handling scientific notation. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Python regex, int()/float() conversion, handle ValueError. |

### 6. Determine the measurement temperature by locating numeric values adjacent to units "K" or "°C" near the conductivity value. If the unit is °C, convert to Kelvin by adding 273.15. If no explicit temperature is mentioned, default to 298 K and flag the assumption in the output for traceability.

| Category | Details |
| --- | --- |
| **Reason** | Temperature context is required for comparison with sensor data. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Regex `([0-9]+(?:\.[0-9]+)?)\s*(K|°C)`; conditional conversion. |

### 7. Extract measurement conditions by scanning the methodology block for phrases that include "pressure", "purity", "sample”, or “environment”. Concatenate the first three identified clauses into a concise string for the "measurement_conditions" output field.

| Category | Details |
| --- | --- |
| **Reason** | Conditions influence the validity of the conductivity value. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Use spaCy NER to detect entities like Quantity and Unit; apply keyword search for conditions; join into single string. |

### 8. Compile key findings by extracting sentences in the results block that contain verbs like "indicates", "shows", "reveals", or “demonstrates” and are not part of tables or figure captions. Store each sentence in the "key_findings" list.

| Category | Details |
| --- | --- |
| **Reason** | Provides a quick summary of the article’s observations for downstream comparison. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Iterate over sentences in results block; filter using a verb keyword list; append to list. |

### 9. Summarize the authors’ conclusion by locating the section titled "Conclusion" or the final paragraph of the article. Extract the first two sentences, or up to 200 characters, as a concise summary for the "conclusion_summary" output field.

| Category | Details |
| --- | --- |
| **Reason** | A short, clear conclusion is needed for synthesis nodes. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Search for heading "Conclusion"; if absent, take last paragraph; limit length with string slicing. |

### 10. Validate all extracted numeric values against reasonable physical ranges (e.g., thermal conductivity of boron typically 200–400 W/mK). If a value falls outside, log a warning and set the output field to null for that field.

| Category | Details |
| --- | --- |
| **Reason** | Prevents downstream propagation of erroneous data. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Compare float to expected min/max; if out of bounds, assign null and log via standard logger. |

### 11. Return a dictionary matching the defined output structure, ensuring data types match (e.g., lists for "key_findings", floats for numeric fields, strings otherwise). Serialize the result as JSON for downstream nodes.

| Category | Details |
| --- | --- |
| **Reason** | Strict adherence to output schema is required for DAG execution. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Build a Python dict; cast floats; use json.dumps with ensure_ascii=False. |
