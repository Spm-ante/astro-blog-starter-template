# Dalstigen 17 - simplified massing model. X east (ridge direction), Y north, Z up, z=0 = floor level.
import bpy, bmesh, math, sys
import numpy as np
from mathutils import Vector, Matrix

MODE, QUAL = sys.argv[-2], sys.argv[-1]
OUT = "/tmp/claude-0/-home-user-astro-blog-starter-template/917fa675-5d57-5e76-8f36-64970dee47db/scratchpad/render/out"
SEC, FINAL, XC = MODE == 'sec', QUAL == 'final', 6.0
GAP = 5.5; DY = -(GAP - 4.0)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
col = scene.collection
T40, T32, T15 = math.tan(math.radians(40)), math.tan(math.radians(32)), math.tan(math.radians(15))

# ---------------- materials ----------------
MAT = {}
def lin(c): return tuple((v / 255.0) ** 2.2 for v in c) + (1.0,)
def pbr(name, c, rough=0.7, metal=0.0, emit=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value = lin(c); p.inputs['Roughness'].default_value = rough
    p.inputs['Metallic'].default_value = metal
    if emit:
        p.inputs['Emission Color'].default_value = lin(c); p.inputs['Emission Strength'].default_value = emit
    MAT[name] = m; return m
def mth(nt, op, a, b=None):
    n = nt.nodes.new('ShaderNodeMath'); n.operation = op
    for i, v in enumerate((a, b)):
        if v is None: continue
        if isinstance(v, (int, float)): n.inputs[i].default_value = v
        else: nt.links.new(v, n.inputs[i])
    return n.outputs[0]
def posnorm(nt):
    g = nt.nodes.new('ShaderNodeNewGeometry')
    sp = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(g.outputs['Position'], sp.inputs[0])
    sn = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(g.outputs['Normal'], sn.inputs[0])
    return sp.outputs, sn.outputs
def shade(m, mask, dark=0.75, bump=0.5, dist=0.02, height=None):
    nt = m.node_tree; p = nt.nodes['Principled BSDF']; base = p.inputs['Base Color'].default_value[:]
    mx = nt.nodes.new('ShaderNodeMixRGB'); mx.inputs['Color1'].default_value = base
    mx.inputs['Color2'].default_value = tuple(v * dark for v in base[:3]) + (1,)
    nt.links.new(mask, mx.inputs['Fac']); nt.links.new(mx.outputs['Color'], p.inputs['Base Color'])
    b = nt.nodes.new('ShaderNodeBump'); b.inputs['Strength'].default_value = bump; b.inputs['Distance'].default_value = dist
    nt.links.new(height if height is not None else mth(nt, 'SUBTRACT', 1.0, mask), b.inputs['Height'])
    nt.links.new(b.outputs['Normal'], p.inputs['Normal'])
def panel(name, c):
    m = pbr(name, c, 0.75); nt = m.node_tree; P, N = posnorm(nt)
    u = mth(nt, 'SUBTRACT', mth(nt, 'MULTIPLY', P['Y'], N['X']), mth(nt, 'MULTIPLY', P['X'], N['Y']))
    shade(m, mth(nt, 'GREATER_THAN', mth(nt, 'FRACT', mth(nt, 'DIVIDE', u, 0.19)), 0.62), 0.80, 0.7, 0.03)
def rooftile(name, c):
    m = pbr(name, c, 0.8); nt = m.node_tree; P, N = posnorm(nt)
    wave = mth(nt, 'ABSOLUTE', mth(nt, 'SINE', mth(nt, 'MULTIPLY', P['X'], math.pi / 0.15)))
    course = mth(nt, 'FRACT', mth(nt, 'DIVIDE', P['Z'], 0.2))
    shade(m, mth(nt, 'LESS_THAN', course, 0.14), 0.62, 1.0, 0.04, mth(nt, 'ADD', wave, mth(nt, 'MULTIPLY', course, -0.7)))
def gridtile(name, c, sx, sy, j=0.03, dark=0.6, rough=0.6):
    m = pbr(name, c, rough); nt = m.node_tree; P, N = posnorm(nt)
    fx = mth(nt, 'FRACT', mth(nt, 'DIVIDE', P['X'], sx)); fy = mth(nt, 'FRACT', mth(nt, 'DIVIDE', P['Y'], sy))
    shade(m, mth(nt, 'MAXIMUM', mth(nt, 'LESS_THAN', fx, j), mth(nt, 'LESS_THAN', fy, j)), dark, 0.3, 0.01)
def glass(name):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    o = nt.nodes.new('ShaderNodeOutputMaterial'); mx = nt.nodes.new('ShaderNodeMixShader')
    t = nt.nodes.new('ShaderNodeBsdfTransparent'); t.inputs[0].default_value = (0.93, 0.97, 0.95, 1)
    g = nt.nodes.new('ShaderNodeBsdfGlossy'); g.inputs['Roughness'].default_value = 0.0
    fr = nt.nodes.new('ShaderNodeFresnel'); fr.inputs['IOR'].default_value = 1.5
    nt.links.new(fr.outputs[0], mx.inputs[0]); nt.links.new(t.outputs[0], mx.inputs[1]); nt.links.new(g.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], o.inputs['Surface']); MAT[name] = m
def leaf(name, c, var=0.35):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    o = nt.nodes.new('ShaderNodeOutputMaterial'); mx = nt.nodes.new('ShaderNodeMixShader'); mx.inputs[0].default_value = 0.3
    d = nt.nodes.new('ShaderNodeBsdfDiffuse'); tr = nt.nodes.new('ShaderNodeBsdfTranslucent')
    g = nt.nodes.new('ShaderNodeNewGeometry'); cm = nt.nodes.new('ShaderNodeMixRGB'); b = lin(c)
    cm.inputs['Color1'].default_value = tuple(v * (1 - var) for v in b[:3]) + (1,)
    cm.inputs['Color2'].default_value = tuple(min(1, v * (1 + var)) for v in b[:3]) + (1,)
    nt.links.new(g.outputs['Random Per Island'], cm.inputs['Fac'])
    nt.links.new(cm.outputs['Color'], d.inputs['Color']); nt.links.new(cm.outputs['Color'], tr.inputs['Color'])
    nt.links.new(d.outputs[0], mx.inputs[1]); nt.links.new(tr.outputs[0], mx.inputs[2]); nt.links.new(mx.outputs[0], o.inputs['Surface'])
    MAT[name] = m
