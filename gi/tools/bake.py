# Blender 4.5, headless:  blender -b --python bake.py -- DUMP OUT [samples] [scale]
# Rebuilds the café from export.js's dump and bakes the "baked indirect" light
# maps for the receivers (see BAKED GI in index.html):
#   pass A: sky + emitters, direct AND indirect      (lamps off)
#   pass B: the real-time lamps, INDIRECT only       (sky, emitters off)
#   E = A + B, written as sqrt(E/EMAX) in a JPG (decoded in the shader).
# Units: three's shading value for albedo 1 == radiance == Cycles' diffuse
# light pass with colour excluded; a three light of intensity I and falloff
# att(d) delivers E = pi*I*att(d), so lamp powers are matched at a reference
# distance (non-physical three falloff is not inverse-square).
import bpy, json, os, sys, math, time
import numpy as np
from mathutils import Vector

argv = sys.argv[sys.argv.index('--') + 1:]
DUMP, OUT = argv[0], argv[1]
SAMPLES = int(argv[2]) if len(argv) > 2 else 256
SCALE = float(argv[3]) if len(argv) > 3 else 1.0
EMAX = 4.0
os.makedirs(OUT, exist_ok=True)
T0 = time.time()
def log(*a): print('[gi]', '%.1fs' % (time.time() - T0), *a, flush=True)

H = json.load(open(os.path.join(DUMP, 'header.json')))
buf = np.concatenate([np.fromfile(os.path.join(DUMP, f), dtype=np.float32)
                      for f in sorted(os.listdir(DUMP)) if f.endswith('.bin')])
assert buf.size == H['floats'], (buf.size, H['floats'])

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
try:
    pr = bpy.context.preferences.addons['cycles'].preferences
    pr.compute_device_type = 'METAL'; pr.get_devices()
    for d in pr.devices: d.use = True
    sc.cycles.device = 'GPU'
    log('devices', [d.name for d in pr.devices if d.use])
except Exception as e:
    log('GPU unavailable, CPU', e)
sc.cycles.samples = SAMPLES
sc.cycles.use_denoising = False
sc.cycles.max_bounces = 8
sc.cycles.diffuse_bounces = 5
sc.cycles.glossy_bounces = 2
sc.cycles.transmission_bounces = 0
sc.cycles.caustics_reflective = False
sc.cycles.caustics_refractive = False
sc.render.bake.margin = 16

def B(p):  # three (x,y,z) -> blender (x,-z,y)
    return (p[0], -p[2], p[1])

# ---------- materials ----------
def boost_for(mesh, mat):
    """Displayed HDR values are not luminances: a 1 cm LED strip shown at 1.0
    in three really outshines the wall by two orders of magnitude. Each class
    is calibrated against the light the art direction had painted (see
    calibrate in the log)."""
    e = max(mat['emit'])
    if e < 0.15: return 1.0
    x0, y0, z0, x1, y1, z1 = mesh['bbox']
    dims = sorted([x1 - x0, y1 - y0, z1 - z0]); cx, cy, cz = (x0+x1)/2, (y0+y1)/2, (z0+z1)/2
    strip = dims[0] < 0.035 and dims[2] > 0.25
    if strip and dims[2] > 9 and cy > 3.0: return BOOST['cove']
    if strip and cy < 0.2: return BOOST['kick']
    if strip and 3.5 < cx < 4.6 and cz < -3.9: return BOOST['fridge']
    if strip and cz > 3.0: return BOOST['picture']
    if strip: return BOOST['strip']
    return BOOST['other']
BOOST = json.loads(os.environ.get('GI_BOOST', '{}')) or {}
for k, v in {'cove': 14, 'kick': 30, 'fridge': 4, 'picture': 25, 'strip': 5, 'other': 0.6, 'key': 3.5}.items():
    BOOST.setdefault(k, v)
bmats = {}
def make_mat(mid, key, strength, top_only=False):
    m = H['materials'][mid]
    mt = bpy.data.materials.new('m%d_%s' % (mid, key)); mt.use_nodes = True
    nt = mt.node_tree; bsdf = nt.nodes['Principled BSDF']
    a = [min(0.92, max(0.0, c)) for c in m['albedo']]
    bsdf.inputs['Base Color'].default_value = (*a, 1)
    bsdf.inputs['Roughness'].default_value = float(min(1, max(0.05, m['rough'])))
    bsdf.inputs['Metallic'].default_value = float(m['metal'])
    e = m['emit']; emax = max(e)
    if emax > 0.01 and strength > 0:
        bsdf.inputs['Emission Color'].default_value = (e[0] / emax, e[1] / emax, e[2] / emax, 1)
        bsdf.inputs['Emission Strength'].default_value = emax * strength
        if top_only:   # an opal globe whose downward light is a real-time spot
            geo = nt.nodes.new('ShaderNodeNewGeometry'); sep = nt.nodes.new('ShaderNodeSeparateXYZ')
            mr = nt.nodes.new('ShaderNodeMapRange'); mul = nt.nodes.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'
            nt.links.new(geo.outputs['Normal'], sep.inputs[0])
            mr.inputs['From Min'].default_value = -0.2; mr.inputs['From Max'].default_value = 0.6
            mr.inputs['To Min'].default_value = 0.0; mr.inputs['To Max'].default_value = 1.0
            nt.links.new(sep.outputs['Z'], mr.inputs['Value'])
            mul.inputs[1].default_value = emax * strength
            nt.links.new(mr.outputs['Result'], mul.inputs[0])
            nt.links.new(mul.outputs[0], bsdf.inputs['Emission Strength'])
    mt['emit_default'] = float(bsdf.inputs['Emission Strength'].default_value)
    return mt

