"""M2 — garment shells cut from the re-posed body (stage 2 outputs).
Tops/trousers: field f(p) > 0 inside -> exact clip along f = 0 -> rounds of
(smooth, push back outside the skin) -> DRAPE (cloth hangs straight from what
it rests on) -> layering over inner garments -> hem bands -> weights copied
from the body where it was cut, smoothed. Shoes: a loft along each foot.
Writes out/g_<name>.npz and out/bodymask.npz (body faces each garment hides)."""
import bpy, json, os, sys, math, time
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out")
sys.path.insert(0, HERE)
import importlib, garmentlib as G
importlib.reload(G)
def log(*a): print("[gm]", *a, flush=True)

rig = json.load(open(os.path.join(OUT, "rig.json")))
V = np.load(os.path.join(OUT, "rest_co.npy")).astype(np.float64)
T = np.load(os.path.join(OUT, "rest_tri.npy")).astype(np.int64)
skI = np.load(os.path.join(OUT, "skI.npy")); skW = np.load(os.path.join(OUT, "skW.npy"))
bones = rig["bones"]; B = {n: i for i, n in enumerate(bones)}
W = np.zeros((len(V), len(bones)))
for k in range(4): np.add.at(W, (np.arange(len(V)), skI[:, k]), skW[:, k])
N = G.vnormals(V, T)

def make_nearest(Vs, Ts, Ns, Ws=None):
    bvh = BVHTree.FromPolygons([Vector(p) for p in Vs], Ts.tolist())
    def bary(fi, loc):
        a, b, c = Ts[fi]; A = Vs[a]; v0, v1, v2 = Vs[b] - A, Vs[c] - A, loc - A
        d00, d01, d11 = v0 @ v0, v0 @ v1, v1 @ v1; d20, d21 = v2 @ v0, v2 @ v1
        den = d00 * d11 - d01 * d01 or 1e-12
        vb = (d11 * d20 - d01 * d21) / den; wb = (d00 * d21 - d01 * d20) / den
        return (a, b, c), np.array([1 - vb - wb, vb, wb])
    def nearest(p):
        loc, fn, fi, d = bvh.find_nearest(Vector(p)); loc = np.array(loc)
        ids, w = bary(fi, loc)
        n = w @ Ns[list(ids)]; n /= np.linalg.norm(n) or 1
        return loc, n
    def weights(p):
        loc, fn, fi, d = bvh.find_nearest(Vector(p)); ids, w = bary(fi, np.array(loc))
        return np.clip(w, 0, 1) @ Ws[list(ids)]
    return nearest, weights
nearest, body_weights = make_nearest(V, T, N, W)
# cloth only collides with what it covers: the hands hang beside the hips,
# and a hem pushed off a knuckle flares out like a bustle

J = rig["joints"]
x, y, z = V[:, 0], V[:, 1], V[:, 2]
armW = W[:, [B[n] for n in ("shoulderL", "elbowL", "wristL", "shoulderR", "elbowR", "wristR")]].sum(1)
legW = W[:, [B[n] for n in ("hipL", "kneeL", "ankleL", "hipR", "kneeR", "ankleR")]].sum(1)
headW = W[:, [B["head"], B["neck"]]].sum(1)
isArm = armW > .5; isLeg = legW > .5
armF = isArm[T].all(1)
near_arm, _ = make_nearest(V, T[armF], N)
near_body, _ = make_nearest(V, T[~isArm[T].any(1)], N)
# Cloth rests on the FORM of a body, not on its muscles: the base mesh is an
# anatomy study, and pushed out against it a sweater showed every lat and
# shoulder blade — on the women too. Collide against a volume-kept smooth of
# the body first, then only keep a thin 3 mm clear of the real skin.
Vs = G.taubin(V, T, 55)
Ns = G.vnormals(Vs, T)
near_arm_s, _ = make_nearest(Vs, T[armF], Ns)
near_body_s, _ = make_nearest(Vs, T[~isArm[T].any(1)], Ns)
def push_split(Vg, armg, off):
    out = Vg.copy()
    if armg.any():
        out[armg] = G.push_out(Vg[armg], near_arm_s, off[armg])
        out[armg] = G.push_out(out[armg], near_arm, np.full(armg.sum(), .003))
    if (~armg).any():
        out[~armg] = G.push_out(Vg[~armg], near_body_s, off[~armg])
        out[~armg] = G.push_out(out[~armg], near_body, np.full((~armg).sum(), .003))
    return out
