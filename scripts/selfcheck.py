"""STEP 6 - self-check the generated kit."""
import json, re
kit = open("output/BOOKER_Prompt_Kit.md").read()
groups = json.load(open("output/groups.json"))
prompts = dict(re.findall(r"### (\w+) – .*?```text\n(.*?)```", kit, re.S))
ok = True
for g, eps in groups.items():
    if g == "X": continue
    txt = prompts.get(g, "")
    for ep in eps:
        m, p = ep.split(" ", 1)
        pat = re.escape(p).replace(r"/:id", r"/\{\{\w+\}\}") + r"(\s|\?|$)"
        hit = re.search(m + r" \{\{baseUrl\}\}" + pat, txt)
        print(f"{g:3} {ep:24} {'OK' if hit else 'MISSING'}"); ok &= bool(hit)
total = sum(len(v) for k, v in groups.items() if k != "N1")
print("group total:", total, "== 8:", total == 8)
print("triple backticks inside prompts:", any("```" in t for t in prompts.values()))
print("secret-like strings:", re.findall(r"(?i)bearer\s+[a-z0-9]{16,}|token=[a-f0-9]{10,}", kit))
print("ALL OK" if ok and total == 8 else "CHECK FAILED")
