# -- PRD --
# 1. BULLET: Conduct stakeholder interviews to capture user personas, primary workflows
#   (watching real‑time prices, placing trades, reviewing history) and pain
#   points.
#   Reason: User‑centric requirements ensure the UI addresses real needs and avoids
#           unnecessary features.
#   Impact: MEDIUM
#   Complexity: LOW
#   Method: Prepare structured interview questions, record sessions, and create a
#           persona & journey map; summarize findings into a requirement
#           spec.
# 
# -----------------------------------------------------------------------------
# 2. BULLET: Translate functional requirements into a screen hierarchy: decide that the
#   platform will expose four top‑level screens – Dashboard (price ticker &
#   watchlist), Portfolio, Trade, and Settings.
#   Reason: Clear top‑level screens provide an intuitive entry point for users and
#           simplify navigation mapping.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Apply use‑case mapping; each requirement maps to a screen, then collapse
#           duplicates; document in a table.
# 
# -----------------------------------------------------------------------------
# 3. BULLET: Generate a primary navigation menu that mirrors the screen hierarchy, adding
#   logical secondary items such as ‘Home’, ‘Watchlist’, ‘Trade’, and
#   ‘Account’.
#   Reason: Consistent navigation reduces cognitive load and aligns with industry best
#           practices for trading apps.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Perform card‑sorting exercises with mock items; finalize order based on
#           heuristic principles (e.g., most frequent actions first).
# 
# -----------------------------------------------------------------------------
# 4. BULLET: Extract the list of API endpoints produced by implement_trading_api
#   (endpoint_list) and filter for those required by the UI: get_stock_price,
#   get_trade_history, place_trade, and get_portfolio_summary.
#   Reason: Ensures the UI design is tightly coupled to actual backend capabilities,
#           preventing design‑implementation mismatch.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Programmatically parse the JSON output from implement_trading_api, map each
#           endpoint to a UI feature, and populate the
#           api_endpoints_integrated list.
# 
# -----------------------------------------------------------------------------
# 5. BULLET: Define responsive breakpoints: mobile (≤480px), tablet (481‑1024px), desktop
#   (>1024px). For each breakpoint, specify how the layout should adjust
#   (single column on mobile, two‑column grid on tablet, three‑column on
#   desktop).
#   Reason: A clear breakpoint strategy guarantees a consistent user experience across
#           all devices.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Use CSS Grid/Flexbox with media queries; document in a responsive design
#           guide; validate with device emulators.
# 
# -----------------------------------------------------------------------------
# 6. BULLET: Create low‑fidelity wireframes for each screen using Figma (or similar),
#   focusing on content placement, navigation flow, and interaction hotspots.
#   Reason: Early visual feedback helps detect layout or navigation issues before
#           detailed design.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Sketch each screen on a 5‑point grid, annotate with notes, and share with
#           stakeholders for quick iteration.
# 
# -----------------------------------------------------------------------------
# 7. BULLET: Iterate wireframes based on stakeholder feedback, refining component
#   placement, labeling, and interaction states until the design aligns with
#   requirements.
#   Reason: Iterative refinement reduces costly rework later in the development cycle.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Hold review sessions, capture changes in a change‑log, and update
#           wireframes in Figma.
# 
# -----------------------------------------------------------------------------
# 8. BULLET: Develop high‑fidelity mockups incorporating branding guidelines (logo, color
#   palette, typography) and component library (buttons, charts, forms).
#   Ensure that real‑time price ticker is visually prominent and that trade
#   forms are user‑friendly.
#   Reason: Mockups provide a realistic reference for developers, ensuring the UI
#           implementation meets visual and functional expectations.
#   Impact: HIGH
#   Complexity: MEDIUM
#   Method: Use a design system (e.g., Storybook components) in Figma; export style
#           guide; handoff specs via Zeplin or Figma’s design tokens.
# 
# -----------------------------------------------------------------------------
# 9. BULLET: Compile the final design artifact: list the screens (ui_screen_list),
#   responsive device types (responsive_devices_supported), integrated API
#   endpoints (api_endpoints_integrated), navigation items
#   (primary_navigation_items), and set is_design_complete to true.
#   Reason: Consolidating all artifacts into a single deliverable ensures that
#           downstream nodes have all required inputs.
#   Impact: HIGH
#   Complexity: LOW
#   Method: Generate a JSON/Markdown document from the design system export;
#           double‑check that all required fields are populated.
# -- END PRD --

from pydantic import BaseModel, Field
from typing import List


class ImplementTradingApiOutput(BaseModel):
    """Pydantic model for implement_trading_api node outputs."""
    endpoint_list: List[str] = Field(..., description="Names of the trading API endpoints created.")
    auth_mechanism: str = Field(..., description="Authentication mechanism used for the trading APIs.")
    rate_limit_per_min: int = Field(..., description="Maximum number of requests allowed per minute per API key.")
    concurrency_limit: int = Field(..., description="Maximum number of concurrent connections supported by the API.")
    is_deployed: bool = Field(..., description="Whether the API has been successfully deployed.")
    error_message: str = Field(..., description="Error message if deployment failed; empty string if none.")
    api_docs_url: str = Field(..., description="URL to the generated API documentation.")


class DesignUserInterfaceOutput(BaseModel):
    """Pydantic model for design_user_interface node outputs."""
    ui_screen_list: List[str] = Field(..., description="Names of top-level screens in the UI (e.g., Dashboard, Portfolio, Trade, Settings)")
    responsive_devices_supported: List[str] = Field(..., description="Device types for which the UI is responsive (e.g., mobile, tablet, desktop)")
    api_endpoints_integrated: List[str] = Field(..., description="Trading API endpoints that the UI will call (e.g., get_stock_price, place_trade)")
    primary_navigation_items: List[str] = Field(..., description="Main navigation items presented in the UI (e.g., Home, Watchlist, Trade, Account)")
    is_design_complete: bool = Field(..., description="Whether the UI design is finalized and ready for implementation")


def design_user_interface(implement_trading_api_input: ImplementTradingApiOutput, **kwargs) -> DesignUserInterfaceOutput:
    """Design a user interface for the stock trading platform.

    Args:
        implement_trading_api_input: Input from the 'implement_trading_api' node.
        **kwargs: Additional keyword arguments.

    Returns:
        DesignUserInterfaceOutput: Object containing outputs for this node.
    """
    # TODO: Implement this function

    # Return stub output with placeholder values
    return DesignUserInterfaceOutput(
        ui_screen_list=[],
        responsive_devices_supported=[],
        api_endpoints_integrated=[],
        primary_navigation_items=[],
        is_design_complete=False,
    )