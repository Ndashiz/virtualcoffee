# exact plane sections of the quad mesh: crossing points joined through faces -> closed loops
import numpy as np, collections
def build(P, F):
    E = {}
    FE = []
    for f in F:
        fe = []
        for i in range(len(f)):
            a, b = f[i], f[(i + 1) % len(f)]
            k = (min(a, b), max(a, b))
            if k not in E: E[k] = len(E)
            fe.append(E[k])
        FE.append(fe)
    EA = np.array(sorted(E, key=E.get))
    return EA, np.array(FE)
def loops(P, EA, FE, h, axis=np.array([0., 1., 0.]), origin=np.zeros(3)):
    d = (P - origin) @ axis
    da, db = d[EA[:, 0]], d[EA[:, 1]]
    m = (da - h) * (db - h) < 0
    idx = -np.ones(len(EA), int); idx[m] = np.arange(m.sum())
    t = ((h - da[m]) / (db[m] - da[m]))[:, None]
    pts = P[EA[m, 0]] + t * (P[EA[m, 1]] - P[EA[m, 0]])
    par = list(range(len(pts)))
    def fd(x):
        while par[x] != x:
            par[x] = par[par[x]]; x = par[x]
        return x
    cf = idx[FE]                       # crossing index per face edge, -1 if none
    for row in cf[(cf >= 0).sum(1) >= 2]:
        c = row[row >= 0]
        for j in range(1, len(c)):
            a, b = fd(c[0]), fd(c[j])
            if a != b: par[a] = b
    g = collections.defaultdict(list)
    for i in range(len(pts)): g[fd(i)].append(i)
    return sorted([pts[v] for v in g.values()], key=lambda c: c[:, 0].mean())
def poly_area(pts2):
    # area of the loop polygon: order points by angle around centroid (fine for star-shaped sections)
    c = pts2.mean(0); a = np.arctan2(pts2[:, 1] - c[1], pts2[:, 0] - c[0]); q = pts2[np.argsort(a)]
    x, y = q[:, 0], q[:, 1]
    return .5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))
