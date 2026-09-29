#!/usr/bin/env python3
# Прогон на ученическом ПК (приложение Claude, вкладка Code): каждая фраза в новом чате,
# какой навык запустился, берём из файла сессии. Запуск: python3 pc_trigger_test.py [номера через запятую]
import os, re, subprocess, sys, time
sys.argv, keep = sys.argv[:1], sys.argv[1:]
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "trigger_test.py")).read().split("def run")[0]
exec(src)
W = os.path.expanduser("~/.config/win-pc")
def mcp(*a): return subprocess.run(["python3", f"{W}/mcp_call.py", *a], capture_output=True, text=True).stdout
def chat(): return subprocess.run(["python3", f"{W}/win_chat.py", "100000"], capture_output=True, text=True).stdout
idx = [int(x) for x in keep[0].split(",")] if keep else range(1, len(CASES) + 1)
ok = 0
for i in idx:
    prompt, want = CASES[i - 1]
    mcp("Shortcut", '{"shortcut":"escape"}'); mcp("Shortcut", '{"shortcut":"ctrl+n"}'); time.sleep(3)
    mcp("Type", '{"loc":[1091,985],"text":' + __import__("json").dumps(prompt + " Ничего не отправляй и не создавай файлов.", ensure_ascii=False) + ',"press_enter":true}')
    got, t0 = [], time.time()
    while time.time() - t0 < 150:
        time.sleep(15)
        c = chat()
        if prompt[:30] not in c: continue
        got = re.findall(r"\[инструмент Skill: \{\"skill\": \"([^\"]+)\"", c)
        if got or "ASSISTANT:" in c.split(prompt[:30])[-1]: break
    hit = any(g.split(":")[-1] == want for g in got)
    ok += hit
    print(f"{i:2} {'OK  ' if hit else 'FAIL'} ждали {want}, запущено {got}", flush=True)
print(f"итог: {ok} из {len(idx)}")
