#!/usr/bin/env python3
"""cafe.obj preprocessor for Virtual Coffee.

- Re-stages the model so the café's table T1 becomes Simon's table:
    * T1 tabletop scaled 1.5x in X/Z (the résumé sheet must fit on it)
    * T1 chair #1 rotated to sit behind the table, facing the camera
    * round rug moved under Simon's table, plant moved to the visible corner
    * global uniform scale so the tabletop lands at y=0.8025 (the height every
      existing scene anchor assumes), then translated so T1 sits at (0,-0.15)
- Quantizes (v 4dp, vt/vn 3dp), dedupes pools, drops vt for untextured
  materials, re-emits a compact OBJ in FINAL WORLD COORDINATES.
- Prints the world anchors the scene code needs.
"""
import math, collections

SRC = "/Users/ndashiz/Downloads/cafe.obj"
DST = "/Users/ndashiz/Documents/virtualcoffee/cafe.obj"

TEXTURED = {"chene_sol","platre","platre_vert","carte","tapis",
            "noyer","noyer_clair","marbre","enseigne_porte"}

# ---------- parse ----------
V,VT,VN = [],[],[]
objs = []  # {name, mat, faces:[((vi,ti,ni)*3)]}
cur = None
with open(SRC) as f:
    for line in f:
        t = line.split()
        if not t: continue
        if t[0]=="v":  V.append([float(t[1]),float(t[2]),float(t[3])])
        elif t[0]=="vt": VT.append([float(t[1]),float(t[2])])
        elif t[0]=="vn": VN.append([float(t[1]),float(t[2]),float(t[3])])
        elif t[0]=="o":
            cur={"name":t[1],"mat":None,"faces":[]}; objs.append(cur)
        elif t[0]=="usemtl": cur["mat"]=t[1]
        elif t[0]=="f":
            tri=[]
            for tok in t[1:]:
                a=tok.split("/")
                tri.append((int(a[0])-1,int(a[1])-1,int(a[2])-1))
            assert len(tri)==3
            cur["faces"].append(tuple(tri))

def bbox(o):
    mn=[1e9]*3; mx=[-1e9]*3
    for tri in o["faces"]:
        for vi,_,_ in tri:
            p=V[vi]
            for k in range(3):
                mn[k]=min(mn[k],p[k]); mx[k]=max(mx[k],p[k])
    return mn,mx

# sanity: expected object names at the set indices
def expect(idx,name):
    assert objs[idx]["name"]==name,(idx,objs[idx]["name"],name)
for i,n in [(64,"plateau_table"),(67,"socle_table"),(71,"assise"),(81,"latte_dossier"),
            (269,"tapis_rond"),(270,"pot"),(278,"feuillage"),(13,"carte_prix"),
            (262,"ampoule"),(69,"tasse_client")]:
    expect(i,n)

# T1 exact centre / top (model space)
mn,mx = bbox(objs[64])
T1C = [(mn[0]+mx[0])/2,(mn[2]+mx[2])/2]
T1_TOP = mx[1]
SCALE = 0.8025/T1_TOP
SHIFT_X = -T1C[0]*SCALE
SHIFT_Z = -0.15 - T1C[1]*SCALE
print(f"T1 centre model=({T1C[0]:.4f},{T1C[1]:.4f}) top={T1_TOP:.4f}")
print(f"SCALE={SCALE:.6f}  SHIFT=({SHIFT_X:.4f},0,{SHIFT_Z:.4f})")

# ---------- per-set transforms (model space), applied to VERTICES ----------
# vertex index sets per object range
def vset(rng):
    s=set()
    for i in rng:
        for tri in objs[i]["faces"]:
            for vi,_,_ in tri: s.add(vi)
    return s
def nset(rng):
    s=set()
    for i in rng:
        for tri in objs[i]["faces"]:
            for _,_,ni in tri: s.add(ni)
    return s

