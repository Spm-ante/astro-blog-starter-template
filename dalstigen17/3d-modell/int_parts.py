##== PRE
def owall(axis, a, b, t, z0, z1, m, ops=()):
    """Wall with real openings; ops = (u0, u1, za, zb), stacked openings allowed."""
    cuts = sorted(set([a, b] + [min(max(o[0], a), b) for o in ops] + [min(max(o[1], a), b) for o in ops]))
    def seg(u0, u1, za, zb):
        if zb - za > 1e-4: (box((u0, u1), t, (za, zb), m) if axis == 'x' else box(t, (u0, u1), (za, zb), m))
    for u0, u1 in zip(cuts[:-1], cuts[1:]):
        if u1 - u0 < 1e-4: continue
        um = (u0 + u1) / 2; cz = z0
        for za, zb in sorted((max(o[2], z0), min(o[3], z1)) for o in ops if o[0] < um < o[1]):
            seg(u0, u1, cz, za); cz = max(cz, zb)
        seg(u0, u1, cz, z1)

##== KITCHEN
# ---------------- existing house interior: open kitchen with island ----------------
pbr('kgreen', (86, 104, 88), 0.55); pbr('hob', (18, 18, 20), 0.08); MAT['pane'] = MAT['glass']
window('y', 5.5, 1, 2.04, 2.76, 1.2, 1.8, sash='white', bars=1); window('y', 5.5, 1, 6.69, 7.46, 1.05, 2.0, sash='white', bars=2)
window('x', 8.9, 1, 1.61, 2.61, 0.85, 2.0, sash='white', bars=2); window('x', 8.9, 1, 2.72, 3.78, 0.85, 2.0, sash='white', bars=2)
box((4.14, 4.92), (5.4, 5.44), (0, 2.0), 'white')
owall('x', wt, 8.9 - wt, (wt, wt + 0.012), 0, 2.3, 'wint', [(1.26, 2.14, 0.85, 2.0), (4.9, 7.6, 0.0, 2.05)])
owall('x', wt, 8.9 - wt, (5.5 - wt - 0.012, 5.5 - wt), 0, 2.3, 'wint', [(2.04, 2.76, 1.2, 1.8), (4.14, 4.92, 0.0, 2.0), (6.69, 7.46, 1.05, 2.0)])
owall('y', wt, 5.5 - wt, (8.9 - wt - 0.012, 8.9 - wt), 0, 2.3, 'wint', [(1.61, 2.61, 0.85, 2.0), (2.72, 3.78, 0.85, 2.0)])
box((wt, wt + 0.012), (wt, 5.5 - wt), (0, 2.3), 'wint')
owall('y', wt, 5.5 - wt, (2.88, 2.98), 0, 2.3, 'wint', [(2.22, 3.0, 0, 2.0), (4.5, 5.28, 0, 2.0)]); box((wt, 2.88), (3.34, 3.44), (0, 2.3), 'wint')
for px in (4.9, 6.22, 7.54): box((px, px + 0.06), (0.04, 0.13), (0, 2.05), 'green')
box((4.9, 7.6), (0.04, 0.13), (1.99, 2.05), 'green'); box((6.25, 7.57), (0.08, 0.09), (0.02, 1.99), 'glass')
box((5.4, 8.13), (4.75, 5.31), (0, 0.1), 'skirt'); box((5.4, 8.13), (4.73, 5.31), (0.1, 0.88), 'kgreen')
box((5.38, 8.13), (4.7, 5.31), (0.88, 0.92), 'oak'); box((6.85, 7.45), (4.85, 5.21), (0.84, 0.921), 'zinc')
box((7.12, 7.16), (5.15, 5.19), (0.92, 1.25), 'zinc'); box((5.4, 8.13), (5.3, 5.318), (0.92, 1.5), 'bathtile')
for zs in (1.55, 1.95): box((5.4, 6.6), (5.07, 5.318), (zs, zs + 0.035), 'oak')
box((8.13, 8.718), (4.03, 5.318), (0, 2.25), 'kgreen'); box((8.12, 8.13), (4.67, 4.69), (0.05, 2.2), 'skirt')
box((5.65, 7.75), (2.6, 3.5), (0, 0.08), 'skirt'); box((5.6, 7.8), (2.55, 3.55), (0.08, 0.88), 'kgreen')
box((5.58, 7.82), (2.25, 3.57), (0.88, 0.92), 'oak'); box((6.3, 6.9), (3.0, 3.45), (0.92, 0.926), 'hob')
for sx in (6.0, 6.7, 7.4):
    cone(sx, 2.28, 0.62, 0.18, 0.18, 0.04, 'oak')
    for lx, ly in ((-0.12, -0.12), (0.12, -0.12), (-0.12, 0.12), (0.12, 0.12)): box((sx + lx - 0.012, sx + lx + 0.012), (2.28 + ly - 0.012, 2.28 + ly + 0.012), (0, 0.62), 'green')
