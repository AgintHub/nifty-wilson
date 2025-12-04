import os
import asyncio
import functools
import inspect
import json
import sys
from typing import Dict, Any, List, Callable, Coroutine, Union, Optional

from code.backtest_trading_strategy import backtest_trading_strategy
from code.compile_final_strategy_blueprint import compile_final_strategy_blueprint
from code.define_market_analysis import define_market_analysis
from code.define_risk_management_rules import define_risk_management_rules
from code.develop_trading_signal_logic import develop_trading_signal_logic
from code.fetch_stock_data_yahoo_data import fetch_stock_data_yahoo_data
from code.fetch_stock_data_yahoo_status import fetch_stock_data_yahoo_status
from code.identify_trading_indicators import identify_trading_indicators
from code.refine_trading_strategy import refine_trading_strategy
from code.select_trading_strategy_type import select_trading_strategy_type
from code.specify_asset_universe import specify_asset_universe

# Get async mode from environment variable or default to False
ASYNC_MODE = os.environ.get('ASYNC_MODE', '').lower() in ('true', '1', 'yes', 'y')

def make_async(func):
    """Convert a synchronous function to an asynchronous function.

    If the function is already asynchronous, return it unchanged.
    If the function is synchronous, wrap it in an async function.
    """
    # If it's already a coroutine function, return it as is
    if inspect.iscoroutinefunction(func):
        return func

    # Otherwise, wrap it as an async function
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return async_wrapper

backtest_trading_strategy_async = make_async(backtest_trading_strategy)
compile_final_strategy_blueprint_async = make_async(compile_final_strategy_blueprint)
define_market_analysis_async = make_async(define_market_analysis)
define_risk_management_rules_async = make_async(define_risk_management_rules)
develop_trading_signal_logic_async = make_async(develop_trading_signal_logic)
fetch_stock_data_yahoo_data_async = make_async(fetch_stock_data_yahoo_data)
fetch_stock_data_yahoo_status_async = make_async(fetch_stock_data_yahoo_status)
identify_trading_indicators_async = make_async(identify_trading_indicators)
refine_trading_strategy_async = make_async(refine_trading_strategy)
select_trading_strategy_type_async = make_async(select_trading_strategy_type)
specify_asset_universe_async = make_async(specify_asset_universe)