# guard: vertex/normal pools must not be shared across set boundaries
all_sets = {}
def claim(name,rng):
    vs=vset(rng)
    for other,ovs in all_sets.items():
        inter=vs&ovs
        assert not inter,(name,other,len(inter))
    all_sets[name]=vs
    return vs

set_table = claim("t1_table",range(64,68))
set_chair = claim("t1_chair",range(71,82))
set_tapis = claim("tapis",[269])
set_plant = claim("plant",range(270,279))
set_menu  = claim("menu",range(12,14))

# 0) chalkboard: right + up, out of Simon's head and the pendant halos
for vi in set_menu:
    V[vi][0]+=0.708   # +0.75 world
    V[vi][1]+=0.283   # +0.30 world

# 1) T1 table: scale 1.5 in x/z about its centre
for vi in set_table:
    p=V[vi]
    p[0]=T1C[0]+(p[0]-T1C[0])*1.5
    p[2]=T1C[1]+(p[2]-T1C[1])*1.5
for ni in nset(range(64,68)):
    n=VN[ni]
    nx,ny,nz=n[0]/1.5,n[1],n[2]/1.5
    l=math.sqrt(nx*nx+ny*ny+nz*nz) or 1
    n[0],n[1],n[2]=nx/l,ny/l,nz/l

# 2) T1 chair: rotate -90° about the table axis, then nudge behind the table
NUDGE=(0.0997,-0.0846)   # model-space ≈ world (+0.106,-0.09)
for vi in set_chair:
    p=V[vi]
    dx,dz=p[0]-T1C[0],p[2]-T1C[1]
    p[0]=T1C[0]+(-dz)+NUDGE[0]      # rotY(-90): x'=-z, z'=x
    p[2]=T1C[1]+( dx)+NUDGE[1]
for ni in nset(range(71,82)):
    n=VN[ni]
    n[0],n[2]=-n[2],n[0]

# 3) rug under Simon's table (world target ~(0.15,-0.75))
def model_target(wx,wz): return ((wx-SHIFT_X)/SCALE,(wz-SHIFT_Z)/SCALE)
mn,mx=bbox(objs[269]); c=[(mn[0]+mx[0])/2,(mn[2]+mx[2])/2]
tx,tz=model_target(0.15,-0.75)
for vi in set_tapis:
    V[vi][0]+=tx-c[0]; V[vi][2]+=tz-c[1]

# 4) plant to the visible left corner (world target (-3.05,-4.6))
mn,mx=bbox(objs[270]); c=[(mn[0]+mx[0])/2,(mn[2]+mx[2])/2]  # pot centre
tx,tz=model_target(-3.05,-4.60)
for vi in set_plant:
    V[vi][0]+=tx-c[0]; V[vi][2]+=tz-c[1]

# ---------- global transform ----------
for p in V:
    p[0]=p[0]*SCALE+SHIFT_X
    p[1]=p[1]*SCALE
    p[2]=p[2]*SCALE+SHIFT_Z

# ---------- anchors dump ----------
def anchor(i,label=None):
    mn,mx=bbox(objs[i])
    c=[(mn[k]+mx[k])/2 for k in range(3)]
    print(f"  {label or objs[i]['name']:26s} ctr({c[0]:6.3f},{c[1]:5.3f},{c[2]:6.3f})"
          f" x[{mn[0]:6.3f},{mx[0]:6.3f}] y[{mn[1]:5.3f},{mx[1]:5.3f}] z[{mn[2]:6.3f},{mx[2]:6.3f}]")
