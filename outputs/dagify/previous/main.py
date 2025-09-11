import os
import asyncio
import functools
import inspect
import json
import sys
from typing import Dict, Any, List, Callable, Coroutine, Union, Optional

from code.analyze_data import analyze_data
from code.collect_data import collect_data
from code.conduct_experiment import conduct_experiment
from code.design_experiment import design_experiment
from code.document_experiment import document_experiment
from code.draw_conclusion import draw_conclusion
from code.formulate_hypothesis import formulate_hypothesis
from code.interpret_results import interpret_results
from code.prepare_materials import prepare_materials

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

analyze_data_async = make_async(analyze_data)
collect_data_async = make_async(collect_data)
conduct_experiment_async = make_async(conduct_experiment)
design_experiment_async = make_async(design_experiment)
document_experiment_async = make_async(document_experiment)
draw_conclusion_async = make_async(draw_conclusion)
formulate_hypothesis_async = make_async(formulate_hypothesis)
interpret_results_async = make_async(interpret_results)
prepare_materials_async = make_async(prepare_materials)

async def run_workflow(user_input: str) -> Dict[str, Any]:
    """Execute the workflow by running each level in the topological sort.

    Args:
        user_input: The input string for the workflow

    Returns:
        Dict containing all results keyed by node name
    """
    # Store results for each node
    results = {}

    # Level 0: formulate_hypothesis
    async def run_formulate_hypothesis():
        # Call the async version of formulate_hypothesis with results from dependencies
        return await formulate_hypothesis_async(user_input)

    # Run level 0 nodes in parallel
    results['formulate_hypothesis'] = await run_formulate_hypothesis()

    # Level 1: design_experiment
    async def run_design_experiment():
        # Call the async version of design_experiment with results from dependencies
        return await design_experiment_async(results['formulate_hypothesis'])

    # Run level 1 nodes in parallel
    results['design_experiment'] = await run_design_experiment()

    # Level 2: prepare_materials
    async def run_prepare_materials():
        # Call the async version of prepare_materials with results from dependencies
        return await prepare_materials_async(results['design_experiment'])

    # Run level 2 nodes in parallel
    results['prepare_materials'] = await run_prepare_materials()

    # Level 3: conduct_experiment
    async def run_conduct_experiment():
        # Call the async version of conduct_experiment with results from dependencies
        return await conduct_experiment_async(results['design_experiment'], results['prepare_materials'])

    # Run level 3 nodes in parallel
    results['conduct_experiment'] = await run_conduct_experiment()

    # Level 4: collect_data
    async def run_collect_data():
        # Call the async version of collect_data with results from dependencies
        return await collect_data_async(results['conduct_experiment'])

    # Run level 4 nodes in parallel
    results['collect_data'] = await run_collect_data()

    # Level 5: analyze_data
    async def run_analyze_data():
        # Call the async version of analyze_data with results from dependencies
        return await analyze_data_async(results['collect_data'])

    # Run level 5 nodes in parallel
    results['analyze_data'] = await run_analyze_data()

    # Level 6: interpret_results
    async def run_interpret_results():
        # Call the async version of interpret_results with results from dependencies
        return await interpret_results_async(results['analyze_data'])

    # Run level 6 nodes in parallel
    results['interpret_results'] = await run_interpret_results()

    # Level 7: draw_conclusion
    async def run_draw_conclusion():
        # Call the async version of draw_conclusion with results from dependencies
        return await draw_conclusion_async(results['interpret_results'])

    # Run level 7 nodes in parallel
    results['draw_conclusion'] = await run_draw_conclusion()

    # Level 8: document_experiment
    async def run_document_experiment():
        # Call the async version of document_experiment with results from dependencies
        return await document_experiment_async(results['draw_conclusion'])

    # Run level 8 nodes in parallel
    results['document_experiment'] = await run_document_experiment()

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
