# select_forex_data_providers PRD

## Description
Select reliable data providers for real-time forex data feeds.


## Implementation Plan

### 1. Retrieve the list of required data feeds from the parent node 'identify_required_data_feeds' and store it locally for context.

| Category | Details |
| --- | --- |
| **Reason** | The selection criteria may depend on the specific forex pairs or data granularity required by downstream ingestion pipelines. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Deserialize the parent output JSON; extract 'feed_names' and 'feed_count' into variables for reference. |

### 2. Compile a comprehensive list of potential forex data providers, gathering metadata for accuracy (%), average latency (ms), monthly cost (USD), and compliance certifications.

| Category | Details |
| --- | --- |
| **Reason** | A diverse vendor set ensures coverage of major currency pairs, low latency, and regulatory compliance. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Perform web scraping and API calls to vendor sites (e.g., Bloomberg, Reuters, OANDA, Dukascopy, Xignite, FXCM). Parse public SLAs, support documents, and industry reports. Store the collected data in a structured table. |

### 3. Normalize all collected metrics to a common scale: convert all latency values to milliseconds, ensure all costs are expressed in USD, and represent accuracy as a percentage.

| Category | Details |
| --- | --- |
| **Reason** | Normalization guarantees a fair comparison across providers with heterogeneous data formats. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Apply unit conversion functions, round values to two decimal places, and store normalized values in a temporary data structure. |

### 4. Score each provider using a weighted scoring model (accuracy 40%, latency 30%, cost 20%, compliance 10%) and compute a composite score.

| Category | Details |
| --- | --- |
| **Reason** | A quantitative score encapsulates the multi‑dimensional trade‑offs, making the selection objective. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | For each provider, calculate: score = (accuracy * 0.4) - (latency_norm * 0.3) - (cost_norm * 0.2) + (compliance_flag * 0.1). Normalize latency and cost to a 0‑1 range before weighting. |

### 5. Rank providers by composite score, select the top N (e.g., 3) providers, and set the corresponding 'is_selected' flag to true. All other providers get a false flag.

| Category | Details |
| --- | --- |
| **Reason** | Selecting a small, high‑quality set ensures low latency ingestion and cost control. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Sort the provider list descending by score, iterate to assign boolean flags, and maintain the original ordering for output consistency. |

### 6. Assemble the final output arrays in the order required by the output structure: provider_names (list of strings), accuracies (list of floats), latencies_ms (list of ints), costs_usd (list of floats), and is_selected (list of bools).

| Category | Details |
| --- | --- |
| **Reason** | Ensures compatibility with downstream nodes such as 'implement_forex_data_ingestion_pipeline'. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Map each provider record to the respective output field, cast numeric types appropriately, and serialize the final JSON. |
