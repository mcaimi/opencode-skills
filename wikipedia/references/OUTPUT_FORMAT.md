# Wikipedia Deep Research — Output Format

Output templates and schemas for the wikipedia skill.

## Markdown output template

```markdown
# Deep Research: {Topic}

**Research Date:** {timestamp}
**Wikipedia URL:** {wikipedia_url}
**Research Depth:** {depth_level}
**Language Edition:** {language}

---

## Executive Summary

{2-3 paragraph overview of the topic, synthesizing key information}

{If custom_summary enabled, add before the standard summary:}

**Summary Style:** {style} | **Target Audience:** {audience}

{LLM-generated custom summary}

---

## Detailed Analysis

### Overview
{Comprehensive introduction: definition and context}

### Historical Context
{Origins, evolution, and historical background}

### Key Concepts
- **{Concept 1}**: {Description}
- **{Concept 2}**: {Description}
- **{Concept 3}**: {Description}

### Applications & Use Cases
{Practical applications and manifestations}

### Significance & Impact
{Why it matters, influence and consequences}

### Current State & Future Outlook
{Contemporary status and projected developments}

### Notable Controversies or Debates
{Significant disagreements, criticisms, or open questions}

## Key Facts & Statistics

- **{Fact 1}**: {Detail}
- **{Fact 2}**: {Detail}
- **{Fact 3}**: {Detail}

## Citation Quality Assessment

{Include only when citation_analysis is enabled}

**Overall Source Quality Score:** {0.0-1.0} ({Poor|Fair|Good|Excellent})

### Reference Evaluation

| Reference | Type | Quality Score | Credibility | Recency | Notes |
|-----------|------|---------------|-------------|---------|-------|
| [Source 1] | Academic Journal | 0.92 | High | 2024 | Peer-reviewed |
| [Source 2] | News Article | 0.65 | Medium | 2023 | Major outlet |

**Quality Distribution:**
- High Quality (0.8-1.0): {count} ({percentage}%)
- Medium Quality (0.5-0.79): {count} ({percentage}%)
- Low Quality (0.0-0.49): {count} ({percentage}%)

**Recommendations:**
- {Recommendation for improving source quality}

## Visual Content

{Include only when visual_content is enabled}

### Featured Images & Diagrams

#### 1. {Image Title}
![{Alt Text}]({Image URL})
- **Caption:** {caption}
- **Type:** {image|diagram|chart|infographic|map}
- **License:** {license}
- **Source:** {Wikimedia Commons URL}
- **Relevance:** {Why this visual matters}

### Visual Content Summary
- Total visual elements: {count}
- Images: {n} | Diagrams: {n} | Charts: {n} | Infographics: {n} | Maps: {n}

## Related Topics & Further Reading

### Primary Related Topics
- [{Topic 1}]({url}) - {Relevance description}
- [{Topic 2}]({url}) - {Relevance description}

### Secondary Related Topics
- [{Topic 3}]({url}) - {Description}

### Broader Context
- [{Broader Topic}]({url}) - {Relationship to main topic}

### Deeper Dives
- [{Specific Aspect}]({url}) - {Why to explore this}

## Concept Map

{Include only when concept_map is enabled}

### Topic Relationship Visualization

```mermaid
graph TD
    A[{Main Topic}] -->|is-a| B[{Broader Category}]
    A -->|part-of| C[{Parent Domain}]
    A -->|related-to| D[{Related Topic 1}]
    A -->|related-to| E[{Related Topic 2}]
```

**Legend:**
- **is-a**: Categorical relationship
- **part-of**: Compositional relationship
- **related-to**: Associative relationship
- **caused-by**: Causal relationship
- **influences**: Influential relationship

**Relationship Analysis:**
- Total concepts: {count}
- Direct relationships: {count}
- Hierarchy depth: {levels}

## External References

{Include only when include_references is true}

1. {Reference 1}
2. {Reference 2}

## Research Metadata

- **Article Length**: {word_count} words
- **Last Wikipedia Update**: {last_modified}
- **Related Articles Discovered**: {count}
- **Disambiguation Note**: {if applicable}

## Continue Your Research

{Include only when interactive_mode is enabled}

**Session ID:** {session_id}

You can refine this research by requesting:
- **Expand**: "Expand the {section_name} section with more details"
- **Focus**: "Focus more on {specific_aspect}"
- **Compare**: "Compare this with {related_topic}"
- **Clarify**: "Clarify the relationship between {concept_a} and {concept_b}"

---

*This research was conducted by the Wikipedia Deep Research Agent. All
information is sourced from Wikipedia (CC BY-SA 4.0).*
```

