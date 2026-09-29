#!/usr/bin/env python3
"""Проверка контрольных цифр: ИНН (10 и 12 знаков) и ОГРНИП (15 знаков).
Запуск: python check_id.py inn 7707083893   |   python check_id.py ogrnip 304500116000157
Код выхода 0 = контрольная цифра верна, 1 = неверна или неверная длина."""
import sys

def inn_ok(s):
    if not s.isdigit(): return False
    d = [int(c) for c in s]
    def ctrl(w, n):
        return sum(a * b for a, b in zip(w, d[:n])) % 11 % 10
    if len(d) == 10:
        return ctrl([2, 4, 10, 3, 5, 9, 4, 6, 8], 9) == d[9]
    if len(d) == 12:
        return ctrl([7, 2, 4, 10, 3, 5, 9, 4, 6, 8], 10) == d[10] and ctrl([3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8], 11) == d[11]
    return False

def ogrnip_ok(s):
    return s.isdigit() and len(s) == 15 and int(s[:14]) % 13 % 10 == int(s[14])

if __name__ == "__main__":
    kind, val = sys.argv[1], sys.argv[2].strip()
    ok = inn_ok(val) if kind == "inn" else ogrnip_ok(val)
    print(("верна" if ok else "НЕ верна") + f": {kind} {val}")
    sys.exit(0 if ok else 1)
