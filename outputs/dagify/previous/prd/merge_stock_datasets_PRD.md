# merge_stock_datasets PRD

## Description
Creates a unified dataset containing Meta and Google OHLCV data.


## Implementation Plan

### 1. Parse the parent node outputs by converting the date and OHLCV lists from Meta and Google into two separate dictionaries keyed by ISO‑format date strings, mapping each date to a sub‑dictionary of its OHLCV values.

| Category | Details |
| --- | --- |
| **Reason** | Using dictionaries allows constant‑time lookup for matching dates and keeps the OHLCV data grouped logically. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Iterate over the lists, zip them together, and store in a Python dict: meta_dict[date] = {'Open': open, 'High': high, 'Low': low, 'Close': close, 'Volume': vol}. |

### 2. Compute the intersection of date keys between the Meta and Google dictionaries to identify only those dates that appear in both datasets.

| Category | Details |
| --- | --- |
| **Reason** | The requirement explicitly states to keep rows that have dates present in both datasets. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use set operations: common_dates = sorted(set(meta_dict.keys()) & set(google_dict.keys())) to preserve ascending order. |

### 3. For each date in the sorted list of common dates, create a merged row by extracting the OHLCV values from both dictionaries and prefixing each column name with META_ or GOOGL_. Assemble the row values in the order: Date, META_Open, META_High, META_Low, META_Close, META_Volume, GOOGL_Open, GOOGL_High, GOOGL_Low, GOOGL_Close, GOOGL_Volume.

| Category | Details |
| --- | --- |
| **Reason** | Explicit column ordering ensures consistency across all consumers of the CSV. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Loop over common_dates, build a list of strings, e.g., [date, str(meta_open), …, str(googl_volume)], and append to a row list. |

### 4. Create the header row by concatenating the prefixed column names exactly once, ensuring no duplicate or missing headers.

| Category | Details |
| --- | --- |
| **Reason** | The output must include a header for downstream processing and human readability. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use a static list: ['Date', 'META_Open', 'META_High', 'META_Low', 'META_Close', 'META_Volume', 'GOOGL_Open', 'GOOGL_High', 'GOOGL_Low', 'GOOGL_Close', 'GOOGL_Volume'] and join with commas. |

### 5. Convert each merged row (including the header) into a single comma‑separated string, ensuring that numeric values are formatted with at least two decimal places for consistency.

| Category | Details |
| --- | --- |
| **Reason** | Consistent formatting prevents parsing errors in downstream nodes. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use Python f‑strings or format specifiers: f"{value:.2f}" for floats and str(value) for integers. |

### 6. Return the list of CSV strings as the value of the output field merged_csv.

| Category | Details |
| --- | --- |
| **Reason** | The downstream nodes expect a list of strings to write or further process. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Assign merged_csv = [header_row] + row_strings and return this list. |
