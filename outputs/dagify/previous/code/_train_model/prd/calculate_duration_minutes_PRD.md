# calculate_duration_minutes PRD

## Description
Calculates the elapsed time in minutes between two ISO 8601 timestamp strings.


## Implementation Plan

### 1. Parse the ISO 8601 timestamp strings into timezone‑aware datetime objects using Python's `datetime.fromisoformat` or `dateutil.parser.isoparse`.

| Category | Details |
| --- | --- |
| **Reason** | Accurate time calculations require proper handling of time zones and formatting nuances. |
| **Impact** | Ensures the function works reliably across different locales and clock settings, preventing off‑by‑one minute errors. |
| **Complexity** | LOW |
| **Method** | Use `datetime.fromisoformat(start_time)` and `datetime.fromisoformat(end_time)`; fall back to `dateutil.parser.isoparse` if timezone offset is missing. |

### 2. Compute the time difference by subtracting the start datetime from the end datetime and converting the resulting `timedelta` to minutes with `total_seconds() / 60`.

| Category | Details |
| --- | --- |
| **Reason** | Directly provides the duration in the desired unit (minutes) with floating‑point precision. |
| **Impact** | Provides a precise duration value that can be used for logging, monitoring, or metric reporting in training workflows. |
| **Complexity** | LOW |
| **Method** | Use `delta = end_dt - start_dt; minutes = delta.total_seconds() / 60.0`. |

### 3. Validate input order and handle errors by raising a `ValueError` if the end time precedes the start time or if parsing fails.

| Category | Details |
| --- | --- |
| **Reason** | Prevent silent failures and make debugging easier when timestamps are incorrect. |
| **Impact** | Improves robustness and debuggability of the training pipeline, ensuring accurate duration metrics. |
| **Complexity** | MEDIUM |
| **Method** | Wrap parsing and subtraction in a try/except block; if `end_dt < start_dt` raise `ValueError('end_time must be after start_time')`. |
