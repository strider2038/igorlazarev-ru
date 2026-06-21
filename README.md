# igorlazarev-ru

Исходный сайт блога о программировании <http://igorlazarev.ru>

## Разработка

Для разработки необходимо установить локально [Hugo](https://gohugo.io) (версия >= 0.160).

Используются темы

* [hugo-theme-stack](https://stack.jimmycai.com/) как основная;
* [reveal-hugo](https://github.com/joshed-io/reveal-hugo) для презентаций.

## Система комментариев

Используется [giscus](https://giscus.app/ru). 

## Установка новых тем

```shell
git submodule add https://github.com/<path-to>/<repository>.git themes/<theme-name>
```

Рецепт как добавить тему с презентациями <https://haseebmajid.dev/posts/2024-05-26-how-to-add-hugo-revealjs-to-a-hugo-site/>

## Частые вопросы

* Иконки можно брать отсюда <https://tabler.io/icons>

## Telegram анонсы новых постов

После деплоя workflow может отправлять анонсы новых постов в Telegram-канал.

Логика:

* сообщение отправляется только для **новых** файлов `content/post/**/index.md`
* правки существующих постов не анонсируются повторно
* на `re-run` workflow повторная отправка отключена
* текст анонса берётся из `telegram.txt` в page bundle поста (2–4 предложения, plain text)
* без `telegram.txt` job падает — анонс готовится при написании поста, а не в CI

Для настройки добавьте GitHub secrets:

* `TELEGRAM_BOT_TOKEN`
* `TELEGRAM_CHAT_ID`