async def run_workflow(user_input: str) -> Dict[str, Any]:
    """Execute the workflow by running each level in the topological sort.

    Args:
        user_input: The input string for the workflow

    Returns:
        Dict containing all results keyed by node name
    """
    # Store results for each node
    results = {}

    # Level 0: fetch_stock_data_yahoo_status, define_market_analysis, fetch_stock_data_yahoo_data
    async def run_fetch_stock_data_yahoo_status():
        # Call the async version of fetch_stock_data_yahoo_status with results from dependencies
        return await fetch_stock_data_yahoo_status_async(user_input)

    async def run_define_market_analysis():
        # Call the async version of define_market_analysis with results from dependencies
        return await define_market_analysis_async(user_input)

    async def run_fetch_stock_data_yahoo_data():
        # Call the async version of fetch_stock_data_yahoo_data with results from dependencies
        return await fetch_stock_data_yahoo_data_async(user_input)

    # Run level 0 nodes in parallel
    level_0_results = await asyncio.gather(run_fetch_stock_data_yahoo_status(), run_define_market_analysis(), run_fetch_stock_data_yahoo_data())
    results['fetch_stock_data_yahoo_status'] = level_0_results[0]
    results['define_market_analysis'] = level_0_results[1]
    results['fetch_stock_data_yahoo_data'] = level_0_results[2]

    # Level 1: select_trading_strategy_type
    async def run_select_trading_strategy_type():
        # Call the async version of select_trading_strategy_type with results from dependencies
        return await select_trading_strategy_type_async(results['define_market_analysis'])

    # Run level 1 nodes in parallel
    results['select_trading_strategy_type'] = await run_select_trading_strategy_type()

    # Level 2: define_risk_management_rules, specify_asset_universe, identify_trading_indicators
    async def run_define_risk_management_rules():
        # Call the async version of define_risk_management_rules with results from dependencies
        return await define_risk_management_rules_async(results['select_trading_strategy_type'])

    async def run_specify_asset_universe():
        # Call the async version of specify_asset_universe with results from dependencies
        return await specify_asset_universe_async(results['select_trading_strategy_type'])

    async def run_identify_trading_indicators():
        # Call the async version of identify_trading_indicators with results from dependencies
        return await identify_trading_indicators_async(results['select_trading_strategy_type'])

    # Run level 2 nodes in parallel
    level_2_results = await asyncio.gather(run_define_risk_management_rules(), run_specify_asset_universe(), run_identify_trading_indicators())
    results['define_risk_management_rules'] = level_2_results[0]
    results['specify_asset_universe'] = level_2_results[1]
    results['identify_trading_indicators'] = level_2_results[2]

    # Level 3: develop_trading_signal_logic
    async def run_develop_trading_signal_logic():
        # Call the async version of develop_trading_signal_logic with results from dependencies
        return await develop_trading_signal_logic_async(results['identify_trading_indicators'])

    # Run level 3 nodes in parallel
    results['develop_trading_signal_logic'] = await run_develop_trading_signal_logic()

    # Level 4: backtest_trading_strategy
    async def run_backtest_trading_strategy():
        # Call the async version of backtest_trading_strategy with results from dependencies
        return await backtest_trading_strategy_async(results['develop_trading_signal_logic'], results['specify_asset_universe'], results['fetch_stock_data_yahoo_data'], results['fetch_stock_data_yahoo_status'])

    # Run level 4 nodes in parallel
    results['backtest_trading_strategy'] = await run_backtest_trading_strategy()

    # Level 5: refine_trading_strategy
    async def run_refine_trading_strategy():
        # Call the async version of refine_trading_strategy with results from dependencies
        return await refine_trading_strategy_async(results['backtest_trading_strategy'])

    # Run level 5 nodes in parallel
    results['refine_trading_strategy'] = await run_refine_trading_strategy()

    # Level 6: compile_final_strategy_blueprint
    async def run_compile_final_strategy_blueprint():
        # Call the async version of compile_final_strategy_blueprint with results from dependencies
        return await compile_final_strategy_blueprint_async(results['refine_trading_strategy'], results['define_risk_management_rules'])

    # Run level 6 nodes in parallel
    results['compile_final_strategy_blueprint'] = await run_compile_final_strategy_blueprint()

    # Return all results
    return results

def run_workflow_sync(user_input: str) -> Dict[str, Any]:
    """Synchronous wrapper around the async workflow execution."""
    return asyncio.run(run_workflow(user_input))

def main():
    """Main entry point.

    Handles arguments in the following priority:
    1. Command-line argument (sys.argv[1])
    2. If no argument, uses empty string as input but displays a warning.
    """
    # Get user input from command line or use empty string
    if len(sys.argv) > 1:
        user_input = sys.argv[1]
    else:
        # No input provided - display help message but continue with empty string
        print('Warning: No input provided. Using empty string as input.')
        print('For better results, provide an input argument:')
        print(f'  python {os.path.basename(__file__)} "your input text here"')
        print('Or use a file as input:')
        print(f'  python {os.path.basename(__file__)} "$(cat input.txt)"')
        user_input = ""

    print(f'Running workflow with input: {user_input}')

    # Run the workflow
    results = run_workflow_sync(user_input)

    # Print results
    try:
        # Convert results to JSON
        json_results = json.dumps(results, indent=2, default=str)
        print(json_results)
    except (TypeError, ValueError) as e:
        print(f'Results could not be converted to JSON: {e}')
        print(f'Raw results: {results}')

    return results

if __name__ == '__main__':
    main()
