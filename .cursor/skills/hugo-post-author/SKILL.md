---
name: hugo-post-author
description: Turn rough user text into a Hugo blog post for igorlazarev.ru, or translate an existing Russian post into English. Use when the user drafts a new article, asks to create a new post, wants a note/article formatted for Hugo, or asks for `index.en.md`. The workflow must create new posts through Hugo, preserve the author's tone, and finish by proposing image prompts for the cover.
---

# Hugo Post Author

## Quick Start

Choose one workflow:

1. `new-post`
   - Take rough user text or dictation.
   - Turn it into either a short note or a fuller article.
   - Create the post through Hugo.
   - Fill front matter and body.
   - End by proposing cover-image prompts.

2. `translate-post`
   - Read an existing Russian post.
   - Create or update `index.en.md` in the same bundle.
   - Keep structure, code blocks, links, and meaning.
   - End by proposing cover-image prompts if useful.

## Guardrails

- New blog posts must be created only through Hugo, not by manually copying files.
- Use a page bundle path like `content/post/YYYY-MM-slug/index.md`.
- Prefer the local Hugo binary if present: `./bin/hugo new ...`.
- Keep the author's voice direct, human, and compact.
- Do not inflate a short note into a long essay.
- If the user's input is rough or fragmentary, improve structure and readability but do not replace their point of view.
- Default featured image name: `poster.webp`.
- Always finish by proposing 2-4 cover prompts in English.

## New Post Workflow

### 1. Infer article shape

Decide whether the material is:

- a `note`: short personal observation, announcement, reflection, or compact idea
- an `article`: longer technical explanation, comparison, tutorial, or structured argument

Default to `note` when ambiguous.

### 2. Infer metadata

Prepare:

- `title`
- `slug`
- `translationKey` equal to the slug
- `date`
- `description`
- `categories`
- `tags`
- `image: "poster.webp"`

Prefer concise slugs in English transliteration or English wording.

### 3. Create the post

Create the file via Hugo:

```bash
./bin/hugo new content/post/$(date '+%Y-%m')-slug/index.md
```

If the local Hugo binary is unavailable but project tooling exists, use:

```bash
task post slug
```

### 4. Write the body

Rules:

- Start with a strong first paragraph that frames the point.
- Insert `<!--more-->` after the intro, usually after the first paragraph.
- Add a short `description` to front matter for homepage previews.
- Use sections only when they help.
- Keep paragraphs short and readable.
- Preserve useful links and examples.
- Prefer Russian for new source posts unless the user asks otherwise.

### 5. Close with cover prompts

After writing the post, propose 2-4 image prompts:

- in English
- minimal tech vector-style
- no text inside the image
- centered composition
- suitable for `poster.webp`

For prompt construction, follow [reference.md](reference.md).

## Translation Workflow

### 1. Locate the source

Prefer the current open Russian post. If unclear, infer from context or ask.

### 2. Create or update English file

For page bundles, create or update `index.en.md` next to `index.md`.

### 3. Preserve metadata

Keep aligned with the source post:

- `slug`
- `translationKey`
- `date`
- `description`
- `image`

Translate when appropriate:

- `title`
- `categories`
- `tags`

### 4. Translate the content

Rules:

- Translate prose and headings naturally, not word-for-word.
- Keep markdown structure intact.
- Do not translate code blocks.
- Do not break links or fenced code.
- Keep the English concise and readable.
- Preserve `<!--more-->` placement if present.

### 5. Final check

- The English version should read like a native short technical blog post.
- Front matter should remain valid.
- File naming should match the current bundle convention.

## Output Format

When done, summarize:

- which file was created or updated
- whether the result is a note or an article
- proposed cover prompts

## Additional Resources

- For metadata defaults, tone, translation notes, and cover-prompt patterns, see [reference.md](reference.md).
