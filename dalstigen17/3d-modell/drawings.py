# Architectural sketch drawings for Dalstigen 17, alternative 2 (5.5 m gap). Model coords: x along houses (east), y north, z up.
import math, sys
OUT = sys.argv[1]
T40, T32, T15 = (math.tan(math.radians(a)) for a in (40, 32, 15))
FONT = "Helvetica, Arial, sans-serif"
CUT, INK, MID, LIGHT = "#1b1b1b", "#2a2a2a", "#6f6f6f", "#b9b9b9"
GREEN, GLASS, OCHRE, BEIGE, TILE = "#1f3a2c", "#dbe7e8", "#cfa45e", "#e6dfd0", "#a9563c"
W = 5.5; M = -W / 2; GZ0 = 2.42; GZR = GZ0 + (W / 2) * T15; ZR_OLD = 2.55 + 2.75 * T40; ZR_NEW = 5.63 + 3.4 * T32

def esc(t): return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

class V:
    def __init__(s, el, ox, oy, S, ar, br, sg=1): s.el, s.ox, s.oy, s.S, s.ar, s.br, s.sg = el, ox, oy, S, ar, br, sg
    def P(s, a, b): return (s.ox + s.sg * (a - s.ar) * s.S, s.oy + (s.br - b) * s.S)
    def poly(s, pts, fill="none", stroke=INK, sw=0.8, dash=None, close=True):
        d = " ".join("%.1f,%.1f" % s.P(a, b) for a, b in pts)
        s.el.append('<%s points="%s" fill="%s" stroke="%s" stroke-width="%s"%s stroke-linejoin="round"/>' % (
            "polygon" if close else "polyline", d, fill, stroke, sw, ' stroke-dasharray="%s"' % dash if dash else ""))
    def rect(s, a0, a1, b0, b1, **k): s.poly([(a0, b0), (a1, b0), (a1, b1), (a0, b1)], **k)
    def line(s, a0, b0, a1, b1, stroke=INK, sw=0.8, dash=None): s.poly([(a0, b0), (a1, b1)], stroke=stroke, sw=sw, dash=dash, close=False)
    def circle(s, a, b, r, fill="none", stroke=INK, sw=0.6):
        x, y = s.P(a, b); s.el.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" stroke="%s" stroke-width="%s"/>' % (x, y, r * s.S, fill, stroke, sw))
    def arc(s, ca, cb, r, t0, t1, n=14, **k):
        s.poly([(ca + r * math.cos(math.radians(t0 + (t1 - t0) * i / n)), cb + r * math.sin(math.radians(t0 + (t1 - t0) * i / n))) for i in range(n + 1)], close=False, **k)
    def text(s, a, b, t, size=12, anchor="middle", weight="normal", fill=INK):
        x, y = s.P(a, b); T(s.el, x, y + size * 0.35, t, size, anchor, weight, fill)

def T(el, x, y, t, size=12, anchor="start", weight="normal", fill=INK, ls=0):
    el.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="%s" font-weight="%s" fill="%s" text-anchor="%s"%s>%s</text>' % (
        x, y, FONT, size, weight, fill, anchor, ' letter-spacing="%s"' % ls if ls else "", esc(t)))

# ---------- plan helpers ----------
def wall(v, axis, a0, a1, t0, t1, ops=()):
    def seg(u0, u1):
        if u1 - u0 > 1e-3: (v.rect(u0, u1, t0, t1, fill=CUT, stroke=CUT, sw=0.4) if axis == 'x' else v.rect(t0, t1, u0, u1, fill=CUT, stroke=CUT, sw=0.4))
    cur = a0
    for u0, u1, typ in sorted(ops):
        seg(cur, u0); cur = u1
        L = (lambda p, q, r, w: v.line(p, r, q, r, stroke=INK, sw=w)) if axis == 'x' else (lambda p, q, r, w: v.line(r, p, r, q, stroke=INK, sw=w))
        E = (lambda u: v.line(u, t0, u, t1, sw=0.6)) if axis == 'x' else (lambda u: v.line(t0, u, t1, u, sw=0.6))
        E(u0); E(u1)
        if typ in ('win', 'glass'):
            for f in ((0.38, 0.62) if typ == 'win' else (0.3, 0.5, 0.7)): L(u0, u1, t0 + (t1 - t0) * f, 0.6)
    seg(cur, a1)
def door(v, ha, hb, w, closed, opened):
    v.line(ha, hb, ha + w * math.cos(math.radians(opened)), hb + w * math.sin(math.radians(opened)), sw=0.9)
    v.arc(ha, hb, w, closed, opened, stroke=MID, sw=0.5, dash="3,2")
def lbl(v, a, b, name, area=None, size=13):
    v.text(a, b + (0.22 if area else 0), name, size, weight="bold")
    if area: v.text(a, b - 0.3, area, size - 2, fill=MID)
def bed(v, a0, a1, b0, b1, head='s'):
    v.rect(a0, a1, b0, b1, stroke=MID, sw=0.6)
    hb = (b0 + 0.08, b0 + 0.45) if head == 's' else (b1 - 0.45, b1 - 0.08)
    n = 2 if a1 - a0 > 1.2 else 1
    for i in range(n): v.rect(a0 + 0.1 + i * (a1 - a0 - 0.1) / n, a0 + (i + 1) * (a1 - a0 - 0.1) / n, hb[0], hb[1], stroke=MID, sw=0.5)
def chair(v, a, b, rot):
    v.rect(a - 0.21, a + 0.21, b - 0.21, b + 0.21, stroke=MID, sw=0.5)
    if rot == 'w': v.line(a - 0.21, b - 0.21, a - 0.21, b + 0.21, stroke=MID, sw=1.4)
    if rot == 'e': v.line(a + 0.21, b - 0.21, a + 0.21, b + 0.21, stroke=MID, sw=1.4)
    if rot == 'n': v.line(a - 0.21, b + 0.21, a + 0.21, b + 0.21, stroke=MID, sw=1.4)
    if rot == 's': v.line(a - 0.21, b - 0.21, a + 0.21, b - 0.21, stroke=MID, sw=1.4)
def plantc(v, a, b, r): v.circle(a, b, r, fill="#eef2e6", stroke="#8aa07a", sw=0.6); v.circle(a, b, r * 0.45, stroke="#b9764f", sw=0.6)
def dim(v, a0, b0, a1, b1, txt, off=0.0, size=11, vertical=False):
    v.line(a0, b0, a1, b1, stroke=INK, sw=0.6)
    for a, b in ((a0, b0), (a1, b1)):
        v.line(a - 0.12, b - 0.12, a + 0.12, b + 0.12, stroke=INK, sw=1.0)
        if vertical: v.line(a - 0.25, b, a + 0.25, b, stroke=INK, sw=0.5)
        else: v.line(a, b - 0.25, a, b + 0.25, stroke=INK, sw=0.5)
    x, y = v.P((a0 + a1) / 2, (b0 + b1) / 2)
    if vertical: v.el.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="%s" fill="%s" text-anchor="middle" transform="rotate(-90 %.1f %.1f)">%s</text>' % (x - 5, y, FONT, size, INK, x - 5, y, esc(txt)))
    else: T(v.el, x, y - 5, txt, size, "middle")
def scalebar(el, x, y, S, n=5, label="0       1       2       3       4       5 m"):
    for i in range(n): el.append('<rect x="%.1f" y="%.1f" width="%.1f" height="5" fill="%s" stroke="%s" stroke-width="0.6"/>' % (x + i * S, y, S, CUT if i % 2 == 0 else "#fff", CUT))
    for i in range(n + 1): T(el, x + i * S, y + 18, str(i) + (" m" if i == n else ""), 10, "middle")