nb = V[(np.abs(y - 1.50) < .008) & (np.abs(x) < .055)]        # the neck column alone
NZ = float((nb[:, 2].min() + nb[:, 2].max()) / 2)
log("neck centre z", round(NZ, 4))

def centre_z(mask, lo, hi, step=.02):
    ys = np.arange(lo, hi + step, step); zs = []
    for yy in ys:
        b = V[mask & (np.abs(y - yy) < step)]
        zs.append((b[:, 2].min() + b[:, 2].max()) / 2 if len(b) else np.nan)
    zs = np.array(zs); ok = np.isfinite(zs)
    return lambda q: np.interp(q, ys[ok], zs[ok])
# measured where the section is a clean torso / a clean leg, held constant
# beyond (np.interp clamps): at the seat the "torso" section is mostly
# buttock, its centre jumps 9 cm back, and a radius measured from a jumping
# axis is meaningless
torso_cz = centre_z(~isArm & ~isLeg & (headW < .5), .95, 1.45)
leg_cz = centre_z(isLeg & (x > 0), .10, .74)

def f_neck(rx, rz, y_front, y_back):
    ell = np.sqrt((x / rx) ** 2 + ((z - NZ) / rz) ** 2) - 1
    t = np.clip((z - (NZ - rz)) / (2 * rz), 0, 1)
    y_n = y_back + (y_front - y_back) * t
    return np.minimum(np.maximum(ell * .08, y_n - y), 1.53 - y)

def top(hem_y, sleeve_y, neck):
    f = np.minimum(y - hem_y, f_neck(*neck))
    f = np.where(isArm, np.minimum(f, y - sleeve_y), f)
    return np.where(isLeg & (y < hem_y + .05), -1.0, f)

def trousers(waist_y, hem_y):
    return np.where(isArm, -1.0, np.minimum(waist_y - y, y - hem_y))

wr_y = J["wristR"][1]; sh_y = J["shoulderR"][1]; SHX = J["shoulderR"][0]; SHZ = J["shoulderR"][2]
CREW = (.084, .076, 1.412, 1.470)
SPECS = {
  "trousers": dict(f=trousers(.975, .078), off=.008, rounds=4, it=6, hem=.007, layer=[]),
  "tee":      dict(f=top(.885, sh_y - .185, CREW), off=.006, loose=.010, rounds=5, it=8, hem=.006, layer=["trousers"]),
  "shirt":    dict(f=top(.87, wr_y + .018, (.074, .068, 1.44, 1.49)), off=.007, loose=.012, rounds=5, it=8, hem=.006, layer=["trousers"]),
  "sweater":  dict(f=top(.875, wr_y + .012, CREW), off=.014, loose=.010, rounds=5, it=9, hem=.010, layer=["trousers"]),
}
def blazer_field():
    f = top(.80, wr_y + .032, (.088, .082, 1.40, 1.497))
    w = np.where(y > 1.06, .088 * np.clip((y - 1.06) / .40, 0, 1), (1.06 - y) * .32)
    front = (z > .0) & ~isArm & (y < 1.47)
    return np.where(front, np.minimum(f, (np.abs(x) - w) / .02 * .01), f)
