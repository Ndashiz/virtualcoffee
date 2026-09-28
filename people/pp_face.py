"""M3a — open the eyes. The base head has its lids shut: refine the eye
region, cut an almond opening EXACTLY along its outline, turn the rim
inward (lid thickness), and record where the eyeballs go.
Reads/writes out/rest_co, rest_tri, skI, skW (run after pp_rig, before
pp_garments); writes out/face.json."""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out")
sys.path.insert(0, HERE)
import garmentlib as G
V = np.load(os.path.join(OUT, "rest_co.npy")).astype(np.float64)
T = np.load(os.path.join(OUT, "rest_tri.npy")).astype(np.int64)
skI = np.load(os.path.join(OUT, "skI.npy")); skW = np.load(os.path.join(OUT, "skW.npy"))
rig = json.load(open(os.path.join(OUT, "rig.json"))); nb = len(rig["bones"])
W = np.zeros((len(V), nb))
for k in range(4): np.add.at(W, (np.arange(len(V)), skI[:, k]), skW[:, k])

EX, EY, EZ, ER = .032, 1.646, .085, .012        # eyeball centre (x mirrored), radius
HALF_W, UP, LO, TILT = .0158, .0063, .0047, .0015
def near_eye(P):
    return (np.abs(np.abs(P[:, 0]) - EX) < .021) & (np.abs(P[:, 1] - EY) < .014) & (P[:, 2] > .06)
def almond(P):
    u = (np.abs(P[:, 0]) - EX) / HALF_W           # -1 inner canthus .. +1 outer
    dy = P[:, 1] - EY - TILT * (u + 1) / 2        # the outer corner sits higher
    uu = np.clip(u, -1, 1)
    up = UP * np.clip(1 - ((uu + .2) / 1.2) ** 2, 0, 1) ** .75     # upper lid peaks medially
    lo = -LO * np.clip(1 - ((uu - .15) / 1.15) ** 2, 0, 1) ** 1.1  # lower lid dips laterally
    f = np.minimum.reduce([(1 - np.abs(u)) * .012, up - dy, dy - lo])
    return np.where((P[:, 2] > .06) & (np.abs(P[:, 1] - EY) < .03), f, -1.0)
cen = V[T].mean(1)                                # one level round the eye
V, T, W = G.refine(V, T, W, near_eye(cen))
for it in range(2):                               # and two more along the lid line
    cen = V[T].mean(1)
    V, T, W = G.refine(V, T, W, np.abs(almond(cen)) < .0022 / (it + 1))
print("[face] after refine: verts", len(V), "tris", len(T))

f = -almond(V)                                    # keep what is OUTSIDE the opening
V, T, W, _ = G.clip(V, T, W, f)
N = G.vnormals(V, T)
B = G.boundary_edges(T)
print("[face] opening rim edges", len(B))
# the rim turns in toward the eyeball: lid thickness, and no view into the skull
inward = np.zeros_like(V)
ids = np.unique(B.ravel())
for i in ids:
    c = np.array([np.sign(V[i, 0]) * EX, EY, EZ])
    d = c - V[i]; inward[i] = d / np.linalg.norm(d)
V, T, W = G.hem_band(V, T, W, .0045, -inward)
I, Wt = G.top4(W)
np.save(os.path.join(OUT, "rest_co.npy"), V.astype(np.float32)); np.save(os.path.join(OUT, "rest_tri.npy"), T.astype(np.uint16))
np.save(os.path.join(OUT, "skI.npy"), I); np.save(os.path.join(OUT, "skW.npy"), Wt)
json.dump(dict(eye=dict(x=EX, y=EY, z=EZ, r=ER)), open(os.path.join(OUT, "face.json"), "w"), indent=1)
print("[face] done: verts", len(V), "tris", len(T))
