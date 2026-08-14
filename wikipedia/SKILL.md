---
name: wikipedia
description: >-
  Deep research agent for Wikipedia topics. Extracts comprehensive information,
  analyzes topics from multiple angles, and discovers related articles. Use when
  asked to research a topic on Wikipedia, summarize a Wikipedia article, find
  related Wikipedia pages, generate a concept map from Wikipedia, assess citation
  quality, or extract visual content from Wikipedia articles. Supports standard,
  comprehensive, and exhaustive depth levels, multiple output formats, citation
  analysis, concept mapping, and custom summaries.
license: Apache-2.0
compatibility: Requires network access to Wikipedia API and wikipedia.org
metadata:
  author: mcaimi
  version: "2.0.0"
allowed-tools: Bash WebFetch WebSearch
---

# Wikipedia Deep Research Agent

Conduct in-depth research on a topic using Wikipedia as the primary source.
Extract comprehensive information, analyze it from multiple angles, and discover
related articles for further exploration.

## Input Parameters

### Required

- `topic` (string): The Wikipedia topic to research.
  **If not provided, stop execution and report the error.**

### Optional

| Parameter            | Default           | Notes                                                        |
|----------------------|-------------------|--------------------------------------------------------------|
| `depth`              | `"comprehensive"` | `"standard"`, `"comprehensive"`, or `"exhaustive"`           |
| `focus_areas`        | all               | Array of aspects to emphasize (e.g. `["history", "impact"]`) |
| `language`           | `"en"`            | Wikipedia language edition code                              |
| `include_references` | `true`            | Include external references from the article                 |
| `max_related_links`  | `10`              | Max related links to return (1-50)                           |
| `format`             | `"markdown"`      | `"markdown"` or `"json"`                                     |
| `citation_analysis`  | `false`           | Evaluate source quality (bool or config object)              |
| `visual_content`     | `false`           | Extract images and diagrams (bool or config object)          |
| `concept_map`        | `false`           | Generate concept map (bool or config object)                 |
| `custom_summary`     | `null`            | LLM-powered summary (style string or config object)          |
| `interactive_mode`   | `false`           | Enable conversational refinement with session tracking       |

See [the reference guide](references/REFERENCE.md) for the full parameter
schemas including advanced object configurations for `citation_analysis`,
`visual_content`, `concept_map`, and `custom_summary`.

## Workflow

### Step 1: Validate input

1. Confirm `topic` is present and non-empty. If missing, report the error and stop.
2. Normalize the topic string (handle spaces, special characters).
3. Validate `language` is a real Wikipedia edition; fall back to `"en"` with a warning if invalid.
4. Clamp `max_related_links` to range 1-50.

### Step 2: Discover topic

Search Wikipedia for the topic:

```bash
# Search via the API
curl -s "https://${LANG}.wikipedia.org/w/api.php?action=opensearch&search=${TOPIC}&limit=5&format=json"
```

- If the result is a disambiguation page, pick the most relevant match or present options.
- If no article is found, suggest similar topics and stop.

### Step 3: Extract content

Fetch the article using the Wikipedia API:

```bash
curl -s "https://${LANG}.wikipedia.org/w/api.php?action=query&titles=${TOPIC}&prop=extracts|links|categories|info&format=json"
```

Parse sections, extract key information based on depth:

| Depth           | Main article | Related links | Additional content                |
|-----------------|--------------|---------------|-----------------------------------|
| `standard`      | Yes          | Top 5         | Main article only                 |
| `comprehensive` | Yes          | Top 10        | Key sections explored             |
| `exhaustive`    | Yes          | Top 20        | Related articles also fetched     |

### Step 4: Run optional analyses

Run enabled features in parallel where possible:

**a. Citation quality assessment** (if `citation_analysis` enabled)

Extract references via `prop=references|extlinks`. Score each using:
- Credibility (40%): Academic=1.0, Gov=0.9, News=0.7, Blog=0.3
- Recency (30%): <1yr=1.0, 1-3yr=0.8, 3-5yr=0.6, >10yr=0.2
- Academic rigor (20%): Peer-reviewed=1.0, Conference=0.8, Trade=0.4
- Diversity (10%): Unique domains / total references

**b. Visual content extraction** (if `visual_content` enabled)

Fetch images via `prop=images&imlimit=50`, get metadata via
`prop=imageinfo&iiprop=url|size|mime|extmetadata`. Exclude UI elements
(<100px), categorize by type, extract license info from Wikimedia Commons.

**c. Concept map construction** (if `concept_map` enabled)

Build a graph from categories, infobox topics, and intro links. Infer
relationship types (is-a, part-of, related-to, caused-by, influences).
Generate output in the requested format (Mermaid, Graphviz, JSON, Cytoscape).

**d. Custom summary generation** (if `custom_summary` enabled)

Generate an LLM-powered summary using the specified style:
- `academic`: Formal, objective, citation-focused
- `journalistic`: Engaging, newsworthy, hook-driven
- `eli5`: Simple language, analogies, accessible
- `technical`: Precise terminology, implementation details
- `brief`: Essential facts only

Apply length constraints: short (1-2 paragraphs), medium (3-5), long (6-10).

### Step 5: Discover related links

Extract internal Wikipedia links from the article. Filter out navigation and
meta links. Rank by frequency of mention, position in article, context, and
category overlap. Categorize into: primary, secondary, broader context, and
deeper dives.

### Step 6: Synthesize and analyze

- Create executive summary (synthesize, don't copy)
- Extract key facts and statistics
- Identify historical timeline if applicable
- Note controversies or open debates

### Step 7: Generate report

Format the output using the templates in [OUTPUT_FORMAT.md](references/OUTPUT_FORMAT.md).
Include source attribution and research metadata.

If `interactive_mode` is enabled, generate a session ID and include refinement
options (expand, focus, compare, clarify) in the output.

## Gotchas

- Wikipedia API rate limit is 200 requests/second. Space requests when doing
  exhaustive research.
- Disambiguation pages look like normal articles but contain only links. Detect
  them via the `disambiguation` category and handle before attempting extraction.
- Some Wikipedia language editions have far less content than English. An
  exhaustive search on a small-edition article may return very few results.
- Image metadata from Wikimedia Commons sometimes lacks license info. Default
  to CC BY-SA 4.0 (Wikipedia's license) when missing, but flag it.
- The `extracts` API property returns HTML by default. Add `&explaintext=true`
  for plain text, or `&exintro=true` for intro only.
- Category names include the `Category:` prefix in API responses. Strip it
  before displaying.

## Error Handling

| Condition                | Action                                              |
|--------------------------|-----------------------------------------------------|
| No topic provided        | Report error, stop immediately                      |
| Topic not found          | Suggest similar topics from search results, stop    |
| Disambiguation page      | Present options or auto-select most relevant         |
| Network error            | Retry with backoff; return partial results on failure|
| Invalid language code    | Fall back to `"en"` with a warning                  |
| API rate limiting        | Add delays between requests                         |
| Citation extraction fail | Proceed without citation analysis, note in report   |
| Image metadata missing   | Include available images, note gaps in metadata      |
| LLM summary fail         | Fall back to standard executive summary              |

## Security

- All Wikipedia content is CC BY-SA 4.0. Maintain attribution in output.
- Do not use for researching living persons without ethical consideration.
- Implement respectful request patterns to avoid overwhelming Wikipedia servers.
- Some topics may contain sensitive or controversial information; note this
  where applicable.
