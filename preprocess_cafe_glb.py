#!/usr/bin/env python3
"""cafe.glb -> cafe.obj preprocessor for Virtual Coffee.

Supersedes preprocess_cafe_obj.py: the stage tool now exports glTF-binary
(THREE.GLTFExporter r184) instead of Wavefront, and the map grew a front wall
with a trophy cabinet, a street with a van, a forest, and two baked stand-ins
of Simon.

What it does:
  * flattens the glTF node tree into world space (1940 of the 3789 nodes carry
    a rotation or a scale, so the full 4x4 matrix is applied, normals through
    the inverse-transpose);
  * DROPS the two baked characters -- the scene has its own rigged Simon and
    its own capsule cast, three Simons on screen is not a look;
  * PRUNES the forest to the parking side only (the storefront is the shot
    that sees it; the window side keeps the painted city gradient);
  * DROPS the three framed press clippings on the front wall (see DROP_NAMES);
  * re-applies the staging gestures the export does not carry: chalkboard
    nudged clear of Simon's head, T1 tabletop widened 1.5x so the resume sheet
    fits, T1 chair swung round behind the table facing the camera, the plant
    moved off the one wall a toilet door fits on, the eight wheels turned a
    quarter (the export mounts them sideways), and the ICE CUBE lettering
    copied onto the van's rear doors;
  * CLONES the van one parking bay over as a second firm (BravoReno), with
    its own lettering material, which the scene paints;
  * puts everything in FINAL WORLD COORDINATES -- same frame as before, so
    every hard-coded anchor in index.html still lands (scale derived from T1's
    tabletop at y=0.8025, shift so T1 sits at (0,-0.15));
  * quantizes (v 4dp, vt/vn 3dp), dedupes the pools, keeps vt only where a
    material is actually textured, re-emits the compact OBJ that index.html's
    own ~60-line parser reads;
  * extracts the label textures (trophies, diplomas, press clippings, van
    lettering) as PNG files next to the model.

Run it again whenever the map is re-exported. The world anchors it prints are
the ones the scene code is written against.
"""
import os, sys, math, json, struct, collections

SRC     = os.path.expanduser("~/Downloads/cafe.glb")
# .obj is served as application/x-tgif, which the CDN does not compress -- the
# old 1.35 MB model went over the wire whole. A text extension is served as
# text/plain and gzips 5:1 (three.min.js: 615 KB -> 154 KB on the same host).
# The loader fetches a URL and parses text; the extension is nothing to it.
DST     = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cafe.obj.txt")
TEX_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tex")

# ---------------------------------------------------------------- pruning ---
# The two baked stand-ins. The scene builds its own Simon and its own cast.
DROP_GROUPS = {"moi_au_comptoir", "moi_assis_table_haute"}

# The three framed press clippings on the front wall -- Simon's call: the
# room already carries the CV, a wall of invented headlines about himself
# reads as bragging, not as scenery. The back-wall pair drawPress() built in
# JS went with them. Exact names only: cadre_carte (the chalkboard) and
# cadre_diplome (the cabinet) keep theirs.
DROP_NAMES = {"cadre", "passe_partout", "article"}

# Forest: 280k triangles blanket 160 m in every direction, for scenery the
# room can only glimpse. Keep the wedge the storefront actually frames -- a
# cone from Simon's table through the two door jambs, widened for the camera's
# travel -- and cap it where a tree stops being more than a few pixels.
FOREST_GROUP   = "foret"
FOREST_MIN_X   = 4.94     # model units; the storefront glass sits at x=4.99
FOREST_MAX_X   = 50.0     # past this a 6 m tree is sub-pixel through the door
FOREST_EYE     = (-1.75, 0.30)          # Simon's table, where the camera lives
FOREST_DOOR_X  = 4.99                   # storefront plane
FOREST_DOOR_Z  = (-4.17, 4.17)          # its two jambs
FOREST_SPREAD  = 1.6      # widen the cone: the camera orbits and dollies

