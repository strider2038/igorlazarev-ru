---
date: '2025-03-12T21:42:31+03:00'
draft: true
title: 'Новая жизнь журнала на Hugo'
image: 'hugo-logo.svg'
---

Перевозил сайты на новый хостинг и заодно решил стряхнуть пыль с полок и заняться своим журналом. 
Предыдущая версия журнала поддерживалась с помощью статического генератора сайтов [Jekyll](https://jekyllrb.com/). 
Моментами это было неудобно: нужно было тянуть зависимости на Ruby, периодически от security бота github прилетали 
оповещения об уязвимостях (хотя для локальной работы они вообще не критичны). Тем временем где-то 
в Golang телеграм каналах периодически мелькал Hugo.

[Hugo](https://gohugo.io/) — генератор статических сайтов, написанный на языке Go. По заявлению с официального сайта, 
это «самая быстрая в мире платформа для создания сайтов». Hugo устанавливается в виде привычного приложения
(можно установить на любую популярную ОС - Linux, macOS, Windows) и включает в себя мощную систему шаблонов.

Для начала работы достаточно выбрать понравившуюся [тему](https://themes.gohugo.io/). Лично мне в конечном
счете приглянулась [hugo-theme-stack](https://stack.jimmycai.com/). Тема минималистична и не перегружена деталями. 
В ней есть удобные меню, разбивки по категориям и тегам, и многое другое. Так же мне понравилась достаточно
детальная [документация](https://stack.jimmycai.com/config/).

Следующим шагом была адаптация репозитория на [Github](https://github.com/strider2038/igorlazarev-ru).
Выбросил устаревший CI/CD пайплайн на Travis CI и заменил его на Github Actions. Поиск подходящих action'ов
для сборки и деплоя занял буквально несколько минут. Для сборки сайта использовал 
[peaceiris/actions-hugo](https://github.com/marketplace/actions/hugo-setup), а для деплоя по FTP на хостинг
[SamKirkland/FTP-Deploy-Action](https://github.com/marketplace/actions/ftp-deploy). В конечном счете получился
такой конфиг. Просто и эффективно!

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
          hugo-version: '0.145.0'
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
