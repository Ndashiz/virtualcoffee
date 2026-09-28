"""Joint landmarks read off the full-res FinalBaseMesh from girth profiles
(exact plane sections), in three.js coords (Y up, face +Z), height H.
Used by pp_rig.py; `python landmarks2.py` prints them."""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import sectlib

def load(H=1.75):
    V, F = [], []
    for line in open(os.path.join(HERE, "FinalBaseMesh.obj")):
        if line.startswith("v "):
            p = line.split(); V.append([float(p[1]), float(p[2]), float(p[3])])
        elif line.startswith("f "):
            F.append([int(t.split("/")[0]) - 1 for t in line.split()[1:]])
    V = np.array(V)
    V[:, 1] -= V[:, 1].min(); V *= H / V[:, 1].max()
    V[:, 0] -= (V[:, 0].min() + V[:, 0].max()) / 2
    band = V[(V[:, 1] > .95) & (V[:, 1] < 1.15)]; V[:, 2] -= band[:, 2].mean()
    head = V[V[:, 1] > 1.58]
    if head[np.abs(head[:, 2]).argmax()][2] < 0: V[:, 0] *= -1; V[:, 2] *= -1
    F4 = []
    for f in F:
        if len(f) == 3: F4.append(f + [f[-1]])
        elif len(f) == 4: F4.append(f)
        else: F4 += [[f[0], f[i], f[i + 1], f[i + 1]] for i in range(1, len(f) - 1)]
    return V, F4

def plateau_min(xs, a, lo, hi, tol=1.0):
    m = (xs >= lo) & (xs <= hi) & np.isfinite(a)
    amin = a[m].min()
    return float(xs[m & (a <= amin + tol)].mean())

def fit_line(P):
    c = P.mean(0); d = np.linalg.svd(P - c)[2][0]
    return c, d / np.linalg.norm(d)

