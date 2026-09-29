#!/usr/bin/env python3
"""Аванс УСН «доходы» 6% для ИП нарастающим итогом (п. 3 ст. 346.21 НК РФ).

Вход (JSON в файле или stdin):
{"rate": 6, "quarters": [400000, 600000, 700000, 500000],
 "fixed_contrib": 57390, "one_percent": null, "employees": false}
one_percent: если null, считается автоматически (доход за год минус 300 000) * 1%, но не больше 321 818 (2026).
Вывод: таблица по периодам. Все суммы в рублях, округление до целых по правилам НК (округляем 0,5 и больше вверх).
Запуск: python usn_calc.py данные.json
Это справочный расчёт: перед уплатой сверьте с бухгалтером или личным кабинетом ФНС.
"""
import json, sys

FIXED_2026 = 57390
CAP_ONE_PCT_2026 = 321818
LABELS = ["1 квартал", "полугодие", "9 месяцев", "год"]

def rnd(x):
    return int(x + 0.5) if x >= 0 else -int(-x + 0.5)

def calc(d):
    rate = d.get("rate", 6) / 100.0
    q = d["quarters"]
    fixed = d.get("fixed_contrib", FIXED_2026)
    employees = bool(d.get("employees", False))
    total_year = sum(q)
    one = d.get("one_percent")
    if one is None:
        one = min(max(0, total_year - 300000) * 0.01, CAP_ONE_PCT_2026)
    limit_share = 0.5 if employees else 1.0
    rows, paid_prev, cum = [], 0, 0
    for i, inc in enumerate(q):
        cum += inc
        tax = cum * rate
        deduct = fixed + (one if i == 3 else 0)
        deduct_max = min(deduct, tax * limit_share)
        to_pay = max(0, rnd(tax - deduct_max) - paid_prev)
        rows.append({"period": LABELS[i], "income_cum": cum, "tax": rnd(tax), "deduct": rnd(deduct_max), "to_pay": to_pay})
        paid_prev += to_pay
    return rows, rnd(one), employees

if __name__ == "__main__":
    src = open(sys.argv[1], encoding="utf-8").read() if len(sys.argv) > 1 else sys.stdin.read()
    rows, one, emp = calc(json.loads(src))
    print("Период | Доход нарастающим | Налог | Вычет взносами | К уплате")
    for r in rows:
        print(f"{r['period']} | {r['income_cum']:,} | {r['tax']:,} | {r['deduct']:,} | {r['to_pay']:,}".replace(",", " "))
    print(f"Взнос 1% за год: {one:,}".replace(",", " ") + f"; работники: {'да, вычет до 50% налога' if emp else 'нет, вычет до 100%'}")
    print("Справочный расчёт. Перед уплатой сверьте с бухгалтером или личным кабинетом ФНС.")
