---
title: '{{ strings.Substr (replace .File.ContentBaseName "-" " ") 8 | title }}'
slug: '{{ strings.Substr .File.ContentBaseName 8 }}'
date: '{{ .Date }}'
categories: ["todo"]
tags: ["todo"]
image: "poster.jpg"
---
