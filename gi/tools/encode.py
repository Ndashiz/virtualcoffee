# blender -b --python encode.py -- DIR OUTDIR ks ke kl   : E = ks*sky + ke*emit + kl*lamp -> sqrt(E/EMAX) JPG
import bpy, os, sys, json
import numpy as np
argv = sys.argv[sys.argv.index('--') + 1:]
D, OUTD = argv[0], argv[1]; ks, ke, kl = map(float, argv[2:5]); SAT = float(argv[5]) if len(argv) > 5 else 1.0; EMAX = 6.0
os.makedirs(OUTD, exist_ok=True)
def blur(a, r):
    for _ in range(2):
        for ax in (0, 1):
            c = np.cumsum(np.pad(a, [(r + 1, r) if i == ax else (0, 0) for i in range(3)], mode='edge'), axis=ax)
            a = (np.take(c, range(2 * r + 1, c.shape[ax]), axis=ax) - np.take(c, range(0, c.shape[ax] - 2 * r - 1), axis=ax)) / (2 * r + 1)
    return a
st = {}
for k in ['floor', 'ceiling', 'backWall', 'frontWall', 'leftWall', 'shopWall']:
    f = os.path.join(D, k + '_sky.npy')
    if not os.path.exists(f): continue
    E = ks * np.load(f) + ke * np.load(os.path.join(D, k + '_emit.npy')) + kl * np.load(os.path.join(D, k + '_lamp.npy'))
    E = blur(E, 2)
    L = (E * np.array([.2126, .7152, .0722], np.float32)).sum(2, keepdims=True); E = L + (E - L) * SAT
    st[k] = [round(float(E.mean()), 3), round(float(np.percentile(E, 99)), 3), round(float((E > EMAX).mean() * 100), 3)]
    c = np.sqrt(np.clip(E / EMAX, 0, 1)).astype(np.float32)
    h, w = c.shape[:2]
    im = bpy.data.images.new('o_' + k, w, h, alpha=False, float_buffer=False)
    im.colorspace_settings.name = 'Non-Color'
    im.pixels.foreach_set(np.concatenate([c, np.ones((h, w, 1), np.float32)], axis=2).ravel())
    im.filepath_raw = os.path.join(OUTD, k + '.jpg'); im.file_format = 'JPEG'
    bpy.context.scene.render.image_settings.quality = 90
    im.save()
print('[enc]', json.dumps(st), flush=True)
