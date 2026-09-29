# CLAUDE.md

Working notes for agent sessions on Virtual Coffee. [`README.md`](README.md) is
the tour and [`VIRTUAL_COFFEE.md`](VIRTUAL_COFFEE.md) is the French deep dive;
this file is the "don't get burned" list.

## What this is

Simon's interactive 3D resume. **Vanilla JS, no build step, no bundler, no
package.json.** Everything — markup, CSS, the VC shell, the whole scene — lives
in one `index.html` of ~10 000 lines. three.js **r134**, vendored. Don't
introduce a framework, a bundler, or a dependency without being asked.

- **Prod** : <https://ndashiz.be/virtualcoffee/> — `git push` IS the deploy
  (GitHub Pages, ~1-2 min). There is no server to restart.
- The LazyPO Cloudflare Worker does **not** apply here: its route is
  `ndashiz.be/pro/*`, so this page gets no CSP and no auth gate.

## The rule that matters most

### Any change to how an NPC moves requires a route audit BEFORE it ships

Adding an agent, moving a waypoint, changing a speed, adding a station — all of
it. The room is small, eleven bodies share it, and two of them (the courier and
the waiter) cross it end to end on authored routes. A path that looks clear on
paper walks a body through a table or through another body.

The audit is not a look at the screen. It is:

1. **Furniture.** Sample every position along the new route and take the
   minimum distance to every table centre, chair and stool. A body is `.26`, a
   café table `.42` to `.48`, so **`.55` m centre-to-centre is the floor** and
   anything under it will be seen. Table and chair coordinates come out of
   `cafe.obj.txt` — parse it, do not eyeball the render.
2. **Bodies.** Run the whole cast at once, for thousands of frames, and take
   the minimum distance for every PAIR. The envelope is `BODY_R*2` = `.52`.
   Drive the guest across the service lanes while you do it: the tightest
   encounters are the ones nobody stages.
3. **A STATION is stricter than a route.** A waypoint another body walks
   through for a second is a passing encounter and steering handles it. A
   spot where somebody STANDS for minutes is a wall. Check every new resting
   position against every point of every other agent's paths, and keep
   `.8` m: the waiter's post shipped 21 cm from `ICE_CARRY`'s last waypoint,
   so the courier's delivery target sat inside a body that never moved and
   he circled it for ever. The courier never yields, so nothing could
   resolve it.
4. **Write the numbers into the commit.** "It looks fine" is how the waiter
   shipped walking through a customer.

Three mechanisms keep bodies apart, and they are not interchangeable:

- **`steerAgents()`** (in `walkLayer`) is the one that actually avoids: if the
  direction of travel points into a body within `AVOID_R`, it takes the
  tangent. Same shape as `steerAround()`, which has done this for furniture
  since the beginning. Swerving cannot deadlock. **Not applied to the guest** —
  he is steered by a person and a route that argues with the keys is worse than
  a bump.
- **`separateAgents()`** (end of `animateAgents`) is the safety net, not the
  rule. It can only say "you are already inside someone, come out". On its own
  it holds two bodies at arm's length, grinding, because both are still pulling
  towards their waypoints. Its push is in metres per SECOND, never per frame: a
  per-frame cap silently becomes a per-frame speed and loses the race to a
  walker as soon as the frame rate drops.

- **`yieldToGuest()`** (in `behaviourTick`) is for the case neither of the
  others covers: a body that is STANDING has no route to bend, so before this
  existed the player walked into it and the separation pass slid it, feet
  still, like furniture. It steps off the line, waits, and walks back to its
  mark. Only bodies with nowhere else to go are eligible — hijacking the
  `walkTarget` of an agent whose own tick drives it is overwritten ten times a
  second.

**Plan A is the route; plan B is the way round whoever is on it — and the
other body is choosing its plan B at the same instant.** `steerAgents` splits
on whether the obstacle is closing: a body merely in the way is furniture, so
take the cheaper tangent; a body walking AT you is a negotiation, so both take
the tangent on the SAME side of the line between them, which is opposite in
the world for the two of them. Neither has to know what the other decided —
the geometry decides, identically, for both. Letting each take "the tangent
that goes my way" is what put the courier inside the waiter: two bodies
choosing the same gap. The choice is committed for ~1 s, because re-deciding
every frame as the angle drifts is what makes two people shuffle in a doorway.