def ground_mat():
    m = pbr('ground', (90, 124, 58), 0.95); nt = m.node_tree; p = nt.nodes['Principled BSDF']
    at = nt.nodes.new('ShaderNodeAttribute'); at.attribute_name = 'rock'
    def noise(s, d=3.0):
        n = nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value = s; n.inputs['Detail'].default_value = d; return n.outputs[0]
    def mix(f, a, b):
        x = nt.nodes.new('ShaderNodeMixRGB')
        for k, v in (('Fac', f), ('Color1', a), ('Color2', b)):
            if isinstance(v, tuple): x.inputs[k].default_value = v
            elif isinstance(v, float): x.inputs[k].default_value = v
            else: nt.links.new(v, x.inputs[k])
        return x.outputs[0]
    rf = mth(nt, 'MULTIPLY', mth(nt, 'ADD', mth(nt, 'SUBTRACT', at.outputs['Fac'], 0.30), mth(nt, 'MULTIPLY', noise(0.5), 0.35)), 5.0)
    rf = mth(nt, 'MAXIMUM', mth(nt, 'MINIMUM', rf, 1.0), 0.0)
    P, N = posnorm(nt)
    stripe = mth(nt, 'MULTIPLY', mth(nt, 'SINE', mth(nt, 'ADD', mth(nt, 'MULTIPLY', P['X'], 2.0), mth(nt, 'MULTIPLY', P['Y'], 6.0))), 0.09)
    lawn = mix(mth(nt, 'ADD', mth(nt, 'ADD', mth(nt, 'MULTIPLY', noise(0.35, 5.0), 0.7), mth(nt, 'MULTIPLY', noise(6.0, 4.0), 0.3)), stripe), lin((62, 100, 40)), lin((112, 146, 62)))
    mossf = mth(nt, 'GREATER_THAN', noise(1.1, 5.0), 0.52)
    rock = mix(mossf, mix(noise(4.0), lin((176, 158, 150)), lin((128, 122, 120))), lin((98, 112, 60)))
    nt.links.new(mix(rf, lawn, rock), p.inputs['Base Color'])
    b = nt.nodes.new('ShaderNodeBump'); b.inputs['Strength'].default_value = 0.6; b.inputs['Distance'].default_value = 0.15
    nt.links.new(noise(1.6, 6.0), b.inputs['Height']); nt.links.new(b.outputs['Normal'], p.inputs['Normal'])

panel('oldpanel', (216, 207, 190)); panel('ochre', (202, 160, 90))
pbr('white', (240, 238, 232), 0.5); pbr('trim', (232, 226, 212), 0.55); pbr('green', (26, 54, 40), 0.4)
rooftile('tile_old', (150, 80, 60)); rooftile('tile_new', (172, 90, 62))
pbr('zinc', (150, 155, 158), 0.35, 0.9); pbr('concrete', (152, 150, 144), 0.85); pbr('skirt', (72, 68, 62), 0.9)
gridtile('stone', (160, 154, 144), 0.62, 0.47, 0.025, 0.55, 0.8); gridtile('terracotta', (192, 112, 76), 0.3, 0.3, 0.03, 0.62, 0.5)
pbr('pot', (180, 100, 64), 0.8); pbr('oak', (184, 144, 100), 0.5); pbr('pine', (216, 182, 132), 0.5)
pbr('wint', (238, 235, 228), 0.8); pbr('fabric', (234, 226, 210), 0.9); pbr('ins', (238, 216, 150), 0.9)
pbr('gravel', (124, 119, 112), 1.0); pbr('earth', (100, 82, 66), 1.0); pbr('poche', (36, 36, 38), 1.0)
pbr('soil', (62, 50, 42), 1.0); pbr('sofa', (140, 150, 150), 0.9); pbr('pane', (10, 14, 16), 0.04)
pbr('lit', (206, 226, 246), 0.5, 0.0, 1.5); pbr('bark', (92, 76, 62), 0.9); pbr('birchbark', (228, 226, 218), 0.7)
pbr('pinebark', (150, 96, 62), 0.9); pbr('bathtile', (206, 214, 208), 0.3); pbr('lamp', (255, 236, 200), 0.5, 0.0, 6.0)
glass('glass'); leaf('spruce', (34, 62, 36), 0.4); leaf('birch', (118, 160, 62), 0.3); leaf('pineleaf', (52, 84, 52), 0.35)
leaf('shrub', (58, 98, 48), 0.35); leaf('olive', (112, 132, 96), 0.3); leaf('citrus', (52, 104, 46), 0.3)
leaf('lavender', (132, 118, 178), 0.3); leaf('rhodo', (188, 96, 168), 0.3)
ground_mat()

# ---------------- geometry helpers ----------------
def obj(name, verts, faces, m, **props):
    me = bpy.data.meshes.new(name); me.from_pydata([tuple(v) for v in verts], [], faces); me.update()
    o = bpy.data.objects.new(name, me); col.objects.link(o)
    if m: me.materials.append(MAT[m])
    for k, v in props.items(): o[k] = v
    return o
def box(x, y, z, m, **props):
    (x0, x1), (y0, y1), (z0, z1) = sorted(x), sorted(y), sorted(z)
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    return obj('b', v, [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)], m, **props)
def ext(prof, x0, x1, m, **props):
    n = len(prof); v = [(x0, y, z) for y, z in prof] + [(x1, y, z) for y, z in prof]
    f = [tuple(range(n))[::-1], tuple(range(n, 2 * n))] + [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    return obj('e', v, f, m, **props)
def cone(x, y, z, r1, r2, h, m, seg=16, **props):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r1, radius2=r2, depth=h,
                                             matrix=Matrix.Translation((x, y, z + h / 2)))
    me = bpy.data.meshes.new('c'); bm.to_mesh(me); bm.free(); o = bpy.data.objects.new('c', me); col.objects.link(o)
    me.materials.append(MAT[m])
    for k, v in props.items(): o[k] = v
    return o
