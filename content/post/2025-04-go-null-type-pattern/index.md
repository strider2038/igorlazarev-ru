---
title: 'Уменьшаем риск nil pointer panic с помощью Null Type pattern'
slug: 'go-null-type-pattern'
date: '2025-04-05'
categories: ["Программирование"]
tags: ["Golang", "null", "типизация", "паттерн"]
image: "poster.jpg"
---

В предыдущей [статье](/p/nullable-or-not-nullable/) я рассматривал какие риски в себе несут nullable-типы. 
В Golang такие данные обычно описываются с помощью атрибутов-указателей, но есть и другие способы. 
В этой статье я рассмотрю паттерн Null Type pattern, который уменьшит вероятность возникновения nil pointer panic.

<!--more-->

## Контекст проблемы

Предположим, мы обрабатываем HTTP запрос в контракте которого предусмотрено использование nullable-типов.
В запросе есть два атрибута: название `name` (значение `null` указывает на отсутствие названия)
и количество `count` (значение `null` указывает на отсутствие количества). JSON-схема для этого контракта 
будет выглядеть следующим образом:

```yaml
type: object
properties:
  name:
    type: [string, null]
  count:
    type: [object, null]
    properties:
      value:
        type: integer
      unit:
        type: string
```

Тогда структуру для работы с этим кодом можно описать в виде.

```go
type Request struct {
    Name  *string `json:"name"`
    Count *Count  `json:"count"`
}

type Count struct {
    Value int    `json:"value"`
    Unit  string `json:"unit"`
}
```

Использование ссылочных типов требует от программиста быть внимательным и всегда проверять их на `nil`.

```go
var r Request

// ...

if r.Name != nil {
    *r.Name = strings.TrimSpace(*r.Name)
}

if r.Name == nil {
    fmt.Println("no name")
} else {
    fmt.Println("name: ", *r.Name)
}

if r.Count == nil {
    fmt.Println("no count")
} else {
    fmt.Println("count: ", r.Count.Value, " ", r.Count.Unit)
}
```

Так же сравнение этих атрибутов будет выглядеть нетривиально.

```go
func main() {
    var r1, r2 Request
    if EqualCount(r1.Count, r2.Count) {
        fmt.Println("equal count")
    }
}

func EqualCount(c1, c2 *Count) bool {
    if c1 == nil && c2 == nil {
        return true
    }
    if c1 == nil || c2 == nil {
        return false
    }
    
    return *c1 == *c2
}
```

## Null Type pattern