def measure(V, F4, H=1.75, PELVIS=.855):
    EA, FE = sectlib.build(V, F4)
    def sect(n, o, target, maxd):
        ls = sectlib.loops(V, EA, FE, float(n @ o), n, np.zeros(3))
        best = None
        for c in ls:
            d = np.linalg.norm(c.mean(0) - target)
            if d < maxd and (best is None or d < best[0]): best = (d, c)
        return None if best is None else best[1]
    def area(c, n):
        u = np.cross(n, [0, 0, 1.]); u /= np.linalg.norm(u); v = np.cross(n, u)
        q = np.c_[(c - c.mean(0)) @ u, (c - c.mean(0)) @ v]
        return sectlib.poly_area(q) * 1e4          # cm2
    LM = {}
    # ---------------- arm (right side, mirrored) ----------------
    def clusters_x(y0, y1):
        b = V[(V[:, 1] >= y0) & (V[:, 1] < y1)]
        xs = np.sort(b[:, 0]); out, s0 = [], xs[0]
        for i in range(1, len(xs)):
            if xs[i] - xs[i - 1] > .04: out.append((s0, xs[i - 1])); s0 = xs[i]
        out.append((s0, xs[-1])); return out
    pts = []
    for y0 in np.arange(.80, 1.30, .02):
        cl = clusters_x(y0, y0 + .02)
        if len(cl) >= 3:
            seg = cl[-1]
            b = V[(V[:, 1] >= y0) & (V[:, 1] < y0 + .02) & (V[:, 0] >= seg[0] - 1e-6) & (V[:, 0] <= seg[1] + 1e-6)]
            pts.append(b.mean(0))
    c0, ax = fit_line(np.array(pts))
    if ax[1] > 0: ax = -ax                         # pointing down the arm
    sh0 = c0 + ax * ((.805 * H - c0[1]) / ax[1])
    ts = np.arange(0, .80, .005); A = np.full(len(ts), np.nan); C = np.full((len(ts), 3), np.nan)
    for i, t in enumerate(ts):
        c = sect(ax, sh0 + ax * t, sh0 + ax * t, .09)
        if c is not None: A[i] = area(c, ax); C[i] = c.mean(0)
    t0 = ts[np.isfinite(A)][0]
    t_el = plateau_min(ts, A, t0 + .10, t0 + .26)
    t_wr = plateau_min(ts, A, t_el + .12, t_el + .28)
    at = lambda t: C[np.argmin(np.abs(ts - t))]
    elbow = (at(t_el - .005) + at(t_el) + at(t_el + .005)) / 3
    wrist = (at(t_wr - .005) + at(t_wr) + at(t_wr + .005)) / 3
    m = (ts >= t0) & (ts <= t_el - .03) & np.isfinite(A)
    pu, du = fit_line(C[m])
    if du[1] > 0: du = -du
    # follow the upper-arm line up to the skin at the shoulder; the humeral
    # head's centre sits ~4.2 cm inside it (head r ~2.3 + deltoid + skin)
    rel = V - pu; tt = rel @ du; rad = np.linalg.norm(rel - np.outer(tt, du), axis=1)
    near = (rad < .03) & (tt < 0) & (V[:, 0] > .10)
    t_exit = tt[near].min()
    gh = pu + du * (t_exit + .042)
    hand = V[((V - wrist) @ ax > 0) & (V[:, 0] > wrist[0] - .06) & (V[:, 1] < wrist[1] + .02)]
    hd = at(t_wr + .08) - wrist; hd /= np.linalg.norm(hd)
    tip = hand[np.argmax((hand - wrist) @ hd)]
    LM["arm"] = dict(axis=ax.tolist(), t_elbow=t_el, t_wrist=t_wr, gh=gh.tolist(), elbow=elbow.tolist(),
                     wrist=wrist.tolist(), tip=tip.tolist(), handDir=hd.tolist(),
                     upLen=float(np.linalg.norm(elbow - gh)), foreLen=float(np.linalg.norm(wrist - elbow)),
                     handLen=float(np.linalg.norm(tip - wrist)), shoulderTop=float(pu[1] + du[1] * t_exit))
    # ---------------- leg (right side) ----------------
    ys = np.arange(.05, .83, .005); LA = np.full(len(ys), np.nan); LC = np.full((len(ys), 3), np.nan)
    up = np.array([0, 1., 0])
    for i, y in enumerate(ys):
        ls = [c for c in sectlib.loops(V, EA, FE, float(y)) if .02 < c[:, 0].mean() < .30]
        if not ls: continue
        c = min(ls, key=lambda c: abs(c[:, 0].mean() - .12))
        LA[i] = area(c, up); LC[i] = c.mean(0)
    y_kn = plateau_min(ys, LA, .44, .60)
    lat = lambda y: LC[np.argmin(np.abs(ys - y))]
    knee = (lat(y_kn - .005) + lat(y_kn) + lat(y_kn + .005)) / 3
    m = (ys >= y_kn + .06) & (ys <= .80) & np.isfinite(LA)
    pt, dt = fit_line(LC[m])
    hip = pt + dt * ((PELVIS - pt[1]) / dt[1])
    ank = lat(.15).copy(); ank[1] = .075
    LM["leg"] = dict(hip=hip.tolist(), knee=[float(knee[0]), y_kn, float(knee[2])], ankle=ank.tolist(),
                     thigh=float(PELVIS - y_kn), shank=float(y_kn - .075))
    # ---------------- spine / neck / head ----------------
    prof = []
    for y0 in np.arange(1.40, 1.60, .005):
        b = V[(V[:, 1] >= y0) & (V[:, 1] < y0 + .005) & (np.abs(V[:, 0]) < .30)]
        if len(b): prof.append((float(y0), float(np.percentile(np.abs(b[:, 0]), 95))))
    y_neck = min(prof, key=lambda p: p[1])[0]; y_top = float(V[:, 1].max())
    LM["axial"] = dict(pelvis=PELVIS, spine=PELVIS + .114, chest=PELVIS + .114 + .186, neck=y_neck,
                       head=(y_neck + .35 * (y_top - y_neck) + y_top) / 2, top=y_top)
    return LM

if __name__ == "__main__":
    V, F4 = load()
    LM = measure(V, F4)
    print(json.dumps(LM, indent=1, default=lambda o: round(o, 4)))