def north(el, x, y, ang):  # ang: degrees from up, counterclockwise positive
    r = 26; c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    tip = (x - r * s, y - r * c); bl = (x + 0.45 * r * c - 0.6 * r * (-s) * 0 + r * 0.42 * s * -1 * 0, 0)
    pts = [(0, -r), (9, 12), (0, 6), (-9, 12)]
    rp = [(x + px * c + py * s * -1 * -1 * 1 if False else x + px * c - py * -s * 1, 0) for px, py in pts]
    rp = [(x + px * c + py * s, y - px * s + py * c) for px, py in pts]
    el.append('<polygon points="%s" fill="%s" stroke="%s" stroke-width="0.8"/>' % (" ".join("%.1f,%.1f" % p for p in rp), CUT, CUT))
    T(el, x - (r + 12) * s, y - (r + 12) * c + 5, "N", 13, "middle", "bold")
def title(el, x, y, t, sub):
    T(el, x, y, t, 15, "start", "bold", ls=1.2); T(el, x, y + 17, sub, 11, "start", "normal", MID)

# ---------- shared new-house geometry (alt 2, after shift) ----------
NX0, NX1, NYA, NYB = 0.3, 8.9, -12.3, -5.5
DXN = 0.5  # new house moved east relative to the existing house
def new_outer(v, floor):
    if floor == 0:
        wall(v, 'x', NX0, NX1, NYB - 0.3, NYB, [(1.3, 2.9, 'glass'), (5.5, 6.7, 'door')])
        wall(v, 'x', NX0, NX1, NYA, NYA + 0.3, [(1.8, 3.8, 'win'), (7.0, 7.6, 'win')])
        wall(v, 'y', NYA + 0.3, NYB - 0.3, NX0, NX0 + 0.3, [(-11.2, -10.0, 'win'), (-7.8, -6.6, 'win')])
        wall(v, 'y', NYA + 0.3, NYB - 0.3, NX1 - 0.3, NX1, [(-11.4, -10.5, 'win'), (-8.5, -7.5, 'win')])
    else:
        wall(v, 'x', NX0, NX1, NYB - 0.3, NYB, [(1.55, 2.65, 'win')])
        wall(v, 'x', NX0, NX1, NYA, NYA + 0.3, [])
        wall(v, 'y', NYA + 0.3, NYB - 0.3, NX0, NX0 + 0.3, [(-11.15, -10.05, 'win'), (-7.75, -6.65, 'win')])
        wall(v, 'y', NYA + 0.3, NYB - 0.3, NX1 - 0.3, NX1, [(-11.05, -10.4, 'win')])