**Nothing may orbit.** A steering rule with no way to give up will circle a
body that never moves: every approach is deflected, the waypoint behind it is
never reached, and the route never ends. `steerAgents` counts how long it has
been turned away by the same body and, past `STUCK_MAX`, walks straight at it
and lets the separation pass part them. Better a shoulder brushed than a
delivery that never arrives.

**A seated body is furniture.** `seated(a)` is `rootY<0 || a.sit`, which is the
pose layer's own definition — and it must be, because the second copy of that
test used `-.05` while the stool customers ride at `-.01`, so the drinker and
the reader read as standing, the give-way rule walked them off their stools,
and they slid along the window bar at seat height with a walk cycle fighting
SEAT_POSE. A seated body is never pushed and never asked to move. Anything
that DOES move one owes it what `tickLeaving` already does: stand it up
(`a.rootY=0`) first.

**The guest is never pushed** — unless what he walked into cannot move either.

 He is the player; being shoved by the scenery
reads as a bug. Whoever he meets takes the whole correction.

Only a body in MOTION takes a push, or the standing trio (`.85` m apart) drifts
apart for ever. The courier never yields — his route threads authored
clearances. Under one body radius, everyone moves regardless: at spawn `walkK`
is still damping up from zero, and two arrivals sharing the doorway would
otherwise sit merged waiting to be considered movers.

## Measure it, do not look at it

Almost every real defect this file has produced was invisible to reasoning and
obvious to a measurement. Three that cost hours:

- **The televisions had no left edge** because the back WALL was 7 mm in front
  of the bezel's far bar — both sets are angled into the room, and an angled
  panel swings its far edge backwards further than its standoff. Every numeric
  test passed (outer box centred, hole edge exact, borders symmetric) because
  none of them asked whether something else was in the way. What found it:
  tinting the picture magenta and rendering the set alone.
- **The barista's whole coffee routine was unreachable code.** `setMode()`
  raises `onModeEnter`, every `setMode` is called from inside the switch, and
  the old code cleared the flag on the last line of the same tick. Read the
  flag once at the top of the tick and clear it there.
- **`gazeAngles()` rotated the wrong way**, so half the room looked away from
  what it was aiming at — 177° off at yaw `-1.83`. Invisible at yaw 0, which is
  why it survived. Plant a target at a known bearing and measure the error;
  a value that is IDENTICAL for everyone is a clamp, a spread is a bug.

Useful probes live in the session scratchpad, not in the repo: headless
Chromium + Playwright, `window.__vc = {...}` injected by rewriting the response
just before `animate();`, then read positions and world transforms directly.
Note the software renderer runs at ~5 fps and `dt` is clamped to `.05`, so
**scene time advances at roughly 0.28× wall time** — never time anything with
`clock.elapsedTime` against a wall-clock loop.

## Geometry gotchas

- **`ExtrudeGeometry` with a `Path` hole is not safe here.** Punching the TV
  bezel that way triangulated the front cap with the left bar missing. Four
  boxes tile a frame exactly and cannot be triangulated wrongly.
- **A prop parented to a wrist inherits the whole arm chain.** The waiter's
  tray became a blade held edge-on. Props that must stay level live in the
  scene and are driven from the joint's world position with their own rotation.
- **The model bakes world coordinates into the vertices**, so a mesh from
  `cafe.obj.txt` starts at position 0 and moving it is an OFFSET, not a
  placement. To move one at all it has to be in the `SPECIAL` set, or it is
  merged by material with every other object sharing it.
- **`tex/*.png` are stored v-flipped** (`flipY=false` cancels the exporter's
  own flip). Repaint one and bump `LABEL_TEX_V`, or returning visitors keep the
  cached old one for hours.
- Forward kinematics rotates a joint without ever shortening the body hanging
  from it: bending hips and knees in place leaves a character hovering. That is
  what `a.dip` on the root is for.

