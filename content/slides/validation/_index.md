---
title: "Валидация на Golang"
outputs: [ "Reveal" ]

reveal_hugo:
  progress: true
---

# Валидация на Golang

Игорь Лазарев
техлид istock.info
https://t.me/strider2038

---

### О себе

* Работаю в IT более 7 лет, около 3 лет пишу на Golang. Изначально писал на PHP.
* Интересы: микросервисная архитектура, Domain Driven Design, Golang.
* Последние 4 года работаю над проектом в промышленной сфере istock.info.
* Начинали с командой около 5 человек, сейчас нас 50+ (три продуктовых команды и менеджемент).

---

### Предпосылки

* Изначально прототип системы делался на основе PHP и фреймворка Symfony.
* Для валидации использовался компонент Symfony Validator.
    * Приятный и расширяемый синтаксис.
    * Есть встроенная система переводов.
    * Сложен в отладке, неудобен для corner cases (например, если нужно заинжектить зависимость).
* При миграции кода на Golang появилась необходимость:
    * использования инструмента валидации, похожего по функциональности;
    * плавного перехода для API;
    * валидации больших сложных структур, в том числе с рекурсией.

---

### Поиск готовых решений

* github.com/asaskevich/govalidator
* github.com/go-ozzo/ozzo-validation

---

### asaskevich/govalidator

```golang
type Document struct {
	Title   string   `valid:"required"`
	Keyword string   `valid:"stringlength(5|10)"`
	Tags    []string // нет встроенной проверки на длину слайса
}

func main() {
	document := Document{
		Title:   "",
		Keyword: "book",
	}

	result, err := govalidator.ValidateStruct(document)
	if err != nil {
		fmt.Println("error: " + err.Error())
	}
}
```

---

### asaskevich/govalidator

* Достоинства:
    * валидация на основе тегов;
    * для простых случаев - минимально и просто;
    * большое количество готовых правил (в виде функций).
* Недостатки:
    * теги используют reflection;
    * теги сложно тонко настроить (проблемы с экранированием строк);
    * отладка - сплошной ад ("почему не работает?");
    * сложно с переводами.

---

### github.com/go-ozzo/ozzo-validation

```go
document := Document{
	Title:    "",
	Keywords: []string{"", "book", "fantasy", "book"},
}

err := validation.ValidateStruct(&document,
	validation.Field(&document.Title, validation.Required),
	validation.Field(&document.Keywords, validation.Required, validation.Length(5, 10)),
)

var errs validation.Errors // map[string]error
if errors.As(err, &errs) {
	for field, e := range errs {
		fmt.Println(field+":", e.Error())
	}
}
```

---

### github.com/go-ozzo/ozzo-validation

* Достоинства:
    * настройка на основе языковых конструкций, а не тегов;
    * => код более гибкий и настраиваемый;
    * структурированные ошибки (код, сообщение, можно составить путь);
    * поддержка переводов;
    * есть много готовых правил, легко добавлять свои.
* Недостатки:
    * местами есть завязка на reflection => трудности с отладкой;
    * местами есть свободные типы `interace{}` => runtime errors;
    * систему переводов надо дорабатывать самостоятельно.

---

### Какие задачи хотелось решить

* Обеспечить полную статическую типизацию без `interface{}`
* Максимальную совместимость по API с Symfony Validator
* Более простую систему переводов
* Стиль, похожий на ozzo validation + структуру как в Symfony Validator для более простой миграции
* Гибкую систему для управления условной валидацией (запускать все, последовательно, одно из правил, группы валидации)
* Передавать контекстные параметры вглубь для сложных вложенных структур и с рекурсией
* Тонкий контроль над формированием путей к ошибкам

---

### github.com/muonsoft/validation

Особенности библиотеки

* Go version >= 1.18
* Гибкое и расширяемое API, созданое с учетом преимуществ статической типизации и дженериков
* Декларативный стиль описания процесса валидации
* Валидация различных типов: логические, числа любого типа, строки, слайсы, карты, `time.Time`
* Валидация собственных типов, удовлетворяющих интерфейсу Validatable
* Гибкая система ошибок с поддержкой переводов и склонений
* Простой способ описания собственных правил с передачей контекста и переводами ошибок
* Подробная документация с большим количеством примеров

