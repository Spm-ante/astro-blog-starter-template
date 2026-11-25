# Draw true-to-model dimension lines on an AI-refined room image.
# 3D points are projected through the Blender camera that made the underlay, then mapped into the AI image
# with the similarity fit measured by align2.py (scale s and shift t about the underlay centre).
# usage: python annotate.py <room> <views.json> <ai_image> <fit_scale> <tx> <ty> <out.jpg> [--check underlay.jpg]
import sys, json, math
from PIL import Image, ImageDraw, ImageFont

room, vj, ai, s, tx, ty, out = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]), float(sys.argv[5]), float(sys.argv[6]), sys.argv[7]
check = sys.argv[sys.argv.index("--check") + 1] if "--check" in sys.argv else None
V = json.load(open(vj))[room]; (cx, cy, cz), yaw, sh = V["loc"], V["yaw"], V["shift_y"]; W, H = V["res"]
FL2, T32, RY = 2.88, math.tan(math.radians(32)), -8.9
def ru(y): return 7.225 - abs(y - RY) * T32
R = (math.cos(yaw), math.sin(yaw), 0.0); UP = (0.0, 0.0, 1.0); FW = (-math.sin(yaw), math.cos(yaw), 0.0)
big = max(W, H); k = 24 / 36

def proj(p):  # 3D world point -> underlay pixel
    d = (p[0] - cx, p[1] - cy, p[2] - cz)
    xc, yc, zc = (sum(a * b for a, b in zip(d, R)), d[2], sum(a * b for a, b in zip(d, FW)))
    return (W / 2 + k * xc / zc * big, H / 2 - (k * yc / zc - sh) * big)

DIMS = {
 "kok": [((5.6, 3.57, 0.93), (7.8, 3.57, 0.93), "Köksö 2,2 m"), ((6.1, 3.57, 0.93), (6.1, 4.7, 0.93), "1,2 m"),
         ((8.71, 3.9, 0.0), (8.71, 3.9, 2.3), "Takhöjd 2,3 m"), ((8.71, 0.17, 0.02), (8.71, 5.33, 0.02), "5,2 m")],
 "vinter": [((8.1, -3.65, 0.76), (8.1, -1.85, 0.76), "Bord 1,8 m"), ((8.66, -2.75, 0.0), (8.66, -2.75, 3.157), "3,2 m i nock"),
            ((8.66, -0.06, 0.0), (8.66, -0.06, 2.42), "2,4 m")],
 "vardag": [((1.12, -12.0, 0.02), (1.12, -5.8, 0.02), "6,2 m"), ((1.12, -11.98, 0.0), (1.12, -11.98, 2.5), "Takhöjd 2,5 m"),
            ((1.5, -11.0, 0.46), (3.9, -11.0, 0.46), "Soffa 2,4 m")],
 "sovrum": [((1.12, -12.0, FL2 + 0.02), (1.12, -9.5, FL2 + 0.02), "2,5 m"), ((1.12, -11.98, FL2), (1.12, -11.98, FL2 + 2.41), "2,4 m"),
            ((1.12, -10.0, FL2), (1.12, -10.0, ru(-10.0)), "ca 3,7 m"), ((1.16, -11.6, FL2 + 1.1), (1.16, -9.9, FL2 + 1.1), "Säng 1,6 m")],
 "barn1": [((2.05, -7.72, FL2), (2.05, -7.72, 5.08), "Hems 2,2 m upp"), ((1.6, -8.9, 5.28), (1.6, -8.9, ru(-8.9)), "1,9 m över hemsen"),
           ((1.12, -9.38, FL2 + 0.02), (1.12, -5.82, FL2 + 0.02), "3,6 m")],
 "barn2": [((3.47, -5.84, FL2 + 0.02), (7.15, -5.84, FL2 + 0.02), "3,7 m"), ((3.47, -5.82, FL2), (3.47, -5.82, FL2 + 2.41), "2,4 m"),
           ((4.8, -5.86, FL2 + 0.76), (6.0, -5.86, FL2 + 0.76), "Skrivbord 1,2 m")],
 "hall": [((8.2, -6.72, 0.9), (9.1, -6.72, 0.9), "Trappa 0,9 m")],
 "dusch": [((9.08, -12.0, FL2 + 1.0), (9.08, -10.45, FL2 + 1.0), "1,55 m")],
 "entre": [((3.09, 6.84, -0.05), (5.91, 6.84, -0.05), "Veranda 2,8 m"), ((5.86, 6.82, -0.05), (5.86, 6.82, 2.12), "Fri höjd 2,2 m")],
 "soder": [((0.8, -12.32, 0), (9.4, -12.32, 0), "8,6 m"), ((0.78, -12.3, 0), (0.78, -5.5, 0), "6,8 m"),
           ((0.78, -12.32, 0), (0.78, -12.32, 5.25), "5,25 m till takfot")],
 "gard": [((3.66, -0.02, 0.1), (3.66, -5.48, 0.1), "5,5 m mellan husen", 0.3), ((3.7, -2.75, 0.05), (3.7, -2.75, 3.157), "3,2 m i nock"),
          ((3.7, -0.06, 0.05), (3.7, -0.06, 2.42), "2,4 m")],
}
img = Image.open(check if check else ai).convert("RGB"); IW, IH = img.size
def to_img(p):
    u, v = proj(p)
    if check: return (u * IW / W, v * IH / H)
    u, v = (u - W / 2) * s + W / 2 + tx, (v - H / 2) * s + H / 2 + ty
    return (u * IW / W, v * IH / H)
d = ImageDraw.Draw(img); sc = IW / 1200
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(22 * sc))
for a, b, lab, *opt in DIMS[room]:
    f = opt[0] if opt else 0.5  # label position along the line
    A, B = to_img(a), to_img(b); L = math.hypot(B[0] - A[0], B[1] - A[1]) or 1
    nx, ny = -(B[1] - A[1]) / L, (B[0] - A[0]) / L; t = 10 * sc
    for w_, col in ((int(7 * sc), (20, 30, 26)), (int(3 * sc), (255, 255, 255))):
        d.line([A, B], fill=col, width=w_)
        for P in (A, B): d.line([(P[0] - nx * t, P[1] - ny * t), (P[0] + nx * t, P[1] + ny * t)], fill=col, width=w_)
    mx, my = A[0] + f * (B[0] - A[0]), A[1] + f * (B[1] - A[1]); bb = d.textbbox((0, 0), lab, font=font); tw, th = bb[2] - bb[0], bb[3] - bb[1]
    pad = 8 * sc; d.rounded_rectangle([mx - tw / 2 - pad, my - th / 2 - pad, mx + tw / 2 + pad, my + th / 2 + pad * 1.2], radius=6 * sc, fill=(31, 58, 44))
    d.text((mx - tw / 2, my - th / 2 - bb[1] + pad * 0.1), lab, font=font, fill=(255, 255, 255))
img.save(out, quality=90); print("saved", out, img.size)
