"""M3b — hair. Every style is a shell grown off the scalp: the region above a
hairline (forehead, receding temples, a sideburn in front of the ear, round
behind it, down to the nape), offset by a thickness that goes to ZERO at the
hairline so it melts into the skin instead of sitting on it like a cap.
Longer cuts add a curtain over the ears and neck that hangs straight from
the widest point of the head (drape). Extras: a bun, a ponytail.
Writes out/g_hair_<style>.npz (same bone order as the body)."""
import bpy, os, sys, json, math
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out")
sys.path.insert(0, HERE)
import importlib, garmentlib as G
importlib.reload(G)
def log(*a): print("[hair]", *a, flush=True)
rig = json.load(open(os.path.join(OUT, "rig.json"))); bones = rig["bones"]; B = {n: i for i, n in enumerate(bones)}
V = np.load(os.path.join(OUT, "rest_co.npy")).astype(np.float64)
T = np.load(os.path.join(OUT, "rest_tri.npy")).astype(np.int64)
skI = np.load(os.path.join(OUT, "skI.npy")); skW = np.load(os.path.join(OUT, "skW.npy"))
W = np.zeros((len(V), len(bones)))
for k in range(4): np.add.at(W, (np.arange(len(V)), skI[:, k]), skW[:, k])
N = G.vnormals(V, T)
armW = W[:, [B[n] for n in ("shoulderL", "elbowL", "wristL", "shoulderR", "elbowR", "wristR")]].sum(1)
# collide against head, neck and upper torso only
colF = (V[T][:, :, 1].min(1) > 1.30) & ~(armW[T] > .5).any(1)
bvh = BVHTree.FromPolygons([Vector(p) for p in V], T[colF].tolist())
Tc = T[colF]
def nearest(p):
    loc, fn, fi, d = bvh.find_nearest(Vector(p)); loc = np.array(loc)
    a, b, c = Tc[fi]; A = V[a]; v0, v1, v2 = V[b] - A, V[c] - A, loc - A
    d00, d01, d11 = v0 @ v0, v0 @ v1, v1 @ v1; d20, d21 = v2 @ v0, v2 @ v1
    den = d00 * d11 - d01 * d01 or 1e-12
    vb = (d11 * d20 - d01 * d21) / den; wb = (d00 * d21 - d01 * d20) / den
    n = (1 - vb - wb) * N[a] + vb * N[b] + wb * N[c]; n /= np.linalg.norm(n) or 1
    return loc, n

C = np.array([0, 1.665, .012])                      # skull centre
D = V - C; R = np.linalg.norm(D, axis=1)
EL = np.degrees(np.arcsin(np.clip(D[:, 1] / np.maximum(R, 1e-9), -1, 1)))
AZ = np.degrees(np.arctan2(D[:, 0], D[:, 2]))       # 0 front, +-180 back
A = np.abs(AZ)
HL_AZ = [0, 30, 50, 68, 74, 84, 92, 100, 118, 145, 180]
HL_EL = [32, 27, 20, 14, -14, -14, 6, 4, -10, -34, -52]
el_min = np.interp(A, HL_AZ, HL_EL)
ear = (np.abs(V[:, 0]) > .073) & (V[:, 1] > 1.593) & (V[:, 1] < 1.664) & (V[:, 2] > -.048) & (V[:, 2] < .032)
headish = (V[:, 1] > 1.50) & (np.abs(V[:, 0]) < .14) & (armW < .5)
scalp_f = np.where(headish & ~ear, (EL - el_min) / 60.0, -1.0)   # ~radians-ish, positive inside

def thickness(P, top, side, back):
    d = P - C; r = np.linalg.norm(d, axis=1)
    el = np.degrees(np.arcsin(np.clip(d[:, 1] / r, -1, 1))); az = np.abs(np.degrees(np.arctan2(d[:, 0], d[:, 2])))
    t_top = np.clip((el - 25) / 30, 0, 1)
    t_back = np.clip((az - 100) / 60, 0, 1)
    base = side + (back - side) * t_back
    return base + (top - base) * t_top

