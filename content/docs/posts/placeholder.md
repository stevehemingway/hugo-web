---
title: "Place your markdown here"
date: 2026-10-21
draft: false
weight: 10
---

# Place your markdown here

This file lives at `content/docs/posts/placeholder.md`. Replace it, or drop more
files alongside it.

## Converting an existing pile of markdown

1. Copy your folder tree into `content/docs/`.
2. If the files have no front matter, prepend a title:

   ```bash
   for f in content/docs/**/*.md; do
     head -1 "$f" | grep -q '^---' || sed -i '1i---\ntitle: "'"$(basename "$f" .md)"'"\n---\n' "$f"
   done
   ```

3. Set `weight` in any files whose order matters.
4. Run `hugo server -D` and check the sidebar.

## Filename rules

- `_index.md` = section landing page
- `index.md` = leaf bundle (page with its own images)
- anything else = a normal page
