---
title: Creating a Hugo Website from trading.wiki
date: '2026-10-21T16:27:59+01:00'
tags: [potential/short, analyst/jehosaphat-research]
type: note
draft: true
---
# Creating a Hugo Website from trading.wiki

## Overview

Your trading.wiki has been normalized with 1496 markdown files, all with proper YAML front matter. This guide walks you through creating a Hugo static website from this content.

## Prerequisites

### Install Hugo

Choose one of these methods:

**Option A: Package manager (Fedora)**
```bash
sudo dnf install hugo
```

**Option B: Package manager (Ubuntu/Debian)**
```bash
sudo apt-get install hugo
```

**Option C: Download binary**
```bash
wget https://github.com/gohugoio/hugo/releases/latest/download/hugo_0.120.4_linux-amd64.tar.gz
tar -xzf hugo_0.120.4_linux-amd64.tar.gz
sudo mv hugo /usr/local/bin/
hugo version
```

## Step 1: Create Hugo Site

```bash
# Create a new Hugo site
hugo new site trading-website
cd trading-website
```

This creates the directory structure:
```
trading-website/
├── archetypes/
├── config.toml
├── content/
├── data/
├── layouts/
└── static/
```

## Step 2: Organize Content

### Option A: Move all content

```bash
# Create subdirectories
mkdir -p content/short content/long

# Move root-level files
cp /home/steve/development/trading.wiki/*.md content/

# Move short/ and long/ files
cp /home/steve/development/trading.wiki/short/*.md content/short/
cp /home/steve/development/trading.wiki/long/*.md content/long/
```

### Option B: Selective import

Choose specific files or categories to import.

## Step 3: Configure Hugo

Edit `config.toml`:

```toml
baseURL = "https://yourdomain.com/"
languageCode = "en-us"
title = "Steve's Trading Wiki"

# Enable tag and category taxonomies
[taxonomies]
  tag = "tag"
  category = "category"

# Theme configuration
theme = "loveit"  # or ananke, even, etc.

# Optional: pretty URLs
[permalinks]
  posts = "/:title/"

# Optional: table of contents
[markup]
  [markup.goldmark.mtoc]
    enable = true
```

## Step 4: Choose a Theme

Popular Hugo themes:

- `loveit` - Feature-rich, highly customizable
- `even` - Minimalist, clean design
- `ankake` - Default, simple
- `hello-friend` - Simple and elegant

Install a theme:
```bash
# Using git submodule
git submodule add https://github.com/panr/hugo-theme-even themes/even

# Or download and extract manually
```

## Step 5: Build and Run

```bash
# Build the site
hugo

# Start development server with live reloading
hugo server

# Visit http://localhost:1313 to preview
```

## Content Format

Your normalized markdown files have this structure:

```markdown
# Techtronic Industries

Jehoshaphat Research published on Techtronic Industries...
```

Hugo will automatically:
- Parse the YAML front matter
- Create tag pages based on the `tags` field
- Generate a table of contents if enabled
- Render markdown to HTML

## Tag Support

The normalized tags format `tags: ["potential/short", "analyst/jehosaphat-research"]` will work automatically with Hugo's taxonomy system. Each tag will generate its own archive page.

## Excluded Directories

The `.agents/` and `.playbooks/` directories were excluded from normalization and should be excluded from your Hugo site, as they contain skill definitions and playbook content, not trading notes.

## Next Steps

1. Install Hugo (see above)
2. Create a new Hugo site
3. Move your 1496 normalized markdown files to `content/`
4. Configure `config.toml`
5. Choose and install a theme
6. Run `hugo` to build the site
7. Preview with `hugo server`

For questions about specific Hugo features or theme customization, consult the [Hugo documentation](https://gohugo.io/documentation/).
