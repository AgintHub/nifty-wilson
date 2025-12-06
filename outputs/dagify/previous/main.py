import os
import asyncio
import functools
import inspect
import json
import sys
from typing import Dict, Any, List, Callable, Coroutine, Union, Optional

from code.apply_hardening_flags import apply_hardening_flags
from code.build_openssl import build_openssl
from code.collect_current_openssl_source import collect_current_openssl_source
from code.document_changes import document_changes
from code.generate_security_report import generate_security_report
from code.identify_known_vulnerabilities import identify_known_vulnerabilities
from code.integrate_patch import integrate_patch
from code.re_run_dynamic_tests import re_run_dynamic_tests
from code.re_run_fuzzing import re_run_fuzzing
from code.re_run_static_analysis import re_run_static_analysis
from code.release_artifacts import release_artifacts
from code.run_dynamic_tests import run_dynamic_tests
from code.run_fuzzing import run_fuzzing
from code.run_static_analysis import run_static_analysis
from code.setup_dynamic_testing_environment import setup_dynamic_testing_environment
from code.setup_fuzzing_environment import setup_fuzzing_environment
from code.setup_static_analysis_environment import setup_static_analysis_environment
from code.verify_build_security import verify_build_security

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

apply_hardening_flags_async = make_async(apply_hardening_flags)
build_openssl_async = make_async(build_openssl)
collect_current_openssl_source_async = make_async(collect_current_openssl_source)
document_changes_async = make_async(document_changes)
generate_security_report_async = make_async(generate_security_report)
identify_known_vulnerabilities_async = make_async(identify_known_vulnerabilities)
integrate_patch_async = make_async(integrate_patch)
re_run_dynamic_tests_async = make_async(re_run_dynamic_tests)
re_run_fuzzing_async = make_async(re_run_fuzzing)
re_run_static_analysis_async = make_async(re_run_static_analysis)
release_artifacts_async = make_async(release_artifacts)
run_dynamic_tests_async = make_async(run_dynamic_tests)
run_fuzzing_async = make_async(run_fuzzing)
run_static_analysis_async = make_async(run_static_analysis)
setup_dynamic_testing_environment_async = make_async(setup_dynamic_testing_environment)
setup_fuzzing_environment_async = make_async(setup_fuzzing_environment)
setup_static_analysis_environment_async = make_async(setup_static_analysis_environment)
verify_build_security_async = make_async(verify_build_security)

