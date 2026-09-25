# File Naming Convention and Content Format

## Naming Convention

Memory files are named to reflect their semantic content using
`CATEGORY-SUBTOPIC.md` format with uppercase and underscores:

| Content                                         | Filename                                     |
|-------------------------------------------------|----------------------------------------------|
| Explanation of the attention mechanism           | `MACHINE_LEARNING-ATTENTION_MECHANISM.md`    |
| Summary of Kubernetes networking                 | `KUBERNETES-NETWORKING.md`                   |
| Notes on Rust ownership rules                    | `RUST-OWNERSHIP_MODEL.md`                    |
| A project's deployment checklist                 | `DEVOPS-DEPLOYMENT_CHECKLIST.md`             |
| Generic data dump without a clear category       | `NOTES-<descriptive_slug>.md`                |

Rules:
- Use UPPERCASE with underscores for spaces.
- Use a single hyphen to separate category from subtopic.
- Keep names concise but unambiguous.
- When the user does not specify a topic, infer the best name from the content.
- For generic or uncategorized data, use the `NOTES-` prefix.

## Metadata Header

Every memory file must begin with a YAML frontmatter block that describes its
content. This header is written as part of the file body, before any Markdown
content.

```yaml
---
topic: "Attention Mechanism"
category: "Machine Learning"
summary: "How scaled dot-product and multi-head attention work in transformer architectures"
saved_from: "conversation"
---
```

| Field        | Required | Description                                                      |
|--------------|----------|------------------------------------------------------------------|
| `topic`      | yes      | Human-readable topic name                                        |
| `category`   | yes      | Top-level category (matches the CATEGORY in the filename)        |
| `summary`    | yes      | One-line description of what the file contains                   |
| `saved_from` | yes      | Origin of the content: `"conversation"`, `"file"`, or `"manual"` |
| `tags`       | no       | List of keyword tags for cross-referencing related memories      |
| `related`    | no       | List of filenames of related memories in the cube                |

Example with optional fields:

```yaml
---
topic: "Attention Mechanism"
category: "Machine Learning"
summary: "How scaled dot-product and multi-head attention work in transformer architectures"
saved_from: "conversation"
tags:
  - transformers
  - deep-learning
  - NLP
related:
  - MACHINE_LEARNING-TRANSFORMERS.md
---
```

When appending to an existing file, do not duplicate the frontmatter — it is
written only once at file creation. When overwriting, regenerate the frontmatter
to match the new content.

## Personality Bank Files

Personality files follow the same `CATEGORY-SUBTOPIC.md` uppercase naming
convention but use categories specific to agent behavior and interaction
preferences.

### Personality Categories

| Category         | Purpose                                          | Example Filename                          |
|------------------|--------------------------------------------------|-------------------------------------------|
| `TONE`           | Communication style: formal, casual, terse, etc. | `TONE-FORMAL_CONCISE.md`                  |
| `MOOD`           | Agent demeanor: friendly, professional, humorous  | `MOOD-FRIENDLY_PROFESSIONAL.md`           |
| `SPECIALIZATION` | Domain focus or persona the agent should assume   | `SPECIALIZATION-KUBERNETES_EXPERT.md`     |
| `RULES`          | Behavioral rules and workflow constraints          | `RULES-ALWAYS_RUN_TESTS.md`              |
| `SKILLS`         | Skill routing preferences and bindings             | `SKILLS-SECURITY_ROUTING.md`             |
| `PREFERENCES`    | Miscellaneous interaction preferences              | `PREFERENCES-NO_EMOJIS.md`              |

### Personality Metadata Header

Personality files use the same frontmatter structure as memory files, but with
categories from the table above and a `type` field that classifies the entry:

```yaml
---
topic: "Formal and Concise Tone"
category: "Tone"
type: "tone"
summary: "Prefer formal language with concise responses, no filler"
saved_from: "conversation"
---
```

| Field        | Required | Description                                                      |
|--------------|----------|------------------------------------------------------------------|
| `topic`      | yes      | Human-readable description of the preference                    |
| `category`   | yes      | One of: Tone, Mood, Specialization, Rules, Skills, Preferences   |
| `type`       | yes      | Lowercase slug: `tone`, `mood`, `specialization`, `rule`, `skill-routing`, `preference` |
| `summary`    | yes      | One-line description of what this entry controls                 |
| `saved_from` | yes      | Origin: `"conversation"`, `"file"`, or `"manual"`               |
| `tags`       | no       | Keyword tags for cross-referencing                               |
| `related`    | no       | Related personality or memory filenames                          |

### Personality Content Structure

Personality files should be short and actionable. Structure them as:

1. **Frontmatter** — As above.
2. **Title** — H1 heading describing the preference or rule.
3. **Rule statement** — A clear, imperative sentence stating what the agent
   should do.
4. **Context** (optional) — Why the user wants this, so the agent can apply
   the rule sensibly in edge cases.
5. **Examples** (optional) — Concrete before/after examples showing the
   preference in action.

Example file:

```markdown
---
topic: "Formal and Concise Tone"
category: "Tone"
type: "tone"
summary: "Prefer formal language with concise responses, no filler"
saved_from: "conversation"
---

# Formal and Concise Tone

Use formal language. Keep responses concise — no filler phrases, no
unnecessary qualifiers. Prefer short sentences and direct statements.

## Examples

- Instead of: "Sure! I'd be happy to help you with that. Let me take a look..."
- Use: "Examining the file now."
```

## Content Formatting Guidelines

When synthesizing conversation content into a memory file, follow these rules:

1. **Start with the metadata header** — Every file begins with the YAML
   frontmatter block described above.
2. **Follow with a title** — Use an H1 heading matching the topic.
3. **Add a brief summary** — One or two sentences describing what the document
   covers.
4. **Organize with headings** — Break the content into logical sections using
   H2/H3 headings.
5. **Use lists and tables** — Prefer structured formats over dense prose.
6. **Include code blocks** — Preserve any code examples with proper language
   tags.
7. **Be self-contained** — A reader should understand the document without
   access to the original conversation.
8. **Attribute sources** — If the content references external material, note
   the source.
