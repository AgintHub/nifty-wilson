import os
import asyncio
import functools
import inspect
import json
import sys
from typing import Dict, Any, List, Callable, Coroutine, Union, Optional

from code.choose_investment_strategy import choose_investment_strategy
from code.choose_legal_entity_type import choose_legal_entity_type
from code.clarify_fund_objectives import clarify_fund_objectives
from code.compile_pitch_deck_outline import compile_pitch_deck_outline
from code.create_hiring_plan import create_hiring_plan
from code.define_asset_universe import define_asset_universe
from code.define_investor_profile import define_investor_profile
from code.define_technology_stack import define_technology_stack
from code.design_compliance_program import design_compliance_program
from code.design_risk_management_framework import design_risk_management_framework
from code.develop_timeline_and_milestones import develop_timeline_and_milestones
from code.draft_fee_structure import draft_fee_structure
from code.draft_operations_workflow import draft_operations_workflow
from code.estimate_setup_and_operating_costs import estimate_setup_and_operating_costs
from code.identify_regulatory_requirements import identify_regulatory_requirements
from code.list_service_providers import list_service_providers
from code.outline_governance_structure import outline_governance_structure
from code.produce_final_fund_plan_summary import produce_final_fund_plan_summary
from code.select_jurisdiction import select_jurisdiction
from code.set_performance_and_risk_targets import set_performance_and_risk_targets

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

choose_investment_strategy_async = make_async(choose_investment_strategy)
choose_legal_entity_type_async = make_async(choose_legal_entity_type)
clarify_fund_objectives_async = make_async(clarify_fund_objectives)
compile_pitch_deck_outline_async = make_async(compile_pitch_deck_outline)
create_hiring_plan_async = make_async(create_hiring_plan)
define_asset_universe_async = make_async(define_asset_universe)
define_investor_profile_async = make_async(define_investor_profile)
define_technology_stack_async = make_async(define_technology_stack)
design_compliance_program_async = make_async(design_compliance_program)
design_risk_management_framework_async = make_async(design_risk_management_framework)
develop_timeline_and_milestones_async = make_async(develop_timeline_and_milestones)
draft_fee_structure_async = make_async(draft_fee_structure)
draft_operations_workflow_async = make_async(draft_operations_workflow)
estimate_setup_and_operating_costs_async = make_async(estimate_setup_and_operating_costs)
identify_regulatory_requirements_async = make_async(identify_regulatory_requirements)
list_service_providers_async = make_async(list_service_providers)
outline_governance_structure_async = make_async(outline_governance_structure)
produce_final_fund_plan_summary_async = make_async(produce_final_fund_plan_summary)
select_jurisdiction_async = make_async(select_jurisdiction)
set_performance_and_risk_targets_async = make_async(set_performance_and_risk_targets)