for px in (6.25, 7.15): box((px - 0.004, px + 0.004), (3.046, 3.054), (1.72, 2.3), 'skirt'); cone(px, 3.05, 1.55, 0.17, 0.04, 0.18, 'lamp')
box((8.33, 8.718), (0.35, 2.4), (0, 0.85), 'oak')
for ax in (3.25, 4.25): box((ax, ax + 0.7), (0.5, 1.2), (0.1, 0.42), 'sofa'); box((ax, ax + 0.7), (0.5, 0.65), (0.42, 0.85), 'sofa')
cone(4.1, 1.75, 0, 0.03, 0.03, 0.5, 'oak'); cone(4.1, 1.75, 0.5, 0.28, 0.28, 0.03, 'oak'); box((2.98, 4.0), (4.73, 5.318), (0, 2.1), 'white')

##== NEWHOUSE
# ---------------- new house, alternative 2 with sheet 1B upper floor (absolute coords) ----------------
NX0, NX1, NYA, NYB = 0.8, 9.4, -12.3, -5.5; IX0, IX1, IYA, IYB = 1.1, 9.1, -12.0, -5.8; RY = -8.9; FL2 = 2.88
def ru(y): return 7.225 - abs(y - RY) * T32
def prof(y0, y1, zb):
    pts = [(y0, zb), (y1, zb), (y1, ru(y1))]
    if y0 < RY < y1: pts.append((RY, ru(RY)))
    return pts + [(y0, ru(y0))]
