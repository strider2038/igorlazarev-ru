# Home Page Overrides

> Applies to blog homepage and listing views.  
> These rules override `design-system/igorlazarev-dev-blog/MASTER.md`.

---

## Layout Overrides

- Container: `max-width: 1200px`.
- Desktop grid: `2` columns (`posts` + `sidebar`), mobile: single column.
- Keep hero compact: value proposition + latest post + CTA.

## Content Blocks

1. Intro strip with blog positioning (1 short paragraph).
2. Featured post card (latest or pinned).
3. Post list (title, excerpt, tags, date, reading time).
4. Sidebar (`tags`, `series`, `about`, `rss`).

## Card Behavior

- Hover feedback via border/shadow only (`transition-colors duration-200`).
- Keep metadata aligned to avoid card height jumps.
- Entire post card acts as one click target.

## Navigation & Search

- Search is always visible on desktop.
- On mobile, use prominent search trigger near top content.
- Active nav state uses accent color and semibold text.

## Home-Specific Anti-Patterns

- Overly tall hero that pushes posts below fold.
- Dense multi-column text blocks on mobile.
- More than one visual accent competing with post titles.
