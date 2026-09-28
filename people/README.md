# people/ — the pipeline behind `people.bin`

The café's cast (and Simon) are one continuous skinned body each, built
offline here from **FinalBaseMesh** and read by the scene at runtime
(`/* ---------------- REAL PEOPLE` in `index.html`). Blender 4.5, headless,
numpy only. Nothing in this folder runs in the browser.

**Source mesh (not committed — licence unknown):** extract
`FinalBaseMesh.obj` from `~/Downloads/fdx54mtvuz28-FinalBaseMesh.rar`
(`bsdtar -xf`) into this folder.

```bash
./build_all.sh          # BLENDER=/path/to/blender to override
```

| Stage | What it does |
|---|---|
| `pp_body.py` | Scale to 1.75 m, face +z, decimate **per region**: the head kept whole (the likeness), hands ×.24, the body ×.15 (it lives under clothes) → ~12.6 k tris |
| `landmarks2.py` | Joints read off **girth profiles** (exact plane sections, `sectlib.py`): elbow = narrowest section between biceps and forearm, wrist = the next one, knee = the plateau of the leg's profile, hip = the thigh's centre line carried up to .855 |
| `pp_rig.py` | Armature on those joints, **heat weights in the A-pose** (arms clear of the body), then re-posed to the rig's rest (limbs straight down, DQS). The joints written out are the re-posed points |
| `pp_face.py` | The base head has its eyes shut: refine, cut an almond opening exactly along its outline, turn the rim in (lid thickness). Eyeball at (±.032, 1.646, .085), r .012 |
| `pp_garments.py` | Tee, shirt, sweater, blazer, trousers, shoes, apron. A field clips the body exactly along the hem; rounds of smoothing + push-out against a **Taubin-smoothed** body (cloth rests on the form, not the muscles) with 3 mm kept off the real skin; a **drape** (cloth falls from what carries it) on torso, sleeves (tapered) and trouser legs; layering over the waistband; hem bands; weights copied from the skin. Shoes are a loft along each foot. Writes, per body face, which garments hide it |
| `pp_hair.py` | Eight cuts, all shells off the scalp with a thickness that reaches **zero at the hairline** (buzz, short, fade, curly, bun, pony, bob, long) |
| `pp_lod.py` | LOD1: every part decimated (~35 %), weights carried; the body mask inherited from the nearest LOD0 face |
| `export_people.py` | `../people.bin`: `VCP1` + JSON header + int16 positions, u16 indices, u8×4 skin; `body.mask` / `body@1.mask` (u16 per face, bit = garment order) |

Coordinates are three.js's throughout (Y up, face +z, feet at 0). Joint
names are the rig's own (`pelvis`, `hipL`, `kneeL`, …), so the runtime binds
a `THREE.Skeleton` straight onto the joint groups `buildPerson` makes.
