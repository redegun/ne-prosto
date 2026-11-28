#!/usr/bin/env python3
"""Вторая правка README аудита #5182 по замечанию верификатора: SEO-TECH-013 — «выполнен» на услугах и статьях,
наблюдение по старым кейсам — строкой KB вне счётчика; пересчёт 97 / 56 / 41."""
import sys

p = sys.argv[1]
t = open(p, encoding="utf-8").read()
pairs = [
    ("Применимых проверено 97: выполнено 55, нарушено 42.", "Применимых проверено 97: выполнено 56, нарушено 41."),
    ("LCP главной — WebP с fetchpriority=high и размерами, картинки ниже первого экрана ленивые.",
     "LCP главной — WebP с fetchpriority=high и размерами. Картинки ниже первого экрана ленивые на главной, 7 услугах и 29 статьях (SEO-TECH-013)."),
]
for a, b in pairs:
    assert a in t, "не найдено: " + a[:70]
    t = t.replace(a, b)

kb_anchor = "- KB: ошибка | content/qa |"
kb_new = ("- KB: гипотеза | seo/40_technical | SEO-TECH-013 (loading=lazy ниже первого экрана) применять и к кейсам портфолио: "
          "сейчас applies.page_type — только услуга и статья, а в старых кейсах самые длинные галереи | #5182: в 10 старых кейсах "
          "ne-prosto lazy нет ни у одной картинки — presentation-servisok 27 img, presentation-stdfast 20, presentation-slono 18, "
          "sajt-dlya-shkolyi-inostrannyix-yazyikov 15 (evidence/analysis.json); вне счётчика нарушений | images, lazy, portfolio, modx\n")
assert kb_anchor in t
t = t.replace(kb_anchor, kb_new + kb_anchor, 1)
open(p, "w", encoding="utf-8").write(t)
print("ok")
