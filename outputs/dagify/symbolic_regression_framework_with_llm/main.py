import os
import asyncio
import functools
import inspect
import json
import sys
from typing import Dict, Any, List, Callable, Coroutine, Union, Optional

from code.configure_llm_for_proposal_generation import configure_llm_for_proposal_generation
from code.define_symbolic_regression_objective import define_symbolic_regression_objective
from code.evaluate_proposal_quality import evaluate_proposal_quality
from code.finalize_symbolic_regression_framework import finalize_symbolic_regression_framework
from code.generate_symbolic_regression_proposals import generate_symbolic_regression_proposals
from code.integrate_refined_proposals_into_framework import integrate_refined_proposals_into_framework
from code.refine_selected_proposals import refine_selected_proposals
from code.select_top_proposals import select_top_proposals
from code.test_symbolic_regression_framework import test_symbolic_regression_framework

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

configure_llm_for_proposal_generation_async = make_async(configure_llm_for_proposal_generation)
define_symbolic_regression_objective_async = make_async(define_symbolic_regression_objective)
evaluate_proposal_quality_async = make_async(evaluate_proposal_quality)
finalize_symbolic_regression_framework_async = make_async(finalize_symbolic_regression_framework)
generate_symbolic_regression_proposals_async = make_async(generate_symbolic_regression_proposals)
integrate_refined_proposals_into_framework_async = make_async(integrate_refined_proposals_into_framework)
refine_selected_proposals_async = make_async(refine_selected_proposals)
select_top_proposals_async = make_async(select_top_proposals)
test_symbolic_regression_framework_async = make_async(test_symbolic_regression_framework)

async def run_workflow(user_input: str) -> Dict[str, Any]:
    """Execute the workflow by running each level in the topological sort.

    Args:
        user_input: The input string for the workflow

    Returns:
        Dict containing all results keyed by node name
    """
    # Store results for each node
    results = {}

    # Level 0: define_symbolic_regression_objective
    async def run_define_symbolic_regression_objective():
        # Call the async version of define_symbolic_regression_objective with results from dependencies
        return await define_symbolic_regression_objective_async(user_input)

    # Run level 0 nodes in parallel
    results['define_symbolic_regression_objective'] = await run_define_symbolic_regression_objective()

    # Level 1: configure_llm_for_proposal_generation
    async def run_configure_llm_for_proposal_generation():
        # Call the async version of configure_llm_for_proposal_generation with results from dependencies
        return await configure_llm_for_proposal_generation_async(results['define_symbolic_regression_objective'])

    # Run level 1 nodes in parallel
    results['configure_llm_for_proposal_generation'] = await run_configure_llm_for_proposal_generation()

    # Level 2: generate_symbolic_regression_proposals
    async def run_generate_symbolic_regression_proposals():
        # Call the async version of generate_symbolic_regression_proposals with results from dependencies
        return await generate_symbolic_regression_proposals_async(results['configure_llm_for_proposal_generation'])

    # Run level 2 nodes in parallel
    results['generate_symbolic_regression_proposals'] = await run_generate_symbolic_regression_proposals()

    # Level 3: evaluate_proposal_quality
    async def run_evaluate_proposal_quality():
        # Call the async version of evaluate_proposal_quality with results from dependencies
        return await evaluate_proposal_quality_async(results['generate_symbolic_regression_proposals'])

    # Run level 3 nodes in parallel
    results['evaluate_proposal_quality'] = await run_evaluate_proposal_quality()

    # Level 4: select_top_proposals
    async def run_select_top_proposals():
        # Call the async version of select_top_proposals with results from dependencies
        return await select_top_proposals_async(results['evaluate_proposal_quality'])

    # Run level 4 nodes in parallel
    results['select_top_proposals'] = await run_select_top_proposals()

    # Level 5: refine_selected_proposals
    async def run_refine_selected_proposals():
        # Call the async version of refine_selected_proposals with results from dependencies
        return await refine_selected_proposals_async(results['select_top_proposals'])

    # Run level 5 nodes in parallel
    results['refine_selected_proposals'] = await run_refine_selected_proposals()

    # Level 6: integrate_refined_proposals_into_framework
    async def run_integrate_refined_proposals_into_framework():
        # Call the async version of integrate_refined_proposals_into_framework with results from dependencies
        return await integrate_refined_proposals_into_framework_async(results['refine_selected_proposals'])

    # Run level 6 nodes in parallel
    results['integrate_refined_proposals_into_framework'] = await run_integrate_refined_proposals_into_framework()

    # Level 7: test_symbolic_regression_framework
    async def run_test_symbolic_regression_framework():
        # Call the async version of test_symbolic_regression_framework with results from dependencies
        return await test_symbolic_regression_framework_async(results['integrate_refined_proposals_into_framework'])

    # Run level 7 nodes in parallel
    results['test_symbolic_regression_framework'] = await run_test_symbolic_regression_framework()

    # Level 8: finalize_symbolic_regression_framework
    async def run_finalize_symbolic_regression_framework():
        # Call the async version of finalize_symbolic_regression_framework with results from dependencies
        return await finalize_symbolic_regression_framework_async(results['test_symbolic_regression_framework'])

    # Run level 8 nodes in parallel
    results['finalize_symbolic_regression_framework'] = await run_finalize_symbolic_regression_framework()

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
