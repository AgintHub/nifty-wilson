# design_database_schema PRD

## Description
Design a relational database schema capable of ingesting and serving real‑time price data for the 500 largest US companies, while supporting efficient querying for analytics and trade execution.


## Implementation Plan

### 1. Validate the number of required data feeds from the parent node to confirm that the ingestion pipeline will provide price updates for all 500 symbols.

| Category | Details |
| --- | --- |
| **Reason** | Ensuring the schema accommodates all data feeds guarantees that no symbol is omitted and that the ingestion pipeline has a defined target. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Parse the parent output `feed_names` and `feed_count`. Verify `feed_count` >= 500; if not, flag an error for upstream data feed selection. |

### 2. Define the metadata table name as `stock_metadata` and list its columns: `symbol`, `company_name`, `exchange`, `industry`, `sector`, `market_cap`, `ipo_date`, `last_updated`.

| Category | Details |
| --- | --- |
| **Reason** | These columns cover common attributes needed for filtering and display in the UI while keeping the table normalized. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Create a DDL snippet: `CREATE TABLE stock_metadata (symbol CHAR(5) PRIMARY KEY, company_name VARCHAR(255), exchange VARCHAR(50), industry VARCHAR(100), sector VARCHAR(100), market_cap BIGINT, ipo_date DATE, last_updated TIMESTAMP);` |

### 3. Design the price history table name as `stock_price_history` with columns: `symbol`, `price_timestamp`, `open`, `high`, `low`, `close`, `volume`, `adjusted_close`.

| Category | Details |
| --- | --- |
| **Reason** | These columns capture a full OHLCV record along with an adjusted price for corporate actions. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Define DDL: `CREATE TABLE stock_price_history (symbol CHAR(5), price_timestamp TIMESTAMP, open NUMERIC(12,4), high NUMERIC(12,4), low NUMERIC(12,4), close NUMERIC(12,4), volume BIGINT, adjusted_close NUMERIC(12,4), PRIMARY KEY (symbol, price_timestamp));` |

### 4. Add a composite primary key on `(symbol, price_timestamp)` for the price history table to guarantee uniqueness and enable fast range queries by symbol and time.

| Category | Details |
| --- | --- |
| **Reason** | A composite key eliminates duplicates and improves index locality for time‑series queries. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Include `PRIMARY KEY (symbol, price_timestamp)` in the table DDL. |

### 5. Enable partitioning on the price history table by daily ranges of `price_timestamp` to accelerate historical queries and simplify archival.

| Category | Details |
| --- | --- |
| **Reason** | Time‑series data benefits from partitioning, reducing table size per partition and improving query performance. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Add `PARTITION BY RANGE (DATE(price_timestamp))` clause and create daily partitions via a deployment script or database management tool. |

### 6. Create an index on `symbol` alone to speed up lookups of all history for a single stock.

| Category | Details |
| --- | --- |
| **Reason** | Many queries request all records for a particular symbol; this index reduces search time. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Execute `CREATE INDEX idx_stock_symbol ON stock_price_history(symbol);` |

### 7. Create a multi‑column index on `(symbol, price_timestamp DESC)` for recent‑price queries and chart generation.

| Category | Details |
| --- | --- |
| **Reason** | Most dashboards request the latest prices; the descending order ensures index is read‑friendly for newest data. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Execute `CREATE INDEX idx_stock_symbol_ts_desc ON stock_price_history(symbol, price_timestamp DESC);` |

### 8. Define data types that match the expected precision: use `NUMERIC(12,4)` for price fields, `BIGINT` for volume, and `TIMESTAMP` with UTC timezone for timestamps.

| Category | Details |
| --- | --- |
| **Reason** | Correct data types prevent overflow and maintain consistency across ingestion and querying. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Choose type specifications in DDL statements; ensure timezone awareness in the database configuration. |

### 9. Add a `last_updated` column to the metadata table and trigger it on any price ingestion to keep the metadata in sync with the latest price data.

| Category | Details |
| --- | --- |
| **Reason** | Maintaining a freshness indicator aids monitoring and UI display of data currency. |
| **Impact** | LOW |
| **Complexity** | MEDIUM |
| **Method** | Create a database trigger that updates `last_updated` on insert/update into `stock_price_history`. |

### 10. Include a `supports_partitioning` flag in the output to inform downstream nodes that partitioning logic is active.

| Category | Details |
| --- | --- |
| **Reason** | Downstream ingestion and query optimization steps rely on knowing partitioning to generate correct queries. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Set the boolean to `true` in the final output structure. |