## The design pass (2026) — how the room is dressed now

[`DIRECTION_ARTISTIQUE_2026.md`](DIRECTION_ARTISTIQUE_2026.md) is the brief. The
mechanics that bite:

- **The loader dresses the model by role, by object name**: `REMAT` (object →
  material), `HIDE` (dropped at parse), `CAPTURE` (bounding box kept in
  `CAFE.boxes`). Add a rule there, never in the OBJ.
- **Rebuilt furniture is placed from `CAFE.boxes`, never from typed
  coordinates.** That is the whole reason the design pass needed no route
  audit: every seat, table and stool is the model's own footprint. Anything
  NEW that stands on the floor is a station for the audit rules above — the
  Strelitzia's leaves were measured against the dancer's spot and the guest's
  ring before it shipped.
- **`LatheGeometry` profiles run counter-clockwise in (r, y)** — out along the
  bottom, up the side, in across the top — or the faces wind inward and the
  object renders inside-out (the stool cushions did). `lathe()` also snaps the
  axis normals, or domes shade as pinwheels.
- **Never feed a `ShaderMaterial` to `PMREMGenerator.fromScene`.** The sky shader
  came out as NaN: every material using that environment rendered black and
  bloom smeared it into black blocks. The street dome is vertex-coloured.
- **The environment map is the room's fill light**, not decoration. Any change
  of lighting state (closing time) must rebuild it — `buildEnvironment(true)`.