def plan_ground(el, ox, oy, S):
    v = V(el, ox, oy, S, -2.6, 8.4)
    # courtyard terrace + beds
    v.rect(-1.6, 3.66, -5.48, -0.55, fill="#f1efea", stroke=MID, sw=0.6); v.rect(-2.0, -1.6, -5.1, -0.9, fill="#f1efea", stroke=MID, sw=0.6)
    for yy in [-5.48 + 0.47 * i for i in range(1, 11)]: v.line(-1.6, yy, 3.66, yy, stroke="#dcd8cf", sw=0.4)
    v.rect(-0.02, 3.66, -0.55, -0.03, fill="#e9efe0", stroke=MID, sw=0.5); v.rect(0.3 + DXN, 3.66, -5.48, -5.0, fill="#e9efe0", stroke=MID, sw=0.5)
    for a in (0.45, 1.25, 2.1, 2.9): v.circle(a, -0.3, 0.2, stroke="#8aa07a", sw=0.5)
    for a in (1.2, 2.0, 2.9): v.circle(a, -5.25, 0.25, stroke="#8aa07a", sw=0.5)
    v.circle(1.0, -2.55, 0.38, stroke=MID, sw=0.6); chair(v, 1.0, -3.2, 's'); chair(v, 1.0, -1.9, 'n')
    v.rect(2.4, 3.5, -4.95, -4.55, stroke=MID, sw=0.6); plantc(v, -1.0, -4.95, 0.45); plantc(v, -1.2, -0.95, 0.25); plantc(v, 3.25, -0.95, 0.25)
    lbl(v, 2.35, -3.85, "Gård / terrass", "ca 29 m²")
    # winter garden
    v.rect(3.74, 8.66, -5.46, -0.04, fill="#f7ebe2", stroke="none", sw=0)
    for a in [3.74 + 0.3 * i for i in range(1, 17)]: v.line(a, -5.46, a, -0.04, stroke="#ead2c2", sw=0.4)
    for b in [-5.46 + 0.3 * i for i in range(1, 18)]: v.line(3.74, b, 8.66, b, stroke="#ead2c2", sw=0.4)
    for xg in (3.66, 8.66):
        v.rect(xg, xg + 0.08, -5.5, 0.0, fill="#ffffff", stroke=GREEN, sw=0.6)
        v.line(xg + 0.04, -5.5, xg + 0.04, 0.0, stroke=GREEN, sw=0.5)
        for b in [-0.05 - (W - 0.1) * i / 5 for i in range(6)]: v.rect(xg - 0.01, xg + 0.09, b - 0.05, b + 0.05, fill=GREEN, stroke=GREEN, sw=0.3)
    v.rect(3.6, 3.8, -3.3, -2.2, fill="#ffffff", stroke="none", sw=0)
    door(v, 3.74, -3.3, 0.55, 90, 0); door(v, 3.74, -2.2, 0.55, -90, 0)
    v.rect(7.2, 8.1, M - 0.9, M + 0.9, fill="#fff", stroke=INK, sw=0.7)
    for cy in (M - 0.6, M, M + 0.6): chair(v, 6.97, cy, 'w'); chair(v, 8.33, cy, 'e')
    for a, b, r in ((4.25, -0.6, 0.35), (4.3, -4.9, 0.4), (8.3, -0.5, 0.3), (8.3, -5.0, 0.3), (4.3, M, 0.4), (5.1, -5.05, 0.18)): plantc(v, a, b, r)
    lbl(v, 6.0, -1.55, "Vinterträdgård", "matplats, ca 25 m²")
    v.line(6.05, -0.45, 6.05, -4.95, stroke=MID, sw=0.6, dash="5,3"); v.poly([(5.95, -4.75), (6.05, -4.95), (6.15, -4.75)], stroke=MID, sw=0.6, close=False)
    v.text(5.25, -3.9, "passage", 10, fill=MID); v.text(5.25, -4.2, "fri bredd >1,1 m", 10, fill=MID)
    # existing house
    wall(v, 'x', 0, 8.9, 0, 0.17, [(1.26, 2.14, 'win'), (5.26, 6.85, 'door')])
    wall(v, 'x', 0, 8.9, 5.33, 5.5, [(2.04, 2.76, 'win'), (4.14, 4.92, 'door'), (6.69, 7.46, 'win')])
    wall(v, 'y', 0.17, 5.33, 0, 0.17, []); wall(v, 'y', 0.17, 5.33, 8.73, 8.9, [(1.61, 2.61, 'win'), (2.72, 3.78, 'win')])
    wall(v, 'y', 0.17, 5.33, 2.88, 2.98, [(2.22, 3.0, 'door'), (4.5, 5.28, 'door')]); wall(v, 'x', 0.17, 2.88, 3.34, 3.44, [])
    wall(v, 'x', 5.75, 7.68, 3.23, 3.33, []); wall(v, 'y', 3.33, 5.33, 5.70, 5.80, [])
    door(v, 4.14, 5.33, 0.78, 0, -90); door(v, 5.26, 0.17, 0.79, 0, 90); door(v, 6.85, 0.17, 0.79, 180, 90)
    door(v, 2.88, 3.0, 0.78, -90, 180); door(v, 2.88, 5.28, 0.78, -90, 180)
    v.rect(5.8, 8.73, 4.73, 5.33, stroke=MID, sw=0.6); v.rect(5.8, 6.45, 3.33, 4.73, stroke=MID, sw=0.6)
    for a, b in ((6.0, 3.62), (6.27, 3.62), (6.0, 3.9), (6.27, 3.9)): v.circle(a, b, 0.09, stroke=MID, sw=0.5)
    v.rect(6.95, 7.6, 4.85, 5.2, stroke=MID, sw=0.5); v.rect(8.13, 8.73, 4.73, 5.33, stroke=MID, sw=0.6); v.text(8.43, 5.03, "K/F", 9, fill=MID)
    v.rect(7.85, 8.68, 0.55, 2.45, stroke=MID, sw=0.6); v.rect(6.6, 7.5, 1.0, 2.0, stroke=MID, sw=0.5)
    bed(v, 0.25, 1.2, 0.25, 2.25, 'n'); v.rect(0.2, 1.0, 4.5, 5.3, stroke=MID, sw=0.5); v.line(0.2, 4.5, 1.0, 5.3, stroke=MID, sw=0.4)
    v.rect(0.25, 0.85, 3.47, 4.05, stroke=MID, sw=0.5); v.circle(0.55, 3.76, 0.2, stroke=MID, sw=0.5)
    v.rect(2.2, 2.6, 3.5, 3.75, stroke=MID, sw=0.5); v.circle(2.4, 3.98, 0.2, stroke=MID, sw=0.5)
    for i in range(5): v.line(2.98, 3.4 + 0.19 * i, 3.6, 3.4 + 0.19 * i, stroke=MID, sw=0.5)
    v.rect(2.98, 3.6, 3.4, 4.35, stroke=MID, sw=0.6); v.text(3.3, 4.6, "loft", 9, fill=MID)
    lbl(v, 6.4, 1.75, "Allrum (bef.)"); lbl(v, 7.1, 4.05, "Kök (bef.)", size=11); lbl(v, 4.3, 4.0, "Hall", size=11)
    lbl(v, 1.55, 1.45, "Sovrum (bef.)", size=11); lbl(v, 1.55, 4.45, "Bad", size=11)
    v.rect(3.09, 5.91, 5.5, 6.83, stroke=INK, sw=0.7); v.rect(4.03, 5.14, 6.83, 7.55, stroke=INK, sw=0.6)
    for i in range(1, 4): v.line(4.03, 6.83 + 0.18 * i, 5.14, 6.83 + 0.18 * i, stroke=INK, sw=0.5)
    v.text(4.5, 6.2, "veranda", 10, fill=MID)
    # new house
    ve = v; v = V(el, ox, oy, S, -2.6 - DXN, 8.4)
    new_outer(v, 0)
    wall(v, 'x', 5.45, 8.6, -9.75, -9.65, [(6.6, 7.4, 'door')]); wall(v, 'y', -12.0, -9.75, 5.45, 5.55, [])
    door(v, 1.3, -5.8, 0.8, 0, -90); door(v, 2.9, -5.8, 0.8, 180, -90); door(v, 5.5, -5.8, 0.6, 0, -90); door(v, 6.7, -5.8, 0.6, 180, -90)
    door(v, 6.6, -9.75, 0.8, 0, -90)
    for i in range(5): v.line(6.7 + 0.25 * i, -6.7, 6.7 + 0.25 * i, -5.8, sw=0.6)
    v.rect(6.7, 8.6, -6.7, -5.8, stroke=INK, sw=0.7); v.rect(7.7, 8.6, -9.2, -6.7, stroke=INK, sw=0.7)
    for j in range(1, 6): v.line(7.7, -6.7 - 0.25 * j, 8.6, -6.7 - 0.25 * j, sw=0.6)
    v.line(7.7, -8.25, 8.6, -7.85, sw=0.9); v.line(6.8, -6.25, 8.15, -6.25, stroke=MID, sw=0.6); v.line(8.15, -6.25, 8.15, -7.95, stroke=MID, sw=0.6)
    v.poly([(8.05, -7.75), (8.15, -7.95), (8.25, -7.75)], stroke=MID, sw=0.6, close=False); v.text(7.2, -6.0, "upp", 9, fill=MID)
    v.rect(1.0, 3.4, -11.95, -11.05, stroke=MID, sw=0.6); v.line(1.0, -11.75, 3.4, -11.75, stroke=MID, sw=0.5)
    v.rect(1.7, 2.7, -10.55, -9.95, stroke=MID, sw=0.5); chair(v, 1.05, -9.3, 'w'); chair(v, 3.35, -9.3, 'e')
    v.rect(0.9, 3.5, -11.0, -8.6, stroke=LIGHT, sw=0.5, dash="2,2")
    v.rect(7.95, 8.55, -11.95, -11.35, stroke=MID, sw=0.5); v.circle(8.25, -11.65, 0.2, stroke=MID, sw=0.5)
    v.rect(7.95, 8.55, -11.3, -10.7, stroke=MID, sw=0.5); v.circle(8.25, -11.0, 0.2, stroke=MID, sw=0.5); v.circle(6.0, -11.5, 0.3, stroke=MID, sw=0.5)
    lbl(v, 3.0, -7.6, "Vardagsrum", "ca 30 m²"); lbl(v, 6.25, -8.55, "Hall", size=12); lbl(v, 6.9, -10.65, "Tvätt / teknik", "ca 7 m²", size=11)
    # dims and section marker
    vn = v; v = ve
    dim(vn, NX0, -13.1, NX1, -13.1, "8,6"); dim(v, 10.05, NYA, 10.05, NYB, "6,8", vertical=True)
    dim(v, 10.05, NYB, 10.05, 0, "5,5", vertical=True); dim(v, 10.05, 0, 10.05, 5.5, "5,5", vertical=True); dim(v, 0, 8.1, 8.9, 8.1, "8,9")
    for b0, b1 in ((7.75, 6.9), (-12.6, -13.5)): v.line(6.3, b0, 6.3, b1, stroke=CUT, sw=1.6)
    for b in (7.75, -13.5):
        v.poly([(6.3, b), (6.8, b), (6.65, b + 0.12), (6.8, b), (6.65, b - 0.12)], stroke=CUT, sw=1.2, close=False); v.text(5.95, b, "A", 13, weight="bold")
    return v