# Materials that carry a map in index.html's MATS table (procedural or baked).
# Anything else drops its vt and writes `v//vn`, which is most of the file.
TEXTURED = {
    # procedural textures painted by the scene
    "chene_sol", "platre", "platre_vert", "carte", "tapis",
    "noyer", "noyer_clair", "marbre", "enseigne_porte",
    # baked label textures shipped alongside the model
    "plaque_palmares", "etq_pspo", "etq_psm", "etq_dynamics", "etq_azure",
    "etq_solvay", "etq_wagon", "etq_parcours",
    "face_trophee_dynamics_365", "face_trophee_azure",
    "parch_diplome_solvay", "parch_certification_le_wagon",
    "lettrage_ice_cube", "lettrage_bravoreno",
}

# The scene paints these itself; no point shipping the baked copy.
SKIP_TEXTURE_EXPORT = {"chene_sol", "carte", "vitrophanie", "enseigne_porte"}

# ------------------------------------------------------------- glb reader ---
CT    = {5120: ('b', 1), 5121: ('B', 1), 5122: ('h', 2),
         5123: ('H', 2), 5125: ('I', 4), 5126: ('f', 4)}
NCOMP = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}


def load_glb(path):
    d = open(path, 'rb').read()
    if d[:4] != b'glTF':
        sys.exit("not a glb: " + path)
    off, js, binoff = 12, None, None
    while off < len(d):
        clen, ctype = struct.unpack_from('<II', d, off)
        off += 8
        if ctype == 0x4E4F534A:
            js = json.loads(d[off:off + clen])
        elif ctype == 0x004E4942:
            binoff = off
        off += clen
    return js, d, binoff


def read_accessor(js, d, binoff, idx):
    a    = js['accessors'][idx]
    n    = NCOMP[a['type']]
    f, s = CT[a['componentType']]
    bv   = js['bufferViews'][a['bufferView']]
    base = binoff + bv.get('byteOffset', 0) + a.get('byteOffset', 0)
    stride = bv.get('byteStride') or n * s
    if stride == n * s:
        flat = struct.unpack_from('<%d%s' % (a['count'] * n, f), d, base)
        return [flat[i * n:(i + 1) * n] for i in range(a['count'])]
    return [struct.unpack_from('<%d%s' % (n, f), d, base + i * stride)
            for i in range(a['count'])]


def mat_mul(A, B):
    """column-major; returns B * A, i.e. A applied then B (child then parent)."""
    return [sum(B[k * 4 + r] * A[c * 4 + k] for k in range(4))
            for c in range(4) for r in range(4)]


def node_matrix(n):
    if 'matrix' in n:
        return list(n['matrix'])
    m = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
    if 'rotation' in n:
        x, y, z, w = n['rotation']
        m = [1 - 2 * (y * y + z * z), 2 * (x * y + z * w), 2 * (x * z - y * w), 0,
             2 * (x * y - z * w), 1 - 2 * (x * x + z * z), 2 * (y * z + x * w), 0,
             2 * (x * z + y * w), 2 * (y * z - x * w), 1 - 2 * (x * x + y * y), 0,
             0, 0, 0, 1]
    if 'scale' in n:
        s = n['scale']
        for c in range(3):
            for r in range(3):
                m[c * 4 + r] *= s[c]
    if 'translation' in n:
        m[12], m[13], m[14] = n['translation']
    return m


def normal_matrix(m):
    """inverse-transpose of the upper 3x3, flattened row-major."""
    a, b, c = m[0], m[4], m[8]
    e, f, g = m[1], m[5], m[9]
    i, j, k = m[2], m[6], m[10]
    det = a * (f * k - g * j) - b * (e * k - g * i) + c * (e * j - f * i)
    if abs(det) < 1e-12:
        return (1, 0, 0, 0, 1, 0, 0, 0, 1)
    q = 1.0 / det
    return ((f * k - g * j) * q, -(e * k - g * i) * q, (e * j - f * i) * q,
            -(b * k - c * j) * q, (a * k - c * i) * q, -(a * j - b * i) * q,
            (b * g - c * f) * q, -(a * g - c * e) * q, (a * f - b * e) * q)


