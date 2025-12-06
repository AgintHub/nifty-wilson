# implement_data_ingestion_pipeline PRD

## Description
Implement a data ingestion pipeline to fetch and store live S&P 500 stock prices.


## Implementation Plan

### 1. Validate provider selection: ensure at least one provider is marked as `provider_selected` in the `select_data_providers` output; otherwise log an error and abort the pipeline.

| Category | Details |
| --- | --- |
| **Reason** | A data ingestion pipeline cannot operate without a valid data source. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Parse the `provider_selected` list, check for at least one `true`; use environment logs to record failure. |

### 2. Select the primary data provider: choose the first provider marked as selected; implement a fail‑over mechanism to switch to the next provider on repeated failures.

| Category | Details |
| --- | --- |
| **Reason** | Simplifies initial implementation while still supporting resilience. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Iterate over `provider_names` and corresponding `provider_selected`; store fallback order; use a context manager to switch providers. |

### 3. Load database schema details from `design_database_schema`: extract table names, columns, primary and foreign keys.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the pipeline inserts data into the correct tables with proper constraints. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Deserialize the schema output into a configuration object; map column names to provider field names. |

### 4. Initialize the API client for the selected provider, loading credentials from secure environment variables or a vault service.

| Category | Details |
| --- | --- |
| **Reason** | Secures sensitive keys and abstracts provider‑specific logic. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use the provider's official SDK or REST wrapper; implement a factory that returns a configured client instance. |

### 5. Establish a database connection pool to the target RDBMS (e.g., PostgreSQL) using a high‑performance driver (psycopg3 or asyncpg).

| Category | Details |
| --- | --- |
| **Reason** | Connection pooling reduces latency for high‑frequency inserts. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Configure pool size based on expected record throughput; enable prepared statement caching. |

### 6. Define the ingestion loop: fetch the latest price snapshot for all S&P 500 tickers via the provider's streaming or batch API endpoint.

| Category | Details |
| --- | --- |
| **Reason** | Continuous data capture is required for real‑time pricing. |
| **Impact** | HIGH |
| **Complexity** | HIGH |
| **Method** | Implement an async loop using aiohttp for streaming; use pagination if the provider limits batch size. |

### 7. Transform each received record into the database schema: map provider field names to `price_history_columns`, cast data types, and generate a composite primary key (`ticker` + `timestamp`).

| Category | Details |
| --- | --- |
| **Reason** | Ensures data consistency and enforces uniqueness constraints. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Create a mapping dictionary; use Pydantic models for validation; handle missing or null fields with defaults. |

### 8. Batch insert transformed records using a single `COPY` or `INSERT ALL` statement within a transaction to maximize throughput.

| Category | Details |
| --- | --- |
| **Reason** | Reduces round‑trips and locks, lowering overall latency. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Accumulate records into a list of tuples; execute `psycopg.execute_values` or `COPY FROM STDIN`; commit after each batch. |

### 9. Measure ingestion latency: record timestamps immediately before fetching and immediately after database commit; compute the average latency for the run.

| Category | Details |
| --- | --- |
| **Reason** | Provides a key metric for performance monitoring. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use `time.monotonic_ns()` for high‑resolution timing; convert to milliseconds. |

### 10. Implement robust error handling: catch network timeouts, API rate‑limit responses, and database constraint violations; increment `error_count` and log details for each failure.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the pipeline can recover gracefully and provides visibility into issues. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Wrap API calls and DB inserts in try/except blocks; use exponential backoff for transient errors; set a retry limit. |

### 11. After successful batch insertion, record the timestamp of the most recent price record to `latest_record_timestamp` and set `db_insert_success` accordingly.

| Category | Details |
| --- | --- |
| **Reason** | Provides a snapshot for downstream services to verify freshness. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Track the max timestamp seen in the batch; format as ISO 8601 using `datetime.isoformat()`. |

### 12. Set `pipeline_running` to `true` at the start of the ingestion process and back to `false` upon completion, regardless of success or failure.

| Category | Details |
| --- | --- |
| **Reason** | Allows external orchestrators to monitor pipeline state. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Toggle a boolean flag at entry and exit points of the main function. |

### 13. Output all metric fields (`records_ingested`, `provider_name`, `latest_record_timestamp`, `ingestion_latency_ms`, `error_count`, `db_insert_success`) in a JSON payload for the orchestrator to consume.

| Category | Details |
| --- | --- |
| **Reason** | Conforms to the defined `Output Structure` and enables downstream nodes to consume the results. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Serialize a dictionary with the required keys; ensure proper type casting (int, bool, str). |