def plan_upper(el, ox, oy, S):
    v = V(el, ox, oy, S, -2.6, 8.4)
    # existing: roof outline, loft
    v.poly([(-0.55, -0.6), (3.7, -0.6), (3.7, -0.02), (9.45, -0.02), (9.45, 6.1), (-0.55, 6.1)], stroke=MID, sw=0.6, dash="6,3")
    v.line(-0.55, 2.75, 9.45, 2.75, stroke=LIGHT, sw=0.5, dash="6,3")
    wall(v, 'y', 0, 5.5, 0, 0.17, [(2.25, 3.25, 'win')]); wall(v, 'y', 0, 5.5, 8.73, 8.9, [(2.25, 3.25, 'win')])
    v.line(0.17, 1.1, 8.73, 1.1, sw=0.7); v.line(0.17, 4.35, 8.73, 4.35, sw=0.7)
    v.rect(2.98, 3.6, 3.4, 4.35, stroke=MID, sw=0.6); v.line(2.98, 3.4, 3.6, 4.35, stroke=MID, sw=0.5)
    lbl(v, 5.4, 2.85, "Sovloft (bef.)", "ca 1,9 m i nock", size=12)
    # winter garden glass roof
    v.rect(3.66, 8.74, -5.5, 0.0, fill="#eef4f4", stroke=GREEN, sw=0.7)
    for a in [3.7 + 5.0 * i / 6 for i in range(7)]: v.line(a, -5.5, a, 0.0, stroke=GREEN, sw=0.6)
    v.line(3.66, M, 8.74, M, stroke=GREEN, sw=1.0); v.rect(7.1, 7.8, M + 0.1, M + 0.85, stroke=GREEN, sw=0.6, dash="3,2")
    v.text(6.2, -1.35, "Glastak ca 15°", 11, fill=GREEN); v.text(6.2, -3.95, "screen / taklucka vid nock", 10, fill=MID)
    v.rect(-1.6, 3.66, -5.48, -0.55, stroke=LIGHT, sw=0.5, dash="3,3")
    # new house upper
    ve = v; v = V(el, ox, oy, S, -2.6 - DXN, 8.4)
    new_outer(v, 1)
    wall(v, 'y', -12.0, -5.8, 5.35, 5.45, [(-10.2, -9.4, 'door'), (-8.5, -7.7, 'door')]); wall(v, 'x', 0.6, 5.35, -8.95, -8.85, [])
    wall(v, 'x', 5.45, 8.6, -10.45, -10.35, [(6.9, 7.6, 'door')]); wall(v, 'x', 5.45, 6.75, -7.15, -7.05, [(5.65, 6.45, 'door')])
    wall(v, 'y', -7.05, -5.8, 6.65, 6.75, [])
    door(v, 5.35, -10.2, 0.8, 90, 180); door(v, 5.35, -8.5, 0.8, 90, 180); door(v, 6.9, -10.45, 0.7, 0, -90); door(v, 5.65, -7.05, 0.8, 0, 90)
    v.poly([(6.75, -5.8), (6.75, -6.7), (7.7, -6.7), (7.7, -9.2), (8.6, -9.2), (8.6, -5.8)], stroke=INK, sw=0.6, dash="4,3")
    for j in range(6, 11): v.line(7.7, -6.7 - 0.25 * j + 0.0, 8.6, -6.7 - 0.25 * j, stroke=LIGHT, sw=0.5)
    v.line(7.7, -9.2, 7.7, -6.7, sw=1.4); v.line(6.75, -6.7, 7.7, -6.7, sw=1.4)
    v.line(8.15, -9.0, 8.15, -7.3, stroke=MID, sw=0.6); v.poly([(8.05, -7.5), (8.15, -7.3), (8.25, -7.5)], stroke=MID, sw=0.6, close=False); v.text(8.15, -9.45, "ned", 9, fill=MID)
    v.text(7.7, -6.25, "trapphål", 9, fill=MID)
    bed(v, 2.4, 4.0, -12.0, -10.0, 's'); v.rect(4.75, 5.35, -12.0, -10.4, stroke=MID, sw=0.5); v.line(4.75, -12.0, 5.35, -10.4, stroke=MID, sw=0.4)
    bed(v, 2.4, 4.0, -8.85, -6.85, 'n'); v.rect(4.75, 5.35, -7.4, -5.8, stroke=MID, sw=0.5); v.line(4.75, -7.4, 5.35, -5.8, stroke=MID, sw=0.4)
    v.rect(5.45, 6.4, -12.0, -11.05, stroke=MID, sw=0.5); v.line(5.45, -12.0, 6.4, -11.05, stroke=MID, sw=0.4); v.line(5.45, -11.05, 6.4, -12.0, stroke=MID, sw=0.4)
    v.rect(8.0, 8.55, -11.95, -11.6, stroke=MID, sw=0.5); v.circle(8.2, -11.35, 0.2, stroke=MID, sw=0.5); v.rect(7.7, 8.55, -10.95, -10.5, stroke=MID, sw=0.5)
    for a, b in ((6.15, -6.2), (6.15, -6.6)): v.line(5.5, b, 6.6, b, stroke=LIGHT, sw=0.5)
    lbl(v, 1.5, -10.25, "Sovrum 1", "ca 14,5 m²", size=12); lbl(v, 1.5, -7.55, "Sovrum 2", "ca 14,5 m²", size=12)
    lbl(v, 7.25, -11.3, "Dusch", "ca 5 m²", size=11); lbl(v, 6.1, -8.7, "Hall", size=11); lbl(v, 6.1, -6.35, "Förråd", size=10)
    v = ve
    for b0, b1 in ((7.75, 6.9), (-12.6, -13.5)): v.line(6.3, b0, 6.3, b1, stroke=CUT, sw=1.6)
    for b in (7.75, -13.5):
        v.poly([(6.3, b), (6.8, b), (6.65, b + 0.12), (6.8, b), (6.65, b - 0.12)], stroke=CUT, sw=1.2, close=False); v.text(5.95, b, "A", 13, weight="bold")
    return v

def site_plan(el, ox, oy, s):
    S = s / 13.7  # map px -> sheet px
    def mp(px, py): return (ox + (px - 560) * S, oy + (py - 380) * S)
    def mo(x, y):  # model -> map px
        return (875 + 13.7 * (x * 0.870 + y * 0.492), 950 + 13.7 * (x * 0.492 - y * 0.870))
    def pg(pts, fill, stroke, sw, dash=None):
        el.append('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%s"%s/>' % (" ".join("%.1f,%.1f" % mp(*p) for p in pts), fill, stroke, sw, ' stroke-dasharray="%s"' % dash if dash else ""))
    def road(pts, w=4.5):
        el.append('<polyline points="%s" fill="none" stroke="#e4e2dc" stroke-width="%.1f" stroke-linejoin="round"/>' % (" ".join("%.1f,%.1f" % mp(*p) for p in pts), w * s))
    road([(600, 345), (830, 390), (1050, 460), (1180, 490), (1300, 492)]); road([(560, 1735), (720, 1665), (1000, 1600), (1240, 1570), (1300, 1572)])
    T(el, *mp(760, 440), "Dalstigen", 11, "middle", fill=MID); T(el, *mp(760, 1675), "Backstigen", 11, "middle", fill=MID)
    plot = [(617, 533), (1160, 551), (1221, 638), (1097, 1505), (846, 1595)]
    pg(plot, "#f6f5f0", INK, 1.0, "8,3,2,3")
    for sh in ([(1022, 748), (1064, 756), (1058, 792), (1018, 784)], [(684, 822), (752, 812), (756, 852), (690, 862)], [(703, 885), (731, 879), (752, 960), (723, 966)]):
        pg(sh, "#ffffff", MID, 0.6)
    pg([(870, 600), (1080, 615), (1075, 690), (865, 675)], "#ecebe6", LIGHT, 0.5); T(el, *mp(970, 655), "P", 11, "middle", "bold", MID)
    pg([mo(*p) for p in ((-1.6, -5.48), (3.66, -5.48), (3.66, -0.55), (-1.6, -0.55))], "#f1efea", MID, 0.5)
    pg([mo(*p) for p in ((0, 0), (8.9, 0), (8.9, 5.5), (0, 5.5))], BEIGE, CUT, 1.0)
    pg([mo(*p) for p in ((3.7, -5.5), (8.7, -5.5), (8.7, 0), (3.7, 0))], GLASS, GREEN, 0.8)
    pg([mo(*p) for p in ((0.3 + DXN, -12.3), (8.9 + DXN, -12.3), (8.9 + DXN, -5.5), (0.3 + DXN, -5.5))], OCHRE, CUT, 1.0)
    # distance new house -> west boundary
    A, E = plot[0], plot[4]; dx, dy = E[0] - A[0], E[1] - A[1]; L = math.hypot(dx, dy); nx, ny = dy / L, -dx / L
    best = min(((abs((mo(*c)[0] - A[0]) * nx + (mo(*c)[1] - A[1]) * ny) / 13.7, c) for c in ((0.3 + DXN, -12.3), (0.3 + DXN, -5.5), (0, 0), (0, 5.5))))
    c = mo(*best[1]); f = ((c[0] - A[0]) * dx + (c[1] - A[1]) * dy) / L ** 2; foot = (A[0] + f * dx, A[1] + f * dy)
    el.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="0.8"/>' % (*mp(*c), *mp(*foot), INK))
    mx, my = mp((c[0] + foot[0]) / 2, (c[1] + foot[1]) / 2); T(el, mx - 4, my + 16, "ca %.1f m" % best[0], 10, "end", fill=INK)
    print("west boundary distance %.2f m at corner %s" % best)
    T(el, *mp(1050, 1150), "Överby 6:21", 11, "middle", "bold", MID); T(el, *mp(1050, 1185), "2 326 m²", 10, "middle", fill=MID)
    north(el, ox + 330, oy + 40, 0)
    return S