OPN = [(1.8, 3.4, 0.0, 2.1), (6.0, 7.2, 0.0, 2.1), (2.05, 3.15, 3.73, 5.03), (4.8, 5.8, 3.73, 5.03)]
OPS = [(2.3, 4.3, 0.5, 2.2), (7.5, 8.1, 1.1, 2.1), (2.5, 3.7, 3.73, 5.03)]
OPW = [(-11.2, -10.0, 0.7, 2.2), (-7.8, -6.6, 0.7, 2.2), (-11.15, -10.05, 3.73, 5.03), (-7.75, -6.65, 3.73, 5.03)]
OPE = [(-11.4, -10.5, 1.1, 2.1), (-11.05, -10.4, 3.95, 4.75), (-8.5, -7.5, 1.6, 3.5)]
owall('x', NX0, NX1, (NYB - 0.3, NYB), -0.02, 5.25, 'ochre', OPN); owall('x', NX0, NX1, (NYA, NYA + 0.3), -0.02, 5.25, 'ochre', OPS)
owall('y', NYA + 0.3, NYB - 0.3, (NX0, NX0 + 0.3), -0.02, 5.25, 'ochre', OPW); owall('y', NYA + 0.3, NYB - 0.3, (NX1 - 0.3, NX1), -0.02, 5.25, 'ochre', OPE)
owall('x', IX0, IX1, (IYB - 0.012, IYB), 0, 5.3, 'wint', OPN); owall('x', IX0, IX1, (IYA, IYA + 0.012), 0, 5.3, 'wint', OPS)
owall('y', IYA, IYB, (IX0, IX0 + 0.012), 0, 5.3, 'wint', OPW); owall('y', IYA, IYB, (IX1 - 0.012, IX1), 0, 5.3, 'wint', OPE)
for xa in (NX0, NX1 - 0.3): ext([(NYA, 5.25), (NYB, 5.25), (RY, 5.25 + 3.4 * T32)], xa, xa + 0.3, 'ochre')
ext([(IYA, 5.25), (IYB, 5.25), (IYB, ru(IYB)), (RY, ru(RY)), (IYA, ru(IYA))], IX0, IX0 + 0.012, 'wint')
roof(NYA, NYB, 5.63, T32, 0.45, NX0 - 0.4, NX1 + 0.4, 'tile_new', os=0.45, on=0.45)
for xa in (NX0 - 0.44, NX1 + 0.4): roof(NYA, NYB, 5.66, T32, 0.49, xa, xa + 0.04, 'trim', os=0.47, on=0.47)
for yg in (NYB + 0.45, NYA - 0.55): box((NX0 - 0.4, NX1 + 0.4), (yg, yg + 0.1), (5.25, 5.34), 'zinc')
for s_ in (-1, 1): ext([(RY, ru(RY) - 0.004), (RY + s_ * 3.1, ru(RY + s_ * 3.1) - 0.004), (RY + s_ * 3.1, ru(RY + s_ * 3.1) - 0.016), (RY, ru(RY) - 0.016)], IX0, 7.25, 'wint')
box((IX0, 7.25), (RY - 0.09, RY + 0.09), (ru(RY) - 0.33, ru(RY) - 0.01), 'pine'); box((NX0, NX1), (NYA, NYB), (-0.64, -0.02), 'concrete')
for u0, u1, z0, z1 in OPN:
    if z0 > 0.1: window('y', NYB, 1, u0, u1, z0, z1, trim='trim')
window('y', NYB, 1, 1.8, 3.4, 0.0, 2.1, trim='trim', bars=0, door=True)
for u0, u1, z0, z1 in OPS: window('y', NYA, -1, u0, u1, z0, z1, trim='trim', bars=0 if u1 - u0 > 1.5 else 2)
for u0, u1, z0, z1 in OPW: window('x', NX0, -1, u0, u1, z0, z1, trim='trim')
for u0, u1, z0, z1 in OPE: window('x', NX1, 1, u0, u1, z0, z1, trim='trim', mull=(u1 - u0) > 0.8)
# floors, slabs, flat ceiling over hall and shower
box((IX0, IX1), (IYA, IYB), (-0.015, 0), 'oak'); box((IX0, IX1), (IYA, IYB), (-0.64, -0.015), 'concrete')
for xa, xb, yb_ in ((IX0, 7.25, IYB), (7.25, 8.2, -6.7), (8.2, IX1, -9.2)):
    box((xa, xb), (IYA, yb_), (2.5, FL2 - 0.015), 'wint'); box((xa, xb), (IYA, yb_), (FL2 - 0.015, FL2), 'oak')
box((5.95, IX1), (IYA, -8.4), (5.28, 5.33), 'wint'); box((7.25, IX1), (-8.4, IYB), (5.28, 5.33), 'wint'); ext(prof(-9.5, -8.4, 5.28), 5.85, 5.95, 'wint')
# ground floor: laundry, stair, living room
owall('x', 5.95, IX1, (-9.75, -9.65), 0, 2.5, 'wint', [(7.1, 7.9, 0, 2.05)]); box((5.95, 6.05), (IYA, -9.75), (0, 2.5), 'wint')
for i in range(1, 5):
    x0_ = 7.2 + 0.25 * (i - 1); box((x0_, x0_ + 0.25), (-6.7, IYB), (0, 0.18 * i - 0.03), 'white'); box((x0_ - 0.02, x0_ + 0.25), (-6.7, IYB), (0.18 * i - 0.03, 0.18 * i), 'oak')
