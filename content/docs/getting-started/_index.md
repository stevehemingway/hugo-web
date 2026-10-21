---
title: "Getting started"
weight: 10
bookCollapseSection: false
---

# Getting started

## 1. Add your markdown

Create files under `content/docs/`:

```
content/docs/getting-started/_index.md     -> /docs/getting-started/
content/docs/getting-started/install.md    -> /docs/getting-started/install/
content/docs/reference/cli.md              -> /docs/reference/cli/
```

Nested folders become collapsible groups in the left sidebar automatically.

## 2. Front matter

Minimum useful set:

```yaml
---
title: "Install"
weight: 20
---
```

Ordering keys:

- `weight` — lower numbers first, in sidebar and within a section
- `bookHidden: true` — keep out of the sidebar but still reachable by URL
- `bookCollapseSection: true` — start a group collapsed

## 3. Page bundles for images

Instead of dumping images in `static/`, put them with the page:

```
content/docs/getting-started/
├── index.md
└── screenshot.png
```

Then reference relatively: `![shot](screenshot.png)`. Hugo serves them under the page URL, so nothing collides.

## 4. Preview and build

```bash
hugo server -D          # live reload on http://localhost:1313
hugo                    # static build into public/
```

`-D` includes drafts (`draft: true`). Drop it for previewing exactly what would ship.

## 5. Deploy

`public/` is plain static HTML. Copy it anywhere: nginx, S3, Cloudflare Pages, GitHub Pages. Nothing at runtime needs Hugo.