def hair_weights(P):
    Wh = np.zeros((len(P), len(bones)))
    y = P[:, 1]
    wh = np.clip((y - 1.50) / .12, 0, 1)            # head above the jaw, neck/chest below
    wn = np.clip(1 - wh, 0, 1) * np.clip((y - 1.38) / .12, 0, 1)
    wc = np.clip(1 - wh - wn, 0, 1)
    Wh[:, B["head"]] = wh; Wh[:, B["neck"]] = wn; Wh[:, B["chest"]] = wc
    return Wh

def shell(field, top, side, back, rounds=3, it=4, drape=None, bottom=None, hem=.003, curl=0.0, edge=9.0):
    f = field.copy()
    if bottom is not None: f = np.minimum(f, (V[:, 1] - bottom) / 60.0 * 30)
    Vg, Tg, Wg, _ = G.clip(V, T, W, f)
    Vg, Tg, Wg = G.largest_component(Vg, Tg, Wg)
    # distance into the region, for the taper at the hairline
    fg = np.interp(np.arange(len(Vg)), [], []) if False else None
    d = Vg - C; r = np.linalg.norm(d, axis=1)
    el = np.degrees(np.arcsin(np.clip(d[:, 1] / r, -1, 1))); az = np.abs(np.degrees(np.arctan2(d[:, 0], d[:, 2])))
    inside = el - np.interp(az, HL_AZ, HL_EL)
    taper = np.clip(inside / edge, 0, 1) ** .7         # 0 at the hairline -> full over `edge` degrees
    if drape is not None: taper = np.maximum(taper, (Vg[:, 1] < 1.66).astype(float))
    off = thickness(Vg, top, side, back) * taper + .0006
    for _ in range(rounds):
        Vg = G.laplacian(Vg, Tg, it, .5)
        Vg = G.push_out(Vg, nearest, off)
    if drape is not None:
        Vg = G.drape(Vg, Vg[:, 1] < 1.70, 0.0, lambda q: np.full_like(q, C[2]), drape[0], drape[1])
        Vg = G.laplacian(Vg, Tg, 2, .4)
        Vg = G.push_out(Vg, nearest, off)
    # soft clumps: a few mm of low-frequency relief, never at the hairline
    Ng = G.vnormals(Vg, Tg)
    d = Vg - C; az = np.arctan2(d[:, 0], d[:, 2]); el = np.arcsin(np.clip(d[:, 1] / np.linalg.norm(d, axis=1), -1, 1))
    n = (np.sin(az * 9 + el * 3.1) * .5 + np.sin(az * 17 - el * 7.3 + 1.7) * .3 + np.sin(el * 13 + az * 5 + .6) * .2)
    Vg = Vg + Ng * (n * .0028 * np.clip(off / .012, 0, 1) * taper)[:, None]
    if curl:          # tight waves on top: two octaves of lumps, strongest where the hair is thick
        c = (np.sin(az * 23 + el * 5.3) * np.sin(el * 19 - az * 3.1) + .5 * np.sin(az * 41 - el * 13 + 2.1) * np.sin(el * 37 + az * 7))
        Vg = Vg + Ng * (c * curl * np.clip(off / .02, 0, 1) * taper)[:, None]
    Vg, Tg, Wg = G.hem_band(Vg, Tg, Wg, hem, G.vnormals(Vg, Tg))
    return Vg, Tg, hair_weights(Vg)

def blob(center, radii, n=14):
    u = np.linspace(0, np.pi, n); v = np.linspace(0, 2 * np.pi, 2 * n, endpoint=False)
    P = [[center[0] + radii[0] * np.sin(a) * np.cos(b), center[1] + radii[1] * np.cos(a),
          center[2] + radii[2] * np.sin(a) * np.sin(b)] for a in u for b in v]
    F = []
    m = len(v)
    for i in range(n - 1):
        for j in range(m):
            a0, a1 = i * m + j, i * m + (j + 1) % m; b0, b1 = a0 + m, a1 + m
            F += [[a0, b0, a1], [a1, b0, b1]]
    P = np.array(P); F = np.array(F)
    fn = np.cross(P[F[:, 1]] - P[F[:, 0]], P[F[:, 2]] - P[F[:, 0]])
    if (np.einsum("ij,ij->i", fn, P[F].mean(1) - center) < 0).mean() > .5: F = F[:, ::-1]
    return P, F

