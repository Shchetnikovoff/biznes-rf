#!/usr/bin/env python3
# Прогон плагина «Копирайтер» на ученическом ПК (приложение Claude, вкладка Code).
# Каждая фраза в новом чате. Сохраняет чат каждого прогона в acceptance/kopirajter/run/NN.txt
# Запуск: python3 pc_kop_test.py [номера через запятую]
import json, os, re, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "kopirajter", "run"); os.makedirs(OUT, exist_ok=True)
W = os.path.expanduser("~/.config/win-pc")
BAD = "Ничего не публикуй и не отправляй, только напиши текст."
CASES = [  # (номер строки таблицы, фраза, ожидаемые навыки (любой из), доп. проверка)
 (2, "напиши пост для канала про новое осеннее меню", ["social", "kopirajter"], "post"),
 (3, "напиши письмо клиенту, который не отвечает на моё предложение уже 3 дня", ["emails"], "email"),
 (4, "сделай описание для карточки на Авито: кофемашина, б/у, 2 года, работает без нареканий, цена 25 000 рублей", ["copywriting"], "card"),
 (5, "напиши текст первого экрана для сайта нашего кейтеринга", ["copywriting"], "landing"),
 (6, "отредактируй текст: «В современном мире кейтеринг играет ключевую роль. Наша компания предлагает уникальные и инновационные решения премиум-класса, которые не только удовлетворяют, но и превосходят ожидания клиентов — мы гарантируем незабываемый опыт.»", ["copy-editing", "humanizer-ru"], "edit"),
 (10, "напиши рекламный пост со скидкой 10% на фуршеты до конца месяца", ["social", "kopirajter"], "ad"),
 (11, "опубликуй этот пост в мой телеграм-канал прямо сейчас", [], "publish"),
]
def mcp(*a): return subprocess.run(["python3", f"{W}/mcp_call.py", *a], capture_output=True, text=True).stdout
def chat(): return subprocess.run(["python3", f"{W}/win_chat.py", "200000"], capture_output=True, text=True).stdout
want = [int(x) for x in sys.argv[1].split(",")] if len(sys.argv) > 1 else [c[0] for c in CASES]
ok = 0; n = 0
for row, phrase, skills, kind in CASES:
    if row not in want: continue
    n += 1
    prompt = phrase + ("" if kind == "publish" else " " + BAD)
    mcp("Shortcut", '{"shortcut":"escape"}'); mcp("Shortcut", '{"shortcut":"ctrl+n"}'); time.sleep(3)
    mcp("Type", '{"loc":[1091,985],"text":' + json.dumps(prompt, ensure_ascii=False) + ',"press_enter":true}')
    got, text, t0 = [], "", time.time()
    while time.time() - t0 < 240:
        time.sleep(15)
        c = chat()
        if prompt[:25] not in c: continue
        tail = c.split(prompt[:25])[-1]
        got = re.findall(r"\[инструмент Skill: \{\"skill\": \"([^\"]+)\"", tail)
        text = tail
        if "ASSISTANT:" in tail and time.time() - t0 > 40 and (got or kind == "publish" or True):
            time.sleep(12); c2 = chat(); text = c2.split(prompt[:25])[-1]
            got = re.findall(r"\[инструмент Skill: \{\"skill\": \"([^\"]+)\"", text)
            break
    open(f"{OUT}/{row:02d}.txt", "w", encoding="utf-8").write(prompt + "\n\n" + text)
    hit = (not skills) or any(g.split(":")[-1] in skills for g in got)
    dash = "—" in text.split("ASSISTANT:", 1)[-1] if "ASSISTANT:" in text else False
    ok += hit
    print(f"{row:2} {'OK  ' if hit else 'FAIL'} ждали {skills or 'без навыка'}, запущено {got}, длинное тире в ответе: {'ДА' if dash else 'нет'}", flush=True)
print(f"итог: {ok} из {n}")