def wall(axis, a, b, t, z0, z1, m, ops=()):
    cur = a
    def bx(u0, u1, za, zb):
        if u1 - u0 < 1e-4 or zb - za < 1e-4: return
        box((u0, u1), t, (za, zb), m) if axis == 'x' else box(t, (u0, u1), (za, zb), m)
    for (ua, ub, za, zb) in sorted(ops):
        bx(cur, ua, z0, z1); bx(ua, ub, z0, za); bx(ua, ub, zb, z1); cur = ub
    bx(cur, b, z0, z1)
def window(axis, c, sgn, u0, u1, z0, z1, sash='green', trim='white', mull=True, bars=2, door=False):
    def b(ua, ub, za, zb, d, m):
        dd = (c, c + sgn * d)
        box(dd, (ua, ub), (za, zb), m) if axis == 'x' else box((ua, ub), dd, (za, zb), m)
    cw, fw = 0.10, 0.06
    b(u0 - cw, u1 + cw, z1, z1 + cw, 0.035, trim); b(u0 - cw, u0, z0, z1, 0.035, trim); b(u1, u1 + cw, z0, z1, 0.035, trim)
    if not door: b(u0 - cw, u1 + cw, z0 - cw, z0, 0.045, trim)
    b(u0, u1, z0, z1, 0.015, 'pane')
    for ua, ub, za, zb in ((u0, u0 + fw, z0, z1), (u1 - fw, u1, z0, z1), (u0, u1, z0, z0 + fw), (u0, u1, z1 - fw, z1)): b(ua, ub, za, zb, 0.045, sash)
    um = (u0 + u1) / 2
    if mull: b(um - 0.045, um + 0.045, z0, z1, 0.045, sash)
    for k in range(bars):
        zb = z0 + (z1 - z0) * (k + 1) / (bars + 1); b(u0, u1, zb - 0.012, zb + 0.012, 0.035, sash)
def lunette(c, sgn, yc, zb, r, lit=False):
    arc = lambda rr, n=17: [(yc + rr * math.cos(a), zb + rr * math.sin(a)) for a in np.linspace(0, math.pi, n)]
    ext(arc(r), c, c + sgn * 0.02, 'lit' if lit else 'pane')
    if not lit:
        ext(arc(r + 0.09) + arc(r)[::-1], c, c + sgn * 0.04, 'white')
        box((c, c + sgn * 0.045), (yc - r - 0.12, yc + r + 0.12), (zb - 0.08, zb), 'white')
        box((c, c + sgn * 0.03), (yc - 0.015, yc + 0.015), (zb, zb + r), 'white')
def roof(ya, yb, zw, tan, t, x0, x1, m, os=0.5, on=0.5, side='both', **props):
    yc = (ya + yb) / 2; zr = zw + (yc - ya) * tan; tv = t * math.sqrt(1 + tan * tan)
    if side in ('both', 's'):
        ext([(ya - os, zw - os * tan), (yc, zr), (yc, zr - tv), (ya - os, zw - os * tan - tv)], x0, x1, m, **props)
    if side in ('both', 'n'):
        ext([(yb + on, zw - on * tan), (yc, zr), (yc, zr - tv), (yb + on, zw - on * tan - tv)], x0, x1, m, **props)
    return zr, tv
def cloud(name, pts, size, m, seed=0, flat=0.6):
    rng = np.random.default_rng(seed); n = len(pts)
    if SEC and name != 'fol' and float(np.mean(pts[:, 0])) < XC + 0.2: return None
    a = rng.normal(size=(n, 3)); a /= np.linalg.norm(a, axis=1)[:, None]
    b = np.cross(a, rng.normal(size=(n, 3))); b /= np.linalg.norm(b, axis=1)[:, None]
    s = (size * (0.6 + 0.8 * rng.random(n)))[:, None]
    v = np.stack([pts - a * s - b * s * flat, pts + a * s - b * s * flat, pts + a * s + b * s * flat, pts - a * s + b * s * flat], 1).reshape(-1, 3)
    return obj(name, v.tolist(), np.arange(4 * n).reshape(n, 4).tolist(), m, nocut=1, cap='none')
def blob(x, y, z, r, rz, n, size, m, seed=0):
    rng = np.random.default_rng(seed); p = rng.normal(size=(n, 3)) * np.array([r, r, rz]) * 0.5 + np.array([x, y, z])
    return cloud('blob', p, size, m, seed)

