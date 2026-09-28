"""Garment shells from the body, pure numpy (+ an optional nearest-point
function for push-out). Rest-pose, three.js coords (Y up, face +Z)."""
import numpy as np

def vnormals(V, T):
    fn = np.cross(V[T[:, 1]] - V[T[:, 0]], V[T[:, 2]] - V[T[:, 0]])
    N = np.zeros_like(V)
    for k in range(3): np.add.at(N, T[:, k], fn)
    return N / np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-12)

def clip(V, T, W, f):
    """Keep the part of the mesh where f > 0, cut EXACTLY along f = 0
    (marching triangles). Returns V, T, W, per-face parent index."""
    ins = f > 0
    nv = len(V); newV, newW, emap = [], [], {}
    def ept(a, b):
        k = (a, b) if a < b else (b, a)
        if k not in emap:
            t = f[a] / (f[a] - f[b])
            newV.append(V[a] + t * (V[b] - V[a])); newW.append(W[a] + t * (W[b] - W[a]))
            emap[k] = nv + len(newV) - 1
        return emap[k]
    outT, par = [], []
    for fi, tri in enumerate(T):
        m = ins[tri]
        if m.all(): outT.append(tri.tolist()); par.append(fi); continue
        if not m.any(): continue
        poly = []
        for k in range(3):
            a, b = tri[k], tri[(k + 1) % 3]
            if ins[a]: poly.append(a)
            if ins[a] != ins[b]: poly.append(ept(a, b))
        for k in range(1, len(poly) - 1):
            outT.append([poly[0], poly[k], poly[k + 1]]); par.append(fi)
    V2 = np.vstack([V, np.array(newV).reshape(-1, 3)]); W2 = np.vstack([W, np.array(newW).reshape(-1, W.shape[1])])
    T2 = np.array(outT, dtype=np.int64)
    used = np.unique(T2); remap = -np.ones(len(V2), np.int64); remap[used] = np.arange(len(used))
    return V2[used], remap[T2], W2[used], np.array(par)

def neighbours(T, n):
    E = np.vstack([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]])
    E = np.vstack([E, E[:, ::-1]])
    E = np.unique(E, axis=0)
    return E

def boundary_edges(T):
    """directed boundary edges (a->b) as they appear in their triangle"""
    D = np.vstack([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]])
    key = {tuple(e) for e in D.tolist()}
    return np.array([e for e in D.tolist() if (e[1], e[0]) not in key], dtype=np.int64).reshape(-1, 2)

def laplacian(V, T, iters, lam=.5, pin=None, bnd_along=True):
    E = neighbours(T, len(V))
    B = boundary_edges(T); isb = np.zeros(len(V), bool); isb[B.ravel()] = True
    if bnd_along and len(B):
        BE = np.vstack([B, B[:, ::-1]])
    for _ in range(iters):
        S = np.zeros_like(V); C = np.zeros(len(V))
        np.add.at(S, E[:, 0], V[E[:, 1]]); np.add.at(C, E[:, 0], 1)
        M = S / np.maximum(C, 1)[:, None]
        if bnd_along and len(B):      # boundary vertices only feel boundary neighbours
            Sb = np.zeros_like(V); Cb = np.zeros(len(V))
            np.add.at(Sb, BE[:, 0], V[BE[:, 1]]); np.add.at(Cb, BE[:, 0], 1)
            M[isb] = (Sb[isb] / np.maximum(Cb[isb], 1)[:, None])
        D = lam * (M - V)
        if pin is not None: D[pin] = 0
        V = V + D
    return V

def smooth_field(X, T, iters, lam=.5):
    E = neighbours(T, len(X))
    for _ in range(iters):
        S = np.zeros_like(X); C = np.zeros(len(X))
        np.add.at(S, E[:, 0], X[E[:, 1]]); np.add.at(C, E[:, 0], 1)
        X = X + lam * (S / np.maximum(C, 1)[:, None] - X)
    return X

def push_out(V, nearest, offset):
    """nearest(p) -> (loc, normal). Moves every vertex to at least
    `offset` (array) outside the body along the body normal."""
    out = V.copy()
    for i, p in enumerate(V):
        loc, n = nearest(p)
        d = np.dot(p - loc, n)
        if d < offset[i]: out[i] = p + n * (offset[i] - d)
    return out

def hem_band(V, T, W, depth, inward):
    """Turn every open edge inward by `depth` (fabric thickness at the hem):
    new, separate vertices (hard edge), faces wound to face out of the hem."""
    B = boundary_edges(T)
    if not len(B): return V, T, W
    ids = np.unique(B.ravel())
    base = {int(v): len(V) + k for k, v in enumerate(ids)}                 # copy of the rim
    inner = {int(v): len(V) + len(ids) + k for k, v in enumerate(ids)}     # rim pushed in
    Vc = V[ids]; Vi = V[ids] - inward[ids] * depth
    V2 = np.vstack([V, Vc, Vi]); W2 = np.vstack([W, W[ids], W[ids]])
    F = []
    for a, b in B.tolist():
        F.append([base[b], base[a], inner[a]]); F.append([base[b], inner[a], inner[b]])
    return V2, np.vstack([T, np.array(F)]), W2

def top4(W):
    idx = np.argsort(-W, axis=1)[:, :4]
    w = np.take_along_axis(W, idx, 1); w = np.clip(w, 0, None)
    w /= np.maximum(w.sum(1, keepdims=True), 1e-9)
    return idx.astype(np.uint8), w.astype(np.float32)

