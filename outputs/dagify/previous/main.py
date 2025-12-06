import os
import asyncio
import functools
import inspect
import json
import sys
from typing import Dict, Any, List, Callable, Coroutine, Union, Optional

from code.build_research_capabilities import build_research_capabilities
from code.choose_legal_structure import choose_legal_structure
from code.compile_business_plan import compile_business_plan
from code.create_hiring_strategy import create_hiring_strategy
from code.create_launch_timeline import create_launch_timeline
from code.define_capital_requirements import define_capital_requirements
from code.define_core_trading_philosophy import define_core_trading_philosophy
from code.design_data_infrastructure import design_data_infrastructure
from code.design_performance_measurement import design_performance_measurement
from code.design_risk_management_framework import design_risk_management_framework
from code.design_trading_strategies import design_trading_strategies
from code.develop_compliance_program import develop_compliance_program
from code.establish_operational_workflows import establish_operational_workflows
from code.identify_prime_brokerage_partners import identify_prime_brokerage_partners
from code.identify_regulatory_requirements import identify_regulatory_requirements
from code.select_primary_markets import select_primary_markets
from code.specify_technology_architecture import specify_technology_architecture

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

build_research_capabilities_async = make_async(build_research_capabilities)
choose_legal_structure_async = make_async(choose_legal_structure)
compile_business_plan_async = make_async(compile_business_plan)
create_hiring_strategy_async = make_async(create_hiring_strategy)
create_launch_timeline_async = make_async(create_launch_timeline)
define_capital_requirements_async = make_async(define_capital_requirements)
define_core_trading_philosophy_async = make_async(define_core_trading_philosophy)
design_data_infrastructure_async = make_async(design_data_infrastructure)
design_performance_measurement_async = make_async(design_performance_measurement)
design_risk_management_framework_async = make_async(design_risk_management_framework)
design_trading_strategies_async = make_async(design_trading_strategies)
develop_compliance_program_async = make_async(develop_compliance_program)
establish_operational_workflows_async = make_async(establish_operational_workflows)
identify_prime_brokerage_partners_async = make_async(identify_prime_brokerage_partners)
identify_regulatory_requirements_async = make_async(identify_regulatory_requirements)
select_primary_markets_async = make_async(select_primary_markets)
specify_technology_architecture_async = make_async(specify_technology_architecture)

