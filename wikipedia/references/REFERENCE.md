# Wikipedia Deep Research — Reference

Detailed parameter schemas, API endpoints, and implementation notes.

## Advanced parameter schemas

### `citation_analysis` (object form)

```json
{
  "enabled": true,
  "criteria": ["credibility", "recency", "academic", "diversity"],
  "min_quality_score": 0.5,
  "include_scores": true
}
```

- `criteria`: Which scoring dimensions to apply (default: all four).
- `min_quality_score` (0.0-1.0): Filter out sources below this threshold.
- `include_scores`: Show per-reference detailed scores in output.

### `visual_content` (object form)

```json
{
  "enabled": true,
  "types": ["images", "diagrams", "charts", "infographics", "maps"],
  "max_items": 10,
  "format": "metadata",
  "include_captions": true
}
```

- `types`: Which visual content types to include.
- `max_items` (1-50, default: 10): Maximum items to extract.
- `format`: `"urls"` (links only), `"metadata"` (full details), or
  `"embedded"` (inline markdown images).
- `include_captions`: Include image captions (default: true).

### `concept_map` (object form)

```json
{
  "enabled": true,
  "format": "mermaid",
  "max_nodes": 15,
  "max_depth": 2,
  "relationship_types": ["is-a", "part-of", "related-to", "caused-by", "influences"]
}
```

- `format`: `"mermaid"`, `"graphviz"`, `"json"`, or `"cytoscape"`.
- `max_nodes` (1-50, default: 15): Maximum nodes in graph.
- `max_depth` (1-3, default: 2): How many levels of relationships to traverse.
- `relationship_types`: Which edge types to include.

### `custom_summary` (object form)

```json
{
  "enabled": true,
  "style": "academic",
  "length": "medium",
  "target_audience": "general",
  "temperature": 0.3
}
```

- `style`: `"academic"`, `"journalistic"`, `"eli5"`, `"technical"`, or
  `"brief"`.
- `length`: `"short"` (1-2 paragraphs), `"medium"` (3-5), `"long"` (6-10).
- `target_audience`: Free-text description of intended audience.
- `temperature` (0.0-1.0): LLM temperature override.

When `custom_summary` is a plain string, it is treated as the `style` value
with all other fields at defaults.

## Wikipedia API endpoints

### Search

```
GET https://{lang}.wikipedia.org/w/api.php?action=opensearch&search={topic}&limit={n}&format=json
```

### Article content

```
GET https://{lang}.wikipedia.org/w/api.php?action=query&titles={topic}&prop=extracts|links|categories|info&format=json
```

Add `&explaintext=true` for plain text. Add `&exintro=true` for intro only.

### Article images

```
GET https://{lang}.wikipedia.org/w/api.php?action=query&titles={topic}&prop=images&imlimit=50&format=json
```

### Image metadata

```
GET https://{lang}.wikipedia.org/w/api.php?action=query&titles=File:{filename}&prop=imageinfo&iiprop=url|size|mime|extmetadata&format=json
```

### References and external links

```
GET https://{lang}.wikipedia.org/w/api.php?action=query&titles={topic}&prop=references|extlinks&format=json
```

### Direct article URL

```
https://{lang}.wikipedia.org/wiki/{topic}
```

## Depth levels in detail

### Standard

- Fetch main article content only.
- Extract top 5 related links from article body.
- Single API call for content + links.

### Comprehensive

- Fetch main article content.
- Parse all major sections individually.
- Extract top 10 related links with categorization (primary, secondary,
  broader context, deeper dives).
- 3-5 API calls.

### Exhaustive

- Fetch main article content.
- Follow and summarize top related articles.
- Extract up to 20 related links with deep categorization.
- Cross-reference categories across related articles.
- 10-25 API calls depending on topic breadth.

## Concept map construction algorithm

1. Create root node from main topic (type: `main`, depth: 0).
2. Extract primary nodes from: article categories, infobox topics, and
   links in the introduction (type: `primary`, depth: 1).
3. If `max_depth > 1`, fetch categories for each primary node to create
   secondary nodes (type: `secondary`, depth: 2).
4. If `max_depth > 2`, repeat for tertiary nodes.
5. Infer relationship types:
   - Category membership -> `is-a`
   - "Part of" template or section -> `part-of`
   - Causal language in context -> `caused-by`
   - Influence language in context -> `influences`
   - Default -> `related-to`
6. Prune to `max_nodes`, keeping higher-depth nodes and stronger
   relationships.
7. Generate output in the requested format.

## Citation scoring algorithm

For each reference extracted from the article:

```
weighted_score = (credibility * 0.4) + (recency * 0.3) + (academic * 0.2) + (diversity * 0.1)
```

### Credibility scoring by source type

| Source Type         | Score |
|---------------------|-------|
| Academic journal    | 1.0   |
| Government source   | 0.9   |
| Major news outlet   | 0.7   |
| Book / monograph    | 0.8   |
| Organization report | 0.6   |
| Blog / personal     | 0.3   |
| Unknown             | 0.2   |

### Recency scoring by publication age

| Age           | Score |
|---------------|-------|
| < 1 year      | 1.0   |
| 1-3 years     | 0.8   |
| 3-5 years     | 0.6   |
| 5-10 years    | 0.4   |
| > 10 years    | 0.2   |

### Academic rigor scoring

| Type              | Score |
|-------------------|-------|
| Peer-reviewed     | 1.0   |
| Conference paper  | 0.8   |
| Trade publication | 0.4   |
| Non-academic      | 0.1   |

### Diversity scoring

```
diversity = unique_domains / total_references
```

## Visual content relevance scoring

| Position / context      | Base score |
|--------------------------|-----------|
| Infobox image            | 1.0       |
| First section image      | 0.9       |
| Captioned image          | 0.8       |
| Section-relevant image   | 0.7       |
| Uncaptioned image        | 0.4       |

Filter out images smaller than 100px in either dimension (UI elements,
icons, flags used in navigation).

## Interactive session management

- Session ID: UUID v4, generated per initial request.
- Session expiry: 24 hours or 10 refinements, whichever comes first.
- Supported refinement actions:
  - **expand**: Re-fetch with increased depth on a specific section.
  - **focus**: Filter content and re-weight related links toward a subtopic.
  - **compare**: Fetch a related topic and generate a comparison matrix.
  - **clarify**: Extract relevant passages and explain relationships between
    concepts.

## Performance expectations

| Feature              | Time impact | API calls | Notes                          |
|----------------------|-------------|-----------|--------------------------------|
| Base research        | 5-10s       | 3-5       | Standard baseline              |
| Citation analysis    | +2-5s       | +1-3      | Reference parsing and scoring  |
| Visual content       | +3-7s       | +5-15     | Per-image metadata fetch       |
| Concept mapping      | +5-10s      | +10-25    | Related topics extraction      |
| Custom summary       | +5-15s      | 0         | LLM generation                 |
| Interactive mode     | +1s         | 0         | Session management overhead    |

All features combined: ~15-30 seconds (parallelized, not cumulative).
Set per-request timeout to 10-15 seconds. Set per-feature timeout to 30
seconds with graceful fallback to partial results.