async def run_workflow(user_input: str) -> Dict[str, Any]:
    """Execute the workflow by running each level in the topological sort.

    Args:
        user_input: The input string for the workflow

    Returns:
        Dict containing all results keyed by node name
    """
    # Store results for each node
    results = {}

    # Level 0: clarify_fund_objectives
    async def run_clarify_fund_objectives():
        # Call the async version of clarify_fund_objectives with results from dependencies
        return await clarify_fund_objectives_async(user_input)

    # Run level 0 nodes in parallel
    results['clarify_fund_objectives'] = await run_clarify_fund_objectives()

    # Level 1: define_investor_profile, select_jurisdiction, choose_investment_strategy
    async def run_define_investor_profile():
        # Call the async version of define_investor_profile with results from dependencies
        return await define_investor_profile_async(results['clarify_fund_objectives'])

    async def run_select_jurisdiction():
        # Call the async version of select_jurisdiction with results from dependencies
        return await select_jurisdiction_async(results['clarify_fund_objectives'])

    async def run_choose_investment_strategy():
        # Call the async version of choose_investment_strategy with results from dependencies
        return await choose_investment_strategy_async(results['clarify_fund_objectives'])

    # Run level 1 nodes in parallel
    level_1_results = await asyncio.gather(run_define_investor_profile(), run_select_jurisdiction(), run_choose_investment_strategy())
    results['define_investor_profile'] = level_1_results[0]
    results['select_jurisdiction'] = level_1_results[1]
    results['choose_investment_strategy'] = level_1_results[2]

    # Level 2: choose_legal_entity_type, set_performance_and_risk_targets, define_asset_universe
    async def run_choose_legal_entity_type():
        # Call the async version of choose_legal_entity_type with results from dependencies
        return await choose_legal_entity_type_async(results['select_jurisdiction'])

    async def run_set_performance_and_risk_targets():
        # Call the async version of set_performance_and_risk_targets with results from dependencies
        return await set_performance_and_risk_targets_async(results['choose_investment_strategy'])

    async def run_define_asset_universe():
        # Call the async version of define_asset_universe with results from dependencies
        return await define_asset_universe_async(results['choose_investment_strategy'])

    # Run level 2 nodes in parallel
    level_2_results = await asyncio.gather(run_choose_legal_entity_type(), run_set_performance_and_risk_targets(), run_define_asset_universe())
    results['choose_legal_entity_type'] = level_2_results[0]
    results['set_performance_and_risk_targets'] = level_2_results[1]
    results['define_asset_universe'] = level_2_results[2]

    # Level 3: outline_governance_structure, identify_regulatory_requirements, design_risk_management_framework, list_service_providers
    async def run_outline_governance_structure():
        # Call the async version of outline_governance_structure with results from dependencies
        return await outline_governance_structure_async(results['choose_legal_entity_type'])

    async def run_identify_regulatory_requirements():
        # Call the async version of identify_regulatory_requirements with results from dependencies
        return await identify_regulatory_requirements_async(results['choose_legal_entity_type'])

    async def run_design_risk_management_framework():
        # Call the async version of design_risk_management_framework with results from dependencies
        return await design_risk_management_framework_async(results['set_performance_and_risk_targets'])

    async def run_list_service_providers():
        # Call the async version of list_service_providers with results from dependencies
        return await list_service_providers_async(results['choose_legal_entity_type'])

    # Run level 3 nodes in parallel
    level_3_results = await asyncio.gather(run_outline_governance_structure(), run_identify_regulatory_requirements(), run_design_risk_management_framework(), run_list_service_providers())
    results['outline_governance_structure'] = level_3_results[0]
    results['identify_regulatory_requirements'] = level_3_results[1]
    results['design_risk_management_framework'] = level_3_results[2]
    results['list_service_providers'] = level_3_results[3]

    # Level 4: estimate_setup_and_operating_costs, draft_operations_workflow, design_compliance_program
    async def run_estimate_setup_and_operating_costs():
        # Call the async version of estimate_setup_and_operating_costs with results from dependencies
        return await estimate_setup_and_operating_costs_async(results['list_service_providers'])

    async def run_draft_operations_workflow():
        # Call the async version of draft_operations_workflow with results from dependencies
        return await draft_operations_workflow_async(results['define_asset_universe'], results['list_service_providers'], results['design_risk_management_framework'])

    async def run_design_compliance_program():
        # Call the async version of design_compliance_program with results from dependencies
        return await design_compliance_program_async(results['identify_regulatory_requirements'], results['design_risk_management_framework'])

    # Run level 4 nodes in parallel
    level_4_results = await asyncio.gather(run_estimate_setup_and_operating_costs(), run_draft_operations_workflow(), run_design_compliance_program())
    results['estimate_setup_and_operating_costs'] = level_4_results[0]
    results['draft_operations_workflow'] = level_4_results[1]
    results['design_compliance_program'] = level_4_results[2]

    # Level 5: define_technology_stack, create_hiring_plan, draft_fee_structure
    async def run_define_technology_stack():
        # Call the async version of define_technology_stack with results from dependencies
        return await define_technology_stack_async(results['draft_operations_workflow'])

    async def run_create_hiring_plan():
        # Call the async version of create_hiring_plan with results from dependencies
        return await create_hiring_plan_async(results['draft_operations_workflow'])

    async def run_draft_fee_structure():
        # Call the async version of draft_fee_structure with results from dependencies
        return await draft_fee_structure_async(results['set_performance_and_risk_targets'], results['estimate_setup_and_operating_costs'])

    # Run level 5 nodes in parallel
    level_5_results = await asyncio.gather(run_define_technology_stack(), run_create_hiring_plan(), run_draft_fee_structure())
    results['define_technology_stack'] = level_5_results[0]
    results['create_hiring_plan'] = level_5_results[1]
    results['draft_fee_structure'] = level_5_results[2]

    # Level 6: compile_pitch_deck_outline
    async def run_compile_pitch_deck_outline():
        # Call the async version of compile_pitch_deck_outline with results from dependencies
        return await compile_pitch_deck_outline_async(results['clarify_fund_objectives'], results['define_investor_profile'], results['choose_investment_strategy'], results['set_performance_and_risk_targets'], results['draft_fee_structure'], results['design_risk_management_framework'])

    # Run level 6 nodes in parallel
    results['compile_pitch_deck_outline'] = await run_compile_pitch_deck_outline()

    # Level 7: develop_timeline_and_milestones
    async def run_develop_timeline_and_milestones():
        # Call the async version of develop_timeline_and_milestones with results from dependencies
        return await develop_timeline_and_milestones_async(results['draft_operations_workflow'], results['define_technology_stack'], results['create_hiring_plan'], results['compile_pitch_deck_outline'])

    # Run level 7 nodes in parallel
    results['develop_timeline_and_milestones'] = await run_develop_timeline_and_milestones()

    # Level 8: produce_final_fund_plan_summary
    async def run_produce_final_fund_plan_summary():
        # Call the async version of produce_final_fund_plan_summary with results from dependencies
        return await produce_final_fund_plan_summary_async(results['design_compliance_program'], results['compile_pitch_deck_outline'], results['develop_timeline_and_milestones'])

    # Run level 8 nodes in parallel
    results['produce_final_fund_plan_summary'] = await run_produce_final_fund_plan_summary()

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
