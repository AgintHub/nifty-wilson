import os
import asyncio
import functools
import inspect
import json
import sys
from typing import Dict, Any, List, Callable, Coroutine, Union, Optional

from code.allocate_resources import allocate_resources
from code.create_vocabulary import create_vocabulary
from code.define_model_architecture import define_model_architecture
from code.evaluate_model import evaluate_model
from code.fine_tune_model import fine_tune_model
from code.initialize_model_weights import initialize_model_weights
from code.load_configuration import load_configuration
from code.prepare_training_data import prepare_training_data
from code.setup_environment import setup_environment
from code.split_data import split_data
from code.test_model import test_model
from code.tokenize_data import tokenize_data
from code.train_model import train_model

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

allocate_resources_async = make_async(allocate_resources)
create_vocabulary_async = make_async(create_vocabulary)
define_model_architecture_async = make_async(define_model_architecture)
evaluate_model_async = make_async(evaluate_model)
fine_tune_model_async = make_async(fine_tune_model)
initialize_model_weights_async = make_async(initialize_model_weights)
load_configuration_async = make_async(load_configuration)
prepare_training_data_async = make_async(prepare_training_data)
setup_environment_async = make_async(setup_environment)
split_data_async = make_async(split_data)
test_model_async = make_async(test_model)
tokenize_data_async = make_async(tokenize_data)
train_model_async = make_async(train_model)

async def run_workflow(user_input: str) -> Dict[str, Any]:
    """Execute the workflow by running each level in the topological sort.

    Args:
        user_input: The input string for the workflow

    Returns:
        Dict containing all results keyed by node name
    """
    # Store results for each node
    results = {}

    # Level 0: prepare_training_data, setup_environment
    async def run_prepare_training_data():
        # Call the async version of prepare_training_data with results from dependencies
        return await prepare_training_data_async(user_input)

    async def run_setup_environment():
        # Call the async version of setup_environment with results from dependencies
        return await setup_environment_async(user_input)

    # Run level 0 nodes in parallel
    level_0_results = await asyncio.gather(run_prepare_training_data(), run_setup_environment())
    results['prepare_training_data'] = level_0_results[0]
    results['setup_environment'] = level_0_results[1]

    # Level 1: tokenize_data, load_configuration, split_data
    async def run_tokenize_data():
        # Call the async version of tokenize_data with results from dependencies
        return await tokenize_data_async(results['prepare_training_data'])

    async def run_load_configuration():
        # Call the async version of load_configuration with results from dependencies
        return await load_configuration_async(results['setup_environment'])

    async def run_split_data():
        # Call the async version of split_data with results from dependencies
        return await split_data_async(results['prepare_training_data'])

    # Run level 1 nodes in parallel
    level_1_results = await asyncio.gather(run_tokenize_data(), run_load_configuration(), run_split_data())
    results['tokenize_data'] = level_1_results[0]
    results['load_configuration'] = level_1_results[1]
    results['split_data'] = level_1_results[2]

    # Level 2: allocate_resources, create_vocabulary
    async def run_allocate_resources():
        # Call the async version of allocate_resources with results from dependencies
        return await allocate_resources_async(results['load_configuration'])

    async def run_create_vocabulary():
        # Call the async version of create_vocabulary with results from dependencies
        return await create_vocabulary_async(results['tokenize_data'])

    # Run level 2 nodes in parallel
    level_2_results = await asyncio.gather(run_allocate_resources(), run_create_vocabulary())
    results['allocate_resources'] = level_2_results[0]
    results['create_vocabulary'] = level_2_results[1]

    # Level 3: define_model_architecture
    async def run_define_model_architecture():
        # Call the async version of define_model_architecture with results from dependencies
        return await define_model_architecture_async(results['create_vocabulary'], results['allocate_resources'])

    # Run level 3 nodes in parallel
    results['define_model_architecture'] = await run_define_model_architecture()

    # Level 4: initialize_model_weights
    async def run_initialize_model_weights():
        # Call the async version of initialize_model_weights with results from dependencies
        return await initialize_model_weights_async(results['define_model_architecture'])

    # Run level 4 nodes in parallel
    results['initialize_model_weights'] = await run_initialize_model_weights()

    # Level 5: train_model
    async def run_train_model():
        # Call the async version of train_model with results from dependencies
        return await train_model_async(results['split_data'], results['initialize_model_weights'])

    # Run level 5 nodes in parallel
    results['train_model'] = await run_train_model()

    # Level 6: evaluate_model
    async def run_evaluate_model():
        # Call the async version of evaluate_model with results from dependencies
        return await evaluate_model_async(results['train_model'])

    # Run level 6 nodes in parallel
    results['evaluate_model'] = await run_evaluate_model()

    # Level 7: fine_tune_model
    async def run_fine_tune_model():
        # Call the async version of fine_tune_model with results from dependencies
        return await fine_tune_model_async(results['evaluate_model'])

    # Run level 7 nodes in parallel
    results['fine_tune_model'] = await run_fine_tune_model()

    # Level 8: test_model
    async def run_test_model():
        # Call the async version of test_model with results from dependencies
        return await test_model_async(results['fine_tune_model'])

    # Run level 8 nodes in parallel
    results['test_model'] = await run_test_model()

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
