---
title: "Swagger Mock - сервер для генерирования фиктивных ответов API"
date: 2019-02-22
categories: ["API"]
tags: ["swagger", "php", "road-runner"]
---

Уже довольно продолжительное время я практикую подход Design First в web-разработке. Одним из удобных инструментов этого подхода является ведение документации в формате [OpenAPI / Swagger](https://swagger.io/specification/). Обычно при поступлении задачи от бизнеса собираются front-end и back-end разработчики и составляют контракт в виде описания API endpoint'ов. Затем разработка разделяется и каждый работает со своей частью.

На пути разработки front-end части кроется трудность в том, что нельзя делать обращения к API в это время, т.к. оно не готово. На помощь могут придти различные mock-библиотеки для локальной разработки (без обращения к серверу) или серверные приложения, которые могут отдавать "фейковые" данные.

<!--more-->

Где-то полгода назад мы начали активно описывать документацию в новой версии формата OpenAPI v3.0. В этот момент я столкнулся с неожиданной для себя ситуацией - не нашел ни одного удовлетворяющего наши требования mock-сервера. Большинство решений (см. [Mock Servers](https://openapi.tools/)) либо поддерживало только вторую версию спецификации, либо основывалось на выдаче ответов по примерам ([examples](https://swagger.io/specification/#exampleObject)). Постоянно расписывать и поддерживать примеры для 100+ endpoint'ов занятие довольно неприятное. Хотелось бы иметь какой-то инструмент, который мог бы генерировать данные хотя бы по указанным типам и форматам. Поэтому я решил написать свое решение.

## Основные возможности

Исходный код mock-сервера <https://github.com/swagger-mock/swagger-mock>

Docker-образ <https://hub.docker.com/r/swaggermock/swagger-mock>

Ключевые особенности Swagger Mock Server

* Поддержка спецификации OpenAPI v3.0
* Загрузка спецификации по URL или из локального файла
* Поддержка файлов в формате JSON и YAML
* Генерирование фиктивных данных по указанным схемам
* Выбор возвращаемого ответа по HTTP-заголовку Accept
* Запуск в Docker-контейнере

Ограничения на текущий момент

* Не поддерживаются теги [xml](https://swagger.io/docs/specification/data-models/representing-xml/) - генерирование данных в xml производится только по минимальной схеме
* Не поддерживается разрешение ссылок [$ref](https://swagger.io/docs/specification/using-ref/) по файлам и URL
* Входные данные из тела запроса не валидируются

## Инструкция по запуску

### Docker-контейнер + консольные команды

Наиболее простой способ запуска сервера - запуск с помощью [Docker](https://www.docker.com/) контейнера. Документацию по установке и настройке докера можно найти по ссылке <https://docs.docker.com/install/>.

```bash
docker pull swaggermock/swagger-mock

# загрузка спецификации по URL-ссылке
docker run -p 8080:8080 -e "SWAGGER_MOCK_SPECIFICATION_URL=https://raw.githubusercontent.com/OAI/OpenAPI-Specification/master/examples/v3.0/petstore.yaml" --rm swaggermock/swagger-mock

# загрузка спецификации из локального файла, проброшенного через volume
docker run -p 8080:8080 -v $PWD/examples/petstore.yaml:/openapi/petstore.yaml -e "SWAGGER_MOCK_SPECIFICATION_URL=/openapi/petstore.yaml" --rm swaggermock/swagger-mock
```

### Docker-контейнер + Docker Compose

Также, довольно удобно использовать [Docker Compose](https://docs.docker.com/compose/). Инструкция по установке - <https://docs.docker.com/compose/install/>. Пример файла `docker-compose.yml` для загрузки спецификации по URL-ссылке.

```yaml
version: '3.0'

services:
  swagger_mock:
    container_name: swagger_mock
    image: swaggermock/swagger-mock
    environment:
      SWAGGER_MOCK_SPECIFICATION_URL: 'https://raw.githubusercontent.com/OAI/OpenAPI-Specification/master/examples/v3.0/petstore.yaml'
    ports:
      - "8080:8080"
```

Пример файла `docker-compose.yml` для загрузки спецификации по из локального файла.

```yaml
version: '3.0'

services:
  swagger_mock:
    container_name: swagger_mock
    image: swaggermock/swagger-mock
    environment:
      SWAGGER_MOCK_SPECIFICATION_URL: '/openapi/petstore.yaml'
    volumes:
      - ./examples/petstore.yaml:/openapi/petstore.yaml
    ports:
      - "8080:8080"
```

Запуск локально сервера осуществляется консольной командой

```bash
docker-compose up -d
```

## Пример использования

Если отправить HTTP-запрос `GET http://localhost:8080/pets` при использовании указанной выше спецификации ([petstore.yaml](https://raw.githubusercontent.com/OAI/OpenAPI-Specification/master/examples/v3.0/petstore.yaml)), то можно будет увидеть примерно такой ответ:

```http
HTTP/1.1 200 OK
Cache-Control: no-cache, private
Content-Type: application/json; charset=utf-8
Date: Fri, 22 Feb 2019 18:36:27 GMT
Transfer-Encoding: chunked

[
  {
    "id": 1879967382,
    "name": "Rerum omnis quisquam aut consectetur velit. Dolore non molestiae excepturi veritatis soluta inventore. Delectus minima quis quaerat veniam earum molestiae.",
    "tag": "Qui aliquid ut quia voluptas. Dolorum aut tenetur eligendi delectus et omnis non."
  },
  ...
]
```

Как видно, качество генерируемых данных зависит напрямую от точности спецификации. Если у вас есть ограничения по длине строк, формату, размеру массивов, то их необходимо указывать в спецификации. В качестве примера возьмем другую модель (полный текст по [ссылке](https://github.com/swagger-mock/swagger-mock/blob/master/examples/persons.yaml)).

```yaml
components:
  schemas:
    Person:
      required:
        - id
        - email
        - name
        - birthDate
      properties:
        id:
          type: string
          format: uuid
        email:
          type: string
          format: email
        name:
          type: string
          maxLength: 20
        birthDate:
          type: string
          format: date
        tags:
          type: array
          minItems: 0
          maxItems: 3
          items:
            type: string
            maxLength: 10
```

При HTTP-запросе `GET http://localhost:8080/persons` получится такой ответ.

```http
HTTP/1.1 200 OK
Cache-Control: no-cache, private
Content-Type: application/json; charset=utf-8
Date: Fri, 22 Feb 2019 18:56:35 GMT
Content-Length: 1392

[
  {
    "id": "09e5561c-eee7-3c4e-9ac8-780eae82eb08",
    "email": "joaquin73@hotmail.com",
    "name": "Sit id nam veniam.",
    "birthDate": "2005-02-04",
    "tags": [
      "Nesciunt.",
      "Enim est.",
      "Non."
    ]
  },
  ...
]
```

## Настройки

### Переменные окружения

Mock-сервер настраивается через переменные окружения.

#### SWAGGER_MOCK_SPECIFICATION_URL

* Путь к файлу спецификации OpenAPI v3 (_обязательный_)
* _Возможные значения_: любой правильный URL-адрес или путь к файлу

#### SWAGGER_MOCK_LOG_LEVEL

* Уровень логирования
* _Значение по умолчанию_: `warning`
* _Возможные значения_: `error`, `warning`, `info`, `debug`

#### SWAGGER_MOCK_CACHE_DIRECTORY

* Директория для хранения кеша спецификации
* _Значение по умолчанию_: `/dev/shm/openapi-cache`
* _Возможные значения_: любой правильный путь к существующей директории

#### SWAGGER_MOCK_CACHE_TTL

* Время жизни кеша спецификации в секундах
* _Значение по умолчанию_: 0
* _Возможные значения_: любое положительное целое число

#### SWAGGER_MOCK_CACHE_STRATEGY

* Стратегия кеширования спецификации OpenAPI
* _Значение по умолчанию_: `disabled`
* _Возможные значения_: `disabled`, `url_md5`, `url_and_timestamp_md5`

### Кеш спецификации

При поведении по умолчанию на каждый запрос к серверу происходит парсинг файла спецификации и преобразование его в набор объектов, используемых для генерирования ответа API. Для спецификаций с большим количеством endpoint'ов парсинг может занимать ощутимое время. Для улучшения производительности предусмотрено кеширование результатов парсинга исходя из различных стратегий. Стратегия кеширования задается с помощью переменной окружения `SWAGGER_MOCK_CACHE_STRATEGY`.

* При использовании значения `url_md5` сервер вычисляет md5-хеш по URL и если он не изменился, то используются объекты из кеша.
* При использовании `url_and_timestamp_md5` сервер составляет md5-хеш по URL и временной метке (время последнего изменения файла или значение заголовка `Last-Modified` при обращении по URL к удаленному ресурсу). Если вы используете файл на удаленном сервере, то при выборе данной стратегии необходимо убедиться, что сервер добавляет правильный заголовок `Last-Modified` к ответу за запрос.

Рекомендуемые значения при использовании файла на удаленном сервере, доступном по URL.

* `SWAGGER_MOCK_CACHE_STRATEGY='url_md5'`
* `SWAGGER_MOCK_CACHE_TTL=3600`

Рекомендуемые значения при использовании локального файла.

* `SWAGGER_MOCK_CACHE_STRATEGY='url_and_timestamp_md5'`
* `SWAGGER_MOCK_CACHE_TTL=3600`

## Предложения, пожелания, замечания

Буду рад увидеть любые предложения, пожелания или замечания, а так же баг-репорты. В случае возникновения проблем, пожалуйста, заведите issue на GitHub'е <https://github.com/swagger-mock/swagger-mock/issues>.

При обнаружении бага, запустите mock-сервер с уровнем логирования `SWAGGER_MOCK_LOG_LEVEL=debug` и пришлите содержимое лога `docker logs swagger_mock` при воспроизведении ошибки. Это поможет быстрее разобраться с багом. Спасибо!
