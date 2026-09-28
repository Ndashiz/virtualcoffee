"""Pack the pipeline's outputs into people.bin — the format the café reads.
Layout: 'VCP1' | uint32 header length | header JSON (utf8, space-padded to 4)
| chunks, each 4-byte aligned; the header says where each lives and how to
dequantise it. Meshes: the body, then every garment (same bone order);
body.mask flags, per body face, which garments hide it (bit = order in
header.garments). Runs under Blender's python (numpy)."""
import json, os, struct, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out")
DST = os.environ.get("DST", os.path.join(HERE, "..", "people.bin"))
GARMENTS = ["tee", "shirt", "sweater", "trousers", "shoes", "blazer", "apron"]
HAIR = ["buzz", "short", "fade", "bun", "pony", "bob", "long", "curly"]
KIND = {"body": 0, "tee": 1, "shirt": 1, "sweater": 2, "trousers": 3, "shoes": 4, "blazer": 2, "apron": 1}

blob = bytearray(); chunks = {}
def add(name, arr, **meta):
    global blob
    arr = np.ascontiguousarray(arr)
    while len(blob) % 4: blob += b"\0"
    chunks[name] = dict(off=len(blob), n=int(arr.size), t=arr.dtype.str.lstrip("<|="), **meta)
    blob += arr.tobytes()

def mesh(name, co, tri, skI, skW, part=None):
    co = co.astype(np.float64)
    lo = co.min(0); span = np.maximum(co.max(0) - lo, 1e-6)
    q = np.round((co - lo) / span * 65535 - 32768).astype(np.int16)        # ~0.03 mm steps
    add(name + ".pos", q, lo=[round(float(v), 6) for v in lo], span=[round(float(v), 6) for v in span])
    add(name + ".index", tri.astype(np.uint16))
    add(name + ".skinIndex", skI.astype(np.uint8))
    w8 = np.round(skW * 255).astype(np.int32)
    w8[:, 0] += 255 - w8.sum(1)                                             # sums to exactly 255
    add(name + ".skinWeight", np.clip(w8, 0, 255).astype(np.uint8))
    if part is not None: add(name + ".part", part.astype(np.uint8))
    return dict(verts=int(len(co)), tris=int(len(tri)))

rig = json.load(open(os.path.join(OUT, "rig.json")))
meshes = {}
meshes["body"] = mesh("body", np.load(os.path.join(OUT, "rest_co.npy")), np.load(os.path.join(OUT, "rest_tri.npy")),
                      np.load(os.path.join(OUT, "skI.npy")), np.load(os.path.join(OUT, "skW.npy")))
M = np.load(os.path.join(OUT, "bodymask.npz"))
mask = np.zeros(meshes["body"]["tris"], np.uint16)
for b, g in enumerate(GARMENTS):
    d = np.load(os.path.join(OUT, "g_" + g + ".npz"))
    meshes[g] = mesh(g, d["pos"], d["tri"], d["skI"], d["skW"], d["part"] if "part" in d else None)
    mask |= (M[g].astype(np.uint16) << b)
add("body.mask", mask)
for h in HAIR:
    d = np.load(os.path.join(OUT, "g_hair_" + h + ".npz"))
    meshes["hair_" + h] = mesh("hair_" + h, d["pos"], d["tri"], d["skI"], d["skW"])
face = json.load(open(os.path.join(OUT, "face.json")))
# LOD1: the same parts decimated (pp_lod.py), suffix "@1", and the body's mask for them
if os.path.exists(os.path.join(OUT, "lod1_body.npz")):
    for n in ["body"] + GARMENTS + ["hair_" + h for h in HAIR]:
        d = np.load(os.path.join(OUT, "lod1_" + n + ".npz"))
        meshes[n + "@1"] = mesh(n + "@1", d["pos"], d["tri"], d["skI"], d["skW"], d["part"] if "part" in d else None)
    M1 = np.load(os.path.join(OUT, "lod1_bodymask.npz"))
    mask1 = np.zeros(meshes["body@1"]["tris"], np.uint16)
    for b, g in enumerate(GARMENTS):
        if g in M1: mask1 |= (M1[g].astype(np.uint16) << b)
    add("body@1.mask", mask1)

header = dict(v=2, H=rig["H"], bones=rig["bones"], joints=rig["joints"], lengths=rig["lengths"],
              garments=GARMENTS, hair=HAIR, kind=KIND, face=face, meshes=meshes, chunks=chunks)
hj = json.dumps(header, separators=(",", ":")).encode("utf8")
while len(hj) % 4: hj += b" "
with open(DST, "wb") as f:
    f.write(b"VCP1"); f.write(struct.pack("<I", len(hj))); f.write(hj); f.write(blob)
print("[exp] wrote", DST, os.path.getsize(DST), "bytes;", {k: v["tris"] for k, v in meshes.items()})
