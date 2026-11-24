# Edge-based distortion check of AI-refined images against their 3D underlay.
# Fits scale/shift of the underlay's structural lines onto the candidate's edges (truncated chamfer),
# then reports what remains: local displacement (p90 of line-point distances) and anisotropic stretch.
# usage: python align2.py <underlay.jpg> <out_prefix> <candidate1> [...]
import sys, json, math
import cv2, numpy as np

und, outp, cands = sys.argv[1], sys.argv[2], sys.argv[3:]
U = cv2.imread(und); H, W = U.shape[:2]
Ue = cv2.Canny(cv2.GaussianBlur(cv2.cvtColor(U, cv2.COLOR_BGR2GRAY), (5, 5), 1.5), 40, 120)
L = cv2.HoughLinesP(Ue, 1, np.pi / 360, 60, minLineLength=int(0.07 * W), maxLineGap=6)
P = []
for x1, y1, x2, y2 in (np.asarray(L).reshape(-1, 4).astype(float) if L is not None else []):
    n = max(2, int(math.hypot(x2 - x1, y2 - y1) / 5))
    P += [(x1 + (x2 - x1) * t, y1 + (y2 - y1) * t) for t in np.linspace(0, 1, n)]
P = np.array(P, np.float32); c = np.array([W / 2, H / 2], np.float32); T = 40.0

def cost_vec(D, sx, sy, tx, ty, full=False):
    q = (P - c) * np.array([sx, sy], np.float32) + c + np.array([tx, ty], np.float32)
    ok = (q[:, 0] >= 0) & (q[:, 0] < W - 1) & (q[:, 1] >= 0) & (q[:, 1] < H - 1)
    d = np.full(len(P), T, np.float32); d[ok] = np.minimum(D[q[ok, 1].astype(int), q[ok, 0].astype(int)], T)
    return d if full else float(d.mean())

rep, tiles = [], []
for cp in cands:
    C0 = cv2.imread(cp); ch, cw = C0.shape[:2]
    C = cv2.resize(C0, (W, H), interpolation=cv2.INTER_AREA)
    Ce = cv2.Canny(cv2.GaussianBlur(cv2.cvtColor(C, cv2.COLOR_BGR2GRAY), (7, 7), 2.0), 60, 160)
    D = cv2.distanceTransform(255 - Ce, cv2.DIST_L2, 3)
    d0 = cost_vec(D, 1, 1, 0, 0, True)
    best = (1e9, 1, 0, 0)
    for s in np.arange(0.94, 1.061, 0.005):
        for tx in range(-40, 41, 4):
            for ty in range(-40, 41, 4):
                v = cost_vec(D, s, s, tx, ty)
                if v < best[0]: best = (v, s, tx, ty)
    _, s, tx, ty = best; tx, ty = float(tx), float(ty)
    for step_s, step_t in ((0.005, 2.0), (0.002, 1.0), (0.001, 0.5)):
        improved = True
        while improved:
            improved = False
            for ds, dt_x, dt_y in ((step_s, 0, 0), (-step_s, 0, 0), (0, step_t, 0), (0, -step_t, 0), (0, 0, step_t), (0, 0, -step_t)):
                if cost_vec(D, s + ds, s + ds, tx + dt_x, ty + dt_y) < cost_vec(D, s, s, tx, ty) - 1e-4: s, tx, ty = s + ds, tx + dt_x, ty + dt_y; improved = True
    sx, sy = s, s
    for _ in range(40):
        moved = False
        for a, b in ((0.002, 0), (-0.002, 0), (0, 0.002), (0, -0.002)):
            if cost_vec(D, sx + a, sy + b, tx, ty) < cost_vec(D, sx, sy, tx, ty) - 1e-4: sx, sy = sx + a, sy + b; moved = True
        if not moved: break
    du = cost_vec(D, s, s, tx, ty, True)
    r = {"file": cp.split('/')[-1], "size": [cw, ch], "aspect_err_pct": round(abs((cw / ch) / (W / H) - 1) * 100, 2),
         "raw_p90_pct": round(float(np.percentile(d0, 90)) / W * 100, 2), "fit_scale": round(s, 3), "fit_shift_px": [round(tx, 1), round(ty, 1)],
         "stretch_pct": round(abs(sx / sy - 1) * 100, 2), "resid_median_pct": round(float(np.median(du)) / W * 100, 2),
         "resid_p90_pct": round(float(np.percentile(du, 90)) / W * 100, 2), "lines_pts": int(len(P))}
    r["score_pct"] = round(max(r["resid_p90_pct"], r["stretch_pct"], abs(s - 1) * 100 / 4), 2)
    rep.append(r)
    M = np.float32([[s, 0, (1 - s) * c[0] + tx], [0, s, (1 - s) * c[1] + ty]])
    Cw = cv2.warpAffine(C, cv2.invertAffineTransform(M), (W, H), borderValue=(255, 255, 255))
    ov = cv2.cvtColor(cv2.cvtColor(Cw, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR) // 2 + 100; ov[Ue > 0] = (30, 30, 235)
    lab = "%s  resid p90 %.1f%%" % (r["file"][:8], r["resid_p90_pct"])
    cv2.putText(ov, lab, (14, 44), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 0), 5); cv2.putText(ov, lab, (14, 44), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (255, 255, 255), 2)
    tiles.append(cv2.resize(ov, (W // 2, H // 2)))
rows = [np.hstack(tiles[i:i + 2] + ([np.full_like(tiles[0], 255)] if len(tiles[i:i + 2]) == 1 else [])) for i in range(0, len(tiles), 2)]
cv2.imwrite(outp + "_overlay.jpg", np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 85])
json.dump(rep, open(outp + "_report.json", "w"), indent=1)
for r in rep: print(json.dumps(r))
