# -- PRD --
# 1. BULLET: Extract the ordered list of ticker symbols from the output of the
#   `specify_asset_universe` node (field `asset_tickers`).
#   Reason: Provides the definitive source of symbols that the downstream strategy
#           expects; ensures alignment with upstream decisions.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Read the parent node's JSON payload, validate that `asset_tickers` exists
#           and is a non‑empty List[str]; raise a clear error if validation
#           fails.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Validate the ticker list for duplicates and illegal characters (e.g.,
#   whitespace, commas).
#   Reason: Duplicate or malformed tickers cause yfinance to raise errors or return
#           ambiguous data, breaking downstream alignment.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Iterate over the list, strip whitespace, use a set to detect duplicates,
#           and filter out any ticker that does not match the regex
#           `^[A-Z\.\-]{1,10}$`. Preserve original order after cleaning.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Create a thread‑pool executor (e.g., `concurrent.futures.ThreadPoolExecutor`)
#   sized to the number of CPU cores (or a configurable max workers) to fetch
#   tickers in parallel while preserving order.
#   Reason: Historical data for dozens of tickers can be fetched concurrently, reducing
#           overall latency without overwhelming Yahoo Finance's rate
#           limits.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Define a worker function `fetch_one(ticker)` that encapsulates the
#           per‑ticker logic (next bullets). Submit all tickers to the
#           executor, collect `Future` objects, and later re‑order results
#           based on the original ticker list.
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Inside `fetch_one(ticker)`, call `yfinance.download(ticker, period='max',
#   interval='1d', auto_adjust=False, progress=False, threads=False)` to
#   obtain a pandas DataFrame.
#   Reason: Using `period='max'` guarantees the longest available history; disabling
#           auto‑adjust preserves the raw OHLCV columns needed later.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Import `yfinance as yf`; invoke `df = yf.download(ticker, period='max',
#           interval='1d', auto_adjust=False, progress=False,
#           threads=False)`.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: If the returned DataFrame is empty or `None`, log a warning, return an empty
#   CSV string (`""`) and a record count of `0` for that ticker.
#   Reason: Ensures the output lists stay aligned with the input order even when a
#           ticker has no data, allowing downstream nodes to handle missing
#           data gracefully.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Check `if df is None or df.empty:`; use Python's `logging` module to emit a
#           warning with the ticker name.
# 
# -----------------------------------------------------------------------------
# 6. BULLET: Force the DataFrame index to be a timezone‑aware `DatetimeIndex` in UTC.
#   Reason: Downstream alignment on a common business‑day index assumes UTC; naive
#           timestamps cause mismatches and subtle bugs in time‑series
#           operations.
#   Impact: HIGH
#   Complexity: LOW
#   Method: If `df.index.tz` is `None`, apply `df.index = df.index.tz_localize('UTC')`;
#           otherwise, convert with `df.index =
#           df.index.tz_convert('UTC')`.
# 
# -----------------------------------------------------------------------------
# 7. BULLET: Standardize the column set to exactly `['Open', 'High', 'Low', 'Close', 'Adj
#   Close', 'Volume']` in that order.
#   Reason: Consistent column ordering simplifies CSV generation and guarantees
#           downstream parsers receive expected fields.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Define `required_cols = ['Open', 'High', 'Low', 'Close', 'Adj Close',
#           'Volume']`. Reindex the DataFrame: `df =
#           df.reindex(columns=required_cols)`. Missing columns will be
#           filled with `NaN`; extra columns are dropped.
# 
# -----------------------------------------------------------------------------
# 8. BULLET: Sort the DataFrame by index ascending to guarantee chronological order.
#   Reason: Chronological order is required for back‑testing calculations that assume
#           forward progression of time.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Execute `df.sort_index(inplace=True)`.
# 
# -----------------------------------------------------------------------------
# 9. BULLET: Serialize the validated DataFrame to a CSV‑formatted string while preserving
#   the index as the first column named `Date`.
#   Reason: The downstream back‑test node expects CSV strings that include the date
#           index for proper alignment.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Use `io.StringIO()` as an in‑memory buffer: `buf = io.StringIO();
#           df.to_csv(buf, index=True, header=True,
#           date_format='%Y-%m-%d'); csv_str = buf.getvalue();
#           buf.close()`.
# 
# -----------------------------------------------------------------------------
# 10. BULLET: Capture the record count as `len(df)` (number of trading days).
#   Reason: Provides a quick sanity check for each ticker and is required for the
#           `record_counts` output field.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Assign `record_count = int(df.shape[0])`.
# 
# -----------------------------------------------------------------------------
# 11. BULLET: Return a tuple `(ticker, csv_str, record_count)` from `fetch_one`; on
#   exception, catch, log the exception, and return `(ticker, "", 0)`.
#   Reason: Guarantees that the main thread can always assemble results in the original
#           order, regardless of per‑ticker failures.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Wrap the logic in a `try/except Exception as e:` block; use `logging.error`
#           to capture stack trace.
# 
# -----------------------------------------------------------------------------
# 12. BULLET: After all futures complete, reconstruct three ordered lists (`tickers_out`,
#   `csv_out`, `counts_out`) by iterating over the original ticker order and
#   pulling the corresponding tuple from the future results.
#   Reason: ThreadPoolExecutor does not preserve submission order when retrieving
#           results; explicit re‑ordering ensures deterministic output
#           alignment.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Create a dict `result_map[ticker] = (csv_str, count)` inside the worker;
#           after `as_completed`, fill the dict. Finally, for `t in
#           original_tickers: tickers_out.append(t);
#           csv_out.append(result_map[t][0]);
#           counts_out.append(result_map[t][1])`.
# 
# -----------------------------------------------------------------------------
# 13. BULLET: Validate that the three output lists have identical lengths and that each
#   element in `record_counts` is a non‑negative integer.
#   Reason: Prevents schema violations before the node returns its payload, ensuring
#           downstream type safety.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Assert `len(tickers_out) == len(csv_out) == len(counts_out)`; loop through
#           `counts_out` to assert `isinstance(c, int) and c >= 0`.
# 
# -----------------------------------------------------------------------------
# 14. BULLET: Assemble the final JSON payload with keys `tickers`, `data_csv`, and
#   `record_counts` using the three ordered lists.
#   Reason: Matches the exact output structure required by downstream nodes and the
#           system's type‑checking layer.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Return `{"tickers": tickers_out, "data_csv": csv_out, "record_counts":
#           counts_out}`.
# 
# -----------------------------------------------------------------------------
# 15. BULLET: Implement a top‑level try/except around the entire orchestration to catch
#   unexpected errors, log a fatal error, and raise a `RuntimeError` with a
#   concise message.
#   Reason: Ensures that a failure surface is visible to the workflow engine, which can
#           then trigger the companion `fetch_stock_data_yahoo_status` node
#           for graceful degradation.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Wrap the main function body in `try: ... except Exception as e:
#           logging.exception('fetch_stock_data_yahoo_data failed'); raise
#           RuntimeError(str(e))`.
# 
# -----------------------------------------------------------------------------
# 16. BULLET: Add optional configuration parameters (environment variables or function
#   arguments) for max workers, request timeout, and retry count, but default
#   them to safe values (e.g., `max_workers = min(32, os.cpu_count() + 4)`).
#   Reason: Provides flexibility for production deployments where rate‑limit handling
#           or resource constraints differ.
#   Impact: LOW
#   Complexity: MEDIUM
#   Method: Read `os.getenv('YF_MAX_WORKERS')` and cast to int; pass to
#           `ThreadPoolExecutor(max_workers=...)`. Use
#           `requests.adapters.HTTPAdapter(max_retries=3)` if needed.
# 
# -----------------------------------------------------------------------------
# 17. BULLET: Document the module with a docstring that outlines the input expectations,
#   output schema, and any side‑effects (e.g., network I/O, logging).
#   Reason: Facilitates maintainability and future extensions by other developers.
#   Impact: LOW
#   Complexity: LOW
#   Method: Write a triple‑quoted string at the top of the Python file describing the
#           function `fetch_stock_data_yahoo_data`.
# -- END PRD --

from pydantic import BaseModel, Field
from typing import List


class FetchStockDataYahooDataOutput(BaseModel):
    """Pydantic model for fetch_stock_data_yahoo_data node outputs."""
    tickers: List[str] = Field(..., description="Ordered list of ticker symbols for which historical data was fetched.")
    data_csv: List[str] = Field(..., description="CSV\u2011formatted string of the OHLCV data for each ticker, preserving dates as the index; list order matches `tickers`.")
    record_counts: List[int] = Field(..., description="Number of rows (trading days) retrieved for each ticker, aligned with the order of `tickers`.")


def fetch_stock_data_yahoo_data(general_input: str, **kwargs) -> FetchStockDataYahooDataOutput:
    """Downloads historical OHLCV data for each ticker in the asset universe and returns the raw ticker list, CSV‑encoded data strings, and per‑ticker record counts.

    Args:
        general_input: General input string for the root node.
        **kwargs: Additional keyword arguments.

    Returns:
        FetchStockDataYahooDataOutput: Object containing outputs for this node.
    """
    # TODO: Implement this function

    # Return stub output with placeholder values
    return FetchStockDataYahooDataOutput(
        tickers=[],
        data_csv=[],
        record_counts=[],
    )