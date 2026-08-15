#!/usr/bin/env python3
"""Cut the decimated FinalBaseMesh into rig segments — v2.

v1 forced every segment to the capsule rig's stylised lengths (legs
stretched 1.6x, torso squashed .75x) and mis-read the crotch where the
thighs touch: deformed bodies. v2 keeps the mesh's own proportions and
prints the joint rest offsets the scene must apply instead; landmarks
come from slice CLUSTERING (two islands = legs, one = pelvis; three at
chest height = torso + two arms).

Outputs: person.obj (parts in joint-local coords, unscaled) + a PARTS
constant block to paste into index.html.
"""
import collections, json, math
import numpy as np

SRC = "/private/tmp/claude-501/-Users-ndashiz-Documents-lazypo/372a9a7f-c8e7-4e25-9329-fb957c093879/scratchpad/person_dec.obj"
DST = "/Users/ndashiz/Documents/virtualcoffee/person.obj"
H = 1.75

V, F = [], []
for line in open(SRC):
    if line.startswith("v "):
        p = line.split(); V.append([float(p[1]), float(p[2]), float(p[3])])
    elif line.startswith("f "):
        F.append([int(t.split("/")[0]) - 1 for t in line.split()[1:]])
V = np.array(V); F = np.array(F)

V[:, 1] -= V[:, 1].min()
V *= H / V[:, 1].max()
V[:, 0] -= (V[:, 0].min() + V[:, 0].max()) / 2
torso_band = V[(V[:, 1] > .95) & (V[:, 1] < 1.15)]
V[:, 2] -= torso_band[:, 2].mean()
head_band = V[V[:, 1] > 1.58]
if head_band[np.abs(head_band[:, 2]).argmax()][2] < 0:
    V[:, 0] *= -1; V[:, 2] *= -1
    print("flipped to face +z")

def clusters_x(y0, y1, xmax=99):
    """1D x-clusters of the slice (gap > 4 cm splits)"""
    b = V[(V[:, 1] >= y0) & (V[:, 1] < y1) & (np.abs(V[:, 0]) < xmax)]
    if len(b) < 4: return []
    xs = np.sort(b[:, 0])
    out, start = [], xs[0]
    for i in range(1, len(xs)):
        if xs[i] - xs[i - 1] > .04:
            out.append((start, xs[i - 1])); start = xs[i]
    out.append((start, xs[-1]))
    return out

# crotch: lowest slice that is ONE cluster (scan upward from mid-thigh)
y_crotch = None
for y0 in np.arange(.30, 1.10, .015):
    cl = clusters_x(y0, y0 + .015, xmax=.30)   # ignore hands hanging beside
    if len(cl) == 1 and cl[0][0] < -.03 and cl[0][1] > .03:
        y_crotch = y0; break
# knee: anatomical fraction of the leg
y_knee = y_crotch * .535
y_ankle = .052 * H / 1.75 * 1.75 * .0 + .075   # ~7.5 cm
# leg lateral centres just above the knee
legs = clusters_x(y_knee + .04, y_knee + .10, xmax=.30)
legX = float(np.mean([abs((a + b) / 2) for a, b in legs])) if len(legs) == 2 else .10

# neck: narrowest slice BETWEEN shoulders and skull (the crown narrows
# too — bounding the scan keeps the minimum off the top of the head)
prof = []
for y0 in np.arange(1.40, 1.60, .01):
    b = V[(V[:, 1] >= y0) & (V[:, 1] < y0 + .01) & (np.abs(V[:, 0]) < .30)]
    if len(b): prof.append((y0, np.percentile(np.abs(b[:, 0]), 95)))
y_neck = min(prof, key=lambda p: p[1])[0]
y_top = V[:, 1].max()
skull = V[V[:, 1] > y_neck + .35 * (y_top - y_neck)]
skull_w = float(np.percentile(np.abs(skull[:, 0]), 97))
skull_ctr_y = float((y_neck + .35 * (y_top - y_neck) + y_top) / 2)
# eye line: widest z-extent band of the upper head; face front there
eye_y = y_neck + .55 * (y_top - y_neck)
eb = V[(V[:, 1] > eye_y - .02) & (V[:, 1] < eye_y + .02)]
face_z = float(np.percentile(eb[:, 2], 97))
chin_gap = eye_y - y_neck

