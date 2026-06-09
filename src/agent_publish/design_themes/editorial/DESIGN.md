---
version: alpha
name: "Agent Publish -- Editorial"
colors:
  bg: "#FAFAF8"
  fg: "#1A1916"
  muted: "#6B6560"
  accent: "#8B4513"
  accent-2: "#A0522D"
  border: "#E0DCD6"
  surface: "#F5F3EF"
  code-bg: "#EFEBE5"

  dark:
    bg: "#1C1A18"
    fg: "#E8E4DF"
    muted: "#9E9891"
    accent: "#C8956C"
    accent-2: "#C8956C"
    border: "#3A3632"
    surface: "#2A2624"
    code-bg: "#232120"

typography:
  font-family:
    sans: '-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif'
    serif: 'Georgia,"Playfair Display","Times New Roman",serif'
    mono: 'ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace'
  base:
    size: 16
    weight: 400
    line-height: 1.7
  h1:
    size: 36
    weight: 700
    line-height: 1.15
    letter-spacing: "-0.03em"
    font-family: serif
  h2:
    size: 20
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
    letter-spacing: "0.05em"
    text-transform: uppercase
spacing:
  scale: [4, 8, 12, 16, 24, 32, 48, 64]
rounded:
  sm: 4
  md: 6
  lg: 8
  full: 9999
---

## Visual Theme & Atmosphere

Warm, literary editorial feel — like a well-set book or high-end literary journal. Off-white canvas, serif display headlines, sienna/brown accent, and generous whitespace. Designed for long-form reading and contemplative technical content.

## Color Palette & Roles

| Token | Value | Role |
|-------|-------|------|
| bg | #FAFAF8 | Warm off-white page canvas |
| fg | #1A1916 | Off-black body text |
| muted | #6B6560 | Secondary text, captions, metadata |
| accent | #8B4513 | Warm sienna — links, left-bar accents, focus rings |
| accent-2 | #A0522D | Darker sienna for blockquote borders |
| surface | #F5F3EF | Slightly darker than bg — TOC, table rows |
| code-bg | #EFEBE5 | Warm linen code backgrounds |

## Typography Rules

- **H1**: Serif font stack (Georgia, Playfair Display, Times New Roman). 36px, weight 700, tight letter-spacing -0.03em.
- **H2**: 20px, weight 600. Left border 3px accent, padding-left 1rem, margin-top 2.5rem.
- **H3**: 16px, weight 600, muted color.
- **Body**: System sans-serif stack, 16px, generous line-height 1.7.
- **Meta**: 13px, uppercase, letter-spacing 0.05em, muted color.
- **Mono**: System monospace stack for code.

## Component Styling

- **Tables**: Clean hairline rows only — `border-bottom: 1px solid var(--border)` on th/td. No border-collapse+border-radius (WebKit bug). No outer box border on table.
- **TOC**: Slim left-ruled list. `border-left: 2px solid var(--accent)`, padding-left 1rem. No background, no border-radius — not a card.
- **Blockquote**: `border-left: 3px solid var(--accent-2)`, italic, muted text color.
- **Code blocks**: Subtle border that brightens on hover.
- **Skip link + back link + focus-visible outlines** for accessibility.

## Layout Principles

- Max content width: 720px centered.
- Header margin: 2rem top, content flush below.
- Single column; no sidebar.
- Generous vertical rhythm.

## Depth & Elevation

- Zero hard shadows. Only subtle border transitions on pre hover.
- TOC and blockquote rely on borders, not cards/surfaces.

## Do's & Don'ts

- **Do** keep the palette warm-sienna, never cold-blue.
- **Don't** use accent color for body text — only for links and accents.
- **Do** maintain 4.5:1 body contrast against off-white background.
- **Don't** add border-radius to tables — use hairline rows instead.

## Responsive Behavior

- Mobile (<640px): reduce base font to 15px, shrink padding to 1rem.
- Tablet (<1024px): slightly wider padding at 1.25rem.

## Agent Prompt Guide

When regenerating this theme:
1. Use `var(--bg)` for canvas, not hardcoded white.
2. Respect the 720px max-width.
3. Keep serif font for H1 only — body stays sans-serif.
4. Tables: hairline rows, no border-collapse + border-radius.
5. TOC: left-ruled list, no background, no border-radius.
