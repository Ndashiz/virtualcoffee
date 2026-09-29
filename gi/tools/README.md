# gi/tools — the baked light behind `gi/*.jpg`

The café's floor, ceiling and four walls carry light computed in Blender
Cycles, not painted (see `BAKED GI` in `index.html`). Six light maps, one per
receiver, in the same world-metre `uv2` the painted maps use. **Any change to
static geometry in the room (a wall, the counter, furniture, a prop that
stands on the floor) means re-baking**, or the shadows and bounce in the maps
stop matching what stands there.

| Step | What it does |
|---|---|
| `cdp.js` + `export.js` | Loads the page headless (chrome-headless-shell from the Playwright cache, driven over the DevTools protocol; no Playwright needed) and dumps the static interior in world space: 300 meshes, their average albedo / emission / roughness, the three.js lights, and the receivers' `uv2`. People, glows, glass and the street are left out; each receiver keeps only its faces that look into the room. |
| `bake.py` | Blender 4.5, headless, Metal GPU. Rebuilds the room and bakes three components per receiver: **sky** (the world through both glazings, direct + indirect), **emitters** (cove, toe kick, fridge LEDs, picture lights, the key globe's upper half, screens — boosted per class, see `BOOST`), **lamps** (the real-time lights, INDIRECT only: their direct light stays live in three.js). Saves `.npy` per component. |
| `encode.py` | `E = ks·sky + ke·emit + kl·lamp`, desaturated by `SAT`, blurred 2 px, written as `sqrt(E / EMAX)` in a JPG (decoded in the shader; `EMAX` must match `GI.EMAX`). Re-weighting is seconds, re-baking minutes. |

```bash
# 1. export (from anywhere; VC_ROOT = the repo)
VC_ROOT=$PWD WARM=6000 PROBE=gi/tools/export.js DUMP_DIR=/tmp/gi/dump node gi/tools/cdp.js /dev/null
# 2. bake: 384 samples, full resolution (~10 min on an M4)
/Applications/Blender.app/Contents/MacOS/Blender -b --python gi/tools/bake.py -- /tmp/gi/dump /tmp/gi/bake 384 1.0
# 3. encode with the shipped weights (sky 4.6, emitters 2.0, lamps 1.8, saturation .5)
/Applications/Blender.app/Contents/MacOS/Blender -b --python gi/tools/encode.py -- /tmp/gi/bake gi 4.6 2.0 1.8 0.5
```

Tuning without re-encoding: `?gigain=1.3` scales every receiver; `?nogi`
shows the painted maps; `?noprobeenv` keeps the old environment "maquette"
for everything that is not baked.

What bites:

- **Mixed lighting, never double.** On a receiver the bake REPLACES the
  whole indirect diffuse (environment, hemisphere, the default light-map add).
  If a light becomes a real-time light in three.js, move it from the emitter
  pass to the lamp pass (indirect only), or it is counted twice.
- **Units line up by construction**: three's shading value for albedo 1 is
  radiance, which is what Cycles' diffuse light pass (colour excluded)
  returns. A three.js light of intensity `I` delivers `E = π·I·att(d)`
  (non-physical falloff is not inverse-square), so lamp powers are matched at
  a reference distance per type (`REF`).
- **The contact blobs under the furniture are hidden** when the floor's bake
  loads (`FURN_BLOBS`); the people's blobs stay.
- **Multiply-blended and additive materials are not surfaces**: the export
  skips them (the blobs came out as emitters the first time and burnt white
  squares under every chair).
