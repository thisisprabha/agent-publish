---
name: briefing
description: Compact, scannable layout ideal for daily stand-ups, internal memos, and project rundowns.
version: "1.0.0"
author: agent-publish
tags: [briefing, memo, update, daily, compact]
license: MIT
homepage: https://github.com/thisisprabha/agent-publish
---

# Briefing

Output type for compact, scannable updates.

## Description

Tight margins, smaller type, and a dense layout ideal for daily stand-ups, internal memos, and quick project rundowns.

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

- TOC is skipped by default in briefings.
- Reading time is shown but de-emphasized.