def drape(V, sel, axis_x, axis_z_of_y, height, slope, nb=64, dy=.005):
    """Fabric hangs from what it rests on: in cylindrical coords round a
    vertical axis, each vertex's radius becomes at least the largest radius
    found ABOVE it (within `height`), less `slope` per metre of drop — cloth
    falls straight from the chest, the shoulder blades, the thigh, instead of
    clinging under them. Only vertices in `sel` move, and only outward."""
    P = V[sel]
    cz = axis_z_of_y(P[:, 1]); dx = P[:, 0] - axis_x; dz = P[:, 2] - cz
    th = np.arctan2(dx, dz); r = np.hypot(dx, dz)
    ti = ((th + np.pi) / (2 * np.pi) * nb).astype(int) % nb
    y0 = P[:, 1].min(); yi = ((P[:, 1] - y0) / dy).astype(int); ny = yi.max() + 1
    R = np.full((nb, ny), -1.0)
    np.maximum.at(R, (ti, yi), r)
    # spread across neighbouring angle bins so a sparse bin does not dent the curtain
    R = np.maximum(R, np.maximum(np.roll(R, 1, 0), np.roll(R, -1, 0)) - .002)
    H = int(height / dy); D = R.copy()
    for k in range(1, H + 1):                     # running max from above, sloped inward
        sh = np.full_like(R, -1.0); sh[:, :-k] = R[:, k:] - slope * k * dy
        D = np.maximum(D, sh)
    # a point near the axis is not on the outside of anything: leave it
    rn = np.where(r > .045, np.maximum(r, D[ti, yi]), r)
    s = np.where(r > 1e-6, rn / np.maximum(r, 1e-6), 1.0)
    out = V.copy()
    out[sel, 0] = axis_x + dx * s; out[sel, 2] = cz + dz * s
    return out

def push_out_layer(V, nearest_fn, offset, reach):
    """push outside another garment, but only where that garment is near"""
    out = V.copy()
    for i, p in enumerate(V):
        loc, n = nearest_fn(p)
        if np.linalg.norm(p - loc) > reach: continue
        d = np.dot(p - loc, n)
        if d < offset: out[i] = p + n * (offset - d)
    return out

def largest_component(V, T, W, keep_min=0):
    """drop islands the field left behind (a sliver of throat, a knuckle)"""
    par = np.arange(len(V))
    def fd(a):
        while par[a] != a: par[a] = par[par[a]]; a = par[a]
        return a
    for a, b, c in T:
        for u, v in ((a, b), (b, c)):
            ru, rv = fd(u), fd(v)
            if ru != rv: par[ru] = rv
    roots = np.array([fd(i) for i in range(len(V))])
    lab, cnt = np.unique(roots[T[:, 0]], return_counts=True)
    keep_roots = set(lab[cnt >= max(keep_min, 1)]) if keep_min else {lab[cnt.argmax()]}
    mask = np.array([roots[t[0]] in keep_roots for t in T])
    T2 = T[mask]; used = np.unique(T2); remap = -np.ones(len(V), np.int64); remap[used] = np.arange(len(used))
    return V[used], remap[T2], W[used]

def refine(V, T, W, sel):
    """1-to-4 split of the selected triangles; neighbours that share a split
    edge are split 1-to-2 / 1-to-3 so no crack opens (red-green refinement,
    one level). New vertices at edge midpoints, weights interpolated."""
    split = set()
    for t in T[sel]:
        for k in range(3):
            a, b = int(t[k]), int(t[(k + 1) % 3]); split.add((min(a, b), max(a, b)))
    mid = {}; newV, newW = [], []
    for e in sorted(split):
        mid[e] = len(V) + len(newV)
        newV.append((V[e[0]] + V[e[1]]) / 2); newW.append((W[e[0]] + W[e[1]]) / 2)
    out = []
    for t in T:
        a, b, c = (int(v) for v in t)
        m = [mid.get((min(p, q), max(p, q))) for p, q in ((a, b), (b, c), (c, a))]
        n = sum(x is not None for x in m)
        if n == 0: out.append([a, b, c]); continue
        if n == 3:
            ab, bc, ca = m; out += [[a, ab, ca], [ab, b, bc], [ca, bc, c], [ab, bc, ca]]; continue
        # rotate so the split edges come first
        vs = [a, b, c]
        for r in range(3):
            if m[r] is not None and (n == 1 or m[(r + 1) % 3] is not None): break
        vs = vs[r:] + vs[:r]; ms = m[r:] + m[:r]
        p0, p1, p2 = vs
        if n == 1:
            out += [[p0, ms[0], p2], [ms[0], p1, p2]]
        else:                            # edges p0p1 and p1p2 split
            out += [[p0, ms[0], p2], [ms[0], p1, ms[1]], [ms[0], ms[1], p2]]
    return np.vstack([V, np.array(newV).reshape(-1, 3)]), np.array(out, dtype=np.int64), \
        np.vstack([W, np.array(newW).reshape(-1, W.shape[1])])

def smooth_rim(V, T, iters, lam=.5):
    """straighten the open edges along themselves (a hem is one clean line)"""
    B = boundary_edges(T)
    if not len(B): return V
    pin = np.ones(len(V), bool); pin[np.unique(B.ravel())] = False
    return laplacian(V, T, iters, lam, pin=pin, bnd_along=True)

def taubin(V, T, iters, lam=.5, mu=-.53):
    """smoothing that keeps the volume (lam/mu pairs): muscle relief goes,
    the overall form stays"""
    for _ in range(iters):
        V = laplacian(V, T, 1, lam, bnd_along=False)
        V = laplacian(V, T, 1, mu, bnd_along=False)
    return V
