---
version: alpha
name: "Agent Publish -- Brutalist"
colors:
  bg: "#000"
  fg: "#0f0"
  accent: "#0f0"
  dim: "#0a0"
  dark:
    bg: "#0a0"
    fg: "#000"
    accent: "#000"
    dim: "#050"

typography:
  font-family:
    sans: '"Courier New",monospace'
spacing:
  scale: [4, 8, 16, 24, 32, 48, 64]
---

## Visual Theme & Atmosphere

Pure terminal energy. Green on black. No softening. Borders are loud, hover inverts.

## Color Palette & Roles

| Token | Value | Role |
|-------|-------|------|
| bg | #000 | Page canvas |
| fg | #0f0 | Body text, headlines |
| accent | #0f0 | Links, borders |
| dim | #0a0 | Muted text, code background, table header |

## Typography Rules

- Courier New everywhere. No sans fallback.
- Bold is 700, not 600.
- All headings share the same accent border treatment.

## Component Styling

- `h1`, `h2`: 2px solid border around the heading.
- `pre`: dim background with hover border flash.
- `table`: 2px solid outer border + 1px solid cell borders.
- Links: invert on hover.

## Layout Principles

- Max-width: 720px centered.
- Heavy padding: 2rem.
- No subtlety.

## Responsive Behavior

- Mobile: shrink padding to 1rem.
- Tablet: padding to 1.25rem.

## Agent Prompt Guide

1. Use `#000` and `#0f0` only.
2. Never add rounded corners.
3. Hover must invert (bg -> fg, fg -> bg).
