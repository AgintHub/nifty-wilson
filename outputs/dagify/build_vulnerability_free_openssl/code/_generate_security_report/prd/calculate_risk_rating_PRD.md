# calculate_risk_rating PRD

## Description
Calculates an overall risk rating for a software build based on input parameters including identified security issues, applied patches, hardening measures, fuzzing crashes, and test failures.


## Implementation Plan

### 1. Design a scoring rubric that quantitatively assesses risk by evaluating the number and severity of security issues identified, applied patches, hardening measures, fuzzing crash counts, and test failures.

| Category | Details |
| --- | --- |
| **Reason** | A structured scoring rubric enables objective and consistent risk classification across builds. |
| **Impact** | Improves reliability and reproducibility of risk assessments and supports informed decision-making about software security posture. |
| **Complexity** | MEDIUM |
| **Method** | Develop heuristic or rule-based scoring rules that assign weighted scores to each input parameter and aggregate them to derive risk levels such as Low, Medium, or High. |

### 2. Implement parsing and normalization logic to interpret the input strings representing identified issues, patches, hardening measures, fuzzing crashes, and test failures, ensuring accurate quantification or categorical interpretation.

| Category | Details |
| --- | --- |
| **Reason** | Input data may vary in format or detail; normalization is essential to reliably feed into the scoring mechanism. |
| **Impact** | Ensures consistent interpretation of heterogeneous inputs, reducing errors in risk calculation. |
| **Complexity** | MEDIUM |
| **Method** | Use pattern matching, keyword extraction, or metadata parsing techniques to convert input strings into standardized counts or categories. |

### 3. Return a clear textual risk rating output (e.g., 'Low', 'Medium', 'High') based on the aggregated score and thresholds defined by security best practices.

| Category | Details |
| --- | --- |
| **Reason** | The final risk rating must be easily understandable and actionable by users and downstream processes. |
| **Impact** | Facilitates clear communication of overall security risk and guides mitigation priorities. |
| **Complexity** | LOW |
| **Method** | Map the computed numerical score to predefined risk levels using if-else conditions or lookup tables and output the corresponding risk rating string. |
