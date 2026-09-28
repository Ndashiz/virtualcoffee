"""M1 stage 2 — landmarks (girth profiles), armature, heat weights, re-pose to
the café rig's rest pose (limbs straight down), export.
Continues from out/stage1.blend. Three.js coords (Y up, face +Z)."""
import bpy, json, math, os, sys
import numpy as np
from mathutils import Vector, Matrix
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out")
sys.path.insert(0, HERE)
import landmarks2
H = 1.75
PELVIS = .855            # fixed by the café: every seat was measured against it
Y_SH = .805 * H          # glenohumeral centre height (anthropometric)
def log(*a): print("[pp]", *a, flush=True)

V, F4 = landmarks2.load(H)
LMm = landmarks2.measure(V, F4, H, PELVIS)
A, L, X = LMm["arm"], LMm["leg"], LMm["axial"]
log("measured", json.dumps(LMm, default=lambda o: round(o, 4)))

# section centroids for the axial joints (their z, and x ~ 0)
def centroid_z(y, xmax=.2):
    b = V[(np.abs(V[:, 1] - y) < .004) & (np.abs(V[:, 0]) < xmax)]
    return float((b[:, 2].min() + b[:, 2].max()) / 2)
axz = {k: centroid_z(X[k], .12 if k in ("neck", "head") else .2) for k in ("spine", "chest", "neck", "head")}
toe = V[(V[:, 1] < .06) & (V[:, 0] > .03)]
toe_tip = toe[np.argmax(toe[:, 2])]
log("axial z", axz, "toe tip", toe_tip.round(3))

bpy.ops.wm.open_mainfile(filepath=os.path.join(OUT, "stage1.blend"))
body = bpy.data.objects["body"]; me = body.data

# ---------- armature: segments on the limbs' centre lines (heat weights) ----------
el = np.array(A["elbow"]); wr = np.array(A["wrist"]); tip = np.array(A["tip"])
ax = np.array(A["axis"])
c_sh = el - ax * A["t_elbow"]                  # the arm axis at the shoulder (as v1, weights looked right)
hipP = np.array(L["hip"]); kneeP = np.array(L["knee"]); ankP = np.array(L["ankle"])
mir = lambda p, s: [s * p[0], p[1], p[2]]
arm_data = bpy.data.armatures.new("rig"); rig = bpy.data.objects.new("rig", arm_data)
bpy.context.scene.collection.objects.link(rig)
bpy.context.view_layer.objects.active = rig
bpy.ops.object.mode_set(mode='EDIT')
eb = arm_data.edit_bones
def bone(name, h, t, parent=None):
    b = eb.new(name); b.head = Vector(h); b.tail = Vector(t)
    if parent: b.parent = eb[parent]
    return b
nk = X["neck"]
bone("pelvis", (0, PELVIS - .07, -.01), (0, X["spine"], axz["spine"]))
bone("spine", (0, X["spine"], axz["spine"]), (0, X["chest"], axz["chest"]), "pelvis")
bone("chest", (0, X["chest"], axz["chest"]), (0, nk - .07, axz["neck"]), "spine")
bone("neck", (0, nk - .07, axz["neck"]), (0, nk + .06, axz["neck"] + .01), "chest")
bone("head", (0, nk + .06, axz["neck"] + .01), (0, X["top"], axz["head"]), "neck")
for s, S in ((-1, "L"), (1, "R")):
    bone("shoulder" + S, mir(c_sh, s), mir(el, s), "chest")
    bone("elbow" + S, mir(el, s), mir(wr, s), "shoulder" + S)
    bone("wrist" + S, mir(wr, s), mir(tip, s), "elbow" + S)
    bone("hip" + S, mir(hipP, s), mir(kneeP, s), "pelvis")
    bone("knee" + S, mir(kneeP, s), mir(ankP, s), "hip" + S)
    bone("ankle" + S, mir(ankP, s), mir([toe_tip[0], .02, toe_tip[2] - .03], s), "knee" + S)
bpy.ops.object.mode_set(mode='OBJECT')

bpy.ops.object.select_all(action='DESELECT')
body.select_set(True); rig.select_set(True)
bpy.context.view_layer.objects.active = rig
bpy.ops.object.parent_set(type='ARMATURE_AUTO')
log("verts without weights:", sum(1 for v in me.vertices if len(v.groups) == 0))

