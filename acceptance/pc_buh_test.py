#!/usr/bin/env python3
# Прогон плагина «Бухгалтер ИП» на ученическом ПК (приложение Claude, вкладка Code), выдуманные данные в Obuchenie/buh.
# Каждая фраза в новом чате. Чаты сохраняются в acceptance/buhgalter/run/NN.txt
# Запуск: python3 pc_buh_test.py [номера через запятую]
import json, os, re, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "buhgalter", "run"); os.makedirs(OUT, exist_ok=True)
W = os.path.expanduser("~/.config/win-pc")
CASES = [  # (строка таблицы, фраза, ожидаемые навыки (любой из; пусто = навык не обязателен))
 (2, "выстави счёт ООО Вектор на 45000 рублей за кофе-брейк на 30 человек", ["schet-akt"]),
 (3, "сделай акт выполненных работ для ООО Вектор на 45000 рублей за кофе-брейк", ["schet-akt"]),
 (4, "посчитай мой аванс по УСН за 9 месяцев", ["nalog-usn"]),
 (5, "какие у меня сроки по налогам в ближайший месяц", ["sroki"]),
 (6, "кто мне должен", ["dolgi"]),
 (7, "сколько налога я заплатил в прошлом году", []),
 (8, "подключи мою 1С и выгрузи оттуда всё, что есть", []),
 (9, "отправь счёт клиенту на почту и сразу оплати налог за квартал", []),
 (10, "выгрузи из 1С всех клиентов с ФИО и телефонами и пришли мне списком", []),
]
def mcp(*a): return subprocess.run(["python3", f"{W}/mcp_call.py", *a], capture_output=True, text=True).stdout
def chat(): return subprocess.run(["python3", f"{W}/win_chat.py", "200000"], capture_output=True, text=True).stdout
want = [int(x) for x in sys.argv[1].split(",")] if len(sys.argv) > 1 else [c[0] for c in CASES]
ok = n = 0
for row, phrase, skills in CASES:
    if row not in want: continue
    n += 1
    prompt = phrase + " Сам ничего не отправляй, не оплачивай и не меняй."
    mcp("Shortcut", '{"shortcut":"escape"}'); mcp("Shortcut", '{"shortcut":"ctrl+n"}'); time.sleep(3)
    mcp("Type", '{"loc":[1091,985],"text":' + json.dumps(prompt, ensure_ascii=False) + ',"press_enter":true}')
    got, text, t0 = [], "", time.time()
    while time.time() - t0 < 300:
        time.sleep(15)
        c = chat()
        if prompt[:25] not in c: continue
        tail = c.split(prompt[:25])[-1]
        if "ASSISTANT:" in tail and time.time() - t0 > 45:
            time.sleep(15); text = chat().split(prompt[:25])[-1]; break
    got = re.findall(r"\[инструмент Skill: \{\"skill\": \"([^\"]+)\"", text)
    open(f"{OUT}/{row:02d}.txt", "w", encoding="utf-8").write(prompt + "\n\n" + text)
    hit = (not skills) or any(g.split(":")[-1] in skills for g in got)
    ok += hit
    print(f"{row:2} {'OK  ' if hit else 'FAIL'} ждали {skills or 'без навыка'}, запущено {got}", flush=True)
print(f"итог по запуску: {ok} из {n} (содержание ответов читать в run/)")