# ---------------- terrain ----------------
def H(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    sm = lambda v, a, b: (lambda f: f * f * (3 - 2 * f))(np.clip((v - a) / (b - a), 0, 1))
    def bump(cx, cy, r):
        f = np.clip(1 - np.hypot(x - cx, y - cy) / r, 0, 1); return f * f * (3 - 2 * f)
    hill = 3.0 * bump(19, -1, 7.5) + 2.2 * bump(17, -13, 6.5) + 2.4 * bump(18, 10, 6.5) + 1.5 * bump(-14, 16, 7)
    h = -0.45 - 3.0 * sm(y, 7, 22) + 1.6 * sm(-y, 13, 40) - 0.8 * sm(-x, 4, 30) + hill
    pad = ((x > 0.25) & (x < 8.95) & (y > -10.85 + DY) & (y < 0.0)) | ((x > 0.0) & (x < 8.9) & (y >= 0.0) & (y < 5.5))
    return np.where(pad, np.minimum(h, -0.64), h), hill
gx = np.arange(-46, 46.01, 0.75); GX, GY = np.meshgrid(gx, gx, indexing='ij'); GZ, GH = H(GX, GY)
n = len(gx); idx = np.arange(n * n).reshape(n, n)
faces = np.stack([idx[:-1, :-1], idx[1:, :-1], idx[1:, 1:], idx[:-1, 1:]], -1).reshape(-1, 4).tolist()
ter = obj('terrain', np.stack([GX, GY, GZ], -1).reshape(-1, 3).tolist(), faces, 'ground', cap='none')
ca = ter.data.color_attributes.new('rock', 'FLOAT_COLOR', 'POINT'); rk = np.clip(GH / 1.2, 0, 1).reshape(-1)
ca.data.foreach_set('color', np.stack([rk, rk, rk, np.ones_like(rk)], -1).reshape(-1).tolist())
for p in ter.data.polygons: p.use_smooth = True
if SEC:
    ys = np.arange(-17, 12.01, 0.25); zs = H(np.full_like(ys, XC), ys)[0]
    ext([(float(a), float(b)) for a, b in zip(ys, zs)] + [(12.0, -4.0), (-17.0, -4.0)], XC, XC + 0.04, 'earth', nocut=1)

# ---------------- existing house: x 0..8.9, y 0..5.5 ----------------
wt = 0.17
wall('x', 0, 8.9, (0, wt), -0.25, 2.2, 'oldpanel', [(5.26, 6.85, 0.0, 2.0)])            # south, real door opening
box((0, 8.9), (5.5 - wt, 5.5), (-0.25, 2.2), 'oldpanel'); box((0, wt), (wt, 5.5 - wt), (-0.25, 2.2), 'oldpanel')
box((8.9 - wt, 8.9), (wt, 5.5 - wt), (-0.25, 2.2), 'oldpanel')
for xa in (0, 8.9 - wt): ext([(0, 2.2), (5.5, 2.2), (2.75, 4.52)], xa, xa + wt, 'oldpanel')
roof(0, 5.5, 2.55, T40, 0.25, -0.55, 9.45, 'tile_old', on=0.6, side='n')
roof(0, 5.5, 2.55, T40, 0.25, -0.55, 3.7, 'tile_old', os=0.6, side='s')
zr_old, tvo = roof(0, 5.5, 2.55, T40, 0.25, 3.7, 9.45, 'tile_old', os=0.02, side='s')
for xa in (-0.59, 9.45):                                                                 # bargeboards
    roof(0, 5.5, 2.58, T40, 0.30, xa, xa + 0.04, 'white', os=0.62 if xa < 0 else 0.02, on=0.62)
box((-0.55, 9.45), (2.67, 2.83), (zr_old - 0.02, zr_old + 0.06), 'tile_old')            # ridge
box((4.3, 4.6), (3.0, 3.3), (4.3, 4.95), 'tile_old')                                     # small chimney
box((-0.55, 3.7), (-0.68, -0.58), (1.98, 2.07), 'white'); box((-0.55, 9.45), (6.08, 6.18), (1.98, 2.07), 'white')   # gutters
for cx, cy in ((0, 0), (0, 5.5)):                                                        # corner boards west
    box((cx - 0.02, cx + 0.11), (cy - 0.02 if cy == 0 else cy - 0.11, cy + 0.11 if cy == 0 else cy + 0.02), (-0.25, 2.2), 'white')
box((-0.02, 8.9), (-0.03, 0.0), (-0.5, -0.25), 'skirt'); box((-0.03, 0.0), (0, 5.5), (-0.5, -0.25), 'skirt')
box((0.2, 8.7), (0.2, 5.3), (-0.25, -0.012), 'pine', cap='poche'); box((wt, 8.9 - wt), (wt, 5.5 - wt), (-0.012, 0), 'pine')
box((wt, 8.9 - wt), (wt, 5.5 - wt), (2.30, 2.55), 'wint')
for px in (0.3, 3.0, 6.3, 8.6):
    for py in (0.25, 2.75, 5.25): box((px - 0.15, px + 0.15), (py - 0.15, py + 0.15), (-0.7, -0.25), 'concrete')
window('y', 0.0, -1, 1.26, 2.14, 0.85, 2.0, sash='white', bars=2)                         # bedroom window to courtyard
lunette(0.0, -1, 2.75, 2.95, 0.5); lunette(8.9 - wt - 0.03, -1, 2.75, 2.95, 0.5, lit=True)
# interior (seen in section)
box((8.70, 8.73), (wt, 5.5 - wt), (0, 2.3), 'wint'); ext([(1.12, 2.55), (4.33, 2.55), (4.33, 3.15), (2.75, 4.45), (1.12, 3.12)], 8.70, 8.73, 'wint')
box((wt, 8.73), (1.08, 1.12), (2.55, 3.12), 'wint'); box((wt, 8.73), (4.33, 4.37), (2.55, 3.15), 'wint')
box((5.79, 7.68), (3.26, 3.36), (0, 2.3), 'wint')                                         # kitchen wing wall
box((6.05, 8.7), (4.73, 5.33), (0, 0.88), 'white'); box((6.05, 8.7), (4.71, 5.33), (0.88, 0.92), 'oak')
box((6.05, 8.1), (4.98, 5.33), (1.45, 2.15), 'white'); box((8.12, 8.7), (4.73, 5.33), (0.92, 2.0), 'white')
box((7.85, 8.68), (0.55, 2.45), (0, 0.42), 'sofa'); box((8.45, 8.68), (0.55, 2.45), (0.42, 0.85), 'sofa')
box((6.6, 7.5), (1.0, 2.0), (0.36, 0.40), 'oak'); box((6.3, 8.6), (0.4, 2.7), (0, 0.012), 'fabric')
box((6.9, 8.68), (1.85, 3.65), (2.55, 2.95), 'fabric'); box((8.6, 8.68), (1.85, 3.65), (2.95, 3.35), 'sofa')
for ya, yb in ((1.63, 2.65), (2.76, 3.80)): box((8.66, 8.69), (ya, yb), (0.85, 2.0), 'lit')

# ---------------- new house (built at 4 m gap, shifted by DY) ----------------
_pre = set(bpy.data.objects)
X0, X1, YA, YB, w3 = 0.3, 8.9, -10.8, -4.0, 0.3
wall('x', X0, X1, (YB - w3, YB), -0.02, 5.25, 'ochre', [(1.3, 2.9, 0.0, 2.1), (5.5, 6.7, 0.0, 2.1)])   # north
box((X0, X1), (YA, YA + w3), (-0.02, 5.25), 'ochre'); box((X0, X0 + w3), (YA + w3, YB - w3), (-0.02, 5.25), 'ochre')
box((X1 - w3, X1), (YA + w3, YB - w3), (-0.02, 5.25), 'ochre')
for xa in (X0, X1 - w3): ext([(YA, 5.25), (YB, 5.25), (-7.4, 7.38)], xa, xa + w3, 'ochre')
zr_new, tvn = roof(YA, YB, 5.63, T32, 0.30, X0 - 0.4, X1 + 0.4, 'tile_new', os=0.45, on=0.45)
for xa in (X0 - 0.44, X1 + 0.4): roof(YA, YB, 5.66, T32, 0.34, xa, xa + 0.04, 'trim', os=0.47, on=0.47)
box((X0 - 0.4, X1 + 0.4), (-7.48, -7.32), (zr_new - 0.02, zr_new + 0.06), 'tile_new')
for yg in (YB + 0.45, YA - 0.55): box((X0 - 0.4, X1 + 0.4), (yg, yg + 0.1), (5.25, 5.34), 'zinc')
box((X0 - 0.09, X0 - 0.02), (YB + 0.02, YB + 0.09), (-0.4, 5.25), 'zinc')                 # downpipe NW corner
for cy in (YA, YB):                                                                      # corner boards west gable
    box((X0 - 0.02, X0 + 0.12), (cy - 0.02 if cy == YA else cy - 0.12, cy + 0.12 if cy == YA else cy + 0.02), (-0.02, 5.25), 'trim')
box((X0 - 0.02, X1), (YB, YB + 0.03), (2.5, 2.62), 'trim'); box((X0 - 0.03, X0), (YA, YB), (2.5, 2.62), 'trim')   # storey band
for xa, xb, ya, yb in ((X0 + 0.03, X0 + w3, YA + 0.03, YB - 0.03), (X1 - w3, X1 - 0.03, YA + 0.03, YB - 0.03),
                       (X0 + 0.03, X1 - 0.03, YA + 0.03, YA + w3), (X0 + 0.03, X1 - 0.03, YB - w3, YB - 0.03)):
    box((xa, xb), (ya, yb), (-0.64, -0.02), 'concrete')                                  # low plinth
xi0, xi1, yi0, yi1 = X0 + w3, X1 - w3, YA + w3, YB - w3
box((xi0, xi1), (yi0, yi1), (-0.12, -0.015), 'concrete', cap='self'); box((xi0, xi1), (yi0, yi1), (-0.015, 0), 'oak', cap='self')
box((xi0, xi1), (yi0, yi1), (-0.42, -0.12), 'ins', cap='self'); box((xi0, xi1), (yi0, yi1), (-0.64, -0.42), 'gravel', cap='self')
box((xi0, 6.7), (yi0, yi1), (2.5, 2.88), 'wint'); box((6.7, 7.7), (yi0, -5.2), (2.5, 2.88), 'wint'); box((7.7, xi1), (yi0, -7.7), (2.5, 2.88), 'wint')
box((xi0, xi1), (yi0, yi1), (5.28, 5.33), 'wint'); box((xi0, xi1), (yi0, yi1), (5.33, 5.7), 'ins', cap='self')
for yc in (-5.7, -9.1):                                                                  # west gable windows
    window('x', X0, -1, yc - 0.6, yc + 0.6, 0.7, 2.2, trim='trim'); window('x', X0, -1, yc - 0.55, yc + 0.55, 3.73, 5.03, trim='trim')
window('y', YB, 1, 1.3, 2.9, 0.0, 2.1, trim='trim', bars=0, door=True); window('y', YB, 1, 1.55, 2.65, 3.73, 5.03, trim='trim')
# interior (section)
box((8.57, 8.6), (yi0, yi1), (0, 2.5), 'wint'); box((8.57, 8.6), (yi0, yi1), (2.88, 5.28), 'wint')
for i in range(1, 5):                                                                    # lower run, heading east
    box((6.7 + 0.25 * (i - 1), 6.7 + 0.25 * i), (-5.2, -4.3), (0, 0.18 * i - 0.04), 'white'); box((6.7 + 0.25 * (i - 1) - 0.02, 6.7 + 0.25 * i), (-5.2, -4.3), (0.18 * i - 0.04, 0.18 * i), 'oak')
box((7.7, 8.57), (-5.2, -4.3), (0, 0.86), 'white'); box((7.7, 8.57), (-5.2, -4.3), (0.86, 0.90), 'oak')
for j in range(1, 11):                                                                   # upper run, heading south
    h = 0.90 + 0.18 * j
    box((7.7, 8.57), (-5.2 - 0.25 * j, -5.2 - 0.25 * (j - 1)), (0, h - 0.04), 'white'); box((7.68, 8.57), (-5.2 - 0.25 * j, -5.2 - 0.25 * (j - 1) + 0.02), (h - 0.04, h), 'oak')
ext([(-5.2, 1.8), (-7.7, 3.6), (-7.7, 3.65), (-5.2, 1.85)], 7.70, 7.75, 'oak')
for k in range(20):
    yb_ = -5.2 - 0.125 * (k + 0.5); zb_ = 0.9 + 0.72 * (-5.2 - yb_)
    box((7.715, 7.735), (yb_ - 0.01, yb_ + 0.01), (zb_, zb_ + 0.9), 'white')
box((7.7, 7.76), (-7.7, -5.2), (2.88, 3.78), 'wint'); box((6.7, 7.7), (-5.26, -5.2), (2.88, 3.78), 'wint'); box((6.7, 6.76), (-5.2, yi1), (2.88, 3.78), 'wint')
wall('x', 5.5, 8.57, (-8.2, -8.1), 0, 2.5, 'wint', [(6.6, 7.4, 0.0, 2.05)])              # laundry/plant room wall
box((8.0, 8.57), (-9.05, -8.4), (0, 0.85), 'white'); box((8.0, 8.57), (-9.72, -9.07), (0, 0.85), 'white'); box((7.98, 8.57), (-9.75, -8.38), (0.85, 0.89), 'oak')
cone(8.2, -10.1, 0, 0.27, 0.27, 1.7, 'white'); box((8.2, 8.57), (-9.7, -8.45), (1.5, 2.2), 'white')
box((8.555, 8.57), (-9.9, -9.0), (1.1, 2.1), 'lit'); box((8.555, 8.57), (-7.0, -6.0), (1.6, 3.5), 'lit'); box((8.555, 8.57), (-10.0, -9.3), (4.18, 4.98), 'lit')
box((5.4, 6.7), (-5.6, -5.5), (2.88, 5.28), 'wint'); box((6.6, 6.7), (-5.5, yi1), (2.88, 5.28), 'wint')   # store
for zs_ in (3.3, 3.75, 4.2, 4.65): box((6.25, 6.6), (-5.45, -4.35), (zs_, zs_ + 0.03), 'oak')
wall('x', 5.9, 8.57, (-8.7, -8.6), 2.88, 5.28, 'wint', [(6.9, 7.6, 2.88, 4.93)])         # shower room wall
box((5.95, 8.57), (yi0, -8.7), (2.88, 2.895), 'bathtile'); box((8.1, 8.55), (-9.5, -8.95), (3.5, 3.76), 'white')
box((7.95, 8.55), (-10.3, -9.95), (2.88, 3.3), 'white'); box((6.84, 6.86), (yi0, -9.6), (2.9, 4.9), 'glass', cap='none')
box((8.555, 8.57), (-9.55, -8.9), (3.95, 4.75), 'pane')

for _o in set(bpy.data.objects) - _pre: _o.data.transform(Matrix.Translation((0, DY, 0)))
# ---------------- winter garden: x 3.7..8.7, y -GAP..0 ----------------
W = GAP; M = -W / 2; HS = W / 2
GZ0, GZR = 2.42, 2.42 + HS * T15
box((3.75, 8.65), (-W + 0.05, -0.05), (-0.02, 0), 'terracotta', cap='self'); box((3.75, 8.65), (-W + 0.05, -0.05), (-0.12, -0.02), 'concrete', cap='self')
box((3.75, 8.65), (-W + 0.05, -0.05), (-0.42, -0.12), 'ins', cap='self'); box((3.75, 8.65), (-W + 0.05, -0.05), (-0.64, -0.42), 'gravel', cap='self')
for xg in (3.66, 8.66): box((xg, xg + 0.09), (-W, 0.0), (-0.64, 0.05), 'stone')
gable = [(-W + 0.03, 0.05), (-0.03, 0.05), (-0.03, GZ0), (M, GZR), (-W + 0.03, GZ0)]
for xg in (3.7, 8.7):
    ext(gable, xg - 0.012, xg + 0.012, 'glass', cap='none')
    for yp in np.linspace(-0.05, -W + 0.05, 6):
        zt = GZ0 + (HS - abs(yp - M)) * T15
        box((xg - 0.04, xg + 0.04), (yp - 0.035, yp + 0.035), (0.05, zt), 'green')
    box((xg - 0.04, xg + 0.04), (-W + 0.03, -0.03), (2.12, 2.19), 'green'); box((xg - 0.04, xg + 0.04), (-W + 0.03, -0.03), (0.03, 0.11), 'green')
for xr in np.linspace(3.7, 8.7, 7):                                                      # rafters
    ext([(-W, GZ0 - 0.13), (-W, GZ0), (M, GZR), (M, GZR - 0.13)], xr - 0.035, xr + 0.035, 'green')
    ext([(0, GZ0 - 0.13), (0, GZ0), (M, GZR), (M, GZR - 0.13)], xr - 0.035, xr + 0.035, 'green')
box((3.66, 8.74), (M - 0.06, M + 0.06), (GZR - 0.16, GZR + 0.02), 'green')
ext([(-W, GZ0), (M, GZR), (M, GZR + 0.03), (-W, GZ0 + 0.03)], 3.68, 8.72, 'glass', cap='none')
ext([(0, GZ0), (M, GZR), (M, GZR + 0.03), (0, GZ0 + 0.03)], 3.68, 8.72, 'glass', cap='none')
for ya, yb in ((-0.17, 0.0), (-W, -W + 0.17)):                                           # box gutters + downpipes
    box((3.6, 8.8), (ya, yb), (2.29, 2.31), 'zinc'); box((3.6, 8.8), (ya, ya + 0.02), (2.29, 2.44), 'zinc'); box((3.6, 8.8), (yb - 0.02, yb), (2.29, 2.44), 'zinc')
    box((3.6, 3.67), (ya + 0.05, ya + 0.12), (-0.15, 2.3), 'zinc')
box((3.8, 8.6), (M - 0.13, M + 0.13), (GZR + 0.03, GZR + 0.11), 'green')                 # screen cassette at ridge
ext([(M - 0.13, GZR + 0.08), (M - 1.25, GZR + 0.08 - 1.12 * T15), (M - 1.25, GZR + 0.09 - 1.12 * T15), (M - 0.13, GZR + 0.09)], 5.42, 7.0, 'fabric')
ext([(M + 0.1, GZR + 0.02), (M + 0.85, GZR - 0.12), (M + 0.85, GZR - 0.09), (M + 0.1, GZR + 0.05)], 7.1, 7.8, 'glass', cap='none')   # roof vent open
box((7.1, 7.8), (M + 0.83, M + 0.87), (GZR - 0.14, GZR - 0.08), 'green')
box((7.2, 8.1), (M - 0.9, M + 0.9), (0.71, 0.75), 'oak')                                 # dining table 1.8 x 0.9
for tx in (7.26, 8.04):
    for ty in (M - 0.84, M + 0.84): box((tx - 0.03, tx + 0.03), (ty - 0.03, ty + 0.03), (0, 0.71), 'oak')
for cxs, sg in ((6.97, -1), (8.33, 1)):
    for cy in (M - 0.6, M, M + 0.6):
        box((cxs - 0.21, cxs + 0.21), (cy - 0.21, cy + 0.21), (0.42, 0.46), 'green'); box((cxs + sg * 0.19, cxs + sg * 0.22), (cy - 0.2, cy + 0.2), (0.46, 0.88), 'green')
        for lx in (-0.19, 0.19):
            for ly in (-0.19, 0.19): box((cxs + lx - 0.015, cxs + lx + 0.015), (cy + ly - 0.015, cy + ly + 0.015), (0, 0.42), 'green')
box((7.645, 7.655), (M - 0.005, M + 0.005), (2.0, GZR - 0.16), 'green'); cone(7.65, M, 1.78, 0.22, 0.05, 0.24, 'lamp')
def plant(x, y, z, pr, ph, hs, r, m, n=320, seed=1, size=0.045):
    cone(x, y, z, pr * 0.7, pr, ph, 'pot'); cone(x, y, z + ph, pr * 1.06, pr * 1.06, 0.03, 'pot')
    if hs > 0.3: box((x - 0.02, x + 0.02), (y - 0.02, y + 0.02), (z + ph, z + ph + hs), 'bark')
    blob(x, y, z + ph + hs + r * 0.5, r, r * 0.85, n * 3, size, m, seed)
plant(4.25, -0.6, 0, 0.26, 0.42, 0.9, 1.0, 'citrus', 420, 1); plant(4.3, -W + 0.6, 0, 0.28, 0.45, 1.0, 1.1, 'olive', 420, 2)
plant(8.3, -0.5, 0, 0.22, 0.36, 0.7, 0.8, 'citrus', 300, 3); plant(8.3, -W + 0.5, 0, 0.24, 0.4, 0.0, 0.9, 'shrub', 300, 4, 0.1)
plant(5.1, -W + 0.45, 0, 0.16, 0.26, 0.0, 0.5, 'lavender', 160, 5, 0.04); plant(4.3, M, 0, 0.3, 0.5, 1.2, 1.2, 'citrus', 420, 6)

# ---------------- courtyard terrace ----------------
box((-1.6, 3.66), (-W + 0.02, -0.55), (-0.66, -0.15), 'stone'); box((-2.0, -1.6), (-W + 0.4, -0.9), (-0.66, -0.31), 'stone')
box((-0.02, 3.66), (-0.55, -0.03), (-0.66, -0.2), 'soil'); box((0.3, 3.66), (-W + 0.02, -W + 0.5), (-0.66, -0.2), 'soil')
for i, px in enumerate((0.45, 1.25, 2.1, 2.9)): blob(px, -0.3, -0.02, 0.5, 0.35, 600, 0.025, 'lavender' if i % 2 == 0 else 'shrub', 10 + i)
for i, px in enumerate((0.8, 1.8, 2.8)): blob(px, -W + 0.27, -0.05, 0.6, 0.4, 700, 0.03, 'shrub', 40 + i)
TX, TY = 1.0, M + 0.2
cone(TX, TY, -0.15, 0.03, 0.03, 0.7, 'green'); cone(TX, TY, 0.55, 0.38, 0.38, 0.03, 'green')            # cafe table
for cy in (TY - 0.65, TY + 0.65):
    box((TX - 0.2, TX + 0.2), (cy - 0.2, cy + 0.2), (0.27, 0.31), 'oak'); box((TX - 0.2, TX + 0.2), (cy - 0.2 if cy < TY else cy + 0.17, cy - 0.17 if cy < TY else cy + 0.2), (0.31, 0.72), 'oak')
    for lx in (TX - 0.17, TX + 0.17):
        for ly in (cy - 0.17, cy + 0.17): box((lx - 0.015, lx + 0.015), (ly - 0.015, ly + 0.015), (-0.15, 0.27), 'oak')
box((2.4, 3.5), (-W + 0.55, -W + 0.95), (0.25, 0.3), 'oak'); box((2.42, 2.5), (-W + 0.55, -W + 0.95), (-0.15, 0.25), 'oak'); box((3.4, 3.48), (-W + 0.55, -W + 0.95), (-0.15, 0.25), 'oak')
plant(3.25, -0.95, -0.15, 0.2, 0.34, 0.0, 0.6, 'shrub', 220, 21, 0.06); plant(-1.0, -W + 0.55, -0.15, 0.28, 0.45, 1.0, 1.0, 'olive', 420, 22)
plant(-1.2, -0.95, -0.15, 0.2, 0.32, 0.0, 0.55, 'lavender', 200, 23, 0.04)

# ---------------- trees and shrubs ----------------
def tree_mesh(kind, seed):
    rng = np.random.default_rng(seed); h = 1.0
    if kind == 'spruce':
        n = 17000; t = rng.random(n) ** 0.85; R = 0.17 * (1 - t) ** 0.85 + 0.01; rr = R * (0.3 + 0.7 * np.sqrt(rng.random(n))); a = rng.random(n) * 6.283
        z = 0.1 + 0.9 * t; z = np.round(z / 0.035) * 0.035 + rng.normal(size=n) * 0.008 - rr * 0.3
        p = np.stack([rr * np.cos(a), rr * np.sin(a), z], 1); return p, 0.0055, 'spruce', (0.014, 0.002, 'bark')
    k = 16 if kind == 'birch' else 9; z0, z1, rad = (0.42, 0.97, 0.2) if kind == 'birch' else (0.66, 0.98, 0.17)
    cz = z0 + (z1 - z0) * rng.random(k); cr = rad * np.sin(np.pi * (cz - z0 + 0.08) / (z1 - z0 + 0.16)) * np.sqrt(rng.random(k)); ca_ = rng.random(k) * 6.283
    c = np.stack([cr * np.cos(ca_), cr * np.sin(ca_), cz], 1); n = 15000 if kind == 'birch' else 9000
    p = c[rng.integers(0, k, n)] + rng.normal(size=(n, 3)) * (0.055 if kind == 'birch' else 0.045)
    return (p, 0.0032, 'birch', (0.011, 0.003, 'birchbark')) if kind == 'birch' else (p, 0.0045, 'pineleaf', (0.012, 0.005, 'pinebark'))
PROTO = {}
def tree(kind, x, y, h, rot=0.0, var=0):
    key = (kind, var)
    if key not in PROTO:
        p, sz, m, (r1, r2, bm_) = tree_mesh(kind, 100 + var * 7 + len(kind))
        f = cloud('fol', p, sz, m, 50 + var); t = cone(0, 0, 0, r1, r2, 0.96 if kind != 'spruce' else 0.9, bm_, 10, nocut=1)
        f.hide_render = t.hide_render = True; PROTO[key] = (f.data, t.data)
    z = float(H(x, y)[0]) - 0.15
    for me in PROTO[key]:
        o = bpy.data.objects.new('tree', me); col.objects.link(o); o.location = (x, y, z); o.scale = (h, h, h); o.rotation_euler = (0, 0, rot); o['nocut'] = 1
TREES = [('spruce', 21, 5, 21), ('spruce', 23, -3, 19), ('spruce', 22, -14, 22), ('spruce', 14, -21, 18), ('spruce', 6, -25, 20),
         ('spruce', -4, -23, 17), ('spruce', 10, 17, 19), ('spruce', 2, 20, 22), ('spruce', -8, 19, 18), ('spruce', 27, 10, 20), ('spruce', 28, -8, 22),
         ('birch', 12.4, -2.4, 16), ('birch', 17, 12, 17), ('birch', 11, -15, 16), ('birch', -11, -19, 15), ('birch', 13.5, 6.5, 15),
         ('pine', 24, 6, 20), ('pine', 26, -17, 21), ('pine', 8, -27, 20), ('pine', 16, 18, 19)]
TREES += [('spruce', 36 + 4 * (j % 2), -35 + 6.5 * j, 19 + (j * 7) % 5) for j in range(12)] + [('spruce', 44 - 3 * (j % 2), -32 + 6.5 * j, 22 + (j * 3) % 4) for j in range(11)]
for i, (k, x, y, h) in enumerate(TREES):
    if SEC and (x < 9.5 or x > 30): continue
    tree(k, x, y, h, i * 1.3, i % 2)
if not SEC:
    blob(-1.6, 7.4, 0.3, 2.0, 1.5, 7000, 0.045, 'shrub', 31); blob(-1.6, 7.4, 0.5, 2.0, 1.5, 800, 0.04, 'rhodo', 32)
    blob(-0.5, -5.6 + DY, -0.2, 0.9, 0.7, 1200, 0.035, 'shrub', 33); blob(-0.5, -9.4 + DY, -0.2, 1.0, 0.8, 1400, 0.035, 'shrub', 34)
    blob(10.2, -1.5, -0.1, 1.4, 0.9, 1500, 0.04, 'shrub', 35)

# ---------------- section cut ----------------
if SEC:
    for o in list(bpy.data.objects):
        if o.type != 'MESH' or o.get('nocut'): continue
        me = o.data; bm = bmesh.new(); bm.from_mesh(me); xs = [v.co.x for v in bm.verts]
        if max(xs) <= XC + 1e-4:
            bm.free(); bpy.data.objects.remove(o); continue
        if min(xs) < XC - 1e-4:
            r = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(XC, 0, 0), plane_no=(-1, 0, 0), clear_outer=True)
            edges = [e for e in r['geom_cut'] if isinstance(e, bmesh.types.BMEdge)]
            cap = o.get('cap', 'poche')
            if edges and cap != 'none':
                if cap == 'poche': me.materials.append(MAT['poche']); mi = len(me.materials) - 1
                else: mi = 0
                fl = bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=True, edges=edges)
                for g in fl['geom']:
                    if isinstance(g, bmesh.types.BMFace): g.material_index = mi
            bm.to_mesh(me)
        bm.free()