def sheet_frame(el, W_, H_, sheet_title, blad, extra):
    el.append('<rect x="0" y="0" width="%d" height="%d" fill="#ffffff"/>' % (W_, H_))
    el.append('<rect x="14" y="14" width="%d" height="%d" fill="none" stroke="%s" stroke-width="1.2"/>' % (W_ - 28, H_ - 28, CUT))
    x, y, w, h = W_ - 474, H_ - 214, 460, 200
    el.append('<rect x="%d" y="%d" width="%d" height="%d" fill="#ffffff" stroke="%s" stroke-width="1.2"/>' % (x, y, w, h, CUT))
    for yy in (y + 52, y + 104, y + 156): el.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="0.6"/>' % (x, yy, x + w, yy, MID))
    el.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="0.6"/>' % (x + 300, y + 104, x + 300, y + h, MID))
    T(el, x + 14, y + 22, "DALSTIGEN 17, RESARÖ – TILLBYGGNAD", 15, "start", "bold", ls=0.6); T(el, x + 14, y + 42, "Fastighet Överby 6:21, Vaxholms kommun", 11, fill=MID)
    T(el, x + 14, y + 74, sheet_title, 14, "start", "bold"); T(el, x + 14, y + 93, "Alternativ 2 – 5,5 m mellan husen, nya huset 0,5 m österut", 11, fill=MID)
    T(el, x + 14, y + 126, "SKISSFÖRSLAG – EJ BYGGLOVSHANDLING", 11, "start", "bold", "#8a3b1e"); T(el, x + 14, y + 144, "Alla mått är skissmått i meter", 10, fill=MID)
    T(el, x + 314, y + 126, "Datum 2026-11-24", 10); T(el, x + 314, y + 144, "Blad " + blad, 10)
    T(el, x + 14, y + 178, extra, 10, fill=MID); T(el, x + 314, y + 178, "Skala enl. skalstock", 10, fill=MID)

def svg(el, W_, H_): return '<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">\n%s\n</svg>\n' % (W_, H_, W_, H_, "\n".join(el))

# ================= SHEET 1: plans =================
el = []; SW, SH = 1600, 1131; S = 42
sheet_frame(el, SW, SH, "Planer och situationsplan", "1 / 2", "Ritningen bygger på 3D-modellen och mäklarens planritning")
plan_ground(el, 40, 44, S); title(el, 48, 1000, "ENTRÉPLAN", "Befintligt hus, vinterträdgård, gård och ny huskropp")
scalebar(el, 48, 1040, S)
plan_upper(el, 590, 44, S); title(el, 598, 1000, "ÖVERVÅNING", "Ny huskropp plan 2 och befintligt sovloft")
scalebar(el, 598, 1040, S)
north(el, 540, 80, 29.5); north(el, 1090, 80, 29.5)
s_site = 5.6
site_plan(el, 1150, 50, s_site); title(el, 1150, 700, "SITUATIONSPLAN", "Ungefärlig, ur Lantmäteriets karta")
scalebar(el, 1150, 740, s_site * 5, 4); el.append('<text x="1150" y="790" font-family="%s" font-size="10" fill="%s">skalstock 0–20 m (steg 5 m)</text>' % (FONT, MID))
ax, ay = 1150, 810
for i, (k, val) in enumerate((("Boarea (skiss)", ""), ("Befintligt hus", "ca 44 m²"), ("Ny huskropp, 2 × 49,6", "ca 99 m²"), ("Vinterträdgård", "ca 25 m²"), ("Summa", "ca 168 m²"), ("Byggnadsarea", "ca 139 av 160 m²"))):
    T(el, ax, ay + i * 17, k, 11, "start", "bold" if i in (0, 4, 5) else "normal"); T(el, ax + 300, ay + i * 17, val, 11, "end", "bold" if i in (4, 5) else "normal")
open(OUT + "/ritning-planer.svg", "w").write(svg(el, SW, SH))

# ================= SHEET 2: section + elevation =================
def Hf(x, y):
    sm = lambda v_, a, b: (lambda f: f * f * (3 - 2 * f))(min(max((v_ - a) / (b - a), 0), 1))
    h = -0.45 - 3.0 * sm(y, 7, 22) + 1.6 * sm(-y, 13, 40) - 0.8 * sm(-x, 4, 30)
    pad = (0.25 < x < 8.95 and -12.35 < y < 0) or (0 < x < 8.9 and 0 <= y < 5.5)
    return min(h, -0.64) if pad else h
def ground(v, x, fill="#efebe3"):
    ys = [8.6 - 0.25 * i for i in range(93)]; pts = [(y, Hf(x, y)) for y in ys]
    v.poly(pts + [(ys[-1], -1.7), (ys[0], -1.7)], fill=fill, stroke="none", sw=0); v.poly(pts, stroke=CUT, sw=1.6, close=False)
def level(v, a, b, txt, side='r'):
    v.poly([(a, b), (a + 0.15, b + 0.22), (a - 0.15, b + 0.22)], fill=CUT, stroke=CUT, sw=0.5); v.line(a - 0.5, b, a + 0.5, b, sw=0.6)
    x, y = v.P(a + (0.3 if side == 'r' else -0.3), b + 0.28); T(v.el, x, y, txt, 10, "start" if side == 'r' else "end")
def roofcut(v, ya, yb, zw, tan, t, oa, ob, fill=CUT):
    yc = (ya + yb) / 2; zr = zw + (yc - ya) * tan; tv = t * math.sqrt(1 + tan * tan)
    top = [(yb + ob, zw - ob * tan), (yc, zr), (ya - oa, zw - oa * tan)]
    v.poly(top + [(p[0], p[1] - tv) for p in top[::-1]], fill=fill, stroke=CUT, sw=0.6)
    return zr, tv

