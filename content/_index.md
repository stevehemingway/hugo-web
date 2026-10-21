---
title: "Hugo Web"
type: docs
---

# Hugo Web

Drop your markdown files into the `content/` folder and they appear here.

## Where things go

- `content/docs/` — the main documentation tree, nested folders become nested sidebar sections
- `content/posts/` — blog-style dated entries
- `static/` — images and files copied verbatim
- Page bundles: a folder with `index.md` next to its images

## Front matter

```yaml
---
title: "Page title"
weight: 10
bookHidden: false
---
```

Use `weight` to control ordering. Without it, pages sort alphabetically by title.

See [Getting started](/docs/getting-started/) for the workflow.
