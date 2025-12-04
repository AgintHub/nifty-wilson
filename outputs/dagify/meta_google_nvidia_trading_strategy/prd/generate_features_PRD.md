# generate_features PRD

## Description
Adds rolling moving averages and volatility features to the cleaned merged stock dataset.


## Implementation Plan

### 1. Parse the cleaned CSV string into a pandas DataFrame and enforce ISO 8601 date ordering.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that all subsequent rolling calculations operate on chronologically sorted data and that the date format matches downstream expectations. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use `pandas.read_csv` with `parse_dates=['Date']`, `skipinitialspace=True`, then `df.sort_values('Date', inplace=True)`. |

### 2. Validate that the DataFrame contains the required columns: `META_Close` and `GOOGL_Close`.

| Category | Details |
| --- | --- |
| **Reason** | Prevents downstream KeyErrors and guarantees that the feature calculation has the necessary data. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Check `set(['META_Close', 'GOOGL_Close']).issubset(df.columns)`; if not, raise a descriptive ValueError. |

### 3. Compute the 10‑day simple moving averages for Meta and Google using `rolling(window=10, min_periods=10).mean()`.

| Category | Details |
| --- | --- |
| **Reason** | Using `min_periods=10` ensures that only full windows contribute to the average, yielding `NaN` for the first nine rows. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Assign new columns: `df['META_MovingAvg_10'] = df['META_Close'].rolling(10, min_periods=10).mean()` and similarly for GOOGL. |

### 4. Compute the 5‑day rolling standard deviations for Meta and Google using `rolling(window=5, min_periods=5).std()`.

| Category | Details |
| --- | --- |
| **Reason** | Captures short‑term volatility dynamics and aligns with the strategy's volatility thresholds. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Assign new columns: `df['META_Std_5'] = df['META_Close'].rolling(5, min_periods=5).std()` and similarly for GOOGL. |

### 5. Replace any remaining `NaN` values in the new feature columns with `None` to produce JSON‑compatible nulls.

| Category | Details |
| --- | --- |
| **Reason** | JSON serialization cannot encode `NaN`; representing missing values as `null` keeps semantic meaning intact. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use `df[col].where(df[col].notna(), None).tolist()` for each new feature column. |

### 6. Extract the date list and feature lists from the DataFrame and return them as separate lists matching the output schema.

| Category | Details |
| --- | --- |
| **Reason** | Ensures that the function signature and downstream consumers receive strictly typed and ordered arrays. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Build the result dictionary: `date_list = df['Date'].dt.strftime('%Y-%m-%d').tolist()`, and assign each feature list from the corresponding column. |