SPECS["blazer"] = dict(f=blazer_field(), off=.018, loose=.012, rounds=5, it=9, hem=.012, layer=["trousers", "shirt"])
built, masks, shells = {}, {}, {}
for name, s in SPECS.items():
    t0 = time.time()
    f = s["f"]
    Vg, Tg, Wg, par = G.clip(V, T, W, f)
    Vg, Tg, Wg = G.largest_component(Vg, Tg, Wg)
    armg = Wg[:, [B[n] for n in ("shoulderL", "elbowL", "wristL", "shoulderR", "elbowR", "wristR")]].sum(1) > .5
    if name == "trousers":
        offf = lambda P: s["off"] + .012 * np.clip((.55 - P[:, 1]) / .45, 0, 1) + .008 * np.clip((.16 - P[:, 1]) / .08, 0, 1)
    else:
        offf = lambda P, s=s, a=armg: s["off"] + s["loose"] * np.clip((1.16 - P[:, 1]) / .28, 0, 1) * (~a)
    for r in range(s["rounds"]):
        Vg = G.laplacian(Vg, Tg, s["it"], .5)
        Vg = push_split(Vg, armg, offf(Vg))
    if name == "trousers":
        for sgn in (1, -1):
            sel = (Vg[:, 0] * sgn > .005) & (Vg[:, 1] < .79)
            Vg = G.drape(Vg, sel, sgn * J["hipR"][0], leg_cz, .45, .045)
    else:
        # a regular fit: it falls from the chest and the shoulder blades but
        # tapers with the body (1 cm per 10 cm) instead of hanging as a tube
        Vg = G.drape(Vg, ~armg & (Vg[:, 1] < 1.40), 0.0, torso_cz, .22, .09)
        for sgn in (1, -1):
            sel = armg & (Vg[:, 0] * sgn > 0) & (Vg[:, 1] < sh_y - .05)
            # a sleeve falls from the deltoid but narrows to the cuff (2 cm per 10 cm):
            # a straight tube is a bell once the elbow bends
            Vg = G.drape(Vg, sel, sgn * SHX, lambda q: np.full_like(q, SHZ), .10, .20)
    Vg = G.laplacian(Vg, Tg, 2, .4)
    Vg = push_split(Vg, armg, offf(Vg))
    for inner in s["layer"]:          # over the waistband, never through it
        Vi, Ti = shells[inner]        # the shell before its hem band: no inner rim to snag on
        near_i, _ = make_nearest(Vi, Ti, G.vnormals(Vi, Ti))
        # the torso over the waistband; a cuff hanging by the hip is not its business
        low = (Vg[:, 1] < Vi[:, 1].max() - .004) & ~armg
        Vg[low] = G.push_out_layer(Vg[low], near_i, .005, .04)
    Vg = G.smooth_rim(Vg, Tg, 6)
    shells[name] = (Vg.copy(), Tg.copy())
    Ng = G.vnormals(Vg, Tg)
    Vg, Tg, Wg = G.hem_band(Vg, Tg, Wg, s["hem"] + s["off"], Ng)
    Wg = G.smooth_field(Wg, Tg, 3, .5)
    built[name] = (Vg, Tg, Wg)
    masks[name] = (f[T] > .012).all(1)
    log(name, "verts", len(Vg), "tris", len(Tg), "hides", int(masks[name].sum()), f"{time.time() - t0:.1f}s")

# ---------------- shoes: a loft along each foot ----------------
def shoe(sgn, ring=18, st=22):
    foot = V[isLeg & (x * sgn > 0) & (y < .13)]
    low = foot[foot[:, 1] < .05]
    zh, zt = low[:, 2].min() - .012, low[:, 2].max() + .020
    zs = np.linspace(zh, zt, st)
    rings, P = [], []
    for i, zz in enumerate(zs):
        u = i / (st - 1)
        sl = foot[np.abs(foot[:, 2] - zz) < .014]
        if len(sl) < 3: sl = foot[np.argsort(np.abs(foot[:, 2] - zz))[:12]]
        cx = (sl[:, 0].min() + sl[:, 0].max()) / 2
        w = (sl[:, 0].max() - sl[:, 0].min()) / 2 + .011
        h = min(sl[:, 1].max(), .115) + .010
        # round the heel and the toe: sections shrink over the last few stations
        e = min(1.0, u / .10, (1 - u) / .16)
        k = np.sqrt(max(e, 0)) if e < 1 else 1.0
        w *= .35 + .65 * k; top_y = .012 + (h - .012) * (.45 + .55 * k)
        bot = -.004 + .012 * max(0, (u - .82) / .18) ** 2          # toe spring
        R = []
        for j in range(ring):
            a = 2 * np.pi * j / ring
            ca, sa = np.cos(a), np.sin(a)
            px = cx + w * np.sign(ca) * abs(ca) ** (2 / 3.2)
            py = (top_y + bot) / 2 + (top_y - bot) / 2 * np.sign(sa) * abs(sa) ** (2 / 3.2)
            R.append(len(P)); P.append([px, max(py, bot), zz])
        rings.append(R)
    F = []
    for i in range(st - 1):
        A, Bq = rings[i], rings[i + 1]
        for j in range(ring):
            a0, a1, b0, b1 = A[j], A[(j + 1) % ring], Bq[j], Bq[(j + 1) % ring]
            F += [[a0, a1, b1], [a0, b1, b0]]
    P = np.array(P)
    for R, flip in ((rings[0], True), (rings[-1], False)):      # caps
        c = len(P); P = np.vstack([P, P[R].mean(0)])
        for j in range(ring):
            t = [c, R[(j + 1) % ring], R[j]]
            F.append(t[::-1] if not flip else t)
    F = np.array(F)
    # wind outward: compare the face normal with the direction from the axis
    fn = np.cross(P[F[:, 1]] - P[F[:, 0]], P[F[:, 2]] - P[F[:, 0]]); cen = P.mean(0)
    if (np.einsum("ij,ij->i", fn, P[F].mean(1) - cen) < 0).mean() > .5: F = F[:, ::-1]
    return P, F
