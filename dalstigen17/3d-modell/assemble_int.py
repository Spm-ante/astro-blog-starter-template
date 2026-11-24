src = open("build55.py").read(); parts = {}; cur = None
for line in open("int_parts.py").read().split("\n"):
    if line.startswith("##== "): cur = line[5:].strip(); parts[cur] = []; continue
    if cur: parts[cur].append(line)
P = {k: "\n".join(v) + "\n" for k, v in parts.items()}
def cut(s, a, b=None):
    i = s.index(a); j = s.index(b) if b else len(s); return s[:i], s[i:j], s[j:]
head, rest = src.split("# ---------------- terrain ----------------", 1)
s = head + P["PRE"] + "# ---------------- terrain ----------------" + rest
for a, b in (("wall('x', 0, 8.9, (0, wt), -0.25, 2.2, 'oldpanel', [(5.26, 6.85, 0.0, 2.0)])", "owall('x', 0, 8.9, (0, wt), -0.25, 2.2, 'oldpanel', [(1.26, 2.14, 0.85, 2.0), (4.9, 7.6, 0.0, 2.05)])"),
             ("box((0, 8.9), (5.5 - wt, 5.5), (-0.25, 2.2), 'oldpanel'); box((0, wt), (wt, 5.5 - wt), (-0.25, 2.2), 'oldpanel')",
              "owall('x', 0, 8.9, (5.5 - wt, 5.5), -0.25, 2.2, 'oldpanel', [(2.04, 2.76, 1.2, 1.8), (4.14, 4.92, 0.0, 2.0), (6.69, 7.46, 1.05, 2.0)]); box((0, wt), (wt, 5.5 - wt), (-0.25, 2.2), 'oldpanel')"),
             ("box((8.9 - wt, 8.9), (wt, 5.5 - wt), (-0.25, 2.2), 'oldpanel')", "owall('y', wt, 5.5 - wt, (8.9 - wt, 8.9), -0.25, 2.2, 'oldpanel', [(1.61, 2.61, 0.85, 2.0), (2.72, 3.78, 0.85, 2.0)])")):
    assert s.count(a) == 1, a[:50]; s = s.replace(a, b)
pre, mid, post = cut(s, "# interior (seen in section)", "# ---------------- new house"); s = pre + P["KITCHEN"] + post
pre, mid, post = cut(s, "# ---------------- new house", "# ---------------- winter garden"); s = pre + P["NEWHOUSE"] + post
pre, mid, post = cut(s, "# ---------------- section cut"); s = pre + P["RENDER"]
open("interiors.py", "w").write(s); print("assembled", len(s))