async def run_workflow(user_input: str) -> Dict[str, Any]:
    """Execute the workflow by running each level in the topological sort.

    Args:
        user_input: The input string for the workflow

    Returns:
        Dict containing all results keyed by node name
    """
    # Store results for each node
    results = {}

    # Level 0: collect_current_openssl_source, identify_known_vulnerabilities, setup_fuzzing_environment, setup_dynamic_testing_environment, setup_static_analysis_environment
    async def run_collect_current_openssl_source():
        # Call the async version of collect_current_openssl_source with results from dependencies
        return await collect_current_openssl_source_async(user_input)

    async def run_identify_known_vulnerabilities():
        # Call the async version of identify_known_vulnerabilities with results from dependencies
        return await identify_known_vulnerabilities_async(user_input)

    async def run_setup_fuzzing_environment():
        # Call the async version of setup_fuzzing_environment with results from dependencies
        return await setup_fuzzing_environment_async(user_input)

    async def run_setup_dynamic_testing_environment():
        # Call the async version of setup_dynamic_testing_environment with results from dependencies
        return await setup_dynamic_testing_environment_async(user_input)

    async def run_setup_static_analysis_environment():
        # Call the async version of setup_static_analysis_environment with results from dependencies
        return await setup_static_analysis_environment_async(user_input)

    # Run level 0 nodes in parallel
    level_0_results = await asyncio.gather(run_collect_current_openssl_source(), run_identify_known_vulnerabilities(), run_setup_fuzzing_environment(), run_setup_dynamic_testing_environment(), run_setup_static_analysis_environment())
    results['collect_current_openssl_source'] = level_0_results[0]
    results['identify_known_vulnerabilities'] = level_0_results[1]
    results['setup_fuzzing_environment'] = level_0_results[2]
    results['setup_dynamic_testing_environment'] = level_0_results[3]
    results['setup_static_analysis_environment'] = level_0_results[4]

    # Level 1: run_dynamic_tests, run_static_analysis, run_fuzzing, integrate_patch
    async def run_run_dynamic_tests():
        # Call the async version of run_dynamic_tests with results from dependencies
        return await run_dynamic_tests_async(results['collect_current_openssl_source'], results['setup_dynamic_testing_environment'])

    async def run_run_static_analysis():
        # Call the async version of run_static_analysis with results from dependencies
        return await run_static_analysis_async(results['collect_current_openssl_source'], results['setup_static_analysis_environment'])

    async def run_run_fuzzing():
        # Call the async version of run_fuzzing with results from dependencies
        return await run_fuzzing_async(results['collect_current_openssl_source'], results['setup_fuzzing_environment'])

    async def run_integrate_patch():
        # Call the async version of integrate_patch with results from dependencies
        return await integrate_patch_async(results['identify_known_vulnerabilities'])

    # Run level 1 nodes in parallel
    level_1_results = await asyncio.gather(run_run_dynamic_tests(), run_run_static_analysis(), run_run_fuzzing(), run_integrate_patch())
    results['run_dynamic_tests'] = level_1_results[0]
    results['run_static_analysis'] = level_1_results[1]
    results['run_fuzzing'] = level_1_results[2]
    results['integrate_patch'] = level_1_results[3]

    # Level 2: apply_hardening_flags
    async def run_apply_hardening_flags():
        # Call the async version of apply_hardening_flags with results from dependencies
        return await apply_hardening_flags_async(results['integrate_patch'])

    # Run level 2 nodes in parallel
    results['apply_hardening_flags'] = await run_apply_hardening_flags()

    # Level 3: build_openssl
    async def run_build_openssl():
        # Call the async version of build_openssl with results from dependencies
        return await build_openssl_async(results['apply_hardening_flags'])

    # Run level 3 nodes in parallel
    results['build_openssl'] = await run_build_openssl()

    # Level 4: re_run_static_analysis, verify_build_security, re_run_dynamic_tests, re_run_fuzzing
    async def run_re_run_static_analysis():
        # Call the async version of re_run_static_analysis with results from dependencies
        return await re_run_static_analysis_async(results['build_openssl'], results['setup_static_analysis_environment'])

    async def run_verify_build_security():
        # Call the async version of verify_build_security with results from dependencies
        return await verify_build_security_async(results['build_openssl'])

    async def run_re_run_dynamic_tests():
        # Call the async version of re_run_dynamic_tests with results from dependencies
        return await re_run_dynamic_tests_async(results['build_openssl'], results['setup_dynamic_testing_environment'])

    async def run_re_run_fuzzing():
        # Call the async version of re_run_fuzzing with results from dependencies
        return await re_run_fuzzing_async(results['build_openssl'], results['setup_fuzzing_environment'])

    # Run level 4 nodes in parallel
    level_4_results = await asyncio.gather(run_re_run_static_analysis(), run_verify_build_security(), run_re_run_dynamic_tests(), run_re_run_fuzzing())
    results['re_run_static_analysis'] = level_4_results[0]
    results['verify_build_security'] = level_4_results[1]
    results['re_run_dynamic_tests'] = level_4_results[2]
    results['re_run_fuzzing'] = level_4_results[3]

    # Level 5: generate_security_report
    async def run_generate_security_report():
        # Call the async version of generate_security_report with results from dependencies
        return await generate_security_report_async(results['run_static_analysis'], results['run_dynamic_tests'], results['run_fuzzing'], results['re_run_static_analysis'], results['re_run_dynamic_tests'], results['re_run_fuzzing'])

    # Run level 5 nodes in parallel
    results['generate_security_report'] = await run_generate_security_report()

    # Level 6: document_changes
    async def run_document_changes():
        # Call the async version of document_changes with results from dependencies
        return await document_changes_async(results['generate_security_report'])

    # Run level 6 nodes in parallel
    results['document_changes'] = await run_document_changes()

    # Level 7: release_artifacts
    async def run_release_artifacts():
        # Call the async version of release_artifacts with results from dependencies
        return await release_artifacts_async(results['document_changes'])

    # Run level 7 nodes in parallel
    results['release_artifacts'] = await run_release_artifacts()

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
