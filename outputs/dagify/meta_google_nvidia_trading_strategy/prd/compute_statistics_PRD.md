# compute_statistics PRD

## Description
Generates summary statistics of the daily log returns for Meta, Google, and Nvidia, including mean, standard deviation, pairwise correlations, and skewness.


## Implementation Plan

### 1. Read the CSV file produced by the compute_daily_returns node into a Pandas DataFrame, ensuring that the META_Return, GOOGL_Return, and NVDA_Return columns are parsed as float.

| Category | Details |
| --- | --- |
| **Reason** | The downstream statistics calculation requires numeric types; reading via Pandas provides robust handling of CSV parsing and missing values. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use `pd.read_csv(csv_file_path)` with `dtype={'META_Return': float, 'GOOGL_Return': float, 'NVDA_Return': float}` and `parse_dates` if needed. |

### 2. Drop any rows where any of the return columns contain NaN to avoid distortion of mean, std, skewness, and correlation calculations.

| Category | Details |
| --- | --- |
| **Reason** | Statistical functions in Pandas ignore NaNs by default but pairwise correlation requires aligned rows; explicit drop ensures consistent dataset. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Apply `df.dropna(subset=['META_Return','GOOGL_Return','NVDA_Return'])`. |

### 3. Compute the mean of each return series using `Series.mean()` and round the result to 8 decimal places for consistency.

| Category | Details |
| --- | --- |
| **Reason** | Mean is a simple aggregate; rounding reduces floating point noise in the JSON output. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Store in variables `meta_mean = df['META_Return'].mean().round(8)` etc. |

### 4. Compute the standard deviation of each return series using `Series.std(ddof=1)` to reflect sample std, and round to 8 decimal places.

| Category | Details |
| --- | --- |
| **Reason** | Using sample standard deviation aligns with typical financial analysis; rounding maintains readability. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use `df['META_Return'].std(ddof=1).round(8)`. |

### 5. Compute the skewness of each return series using `Series.skew()` from SciPy or Pandas, rounding to 8 decimal places.

| Category | Details |
| --- | --- |
| **Reason** | Skewness provides insight into return distribution asymmetry; rounding keeps output concise. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | If Pandas does not provide skewness, use `from scipy.stats import skew; skew(df['META_Return']).round(8)`. |

### 6. Compute Pearson correlations for each unique pair of return series using `DataFrame.corr(method='pearson')`, selecting the corresponding matrix entries and rounding to 8 decimal places.

| Category | Details |
| --- | --- |
| **Reason** | Pearson correlation captures linear dependence; rounding ensures JSON numerical precision. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Create `corr_matrix = df[['META_Return','GOOGL_Return','NVDA_Return']].corr()` then extract `corr_meta_googl = corr_matrix.loc['META_Return','GOOGL_Return'].round(8)` and similarly for other pairs. |

### 7. Assemble all computed metrics into a dictionary matching the defined output fields.

| Category | Details |
| --- | --- |
| **Reason** | The node contract requires a JSON object with specific keys; assembling in a dict guarantees correct key order and type. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use `output_dict = {'meta_return_mean': meta_mean, 'meta_return_std': meta_std, ...}`. |

### 8. Serialize the dictionary to JSON and return it as the node's output, ensuring that numerical values are cast to float types (not numpy floats).

| Category | Details |
| --- | --- |
| **Reason** | JSON expects standard Python types; converting avoids serialization errors. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use `json.dumps(output_dict)` after converting values with `float()` if necessary. |