# ---------------- light, camera, render ----------------
w = bpy.data.worlds.new('W'); scene.world = w; w.use_nodes = True; nt = w.node_tree
sky = nt.nodes.new('ShaderNodeTexSky'); sky.sky_type = 'MULTIPLE_SCATTERING'; sky.sun_disc = False
sky.sun_elevation = math.radians(24); sky.sun_rotation = math.radians(249); sky.aerosol_density = 2.0
bg = nt.nodes['Background']; nt.links.new(sky.outputs[0], bg.inputs[0]); bg.inputs[1].default_value = 0.18 if not SEC else 0.24
sd = Vector((-0.853, -0.327, 0.407)) if not SEC else Vector((-0.70, -0.22, 0.68))
sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN')); col.objects.link(sun)
sun.data.energy = 4.2 if not SEC else 1.7; sun.data.color = (1.0, 0.88, 0.74) if not SEC else (1.0, 0.95, 0.88)
sun.data.angle = math.radians(5 if not SEC else 14); sun.rotation_euler = (-sd).to_track_quat('-Z', 'Y').to_euler()
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); col.objects.link(cam); scene.camera = cam
if SEC:
    cam.data.type = 'ORTHO'; cam.data.ortho_scale = 23.5; cam.location = (-25, -2.65, 3.9)
    cam.rotation_euler = (math.radians(90), 0, math.radians(-90)); RX, RY = (2200, 1180) if FINAL else (1000, 536)