Чтобы уменьшить риск nil pointer panic, можно использовать Null Type pattern. Примеры
реализации не трудно найти как в стандартном пакете ([`sql.NullString`](https://pkg.go.dev/database/sql#NullString), 
[`sql.NullInt64`](https://pkg.go.dev/database/sql#NullInt64)), так и в некоторых популярных пакетах
(например, [google/uuid](https://pkg.go.dev/github.com/google/uuid#NullUUID)).
Следуя логике реализации таких типов следует объявить отдельный тип и добавить ему методы
для интеграции с кодированием и декодированием:

* `Scan()`, `Value()` - кодирование и декодирование в базе данных;
* `MarshalJSON()`, `UnmarshalJSON()` - кодирование и декодирование в JSON;
* `MarshalText()`, `UnmarshalText()` - кодирование и декодирование в текст;
* `MarshalBinary()`, `UnmarshalBinary()` - кодирование и декодирование в бинарном формате.

Рассмотрим пример реализации для нашего контракта, исходя из предположения, что
типы будут использоваться для работы с JSON и базой данных.

```go
var jsonNull = []byte("null")

type NullString struct {
    String string
    Valid  bool
}

func (s *NullString) Scan(value any) error {
    var ns sql.NullString
    if err := ns.Scan(value); err != nil {
        return err
    }

    s.Valid = ns.Valid
    s.String = ns.String

    return nil
}

func (s NullString) Value() (driver.Value, error) {
    if !s.Valid {
        return nil, nil
    }

    return s.String, nil
}

func (s NullString) MarshalJSON() ([]byte, error) {
    if !s.Valid {
        return jsonNull, nil
    }

    return json.Marshal(s.String)
}

func (s *NullString) UnmarshalJSON(b []byte) error {
    if bytes.Equal(b, jsonNull) {
        s.String, s.Valid = "", false

        return nil
    }

    if err := json.Unmarshal(b, &s.String); err != nil {
        return err
    }

    s.Valid = true

    return nil
}
```

Так как `Count` это составной тип и в базе данных он может быть представлен в виде двух колонок, то методы
`Scan()` и `Value()` добавлять не будем, только `MarshalJSON()` и `UnmarshalJSON()`.

```go
type NullCount struct {
    Count Count
    Valid bool
}

func (c NullCount) MarshalJSON() ([]byte, error) {
    if !c.Valid {
        return jsonNull, nil
    }

    return json.Marshal(c.Count)
}

func (c *NullCount) UnmarshalJSON(b []byte) error {
    if bytes.Equal(b, jsonNull) {
        c.Count, c.Valid = Count{}, false

        return nil
    }

    if err := json.Unmarshal(b, &c.Count); err != nil {
        return err
    }

    c.Valid = true

    return nil
}
```

## Пример использования

Перепишем предыдущий код, используя Null Type pattern.

```go
var r Request

r.Name.String = strings.TrimSpace(r.Name.String)

if !r.Name.Valid {
    fmt.Println("no name")
} else {
    fmt.Println("name: ", r.Name.String)
}

if !r.Count.Valid {
    fmt.Println("no count")
} else {
    fmt.Println("count: ", r.Count.Count.Value, " ", r.Count.Count.Unit)
}

var r1, r2 Request
if r1.Count == r2.Count {
    fmt.Println("equal count")
}
```

Что изменилось?

* В некоторых местах можно убрать избыточные проверки на `Valid` (раньше проверять было необходимо).
* В основной логике проверки `Valid` остались (по сути это бизнес-логика).
* Сравнение типов стало тривиальным `r1.Count == r2.Count` (но это возможно только если все атрибуты структуры `comparable`).
* Цепочки обращения к атрибутам стали длиннее `r.Count.Count.Value`.

Еще можно добавить, что инициализация атрибута стала менее удобной.

```go
var r Request

r.Name = NullString{Valid: true, String: "name"}
r.Count = NullCount{Valid: true, Count: Count{Value: 1, Unit: "kg"}}
```

Но эта проблема легко решается добавлением конструкторов.

```go
func NewNullString(s string) NullString {
    return NullString{Valid: true, String: s}
}

func NewNullCount(value int, unit string) NullCount {
    return NullCount{Valid: true, Count: Count{Value: value, Unit: unit}}
}
```

В итоге код будет выглядеть следующим образом:

```go
var r Request

r.Name = NewNullString("name")
r.Count = NewNullCount(1, "kg")
```

Кроме того, отдельные типы можно обогащать любыми вспомогательными или прокси-методами.

```go
func (c NullCount) String() string {
    if c.Valid {
        return c.Count.String()
    }

    return ""
}

func (c NullCount) Add(next NullCount) (NullCount, error) {
    if c.Valid && next.Valid {
        sum, err := c.Count.Add(next.Count)
        if err != nil {
            return NullCount{}, err
        }

        return NullCount{Valid: true, Count: sum}, err
    }
    if c.Valid {
        return NullCount{Valid: true, Count: c.Count}, nil
    }
    if next.Valid {
        return NullCount{Valid: true, Count: next.Count}, nil
    }

    return NullCount{}, nil
}
```

## Альтернатива

Однако, Null Type pattern не является единственным способом решения проблемы. В некоторых случаях он может
быть неудобен и только усложнять работу с кодом. Например, когда в структуре используется большое количество
атрибутов, то это усложняет чтение и понимание кода. Если для этой структуры допустимо всегда использовать
значение по ссылке, то будет проще добавить проверки на nil во все методы. В этом случае всегда необходимо
соблюдать два условия:

1) у всех методов должны быть ресиверы по указателю;
2) во всех методах ресивер необходимо проверять на nil.

Сделаем это на примере `Count`.

```go
func (c *Count) String() string {
    if c == nil {
        return ""
    }

    return fmt.Sprintf("%d %s", c.Value, c.Unit)
}

func (c *Count) Add(next *Count) (*Count, error) {
    if c != nil && next != nil {
        if c.Unit != next.Unit {
            return nil, fmt.Errorf("unit mismatch")
        }

        return &Count{Value: c.Value + next.Value, Unit: c.Unit}, nil
    }
    if c != nil {
        return c, nil
    }
    if next != nil {
        return next, nil
    }

    return nil, nil
}
```

## Заключение

В итоге наш код стал более удобным и безопасным. Среди достоинств Null Type pattern можно отметить.

1. Нет риска nil pointer panic. 
2. Удобнее сравнивать comparable-структуры (не нужно описывать метод Equal с проверкой nil-значений).

Однако, поголовное применение подхода для всех типов может избыточно усложнять код. Поэтому паттерн
имеет смысл использовать только для примитивных типов и для структур с малым количеством атрибутов.
Для больших структур лучше использовать другие способы безопасного программирования.
