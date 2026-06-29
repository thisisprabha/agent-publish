---
name: changelog
description: Date-stamped list layout for release notes, version histories, and iteration logs.
version: "1.0.0"
author: agent-publish
tags: [changelog, release, version, history, log]
license: MIT
homepage: https://github.com/thisisprabha/agent-publish
---

# Changelog

Output type for dated release notes and iteration logs.

## Description

Date-stamped list layout with clear hierarchy for versions, milestones, and shipped changes. Optimized for scanning history.

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

- Markdown headings are styled as version stamps.
- Lists and code blocks are given extra vertical breathing room.
