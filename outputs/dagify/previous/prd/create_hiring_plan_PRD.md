# create_hiring_plan PRD

## Description
Determine initial staffing requirements for the hedge fund launch.


## Implementation Plan

### 1. Parse the input JSON from draft_operations_workflow to extract the two arrays: trade_lifecycle_steps and responsible_parties.

| Category | Details |
| --- | --- |
| **Reason** | These arrays provide the foundation for identifying which operational stages lack sufficient internal coverage. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use a JSON parser to map each step to its responsible party; store in a dictionary step_to_party. |

### 2. Create a reference list of standard internal operational roles (e.g., Portfolio Analyst, Execution Trader, Risk Manager, Operations Coordinator, Compliance Officer, Fund Administrator Liaison, IT Systems Specialist, Finance & Accounting Lead).

| Category | Details |
| --- | --- |
| **Reason** | Having a pool of role templates streamlines role selection and ensures coverage of all workflow gaps. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Consult industry best‑practice staffing matrices for hedge funds and encode the list in a static array. |

### 3. Identify workflow gaps by comparing each responsible_party with the internal role pool; if a party is 'GP' or an external provider (Prime Broker, Fund Admin, etc.), flag that step as a gap.

| Category | Details |
| --- | --- |
| **Reason** | Gap identification directly informs which positions must be filled internally. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Iterate over step_to_party; for each party that is not a core internal role, record the step as a gap in gap_list. |

### 4. Map each identified gap to the most appropriate internal role from the reference list, ensuring that the role’s core responsibility covers the step’s function.

| Category | Details |
| --- | --- |
| **Reason** | Accurate mapping guarantees that responsibilities are neither duplicated nor omitted. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use a rule table: e.g., idea generation -> Portfolio Analyst, order entry -> Execution Trader, execution -> Execution Trader, confirmation -> Operations Coordinator, settlement -> Fund Administrator Liaison, reconciliation -> Risk Manager. Adjust for multiple gaps if necessary. |

### 5. Limit the final list to a maximum of eight positions by prioritizing roles that cover multiple gaps or by consolidating closely related responsibilities (e.g., combining Compliance Officer with Operations Coordinator if resources are tight).

| Category | Details |
| --- | --- |
| **Reason** | The node constraint of 8 positions requires efficient role consolidation without losing critical coverage. |
| **Impact** | HIGH |
| **Complexity** | HIGH |
| **Method** | Score each role by the number of gaps it covers; select top N roles until reaching 8 or all gaps are addressed. |

### 6. Generate the one-line responsibility description for each selected position by summarizing the mapped step(s) and the core duties of the role, e.g., "Lead execution of all equity orders, ensuring timely trade capture and reconciliation."

| Category | Details |
| --- | --- |
| **Reason** | Clear, concise responsibilities aid in hiring, performance management, and stakeholder communication. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Template strings per role: '{role}: {responsibility}' where responsibility is a concatenation of step names covered. |

### 7. Populate the output fields: position_titles (list of role names), responsibility_descriptions (aligned list of responsibility strings), gap_alignment (list of corresponding trade_lifecycle_step names), and total_positions (integer count).

| Category | Details |
| --- | --- |
| **Reason** | Ensures compliance with the node’s specified output structure. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Construct parallel arrays; verify lengths match; compute total_positions as array length. |

### 8. Validate that total_positions does not exceed 8; if it does, revisit role consolidation step to remove the least critical role, re‑generate responsibilities, and update the arrays accordingly.

| Category | Details |
| --- | --- |
| **Reason** | Guarantees node constraint compliance and avoids downstream errors. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Loop until len(position_titles) <= 8; use a priority threshold based on role seniority or gap coverage count. |
