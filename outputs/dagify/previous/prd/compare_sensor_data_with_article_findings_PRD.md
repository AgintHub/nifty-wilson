# compare_sensor_data_with_article_findings PRD

## Description
This node compares the statistical and trend information extracted from the mine shaft sensor data with the thermal conductivity data reported in the Springer article. It calculates quantitative similarity measures, identifies differences, and produces a concise textual summary of the comparison.


## Implementation Plan

### 1. Validate that all parent node outputs are available and non‑null before proceeding. If any required field is missing or indicates invalid data, raise an error and terminate with a clear message.

| Category | Details |
| --- | --- |
| **Reason** | Ensures data integrity and prevents downstream failures due to missing inputs. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Simple null checks and boolean flags on `is_data_valid` from both parents. |

### 2. Convert the article’s measurement temperature from Kelvin to Celsius (if necessary) and compute the absolute difference with the sensor’s `avg_temperature`. Store this value as `avg_temp_difference`.

| Category | Details |
| --- | --- |
| **Reason** | Standardizes temperature units for a meaningful comparison. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Apply formula `C = K - 273.15`. Use Python float arithmetic. |

### 3. Extract the numerical trend descriptor from the article’s `key_findings`. If the article states, for example, "conductivity increases with temperature", map this to a numeric trend value of +1; if it says "decreases", map to -1; if it is ambiguous, assign 0.

| Category | Details |
| --- | --- |
| **Reason** | Provides a quantifiable representation of the article’s thermal conductivity trend for correlation analysis. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Keyword search in `key_findings`; regex to detect 'increase', 'decrease', or 'constant'; mapping to integers. |

### 4. Map the sensor temperature trend (from `temperature_trend` in `analyze_sensor_data`) to a numeric value using the same +1 / 0 / -1 scheme.

| Category | Details |
| --- | --- |
| **Reason** | Aligns sensor trend representation with article trend for a consistent correlation metric. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Simple conditional mapping on the string value. |

### 5. Compute the Pearson correlation coefficient between the two numeric trend values. Since we only have one value per dataset, treat the coefficient as the absolute product of the two trend numbers normalized to [-1, 1]; if both trends are zero, set coefficient to 0.

| Category | Details |
| --- | --- |
| **Reason** | Provides a simplistic yet interpretable correlation measure given limited data. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Implement logic: `corr = trend_sensor * trend_article` with saturation to [-1,1]. |

### 6. Estimate a sensor-derived thermal conductivity value using the sensor’s `avg_temperature` and the linear relation reported in the article’s `methodology_description` (if a slope `k` and intercept `c` are provided). If the article only gives a single conductivity point, assume a slope of 0 and use the provided conductivity as the estimate.

| Category | Details |
| --- | --- |
| **Reason** | Creates a comparable numeric value to assess conductivity differences. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Parse the methodology text with NLP to find phrases like 'k =', 'slope =', 'intercept ='; fallback to default values if absent. |

### 7. Compute `thermal_conductivity_difference` as the absolute difference between the article’s `conductivity_value_wmK` and the sensor-derived estimate.

| Category | Details |
| --- | --- |
| **Reason** | Quantifies discrepancy in thermal conductivity between sources. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Simple subtraction and `abs()`. |

### 8. Generate `discrepancy_summary` by concatenating key numerical differences and any textual mismatches (e.g., trend direction differences). Use templated sentences for readability.

| Category | Details |
| --- | --- |
| **Reason** | Provides a human‑readable explanation of differences for downstream reporting. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | String templating with placeholders replaced by computed values. |

### 9. Determine `findings_match` by evaluating two conditions: (1) correlation coefficient magnitude ≥ 0.5 and (2) both `avg_temp_difference` and `thermal_conductivity_difference` below pre‑defined thresholds (e.g., 5 °C and 10 W/mK). If both hold, set `findings_match` to true; otherwise false.

| Category | Details |
| --- | --- |
| **Reason** | Provides a binary flag indicating overall consistency. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Boolean logic with threshold constants. |

### 10. Populate `significant_observations` with a list that includes at least: trend agreement/disagreement, magnitude of temperature difference, magnitude of conductivity difference, and any data quality notes from the parent nodes.

| Category | Details |
| --- | --- |
| **Reason** | Captures essential insights for later synthesis. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Create list of formatted strings. |
