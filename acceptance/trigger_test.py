#!/usr/bin/env python3
# Проверка: запускается ли нужный навык по русской фразе без имени навыка.
# Запуск: python3 trigger_test.py [рабочая папка]
import json, os, subprocess, sys, tempfile

PLUGIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "biznes-rf")
CASES = [
    ("с чего начать, у меня кейтеринг в Уфе, 5 человек", "smb-router"),
    ("сделай КП на фуршет 40 человек 10 октября, бюджет до 80 тысяч, меню стандарт 1800 рублей на гостя", "proposal-builder"),
    ("пришла заявка в ватсап: «Здравствуйте, нужен кофе-брейк на 20 человек в пятницу, сколько стоит? Павел»", "speed-to-lead"),
    ("кто мне должен? вот список: ООО Вектор 45000 срок был 01.09, ИП Сафин 12000 срок 20.09", "invoice-chase"),
    ("кому позвонить сегодня? клиенты: Ирина (банкет, ждёт цену), Руслан (свадьба, думает), Алсу (просила перезвонить)", "call-list"),
    ("хватит ли денег на 3 месяца? на счету 300 тысяч, в месяц приходит 900, уходит 950", "cash-flow-snapshot"),
    ("напиши пост для телеграм-канала про новое осеннее меню", "social-content-engine"),
    ("ответь на плохой отзыв с яндекс карт: «Привезли холодное, опоздали на час»", "review-reputation"),
    ("напиши вакансию повара в кейтеринг", "job-post-builder"),
    ("проверь договор: оплата в течение 90 дней после акта, штраф исполнителя 1% в день, подсудность Москва", "contract-review"),
]

def run(prompt, cwd):
    cmd = ["claude", "-p", prompt, "--plugin-dir", PLUGIN, "--output-format", "stream-json",
           "--verbose", "--max-turns", "3", "--model", "sonnet"]
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=600)
    skills = []
    for line in p.stdout.splitlines():
        try: j = json.loads(line)
        except Exception: continue
        m = j.get("message") or {}
        for b in m.get("content") or [] if isinstance(m.get("content"), list) else []:
            if b.get("type") == "tool_use" and b.get("name") == "Skill":
                skills.append(b.get("input", {}).get("skill") or b.get("input", {}).get("command"))
    return skills

cwd = sys.argv[1] if len(sys.argv) > 1 else tempfile.mkdtemp(prefix="brf-")
ok = 0
for i, (prompt, want) in enumerate(CASES, 1):
    got = run(prompt, cwd)
    hit = any(s and s.split(":")[-1] == want for s in got)
    ok += hit
    print(f"{i:2} {'OK  ' if hit else 'FAIL'} ждали {want}, запущено {got}", flush=True)
print(f"итог: {ok} из {len(CASES)}")