# shoulder height for the arm-slice scan (refined by the arm fit below)
shoulder_y = 1.42

# arm axes from per-slice OUTER cluster centroids, y from wrist to armpit
arm = {}
for s in (1, -1):
    pts = []
    for y0 in np.arange(.70, shoulder_y, .02):
        cl = clusters_x(y0, y0 + .02)
        if len(cl) >= 3:
            seg = cl[-1] if s > 0 else cl[0]
            b = V[(V[:, 1] >= y0) & (V[:, 1] < y0 + .02) &
                  (V[:, 0] >= seg[0] - 1e-6) & (V[:, 0] <= seg[1] + 1e-6)]
            pts.append(b.mean(0))
    pts = np.array(pts)
    ctr = pts.mean(0)
    ax = np.linalg.svd(pts - ctr)[2][0]
    if ax[1] > 0: ax = -ax                     # point shoulder -> hand
    # shoulder = top end of the fitted segment
    tproj = (pts - ctr) @ ax
    sh = ctr + ax * tproj.min()
    # true tip: farthest mesh vert along the axis in this side
    cand = V[(V[:, 0] * s > .15) & (V[:, 1] > .55) & (V[:, 1] < shoulder_y + .05)]
    L = float(((cand - sh) @ ax).max())
    arm[s] = dict(ax=ax, sh=sh, L=L)
    print(f"arm {'R' if s>0 else 'L'} shoulder {sh.round(3)} axis {ax.round(3)} L {L:.3f}")

print(f"crotch {y_crotch:.3f} knee {y_knee:.3f} ankle {y_ankle:.3f} legX {legX:.3f}")
print(f"shoulder_y {shoulder_y:.3f} neck {y_neck:.3f} top {y_top:.3f} "
      f"skull_w {skull_w:.3f} skull_ctr {skull_ctr_y:.3f} eye_y {eye_y:.3f} face_z {face_z:.3f}")

waist_y = y_crotch + .13
chest_y = y_crotch + .30                      # chest joint height on the mesh

def arm_of(p):
    """the axis radius alone separates arm from body — hands hang beside
    the thighs, so no height gate (v1's mistake fused hands into thighs)"""
    for s in (1, -1):
        a = arm[s]
        rel = p - a["sh"]; t = float(rel @ a["ax"])
        if -.03 <= t <= a["L"] + .02:
            d = float(np.linalg.norm(rel - t * a["ax"]))
            if d < .105 and p[0] * s > legX + .04:
                return s, t
    return None

def region(p):
    ai = arm_of(p)
    if ai:
        s, t = ai; side = "R" if s > 0 else "L"; L = arm[s]["L"]
        if t > .78 * L: return "hand" + side
        if t > .47 * L: return "fore" + side
        return "upper" + side
    y = p[1]
    if y >= y_neck - .01: return "head"
    if y >= waist_y: return "torso"
    if y >= y_crotch - .015: return "pelvis"
    side = "R" if p[0] > 0 else "L"
    if y >= y_knee: return "thigh" + side
    if y >= y_ankle: return "shin" + side
    return "foot" + side

cent = V[F].mean(axis=1)
part_faces = collections.defaultdict(list)
for fi, c in enumerate(cent):
    part_faces[region(c)].append(fi)
for k in sorted(part_faces):
    print(f"  {k:8s}{len(part_faces[k]):5d} tris")

# joint anatomy (mesh space) — the scene applies these as rest offsets
J = {
    "pelvis": [0, y_crotch, 0],
    "hipL": [-legX, 0, 0], "hipR": [legX, 0, 0],           # rel pelvis
    "kneeY": -(y_crotch - y_knee), "ankleY": -(y_knee - y_ankle),
    "spineY": (chest_y - y_crotch) * .38,
    "chestY": (chest_y - y_crotch) * .62,
    "neckY": y_neck - chest_y,
    "headY": skull_ctr_y - y_neck,
    "shX": float(np.mean([abs(arm[s]["sh"][0]) for s in (1, -1)])),
    "shYrel": float(np.mean([arm[s]["sh"][1] for s in (1, -1)])) - chest_y,
    "upperL_": .47, "foreL_": .31, "handL_": .22,
    "skullW": skull_w, "eyeY": eye_y - skull_ctr_y, "faceZ": face_z,
}
# arm segment lengths along the axis
armL = float(np.mean([arm[s]["L"] for s in (1, -1)]))
J["upperLen"] = armL * .47; J["foreLen"] = armL * .31; J["handLen"] = armL * .22