# ---------- re-pose to the rig's rest: every limb segment straight down ----------
body.modifiers[0].use_deform_preserve_volume = True       # DQS while reposing
bpy.context.view_layer.objects.active = rig
bpy.ops.object.mode_set(mode='POSE')
DOWN = Vector((0, -1, 0))
def about(p, R):
    p = Vector(p); return Matrix.Translation(p) @ R.to_4x4() @ Matrix.Translation(-p)
def frontal(a, b):          # rotation about Z that puts a->b vertical in the front view
    v = Vector(b) - Vector(a); return Matrix.Rotation(-math.atan2(v.x, -v.y), 3, 'Z')
def full(a, b):
    return (Vector(b) - Vector(a)).rotation_difference(DOWN).to_matrix()
def turn(name, M):
    pb = rig.pose.bones[name]; pb.matrix = M @ pb.matrix; bpy.context.view_layer.update()
J = {"pelvis": [0, PELVIS, 0], "spine": [0, X["spine"], axz["spine"]], "chest": [0, X["chest"], axz["chest"]],
     "neck": [0, nk, axz["neck"]], "head": [0, X["head"], axz["head"]]}
LEN = {}
for s, S in ((-1, "L"), (1, "R")):
    # arm: upper arm swung down in the frontal plane about the shoulder axis
    # point (keeps the modelled sagittal hang), then forearm and hand straightened
    P0 = Vector(mir(c_sh, s)); e = Vector(mir(el, s)); w = Vector(mir(wr, s)); t = Vector(mir(tip, s))
    M1 = about(P0, frontal(P0, e)); turn("shoulder" + S, M1); e, w, t = M1 @ e, M1 @ w, M1 @ t
    M2 = about(e, full(e, w)); turn("elbow" + S, M2); w, t = M2 @ w, M2 @ t
    M3 = about(w, full(w, t)); turn("wrist" + S, M3); t = M3 @ t
    J["shoulder" + S] = [e.x, Y_SH, e.z]; J["elbow" + S] = list(e); J["wrist" + S] = list(w)
    LEN["upLen"], LEN["foreLen"], LEN["handLen"] = Y_SH - e.y, e.y - w.y, w.y - t.y
    # leg: thigh and shank straightened in the frontal plane only
    h = Vector(mir(hipP, s)); k = Vector(mir(kneeP, s)); a = Vector(mir(ankP, s))
    M4 = about(h, frontal(h, k)); turn("hip" + S, M4); k, a = M4 @ k, M4 @ a
    M5 = about(k, frontal(k, a)); turn("knee" + S, M5); a = M5 @ a
    J["hip" + S] = list(h); J["knee" + S] = list(k); J["ankle" + S] = list(a)
    LEN["thigh"], LEN["shank"] = h.y - k.y, k.y - a.y
bpy.ops.object.mode_set(mode='OBJECT')
bpy.context.view_layer.objects.active = body
bpy.ops.object.modifier_apply(modifier=body.modifiers[0].name)
co = np.array([v.co[:] for v in me.vertices], dtype=np.float32)
log("re-posed; floor", co[:, 1].min().round(4), "top", co[:, 1].max().round(4))

# ---------- export ----------
tri = np.array([p.vertices[:] for p in me.polygons], dtype=np.uint16)
names = [g.name for g in body.vertex_groups]
skI = np.zeros((len(co), 4), np.uint8); skW = np.zeros((len(co), 4), np.float32)
for v in me.vertices:
    gs = sorted(((g.weight, g.group) for g in v.groups if g.weight > 1e-4), reverse=True)[:4]
    tot = sum(w_ for w_, _ in gs) or 1
    for q, (w_, gi) in enumerate(gs): skI[v.index, q] = gi; skW[v.index, q] = w_ / tot
J = {k: [round(float(c), 5) for c in v] for k, v in J.items()}
out = dict(H=H, joints=J, lengths={k: round(float(v), 5) for k, v in LEN.items()}, bones=names,
           measured=LMm, toe=toe_tip.tolist())
json.dump(out, open(os.path.join(OUT, "rig.json"), "w"), indent=1, default=float)
np.save(os.path.join(OUT, "rest_co.npy"), co); np.save(os.path.join(OUT, "rest_tri.npy"), tri)
np.save(os.path.join(OUT, "skI.npy"), skI); np.save(os.path.join(OUT, "skW.npy"), skW)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "stage2.blend"))
log("joints", json.dumps(J)); log("lengths", json.dumps(out["lengths"]))
log("exported", len(co), "verts", len(tri), "tris")