def flatten(js, d, binoff):
    """-> [{name, group, mat, tri:[(pos,nrm,uv)*3n]}] in model world space."""
    nodes, meshes = js['nodes'], js['meshes']
    mats  = js.get('materials', [])
    cache = {}

    def acc(i):
        if i not in cache:
            cache[i] = read_accessor(js, d, binoff, i)
        return cache[i]

    out = []

    def walk(ni, parent, group, inherited):
        n    = nodes[ni]
        m    = mat_mul(node_matrix(n), parent)
        name = n.get('name', inherited)
        if 'mesh' in n:
            nm = normal_matrix(m)
            for p in meshes[n['mesh']]['primitives']:
                at = p['attributes']
                P  = acc(at['POSITION'])
                N  = acc(at['NORMAL']) if 'NORMAL' in at else None
                U  = acc(at['TEXCOORD_0']) if 'TEXCOORD_0' in at else None
                idx = ([i[0] for i in acc(p['indices'])] if 'indices' in p
                       else list(range(len(P))))
                pos, nrm, uv = [], [], []
                for i in idx:
                    x, y, z = P[i][0], P[i][1], P[i][2]
                    pos.append([m[0] * x + m[4] * y + m[8] * z + m[12],
                                m[1] * x + m[5] * y + m[9] * z + m[13],
                                m[2] * x + m[6] * y + m[10] * z + m[14]])
                    if N:
                        x, y, z = N[i][0], N[i][1], N[i][2]
                        ox = nm[0] * x + nm[3] * y + nm[6] * z
                        oy = nm[1] * x + nm[4] * y + nm[7] * z
                        oz = nm[2] * x + nm[5] * y + nm[8] * z
                        l  = math.sqrt(ox * ox + oy * oy + oz * oz) or 1.0
                        nrm.append([ox / l, oy / l, oz / l])
                    else:
                        nrm.append([0.0, 1.0, 0.0])
                    uv.append(list(U[i]) if U else None)
                out.append({'name': name, 'group': group,
                            'mat': mats[p['material']]['name'] if 'material' in p else 'default',
                            'pos': pos, 'nrm': nrm, 'uv': uv})
        for c in n.get('children', []):
            walk(c, m, group, name)

    root = js['scenes'][js.get('scene', 0)]['nodes'][0]
    rm = node_matrix(nodes[root])
    for c in nodes[root].get('children', []):
        walk(c, rm, nodes[c].get('name', '?'), nodes[c].get('name', '?'))
    return out


# ------------------------------------------------------------------- main ---
def bbox(objs):
    lo, hi = [1e30] * 3, [-1e30] * 3
    for o in objs:
        for p in o['pos']:
            for k in range(3):
                if p[k] < lo[k]: lo[k] = p[k]
                if p[k] > hi[k]: hi[k] = p[k]
    return lo, hi


def tris(objs):
    return sum(len(o['pos']) for o in objs) // 3


def in_door_cone(x, z):
    """Is (x,z) inside the wedge the storefront frames, seen from the table?"""
    if not (FOREST_MIN_X < x < FOREST_MAX_X):
        return False
    ex, ez = FOREST_EYE
    depth = FOREST_DOOR_X - ex
    lo = (FOREST_DOOR_Z[0] - ez) / depth * FOREST_SPREAD
    hi = (FOREST_DOOR_Z[1] - ez) / depth * FOREST_SPREAD
    slope = (z - ez) / (x - ex)
    return lo <= slope <= hi