box((8.2, IX1), (-6.7, IYB), (0, 0.87), 'white'); box((8.2, IX1), (-6.7, IYB), (0.87, 0.9), 'oak')
for j in range(1, 11):
    h = 0.9 + 0.18 * j; y1_ = -6.7 - 0.25 * (j - 1)
    box((8.2, IX1), (y1_ - 0.25, y1_), (h - 0.2, h - 0.03), 'white'); box((8.2, IX1), (y1_ - 0.25, y1_ + 0.02), (h - 0.03, h), 'oak')
for k in range(14):
    y_ = -6.75 - 0.18 * k; zb_ = 0.9 + 0.792 * (-6.7 - y_); box((8.185, 8.205), (y_ - 0.01, y_ + 0.01), (zb_, min(zb_ + 0.9, 2.49)), 'white')
ext([(-6.7, 1.8), (-7.58, 2.5), (-7.58, 2.48), (-6.7, 1.78)], 8.17, 8.22, 'oak')
box((8.19, 8.21), (-9.2, -6.7), (FL2, FL2 + 0.9), 'glass'); box((8.18, 8.22), (-9.2, -6.7), (FL2 + 0.9, FL2 + 0.94), 'oak')
box((7.25, 8.2), (-6.71, -6.69), (FL2, FL2 + 0.9), 'glass'); box((7.25, 8.2), (-6.72, -6.68), (FL2 + 0.9, FL2 + 0.94), 'oak')
box((1.4, 4.0), (-11.0, -8.6), (0, 0.012), 'fabric')
box((1.5, 3.9), (-11.95, -11.05), (0.1, 0.44), 'sofa'); box((1.5, 3.9), (-11.95, -11.75), (0.44, 0.85), 'sofa')
for ax in (1.5, 3.7): box((ax, ax + 0.2), (-11.95, -11.05), (0.1, 0.62), 'sofa')
box((2.2, 3.2), (-10.55, -9.95), (0.38, 0.42), 'oak')
for lx, ly in ((2.25, -10.5), (3.15, -10.5), (2.25, -10.0), (3.15, -10.0)): box((lx - 0.02, lx + 0.02), (ly - 0.02, ly + 0.02), (0, 0.38), 'oak')
for cx_ in (1.55, 3.85): box((cx_ - 0.38, cx_ + 0.38), (-9.68, -8.92), (0.1, 0.44), 'sofa'); box((cx_ - 0.38, cx_ + 0.38), (-9.08, -8.92), (0.44, 0.85), 'sofa')
box((5.6, 5.95), (-11.9, -10.0), (0, 2.0), 'oak')
# upper floor, sheet 1B: walls up to the roof where the ceiling is open to the ridge
def pw_y(x0, x1, y0, y1, doors=()):
    cur = y0
    for d0, d1 in doors: ext(prof(cur, d0, FL2), x0, x1, 'wint'); ext(prof(d0, d1, FL2 + 2.05), x0, x1, 'wint'); cur = d1
    ext(prof(cur, y1, FL2), x0, x1, 'wint')
def pw_x(x0, x1, y0, y1, doors=()):
    cur = x0
    for d0, d1 in doors: ext(prof(y0, y1, FL2), cur, d0, 'wint'); ext(prof(y0, y1, FL2 + 2.05), d0, d1, 'wint'); cur = d1
    ext(prof(y0, y1, FL2), cur, x1, 'wint')
