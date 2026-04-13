# Design System Master File

> **Logic:** when building a page, check `design-system/igorlazarev-dev-blog/pages/[page-name].md` first.  
> If page overrides exist, they take priority over this file.

---

**Project:** IgorLazarev Dev Blog  
**Category:** Programming Blog / Editorial  
**Voice:** Expert, practical, calm

---

## Core Principles

1. Reading first: article text and code are primary UI objects.
2. Scannability: clear hierarchy, short visual rhythm, predictable spacing.
3. Fast + stable: no layout shifts, minimal animation, optimized images.
4. Accessibility by default: keyboard-first, high contrast, visible focus.

## Color Tokens

### Light Theme

| Token | Value | Purpose |
|---|---|---|
| `--bg` | `#F8FAFC` | Page background |
| `--surface` | `#FFFFFF` | Cards, code frame shell |
| `--text` | `#0F172A` | Primary text |
| `--muted` | `#475569` | Secondary text, metadata |
| `--border` | `#E2E8F0` | Dividers and input borders |
| `--accent` | `#2563EB` | Links, active states |
| `--accent-soft` | `#DBEAFE` | Tag/chip background |

### Dark Theme

| Token | Value | Purpose |
|---|---|---|
| `--bg` | `#020617` | Page background |
| `--surface` | `#0F172A` | Cards, nav, code shell |
| `--text` | `#E2E8F0` | Primary text |
| `--muted` | `#94A3B8` | Secondary text |
| `--border` | `#1E293B` | Dividers and input borders |
| `--accent` | `#60A5FA` | Links, active states |
| `--accent-soft` | `#1E3A8A` | Tag/chip background |

## Typography

- **Headings:** `Inter` (600/700), tight but readable spacing.
- **Body:** `Inter` (400/500), neutral for long-form reading.
- **Code:** `JetBrains Mono` (400/500), only for inline/code blocks.
- **Scale:** `16` base, `1.25` modular ratio for headings.
- **Line height:** `1.7` body, `1.55` headings, `1.6` list items.

## Layout & Spacing

- **Containers:** `max-width: 72ch` for post body; `max-width: 1200px` for listing/home.
- **Grid:** single-column reading flow, optional right rail for TOC on desktop.
- **Spacing scale:** 4 / 8 / 12 / 16 / 24 / 32 / 48 / 64.
- **Section rhythm:** article blocks separated by `32-40px`.
- **Responsive breakpoints:** 375, 768, 1024, 1280, 1440.

## Component Rules

### Navigation

- Sticky header with subtle border and background blur.
- Include clear `Search`, `Posts`, `Tags`, `About`.
- Keep height stable to avoid content jumps.

### Post Cards

- Show title, short excerpt, date, reading time, tags.
- Card hover: only color/shadow change (`150-200ms`), no layout shift.
- Entire card is clickable and has `cursor-pointer`.

### Article Content

- Use prose styles with good defaults for headings, lists, blockquotes.
- Keep images full-width within content column and always include alt text.
- Add anchor links to `h2/h3` for long posts.

### Code Blocks

- Distinct surface, visible border, horizontal scroll without breaking layout.
- Monospace `0.9-0.95rem`, line-height `1.6`, comfortable padding.
- Optional copy button with keyboard-accessible focus ring.

## Interaction & Motion

- Transition duration `150-250ms`, easing `ease-out`.
- Respect `prefers-reduced-motion: reduce`.
- Never use parallax/scroll-jacking on article pages.

## Accessibility Baseline

- Contrast target >= WCAG AA (`4.5:1` for normal text).
- Visible focus styles for all links/buttons/inputs.
- Skip link to main content.
- Logical tab order follows visual order.

## Anti-Patterns

- Emoji as UI icons.
- Low-contrast text or borders in light mode.
- Animated hover transforms that move surrounding content.
- Full-width long text lines on large screens.
- Hidden focus outlines without replacement.