def main():
    js, d, binoff = load_glb(SRC)
    objs = flatten(js, d, binoff)
    total = tris(objs)
    print(f"flattened {len(objs)} primitives, {total} triangles")

    # ---------------------------------------------------------- pruning ---
    kept, dropped = [], collections.Counter()
    forest_kept = forest_drop = 0
    # A forest primitive is kept when its own centroid sits on the parking
    # side. Trunk and foliage are separate primitives, but a tree is ~2 m wide
    # and the nearest kept one stands at x=6.0, so nothing straddles the cut.
    # The natural ground and the clearing floor are 200 triangles for the whole
    # outside; they stay whatever happens, or the street opens onto a void.
    for o in objs:
        g = o['group']
        if g in DROP_GROUPS:
            dropped[g] += len(o['pos']) // 3
            continue
        if o['name'] in DROP_NAMES:
            dropped['presse_encadree'] += len(o['pos']) // 3
            continue
        if g == FOREST_GROUP and o['name'] not in ('sol_naturel', 'clairiere_sous_bois'):
            cx = sum(p[0] for p in o['pos']) / len(o['pos'])
            cz = sum(p[2] for p in o['pos']) / len(o['pos'])
            if not in_door_cone(cx, cz):
                forest_drop += len(o['pos']) // 3
                dropped[g] += len(o['pos']) // 3
                continue
            forest_kept += len(o['pos']) // 3
        kept.append(o)
    objs = kept
    for g, n in dropped.most_common():
        print(f"  dropped {g:22s} {n:7d} tris")
    print(f"  forest kept {forest_kept} tris / pruned {forest_drop}")
    print(f"kept {tris(objs)} triangles ({100*tris(objs)/total:.0f}% of the export)")

    # ------------------------------------------------- staging (model sp) ---
    byname = collections.defaultdict(list)
    for o in objs:
        byname[(o['group'], o['name'])].append(o)

    def sel(group, name=None):
        if name:
            return byname.get((group, name), [])
        return [o for o in objs if o['group'] == group]

    plateau = sel('table_1', 'plateau_table')
    if not plateau:
        sys.exit("table_1/plateau_table missing -- did the map get renamed?")
    lo, hi = bbox(plateau)
    T1C    = [(lo[0] + hi[0]) / 2, (lo[2] + hi[2]) / 2]
    T1_TOP = hi[1]
    SCALE  = 0.8025 / T1_TOP
    SHIFT_X = -T1C[0] * SCALE
    SHIFT_Z = -0.15 - T1C[1] * SCALE
    print(f"\nT1 centre model=({T1C[0]:.4f},{T1C[1]:.4f}) top={T1_TOP:.4f}")
    print(f"SCALE={SCALE:.6f}  SHIFT=({SHIFT_X:.4f},0,{SHIFT_Z:.4f})")

    def move(objects, dx=0.0, dy=0.0, dz=0.0):
        for o in objects:
            for p in o['pos']:
                p[0] += dx; p[1] += dy; p[2] += dz

    # 0) chalkboard: right + up, out of Simon's head and the pendant halos.
    #    (+0.75, +0.30) in world units, which is what the old model carried.
    menu = sel('cadre_carte') + sel('carte_prix')
    move(menu, dx=0.75 / SCALE, dy=0.30 / SCALE)

    # 1) T1 tabletop: 1.5x in x/z about its centre, so the resume sheet
    #    (0.62 x 0.877) clears the edge of what is otherwise a 0.49 m radius.
    for o in sel('table_1', 'plateau_table') + sel('table_1', 'bord_table'):
        for p in o['pos']:
            p[0] = T1C[0] + (p[0] - T1C[0]) * 1.5
            p[2] = T1C[1] + (p[2] - T1C[1]) * 1.5
        for n in o['nrm']:
            nx, ny, nz = n[0] / 1.5, n[1], n[2] / 1.5
            l = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
            n[0], n[1], n[2] = nx / l, ny / l, nz / l

    # 2) T1 chair: rotate -90 deg about the table axis so it sits behind the
    #    table facing the camera, then nudge it clear of the widened top.
    NUDGE = (0.0997, -0.0846)     # model space ~ world (+0.106, -0.09)
    for o in sel('chaise_1'):
        for p in o['pos']:
            dx, dz = p[0] - T1C[0], p[2] - T1C[1]
            p[0] = T1C[0] + (-dz) + NUDGE[0]      # rotY(-90): x' = -z, z' = x
            p[2] = T1C[1] + (dx) + NUDGE[1]
        for n in o['nrm']:
            n[0], n[2] = -n[2], n[0]

    # 3) The plant moves along the front wall, out of the left corner and
    #    over to the stretch right of the trophy cabinet. That corner is the
    #    only run of wall a toilet door fits on (the rest of the window wall
    #    IS window), and a door behind a ficus is not a door.
    #    (+6.69, +0.26) in world units.
    move(sel('plante'), dx=6.69 / SCALE, dz=0.255 / SCALE)

    # 4) WHEELS. The export mounts all eight of them sideways: the discs sit
    #    in the y/z plane while both vehicles run along x (headlights at max
    #    x, tail lights at min x), so the car reads as rolling on spinning
    #    tops. Turn each a quarter about its own hub. A wheel is symmetric
    #    about its axle, so which way round the quarter goes does not matter.
    wheels = [o for o in objs if o['name'] in ('pneu', 'jante')]
    for o in wheels:
        cx = (min(p[0] for p in o['pos']) + max(p[0] for p in o['pos'])) / 2
        cz = (min(p[2] for p in o['pos']) + max(p[2] for p in o['pos'])) / 2
        for p in o['pos']:
            dx, dz = p[0] - cx, p[2] - cz
            p[0], p[2] = cx - dz, cz + dx          # rotY: (x,z) -> (-z,x)
        for n in o['nrm']:
            n[0], n[2] = -n[2], n[0]
    print(f"  wheels squared up: {len(wheels)} primitives")

    # 5) The van's rear doors get the ICE CUBE lettering too. The map letters
    #    the two flanks only, and from inside the café the back of the van is
    #    what you actually see -- it is parked nose-out. Built off the flank
    #    quad so it keeps its texture, its aspect and its height off the road.
    flanks = [o for o in objs if o['name'] == 'lettrage_ice_cube']
    doors  = [o for o in objs if o['name'] == 'portes_arriere']
    if flanks and doors:
        src = flanks[0]
        fx = [p[0] for p in src['pos']]
        fy = [p[1] for p in src['pos']]
        dlo, dhi = bbox(doors)
        w  = (dhi[2] - dlo[2]) * 0.86                 # 86% of the door width
        h  = w * (max(fy) - min(fy)) / (max(fx) - min(fx))
        cy = (min(fy) + max(fy)) / 2                  # the flanks' own line
        cz = (dlo[2] + dhi[2]) / 2
        px = dlo[0] - 0.004                           # a hair proud of the doors
        # u grows with z: seen from behind (looking +x) that is screen-left to
        # screen-right, which is how the flanks read from their own side.
        quad = [(cz - w / 2, cy + h / 2, 0.0, 1.0), (cz - w / 2, cy - h / 2, 0.0, 0.0),
                (cz + w / 2, cy + h / 2, 1.0, 1.0), (cz - w / 2, cy - h / 2, 0.0, 0.0),
                (cz + w / 2, cy - h / 2, 1.0, 0.0), (cz + w / 2, cy + h / 2, 1.0, 1.0)]
        objs.append({'name': 'lettrage_ice_cube', 'group': doors[0]['group'],
                     'mat': src['mat'],
                     'pos': [[px, y, z] for z, y, u, v in quad],
                     'nrm': [[-1.0, 0.0, 0.0] for _ in quad],
                     'uv':  [[u, v] for z, y, u, v in quad]})
        print(f"  ICE CUBE lettered on the rear doors ({w:.2f} x {h:.2f} model units)")
    else:
        print("  !! van lettering/rear doors missing -- rear stays blank")

    # ------------------------------------------------- global transform ---
    for o in objs:
        for p in o['pos']:
            p[0] = p[0] * SCALE + SHIFT_X
            p[1] = p[1] * SCALE
            p[2] = p[2] * SCALE + SHIFT_Z

    # ------------------------------------------ second van (world space) ---
    # BravoReno, the electrician. One parking bay over from the ICE CUBE
    # van, same bodyshell, its own lettering and its own accent colour.
    # Picked by a BOX rather than by group -- the whole outside is a single
    # group in the export -- and a primitive only counts if it sits
    # ENTIRELY inside it, which is what keeps the 8 000-triangle asphalt
    # slab and the road out of the clone. The roof ice cube stays behind:
    # it belongs to the other firm.
    VAN_BOX = (11.20, 17.80, -0.35, 2.35)      # x0,x1,z0,z1, world
    VAN_DZ  = 2.542                            # exactly one bay (ligne_place_*)
    VAN_MAT = {"lettrage_ice_cube": "lettrage_bravoreno", "van_bleu": "van_jaune"}
    src = []
    for o in objs:
        if o['name'].startswith('glacon'):
            continue
        xs = [p[0] for p in o['pos']]
        zs = [p[2] for p in o['pos']]
        if (min(xs) >= VAN_BOX[0] and max(xs) <= VAN_BOX[1]
                and min(zs) >= VAN_BOX[2] and max(zs) <= VAN_BOX[3]):
            src.append(o)
    for o in src:
        objs.append({'name': o['name'], 'group': o['group'],
                     'mat': VAN_MAT.get(o['mat'], o['mat']),
                     'pos': [[p[0], p[1], p[2] + VAN_DZ] for p in o['pos']],
                     'nrm': [list(n) for n in o['nrm']],
                     'uv':  [list(u) if u else None for u in o['uv']]})
    print(f"\nBravoReno van: {len(src)} primitives cloned, dz=+{VAN_DZ}"
          f" ({tris(src)} tris)")

    # ------------------------------------------------------- anchor dump ---
    print("\n--- WORLD ANCHORS ---")
    for g in ("sol", "mur_fond", "mur_avant", "mur_gauche_bas", "fenetre_vitre",
              "devanture_droite", "paillasson", "comptoir", "carte_prix",
              "table_1", "chaise_1", "chaise_2", "table_2", "table_3",
              "table_4", "table_5", "table_haute_fenetre", "tapis_rond",
              "plante", "armoire_trophees", "parking_exterieur", "foret"):
        s = sel(g)
        if not s:
            continue
        lo, hi = bbox(s)
        c = [(lo[k] + hi[k]) / 2 for k in range(3)]
        print(f"  {g:22s} {tris(s):6d} ctr({c[0]:6.2f},{c[1]:5.2f},{c[2]:6.2f})"
              f" x[{lo[0]:7.2f},{hi[0]:7.2f}] y[{lo[1]:5.2f},{hi[1]:5.2f}]"
              f" z[{lo[2]:7.2f},{hi[2]:7.2f}]")

    # ------------------------------------------------------------- emit ---
    def fmt(x, dp):
        s = f"{x:.{dp}f}".rstrip("0").rstrip(".")
        return "0" if s in ("-0", "") else s

    vmap, vout = {}, []
    tmap, tout = {}, []
    nmap, nout = {}, []

    def remap(val, mp, out, dp):
        key = "/".join(fmt(x, dp) for x in val)
        i = mp.get(key)
        if i is None:
            i = len(out); mp[key] = i; out.append(key.replace("/", " "))
        return i

    namecount = collections.Counter()
    lines = []
    for o in objs:
        nm = o['name']
        nc = namecount[nm]; namecount[nm] += 1
        lines.append(f"o {nm}.{nc}")
        lines.append(f"usemtl {o['mat']}")
        tex = o['mat'] in TEXTURED and o['uv'][0] is not None
        for i in range(0, len(o['pos']), 3):
            toks = []
            for j in (i, i + 1, i + 2):
                a = remap(o['pos'][j], vmap, vout, 4) + 1
                c = remap(o['nrm'][j], nmap, nout, 3) + 1
                if tex:
                    b = remap(o['uv'][j], tmap, tout, 3) + 1
                    toks.append(f"{a}/{b}/{c}")
                else:
                    toks.append(f"{a}//{c}")
            lines.append("f " + " ".join(toks))

    with open(DST, "w") as f:
        f.write("# Virtual Coffee cafe model -- preprocessed from cafe.glb,"
                " FINAL WORLD COORDINATES\n")
        f.write("# (T1 re-staged as Simon's table; baked stand-ins dropped;"
                " forest pruned to the parking side;\n")
        f.write("#  quantized + deduped; vt kept only for textured materials)\n")
        for v in vout: f.write("v " + v + "\n")
        for t in tout: f.write("vt " + t + "\n")
        for n in nout: f.write("vn " + n + "\n")
        f.write("\n".join(lines) + "\n")

    print(f"\nverts {len(vout)}  vts {len(tout)}  vns {len(nout)}  objects {len(objs)}")
    print(f"written {DST}  {os.path.getsize(DST)/1e6:.2f} MB")

    # --------------------------------------------------- label textures ---
    used = {o['mat'] for o in objs}
    mats = js.get('materials', [])
    os.makedirs(TEX_DIR, exist_ok=True)
    n_tex = total_b = 0
    for m in mats:
        if m['name'] not in used or m['name'] in SKIP_TEXTURE_EXPORT:
            continue
        t = m.get('pbrMetallicRoughness', {}).get('baseColorTexture')
        if not t:
            continue
        img = js['images'][js['textures'][t['index']]['source']]
        bv  = js['bufferViews'][img['bufferView']]
        blob = d[binoff + bv.get('byteOffset', 0):
                 binoff + bv.get('byteOffset', 0) + bv['byteLength']]
        path = os.path.join(TEX_DIR, m['name'] + ".png")
        with open(path, "wb") as f:
            f.write(blob)
        n_tex += 1; total_b += len(blob)
    print(f"extracted {n_tex} label textures -> {TEX_DIR}  ({total_b/1e6:.2f} MB)")


if __name__ == "__main__":
    main()
