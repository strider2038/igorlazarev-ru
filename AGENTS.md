# agents.md — контекст для автоматизированных агентов

## Проект

Репозиторий **igorlazarev-ru** — исходники личного блога [igorlazarev.ru](https://igorlazarev.ru): статический сайт на **Hugo** с русским контентом, темой **hugo-theme-stack**, поиском (JSON на главной), RSS и комментариями **giscus** (настройки в `hugo.yaml`).

Отдельно собираются **слайды** (Reveal.js через **reveal-hugo**): свой конфиг `hugo-slides.yaml`, контент в `content/slides/`, публикация в `public/slides/`. Основной сайт в `hugo.yaml` игнорирует `content/slides` через `ignorefiles`.

Деплой: GitHub Actions (`.github/workflows/deploy.yaml`) при пуше в `master` — Extended Hugo 0.145.0, затем `hugo --minify` и второй проход с `--config hugo-slides.yaml`, выкладка `public/` по FTP.

## Зависимости и окружение

| Компонент | Назначение |
|-----------|------------|
| **Hugo Extended** ≥ **0.145** | Сборка сайта и темы (SCSS и т.п. в extended). В CI зафиксировано `0.145.0`. |
| **Git** + **submodules** | Темы подключаются как субмодули (см. `.gitmodules`). После клонирования: `git submodule update --init --recursive`. |
| **Go** (модуль не обязателен для блога) | Локальный просмотр: `go run main.go` отдаёт `./public` на `:1313` после сборки. |
| **[Task](https://taskfile.dev/)** (опционально) | Обертки в `Taskfile.yml`: `post`, `build`, `serve`, `dev-slides`. |

### Темы (submodules)

- `themes/hugo-theme-stack` — основной сайт.
- `themes/reveal-hugo` — презентации (URL в `.gitmodules` через SSH; при необходимости заменить на HTTPS для окружений без SSH-ключей).

## Структура (важное)

- `hugo.yaml` — основной конфиг блога.
- `content/post/` — посты; типичный путь: `content/post/YYYY-MM-slug/index.md` (см. существующие посты).
- `content/page/` — статические страницы (about, search, archives, slides-лендинг и т.д.).
- `archetypes/default.md` — шаблон front matter для `hugo new` (title/slug из имени, черновые categories/tags).
- `layouts/` — переопределения шаблонов темы (например, `layouts/partials/head/custom.html`).
- `static/`, `assets/` — статика и ресурсы обработки изображений темой.

## Добавление новых статей (обязательно через Hugo)

**Новые статьи блога создавать только командой Hugo**, а не копированием файлов вручную, чтобы сработал archetype и корректные метаданные.

Базовый вариант (подставьте свой slug вместо `my-article`):

```bash
hugo new content/post/$(date '+%Y-%m')-my-article/index.md
```

Или эквивалент через Task (добавляет файл и делает `git add .`):

```bash
task post my-article
```

После создания отредактируйте front matter (`title`, `slug`, `date`, `categories`, `tags`, `image` и т.д.) и тело в Markdown.

Черновики: при локальной разработке можно включить `buildDrafts: true` в конфиге или использовать флаги сервера (`hugo server -D`), не меняя прод-настройки без необходимости.

## Сборка и локальный просмотр

```bash
# только основной сайт
hugo

# как в CI: основной + слайды
task build

# собрать и отдать public на http://localhost:1313
task serve
```

Слайды в режиме разработки:

```bash
task dev-slides
```

## Полезные ссылки в репозитории

- Человеческое README: `README.md` (установка Hugo, темы, giscus, иконки).
- Рецепт презентаций упомянут в README (внешняя статья).

При изменении конфигов или путей контента проверяйте, что CI по-прежнему выполняет обе команды `hugo` (основной и `hugo-slides.yaml`), иначе на прод попадёт неполный `public/`.