---

### Простейший пример

```go
import (
	"context"
	"fmt"

	"github.com/muonsoft/validation"
	"github.com/muonsoft/validation/it"
)

func main() {
	validator, _ := validation.NewValidator()

	err := validator.Validate(context.Background(),
		// список опций-аргументов
		validation.String("", // валидируемое значение // HL
			// далее список правил
			it.IsNotBlank(),      // HL
			it.HasMaxLength(100), // HL
		),
	)

	fmt.Println(err)
	// Output:
	// violation: This value should not be blank.
}
```

---

### Валидация структуры

```go
document := Document{
	Title:    "",                                      // HL00
	Keywords: []string{"", "book", "fantasy", "book"}, // HL00
}

err := validator.Validate(context.Background(),
	validation.StringProperty("title", document.Title, it.IsNotBlank()),                                 // HL01
	validation.CountableProperty("keywords", len(document.Keywords), it.HasCountBetween(5, 10)),         // HL02
	validation.ComparablesProperty[string]("keywords", document.Keywords, it.HasUniqueValues[string]()), // HL03
	validation.EachStringProperty("keywords", document.Keywords, it.IsNotBlank()),                       // HL04
)

if violations, ok := validation.UnwrapViolationList(err); ok { // HL05
	violations.ForEach(func(i int, violation validation.Violation) error { // HL05
		fmt.Println(violation)
		return nil
	})
}
// Output:
// violation at 'title': This value should not be blank.
// violation at 'keywords': This collection should contain 5 elements or more.
// violation at 'keywords': This collection should contain only unique elements.
// violation at 'keywords[0]': This value should not be blank.
```