def tube(path, radii, ring=12):
    path = np.array(path); P, F = [], []
    for i, (p, r) in enumerate(zip(path, radii)):
        t = path[min(i + 1, len(path) - 1)] - path[max(i - 1, 0)]; t /= np.linalg.norm(t)
        a = np.cross(t, [1, 0, 0]); a /= np.linalg.norm(a); b = np.cross(t, a)
        for j in range(ring):
            th = 2 * np.pi * j / ring; P.append(p + r * (np.cos(th) * a + np.sin(th) * b))
    for i in range(len(path) - 1):
        for j in range(ring):
            a0, a1 = i * ring + j, i * ring + (j + 1) % ring; b0, b1 = a0 + ring, a1 + ring
            F += [[a0, a1, b1], [a0, b1, b0]]
    P = np.array(P); c = len(P); P = np.vstack([P, path[-1]])
    for j in range(ring): F.append([c, (len(path) - 1) * ring + (j + 1) % ring, (len(path) - 1) * ring + j])
    F = np.array(F)
    cen = np.repeat(path, ring, 0); cen = np.vstack([cen, path[-1]])
    fn = np.cross(P[F[:, 1]] - P[F[:, 0]], P[F[:, 2]] - P[F[:, 0]])
    if (np.einsum("ij,ij->i", fn, P[F].mean(1) - cen[F[:, 0]]) < 0).mean() > .5: F = F[:, ::-1]
    return P, F

def merge(*parts):
    Vs, Ts, off = [], [], 0
    for P, F in parts: Vs.append(P); Ts.append(F + off); off += len(P)
    P = np.vstack(Vs); return P, np.vstack(Ts), hair_weights(P)

STY = {}
STY["buzz"] = shell(scalp_f, .0024, .0018, .0020, rounds=2, it=3, hem=.0015)
STY["short"] = shell(scalp_f, .017, .0058, .0080)
STY["fade"] = shell(scalp_f, .013, .0016, .0022, hem=.002)
# Simon (photo.jpg): short, dark, waves and loose curls on top, tidier at the sides
curly_f = np.where(headish & ~ear, (EL - (el_min - 4 * np.clip(1 - A / 40, 0, 1))) / 60.0, -1.0)
STY["curly"] = shell(curly_f, .030, .0105, .0140, rounds=3, it=4, hem=.004, curl=.0055, edge=3.5)
tight = shell(scalp_f, .0065, .0042, .0055)
STY["bun"] = merge(tight[:2], blob(np.array([0, 1.722, -.083]), (.040, .034, .036)))
STY["pony"] = merge(tight[:2], blob(np.array([0, 1.690, -.086]), (.017, .016, .015)),
                    tube([[0, 1.692, -.092], [0, 1.655, -.112], [0, 1.60, -.118], [0, 1.545, -.110], [0, 1.50, -.098]],
                         [.020, .024, .021, .016, .008]))
# a bob: scalp plus a curtain over the ears and round the back, to the jaw line
curtain = headish & (A > 62) & (V[:, 1] > 1.575)
STY["bob"] = shell(np.where(curtain, np.maximum(scalp_f, .05), scalp_f), .020, .026, .024,
                   rounds=4, it=5, drape=(.16, .03), bottom=1.585, hem=.006)
# long: the curtain continues over the neck and the top of the back
curtain_l = (A > 62) & (V[:, 1] > 1.40) & (armW < .5) & (np.abs(V[:, 0]) < .16) & ~((V[:, 2] > .02) & (V[:, 1] < 1.55))
STY["long"] = shell(np.where(curtain_l, np.maximum(scalp_f, .05), scalp_f), .022, .028, .030,
                    rounds=4, it=6, drape=(.30, .03), bottom=1.42, hem=.007)
for name, (P, F, Wh) in STY.items():
    gI, gW = G.top4(Wh)
    np.savez(os.path.join(OUT, "g_hair_" + name + ".npz"), pos=P.astype(np.float32), tri=F.astype(np.uint16), skI=gI, skW=gW)
    log(name, "verts", len(P), "tris", len(F))
