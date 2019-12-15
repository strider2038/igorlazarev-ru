---
layout: post
title:  "Nullable или не nullable?"
date:   2019-00-00
categories: api типизация
permalink: /posts/2019-00-00-nullable-or-not-nullable
---

Пожалуй, одна из самых типичных проблем при составлении схем данных - стоит ли объявлять атрибуты с null-значениями? Стоит ли все атрибуты всегда делать nullable или это может привести к неприятным последствиям? В этой статье я постараюсь рассмотреть возможные проблемы nullable-атрибутов.

<!--more-->

## Проблемы типизации

В информатике есть такое понятие как [типобезопасность](https://ru.wikipedia.org/wiki/%D0%A2%D0%B8%D0%BF%D0%BE%D0%B1%D0%B5%D0%B7%D0%BE%D0%BF%D0%B0%D1%81%D0%BD%D0%BE%D1%81%D1%82%D1%8C). Одна из часто встречаемых проблем работы исполняемого приложения - ошибка согласования типов, которая во время исполнения программы может привести к неожиданным последствиям и даже к краху программы. Именно поэтому практически во всех современных языках программирования особое внимание уделяется проблемам типизации.

К общим типам (примитивам) относят

* булевы типы `boolean`
* целочисленные типы `integer`
* вещественные числа `float`
* строковое типы `string`

К составным типам относят

* массивы `array`
* объекты `object`

В разных языках примитивы и составные типы реализованы по разному. Операции между разными типами данных в общем случае невозможны. Например, число нельзя делить на строку. В частном случае, для реализации операций между разными типами данных требуется привести их к одному формату. Например, если нужно к строке добавить строковое представление числа, то это число необходимо сначала правильным образом преобразовать в строку, а потом объединить обе эти строки.

В некоторых языках реализовано автоматическое преобразование и приведение типов. Это имеет свои преимущества и недостатки. С одной стороны, удобство проявляется в том, что программисту можно не указывать явные преобразования (как в предыдущем примере со строкой и числом) и код выглядит более компактным и читаемым. С другой стороны, программа может вести себя не так, как задумано. Например, если числа складывать со строками, то строки могут быть преобразованы к 0 и вероятно результатом работы будет совершенно не то, что задумывал программист.

Кроме самих типов есть еще одно специальное значение - `null`. В компилируемых языках оно означает, что под переменную не выделена область памяти и указатель равен пустому значению. В реляционных базах данных значение NULL говорит о том, что ячейка таблицы не заполнена (оставлена пустой). В динамических языках, таких как JavaScript или PHP это значение говорит о том, что переменная не заполнена. Соответственно, к проблеме типизации еще добавляется проблема null-значений. Например, в компилируемом языке попытка сложить null с числом приведет к фатальной ошибке (т.к. не получится разыменовать указатель в памяти). В динамических языках null будет приведено к 0 или пустой строке, но это не всегда может означать, что это то, что хотел бы видеть программист. Поэтому при работе с nullable переменными всегда следует иметь ввиду что же означает null и обрабатывать поведение программы вручную.

## Потенциальные ошибки в программе, связанные с типизацией

В современных языках особое внимание уделяется ошибкам при работе с типами данных. Например, в новой версии PHP 7.4 добавлена поддержка типизированных свойств классов. Объявление таких свойств переносит заботу о контроле правильности типов с плеч программиста на уровень самого языка и попытка присвоить значение неправильного типа ведет к появлению фатальной ошибки. Это в свою очередь спасает от повреждения данных, с которыми работает программа и позволяет обнаруживать баги на более ранних этапах разработки.

...

## Null и примитивные типы

В крупных проектах для согласования работы между разными частями кода важно использовать соглашения о структурах данных. Например, при разделении веб-системы на клиентскую часть (frontend) и серверную (backend) соглашением может служить формат работы серверного API. В настоящее время наибольшую популярность приобрел формат JSON. Поэтому в целях улучшения взаимодействия frontend и backend, как правило, договариваются о структуре данных, используемых атрибутах и типах для их значений и закрепляют это в документации.

Кроме самих типов еще нужно договориться о том, можно ли использовать значение `null` для атрибутов. Это довольно важная часть соглашения, т.к. значение `null` может по-разному интерпретироваться на frontend и backend и неправильный выбор может вести к неприятным последствиям.

Предположим, что в некоторой структуре JSON есть поле "описание", которое представляет собой строку.

```json
{
    "description": "string"
}
```

Гипотетически у этого поля могут быть два изначальных состояния - _"не заполнено"_ и _"пустое"_. Состояние _"не заполнено"_ можно выразить значением `null`, а состояние _"пустое"_ с помощью пустой строки `""`. И тут важно задаться вопросом: __а есть ли между этими значениями принципиальная разница с точки зрения бизнес-логики?__ Если этой разницы нет, то состояние "не заполнено" можно считать идентичным состоянию _"пустое"_ и выражать его с помощью пустой строки `""`. В противном случае, если разрешить значение `null`, то во всем коде всегда нужно будет учитывать поведение программы в случае равенства атрибута `description = null`. В качестве примера рассмотрим гипотетически код, который должен отображать это описание пользователю системы.

```
if (description == null) {
    description = ""
}

println("Description: " + description)
```

Если не сделать операции, указанной в условном блоке, то в зависимости от языка, значение `null` может быть приведено к пустой строке `""`, а может к строковому представлению `"null"`. В последнем случае пользователь, чаще всего далекий от программирования, увидит непонятное ему значение "null". Более того, если это значение попадет в форму редактирования, то оно будет сохранено и вряд ли это то описание, которое хотел бы сохранить пользователь.

Так как код пишут разные программисты, то программист ответственный за обработку формы может не знать о том, что атрибут `description` может принимать значение `null` и забыть добавить условный блок. Если же договориться о том, что в состоянии "не заполнено" атрибут принимает значение пустой строки и запретить значение `null` (например, при валидации формы на backend), то это снижает риск ошибок с null-значениями.

Рассмотрим подобный случай с числами. Предположим, что в объекте описываются габариты какого-либо объемного предмета.

```json
{
    "width": 123,
    "height": 456,
    "length": 789
}
```

Есть ли у атрибутов ширины, высоты и длины какой-то смысл в значении `null` с точки зрения бизнес-логики? Чем оно отличается от значения `0`? Чаще всего разницы между `null` и `0` нет и значение `null` лучше всего запретить. В противном случае, к примеру, в компилируемом языке Golang придется работать с указателями и расчет объема предмета превращается из такого кода

```golang
type Item struct {
    Width  int
    Height int
    Length int
}

func Volume(item Item) int {
    return item.Width * item.Height * item.Length
}
```

в такой

```golang
type Item struct {
    Width  *int
    Height *int
    Length *int
}

func Volume(item Item) int {
    width := 0
    height := 0
    length := 0

    if item.Width != nil {
        width = item.Width*
    }
    if item.Height != nil {
        width = item.Height*
    }
    if item.Length != nil {
        length = item.Length
    }

    return width * height * length
}
```

В качестве контрпримера, когда значение `null` оправдано, можно привести объект с диапазоном значений. Предположим, что в системе есть объекты, которые описывают диапазоны с вещественными значениям "от" `from` и "до" `to`.

```json
{
    "from": 1.25,
    "to": 5.75
}
```

С точки зрения бизнес-логики есть правило, которое говорит о том, что диапазоны могут быть частичными, т.е. в объекте может отсутствовать одно из значений `from` или `to`. При этом значение `0` - это существующее значение, отличающееся по смыслу от значения _"не заполнено"_. То есть объект

```json
{
    "from": 0,
    "to": 5.75
}
```

эквивалентен по смыслу диапазону __"от 0 до 5,75"__, а объект

```json
{
    "from": null,
    "to": 5.75
}
```

эквивалентен по смыслу диапазону __"до 5,75"__. В этом случае использование `null` оправдано и важно с точки зрения бизнес-логики. Значения `0` и `null` несут разный смысл.

Еще один интересный пример - массивы. Если в случае чисел и строк большинство динамических языков могу приводить значения `null` к `0` или пустой строке `""` и часто это может сочетаться с логикой программы, то разрешение значения `null` у атрибута типа массив `array` однозначно приводит к появлению блоков кода такого вида.

```php
if ($items !== null) {
    foreach ($items as $item) {
        doStuff($item);
    }
}
```

## Null и объекты

null pointer exception - ошибка на миллион долларов