[//]: # ()
[//]: # (---)

[//]: # ()
[//]: # (### Валидация структуры, атрибут title)

[//]: # ()
[//]: # (.code struct-validation.go /START/,/END/ HL01)

[//]: # ()
[//]: # (---)

[//]: # ()
[//]: # (### Валидация структуры, длина атрибута keywords)

[//]: # ()
[//]: # (.code struct-validation.go /START/,/END/ HL02)

[//]: # ()
[//]: # (---)

[//]: # ()
[//]: # (### Валидация структуры, уникальные значения keywords)

[//]: # ()
[//]: # (.code struct-validation.go /START/,/END/ HL03)

[//]: # ()
[//]: # (---)

[//]: # ()
[//]: # (### Валидация структуры, каждое значение keywords)

[//]: # ()
[//]: # (.code struct-validation.go /START/,/END/ HL04)

[//]: # ()
[//]: # (---)

[//]: # ()
[//]: # (### Валидация структуры, перебор структурированных ошибок)

[//]: # ()
[//]: # (.code struct-validation.go /START/,/END/ HL05)

[//]: # ()

---

### Встроенные переводы

```go
validator, _ := validation.NewValidator(validation.Translations(russian.Messages)) // HL01

document := Document{
	Title:    "",
	Keywords: []string{"", "book", "fantasy", "book"},
}

ctx := language.WithContext(context.Background(), language.Russian) // HL01
err := validator.Validate(
	ctx,
	validation.StringProperty("title", document.Title, it.IsNotBlank()),
	validation.AtProperty(
		"keywords",
		validation.Countable(len(document.Keywords), it.HasCountBetween(5, 10)),
		validation.Comparables[string](document.Keywords, it.HasUniqueValues[string]()),
		validation.EachString(document.Keywords, it.IsNotBlank()),
	),
)

data, _ := json.MarshalIndent(err, "", "\t") // HL02
fmt.Println(string(data))
```

---

### Маршалинг в JSON

```json
[
  {
    "error": "is blank",
    "message": "Значение не должно быть пустым.",
    "propertyPath": "title"
  },
  {
    "error": "too few elements",
    "message": "Эта коллекция должна содержать 5 элементов или больше.",
    "propertyPath": "keywords"
  },
  {
    "error": "is not unique",
    "message": "Эта коллекция должна содержать только уникальные элементы.",
    "propertyPath": "keywords"
  },
  {
    "error": "is blank",
    "message": "Значение не должно быть пустым.",
    "propertyPath": "keywords[0]"
  }
]
```

---

### Типовое использование, реализация интерфейса Validatable

```go
type Product struct {
	Name       string
	Tags       []string
	Components []Component
}

func (p Product) Validate(ctx context.Context, validator *validation.Validator) error { // HL01
	return validator.Validate(
		ctx,
		validation.StringProperty("name", p.Name, it.IsNotBlank()),
		validation.AtProperty(
			"tags",
			validation.Countable(len(p.Tags), it.HasMinCount(5)),
			validation.Comparables[string](p.Tags, it.HasUniqueValues[string]()),
			validation.EachString(p.Tags, it.IsNotBlank()),
		),
		validation.AtProperty(
			"components",
			validation.Countable(len(p.Components), it.HasMinCount(1)),
			// this runs validation on each of the components
			validation.ValidSlice(p.Components), // HL02
		),
	)
}
```

[//]: # ()
[//]: # (---)

[//]: # ()
[//]: # (### Типовое использование, валидация слайса []Validatable)

[//]: # ()
[//]: # (.code typical-usage.go /START BASE/,/END BASE/ HL02)

---

### Типовое использование, запуск на типе Validatable

```go
p := Product{
	Name:       "",
	Tags:       []string{"device", "", "phone", "device"},
	Components: []Component{{ID: 1, Name: ""}},
}

err := validator.ValidateIt(context.Background(), p) // HL03

if violations, ok := validation.UnwrapViolationList(err); ok {
	violations.ForEach(func(i int, violation validation.Violation) error {
		fmt.Println(violation)
		return nil
	})
}
// Output:
// violation at 'name': This value should not be blank.
// violation at 'tags': This collection should contain 5 elements or more.
// violation at 'tags': This collection should contain only unique elements.
// violation at 'tags[1]': This value should not be blank.
// violation at 'components[0].name': This value should not be blank.
// violation at 'components[0].tags': This collection should contain 1 element or more.
```

---

### Немного экзотики, управляющие конструкции

* `validation.AtLeastOneOf()`
* `validation.Sequentially()`
* `validation.All()`
* `validation.When()`
* `validation.Async()`

```go
err := validator.Validate(
	context.Background(),
	validation.AtLeastOneOf(
		validation.CountableProperty("keywords", len(banner.Keywords), it.IsNotBlank()),
		validation.CountableProperty("companies", len(banner.Companies), it.IsNotBlank()),
		validation.CountableProperty("brands", len(banner.Brands), it.IsNotBlank()),
	),
)
```

---

### Немного экзотики, группы валидации (1)

```go
type User struct {
	Email    string
	Password string
	City     string
}

func (u User) Validate(ctx context.Context, validator *validation.Validator) error {
	return validator.Validate(
		ctx,
		validation.StringProperty(
			"email",
			u.Email,
			it.IsNotBlank().WhenGroups("registration"), // HL
			it.IsEmail().WhenGroups("registration"),    // HL
		),
		validation.StringProperty(
			"password",
			u.Password,
			it.IsNotBlank().WhenGroups("registration"),
			it.HasMinLength(7).WhenGroups("registration"),
		),
		validation.StringProperty(
			"city",
			u.City,
			it.HasMinLength(2), // this constraint belongs to the default group
		),
	)
}
```

---

### Немного экзотики, группы валидации (2)

```go
err1 := validator.WithGroups("registration").Validate( // HL
	context.Background(),
	validation.Valid(user),
)
err2 := validator.Validate(
	context.Background(),
	validation.Valid(user),
)
```

---

### Результат

* Получился гибкий инструмент для решения всех поставленных задач.
    * Высокий уровень кастомизации.
    * Простые переводы.
    * Понятный стиль описания.
    * Можно использовать для описания сложных процедур валидации.
* На проекте используется уже несколько лет, эволюционировала вместе с запросами.
* Версия библиотеки near stable (на 95%), но пока еще `v0`.

---

### Ссылки

Спасибо за внимание!
Буду рад любой обратной связи.

https://github.com/muonsoft/validation