# ---------- geometry ----------
off = 0
recv_objs = {}
emit_mats = []
for mi, M in enumerate(H['meshes']):
    n = M['verts']
    pos = buf[off:off + n * 3].reshape(-1, 3); off += n * 3
    nrm = buf[off:off + n * 3].reshape(-1, 3); off += n * 3
    uv = None
    if M['recv']:
        uv = buf[off:off + n * 2].reshape(-1, 2); off += n * 2
    v = np.stack([pos[:, 0], -pos[:, 2], pos[:, 1]], axis=1)
    me = bpy.data.meshes.new(M['name'])
    me.vertices.add(n); me.vertices.foreach_set('co', v.ravel())
    nt = n // 3
    me.loops.add(nt * 3); me.loops.foreach_set('vertex_index', np.arange(nt * 3, dtype=np.int32))
    me.polygons.add(nt)
    me.polygons.foreach_set('loop_start', np.arange(0, nt * 3, 3, dtype=np.int32))
    me.polygons.foreach_set('loop_total', np.full(nt, 3, dtype=np.int32))
    if uv is not None:
        uvl = me.uv_layers.new(name='LM'); uvl.data.foreach_set('uv', uv.ravel())
    me.update(calc_edges=True); me.validate(clean_customdata=False)
    ob = bpy.data.objects.new(M['name'], me); sc.collection.objects.link(ob)
    mat = H['materials'][M['mat']]
    name = M['name']
    if M['recv']:
        mt = make_mat(M['mat'], 'recv_' + M['recv'], 0.0)
        recv_objs[M['recv']] = ob
    else:
        bb = M['bbox']; cxm = (bb[0] + bb[3]) / 2; cym = (bb[1] + bb[4]) / 2; szm = bb[4] - bb[1]
        hot = max(mat['emit']) > 1.0 and mat['type'] == 'MeshStandardMaterial'
        is_key = hot and 2.6 < cym < 3.1 and abs(cxm) < .3 and szm > .38
        is_bar_globe = hot and not is_key and 1.85 < cym < 2.25
        if is_bar_globe:
            mt = make_mat(M['mat'], 'barglobe_%d' % mi, 0.0)       # its point light is live
        elif is_key:
            mt = make_mat(M['mat'], 'keyglobe_%d' % mi, BOOST['key'], top_only=True)
        else:
            mt = make_mat(M['mat'], 'o%d' % mi, boost_for(M, mat))
    me.materials.append(mt)
    if mt['emit_default'] > 0: emit_mats.append(mt)
log('meshes', len(H['meshes']), 'receivers', list(recv_objs), 'emitters', len(emit_mats))

# ---------- world: the sky through two glazings, the street below ----------
w = bpy.data.worlds.new('sky'); sc.world = w; w.use_nodes = True
wn = w.node_tree; bg = wn.nodes['Background']
tc = wn.nodes.new('ShaderNodeTexCoord'); sep = wn.nodes.new('ShaderNodeSeparateXYZ')
ramp = wn.nodes.new('ShaderNodeValToRGB')
wn.links.new(tc.outputs['Generated'], sep.inputs[0])
wn.links.new(sep.outputs['Z'], ramp.inputs['Fac'])
cr = ramp.color_ramp
# Generated Z runs 0 (straight down) .. 1 (straight up) for the world
cr.elements[0].position = 0.46; cr.elements[0].color = (0.30, 0.29, 0.27, 1)    # street, pavement
cr.elements[1].position = 0.52; cr.elements[1].color = (0.84, 0.90, 0.96, 1)    # horizon
e3 = cr.elements.new(1.0); e3.color = (0.62, 0.70, 0.80, 1)                     # zenith
wn.links.new(ramp.outputs['Color'], bg.inputs['Color'])
SKY_STRENGTH = 2.3
bg.inputs['Strength'].default_value = SKY_STRENGTH

