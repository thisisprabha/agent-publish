---
version: alpha
name: "Agent Publish -- Default"
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
    surface: "#242220"
    code-bg: "#1f1d1a"

typography:
  font-family:
    display: "Georgia, 'Times New Roman', serif"
    sans: '-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif'
    mono: 'ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace'
  base:
    size: 16
    weight: 400
    line-height: 1.7
  h1:
    family: display
    size: 32
    weight: 700
    line-height: 1.2
    letter-spacing: "-0.025em"
  h2:
    size: 21
    weight: 600
    line-height: 1.3
  h3:
    size: 16
    weight: 600
    line-height: 1.4
    color: muted
  meta:
    size: 13
    weight: 400
    line-height: 1.5
    letter-spacing: 0.06em
    transform: uppercase
    scale: 0.75rem
spacing:
  scale: [4, 8, 12, 16, 24, 32, 48, 64]
rounded:
  sm: 4
  md: 6
  lg: 8
  full: 9999
---

## 1. Visual Theme & Atmosphere

Clean editorial with generous whitespace. Warm off-white background, stone text, and a calm blue accent. Feels like a well-typeset technical document -- strong typographic hierarchy with a serif display heading contrasting against sans-serif body.

## 2. Color Palette & Roles

### Light Mode

- **bg** `#faf8f5` -- Page canvas (warm off-white)
- **fg** `#1c1917` -- Body text, headings (stone)
- **muted** `#78716c` -- Secondary text, captions, H3 color
- **accent** `#0077b6` -- Links, H2 left border, focus rings
- **accent-2** `#48cae4` -- Blockquote left border
- **surface** `#fff` -- Card-like surfaces (TOC, tables)
- **code-bg** `#f5f5f0` -- Inline + block code background

### Dark Mode

- **bg** `#1a1816` -- Deep warm canvas
- **fg** `#e8e4df` -- Light stone text
- **muted** `#9e9891` -- Secondary text
- **accent** `#4fb3d9` -- Brighter blue for dark surfaces
- **accent-2** `#7bcfe8` -- Lighter teal
- **border** `#2e2a26` -- Subtle dark borders
- **surface** `#242220` -- Distinct from bg (stepped luminance)
- **code-bg** `#1f1d1a` -- Between bg and surface

Dark mode uses stepped luminance: `bg < code-bg < surface` so each layer is visibly distinct.

## 3. Typography Rules

- **H1**: Display serif font (Georgia, 'Times New Roman', serif), 32px, bold 700 weight, tight letter-spacing (-0.025em). Visually dominant -- this is the page hero.
- **H2**: Sans-serif, 21px, semibold 600 weight. Clearly smaller/lighter than H1. Left accent bar (3px solid accent) with left padding replaces the old border-top pattern.
- **H3**: Sans-serif, 16px (same as body), semibold 600 weight, muted color. Subtly distinguished from body by weight + color, not size.
- **Body**: Sans-serif system stack, 16px, regular 400 weight, comfortable 1.7 line-height.
- **Meta/eyebrow**: 13px (0.75rem), uppercase, 0.06em letter-spacing, muted color. Distinctly small and airy.
- **Code**: Monospace system stack, 0.85em size for inline, 0.82em for blocks.

Clear hierarchy: H1 (display serif, 32px) > H2 (sans, 21px, accent border) > H3 (sans, 16px, muted) > body (sans, 16px) > meta (sans, 13px, uppercase).

## 4. Spacing System

Base scale: 4, 8, 12, 16, 24, 32, 48, 64px.

- Paragraphs: 1.125rem bottom margin (~18px)
- Heading top margins: H2 2.5rem, H3 1.5rem
- Content padding: 1.75rem default, 1rem mobile, 1.25rem tablet
- Max content width: 720px centered

## 5. Component Styling

- **Tables**: `border-collapse:collapse`, no border-radius (WebKit compat). Hairline `border-bottom:1px solid var(--border)` on th/td. Hover highlight with accent tint. Headings get heavier bottom border.
- **Blockquotes**: Left accent-2 stripe (3px), italic, muted color, no background.
- **TOC**: Surface background, 1px border, 8px radius, compact font-size (0.8125rem). Nested lists with 1.1rem indent.
- **Code blocks**: `code-bg` background, 8px radius, 1px border that brightens to accent on hover. Transition on border-color and box-shadow.
- **Inline code**: Slightly smaller (0.85em), 4px radius, code-bg background.
- **Skip link**: Accent background, white text, slides in on focus.
- **Tags**: Pill-shaped (full radius), surface bg, border, small dot indicator.

## 6. Layout Principles

- Single column, no sidebar. Max 720px centered.
- Header sits flush above main content (header has reduced bottom padding).
- `.main` has zero top padding so content flows directly after header meta.
- Mobile-first responsive with breakpoints at 640px and 1024px.

## 7. Depth & Elevation

- Zero hard shadows. Depth comes from subtle border color transitions.
- `pre` blocks: 1px border that transitions to accent + soft glow ring on hover/focus.
- Tables and TOC use border only, no shadow.
- Print mode: flat white background, no borders or decoration.

## 8. Do's & Don'ts

- **Do** use the serif display font for H1 only -- it's the visual anchor.
- **Do** keep the warm-dusty palette (not cold-grey).
- **Do** maintain 4.5:1+ contrast for body text.
- **Do** use left-border accents (H2, blockquotes) instead of full-width top borders.
- **Don't** use accent color for body text.
- **Don't** add border-radius to tables with border-collapse (WebKit bug).
- **Don't** make dark mode surfaces too close to background -- use stepped luminance.

## 9. Responsive Behavior + Agent Prompt Guide

### Responsive

- Mobile (<640px): base font 15px, padding 1rem, H1 1.35rem, H2 1.05rem, tables scroll horizontally.
- Tablet (<1024px): padding 1.25rem.
- Print: white background, links as URLs, no TOC/skip-link/back.

### Agent Prompt Guide

When regenerating this theme:
1. Use the serif display font stack (Georgia) for H1 -- it defines the visual identity.
2. H2 gets a left accent border, not a top border.
3. H3 should use muted color for clear hierarchy separation.
4. Respect the 720px max-width.
5. Keep pre/code background slightly darker than body for readability.
6. Dark mode: step luminance so bg, code-bg, and surface are all visibly distinct.
7. Never use border-radius on tables with border-collapse.
8. Meta text should be uppercase with wide letter-spacing.
