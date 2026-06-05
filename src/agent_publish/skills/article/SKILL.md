# Article

Output type for long-form, narrative content.

## Description

Centered, readable layout optimized for essays, reports, and research posts. Generous line-height, comfortable measure, and a clean editorial feel.

## Template Vars

- `html_title` — `<title>` tag content
- `author_meta` — `<meta name="author">` tag (optional)
- `page_title` — `<h1>` text
- `css` — inline CSS string
- `fingerprint` — content fingerprint
- `date` — publication date
- `body` — converted HTML body
- `entry_type` — entry category label
- `reading_time` — estimated minutes
- `og_tags` — Open Graph meta tags
- `favicon_tag` — favicon `<link>` tag (optional)
- `site_title_tag` — site title above page header (optional)

## Processing Notes

- TOC is enabled by default when 2+ headings exist.
- Mermaid diagrams are preserved if present.