parts = []
for sgn in (1, -1):
    Ps, Fs = shoe(sgn)
    Ws = np.array([body_weights(p) for p in Ps])
    # the collar: open behind the instep, above the ankle bone
    zlen = Ps[:, 2].max() - Ps[:, 2].min()
    z_open = Ps[:, 2].min() + .48 * zlen
    fcol = np.maximum(Ps[:, 2] - z_open, .082 + .02 * np.clip((Ps[:, 2] - Ps[:, 2].min()) / zlen, 0, 1) - Ps[:, 1])
    Ps, Fs, Ws, _ = G.clip(Ps, Fs, Ws, fcol)
    Ps, Fs, Ws = G.hem_band(Ps, Fs, Ws, .008, G.vnormals(Ps, Fs))
    parts.append((Ps, Fs, Ws))
Pv = np.vstack([parts[0][0], parts[1][0]]); Fv = np.vstack([parts[0][1], parts[1][1] + len(parts[0][0])])
Wv = np.vstack([parts[0][2], parts[1][2]])
built["shoes"] = (Pv, Fv, Wv)
masks["shoes"] = (np.where(isLeg, .098 - y, -1.0)[T] > .0).all(1)
log("shoes verts", len(Pv), "tris", len(Fv), "hides", int(masks["shoes"].sum()))

# ---------------- the apron: a bistro apron, waist to knee ----------------
# Not cut from the body: a sheet hung from a ring round the front of the
# waist, falling straight (cloth over the thighs, not between them), pushed
# clear of the body where a thigh or the belly would come through. Weights:
# the waistband rides the pelvis; the skirt follows the two legs half each,
# so a stride swings it without tearing it between them.
def apron():
    NU, NV = 22, 12
    TH = np.radians(np.linspace(-78, 78, NU)); ys = np.linspace(.965, .545, NV)
    ring = V[(np.abs(V[:, 1] - .965) < .012) & ~isArm & ~isLeg]
    rc = np.array([0.0, torso_cz(np.array([.965]))[0]])
    P = []
    for j, yy in enumerate(ys):
        for i, th in enumerate(TH):
            d = np.array([np.sin(th), np.cos(th)])
            proj = (ring[:, [0, 2]] - rc) @ d
            r = proj.max() + .020 + .012 * (j / (NV - 1))       # out over the trousers, flaring a little
            P.append([rc[0] + d[0] * r, yy, rc[1] + d[1] * r])
    P = np.array(P)
    F = []
    for j in range(NV - 1):
        for i in range(NU - 1):
            a, b = j * NU + i, j * NU + i + 1; c, e = a + NU, b + NU
            F += [[a, c, b], [b, c, e]]
    F = np.array(F)
    fn = np.cross(P[F[:, 1]] - P[F[:, 0]], P[F[:, 2]] - P[F[:, 0]])
    if (np.einsum("ij,ij->i", fn, P[F].mean(1) - np.array([0, P[:, 1].mean(), rc[1]])) < 0).mean() > .5: F = F[:, ::-1]
    for _ in range(3):
        P = G.push_out(P, near_body, np.full(len(P), .016))
        P = G.laplacian(P, F, 2, .3)
    Wa = np.zeros((len(P), len(bones)))
    k = np.clip((.95 - P[:, 1]) / .30, 0, 1)
    Wa[:, B["pelvis"]] = 1 - k; Wa[:, B["hipL"]] = k / 2; Wa[:, B["hipR"]] = k / 2
    P, F, Wa = G.hem_band(P, F, Wa, .006, G.vnormals(P, F))
    return P, F, Wa
built["apron"] = apron()
masks["apron"] = np.zeros(len(T), bool)
log("apron verts", len(built["apron"][0]), "tris", len(built["apron"][1]))

for name, (Vg, Tg, Wg) in built.items():
    gI, gW = G.top4(Wg)
    extra = {}
    if name == "shoes": extra["part"] = (Vg[:, 1] < .014).astype(np.uint8)       # the sole
    np.savez(os.path.join(OUT, "g_" + name + ".npz"), pos=Vg.astype(np.float32), tri=Tg.astype(np.uint16),
             skI=gI, skW=gW, **extra)
np.savez(os.path.join(OUT, "bodymask.npz"), **masks)