el = []; S = 40
sheet_frame(el, SW, SH, "Sektion A–A och fasad mot väster", "2 / 2", "Sektionen går genom altandörrarnas läge, sett mot öster")
# ---- section ----
v = V(el, 50, 60, S, 8.6, 8.6, sg=-1)
ground(v, 6.0)
# existing house (cut x=6)
for py in (0.25, 2.75, 5.25): v.rect(py - 0.15, py + 0.15, -0.68, -0.25, fill="#ffffff", stroke=MID, sw=0.6)
v.rect(0.17, 5.33, -0.25, 0.0, fill="#cfc9bd", stroke=CUT, sw=0.6)
v.rect(0.0, 0.17, 2.0, 2.2, fill=CUT, stroke=CUT, sw=0.4); v.line(0.0, 0.0, 0.0, 2.0, sw=0.6); v.line(0.17, 0.0, 0.17, 2.0, sw=0.6)
v.rect(5.33, 5.5, -0.25, 2.2, fill=CUT, stroke=CUT, sw=0.4); v.rect(3.23, 3.33, 0.0, 2.3, fill=CUT, stroke=CUT, sw=0.4)
v.rect(0.17, 5.33, 2.3, 2.55, fill=CUT, stroke=CUT, sw=0.4)
roofcut(v, 0.0, 5.5, 2.55, T40, 0.25, 0.02, 0.6)
v.rect(1.08, 1.12, 2.55, 3.12, fill=CUT, stroke=CUT, sw=0.3); v.rect(4.33, 4.37, 2.55, 3.15, fill=CUT, stroke=CUT, sw=0.3)
v.rect(1.61, 2.61, 0.85, 2.0, stroke=LIGHT, sw=0.6); v.rect(2.72, 3.78, 0.85, 2.0, stroke=LIGHT, sw=0.6)
v.rect(4.73, 5.33, 0.0, 0.9, stroke=LIGHT, sw=0.6); v.rect(4.98, 5.33, 1.45, 2.15, stroke=LIGHT, sw=0.6); v.rect(0.55, 2.45, 0.0, 0.85, stroke=LIGHT, sw=0.6)
lbl(v, 1.9, 1.35, "Allrum (bef.)", size=12); lbl(v, 4.3, 1.35, "Kök", size=11); lbl(v, 2.75, 3.25, "Sovloft", size=11)
# winter garden
for z0, z1, f in ((-0.02, 0.0, "#c0704c"), (-0.12, -0.02, "#bdbab3"), (-0.42, -0.12, "#f3e6b8"), (-0.64, -0.42, "#d9d5cc")): v.rect(-5.45, -0.05, z0, z1, fill=f, stroke=CUT, sw=0.5)
for yp in [-0.05 - (W - 0.1) * i / 5 for i in range(6)]:
    zt = GZ0 + (W / 2 - abs(yp - M)) * T15; v.rect(yp - 0.035, yp + 0.035, 0.05, zt, fill="#ffffff", stroke=GREEN, sw=0.6)
v.poly([(-0.05, 0.05), (-5.45, 0.05), (-5.45, GZ0), (M, GZR), (-0.05, GZ0)], fill=GLASS, stroke="none", sw=0)
v.rect(-5.45, -0.05, 2.12, 2.19, fill=GREEN, stroke=GREEN, sw=0.3)
v.poly([(0, GZ0 - 0.13), (0, GZ0), (M, GZR), (-W, GZ0), (-W, GZ0 - 0.13), (M, GZR - 0.13)], fill=GREEN, stroke=GREEN, sw=0.4)
v.poly([(0, GZ0 + 0.03), (M, GZR + 0.03), (-W, GZ0 + 0.03)], stroke=CUT, sw=1.4, close=False)
v.rect(M - 0.06, M + 0.06, GZR - 0.16, GZR + 0.02, fill=CUT, stroke=CUT, sw=0.3); v.rect(M - 0.13, M + 0.13, GZR + 0.03, GZR + 0.11, fill=GREEN, stroke=CUT, sw=0.4)
for ya, yb in ((-0.17, 0.0), (-W, -W + 0.17)): v.poly([(ya, 2.44), (ya, 2.29), (yb, 2.29), (yb, 2.44)], stroke=CUT, sw=1.0, close=False)
v.rect(M - 0.9, M + 0.9, 0.71, 0.75, fill="#ffffff", stroke=INK, sw=0.7)
for ty in (M - 0.84, M + 0.84): v.rect(ty - 0.03, ty + 0.03, 0.0, 0.71, fill="#ffffff", stroke=INK, sw=0.5)
for cy in (M - 0.6, M, M + 0.6): v.rect(cy - 0.21, cy + 0.21, 0.42, 0.46, stroke=MID, sw=0.5); v.rect(cy - 0.21, cy + 0.21, 0.46, 0.88, stroke=LIGHT, sw=0.4)
v.line(M, 2.0, M, GZR - 0.16, sw=0.5); v.poly([(M - 0.22, 1.78), (M + 0.22, 1.78), (M + 0.05, 2.02), (M - 0.05, 2.02)], fill="#fff4dc", stroke=INK, sw=0.5)
for py, r, h in ((-0.5, 0.3, 1.5), (-5.0, 0.35, 1.3)): v.rect(py - 0.22, py + 0.22, 0.0, 0.36, fill="#e2b496", stroke=MID, sw=0.5); v.circle(py, 0.36 + h * 0.6, r + 0.15, fill="#e8eedf", stroke="#8aa07a", sw=0.5)
lbl(v, M, 1.25, "Vinterträdgård", size=12)
# new house (cut x=6)
for z0, z1, f in ((-0.015, 0.0, "#c99a62"), (-0.12, -0.015, "#bdbab3"), (-0.42, -0.12, "#f3e6b8"), (-0.64, -0.42, "#d9d5cc")): v.rect(-12.0, -5.8, z0, z1, fill=f, stroke=CUT, sw=0.5)
v.rect(-5.8, -5.5, -0.64, -0.02, fill="#bdbab3", stroke=CUT, sw=0.5); v.rect(-12.3, -12.0, -0.64, -0.02, fill="#bdbab3", stroke=CUT, sw=0.5)
v.rect(-5.8, -5.5, 2.1, 5.25, fill=CUT, stroke=CUT, sw=0.4); v.line(-5.8, 0.0, -5.8, 2.1, sw=0.6); v.line(-5.5, 0.0, -5.5, 2.1, sw=0.6)
v.rect(-12.3, -12.0, -0.02, 5.25, fill=CUT, stroke=CUT, sw=0.4)
v.rect(-12.0, -5.8, 2.5, 2.88, fill=CUT, stroke=CUT, sw=0.4)
v.rect(-12.0, -5.8, 5.28, 5.33, fill=CUT, stroke=CUT, sw=0.3); v.rect(-12.0, -5.8, 5.33, 5.7, fill="#f3e6b8", stroke=CUT, sw=0.5)
v.rect(-9.75, -9.65, 0.0, 2.5, fill=CUT, stroke=CUT, sw=0.3); v.rect(-10.45, -10.35, 2.88, 5.28, fill=CUT, stroke=CUT, sw=0.3)
v.rect(-7.15, -7.05, 4.93, 5.28, fill=CUT, stroke=CUT, sw=0.3); v.line(-7.15, 2.88, -7.15, 4.93, sw=0.5); v.line(-7.05, 2.88, -7.05, 4.93, sw=0.5)
zr, tv = roofcut(v, -12.3, -5.5, 5.63, T32, 0.30, 0.45, 0.45)
for a, b in (((-12.0, 5.7), (-8.9, 7.38)), ((-5.8, 5.7), (-8.9, 7.38)), ((-8.9, 5.7), (-8.9, 7.38)), ((-10.45, 5.7), (-8.9, 7.38 - 1.0)), ((-7.35, 5.7), (-8.9, 7.38 - 1.0))): v.line(a[0], a[1], b[0], b[1], stroke=LIGHT, sw=0.6)
v.rect(-6.7, -5.8, 0.0, 0.9, fill="#ffffff", stroke=INK, sw=0.6)
for k in range(1, 5): v.line(-6.7, 0.18 * k, -5.8, 0.18 * k, stroke=LIGHT, sw=0.5)
prof = [(-6.7, 0.9)]
for j in range(1, 11): prof += [(-6.7 - 0.25 * (j - 1), 0.9 + 0.198 * j), (-6.7 - 0.25 * j, 0.9 + 0.198 * j)]
v.poly(prof + [(-9.2, 2.5), (-6.9, 0.7)], fill="#ffffff", stroke=INK, sw=0.7)
v.line(-6.55, 1.8, -9.2, 3.78, stroke=MID, sw=0.6); v.line(-9.2, 2.88 + 0.9, -9.2, 2.88, stroke=MID, sw=0.6)
v.rect(-8.5, -7.5, 1.6, 3.5, stroke=LIGHT, sw=0.6); v.rect(-11.4, -10.5, 1.1, 2.1, stroke=LIGHT, sw=0.6); v.rect(-11.05, -10.4, 3.95, 4.75, stroke=LIGHT, sw=0.6)
lbl(v, -10.85, 1.35, "Tvätt / teknik", size=11); lbl(v, -7.9, 0.45, "Hall", size=11); lbl(v, -8.6, 4.35, "Övre hall", size=11)
lbl(v, -11.2, 4.45, "Dusch", size=11); lbl(v, -6.35, 4.35, "Förråd", size=10); lbl(v, -8.9, 6.15, "Kallvind", size=10)
# levels + dims
level(v, -13.2, 0.0, "±0,00 färdigt golv"); level(v, -13.2, 2.88, "+2,88 golv plan 2"); level(v, -13.2, ZR_NEW, "+%.2f nock" % ZR_NEW)
level(v, -13.2, 5.28, "+5,28 tak plan 2"); level(v, 7.5, ZR_OLD, "+%.2f nock (bef.)" % ZR_OLD, 'l'); level(v, M, GZR + 0.75, "+%.2f nock glastak" % GZR)
dim(v, -12.9, 0.0, -12.9, 2.5, "2,5", vertical=True); dim(v, -12.9, 2.88, -12.9, 5.28, "2,4", vertical=True)
for a0, a1, t in ((5.5, 0.0, "5,5"), (0.0, -5.5, "5,5"), (-5.5, -12.3, "6,8")): dim(v, a0, -1.25, a1, -1.25, t)
for k, (a, b) in enumerate(((0.0, 2.55), (M, GZR + 0.35), (-5.5, 2.75), (-12.0, -0.3), (-8.0, 2.3), (-10.2, 6.6), (5.0, -0.5))):
    x, y = v.P(a, b); el.append('<circle cx="%.1f" cy="%.1f" r="9" fill="%s"/>' % (x, y, GREEN)); T(el, x, y + 4, str(k + 1), 11, "middle", "bold", "#ffffff")
