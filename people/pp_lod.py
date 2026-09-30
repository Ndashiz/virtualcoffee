"""M8 — LOD1: every part decimated (collapse, weights carried by Blender's
vertex groups), for phones and for people across the room. The body's
per-face 'hidden by garment' mask is inherited from the nearest LOD0 face.
Writes out/lod1_<name>.npz (pos, tri, skI, skW[, part]) and out/lod1_bodymask.npz."""
import bpy, os, sys, json
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out")
sys.path.insert(0, HERE)
import garmentlib as G
def log(*a): print("[lod]", *a, flush=True)
rig = json.load(open(os.path.join(OUT, "rig.json"))); bones = rig["bones"]
RATIO = {"body": .34, "hair": .42, "shoes": .40, "default": .36}

def load(name):
    if name == "body":
        return dict(pos=np.load(os.path.join(OUT, "rest_co.npy")), tri=np.load(os.path.join(OUT, "rest_tri.npy")),
                    skI=np.load(os.path.join(OUT, "skI.npy")), skW=np.load(os.path.join(OUT, "skW.npy")))
    return dict(np.load(os.path.join(OUT, "g_" + name + ".npz")))

def decimate(d, ratio, face_safe=False):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    P = d["pos"].astype(np.float64); F = d["tri"].astype(np.int64)
    me = bpy.data.meshes.new("m"); me.from_pydata(P.tolist(), [], F.tolist()); me.update()
    o = bpy.data.objects.new("m", me); bpy.context.scene.collection.objects.link(o)
    groups = [o.vertex_groups.new(name=b) for b in bones]
    for i in range(len(P)):
        for k in range(4):
            w = float(d["skW"][i, k])
            if w > 1e-4: groups[int(d["skI"][i, k])].add([i], w, 'ADD')
    part = d.get("part")
    if part is not None:
        pg = o.vertex_groups.new(name="__part")
        idx = np.where(part > 0)[0].tolist()
        if idx: pg.add(idx, 1.0, 'REPLACE')
    bpy.context.view_layer.objects.active = o; o.select_set(True)
    import bmesh
    if face_safe:
        # The face is where a decimation shows: collapse moved the lip line and
        # the lid rims, and the painted mouth and lash lines (laid out on the
        # original surface) slid off them — every distant face looked shifted.
        # Protecting only eyes, mouth and nose was not enough (2026-09-29):
        # the rest of the head, halved WITHOUT symmetry, came out with one
        # cheek and one side of the jaw wider than the other, and from across
        # the room a lopsided head reads as a face that is off-centre. So the
        # whole head AND the neck are kept exactly as LOD0, and so are the
        # hands (pp_body already took them to x.24; any further and the
        # fingers go to spikes).
        # They are kept OUT OF THE SELECTION, not weighted: the collapse only
        # sees the rest of the body and `ratio` is a share of THAT. The first
        # version weighted them inside one global collapse — and the head alone
        # is more than .34 of the body's triangles, so to reach the target the
        # collapse ate everything it was allowed to touch: every arm, leg and
        # foot in the room went to a few slivers past 6 m (2026-09-30, "le
        # livreur n'a pas de bras"). Symmetric, like every other part: the
        # head it once threw a shard from is not in the selection any more.
        bm = bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table()
        skI = d["skI"]
        for v in bm.verts:
            x, y, z = v.co
            lead = bones[int(skI[v.index, 0])]
            v.select = not (lead in ("head", "neck", "wristL", "wristR") or y > 1.45 or (y > 1.53 and abs(x) < .13))
        for e in bm.edges: e.select = all(v.select for v in e.verts)
        for f in bm.faces: f.select = all(v.select for v in f.verts)
        nsel = sum(1 for f in bm.faces if f.select)
        bm.to_mesh(o.data); bm.free()
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.decimate(ratio=ratio, use_symmetry=True, symmetry_axis='X')
        bpy.ops.object.mode_set(mode='OBJECT')
        log("body: collapsed", nsel, "of", len(F), "faces at", ratio, "->", len(o.data.polygons) - (len(F) - nsel))
    else:
        m = o.modifiers.new("d", 'DECIMATE'); m.decimate_type = 'COLLAPSE'; m.ratio = ratio
        m.use_symmetry = True; m.symmetry_axis = 'X'
        bpy.ops.object.modifier_apply(modifier="d")
    bm = bmesh.new(); bm.from_mesh(o.data); bmesh.ops.triangulate(bm, faces=bm.faces[:]); bm.to_mesh(o.data); bm.free()
    me = o.data
    P2 = np.array([v.co[:] for v in me.vertices], np.float32); F2 = np.array([p.vertices[:] for p in me.polygons], np.int64)
    W = np.zeros((len(P2), len(bones))); pw = np.zeros(len(P2))
    names = [g.name for g in o.vertex_groups]
    for v in me.vertices:
        for g in v.groups:
            n = names[g.group]
            if n == "__part": pw[v.index] = g.weight
            elif n == "__keep": pass
            else: W[v.index, bones.index(n)] = g.weight
    I, Wt = G.top4(W)
    out = dict(pos=P2, tri=F2.astype(np.uint16), skI=I, skW=Wt)
    if part is not None: out["part"] = (pw > .5).astype(np.uint8)
    return out

names = ["body", "tee", "shirt", "sweater", "trousers", "shoes", "blazer", "apron",
         "hair_buzz", "hair_short", "hair_fade", "hair_curly", "hair_bun", "hair_pony", "hair_bob", "hair_long"]
res = {}
for n in names:
    d = load(n)
    r = RATIO["body"] if n == "body" else RATIO["hair"] if n.startswith("hair") else RATIO.get(n, RATIO["default"])
    res[n] = decimate(d, r, face_safe=(n == "body"))
    # a limb the collapse ate is invisible in the numbers above (the head
    # holds most of the body's triangles), so count what each bone still leads
    lead = lambda I, W: np.bincount(I[np.arange(len(I)), W.argmax(1)], minlength=len(bones))
    l0, l1 = lead(d["skI"], d["skW"]), lead(res[n]["skI"], res[n]["skW"])
    lost = [bones[b] for b in range(len(bones)) if l0[b] >= 20 and l1[b] < .15 * l0[b]]
    if lost: raise SystemExit("[lod] %s: the collapse ate %s" % (n, ", ".join(lost)))
    np.savez(os.path.join(OUT, "lod1_" + n + ".npz"), **res[n])
    log(n, len(d["tri"]), "->", len(res[n]["tri"]))
# body mask: each LOD1 face takes the mask of the LOD0 face nearest its centre
V0 = np.load(os.path.join(OUT, "rest_co.npy")).astype(np.float64); T0 = np.load(os.path.join(OUT, "rest_tri.npy")).astype(np.int64)
M0 = np.load(os.path.join(OUT, "bodymask.npz"))
bvh = BVHTree.FromPolygons([Vector(p) for p in V0], T0.tolist())
b1 = res["body"]; C1 = b1["pos"][b1["tri"].astype(np.int64)].mean(1)
near = np.array([bvh.find_nearest(Vector(c))[2] for c in C1])
np.savez(os.path.join(OUT, "lod1_bodymask.npz"), **{k: M0[k][near] for k in M0.files})
log("body mask carried over", len(C1), "faces")
