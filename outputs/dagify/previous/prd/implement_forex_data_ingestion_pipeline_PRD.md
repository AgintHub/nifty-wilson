# implement_forex_data_ingestion_pipeline PRD

## Description
This node builds a robust, fault‑tolerant ingestion pipeline that pulls live forex rates from the chosen data providers, validates the data, persists it to the pre‑designed database schema, and records key performance metrics for monitoring.


## Implementation Plan

### 1. Extract the list of selected providers and their connection parameters from the output of `select_forex_data_providers`; filter to include only those where `is_selected` is true, and construct a runtime configuration mapping provider name to API endpoint, authentication token, and rate‑limit details.

| Category | Details |
| --- | --- |
| **Reason** | Using the provider selection data ensures the pipeline only attempts to call APIs that the organization has chosen and is compliant with cost and latency budgets. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Parse JSON output, filter boolean list, build dict with key: provider_name, values: {endpoint, token, rate_limit} |

### 2. Retrieve the database table names and column metadata from `design_database_schema`; validate that the forex rate table exists and that its schema matches the expected columns (e.g., base_currency, quote_currency, rate, timestamp).

| Category | Details |
| --- | --- |
| **Reason** | Schema validation prevents runtime failures due to mismatched columns and guarantees data integrity during inserts. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Execute a lightweight 'DESCRIBE table' query; compare result set to expected column list |

### 3. Instantiate a lightweight orchestration scheduler (e.g., APScheduler or a cron‑like loop) to trigger the ingestion job at the required frequency (e.g., every 5 seconds).

| Category | Details |
| --- | --- |
| **Reason** | A simple scheduler keeps the implementation lean while still enabling high‑frequency data pulls. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use APScheduler with a `BackgroundScheduler` and a `IntervalTrigger` set to 5s |

### 4. For each selected provider, implement a dedicated fetcher module that (1) constructs the HTTP request with necessary headers (including API keys), (2) sends the request, and (3) records the start and end timestamps to compute latency.

| Category | Details |
| --- | --- |
| **Reason** | Provider‑specific fetchers abstract API quirks, allowing uniform downstream processing. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Use `httpx` async client, wrap call in try/except, capture `time.monotonic()` before/after |

### 5. Parse the provider’s JSON/XML response into a canonical record format: `{base_currency, quote_currency, rate, timestamp}`. Normalize timestamp to UTC ISO‑8601 and enforce numeric types for rate.

| Category | Details |
| --- | --- |
| **Reason** | Standardizing the record format simplifies downstream validation, deduplication, and DB insertion. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Write a parser per provider using `pydantic` models or custom dict mapping; convert timestamp via `datetime.fromisoformat` or `pytz` |

### 6. Validate each record: ensure required fields are present, rate is within a realistic numeric range, and timestamp is not older than a configurable threshold (e.g., 5 minutes). Discard or flag any record failing validation.

| Category | Details |
| --- | --- |
| **Reason** | Early validation prevents corrupt data from polluting the database and reduces downstream error handling. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Implement validation functions using `pydantic` validators; log validation failures and increment `errors_found` counter |

### 7. Batch validated records and perform a single bulk `INSERT ... ON CONFLICT` (upsert) operation into the forex rate table. Use a transaction per batch to guarantee atomicity.

| Category | Details |
| --- | --- |
| **Reason** | Bulk writes reduce latency and database load; upsert logic prevents duplicate keys on repeated runs. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use SQLAlchemy or raw PostgreSQL `INSERT ... ON CONFLICT (base_currency, quote_currency, timestamp) DO UPDATE` |

### 8. Aggregate ingestion metrics: sum `records_ingested`, compute `average_latency_ms` across all provider fetches, and determine `ingestion_success` based on whether `errors_found` is below a critical threshold.

| Category | Details |
| --- | --- |
| **Reason** | Metric aggregation provides actionable insight into pipeline health and performance. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Maintain counters in memory during job run; after completion, compute averages and boolean status |

### 9. Persist a metrics snapshot to a dedicated `ingestion_metrics` table (or expose via Prometheus exporter) for downstream monitoring and alerting.

| Category | Details |
| --- | --- |
| **Reason** | Historical metrics enable trend analysis and trigger alerts when ingestion quality degrades. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Insert a row into `ingestion_metrics` with fields: provider_names, timestamp, records_ingested, errors_found, average_latency_ms, ingestion_success |

### 10. Implement robust error handling and retry logic: for transient network errors, retry with exponential backoff up to 3 attempts; for permanent errors (e.g., 401), log and skip provider for that cycle.

| Category | Details |
| --- | --- |
| **Reason** | Retries increase reliability without manual intervention, while graceful degradation prevents cascading failures. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use `tenacity` retry decorator with `wait_exponential` and `stop_after_attempt` |

### 11. Generate a concise, machine‑readable report (JSON) at the end of each ingestion cycle containing all required output fields, ensuring timestamps are formatted in UTC ISO‑8601.

| Category | Details |
| --- | --- |
| **Reason** | A deterministic output format simplifies integration with downstream nodes like `implement_forex_trading_api`. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Construct dict, serialize with `json.dumps` with `ensure_ascii=False`; use `datetime.utcnow().isoformat() + 'Z'` |
