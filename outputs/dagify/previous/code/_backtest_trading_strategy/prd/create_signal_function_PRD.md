# create_signal_function PRD

## Description
Creates a callable trading signal function from textual logic steps and a list of required indicators.


## Implementation Plan

### 1. Parse the `signal_logic_steps` string into a safe executable Python function.

| Category | Details |
| --- | --- |
| **Reason** | The textual description must be transformed into executable code that can be applied to market data. |
| **Impact** | Enables dynamic generation of signal logic without manual coding, allowing end‑users to define strategies in plain language. |
| **Complexity** | MEDIUM |
| **Method** | Use the `ast` module to parse and validate the expression, then compile it with `compile()` and wrap it in a closure that receives indicator values. |

### 2. Validate that all `used_indicators` are present in the data passed to the generated function.

| Category | Details |
| --- | --- |
| **Reason** | Ensuring required indicators exist prevents runtime KeyError exceptions during backtesting. |
| **Impact** | Improves robustness of the backtest pipeline and provides clear error messages to the user. |
| **Complexity** | LOW |
| **Method** | Compare the set of indicator names extracted from the parsed logic with the `used_indicators` list; raise a descriptive `ValueError` if any are missing. |

### 3. Wrap the compiled logic into a callable that accepts a dictionary (or DataFrame row) of indicator values and returns a standard signal label (e.g., "BUY", "SELL", "NEUTRAL").

| Category | Details |
| --- | --- |
| **Reason** | Downstream nodes expect a uniform interface to generate trading signals across multiple assets. |
| **Impact** | Provides a consistent API for signal generation, simplifying integration with `generate_trading_signals` and the backtest engine. |
| **Complexity** | HIGH |
| **Method** | Create a function string like `def signal_fn(indicators): <compiled_body>`; execute it in a dedicated namespace using `exec`, capture the resulting `signal_fn`, and serialize its reference as a string (e.g., via `cloudpickle` or `inspect.getsource`). |
