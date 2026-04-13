# Post Page Overrides

> Applies to article detail pages.  
> These rules override `design-system/igorlazarev-dev-blog/MASTER.md`.

---

## Reading Layout

- Main article column: `max-width: 72ch`.
- Optional right TOC rail on `>= 1280px`; hide TOC on small screens.
- Keep header metadata compact: date, reading time, tags, series.

## Typography Overrides

- Body size `18px` on desktop, `16px` on mobile.
- Paragraph spacing `1em` with strong heading separation (`2em` before `h2`).
- Inline code: higher contrast background and `0.2em 0.35em` padding.

## Code Block Rules

- Horizontal scrolling enabled; no wrapping that breaks code semantics.
- Add top utility row for language label and copy action.
- Keep line numbers subtle, never lower contrast than readable threshold.

## Media & Embeds

- Images remain within content width, with optional caption below.
- Tables auto-scroll on mobile in isolated wrapper.
- External embeds (video/slides) must keep fixed aspect ratio.

## Interaction

- Progress indicator is allowed if it does not overlap article text.
- Anchor links for headings appear on hover/focus.
- Respect `prefers-reduced-motion`; no animated background effects.

## Post-Specific Anti-Patterns

- Full-width paragraphs spanning entire viewport.
- Decorative motion near code blocks.
- Sticky UI elements covering heading anchors.
