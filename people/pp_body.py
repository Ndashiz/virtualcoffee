"""M1 — FinalBaseMesh -> rig rest pose, skinned to the café rig's joints.
Run: blender -b --python pp_body.py -- [stage]
Coordinates are three.js's throughout: Y up, face toward +Z, feet at y=0
(the OBJ is already Y-up; imported with NO axis conversion)."""
import bpy, bmesh, json, math, sys, os
import numpy as np
from mathutils import Vector, Matrix, Quaternion

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
H = 1.75                      # the height HUMAN was measured at: pelvis .855
TARGET_TRIS = int(os.environ.get("TRIS", "11000"))

def log(*a): print("[pp]", *a, flush=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.obj_import(filepath=os.path.join(HERE, "FinalBaseMesh.obj"),
                      forward_axis='Y', up_axis='Z')
body = [o for o in bpy.data.objects if o.type == 'MESH'][0]
body.name = "body"
bpy.context.view_layer.objects.active = body
body.select_set(True)

# --- scale, floor, centre, face +z ---
me = body.data
co = np.array([v.co[:] for v in me.vertices])
log("raw bounds", co.min(0).round(3), co.max(0).round(3))
co[:, 1] -= co[:, 1].min()
co *= H / co[:, 1].max()
co[:, 0] -= (co[:, 0].min() + co[:, 0].max()) / 2
band = co[(co[:, 1] > .95) & (co[:, 1] < 1.15)]
co[:, 2] -= band[:, 2].mean()
head = co[co[:, 1] > 1.58]
if head[np.abs(head[:, 2]).argmax()][2] < 0:
    co[:, 0] *= -1; co[:, 2] *= -1; log("flipped to face +z")
for i, v in enumerate(me.vertices): v.co = co[i]
me.update()

# --- decimate per region, symmetric, then triangulate ---
# the face carries the likeness: kept whole. The hands carry the gestures:
# a quarter. The body will mostly sit under clothes: what is left.
tris0 = sum(len(p.vertices) - 2 for p in me.polygons)
def region(c):
    x, y, z = c
    return "head" if (y > 1.47 and abs(x) < .13) else ("hand" if (abs(x) > .36 and y < 1.02) else "body")
RATIO = {"hand": float(os.environ.get("R_HAND", ".24")), "body": float(os.environ.get("R_BODY", ".15"))}
bpy.ops.object.mode_set(mode="EDIT")
for reg in ("hand", "body"):
    bm = bmesh.from_edit_mesh(me)
    for f in bm.faces:
        f.select_set(all(region(v.co) == reg for v in f.verts))
    bmesh.update_edit_mesh(me)
    bpy.ops.mesh.decimate(ratio=RATIO[reg], use_symmetry=True, symmetry_axis="X")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.object.mode_set(mode="OBJECT")
bm = bmesh.new(); bm.from_mesh(me)
bmesh.ops.triangulate(bm, faces=bm.faces[:])
bm.to_mesh(me); bm.free(); me.update()
log("tris", tris0, "->", len(me.polygons), "verts", len(me.vertices))

np.save(os.path.join(OUT, "stage1_co.npy"), np.array([v.co[:] for v in me.vertices]))
np.save(os.path.join(OUT, "stage1_tri.npy"), np.array([p.vertices[:] for p in me.polygons]))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "stage1.blend"))
log("saved stage1")
co1 = np.array([v.co[:] for v in me.vertices]); tri1 = np.array([p.vertices[:] for p in me.polygons])
cy = co1[tri1].mean(1)[:, 1]; cx = np.abs(co1[tri1].mean(1)[:, 0])
log("tris head", int(((cy > 1.47) & (cx < .13)).sum()), "hands", int(((cx > .36) & (cy < 1.02)).sum()), "rest", int(((cy <= 1.47) & ~((cx > .36) & (cy < 1.02))).sum()))