async def run_workflow(user_input: str) -> Dict[str, Any]:
    """Execute the workflow by running each level in the topological sort.

    Args:
        user_input: The input string for the workflow

    Returns:
        Dict containing all results keyed by node name
    """
    # Store results for each node
    results = {}

    # Level 0: choose_legal_structure, define_core_trading_philosophy
    async def run_choose_legal_structure():
        # Call the async version of choose_legal_structure with results from dependencies
        return await choose_legal_structure_async(user_input)

    async def run_define_core_trading_philosophy():
        # Call the async version of define_core_trading_philosophy with results from dependencies
        return await define_core_trading_philosophy_async(user_input)

    # Run level 0 nodes in parallel
    level_0_results = await asyncio.gather(run_choose_legal_structure(), run_define_core_trading_philosophy())
    results['choose_legal_structure'] = level_0_results[0]
    results['define_core_trading_philosophy'] = level_0_results[1]

    # Level 1: select_primary_markets
    async def run_select_primary_markets():
        # Call the async version of select_primary_markets with results from dependencies
        return await select_primary_markets_async(results['define_core_trading_philosophy'])

    # Run level 1 nodes in parallel
    results['select_primary_markets'] = await run_select_primary_markets()

    # Level 2: identify_regulatory_requirements, design_trading_strategies
    async def run_identify_regulatory_requirements():
        # Call the async version of identify_regulatory_requirements with results from dependencies
        return await identify_regulatory_requirements_async(results['choose_legal_structure'], results['select_primary_markets'])

    async def run_design_trading_strategies():
        # Call the async version of design_trading_strategies with results from dependencies
        return await design_trading_strategies_async(results['define_core_trading_philosophy'], results['select_primary_markets'])

    # Run level 2 nodes in parallel
    level_2_results = await asyncio.gather(run_identify_regulatory_requirements(), run_design_trading_strategies())
    results['identify_regulatory_requirements'] = level_2_results[0]
    results['design_trading_strategies'] = level_2_results[1]

    # Level 3: design_risk_management_framework, specify_technology_architecture, develop_compliance_program
    async def run_design_risk_management_framework():
        # Call the async version of design_risk_management_framework with results from dependencies
        return await design_risk_management_framework_async(results['design_trading_strategies'])

    async def run_specify_technology_architecture():
        # Call the async version of specify_technology_architecture with results from dependencies
        return await specify_technology_architecture_async(results['design_trading_strategies'])

    async def run_develop_compliance_program():
        # Call the async version of develop_compliance_program with results from dependencies
        return await develop_compliance_program_async(results['identify_regulatory_requirements'])

    # Run level 3 nodes in parallel
    level_3_results = await asyncio.gather(run_design_risk_management_framework(), run_specify_technology_architecture(), run_develop_compliance_program())
    results['design_risk_management_framework'] = level_3_results[0]
    results['specify_technology_architecture'] = level_3_results[1]
    results['develop_compliance_program'] = level_3_results[2]

    # Level 4: create_hiring_strategy, design_data_infrastructure, define_capital_requirements
    async def run_create_hiring_strategy():
        # Call the async version of create_hiring_strategy with results from dependencies
        return await create_hiring_strategy_async(results['specify_technology_architecture'], results['design_trading_strategies'])

    async def run_design_data_infrastructure():
        # Call the async version of design_data_infrastructure with results from dependencies
        return await design_data_infrastructure_async(results['specify_technology_architecture'])

    async def run_define_capital_requirements():
        # Call the async version of define_capital_requirements with results from dependencies
        return await define_capital_requirements_async(results['identify_regulatory_requirements'], results['design_risk_management_framework'])

    # Run level 4 nodes in parallel
    level_4_results = await asyncio.gather(run_create_hiring_strategy(), run_design_data_infrastructure(), run_define_capital_requirements())
    results['create_hiring_strategy'] = level_4_results[0]
    results['design_data_infrastructure'] = level_4_results[1]
    results['define_capital_requirements'] = level_4_results[2]

    # Level 5: identify_prime_brokerage_partners, build_research_capabilities
    async def run_identify_prime_brokerage_partners():
        # Call the async version of identify_prime_brokerage_partners with results from dependencies
        return await identify_prime_brokerage_partners_async(results['select_primary_markets'], results['define_capital_requirements'])

    async def run_build_research_capabilities():
        # Call the async version of build_research_capabilities with results from dependencies
        return await build_research_capabilities_async(results['design_data_infrastructure'], results['create_hiring_strategy'])

    # Run level 5 nodes in parallel
    level_5_results = await asyncio.gather(run_identify_prime_brokerage_partners(), run_build_research_capabilities())
    results['identify_prime_brokerage_partners'] = level_5_results[0]
    results['build_research_capabilities'] = level_5_results[1]

    # Level 6: establish_operational_workflows
    async def run_establish_operational_workflows():
        # Call the async version of establish_operational_workflows with results from dependencies
        return await establish_operational_workflows_async(results['design_risk_management_framework'], results['identify_prime_brokerage_partners'], results['develop_compliance_program'])

    # Run level 6 nodes in parallel
    results['establish_operational_workflows'] = await run_establish_operational_workflows()

    # Level 7: design_performance_measurement
    async def run_design_performance_measurement():
        # Call the async version of design_performance_measurement with results from dependencies
        return await design_performance_measurement_async(results['establish_operational_workflows'])

    # Run level 7 nodes in parallel
    results['design_performance_measurement'] = await run_design_performance_measurement()

    # Level 8: create_launch_timeline
    async def run_create_launch_timeline():
        # Call the async version of create_launch_timeline with results from dependencies
        return await create_launch_timeline_async(results['build_research_capabilities'], results['design_performance_measurement'])

    # Run level 8 nodes in parallel
    results['create_launch_timeline'] = await run_create_launch_timeline()

    # Level 9: compile_business_plan
    async def run_compile_business_plan():
        # Call the async version of compile_business_plan with results from dependencies
        return await compile_business_plan_async(results['create_launch_timeline'])

    # Run level 9 nodes in parallel
    results['compile_business_plan'] = await run_compile_business_plan()

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
