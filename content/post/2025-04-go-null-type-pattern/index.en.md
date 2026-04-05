---
title: 'Reducing nil pointer panic risk with the Null Type pattern'
slug: 'go-null-type-pattern'
translationKey: go-null-type-pattern
date: '2025-04-05'
categories: ["Programming"]
tags: ["Golang", "null", "typing", "pattern"]
image: "poster.jpg"
---

In the previous [article](https://igorlazarev.ru/p/nullable-or-not-nullable/) (Russian) I looked at the risks of nullable types.
In Go such data is usually modeled with pointer fields, but there are other approaches.
This post covers the Null Type pattern, which reduces the chance of nil pointer panics.

<!--more-->

## Problem context

Suppose we handle an HTTP request whose contract allows nullable types.
The payload has two fields: `name` (`null` means “no name”)
and `count` (`null` means “no count”). A JSON schema for this contract
might look like this:

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

We can model that in Go as follows.

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

Pointer fields demand care: you must always check for `nil`.

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

Comparing these fields is also non-trivial.

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

To lower nil pointer risk, you can use the Null Type pattern. Examples
appear in the standard library ([`sql.NullString`](https://pkg.go.dev/database/sql#NullString),
[`sql.NullInt64`](https://pkg.go.dev/database/sql#NullInt64)) and in popular packages
(e.g. [google/uuid](https://pkg.go.dev/github.com/google/uuid#NullUUID)).
The usual recipe is a dedicated type with methods for encoding and decoding:

* `Scan()`, `Value()` — database encoding/decoding;
* `MarshalJSON()`, `UnmarshalJSON()` — JSON;
* `MarshalText()`, `UnmarshalText()` — text;
* `MarshalBinary()`, `UnmarshalBinary()` — binary formats.

Below is an implementation for our contract, assuming the types are used with JSON and a database.

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

Because `Count` is composite and might map to two DB columns, we skip `Scan()` and `Value()` here
and only add `MarshalJSON()` and `UnmarshalJSON()`.

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

## Usage example

Rewriting the earlier snippet with the Null Type pattern:

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

What changed?

* Some redundant `Valid` checks can go away (they used to be mandatory).
* Core business logic still checks `Valid` where it matters.
* Comparison becomes trivial: `r1.Count == r2.Count` (only if every field of the struct is `comparable`).
* Field paths get longer: `r.Count.Count.Value`.

Initialization is a bit more verbose.

```go
var r Request

r.Name = NullString{Valid: true, String: "name"}
r.Count = NullCount{Valid: true, Count: Count{Value: 1, Unit: "kg"}}
```

Constructors fix that.

```go
func NewNullString(s string) NullString {
    return NullString{Valid: true, String: s}
}

func NewNullCount(value int, unit string) NullCount {
    return NullCount{Valid: true, Count: Count{Value: value, Unit: unit}}
}
```

Then:

```go
var r Request

r.Name = NewNullString("name")
r.Count = NewNullCount(1, "kg")
```

You can also add helpers or proxy methods.

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

## Alternative

The Null Type pattern is not the only option. With many fields it can hurt readability.
If a pointer is acceptable for the whole struct, nil checks inside methods may be simpler—but you must:

1) use pointer receivers on all methods;  
2) guard the receiver against `nil` in every method.

Example for `Count`:

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

## Conclusion

The code becomes safer and often clearer. Benefits of the Null Type pattern:

1. No nil pointer panics from these fields.  
2. Easier comparison of `comparable` structs (no custom `Equal` with nil branches).

Applying it everywhere can overcomplicate the codebase. It fits primitives and small structs best;
for large structs, prefer other safe-design techniques.