# ---------- lamps (three's real-time lights) ----------
lamps = []
REF = {'SpotLight': 1.9, 'PointLight': 1.2}
for L in H['lights']:
    col = L['color']; I = L['intensity']; D = L['distance']; dec = L['decay']
    if L['type'] == 'DirectionalLight':
        ld = bpy.data.lights.new('sun', 'SUN'); ld.energy = math.pi * I; ld.angle = math.radians(0.6)
        ob = bpy.data.objects.new('sun', ld)
        d = Vector(B(L['target'])) - Vector(B(L['pos']))
        ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    else:
        ref = 0.8 if (L['type'] == 'SpotLight' and L['pos'][1] > 3.0) else REF[L['type']]
        if I * max(col) < 0.2 or (D and D < 1.0): continue          # laptop, jukebox: negligible
        att = (max(0.0, 1 - ref / D) ** dec) if D else 1.0
        P = 4 * math.pi ** 2 * ref ** 2 * I * att
        if L['type'] == 'SpotLight':
            ld = bpy.data.lights.new('spot', 'SPOT'); ld.spot_size = 2 * L['angle']; ld.spot_blend = L['penumbra']
            ob = bpy.data.objects.new('spot', ld)
            d = Vector(B(L['target'])) - Vector(B(L['pos']))
            ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
        else:
            ld = bpy.data.lights.new('pt', 'POINT'); ob = bpy.data.objects.new('pt', ld)
        ld.energy = P; ld.shadow_soft_size = 0.05
        try: ld.use_soft_falloff = False
        except Exception: pass
    ld.color = col
    ob.location = B(L['pos']); sc.collection.objects.link(ob); lamps.append(ob)
log('lamps', [(o.data.type, round(o.data.energy, 1)) for o in lamps])

# ---------- bake targets ----------
R = H['room']; W_ = R['x1'] - R['x0']; D_ = R['z1'] - R['z0']; H_ = R['h']
SIZES = {'floor': (W_, D_), 'ceiling': (W_, D_), 'backWall': (W_, H_), 'frontWall': (W_, H_),
         'leftWall': (D_, H_), 'shopWall': (D_, H_)}
imgs = {}
for k, ob in recv_objs.items():
    a, b = SIZES[k]; px = int(round(1024 * SCALE / max(W_, D_) * a)); py = int(round(1024 * SCALE / max(W_, D_) * b))
    im = bpy.data.images.new('lm_' + k, px, py, alpha=False, float_buffer=True)
    mt = ob.data.materials[0]; nd = mt.node_tree.nodes.new('ShaderNodeTexImage'); nd.image = im
    mt.node_tree.nodes.active = nd
    imgs[k] = im
    ob.data.uv_layers.active = ob.data.uv_layers['LM']

def bake(filt, tag):
    bpy.ops.object.select_all(action='DESELECT')
    for ob in recv_objs.values(): ob.select_set(True)
    bpy.context.view_layer.objects.active = list(recv_objs.values())[0]
    t = time.time()
    bpy.ops.object.bake(type='DIFFUSE', pass_filter=filt, margin=16, use_clear=True)
    out = {}
    for k, im in imgs.items():
        a = np.empty(im.size[0] * im.size[1] * 4, dtype=np.float32); im.pixels.foreach_get(a)
        out[k] = a.reshape(im.size[1], im.size[0], 4)[:, :, :3].copy()
    log('bake', tag, '%.1fs' % (time.time() - t))
    return out

def emitters_on(on):
    for mt in emit_mats:
        bs = mt.node_tree.nodes['Principled BSDF']
        if on:
            if not bs.inputs['Emission Strength'].links: bs.inputs['Emission Strength'].default_value = mt['emit_default']
        else:
            mt['saved_links'] = 0
            bs.inputs['Emission Strength'].default_value = 0.0
    return True
# keep the key globe's hemisphere node wiring: store and restore its links
KEYLINKS = []
for mt in emit_mats:
    bs = mt.node_tree.nodes['Principled BSDF']
    for l in bs.inputs['Emission Strength'].links: KEYLINKS.append((mt, l.from_socket))
def unlink_emitters():
    for mt, fs in KEYLINKS:
        for l in list(mt.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].links): mt.node_tree.links.remove(l)
def relink_emitters():
    for mt, fs in KEYLINKS: mt.node_tree.links.new(fs, mt.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'])

# pass SKY: world only, direct + indirect
for o in lamps: o.hide_render = True
emitters_on(False); unlink_emitters()
bg.inputs['Strength'].default_value = SKY_STRENGTH
SKY = bake({'DIRECT', 'INDIRECT'}, 'sky')
# pass EMIT: emitters only, direct + indirect
bg.inputs['Strength'].default_value = 0.0
emitters_on(True); relink_emitters()
EMT = bake({'DIRECT', 'INDIRECT'}, 'emitters')
# pass LAMP: the real-time lamps, indirect only
emitters_on(False); unlink_emitters()
for o in lamps: o.hide_render = False
LMP = bake({'INDIRECT'}, 'lamps indirect')
for k in imgs:
    np.save(os.path.join(OUT, k + '_sky.npy'), SKY[k])
    np.save(os.path.join(OUT, k + '_emit.npy'), EMT[k])
    np.save(os.path.join(OUT, k + '_lamp.npy'), LMP[k])
log('components saved')
