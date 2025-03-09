---
title: "Настройка покрытия тестами проекта на Go в GitLab CI"
date: 2019-03-16
categories: ["CI"]
tags: ["go", "gitlab", "ci", "testing"]
---

Go - относительно молодой и динамично развивающийся язык. Инструменты и библиотеки для языка довольно быстро меняются. Поэтому при поиске каких-то типовых решений часто натыкаешься на устаревшие подходы и в процессе работы узнаешь, что некоторые вещи можно решить проще. Например, так получилось с измерением покрытия кода тестами. На GitHub довольно много библиотек и скриптов для оценки покрытия мультипакетных проектов на Go, но оказывается, все можно решить с помощью встроенных инструментов. По крайней мере, это касается наиболее свежей версии v1.12 на текущий момент.

В заметке приведена инструкция по настройке измерения покрытия тестами для приватного проекта на GitLab.

<!--more-->

## Измерение покрытия тестами

Предположим, что у нас есть мультипакетный проект на Go со структурой, описанной в [golang-standards/project-layout](https://github.com/golang-standards/project-layout). В проекте есть тесты разных категорий. Unit-тесты расположены в пакетах `internal`, `pkg`, функциональные и интеграционные тесты в директории `test`. Стоит задача подсчитать общее покрытие всего кода всеми возможными видами тестов. Сделать это можно двумя инструкциями.

Запуск всех тестов и запись профиля покрытия в файл `coverage.out`.

```bash
go test $(go list ./... | grep -v vendor) -race -coverprofile=coverage.out
```

Вывод отчета о покрытии в консоли.

```bash
go tool cover -func=coverage.out
```

Вывод последней команды будет содержать подробные проценты покрытия по всем функциям в пакетах и в конце строчку с общим процентом покрытия всех модулей.

```text
github.com/strider2038/message-router/config/Config.go:16:				LoadConfigFromEnvironment	100.0%
github.com/strider2038/message-router/producing/KafkaMessageProducer.go:15:		NewKafkaMessageProducer		100.0%
github.com/strider2038/message-router/producing/KafkaMessageProducer.go:19:		Produce				100.0%
github.com/strider2038/message-router/producing/KafkaWriterFlyweightFactory.go:10:	NewKafkaWriterFlyweightFactory	100.0%
github.com/strider2038/message-router/producing/KafkaWriterFlyweightFactory.go:16:	CreateWriterForTopic		100.0%
github.com/strider2038/message-router/producing/KafkaWriterFlyweightFactory.go:29:	PoolSize			100.0%
github.com/strider2038/message-router/server/DispatchingServer.go:17:			NewDispatchingServer		100.0%
github.com/strider2038/message-router/server/MessageDispatcher.go:17:			Handle				100.0%
total:											(statements)			100.0%
```

## Настройка GitLab CI

Разберем настройку GitLab CI на примере файла `.gitlab-ci.yml`. Задача - измерять покрытие тестами и выводить в виде значка в файле `README.md` (на главной странице проекта) и генерировать отчет с подробным профилем покрытия в виде статичных HTML-страниц на GitLab Pages.

```yaml
variables:
  DOCKER_DRIVER: overlay2

stages:
  - test
  - deploy

test:
  stage: test
  image: golang/alpine
  before_script:
    - go version
    - go get
  script:
    - go test $(go list ./... | grep -v vendor) -race -coverprofile=coverage.out
    - go tool cover -func=coverage.out
  artifacts:
    paths:
      - coverage.out
    expire_in: 1 day

pages:
  stage: deploy
  image: golang/alpine
  dependencies:
    - test
  script:
    - go tool cover -html=coverage.out -o coverage.html
    - rm -rf public
    - mkdir -p public
    - cp coverage.html ./public/index.html
  artifacts:
    paths:
      - public
    expire_in: 30 days
  only:
    - master
```

Конфигурация состоит из двух задач `test` и `pages`, разделенных на два этапа `test` и `deploy` соответственно. Первая задача отвечает за тестирование кода с составлением профиля покрытия, который передается на следующий этап с помощью [артефактов](https://docs.gitlab.com/ee/user/project/pipelines/job_artifacts.html). Вторая задача отвечает за генерирование HTML-отчета и его доставку на статические страницы GitLab Pages.

Рассмотрим подробно каждую инструкцию задачи `test`.

* `stage: test` - привязка задачи `test` к стадии `test`
* `image: golang/alpine` - использование Docker-образа [golang/alpine](https://hub.docker.com/_/golang)
* `before_script:`
  * `go version`- вывод версии Go (для диагностики потенциальных проблем)
  * `go get` - установка зависимостей (подразумевается, что в проекте находится файл модулей `go.mod`)
* `script` - рассмотренные выше инструкции для тестирования кода и вывода отчета в консоль
* `artifacts` - сохранение профиля покрытия `coverage.out` для следующей стадии (если нет необходимости генерировать HTML-отчет, то этот раздел можно не указывать)

Основные инструкции для доставки отчета на GitLab Pages задачи `pages`.

* `stage: deploy` - задача привязывается к стадии доставки кода (ее следует запускать после доставки кода на релизный сервер, например)
* `dependencies` - обязательно нужно указать задачу, на которой были сгенерированы артефакты, иначе они не загрузятся для текущей задачи
* `script`
  * `go tool cover -html=coverage.out -o coverage.html` - гененирование стандартного HTML-отчета о покрытии модулей
  * `rm -rf public` - удаление директории (если такая есть в репозитории проекта), которая необходима для статичных страниц GitLab Pages
  * `mkdir -p public` - создание пустой директории
  * `cp coverage.html ./public/index.html` - копирование отчета в директорию `public`, которая будет обслуживаться web-сервером GitLab Pages
  * `artifacts` - необходимы для загрузки на GitLab Pages
  * `only` - доставку отчета следует делать только для основной ветки `master`

"Вишенкой на торте" служит значок `coverage` с процентом покрытия тестами в файле `README.md`. В GitLab CI существует встроенный [инструмент генерирования значков](https://docs.gitlab.com/ee/user/project/pipelines/settings.html#test-coverage-parsing). Чтобы настроить автоматическое генерирование значка необходимо зайти на страницу настроек проекта `Settings -> CI/CI -> General pipelines` (путь актуален для версии GitLab v11.8) и указать регулярное выражение `^total:.*\d+.\d+%`, которое будет парсить вывод команды `go tool cover` и сохранять процент покрытия. Затем необходимо скопировать текст для вставки значка в markdown-синтаксисе и вставить его в файл `README.md`.
