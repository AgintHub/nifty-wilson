# collect_sensor_data PRD

## Description
Collect sensor data from the mine shaft in winter


## Implementation Plan

### 1. Instantiate the sensor driver(s) for temperature and humidity using the manufacturer's SDK or open‑source library, ensuring drivers are compatible with the embedded platform (e.g., Raspberry Pi, PLC).

| Category | Details |
| --- | --- |
| **Reason** | Proper driver instantiation guarantees that sensor registers can be accessed reliably and that low‑level I/O is abstracted. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use the official SDK documentation, perform unit tests on each sensor endpoint, and capture any initialization errors in a structured log. |

### 2. Configure data acquisition parameters: set sampling period to 5 s, define acceptable temperature range (−30 °C to 10 °C) and humidity range (0 % to 100 %) to capture winter extremes.

| Category | Details |
| --- | --- |
| **Reason** | Defining bounds early prevents sensor saturation and ensures the collected data falls within physically plausible limits. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Call the driver’s configuration API with validated constants; verify configuration via a quick readback. |

### 3. Start a timed loop that triggers every 5 s: read temperature, read humidity, capture UTC ISO 8601 timestamp, and append each value to the respective list.

| Category | Details |
| --- | --- |
| **Reason** | A deterministic schedule ensures synchronous data streams, simplifying downstream analysis. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Implement using a high‑resolution timer (e.g., `time.monotonic_ns()`), guard against drift by recalculating sleep duration, and log any missed reads. |

### 4. During each iteration, perform real‑time validation: check for NaN, sensor error codes, and out‑of‑range values; if any anomaly is detected, flag the reading as invalid and store a sentinel value (e.g., None).

| Category | Details |
| --- | --- |
| **Reason** | Early detection of corrupted samples prevents propagation of bad data into analysis steps. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Implement a validation function that returns a boolean and optional corrected value using a simple median filter if consecutive readings are flagged. |

### 5. After the acquisition window (e.g., 2 h), compute a global validity flag: `is_data_valid = all(valid_readings)` where `valid_readings` is a boolean list corresponding to each timestamp.

| Category | Details |
| --- | --- |
| **Reason** | The downstream `analyze_sensor_data` node requires a single boolean to gate analysis; computing it here centralizes the logic. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use Python’s `all()` function or a vectorized NumPy operation for speed. |

### 6. Package the collected lists and validity flag into the node’s output dictionary, converting any `None` values to `float('nan')` for consistency with downstream numeric operations.

| Category | Details |
| --- | --- |
| **Reason** | Consistent numeric representations avoid type errors in subsequent statistical calculations. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Apply a list comprehension to replace None with `float('nan')`; ensure output types match the defined schema. |

### 7. Persist the raw data locally as a JSON file named `winter_shaft_readings.json` and optionally upload it to a central data lake for auditability.

| Category | Details |
| --- | --- |
| **Reason** | Long‑term storage enables reproducibility, debugging, and historical trend analysis. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use `json.dump()` with indentation for readability and include a metadata header (timestamp, sensor IDs). |

### 8. Implement a lightweight watchdog that monitors the acquisition loop; if the loop stalls beyond 10 s, log an error, attempt a graceful restart, and set `is_data_valid` to False.

| Category | Details |
| --- | --- |
| **Reason** | Fault tolerance is critical in harsh mine environments where power interruptions may occur. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Spawn a separate thread or use async callbacks to monitor elapsed time; handle exceptions and trigger a restart sequence defined in the driver API. |