- **Light maps need `uv2` AND their own material instance.** A shared material
  carrying a light map applies it to meshes with no `uv2` as one constant
  sample (that is why the front wall does not share the left wall's limewash).
- **Code that runs before `loadCafe`** (the plaque, the press frames) cannot use
  `CAFE.mats`, `mtx` or `Batch` — temporal dead zone. `galleryFrame()` exists
  for that.
- **The fitted ACES holds the darks down** harder than the one-liner it
  replaced: grade offsets that were harmless before clip walnut, bronze and
  smoked oak to pure black (the night grade's exposure had to move).
- **Hex colours are LINEAR here** (r134, no colour management): `0x3e4246`
  renders as a light grey, not an anthracite. A surface meant to look dark
  needs a genuinely dark hex (the fridge interior is `0x1c1f22`). Vertex and
  instance colours are linear too — convert sRGB picks with
  `convertSRGBToLinear()`.
- **The interview shot is a shift lens** (DA audit phase 1, 2026-09-29): the
  camera looks level at its target's height and `setViewOffset` slides the
  frame down, so verticals stay vertical; `levelK` blends it off for the
  chase. Two traps: `setViewOffset` REWRITES `camera.aspect` as
  fullWidth/fullHeight (pass the aspect, or the picture is squeezed square),
  and anything rebuilding view positions from depth must add the
  off-centre term — SSAO's `uOff` is projection `[8]`, `[9]`.
- **Where the bar's globes hang is measured** (`BAR_GLOBES`): from every
  gameplay camera (desktop, ±.10 parallax, portrait) only x −.22..0 and
  x 2.77..3.19 clear both the left TV and the menu. Move the shot or either
  of those, re-project before moving a globe. The model's cables are HIDE'd
  (each globe's stem runs to the rail) and its bulbs are offset into the
  globes; the third bulb is hidden.
- **The parser can bake a half-turn** (`parseOBJGroups`' 4th argument): the
  espresso machine's parts (`MACHINE_TURN`) turn about their body's centre
  at parse, so they still merge by material — no SPECIAL, no extra draw call.
- **`mergeGeos` keeps vertex colours** (white where a part has none), so
  baked-colour props (`croissantGeo`, `painAuChocGeo`) batch like anything else.
- **The room's light is BAKED** (DA audit phase 2): floor, ceiling and four
  walls carry Cycles light maps (`gi/*.jpg`, pipeline and weights in
  `gi/tools/README.md`). Mixed lighting: the bake is the sky, the
  non-three.js emitters and the bounce of the real-time lights; on those six
  receivers it REPLACES the indirect diffuse (`giPatch`), the lights' direct
  light stays live. **Move a wall, the counter, furniture or anything that
  stands on the floor and the maps must be re-baked** — they would show the
  old shadows. The export skips multiply/additive materials (the furniture
  blobs once baked as white emitters) and the blobs are hidden once the
  floor's bake is on (`FURN_BLOBS`). `?nogi`, `?gigain=`, `?noprobeenv` for
  comparisons.
- **With the bake on, `scene.environment` is a photograph of the room**
  (`captureProbe`, re-taken at closing time), not the "maquette": people and
  furniture take the baked room's light. The floor and a reflection layer
  over all glass read it BOX-PROJECTED (`boxProject`) — anything that edits
  `envmap_physical_pars_fragment` on those materials must keep that patch.
- **The barista's aisle is 61–69 cm now**: the back bar, the grinder and the
  cup stacks on it are HIDE'd and the counter lost 12 cm on HER side at parse
  (`COUNTER_BACK`, the captured boxes follow). Its face, the stools, the
  laptop and every route are where they were. The counter stool in front of
  the till is gone (nobody sat there).
- **Outside there are passers-by** (`PASSERS`, kind `passer`): three real
  bodies on the café's own west pavement, x -4.35..-5.85 (a metre off the
  young trees), never inside, never recruited by the jukebox (its crew is a
  fixed list). They stand at the pavement's `.15`. Bikes, a terrace and an
  A-board stand outside the storefront, measured off the courier's lanes
  (bikes 2.8 m, terrace 1.4 m, A-board 2.1 m) and out of the door's swing.
  The street's sun is the room's sun now (west, late afternoon).
- **The espresso machine is built in code** (`buildMachine`): the model's
  body, lid and facade are HIDE'd; its groups, portafilters, wand and gauge
  stay (MACHINE_TURN). Steel (`inox`, the machine's polished panel) reflects
  the photographed room box-projected, not STEEL_ENV, once the bake is on.
- **Shadow maps are NOT re-rendered every frame** (`renderer.shadowMap.
  autoUpdate=false`, `needsUpdate` one frame in `SHADOW_EVERY`: 2 desktop,
  3 phone — DA audit phase 4, the mobile budget). Anything that makes a
  shadow change in a single frame and must show at once (a light switched,
  a caster teleported) sets `renderer.shadowMap.needsUpdate=true` itself.
  Far eyelids are hidden (`cullLids`, `EYE_FAR`); on a phone small casters
  lose `castShadow`.
- **The room has a sound** (`ambBuild`/`ambTick`, all synthesised,
  THE ROOM'S SOUND): it starts once the page's AudioContext (`lipCtx`) is
  running, ducks under `speaking` and `JB.on`, obeys `muted` (the mute is
  the page's now: "Mute the sound"), and is cued by the barista's `BAR`
  modes and `openDoor()`. `ambBuild(ctx,dest)` takes any context — render
  it offline to listen (film/sound.js). `?noamb` turns it off.
- **Scanned materials** (`applyScans`, `tex/scan/`, 1.3 MB): oak, walnut,
  travertine, limewash/tadelakt and leather take a CC0 scan's normal and
  roughness, and its detail OVERLAID on the painted colour (luminance
  normalised to .5, so the palette does not move). The wood scans' normal
  and roughness are pre-rotated so the grain runs along v (boxUV); their
  detail maps are rotated by the page. Normal/roughness ride the MAP's uv
  transform (one per material in r134), so they are tiled in canvases to
  match the colour. A scanned material is flagged `userData.scanned` and
  the idle Sobel/roughness jobs skip it. The floor keeps its painted
  point de Hongrie; `paintChevron(…, grain)` cuts each plank from the oak
  scan. `?noscan` shows the painted room.
- **Roughness maps**: `roughFromCanvas()` (paint luminance + a tileable wear
  field, written to G, linear) runs in the same idle queue as the normals
  (`RGH`); a material that gets one is set to `roughness:1`, the map carries
  the absolute value. Steel reflects `STEEL_ENV`, a painted panorama — the
  room's environment is too even for metal to read as metal.

## The people (people.bin) — what bites

The cast is skinned onto the rig's own `THREE.Group` joints (`realizeRig()`,
section `REAL PEOPLE`). The capsules are still built first and are the
fallback. Rebuild the asset with `people/build_all.sh` (Blender 4.5, source
mesh not in the repo — see `people/README.md`).

- **Height never goes through `root.scale`.** The pelvis rides at .855
  because every seat was measured against it, and "seated" IS `rootY<0` —
  for the pose layer and the give-way rule alike. A woman scaled to .95 on a
  window stool needs a positive `rootY` and stands up off it. The `up` trait
  shortens the upper body instead (`morphPoint`).
- **Real bodies sit 3.7 cm higher on chairs** (`seatPelvisY()` → .597, not
  .56): a capsule hip bottomed out exactly on the seat, a real seat carries
  more of the person under the joint. Measured by CPU-skinning the lowest
  pelvis-led vertex. Stools (`rootY -.01`) needed nothing. Any new seat code
  goes through `seatPelvisY`, and `SEAT_POSE_REAL` (hips -1.45, knees 1.3)
  keeps the soles on the floor — the capsule angles sank them 6 cm.
- **Never name a shader variable `r1`, `r2`, `m0`, `v0`…** three's cube-UV
  chunk `#define`s them (`r1` is `0.8`), and every material lit by the room's
  PMREM environment includes it. The syntax error names the number, not you.
- **Real eyes turn less** (gaze yaw .30 / pitch .16, the head takes the rest)
  and the upper lid is written EVERY frame in `blinkLayer`: it rests on the
  iris and follows a downward look. An eye looking down under a lid that stays
  up is all white above the iris — the "blind" stare.
- **Props on joints were cut for capsules.** `realProps()` refits them (the
  scarf, the ice bags); aprons are cloth now (`apronC` in the outfit) and the
  old boxes are hidden. Hand-held things use `gripPoint()`, not the wrist:
  a real hand is 21 cm long.
- **Faces are paint on the BASE head** (`base` attribute = the unmorphed
  position): a trait that moves the face must not move the paint with it.
- **LOD**: `THREE.LOD` with two skinned meshes on one skeleton, swap at
  `REAL_LOD_FAR`; touch devices build only LOD1, except Simon. LOD1 keeps
  the head and neck EXACTLY as LOD0 (`pp_lod.py`): a head decimated without
  symmetry comes out lopsided, and a lopsided head reads as a face that is
  off-centre. Do not mirror the collapse either — against the protected head
  it threw a shard of skin from the chin across the chest.
- **Garment kinds** (DA audit phase 3): the file says blazer = sweater (2)
  and shirt = tee (1); `dressGeometry` gives the blazer **7** and the shirt
  **8** so they shade as woven wool (lapels, button) and as a shirt (placket,
  buttons). realShader tests kinds with `K(n)`, never `vKind>5.5` — any new
  kind would have been taken for hair. Knit ribs follow the body
  (`ribPh`: arc length round the torso or the sleeve); a sine through a
  plane in rest space draws contour rings on a chest — the knit and the
  twill both read as wood grain until they were rewritten.
- **Hands are curled at dress time** (`REAL_CURL`, default .7 rad, Simon
  .3): a constant-curvature bend of every wrist-led vertex past the
  knuckles (y .805 rest), the thumb (z > -.02) left straight. The rig has
  no finger bones; a new pose that needs open fingers needs a per-rig curl.
- **`solveArm(…, palmDown)`** also turns the forearm so the palm faces the
  table; without it Simon's "flat" hands stood on their edge.
- **The scalp takes the hair colour** within 2 cm of the style's shell
  (dressGeometry, hashed grid); the shell's silhouette is frayed by a
  hashed discard in rest space. Ears and face below the hairline keep skin.
- **Skin wraps its direct light** (`SKIN_WRAP`, a patched
  `lights_physical_pars_fragment` for this material only) and its roughness
  follows the T-zone. The eyes are `MeshPhysicalMaterial` with a clearcoat
  cornea and an sRGB iris canvas (it was read as linear: grey eyes).
- Simon's old primitives are hidden, never deleted: `mapSimon()` reads the
  animate loop's writes to `simonHead` / `eyeGroups` / `mouthMesh` /
  `rShoulder` back onto the real rig, and puts `simonHead` on the real head
  every frame because every glance in the room is aimed at it.

## The street (THE STREET block) — what bites

- **`camera.far` is 450**, not 25. Anything that assumed 25 (a shadow box, a
  CoC, a clip) must read `camera.far`. The DOF pass now always runs on "high"
  because it carries the street's distance softening (`dofMat.uBg`); a
  `uRange` of 8 m or more contributes NOTHING by design (it only ever meant
  "skip the pass").
- **Every material outside goes through `streetMat()` / `streetInject()`**:
  it gets the street's sun (an injected `RE_Direct`, NOT a scene light — one
  more light re-lights the whole room), the street's haze instead of the
  room's fog, and the night fade. A new outdoor material that skips it will
  sit in a different day. Give each variant its own `customProgramCacheKey`
  key, or three reuses the wrong program.
- **Varyings that pack integers must be rounded before `mod()`**: a constant
  varying comes back as 7.9999995 on some rows. `aG.w` (shop + 2×floors) did
  exactly that and turned whole scanlines of a house into a shopfront.
- **Facade detail fades per axis** (`dw.x`, `dw.y`), never on one shared
  width: a wall seen edge-on is fine across and sub-pixel along.
- **The courier's route still owns the car park.** The pavement trees keep
  the model's trunk positions (the z 2.7 squeeze is audited against them),
  the bay in front of the door (z -1.68..0.74) stays empty, and nothing new
  stands behind the vans' doors past x 11.30. Any new outdoor object near
  x 7-18, z 0-3 needs the route audit.
- **The flying man** is realized lazily (`buildHero()` once `REAL.ready`) and
  stops at x -10.2, z -12.5 because raycasts from SHOTS.gameplay to thirteen
  of his joints find nothing in the way there (at x -12.6 a mullion cut him
  in half). Move the shot, re-run `.work/exterior/probe_hero.js` (a `PROBE=`
  script for `shoot.js`) and move the stop.
- **HENRY TV is a render-to-texture studio** (`TVS`, `tvBuild`, `tvRender`):
  its people are `buildPerson` + `realizeRig` rigs re-parented into the
  studio scenes (not agents — they never walk and never take part in the
  wardrobe or the gaze lottery). Their mouths go through `tvMouth()`, which
  moves Simon's mouth mesh onto THEIR morphed lips (a fem / short face put it
  on the nose). Both renders force ACES tone mapping and restore it: the
  café's own renderer runs NoToneMapping into the HDR target.
- **Clothes are allocated, not rolled** (`pickDistinct()`, NO TWO ALIKE):
  any new cast member or rack colour must keep ΔE ≥ 16 (cast) / ≥ 12
  (extras) against everything worn, measured on the DISPLAYED colour
  (`shownLab` treats the hex as linear, as the café feeds it).
- **The vans' cabs are `CAR_TYPES.vancab`** (placeCar), the model's cabs,
  wheels and lamps are HIDE'd. The boxes and the ICE CUBE leaves are still
  the model's; door hardware is `vanDoorKit()`, a child of each leaf so it
  swings with it. Mirror heads end at z 0.80 and the step bumper at x 11.30:
  both are courier-lane clearances.

## Conventions

- **Commits** — conventional style with a scope, then an em-dash clause, in
  French: `fix(café/marche): la foulée cesse de mentir — …`. Dense subject
  lines; a body when the change earns one, with the measured numbers in it.
- **Comments** — English, dense, and they explain the WHY, never what the next
  line does. Match the surrounding density; this file is written with care.
- **Docs** — `README.md` is English, `VIRTUAL_COFFEE.md` is French. Keep it
  that way, and keep both in step when the room changes.
- `prefers-reduced-motion` (`const RM`) is respected seriously: under it nobody
  walks. Any new movement needs an RM branch that still leaves the scene alive.