title(el, 58, 520, "SEKTION A–A", "Befintligt allrum – vinterträdgård – nytt hus med trappa och övervåning")
scalebar(el, 58, 548, S)
# ---- elevation west ----
v = V(el, 50, 590, S, 8.6, 8.6, sg=-1)
ys = [8.6 - 0.25 * i for i in range(93)]; gp = [(y, Hf(-0.4, y)) for y in ys]
v.poly(gp + [(ys[-1], -1.7), (ys[0], -1.7)], fill="#eef1e6", stroke="none", sw=0)
# winter garden west gable (behind)
v.poly([(-0.05, 0.05), (-5.45, 0.05), (-5.45, GZ0), (M, GZR), (-0.05, GZ0)], fill=GLASS, stroke=GREEN, sw=0.6)
for yp in [-0.05 - (W - 0.1) * i / 5 for i in range(6)]:
    zt = GZ0 + (W / 2 - abs(yp - M)) * T15; v.rect(yp - 0.04, yp + 0.04, 0.05, zt, fill=GREEN, stroke=GREEN, sw=0.3)
v.rect(-5.45, -0.05, 2.12, 2.19, fill=GREEN, stroke=GREEN, sw=0.3); v.rect(-5.45, -0.05, 0.03, 0.11, fill=GREEN, stroke=GREEN, sw=0.3)
v.rect(-3.3, -2.2, 0.05, 2.12, fill="none", stroke=GREEN, sw=1.2); v.line(-2.75, 0.05, -2.75, 2.12, stroke=GREEN, sw=1.0)
v.poly([(0.0, GZ0 - 0.13), (0.0, GZ0 + 0.03), (M, GZR + 0.03), (-W, GZ0 + 0.03), (-W, GZ0 - 0.13), (M, GZR - 0.13)], fill=GREEN, stroke=CUT, sw=0.5)
v.rect(-W, -W + 0.17, 2.29, 2.44, fill="#a9adb0", stroke=CUT, sw=0.4); v.rect(-0.17, 0.0, 2.29, 2.44, fill="#a9adb0", stroke=CUT, sw=0.4)
# terrace front
v.rect(-5.48, -0.55, -0.66, -0.15, fill="#d8d3c8", stroke=INK, sw=0.6); v.rect(-5.1, -0.9, -0.66, -0.31, fill="#e3dfd6", stroke=INK, sw=0.6)
for py, r in ((-4.95, 0.5), (-0.95, 0.3)): v.rect(py - 0.25, py + 0.25, -0.15, 0.3, fill="#c98a64", stroke=MID, sw=0.5); v.circle(py, 0.3 + r + 0.6, r + 0.2, fill="#dfe8d4", stroke="#7d9670", sw=0.6)
# existing house west gable
v.rect(3.0, 3.3, 4.2, 4.95, fill="#b0543a", stroke=CUT, sw=0.5)
v.rect(5.5, 6.95, 2.25, 3.15, fill=TILE, stroke=CUT, sw=0.5); v.line(6.85, 0.0, 6.85, 2.25, sw=1.2); v.rect(5.5, 6.85, -0.05, 0.0, fill=CUT, stroke=CUT, sw=0.4)
v.line(5.5, 0.9, 6.85, 0.9, sw=0.8)
v.poly([(0, -0.25), (5.5, -0.25), (5.5, 2.2), (2.75, 4.52), (0, 2.2)], fill=BEIGE, stroke=CUT, sw=0.8)
for k in range(1, 29): v.line(0.19 * k, -0.25, 0.19 * k, min(2.2 + min(0.19 * k, 5.5 - 0.19 * k) * T40, 4.5), stroke="#cfc6b3", sw=0.5)
v.rect(0, 5.5, -0.5, -0.25, fill="#4a4640", stroke=CUT, sw=0.5); v.rect(-0.02, 0.11, -0.25, 2.2, fill="#ffffff", stroke=INK, sw=0.5); v.rect(5.39, 5.52, -0.25, 2.2, fill="#ffffff", stroke=INK, sw=0.5)
v.arc(2.75, 2.95, 0.59, 0, 180, fill="#ffffff", stroke=INK, sw=0.6); v.poly([(2.25, 2.95), (3.25, 2.95)] + [(2.75 + 0.5 * math.cos(math.radians(t)), 2.95 + 0.5 * math.sin(math.radians(t))) for t in range(0, 181, 15)], fill="#2c3a3c", stroke=INK, sw=0.5)
for t in (45, 90, 135): v.line(2.75, 2.95, 2.75 + 0.5 * math.cos(math.radians(t)), 2.95 + 0.5 * math.sin(math.radians(t)), stroke="#ffffff", sw=1.0)
v.rect(2.16, 3.34, 2.87, 2.95, fill="#ffffff", stroke=INK, sw=0.5)
tv = 0.30 * math.sqrt(1 + T40 * T40); top = [(6.1, 2.55 - 0.6 * T40 + 0.03), (2.75, ZR_OLD + 0.03), (-0.6, 2.55 - 0.6 * T40 + 0.03)]
v.poly(top + [(p[0], p[1] - tv) for p in top[::-1]], fill="#ffffff", stroke=INK, sw=0.7); v.poly(top, stroke=TILE, sw=3.0, close=False)
v.rect(-0.12, -0.05, -0.4, 2.1, fill="#c9cdd0", stroke=MID, sw=0.4)
# new house west gable
v.rect(-12.3, -5.5, -0.64, -0.02, fill="#b9b5ad", stroke=CUT, sw=0.6)
v.poly([(-12.3, -0.02), (-5.5, -0.02), (-5.5, 5.25), (-8.9, 5.25 + 3.4 * T32), (-12.3, 5.25)], fill=OCHRE, stroke=CUT, sw=0.8)
for k in range(1, 36):
    y_ = -5.5 - 0.19 * k; v.line(y_, -0.02, y_, 5.25 + min(y_ + 12.3, -5.5 - y_) * T32 - 0.05, stroke="#b48a48", sw=0.5)