print("\n--- WORLD ANCHORS ---")
anchor(0,"sol"); anchor(1,"mur_fond"); anchor(3,"mur_gauche_bas"); anchor(7,"fenetre_vitre")
anchor(12,"cadre_carte"); anchor(13,"carte_prix")
anchor(16,"comptoir_plateau"); anchor(14,"comptoir_corps"); anchor(18,"meuble_arriere")
anchor(45,"machine_corps"); anchor(22,"caisse_socle"); anchor(20,"vitrine_socle"); anchor(21,"vitrine_verre")
anchor(58,"moulin_base")
anchor(64,"T1_plateau"); anchor(69,"T1_tasse_client"); anchor(71,"T1_chaise_assise")
anchor(78,"T1_chaise_montant"); anchor(82,"T1_chaise2_assise")
anchor(93,"T2_plateau"); anchor(119,"T3_plateau"); anchor(148,"T4_plateau"); anchor(174,"T5_plateau")
for i in (203,207,211,215): anchor(i,"tabouret_comptoir")
anchor(219,"table_haute_plateau")
for i in (229,235,239,245,249,255): anchor(i,"tabouret_fenetre")
for i in (233,243,253): anchor(i,"soucoupe_bar")
for i in (262,265,268): anchor(i,"ampoule")
anchor(259,"rail_plafond")
anchor(269,"tapis_rond"); anchor(270,"pot_plante"); anchor(279,"etagere")
anchor(288,"frigo_dos"); anchor(303,"frigo_bandeau")
anchor(383,"devanture_linteau"); anchor(402,"porte_battant"); anchor(416,"paillasson")

# carte_prix UV orientation check
print("\n--- carte_prix (v -> vt) ---")
for tri in objs[13]["faces"]:
    for vi,ti,ni in tri:
        p,u=V[vi],VT[ti]
        print(f"   v({p[0]:6.3f},{p[1]:5.3f},{p[2]:6.3f})  vt({u[0]:.3f},{u[1]:.3f})")
print("--- tapis uv sample ---")
us=[VT[ti] for tri in objs[269]["faces"][:40] for _,ti,_ in tri]
print("   u range",min(u[0] for u in us),max(u[0] for u in us),
      " v range",min(u[1] for u in us),max(u[1] for u in us))
print("--- enseigne quads ---")
for i in (413,415):
    anchor(i)
    for tri in objs[i]["faces"]:
        for vi,ti,ni in tri:
            p,u=V[vi],VT[ti]
            print(f"   v({p[0]:6.3f},{p[1]:5.3f},{p[2]:6.3f})  vt({u[0]:.3f},{u[1]:.3f})")

# ---------- emit ----------
def fmt(x,dp):
    s=f"{x:.{dp}f}"
    s=s.rstrip("0").rstrip(".")
    return "0" if s in("-0","") else s

vmap,vout={},[]
tmap,tout={},[]
nmap,nout={},[]
def remap(pool,val,mp,out,dp):
    key="/".join(fmt(x,dp) for x in val)
    i=mp.get(key)
    if i is None:
        i=len(out); mp[key]=i; out.append(key.replace("/"," "))
    return i

namecount=collections.Counter()
lines=[]
for o in objs:
    nc=namecount[o["name"]]; namecount[o["name"]]+=1
    lines.append(f"o {o['name']}.{nc}")
    lines.append(f"usemtl {o['mat']}")
    tex=o["mat"] in TEXTURED
    for tri in o["faces"]:
        toks=[]
        for vi,ti,ni in tri:
            a=remap(V,V[vi],vmap,vout,4)+1
            c=remap(VN,VN[ni],nmap,nout,3)+1
            if tex:
                b=remap(VT,VT[ti],tmap,tout,3)+1
                toks.append(f"{a}/{b}/{c}")
            else:
                toks.append(f"{a}//{c}")
        lines.append("f "+" ".join(toks))

with open(DST,"w") as f:
    f.write("# Virtual Coffee cafe model — preprocessed, FINAL WORLD COORDINATES\n")
    f.write("# (T1 re-staged as Simon's table; quantized + deduped; vt kept only for textured materials)\n")
    for v in vout: f.write("v "+v+"\n")
    for t in tout: f.write("vt "+t+"\n")
    for n in nout: f.write("vn "+n+"\n")
    f.write("\n".join(lines)+"\n")

import os
print(f"\nverts {len(vout)}  vts {len(tout)}  vns {len(nout)}  objs {len(objs)}")
print(f"written {DST}  {os.path.getsize(DST)/1e6:.2f} MB (src 5.3 MB)")