## JSON output schema

When the user requests JSON output, use this structure:

```json
{
  "topic": "string",
  "version": "2.0.0",
  "research_date": "ISO-8601-timestamp",
  "wikipedia_url": "string",
  "depth": "standard|comprehensive|exhaustive",
  "language": "string",
  "executive_summary": "string",
  "detailed_analysis": {
    "overview": "string",
    "historical_context": "string",
    "key_concepts": [
      {
        "name": "string",
        "description": "string"
      }
    ],
    "applications": "string",
    "significance": "string",
    "current_state": "string",
    "controversies": "string"
  },
  "key_facts": ["string"],
  "related_links": {
    "primary": [
      {
        "title": "string",
        "url": "string",
        "description": "string",
        "relevance": "high|medium|low"
      }
    ],
    "secondary": [
      {
        "title": "string",
        "url": "string",
        "description": "string"
      }
    ],
    "broader_context": [
      {
        "title": "string",
        "url": "string",
        "relationship": "string"
      }
    ],
    "deeper_dives": [
      {
        "title": "string",
        "url": "string",
        "reason": "string"
      }
    ]
  },
  "external_references": ["string"],
  "metadata": {
    "article_length": "number",
    "last_modified": "ISO-8601-timestamp",
    "related_count": "number",
    "disambiguation": "string|null"
  },
  "citation_quality": {
    "enabled": "boolean",
    "overall_score": "number (0.0-1.0)",
    "quality_distribution": {
      "high": {"count": "number", "percentage": "number"},
      "medium": {"count": "number", "percentage": "number"},
      "low": {"count": "number", "percentage": "number"}
    },
    "references": [
      {
        "reference": "string",
        "type": "academic|news|book|government|organization|blog|other",
        "quality_score": "number (0.0-1.0)",
        "credibility": "high|medium|low",
        "recency_score": "number (0.0-1.0)",
        "publication_year": "number",
        "academic_score": "number (0.0-1.0)",
        "url": "string",
        "notes": "string"
      }
    ],
    "recommendations": ["string"],
    "criteria_used": ["string"]
  },
  "visual_content": {
    "enabled": "boolean",
    "total_items": "number",
    "items": [
      {
        "title": "string",
        "url": "string",
        "thumbnail_url": "string",
        "type": "image|diagram|chart|infographic|map",
        "caption": "string",
        "alt_text": "string",
        "source": "string",
        "license": "string",
        "license_url": "string",
        "width": "number",
        "height": "number",
        "format": "jpg|png|svg|gif",
        "relevance_score": "number (0.0-1.0)",
        "relevance_note": "string",
        "commons_url": "string"
      }
    ],
    "summary": {
      "images": "number",
      "diagrams": "number",
      "charts": "number",
      "infographics": "number",
      "maps": "number"
    }
  },
  "concept_map": {
    "enabled": "boolean",
    "format": "mermaid|graphviz|json|cytoscape",
    "visualization": "string",
    "nodes": [
      {
        "id": "string",
        "label": "string",
        "type": "main|primary|secondary|tertiary",
        "wikipedia_url": "string",
        "depth": "number"
      }
    ],
    "edges": [
      {
        "source": "string",
        "target": "string",
        "relationship": "is-a|part-of|related-to|caused-by|influences",
        "strength": "number (0.0-1.0)",
        "bidirectional": "boolean"
      }
    ],
    "statistics": {
      "total_nodes": "number",
      "total_edges": "number",
      "max_depth": "number",
      "relationship_counts": {
        "is-a": "number",
        "part-of": "number",
        "related-to": "number",
        "caused-by": "number",
        "influences": "number"
      }
    }
  },
  "custom_summary": {
    "enabled": "boolean",
    "style": "academic|journalistic|eli5|technical|brief",
    "length": "short|medium|long",
    "target_audience": "string",
    "content": "string",
    "focus_aspects": ["string"],
    "generation_metadata": {
      "temperature": "number",
      "model": "string",
      "tokens": "number"
    }
  },
  "interactive_session": {
    "enabled": "boolean",
    "session_id": "string (UUID)",
    "refinement_options": [
      {
        "action": "expand|focus|compare|clarify",
        "description": "string",
        "available_targets": ["string"]
      }
    ],
    "conversation_context": {
      "research_history": ["string"],
      "refinements_applied": "number",
      "last_updated": "ISO-8601-timestamp"
    }
  }
}
```

Omit top-level feature objects (`citation_quality`, `visual_content`,
`concept_map`, `custom_summary`, `interactive_session`) entirely when the
corresponding feature is not enabled. Do not include them with
`"enabled": false`.