pw_x(IX0, 5.95, -9.5, -9.4, [(4.1, 4.9)]); pw_y(5.85, 5.95, IYA, -9.5); pw_y(3.35, 3.45, -9.4, IYB, [(-9.35, -8.55)])
pw_x(3.45, 7.25, -8.4, -8.3, [(4.9, 5.7)]); pw_y(7.15, 7.25, -8.3, IYB)
owall('x', 5.95, IX1, (-10.45, -10.35), FL2, 5.28, 'wint', [(7.4, 8.1, FL2, FL2 + 2.05)]); box((5.95, IX1), (IYA, -10.45), (FL2, FL2 + 0.005), 'bathtile')
# sleeping loft (hems) in children's room 1
box((IX0, 3.35), (-9.4, -7.7), (5.08, 5.28), 'pine'); box((1.15, 3.3), (-9.35, -8.1), (5.28, 5.42), 'fabric')
for k in range(12): xb_ = 1.15 + 0.19 * k; box((xb_, xb_ + 0.025), (-7.72, -7.69), (5.28, 5.9), 'white')
box((IX0, 3.35), (-7.73, -7.68), (5.88, 5.92), 'oak')
for xr in (2.15, 2.5): box((xr, xr + 0.04), (-7.66, -7.62), (FL2, 5.95), 'oak')
for k in range(1, 9): box((2.15, 2.54), (-7.655, -7.625), (FL2 + 0.3 * k, FL2 + 0.3 * k + 0.03), 'oak')
# furniture upper floor
def desk(x0, x1, y0, y1):
    box((x0, x1), (y0, y1), (FL2 + 0.72, FL2 + 0.75), 'oak')
    for lx in (x0 + 0.03, x1 - 0.06):
        for ly in (y0 + 0.03, y1 - 0.06): box((lx, lx + 0.03), (ly, ly + 0.03), (FL2, FL2 + 0.72), 'oak')
box((1.15, 3.15), (-11.55, -9.95), (FL2, FL2 + 0.45), 'fabric'); box((1.12, 1.2), (-11.6, -9.9), (FL2, FL2 + 1.1), 'oak')
for py0, py1 in ((-11.45, -10.8), (-10.7, -10.05)): box((1.22, 1.55), (py0, py1), (FL2 + 0.45, FL2 + 0.58), 'white')
for ny0, ny1 in ((-11.95, -11.6), (-9.9, -9.55)): box((1.15, 1.6), (ny0, ny1), (FL2, FL2 + 0.5), 'oak')
box((5.25, 5.85), (IYA, -9.6), (FL2, FL2 + 2.2), 'white')
box((1.15, 2.05), (-9.35, -7.35), (FL2, FL2 + 0.45), 'fabric'); desk(2.2, 3.3, -6.4, -5.82); box((2.75, 3.35), (-8.4, -7.2), (FL2, FL2 + 2.1), 'white')
box((3.5, 4.4), (-8.25, -6.25), (FL2, FL2 + 0.45), 'fabric'); desk(4.8, 6.0, -6.4, -5.82); box((6.55, 7.15), (-8.25, -7.05), (FL2, FL2 + 2.1), 'white')

##== RENDER
# ---------------- interior lighting, cameras, render ----------------
import json
w = bpy.data.worlds.new('W'); scene.world = w; w.use_nodes = True; nt = w.node_tree
sky = nt.nodes.new('ShaderNodeTexSky'); sky.sky_type = 'MULTIPLE_SCATTERING'; sky.sun_disc = False
sky.sun_elevation = math.radians(30); sky.sun_rotation = math.radians(197); sky.aerosol_density = 1.5
bg = nt.nodes['Background']; nt.links.new(sky.outputs[0], bg.inputs[0]); bg.inputs[1].default_value = 0.6
sd = Vector((-0.8, -0.25, 0.5)).normalized()
sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN')); col.objects.link(sun)
sun.data.energy = 3.2; sun.data.color = (1.0, 0.93, 0.84); sun.data.angle = math.radians(3); sun.rotation_euler = (-sd).to_track_quat('-Z', 'Y').to_euler()
for (x, y, z, sx, sy, p) in ((6.6, 2.9, 2.22, 2.4, 1.6, 90), (3.3, -9.0, 2.42, 3.0, 2.4, 120), (3.4, -10.75, 5.8, 3.0, 1.6, 60), (2.2, -6.8, 5.2, 1.4, 1.4, 40), (5.3, -7.0, 5.4, 2.0, 1.4, 50), (6.2, -2.75, 2.6, 3.0, 3.0, 160)):
    L = bpy.data.lights.new('a', 'AREA'); L.shape = 'RECTANGLE'; L.size = sx; L.size_y = sy; L.energy = p; L.color = (1.0, 0.96, 0.9)
    o = bpy.data.objects.new('a', L); col.objects.link(o); o.location = (x, y, z)