v.rect(-12.3, -5.5, 2.5, 2.62, fill="#efe6d2", stroke=INK, sw=0.5)
for a0, a1 in ((-12.32, -12.18), (-5.62, -5.48)): v.rect(a0, a1, -0.02, 5.25, fill="#efe6d2", stroke=INK, sw=0.5)
for (y0, y1), (z0, z1) in (((-7.8, -6.6), (0.7, 2.2)), ((-11.2, -10.0), (0.7, 2.2)), ((-7.75, -6.65), (3.73, 5.03)), ((-11.15, -10.05), (3.73, 5.03))):
    v.rect(y0 - 0.1, y1 + 0.1, z0 - 0.1, z1 + 0.1, fill="#efe6d2", stroke=INK, sw=0.6); v.rect(y0, y1, z0, z1, fill=GREEN, stroke=INK, sw=0.5)
    for (qa, qb) in (((y0 + 0.06, (y0 + y1) / 2 - 0.045)), (((y0 + y1) / 2 + 0.045, y1 - 0.06))): v.rect(qa, qb, z0 + 0.06, z1 - 0.06, fill="#33454a", stroke="none", sw=0)
    for k in (1, 2): zb = z0 + (z1 - z0) * k / 3; v.line(y0, zb, y1, zb, stroke=GREEN, sw=1.6)
tvn = 0.34 * math.sqrt(1 + T32 * T32); top = [(-5.05, 5.63 - 0.45 * T32 + 0.03), (-8.9, ZR_NEW + 0.03), (-12.75, 5.63 - 0.45 * T32 + 0.03)]
v.poly(top + [(p[0], p[1] - tvn) for p in top[::-1]], fill="#efe6d2", stroke=INK, sw=0.7); v.poly(top, stroke=TILE, sw=3.0, close=False)
v.rect(-5.48, -5.41, -0.4, 5.25, fill="#a9adb0", stroke=MID, sw=0.4)
v.poly(gp, stroke=CUT, sw=1.4, close=False)
# notes on elevation
for (a, b), (ta, tb), txt, anc in ((((-9.4, 4.3), (-9.4, 9.2), "Stående träpanel, dämpad ockra", 'm')), (((-2.4, 1.2), (-1.0, 4.8), "Isolerglas i skogsgröna profiler", 'm')),
                                  (((1.2, 1.4), (2.2, 6.0), "Stående panel, ljus gråbeige (bef.)", 'm')), (((4.2, 3.95), (5.2, 6.8), "Röda takpannor", 'm'))):
    v.line(a, b, ta, tb - 0.15, stroke=MID, sw=0.5); v.circle(a, b, 0.05, fill=MID, stroke=MID); v.text(ta, tb, txt, 10, fill=INK)
level(v, -13.2, 0.0, "±0,00"); level(v, -13.2, ZR_NEW, "+%.2f" % ZR_NEW); level(v, 7.6, ZR_OLD, "+%.2f" % ZR_OLD, 'l')
title(el, 58, 1050, "FASAD MOT VÄSTER", "Gårdsfasaden med vinterträdgården mellan husen")
scalebar(el, 58, 1078, S)
# notes column
nx, ny = 1012, 90
T(el, nx, ny, "KONSTRUKTIONSPRINCIPER (skiss)", 13, "start", "bold", ls=0.5)
notes = ["Befintlig takfot kapas vid vägglivet. Ränndal och plåtbeslag tar vatten från glastaket.",
         "Lågt sadeltak i isolerglas ca 15°, nock ca +3,2 m. Öppningsbar taklucka och utvändig screen vid nocken.",
         "Ränndal och plåtbeslag mot nya husets vägg, stuprör i gavlarna.",
         "Isolerad platta på mark med kantelement och golvvärme. Samma golvnivå ±0,00 i alla tre delar.",
         "Mellanbjälklag ca 380 mm. L-trappa med 4 + 10 steg och vilplan i hörnet.",
         "Isolerat vindsbjälklag under kallvind. Takstolar och röda lertegelpannor ca 32°.",
         "Befintligt hus kvar på plintar. Loft under sadeltak ca 40°."]
yy = ny + 28
for i, n_ in enumerate(notes):
    el.append('<circle cx="%d" cy="%d" r="9" fill="%s"/>' % (nx + 9, yy - 4, GREEN)); T(el, nx + 9, yy, str(i + 1), 11, "middle", "bold", "#ffffff")
    words = n_.split(" "); line_ = ""; lines = []
    for w_ in words:
        if len(line_) + len(w_) > 62: lines.append(line_); line_ = w_
        else: line_ = (line_ + " " + w_).strip()
    lines.append(line_)
    for k, l_ in enumerate(lines): T(el, nx + 28, yy + k * 15, l_, 11)
    yy += 15 * len(lines) + 12
yy += 10; T(el, nx, yy, "ÖVRIGT", 13, "start", "bold", ls=0.5); yy += 22
for l_ in ("Ny huskropp: ytterväggar ca 300 mm, stående träpanel i dämpad ockra,",
           "mörkgröna bågar och dörrar, låg grå sockel.",
           "Vinterträdgård: uppvärmt bostadsrum med isolerglas, profiler med",
           "brutna köldbryggor och golvvärme under terrakottagolv.",
           "Fri rumshöjd ca 2,5 m i entréplan och ca 2,4 m på övervåningen.",
           "Avstånd till tomtgräns och byggnadshöjd ska kontrolleras",
           "mot detaljplanen innan bygglov."):
    T(el, nx, yy, l_, 11); yy += 16
open(OUT + "/ritning-sektion-fasad.svg", "w").write(svg(el, SW, SH))
print("ok")
