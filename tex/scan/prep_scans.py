# blender -b --python tex/scan/prep_scans.py -- SRC OUT
# SRC: the 1K JPG downloads — Poly Haven oak_veneer_02, black_walnut_veneer_02,
# brown_leather, white_plaster_02 (diff, nor_gl, rough, saved as <id>_diff/_nor/_rough.jpg)
# and ambientCG Travertine009_1K-JPG unzipped in SRC/trav. All CC0.
# Turns the downloaded CC0 scans into the three files per material the page uses:
#   <m>_detail.jpg  luminance only, mean .5, fixed contrast -> overlaid on the painted colour
#   <m>_nor.jpg     OpenGL normal map (rotated with the grain when needed)
#   <m>_rough.jpg   roughness remapped to the material's range
# Wood grain in the veneer scans runs along u; boxUV wants it along v, so the
# normal and roughness maps of oak and walnut are turned 90 deg here (the normal's
# x/y rotated with them). The detail maps keep the scan's orientation: the page
# rotates them itself (along v for joinery, along each plank for the floor).
import bpy, sys, os
import numpy as np
a = sys.argv[sys.argv.index('--') + 1:]; SRC, OUT = a[0], a[1]
os.makedirs(OUT, exist_ok=True)

def load(p):
    im = bpy.data.images.load(p); im.colorspace_settings.name = 'Non-Color'
    w, h = im.size; px = np.empty(w * h * 4, np.float32); im.pixels.foreach_get(px)
    return px.reshape(h, w, 4)[:, :, :3].copy()

def save(arr, path, size, q):
    h, w = arr.shape[:2]
    if w != size:
        f = w // size
        arr = arr.reshape(size, f, size, f, 3).mean((1, 3))
    im = bpy.data.images.new('o', size, size, alpha=False, float_buffer=False)
    im.colorspace_settings.name = 'Non-Color'
    im.pixels.foreach_set(np.concatenate([np.clip(arr, 0, 1), np.ones((size, size, 1), np.float32)], 2).ravel())
    im.filepath_raw = path; im.file_format = 'JPEG'
    bpy.context.scene.render.image_settings.quality = q
    im.save(); bpy.data.images.remove(im)

def detail(rgb, std=.14):
    L = rgb @ np.array([.2126, .7152, .0722], np.float32)
    d = .5 + (L - L.mean()) / max(1e-4, L.std()) * std
    return np.repeat(np.clip(d, 0, 1)[:, :, None], 3, 2)

def rough(g, lo, hi):
    g = g[:, :, 0]; a, b = np.percentile(g, 2), np.percentile(g, 98)
    r = lo + (hi - lo) * np.clip((g - a) / max(1e-4, b - a), 0, 1)
    return np.repeat(r[:, :, None], 3, 2)

def rot_nor(n):
    r = np.rot90(n, 1).copy()           # grain u -> v
    R, G = r[:, :, 0].copy(), r[:, :, 1].copy()
    r[:, :, 0] = G; r[:, :, 1] = 1 - R
    return r

J = {
 # name: (diffuse, normal, rough, rotate, lo, hi, size, detail_std)
 'oak':     ('oak_veneer_02_diff.jpg', 'oak_veneer_02_nor.jpg', 'oak_veneer_02_rough.jpg', True, .42, .7, 1024, .16),
 'walnut':  ('black_walnut_veneer_02_diff.jpg', 'black_walnut_veneer_02_nor.jpg', 'black_walnut_veneer_02_rough.jpg', True, .32, .58, 1024, .14),
 'trav':    ('trav/Travertine009_1K-JPG_Color.jpg', 'trav/Travertine009_1K-JPG_NormalGL.jpg', 'trav/Travertine009_1K-JPG_Roughness.jpg', False, .3, .62, 1024, .12),
 'plaster': ('white_plaster_02_diff.jpg', 'white_plaster_02_nor.jpg', 'white_plaster_02_rough.jpg', False, .82, .97, 512, .12),
 'leather': ('brown_leather_diff.jpg', 'brown_leather_nor.jpg', 'brown_leather_rough.jpg', False, .34, .68, 512, .14),
}
for k, (d, n, r, rot, lo, hi, size, sd) in J.items():
    D = load(os.path.join(SRC, d)); N = load(os.path.join(SRC, n)); Rr = load(os.path.join(SRC, r))
    save(detail(D, sd), os.path.join(OUT, k + '_detail.jpg'), 512, 82)
    if rot: N = rot_nor(N); Rr = np.rot90(Rr, 1).copy()
    save(N, os.path.join(OUT, k + '_nor.jpg'), size, 88)
    save(rough(Rr, lo, hi), os.path.join(OUT, k + '_rough.jpg'), 512, 80)
    print('[prep]', k, flush=True)
