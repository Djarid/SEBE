# Blog Tagging

> GOTCHA goal: tag blog posts by topic and difficulty level.

## Purpose

Signal content difficulty (accessible/intermediate/advanced) and topic to readers via visual badges on blog posts and the blog index. No JavaScript required.

## Taxonomy

### Level tags (coloured backgrounds)

| Tag | Colour | CSS class | Audience |
|---|---|---|---|
| accessible | Green (`--accent`) | `.post-tag-accessible` | General public, no prior knowledge needed |
| intermediate | Amber (`--highlight`) | `.post-tag-intermediate` | Readers with some policy/economics background |
| advanced | Red (`--tag-advanced`) | `.post-tag-advanced` | Specialist audience, assumes domain knowledge |

### Topic tags (neutral border-only pills)

Free-form, current set: `policy`, `economics`, `personal`, `macroeconomics`, `geopolitics`, `rebuttal`, `energy`, `defence`

## Implementation

### Front matter

Add `tags` array to post YAML:

```yaml
tags: [policy, economics, accessible]
```

Every post should have exactly ONE level tag and one or more topic tags.

### Rendering

Tags render in two locations:
1. **Post layout** (`_layouts/post.html`): `<div class="post-tags">` between date and content
2. **Blog index** (`blog.md`): `<span class="post-tags">` inline after title

Liquid logic detects level tags and applies coloured CSS classes; all other tags get neutral styling.

### CSS

Styles in `site/assets/css/style.css` under `/* ========== POST TAGS ========== */`. Uses existing design language: monospace font, uppercase, letter-spacing. Dark mode handled via `--tag-advanced` CSS variable.

## Status

- [x] Plan and spec
- [x] CSS implementation
- [x] Post layout tag rendering
- [x] Blog index tag rendering
- [x] Front matter on all posts
- [x] Goal file and manifest update
