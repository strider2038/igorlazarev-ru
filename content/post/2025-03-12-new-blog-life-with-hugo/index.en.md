---
title: 'A new life for the blog on Hugo'
slug: 'new-blog-life-with-hugo'
translationKey: new-blog-life-with-hugo
date: '2025-03-12T21:42:31+03:00'
description: 'I moved the blog to Hugo, switched deployment to GitHub Actions, and decided to give the site a fresh start.'
image: 'hugo-logo.svg'
tags: ["news"]
---

I was moving sites to a new host and decided to dust off the shelves and work on my blog again.
The previous version was powered by the static site generator [Jekyll](https://jekyllrb.com/).
That was sometimes awkward: Ruby dependencies, and occasional vulnerability alerts from GitHub’s security bot
(though for local work those were never critical). Meanwhile, [Hugo](https://gohugo.io/) kept popping up
in Go-related Telegram channels.

[Hugo](https://gohugo.io/) is a static site generator written in Go. According to the official site,
it is “the world’s fastest framework for building websites.” Hugo ships as a normal binary
(you can install it on Linux, macOS, or Windows) and includes a powerful templating system.

To get started you pick a [theme](https://themes.gohugo.io/). I ended up liking
[hugo-theme-stack](https://stack.jimmycai.com/): it is minimal without extra noise,
has handy menus, categories, tags, and more—and the [documentation](https://stack.jimmycai.com/config/) is detailed.

Next I adapted the repo on [GitHub](https://github.com/strider2038/igorlazarev-ru).
I dropped the old Travis CI pipeline and replaced it with GitHub Actions. Finding actions
for build and deploy took just a few minutes. I used [peaceiris/actions-hugo](https://github.com/marketplace/actions/hugo-setup)
for the build and [SamKirkland/FTP-Deploy-Action](https://github.com/marketplace/actions/ftp-deploy)
for FTP deploy to hosting. The result looks like this—simple and effective!

```yaml
jobs:
  deploy:
    runs-on: ubuntu-22.04
    concurrency:
      group: ${{ github.workflow }}-${{ github.ref }}
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: true  # Fetch Hugo themes (true OR recursive)
          fetch-depth: 0    # Fetch all history for .GitInfo and .Lastmod

      - name: Setup Hugo
        uses: peaceiris/actions-hugo@v3
        with:
          hugo-version: '0.160.0'
          extended: true

      - name: Build
        run: hugo --minify

      - name: Deploy
        uses: SamKirkland/FTP-Deploy-Action@v4.3.5
        with:
          local-dir: ./public/
          server: ${{ secrets.server }}
          username: ${{ secrets.username }}
          password: ${{ secrets.password }}
```
