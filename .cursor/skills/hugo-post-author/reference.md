# Reference

## Front Matter Defaults

For new source posts, prefer:

```yaml
title: '...'
slug: '...'
translationKey: ...
date: '...'
categories: ["..."]
tags: ["..."]
image: "poster.webp"
```

Notes:

- `translationKey` should normally match `slug`.
- Keep categories and tags concise.
- For English translations, preserve `slug`, `translationKey`, `date`, and `image`.

## Tone Rules

- Keep the author's voice personal and direct.
- Make the text cleaner, but not more generic.
- Prefer short paragraphs over long blocks.
- Avoid overblown AI-style intros and conclusions.
- If the source material is compact, keep the output compact.

## Note vs Article

Use a `note` when:

- the user gives a short reflection
- the text is closer to an observation than a tutorial
- the best result is 3-6 paragraphs

Use an `article` when:

- the topic needs sections
- there are examples, comparisons, or code blocks
- the reader benefits from a guided structure

## Translation Rules

- Translate idiomatically, not mechanically.
- Keep markdown, links, and fenced code intact.
- Keep examples and code comments as-is unless they are prose-heavy and clearly need translation.
- Preserve the author's level of informality.

## Cover Prompt Pattern

Always propose 2-4 prompts in English.

Template:

```text
Minimal tech vector-style editorial illustration for a software engineering blog cover.
Topic: [short phrase].
Main subject: [primary object or metaphor].
Supporting subject: [secondary object, if needed].
Composition: centered, simple, clean, readable when square-cropped, generous safe margins.
Style: flat or softly isometric minimal illustration, crisp shapes, subtle depth, restrained palette, clean background, modern technical editorial feel.
Output: horizontal 4:3 cover, exported as webp.
Negative constraints: no text, no letters, no captions, no logos, no watermark, no photorealism, no clutter, no busy background, no tiny UI details, no important details near edges.
```

## Prompt Concepts

- `desk-scene`: laptop, phone, notes, calm workspace
- `single-object`: one terminal, card, dashboard, server, notebook
- `paired-objects`: draft and final text, AI node and editor, raw and structured data
- `simple-workflow`: idea -> draft -> publish, code -> metrics -> dashboard
- `abstract-metaphor`: layered cards, paths, connected blocks

## Translation Prompt Examples

When translating a Russian post into English, cover prompts usually do not need to change. Reuse the same visual concept unless the user asks for a new cover.
