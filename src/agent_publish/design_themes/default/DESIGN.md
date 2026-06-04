---
version: alpha
name: "Agent Publish — Default"
colors:
  bg: "#faf8f5"
  fg: "#1c1917"
  muted: "#78716c"
  accent: "#0077b6"
  accent-2: "#48cae4"
  border: "#e7e5e4"
  surface: "#fff"
  code-bg: "#f5f5f0"

  dark:
    bg: "#1a1816"
    fg: "#e8e4df"
    muted: "#9e9891"
    accent: "#4fb3d9"
    accent-2: "#7bcfe8"
    border: "#2e2a26"
    surface: "#22201d"
    code-bg: "#1f1d1a"

typography:
  font-family:
    sans: '-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif'
    mono: 'ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace'
  base:
    size: 16
    weight: 400
    line-height: 1.6
  h1:
    size: 26
    weight: 700
    line-height: 1.2
    letter-spacing: "-0.025em"
  h2:
    size: 18
    weight: 600
    line-height: 1.3
  h3:
    size: 16
    weight: 600
    line-height: 1.4
  meta:
    size: 13
    weight: 400
    line-height: 1.5
spacing:
  scale: [4, 8, 12, 16, 24, 32, 48, 64]
rounded:
  sm: 4
  md: 6
  lg: 8
  full: 9999
---

## Visual Theme & Atmosphere

Clean editorial with generous whitespace. Warm off-white background, stone text, and a calm blue accent. Feels like a well-typeset technical document.

## Color Palette & Roles

| Token | Value | Role |
|-------|-------|------|
| bg | #faf8f5 | Page canvas |
| fg | #1c1917 | Body text, headings |
| muted | #78716c | Secondary text, captions |
| accent | #0077b6 | Links, active borders, focus rings |
| accent-2 | #48cae4 | Blockquote left border |
| surface | #fff | Card-like surfaces (TOC, tables) |
| code-bg | #f5f5f0 | Inline + block code background |

## Typography Rules

- Sans stack for all body text and headings.
- Mono stack for code only.
- H1: 700 weight, tight tracking.
- Body: comfortable 1.6 line-height.

## Component Styling

- `pre`: subtle border that brightens on hover/focus.
- `table`: collapse, alternating row feel via hover state.
- `blockquote`: left accent stripe.
- `toc`: bordered card with nested list.

## Layout Principles

- Max content width: 720px centered.
- Header margin: 2rem top, content flush below.
- Single column; no sidebar.

## Depth & Elevation

- Zero hard shadows. Only subtle border transitions on `pre` hover.

## Do's & Don'ts

- **Do** keep the palette warm-dusty, not cold-grey.
- **Don't** use accent color for body text.
- **Do** maintain 4.5:1 body contrast.

## Responsive Behavior

- Mobile (<640px): reduce base font to 15px, shrink padding to 1rem.
- Tablet (<1024px): slightly wider padding at 1.25rem.

## Agent Prompt Guide

When regenerating this theme:
1. Use `var(--color-bg)` for canvas, not `#fff`.
2. Respect the 720px max-width.
3. Keep pre/code background slightly darker than body for readability.
