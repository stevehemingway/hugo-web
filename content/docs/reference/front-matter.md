---
title: "Front matter"
weight: 10
---

# Front matter keys

| Key | Purpose |
| --- | --- |
| `title` | Page title, used in sidebar and `<title>` |
| `weight` | Sort order, lower first |
| `date` | Publish date, drives RSS ordering |
| `draft` | `true` = excluded unless `--buildDrafts` |
| `description` | Meta description |
| `bookHidden` | Hide from sidebar |
| `bookCollapseSection` | Start section collapsed |
| `bookFlatSection` | Render section children flat |

## YAML, TOML or JSON

All three delimiters work. YAML is the convention:

```yaml
---
title: "Page"
weight: 10
---
```

```toml
+++
title = "Page"
weight = 10
+++
```
