# produce_final_fund_plan_summary PRD

## Description
Generate an all-in, concise executive summary of the hedge fund plan by integrating key outputs from the compliance program, pitch deck outline, and launch timeline.


## Implementation Plan

### 1. Acquire the full output payloads from the three parent nodes: the compliance checklist, the 10-slide pitch deck outline, and the 12‑month timeline.

| Category | Details |
| --- | --- |
| **Reason** | These three inputs contain all the required context (strategy, structure, risk controls, operations milestones, and regulatory alignment) needed to craft an accurate summary. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Deserialize JSON objects returned by the parent nodes and store the fields: compliance_requirements, policy_references, slide_titles, monthly_milestones, final_go_live_month, overall_status. |

### 2. Map each key summary element to the most relevant parent data: strategy → first slide title (or slide labeled ‘Strategy’); structure → slide labeled ‘Structure’; risk → any slide containing ‘Risk’ plus the compliance checklist; operations → slide titled ‘Operations’ plus monthly_milestones; fees → slide titled ‘Fees’ (or infer from slide list if present); timeline → final_go_live_month and a brief summary of monthly milestones.

| Category | Details |
| --- | --- |
| **Reason** | Direct mapping guarantees that the summary references explicit, validated content rather than inferred or ambiguous data. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Iterate through slide_titles and use string matching (case‑insensitive) to locate target keywords. For risk, concatenate compliance_requirements into a short list. For operations, generate a bullet summarizing the overall timeline status. |

### 3. Construct a first draft of the executive summary using short, declarative sentences and bullet points, ensuring each paragraph/point covers one of the six focus areas: strategy, structure, risk, operations, fees, timeline.

| Category | Details |
| --- | --- |
| **Reason** | Bullet or short paragraph format is mandated by the prompt and improves readability for executive stakeholders. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Employ a template engine (e.g., Jinja2 or a simple string format) that inserts mapped content into predefined sentence structures. Keep each section under 50 words to provide a buffer before the final word count check. |

### 4. Count words in the drafted summary. If the word count exceeds 400, iteratively prune or condense the longest sections (usually risk or operations) by removing non‑essential adjectives or phrases until the limit is met.

| Category | Details |
| --- | --- |
| **Reason** | The word limit is strict; exceeding it invalidates the output, so an automated check and adjustment loop is necessary. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Split the summary string by whitespace to obtain an array of words. If length > 400, identify sections with the highest word count using regex or string index ranges, then remove the longest 5–10 words per iteration. Re‑count until within limit. |

### 5. Validate that the compliance mapping is consistent: if is_consistent is false, append a brief disclaimer noting potential gaps between regulatory requirements and internal policies.

| Category | Details |
| --- | --- |
| **Reason** | Stakeholders need to be aware of compliance alignment status; a missing disclaimer could misrepresent the fund’s readiness. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Check the boolean flag is_consistent from design_compliance_program. If false, add a sentence such as: “Note: The current compliance‑policy mapping shows an outstanding gap requiring remediation.” |

### 6. Append a final sentence summarizing the go‑live status: e.g., “The fund is slated to go live in Month X, contingent upon the completion of all regulatory and operational milestones.”

| Category | Details |
| --- | --- |
| **Reason** | This ties the summary back to the concrete launch timeline, reinforcing the practical readiness of the plan. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Insert final sentence using final_go_live_month and overall_status; if overall_status is false, prepend “Pending completion of the following milestones: …” derived from monthly_milestones where the description indicates incomplete status. |

### 7. Return the finalized executive_summary string and compute the final word_count integer for the JSON payload.

| Category | Details |
| --- | --- |
| **Reason** | These are the required output fields; they must be in the exact format to satisfy downstream nodes. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Package the summary string and word count into a JSON object with keys executive_summary and word_count, ensuring correct data types (str and int). |