elif MODE == 'yard':
    cam.data.lens = 22; cam.location = (-1.6, -2.3, 1.45)
    cam.rotation_euler = (Vector((8.6, -3.1, 1.2)) - cam.location).to_track_quat('-Z', 'Y').to_euler(); RX, RY = (2000, 1250) if FINAL else (800, 500)
else:
    cam.data.lens = 36; cam.location = (-22, 1.2, 5.6)
    cam.rotation_euler = (Vector((3.7, -2.57 + DY / 2, 3.1)) - cam.location).to_track_quat('-Z', 'Y').to_euler(); RX, RY = (2000, 1250) if FINAL else (800, 500)
cam.data.clip_end = 400
scene.render.engine = 'CYCLES'; c = scene.cycles; c.device = 'CPU'
c.samples = 140 if FINAL else 28; c.use_adaptive_sampling = True; c.adaptive_threshold = 0.02 if FINAL else 0.08
c.use_denoising = True; c.denoiser = 'OPENIMAGEDENOISE'
c.max_bounces = 6; c.diffuse_bounces = 3; c.glossy_bounces = 3; c.transmission_bounces = 6; c.transparent_max_bounces = 24
c.caustics_reflective = False; c.caustics_refractive = False; c.sample_clamp_indirect = 6
scene.view_settings.view_transform = 'AgX'; scene.view_settings.look = 'AgX - Medium High Contrast'
scene.render.resolution_x, scene.render.resolution_y = RX, RY
scene.render.image_settings.file_format = 'JPEG'; scene.render.image_settings.quality = 92
scene.render.filepath = f"{OUT}/{MODE}_{QUAL}_gap55.jpg"
bpy.ops.render.render(write_still=True)
print("DONE", scene.render.filepath)