# per-part origin (mesh space) + optional rotation (arms -> -y)
def rot_to_down(ax):
    d = np.array([0., -1., 0.])
    v = np.cross(ax, d); c = float(ax @ d)
    if np.linalg.norm(v) < 1e-8: return np.eye(3) * (1 if c > 0 else -1)
    vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + vx + vx @ vx / (1 + c)

T = {}
for side, s in (("R", 1), ("L", -1)):
    T["thigh" + side] = dict(o=[s * legX, y_crotch, 0])
    T["shin" + side] = dict(o=[s * legX, y_knee, 0])
    T["foot" + side] = dict(o=[s * legX, y_ankle, 0])
    a = arm[s]; R = rot_to_down(a["ax"])
    T["upper" + side] = dict(o=a["sh"], R=R)
    T["fore" + side] = dict(o=a["sh"] + a["ax"] * J["upperLen"], R=R)
    T["hand" + side] = dict(o=a["sh"] + a["ax"] * (J["upperLen"] + J["foreLen"]), R=R)
T["pelvis"] = dict(o=[0, y_crotch, 0])
T["torso"] = dict(o=[0, chest_y, 0])
T["head"] = dict(o=[0, skull_ctr_y, face_z * 0], oz=0)
T["head"]["o"] = [0, skull_ctr_y, 0]

def q(x, dp=3):
    s = f"{x:.{dp}f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s

out = ["# male NPC segments v2 — mesh proportions kept, joint-local coords"]
vtotal = 0
for part in sorted(part_faces):
    t = T[part]
    fids = part_faces[part]
    vids = np.unique(F[fids])
    remap = {v: i for i, v in enumerate(vids)}
    P = V[vids] - np.array(t["o"])
    if "R" in t: P = P @ t["R"].T
    tris = np.array([[remap[a] for a in F[f]] for f in fids])
    keys = [f"{q(p[0])}/{q(p[1])}/{q(p[2])}" for p in P]
    weld = {}
    for i, kk in enumerate(keys): weld.setdefault(kk, []).append(i)
    N = np.zeros_like(P)
    fn = np.cross(P[tris[:, 1]] - P[tris[:, 0]], P[tris[:, 2]] - P[tris[:, 0]])
    for ti, tr in enumerate(tris):
        for c in tr: N[c] += fn[ti]
    for kk, grp in weld.items():
        if len(grp) > 1: N[grp] = N[grp].sum(0)
    ln = np.linalg.norm(N, axis=1); ln[ln == 0] = 1
    N /= ln[:, None]
    out.append(f"o {part}"); out.append(f"usemtl {part}")
    base_v = vtotal
    for p in P: out.append(f"v {q(p[0])} {q(p[1])} {q(p[2])}")
    nmap, nout, nidx = {}, [], []
    for n in N:
        kk = f"{q(n[0],2)} {q(n[1],2)} {q(n[2],2)}"
        if kk not in nmap: nmap[kk] = len(nout); nout.append(kk)
        nidx.append(nmap[kk])
    nbase = sum(1 for l in out if l.startswith("vn "))
    out += ["vn " + n for n in nout]
    out += ["f " + " ".join(f"{base_v+c+1}//{nbase+nidx[c]+1}" for c in tr) for tr in tris]
    vtotal += len(P)

open(DST, "w").write("\n".join(out) + "\n")
import os
print(f"\nwritten {DST} {os.path.getsize(DST)/1e3:.0f} KB, {vtotal} verts")
print("\n=== PASTE INTO index.html (HUMAN geometry constants) ===")
print("const HUMAN=" + json.dumps({k: (round(v, 4) if isinstance(v, float) else v)
      for k, v in J.items() if not k.endswith("_")}, indent=0).replace("\n", "") + ";")
