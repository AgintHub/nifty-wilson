import os
import asyncio
import functools
import inspect
import json
import sys
from typing import Dict, Any, List, Callable, Coroutine, Union, Optional

from code.conduct_performance_optimization import conduct_performance_optimization
from code.deploy_to_production import deploy_to_production
from code.design_database_schema import design_database_schema
from code.design_user_interface import design_user_interface
from code.develop_trading_platform_backend import develop_trading_platform_backend
from code.identify_required_data_feeds import identify_required_data_feeds
from code.implement_data_ingestion_pipeline import implement_data_ingestion_pipeline
from code.implement_forex_data_ingestion_pipeline import implement_forex_data_ingestion_pipeline
from code.implement_forex_trading_api import implement_forex_trading_api
from code.implement_trading_api import implement_trading_api
from code.implement_user_interface import implement_user_interface
from code.perform_security_auditing import perform_security_auditing
from code.select_data_providers import select_data_providers
from code.select_forex_data_providers import select_forex_data_providers

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

conduct_performance_optimization_async = make_async(conduct_performance_optimization)
deploy_to_production_async = make_async(deploy_to_production)
design_database_schema_async = make_async(design_database_schema)
design_user_interface_async = make_async(design_user_interface)
develop_trading_platform_backend_async = make_async(develop_trading_platform_backend)
identify_required_data_feeds_async = make_async(identify_required_data_feeds)
implement_data_ingestion_pipeline_async = make_async(implement_data_ingestion_pipeline)
implement_forex_data_ingestion_pipeline_async = make_async(implement_forex_data_ingestion_pipeline)
implement_forex_trading_api_async = make_async(implement_forex_trading_api)
implement_trading_api_async = make_async(implement_trading_api)
implement_user_interface_async = make_async(implement_user_interface)
perform_security_auditing_async = make_async(perform_security_auditing)
select_data_providers_async = make_async(select_data_providers)
select_forex_data_providers_async = make_async(select_forex_data_providers)

async def run_workflow(user_input: str) -> Dict[str, Any]:
    """Execute the workflow by running each level in the topological sort.

    Args:
        user_input: The input string for the workflow

    Returns:
        Dict containing all results keyed by node name
    """
    # Store results for each node
    results = {}

    # Level 0: identify_required_data_feeds
    async def run_identify_required_data_feeds():
        # Call the async version of identify_required_data_feeds with results from dependencies
        return await identify_required_data_feeds_async(user_input)

    # Run level 0 nodes in parallel
    results['identify_required_data_feeds'] = await run_identify_required_data_feeds()

    # Level 1: select_data_providers, select_forex_data_providers, design_database_schema
    async def run_select_data_providers():
        # Call the async version of select_data_providers with results from dependencies
        return await select_data_providers_async(results['identify_required_data_feeds'])

    async def run_select_forex_data_providers():
        # Call the async version of select_forex_data_providers with results from dependencies
        return await select_forex_data_providers_async(results['identify_required_data_feeds'])

    async def run_design_database_schema():
        # Call the async version of design_database_schema with results from dependencies
        return await design_database_schema_async(results['identify_required_data_feeds'])

    # Run level 1 nodes in parallel
    level_1_results = await asyncio.gather(run_select_data_providers(), run_select_forex_data_providers(), run_design_database_schema())
    results['select_data_providers'] = level_1_results[0]
    results['select_forex_data_providers'] = level_1_results[1]
    results['design_database_schema'] = level_1_results[2]

    # Level 2: implement_data_ingestion_pipeline, implement_forex_data_ingestion_pipeline
    async def run_implement_data_ingestion_pipeline():
        # Call the async version of implement_data_ingestion_pipeline with results from dependencies
        return await implement_data_ingestion_pipeline_async(results['select_data_providers'], results['design_database_schema'])

    async def run_implement_forex_data_ingestion_pipeline():
        # Call the async version of implement_forex_data_ingestion_pipeline with results from dependencies
        return await implement_forex_data_ingestion_pipeline_async(results['select_forex_data_providers'], results['design_database_schema'])

    # Run level 2 nodes in parallel
    level_2_results = await asyncio.gather(run_implement_data_ingestion_pipeline(), run_implement_forex_data_ingestion_pipeline())
    results['implement_data_ingestion_pipeline'] = level_2_results[0]
    results['implement_forex_data_ingestion_pipeline'] = level_2_results[1]

    # Level 3: develop_trading_platform_backend
    async def run_develop_trading_platform_backend():
        # Call the async version of develop_trading_platform_backend with results from dependencies
        return await develop_trading_platform_backend_async(results['implement_data_ingestion_pipeline'])

    # Run level 3 nodes in parallel
    results['develop_trading_platform_backend'] = await run_develop_trading_platform_backend()

    # Level 4: implement_forex_trading_api, implement_trading_api
    async def run_implement_forex_trading_api():
        # Call the async version of implement_forex_trading_api with results from dependencies
        return await implement_forex_trading_api_async(results['develop_trading_platform_backend'], results['implement_forex_data_ingestion_pipeline'])

    async def run_implement_trading_api():
        # Call the async version of implement_trading_api with results from dependencies
        return await implement_trading_api_async(results['develop_trading_platform_backend'])

    # Run level 4 nodes in parallel
    level_4_results = await asyncio.gather(run_implement_forex_trading_api(), run_implement_trading_api())
    results['implement_forex_trading_api'] = level_4_results[0]
    results['implement_trading_api'] = level_4_results[1]

    # Level 5: design_user_interface
    async def run_design_user_interface():
        # Call the async version of design_user_interface with results from dependencies
        return await design_user_interface_async(results['implement_trading_api'])

    # Run level 5 nodes in parallel
    results['design_user_interface'] = await run_design_user_interface()

    # Level 6: implement_user_interface
    async def run_implement_user_interface():
        # Call the async version of implement_user_interface with results from dependencies
        return await implement_user_interface_async(results['design_user_interface'], results['implement_trading_api'])

    # Run level 6 nodes in parallel
    results['implement_user_interface'] = await run_implement_user_interface()

    # Level 7: perform_security_auditing, conduct_performance_optimization
    async def run_perform_security_auditing():
        # Call the async version of perform_security_auditing with results from dependencies
        return await perform_security_auditing_async(results['implement_user_interface'], results['implement_trading_api'])

    async def run_conduct_performance_optimization():
        # Call the async version of conduct_performance_optimization with results from dependencies
        return await conduct_performance_optimization_async(results['implement_user_interface'], results['implement_trading_api'])

    # Run level 7 nodes in parallel
    level_7_results = await asyncio.gather(run_perform_security_auditing(), run_conduct_performance_optimization())
    results['perform_security_auditing'] = level_7_results[0]
    results['conduct_performance_optimization'] = level_7_results[1]

    # Level 8: deploy_to_production
    async def run_deploy_to_production():
        # Call the async version of deploy_to_production with results from dependencies
        return await deploy_to_production_async(results['conduct_performance_optimization'], results['perform_security_auditing'])

    # Run level 8 nodes in parallel
    results['deploy_to_production'] = await run_deploy_to_production()

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
