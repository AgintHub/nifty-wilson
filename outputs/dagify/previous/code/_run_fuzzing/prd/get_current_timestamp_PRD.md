# get_current_timestamp PRD

## Description
Retrieve the current system timestamp as a floating-point number representing the number of seconds elapsed since the epoch.


## Implementation Plan

### 1. Obtain an accurate and high-resolution current time value from the system clock.

| Category | Details |
| --- | --- |
| **Reason** | Precise timestamping is critical to measure durations and sequence events accurately during fuzzing runs. |
| **Impact** | Enables reliable calculation of elapsed time, which is essential for tracking fuzzing session length and performance metrics. |
| **Complexity** | LOW |
| **Method** | Use standard system time APIs such as time.time() in Python or equivalent to retrieve the current timestamp as a float. |

### 2. Ensure the timestamp is returned in a consistent floating-point format representing seconds since Unix epoch.

| Category | Details |
| --- | --- |
| **Reason** | A standardized timestamp format is necessary for consistent usage across various components and calculations related to runtime durations. |
| **Impact** | Facilitates interoperability between nodes and simplifies arithmetic operations on time values. |
| **Complexity** | LOW |
| **Method** | Return the timestamp directly from system API call without additional conversion, ensuring floating-point seconds precision. |
