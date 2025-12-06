# -- PRD --
# 1. BULLET: Validate the number of required data feeds from the parent node to confirm
#   that the ingestion pipeline will provide price updates for all 500
#   symbols.
#   Reason: Ensuring the schema accommodates all data feeds guarantees that no symbol
#           is omitted and that the ingestion pipeline has a defined
#           target.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Parse the parent output `feed_names` and `feed_count`. Verify `feed_count`
#           >= 500; if not, flag an error for upstream data feed selection.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Define the metadata table name as `stock_metadata` and list its columns:
#   `symbol`, `company_name`, `exchange`, `industry`, `sector`, `market_cap`,
#   `ipo_date`, `last_updated`.
#   Reason: These columns cover common attributes needed for filtering and display in
#           the UI while keeping the table normalized.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Create a DDL snippet: `CREATE TABLE stock_metadata (symbol CHAR(5) PRIMARY
#           KEY, company_name VARCHAR(255), exchange VARCHAR(50), industry
#           VARCHAR(100), sector VARCHAR(100), market_cap BIGINT, ipo_date
#           DATE, last_updated TIMESTAMP);`
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Design the price history table name as `stock_price_history` with columns:
#   `symbol`, `price_timestamp`, `open`, `high`, `low`, `close`, `volume`,
#   `adjusted_close`.
#   Reason: These columns capture a full OHLCV record along with an adjusted price for
#           corporate actions.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Define DDL: `CREATE TABLE stock_price_history (symbol CHAR(5),
#           price_timestamp TIMESTAMP, open NUMERIC(12,4), high
#           NUMERIC(12,4), low NUMERIC(12,4), close NUMERIC(12,4), volume
#           BIGINT, adjusted_close NUMERIC(12,4), PRIMARY KEY (symbol,
#           price_timestamp));`
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Add a composite primary key on `(symbol, price_timestamp)` for the price
#   history table to guarantee uniqueness and enable fast range queries by
#   symbol and time.
#   Reason: A composite key eliminates duplicates and improves index locality for
#           time‑series queries.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Include `PRIMARY KEY (symbol, price_timestamp)` in the table DDL.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Enable partitioning on the price history table by daily ranges of
#   `price_timestamp` to accelerate historical queries and simplify archival.
#   Reason: Time‑series data benefits from partitioning, reducing table size per
#           partition and improving query performance.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Add `PARTITION BY RANGE (DATE(price_timestamp))` clause and create daily
#           partitions via a deployment script or database management tool.
# 
# -----------------------------------------------------------------------------
# 6. BULLET: Create an index on `symbol` alone to speed up lookups of all history for a
#   single stock.
#   Reason: Many queries request all records for a particular symbol; this index
#           reduces search time.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Execute `CREATE INDEX idx_stock_symbol ON stock_price_history(symbol);`
# 
# -----------------------------------------------------------------------------
# 7. BULLET: Create a multi‑column index on `(symbol, price_timestamp DESC)` for
#   recent‑price queries and chart generation.
#   Reason: Most dashboards request the latest prices; the descending order ensures
#           index is read‑friendly for newest data.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Execute `CREATE INDEX idx_stock_symbol_ts_desc ON
#           stock_price_history(symbol, price_timestamp DESC);`
# 
# -----------------------------------------------------------------------------
# 8. BULLET: Define data types that match the expected precision: use `NUMERIC(12,4)` for
#   price fields, `BIGINT` for volume, and `TIMESTAMP` with UTC timezone for
#   timestamps.
#   Reason: Correct data types prevent overflow and maintain consistency across
#           ingestion and querying.
#   Impact: LOW
#   Complexity: LOW
#   Method: Choose type specifications in DDL statements; ensure timezone awareness in
#           the database configuration.
# 
# -----------------------------------------------------------------------------
# 9. BULLET: Add a `last_updated` column to the metadata table and trigger it on any price
#   ingestion to keep the metadata in sync with the latest price data.
#   Reason: Maintaining a freshness indicator aids monitoring and UI display of data
#           currency.
#   Impact: LOW
#   Complexity: MEDIUM
#   Method: Create a database trigger that updates `last_updated` on insert/update into
#           `stock_price_history`.
# 
# -----------------------------------------------------------------------------
# 10. BULLET: Include a `supports_partitioning` flag in the output to inform downstream
#   nodes that partitioning logic is active.
#   Reason: Downstream ingestion and query optimization steps rely on knowing
#           partitioning to generate correct queries.
#   Impact: LOW
#   Complexity: LOW
#   Method: Set the boolean to `true` in the final output structure.
# -- END PRD --

from pydantic import BaseModel, Field
from typing import List


class IdentifyRequiredDataFeedsOutput(BaseModel):
    """Pydantic model for identify_required_data_feeds node outputs."""
    feed_names: List[str] = Field(..., description="Names of data feeds required for real-time S&P 500 stock prices.")
    feed_count: int = Field(..., description="Total number of data feeds identified.")


class DesignDatabaseSchemaOutput(BaseModel):
    """Pydantic model for design_database_schema node outputs."""
    metadata_table_name: str = Field(..., description="Name of the table storing stock metadata (e.g., company symbol, name, sector).")
    metadata_columns: str = Field(..., description="List of column names for the metadata table.")
    price_history_table_name: str = Field(..., description="Name of the table storing real\u2011time price history.")
    price_history_columns: str = Field(..., description="List of column names for the price history table.")
    primary_key: str = Field(..., description="Primary key column for the price history table (typically a composite of stock symbol and timestamp).")
    supports_partitioning: bool = Field(..., description="Indicates whether the schema design includes partitioning (e.g., by date or symbol).")


def design_database_schema(identify_required_data_feeds_input: IdentifyRequiredDataFeedsOutput, **kwargs) -> DesignDatabaseSchemaOutput:
    """Design a relational database schema capable of ingesting and serving real‑time price data for the 500 largest US companies, while supporting efficient querying for analytics and trade execution.

    Args:
        identify_required_data_feeds_input: Input from the 'identify_required_data_feeds' node.
        **kwargs: Additional keyword arguments.

    Returns:
        DesignDatabaseSchemaOutput: Object containing outputs for this node.
    """
    # TODO: Implement this function

    # Return stub output with placeholder values
    return DesignDatabaseSchemaOutput(
        metadata_table_name="",
        metadata_columns="",
        price_history_table_name="",
        price_history_columns="",
        primary_key="",
        supports_partitioning=False,
    )