VIEWS = {'kok': ((3.35, 2.35, 1.6), (8.73, 2.9), 0.0, False), 'vinter': ((5.5, -4.95, 1.6), (8.4, -0.3), 0.12, False),
         'vardag': ((6.9, -7.05, 1.6), (1.1, -9.7), 0.0, False), 'sovrum': ((4.6, -9.75, FL2 + 1.6), (1.1, -11.5), 0.05, True),
         'barn1': ((3.15, -6.55, FL2 + 1.6), (1.3, -9.0), 0.05, True), 'barn2': ((5.3, -8.1, FL2 + 1.6), (4.3, -5.8), 0.05, True),
         'gard': ((-1.4, -2.75, 1.45), (8.0, -2.9), 0.1, False)}
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); col.objects.link(cam); scene.camera = cam
cam.data.lens = 24; cam.data.sensor_fit = 'HORIZONTAL'; cam.data.sensor_width = 36; cam.data.clip_start = 0.05; cam.data.clip_end = 300
scene.render.engine = 'CYCLES'; c = scene.cycles; c.device = 'CPU'
c.samples = 96 if FINAL else 24; c.use_adaptive_sampling = True; c.adaptive_threshold = 0.03 if FINAL else 0.1
c.use_denoising = True; c.denoiser = 'OPENIMAGEDENOISE'
c.max_bounces = 8; c.diffuse_bounces = 4; c.glossy_bounces = 3; c.transmission_bounces = 8; c.transparent_max_bounces = 24
c.caustics_reflective = False; c.caustics_refractive = False; c.sample_clamp_indirect = 8
scene.view_settings.view_transform = 'AgX'; scene.view_settings.look = 'AgX - Medium High Contrast'; scene.view_settings.exposure = 0.9
scene.render.image_settings.file_format = 'JPEG'; scene.render.image_settings.quality = 92
info = {}
for n in MODE.split(','):
    (cx, cy, cz), (tx, ty), sh, portrait = VIEWS[n]
    cam.data.sensor_fit = 'VERTICAL' if portrait else 'HORIZONTAL'; cam.data.sensor_width = 36; cam.data.sensor_height = 36
    scene.render.resolution_x, scene.render.resolution_y = ((800, 1200) if portrait else (1200, 800)) if FINAL else ((300, 450) if portrait else (450, 300))
    cam.location = (cx, cy, cz); cam.rotation_euler = (math.radians(90), 0, math.atan2(-(tx - cx), (ty - cy)))
    cam.data.shift_x = 0.0; cam.data.shift_y = sh
    for o in scene.objects:
        if o.type == 'MESH' and not o.get('nocut') is None: pass
        if o.type == 'MESH' and o.name.startswith(('blob', 'c')) and len(o.data.vertices) > 0:
            cen = sum((Vector(vv.co) for vv in o.data.vertices[:200]), Vector()) / min(len(o.data.vertices), 200)
            o.hide_render = o.name.startswith('blob') or (Vector((cen.x - cx, cen.y - cy)).length < 1.4 and abs(cen.z - cz) < 2.5)
    scene.render.filepath = f"{OUT}/int_{n}_{QUAL}.jpg"; bpy.ops.render.render(write_still=True); print("DONE", n)
    info[n] = {"loc": [cx, cy, cz], "target": [tx, ty], "yaw": cam.rotation_euler[2], "lens": 24, "sensor": 36, "portrait": portrait, "shift_y": sh, "res": [scene.render.resolution_x, scene.render.resolution_y]}
json.dump(info, open(f"{OUT}/int_views_{QUAL}.json", "w"), indent=1)
