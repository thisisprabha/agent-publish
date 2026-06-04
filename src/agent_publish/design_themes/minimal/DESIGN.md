---
version: alpha
name: "Agent Publish — Minimal"
colors:
  bg: "#fff"
  fg: "#111"
  muted: "#666"
  accent: "#111"
  code-bg: "#f5f5f5"
  dark:
    bg: "#000"
    fg: "#eee"
    muted: "#999"
    accent: "#ccc"
    code-bg: "#1a1a1a"

typography:
  font-family:
    sans: 'system-ui,-apple-system,sans-serif'
    mono: 'monospace'
  base:
    size: 15
    weight: 400
    line-height: 1.6
  h1:
    size: 24
    weight: 500
    line-height: 1.2
  h2:
    size: 17
    weight: 500
    line-height: 1.3
spacing:
  scale: [4, 8, 12, 16, 24, 32, 48]
rounded:
  sm: 0
  md: 0
  lg: 0
---

## Visual Theme & Atmosphere

Pure utility. No color noise. Black on white, system fonts, zero decorative elements.

## Color Palette & Roles

| Token | Value | Role |
|-------|-------|------|
| bg | #fff | Page canvas |
| fg | #111 | Body text |
| muted | #666 | Secondary |
| accent | #111 | Links, borders |
| code-bg | #f5f5f5 | Code background |

## Typography Rules

- System sans for body. Monospace for code.
- H1: 500 weight, tight.
- No tracking adjustments. No serif.

## Component Styling

- `pre` / `code`: light grey background.
- `table`: solid rule borders between rows.
- Links: underline only. No color flash.

## Layout Principles

- Body padding: 2rem all around.
- Max width: 680px.
- Flush left, no centering.

## Responsive Behavior

- Mobile: body padding drops to 1rem.
- Tablet: padding drops to 1.5rem.

## Agent Prompt Guide

1. Never add decorative colors.
2. Use the system font stack.
3. Underline links. No border-bottom transitions.
