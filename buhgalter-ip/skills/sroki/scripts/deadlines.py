#!/usr/bin/env python3
"""Сроки ИП на УСН «доходы»: перенос с выходного на следующий рабочий день (ст. 6.1 НК РФ).
Праздничные дни скрипт не знает: сверьте с производственным календарём на consultant.ru.
Запуск: python deadlines.py 2026-10-01 2027-04-30 [--employees]
Правила: авансы УСН 28.04, 28.07, 28.10; налог за год 28.04; декларация ИП за год 25.04;
фиксированные взносы 28.12; взнос 1% до 01.07; уведомление по авансу до 25 числа месяца уплаты (ЕНП)."""
import sys, datetime as dt

def shift(d):
    while d.weekday() >= 5:
        d += dt.timedelta(days=1)
    return d

def events(y0, y1, employees):
    out = []
    for y in range(y0, y1 + 1):
        out += [(dt.date(y, 4, 25), "Декларация УСН ИП за прошлый год"),
                (dt.date(y, 4, 28), "Налог УСН ИП за прошлый год (через ЕНП)"),
                (dt.date(y, 7, 1), "Взнос 1% с дохода свыше 300 000 за прошлый год"),
                (dt.date(y, 12, 28), "Фиксированные взносы ИП за этот год"),
                (dt.date(y, 4, 25), "Уведомление об авансе УСН за 1 квартал"),
                (dt.date(y, 7, 25), "Уведомление об авансе УСН за полугодие"),
                (dt.date(y, 10, 25), "Уведомление об авансе УСН за 9 месяцев"),
                (dt.date(y, 7, 28), "Аванс УСН за полугодие (через ЕНП)"),
                (dt.date(y, 10, 28), "Аванс УСН за 9 месяцев (через ЕНП)")]
        if employees:
            out += [(dt.date(y, m, 25), "Уведомление по НДФЛ и взносам за работников") for m in range(1, 13)]
            out += [(dt.date(y, m, 28), "Уплата по ЕНП (НДФЛ и взносы за работников)") for m in range(1, 13)]
            out += [(dt.date(y, 1, 25), "РСВ за прошлый год")]
    return sorted((shift(d), t) for d, t in out)

if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    s, e = dt.date.fromisoformat(a[0]), dt.date.fromisoformat(a[1])
    emp = "--employees" in sys.argv
    seen = set()
    for d, t in events(s.year, e.year, emp):
        if s <= d <= e and (d, t) not in seen:
            seen.add((d, t)); print(f"{d.strftime('%d.%m.%Y')} {['пн','вт','ср','чт','пт','сб','вс'][d.weekday()]} | {t}")
    print("Праздники не учтены: сверьте с производственным календарём.")
