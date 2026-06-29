---
name: deck
description: Full-width presentation layout with larger type scale for slide-like documents and one-pagers.
version: "1.0.0"
author: agent-publish
tags: [deck, presentation, slide, one-pager, wide]
license: MIT
homepage: https://github.com/thisisprabha/agent-publish
---

# Deck

Output type for wide, presentation-style documents.

## Description

Full-width layout with larger type scale and generous whitespace. Designed for slide-like documents, one-pagers, and visual-first content.

## Template Vars

- `html_title` -- `<title>` tag content
- `author_meta` -- `<meta name="author">` tag (optional)
- `page_title` -- `<h1>` text
- `css` -- inline CSS string
- `fingerprint` -- content fingerprint
- `date` -- publication date
- `body` -- converted HTML body
- `entry_type` -- entry category label
- `reading_time` -- estimated minutes
- `og_tags` -- Open Graph meta tags
- `favicon_tag` -- favicon `<link>` tag (optional)
- `site_title_tag` -- site title above page header (optional)

## Processing Notes

- TOC is shown as a horizontal anchor bar when 2+ headings exist.
- Images are displayed edge-to-edge in the main column.
