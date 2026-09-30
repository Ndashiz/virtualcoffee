# Virtual Coffee

An interactive 3D resume. "Take a seat" spawns your character by the door and
**the arrow keys are yours** (physical WASD works too, which lands on ZQSD for
AZERTY, or a tap on the floor — the only control a phone has): nothing moves
until you move it, so Simon calls you over out loud. A third-person camera
follows you across the room — drag to look, wheel to pull back, Shift to run —
to the chair across the table from him, marked by a ring on the floor, an
arrow and a sign above it — look for the **green cushion**, which is what the
welcome tells you to look for. Simon greets you the moment you step in and
tells you to have a wander first; the conversation itself waits until you are
actually in the chair.

Sitting down raises the CV to near full-screen and he starts talking over it
straight away — the line is the caption to what you are reading. It goes back
down when he finishes, or the moment you click beside it or hit the ✕ riding
its corner — no one is made to sit through the monologue — and the
**dialogue box** opens down the left: five
sections — work experience, education, skills, certifications, languages —
each of which Simon talks you through out loud while he looks you in the eye —
his words, read by a voice model (see "Voice"). A section you have heard right through keeps a green
marker; ask for it again and he says so before repeating himself. Work
experience has two openings and picks the one that fits what you have already
heard. Once all five are done a **second tier** opens — off the clock, AI long
term, why banking, how I built this — along with the wrap-up. The box carries
a permanent **See the resume / Download it / Leave the table** row from its
first option: seeing the sheet again or keeping it must never be more than one
tap away. On a touchscreen that tap opens the sheet full-screen in the readers'
overlay instead of lifting it into the room — a whole A4 framed on a phone is
five-pixel body copy — so the phone gets the page whole, at 17 px, panning under
a finger. Leaving is not quitting — stand up mid-visit (the sit-down blend,
run backwards), wander the room, and the moment you take the chair again the
box reopens exactly as you left it, green markers, tier and all. Sit at one of
the window tables and **a waiter brings you a coffee** — tray in hand, stooping
to set the cup down in front of you — and comes back for the cup once you have
gone. The **LinkedIn
link rides in that row too, from the very first option** — it used to be the
outro's reveal, which put the one link a recruiter actually wants behind eight
minutes of audio. The outro ends the visit. When Simon finishes that outro the
barista comes over, says they're closing, and the room empties around you.

**A reload costs nothing.** The visit rides in `sessionStorage` — per tab,
gone when the tab closes — so a page that comes back (a phone discarding a
background tab is the usual reason, and why "left alone for ten minutes" used
to return you to the front door) puts you straight back in the chair with your
green markers, your unlocked tier and your outro state. No welcome, no walk, no
monologue, and deliberately no audio: there is no user gesture on a reload, so
the first section you click is what turns the sound back on.

There is a mute pill (or `M`) for the voice, a skip pill (or `space`) to cut
him off, and the subtitles carry every word without sound. English only (the FR
mode was retired: the scripts only exist in English). Under
`prefers-reduced-motion` the walk is skipped: you appear seated at once.

**Live** : <https://ndashiz.be/virtualcoffee/>

## How it is served

GitHub Pages serves the café; the VPS answers one question about it.

`ndashiz.be` is a Cloudflare-proxied domain whose origin is the **user** site repo
`Ndashiz/ndashiz.github.io`. Every other repo on the account is published as a
*project* site underneath it, at `ndashiz.be/<repo-name>/` — so this repo being
named `virtualcoffee` is what produces the URL. Renaming the repo moves the site.

```
git push  →  GitHub Pages  →  ndashiz.be/virtualcoffee/
                              └── ~1–2 min build, then Cloudflare cache (~10 min)
```

That is the whole deployment. There is no server to restart and nothing to copy.

### Why the CV is not on the VPS

Moving it there was tried and deliberately reversed. Serving the café from the
VPS would have made the switch same-origin and removed every line of CORS below
— but it would also have made **the CV itself depend on a personal VPS being up**.
A resume that 404s because a box rebooted is a worse failure than a switch that
occasionally cannot be flipped, so the dependency runs the other way: Pages
serves the page, and only the *switch* asks the VPS.

The route that would have made it possible — a Cloudflare Origin Rule
overriding the origin for `/virtualcoffee*` — turned out to be a paid feature on
this account, which settled the question.

`jarvis/deploy/nginx-virtualcoffee.conf` and `deploy-virtualcoffee.sh` are kept
as a working standby: they still publish and serve the café correctly, and the
ping's absolute url means the page behaves identically either way (its origin is
`https://ndashiz.be` in both cases). If you ever enable that path, remember the
copy under `/var/www/virtualcoffee/` drifts the moment you stop deploying to it.

### Still true

- **The LazyPO Cloudflare Worker does not apply here.** Its route is
  `ndashiz.be/pro/*`, so `/virtualcoffee/` gets no auth gate, no CSP and none of
  its security headers. Nothing on this page needs them.
- **`robots.txt` cannot live in this repo.** Crawlers only read
  `ndashiz.be/robots.txt`, served by `Ndashiz/ndashiz.github.io`. Same for a
  sitemap entry.

## Layout

```
index.html          Everything: markup, CSS, the VC shell, the scene code
ANATOMIE.md         Body measurements + 100 joint criteria — the cast's reference
cafe.obj.txt        The café itself — real 3D model, ~95k tris (5.1 MB, ~980 KB gzipped)
tex/*.png           13 baked label maps — trophy cabinet, diplomas, van (~376 KB)
DIRECTION_ARTISTIQUE_2026.md  The 2026 design brief, space by space (French)
people.bin          The cast's bodies, clothes and hair — one skinned mesh per person,
                    two levels of detail (~1.1 MB, built by people/)
people/             The offline Blender pipeline that writes people.bin
person.obj          Retired segmented body (USE_PERSON_MESH=false, never fetched)
fonts.css           @font-face for the three self-hosted families
fonts/*.woff2       Space Grotesk · Inter · Caveat (latin + latin-ext)
three.min.js        three.js r134, vendored
audio/en/*.mp3      The narration, one file per clip (see "Voice")
audio/en/v1/*.mp3   The retired v1 recordings — kept, never loaded
audio/music/*      The jukebox's four tracks — Simon's own songs; lazy-loaded,
                    never fetched before someone presses play
preprocess_music.py A small numpy DAW + afconvert (AAC 128k) — source of the three
                    original tracks they replaced (removed from the repo, alive in git)
og.jpg              1200×630 share card, rendered from the scene itself
favicon.svg
.nojekyll           skip the Jekyll build on Pages
```

**Why the model is a `.txt`.** Pages serves `.obj` as `application/x-tgif`,
which the CDN will not compress — the old 1.35 MB model went over the wire
whole. As `text/plain` the same file gzips better than 5:1, so a model nearly
four times the size lands *lighter* than the one it replaces. The loader
fetches a URL and parses text; the extension means nothing to it.

`cafe.obj.txt` is preprocessed offline from the stage tool's glTF-binary export
into **final world coordinates** (Simon's table at the origin, tabletop at
y=.8025 — the height every scene anchor assumes), quantized and deduped, one
`usemtl` per object. The scene has its own ~60-line parser: no `OBJLoader`
exists in the r134 UMD build, and none is needed for a file this repo itself
produces. Faces merge into one mesh per material (~55 draw calls). Since the
2026 design pass the model's French `usemtl` names (`chene_sol`, `laiton`,
`marbre`, …) are only the starting point: the loader re-assigns objects to
the material they PLAY by name (`REMAT`), drops what the new furniture
replaces (`HIDE`) and keeps the bounding box of everything it rebuilds
(`CAPTURE` → `CAFE.boxes`) — see "The design pass" below. If the fetch
fails, the room is gone but the table, Simon and the resume are all
procedural: the conversation survives on a bare parquet.

The map also carries what the room could never show before: a **front wall**
with Simon's trophy cabinet (PSPO, PSM I, Dynamics 365, Azure, the Solvay
diploma, Le Wagon), and a **real outside** — a parking lot with a van and a
car, and a treeline — visible through the storefront (since 2026-09-28 the
treeline and the car are gone and both windows look onto a real street: see
"The street"). The trophy labels ship as
baked PNG under `tex/` because they carry awarded titles and vendor marks;
everything else stays procedural.

The map's three framed press clippings are **dropped** in the preprocessor
(`DROP_NAMES`), and the pair `drawPress()` used to paint on the back wall went
with them: a café papered with invented headlines about its own owner reads as
bragging. What hangs on that wall now is one small plaque — *Employee of the
Month*, awarded to a man nobody in the room has ever met — painted by
`drawEotm()`, and, back by popular demand, four
frames of **The Daily Salfari** (`drawArticle()`): the building he rebuilt
alone, the first triathlon, the one-man web-and-AI studio, and the unpaid
syndic of his own co-ownership. The rule was never "no press" — it was
"no invented press", and all four actually happened. Each hangs in an oak
gallery frame with an ivory mat under its own bronze picture light.
Like the plaque they are registered readables: walk up and they open full
size, article legible, ink illustration and all — and once one is open,
**an arrow either side steps to the next story** without walking back to the
wall (the plaque and the television stay out of that ring: one is not an
article and the other is not a page). The preprocessor also squares up the eight wheels (the export
mounts them sideways), copies the ICE CUBE lettering onto the van's rear doors,
moves the plant off the one run of wall a toilet door fits on, and clones the
van one parking bay over for a second firm — BravoReno the electrician, whose
livery the scene paints (`drawBravo()`).

**The van has a driver now — and he delivers INSIDE.** On a slow loop
(~55 s, most of it spent with the tailgate shut so the lettering stays a
readable poster), the ICE CUBE courier appears from behind the cab, swings
the two rear leaves open — real doors now, split on the ICE|CUBE seam, each
carrying its half of the decal — takes two printed bags of ice off the sill,
crosses the lot, steps the kerb and the threshold (the ground function knows
all three levels), shoulders through the café's own swinging leaf, hands
full, and carries the load across the room and round the EAST end of the
counter — the barista's own authored lane. The bags go down on the floor at
the mouth of the service aisle, by the drinks fridge: the counter body hides
the bags themselves from the room, so what reads is the gesture — he bends
behind the bar, he comes up empty. The barista turns to watch the delivery
land, patrons glance over (the ice man outranks the window in the gaze
lottery), the stroller yields the doorway while the courier holds it, and
the delivered pair stays on the floor until the next round restocks it
off-camera. The walk back out is the tell that sells the whole act: hands
free, arms swinging in opposition, longer stride, +18% pace, chin up —
against the loaded walk in, leaned back, arms pinned dead straight, short
heavy steps, eyes on the floor. Half a second's pause at the van, both
leaves shoved shut, back around the nose to the cab. Behind the doors the
scene builds the cargo bay the model never had (the closed box's own rear
face is stripped at load): dark walls, a pale alu deck, a part-worked
pallet, and one 6500 K strip across the head of the opening — the only cold
light in a warm scene, which is what reads as refrigeration. One mark,
three supports: the same canvas letters his shirt (chest and back,
straddling the torso cylinder's UV seam) and the bags, while the van keeps
its baked PNG.

Around the delivery, the outside grew up (2026-08-23, Simon directing from
the chair): all three vehicles are **reparked onto the ligne_place grid**
they used to straddle (fixed in the preprocessor and in the shipped OBJ);
the painted backdrop behind the window bay is now **his actual skyline** —
a Big Four house and two banks the café already talks about, *NdaBank
Private Wealth* and *HENRY Investment Bank*, names on plates sized to
survive the glass; and the **flying man stops now**: he sweeps in, pulls up
at the bay, hangs there looking into the room for a beat — the gaze lottery
lets the window bar catch him at it — then leaves the way he was going.
The welcome card teaches the real rules at last: the yellow circle is where
the interview starts, and the café hides the rest — walk up to things and a
bubble says what they can do. Inside, the laptop guy's screen runs LazyPO
(sprint board, burndown and all), and both faces of the VIRTUAL COFFEE sign
plus the trophy-cabinet banner finally read the right way round — the sign
canvas was painted mirrored for both quads, the plaque PNG was stored
rotated 180°.

**Two televisions, one feed** — HENRY TV, sound off: six stories on an
eight-second loop (a 48-second "video", which is what the player's scrub bar
actually measures), a presenter whose mouth moves, and a ticker carrying only
real quotes. Since 2026-09-29 the feed is a small 3D studio rendered into a
texture (`tvBuild()` / `tvRender()`, 768×432, 15 Hz — 512×288 and 8 Hz on a
phone): the presenter is a real person from the café's own skinned-body
pipeline, in a burgundy blazer behind a lacquered desk under a three-point
light, talking with Simon's mouth, blinking, glancing down at her notes, in
front of an out-of-focus set; the story box over her shoulder carries a
broadcast chart that draws itself in (area, previous close, price flag) for
the three market stories, and a real scene for the other three — NdaBank's
chief executive in a charcoal suit and tie at a walnut lectern, in front of a
navy step-and-repeat, with gooseneck mics, the press pack's flagged mics and
their flashes; EU flags stirring in front of a glass facade; a trading floor
at night for tonight's programme. For those three the gallery CUTS to the
picture full frame from 2.2 s to 6.6 s of the story, then back to her — the
way news runs footage, and the only way a man at a lectern reads at the size
of a café television. The channel furniture (bug, clock, lower
third, ticker) stays crisp 2D over the render, and the render is filmic
(ACES) so the key light does not burn her face. The painted feed (`drawTV`)
still runs until people.bin lands, and the zoom reads the studio's own frame
back (`tvReadInto`).

Walk up to a screen or the plaque and a bubble says it opens; click and
`openZoom()` re-runs the painter at 2× into a full-screen canvas rather than
blowing up the wall texture, so the ticker is legible — a second of "connecting
to the live", then the picture, a progress bar and the current story. One big
arrow sends it back.

### The people (real bodies, 2026-09)

Everyone in the room — the cast, the extras, the guest and Simon — is now **one
continuous skinned body**, not a stack of capsules: `people.bin` carries
FinalBaseMesh re-posed to the rig's rest, heat-weighted to the rig's **own
joint names**, so a `THREE.Skeleton` binds straight onto the `THREE.Group`
joints `buildPerson()` already makes. Every behaviour layer, `applyPose()`
and its `LIMITS`, the seats and the props keep driving the same joints —
nothing about how people move was rewritten. The capsules are still built
first and only swapped once the file lands (`realizeRig()`), so a failed
fetch leaves the old cast in place.

- **Dressed, not painted.** Tee, shirt, sweater, blazer, trousers, shoes and
  a bistro apron are shells cut from the body offline — hems exactly on a
  line, cloth that falls from the chest and the shoulder blades instead of
  clinging under them, sleeves that taper. The body faces a garment covers
  are dropped at runtime; body + clothes + hair merge into **one draw call
  per person** (the capsules were ~30).
- **Faces.** The base head's eyes are cut open; real eyeballs turn in the
  sockets under upper lids that rest on the iris and follow a downward
  glance; brows, lashes, lips, stubble and beards, the fuzz of a hairline and
  the lines of age are painted per person onto a canvas projected round the
  head. Eight haircuts, each a shell that thins to nothing at the hairline.
- **Who they are.** `fem` and `heavy` are displacement fields applied to
  body, clothes, hair and joints alike (shoulders, waist, hips, bust, jaw,
  brow, nose, lips; belly and limbs). Height shortens the upper body and never
  goes through `root.scale` (see CLAUDE.md). The cast sheet — who wears what,
  which haircut, which beard — is `REAL_TOPS` / `REAL_HAIR` / `REAL_BEARD` /
  `REAL_TRAITS`.
- **Simon** is a real body too, seated at his table with his hands placed by
  a small IK solve, in the navy blazer, round tortoiseshell glasses,
  moustache and goatee of the photo; the old head/eye/mouth handles are read
  back onto him every frame (`mapSimon()`), his voice opens a real mouth.
- **Cost.** One `MeshStandardMaterial` per person (shared program) with an
  `onBeforeCompile` for the paint, fabric and skin micro-relief and a hair
  sheen. LOD1 beyond 6 m and everywhere on touch devices except Simon
  (head, neck and hands as LOD0, the rest at ~35 %). Draw calls went 772 → 319 (desktop), triangles
  242 k → ~435 k in the main pass.

`person.obj` is currently **retired** (`USE_PERSON_MESH=false` in the scene):
the segmented base-mesh bodies read as ragged mannequins next to the capsule
cast, so the capsules stayed the look until the continuous bodies above
replaced them (the capsules are still what renders if `people.bin` fails). The whole swap pipeline is still in the file and the asset
still ships, for a future better-cut mesh: it is a decimated base mesh cut
offline into fifteen segments, each exported **in the local space of the rig
joint that carries it**, so the swap is just "remove the cylinder under this
joint, add this mesh under the same joint" and every behaviour written for the
capsules (gaze, turn-taking, sip, walk, `reskin()`) drives either body
untouched. Flip the flag to try again.

Before that, the capsules got the pass they had been owed: **hands
with five digits** (a palm, four fingers and a thumb, shared geometry, and
cheaper than the ball they replace), **ears**, **shoulders that meet the body**
— a deltoid cap bridges the joint, with the arm socket a centimetre in from
where it used to float — and **a neck you can see**: the trapezius pad used to
top out a centimetre and a half under the skull, which reads as a head set
straight onto a pair of shoulders. Simon got the same treatment, his collar
lowered and his head lifted to 1.67 (`SIMON_HEAD_Y`, which the animate loop
breathes around).

Half the cast are **women**, told by longer hair falling to the nape and by
the silhouette the reference sheet asks for (shoulder-to-hip 1.45 on a man,
0.92 on a woman — he tapers to the waist, she flares to the hip); worn down,
that hair takes the ears with it, and hangs behind the throat so the neck
still reads in front of it. The stroller and the guest roll their gender with
the rest of the wardrobe in `reskin()`.

**[`ANATOMIE.md`](ANATOMIE.md) is the reference for all of this** — two
morphology sheets and a hundred joint criteria — and it is not decoration: the
`LIMITS` table in the scene encodes those criteria and is enforced in
`applyPose()`, the single point every animation layer's pose lands on. An
elbow cannot hyperextend, a knee cannot bend forward, a hinge cannot bend
sideways and nothing turns faster than 300°/s, no matter what a gesture
written later asks for. That guard exists because the alternative had already
failed: Simon's own rest pose sat at +.5 on the elbow — a forearm folded
backwards out of his arm — and nobody caught it for months.

The typing pose is **solved rather than eyeballed**: two-link IK from the real
numbers (shoulder at 1.335, keyboard at 1.231 and .50 forward, upper arm .30,
forearm .25) lands the laptop guy's wrists on the keys, where the old
hand-picked angles left them 12 cm low and pointing into the room. And the wall clock **runs**: it reads
the visitor's own time, second hand included, instead of being stamped once at
load and drifting for the rest of the visit.

No build step, no bundler, no dependencies to install. Open `index.html` or:

```bash
npx serve -l 4321 .
```

The ping still goes to the real `jarvis.ndashiz.be`, but the backend grants CORS
to `https://ndashiz.be` only, so the browser refuses the answer and the café
stays open. You get a console CORS complaint and nothing else — which is exactly
the production behaviour when the backend is down. That is the point, not a gap.
To exercise the closed café locally, see "Trying the closed café locally" below.

## The street (2026-09-28)

Simon's brief: the outside had to stop reading as a screen. It did because
of three things, and all three are gone:

- **the far plane was 25 m.** The street and everything past it were never
  drawn; the sky dome filled the hole — and its colours were raw hex read as
  linear, so nearly white. `camera.far` is now 450 (depth precision is set by
  `near`, so the room loses nothing), and the sky (`skyMat`) is a proper
  linear gradient with the sun's glow and a drifting layer of fair-weather
  cumulus, flattened into the haze at the horizon;
- **the west bay looked at a painted plate** 65 cm behind the glass. It now
  looks across a real 30 km/h street — pavement with bollards and two young
  plane trees, cars parked both sides, a zebra, road signs — at a row of
  Brussels facades 24 m out: **BIG FOUR**, **NdaBank Private Wealth**, a white
  maison de maître, a boulangerie, **HENRY Investment Bank**, broken by a cross
  street for depth, with the skyline's towers beyond;
- **the car park sat in a forest clearing.** The forest, the guard rail and the
  grass are dropped at load (`HIDE`); across the street stands a second row of
  houses (a pharmacie with its green cross, a brasserie…), and two blocks
  close the car park's sides.

How it is built (`/* ---------------- THE STREET` in `index.html`):

- **One shader paints every facade** (`FACADE_MAIN`): bays, stone sills and
  lintels, painted frames with glazing bars, curtains and blinds, brick
  courses or stone joints that fade out per axis before they can alias, soot
  under the sills, grime at the foot, shopfronts with a painted fascia, curtain
  walls for the offices, a third of the windows lit at night — all from eight
  numbers per building (`aF`, `aG`). Forty-odd buildings are one draw call.
  Cornices, roofs and chimneys are real geometry; the shop signs are one
  canvas (`drawSigns()`).
- **The street's own sun and haze.** The room is lit by its own fixtures and
  has been tuned against them for a year, so the sun is not a `THREE.Light`:
  `streetInject()` adds one `RE_Direct()` call to every material out there
  (the facades, the tarmac, the cars' clear coat, the trees, the model's own
  car park and vans) — nothing indoors ever sees it. The same injection
  replaces the room's `FogExp2` with a haze the colour of the sky's horizon,
  so a far roof dissolves into air instead of into a grey wall.
- **Cars are lofted, not boxed** (`carBody()`): a side silhouette, a plan and
  a tumblehome sampled into rings of one fixed topology, so glass, pillars and
  paint fall on exact rows. Clear-coated paint, tinted reflective glass,
  tyres, five-spoke rims, flush lamps, a grille, door shut lines and handles,
  Belgian plates, a soft contact shadow. Nineteen cars, merged by material.
- **Trees are London planes**: branching limbs with a mottled bark, crowns of
  leaf cards whose normals point out of the crown so they shade like a
  volume, swaying in the vertex shader (still under reduced motion).
- **Depth of field is a lens now, not a switch**: the DOF pass also softens
  the far side of the glass with distance (`uBg` — under a pixel at the
  parked cars, about three at the roofs), with an early-out so the room, in
  focus, costs two taps a pixel.
- The vans keep the model's cargo boxes — the courier's whole round is
  timed against those doors — but since 2026-09-29 everything forward of
  them is a real light-commercial cab (`CAR_TYPES.vancab`, lofted like the
  cars: raked windscreen, short hood, door glass, grille, wrap-round bumper,
  head lamps) on twin rear tyres, with a roof fairing up to the box, wheel
  wells cut into the box skirt, aluminium posts and bottom rail, a step
  bumper (stopping at x 11.30; the courier stands at 10.95 at most), barn-door
  hardware on the rear doors (hinge straps, locking rods, handle, seal — on
  the ICE CUBE leaves it swings with them), plates, mud flaps, rubbing
  strips, roof rails and mirrors whose heads stop at z 0.80, clear of the
  courier's lane.

**The menu grew** with it: 2.75 x 1.12 m, from just right of Simon's head to
the clock and from the machine's top to 10 cm under the soffit, with a bronze
picture light of its own — lit like the room instead of glowing. Since
2026-09-29 it is written to be READ from the chair (7.6 m away): Simon's
eight coffees in two columns at 54 px on the 832 px board (7.3 cm letters),
each joke on one line, the bakery on a single line beneath, no dot leaders —
and a click opens the whole card full size, like the plaque and the press
(its `menu` key is not in the ping's `ITEMS` yet: the read is counted without
an item until store.ts learns it).

**The jukebox calls you over.** An amber LED strip under its marquee blinks
PICK A RECORD while it waits — the box's own words; the "click"/"tap" lives
in the HUD hint that also labels the frames — and says NOW PLAYING, steady,
once it is on; a string of 27 marquee bulbs round the arch
and down the brass stiles runs a fairground chase — one in four lit and
marching, the whole string flashing twice every 6.5 s with the arch's neon —
and breathes with the track on air. One instanced mesh; the lit bulbs are HDR
so the bloom does the glow. Steady under reduced motion.

**No two alike.** No two people in the café wear the same clothes at the same
time: the cast is ten colours at least ΔE 16 apart as the screen shows them
(clothing hex is fed as linear, so the check runs on the displayed colour),
the extras' rack shares none of them, and every roll — stroller, window
customers, guest — takes a colour at least ΔE 12 from everything anyone else
is wearing (`pickDistinct()`), seen or not.

**The flying man is a man.** He was a 42 cm figure of primitives flying in the
gap between the plate and the wall. He is now built by the real-person
pipeline — 1.88 m, the suit painted per pixel on the real body (blue to the
collar and the wrists, red trunks cut high on the hip, a gold belt, red boots,
the shield), a cloth cape that streams and ripples harder the faster he goes,
lit by the street's sun and hazed like it. He flies the west street at three
to four metres, passes behind the young trees on our pavement, pulls up over
the middle of the street at z -12.5 — exactly where the main shot sees
through the bay — hangs there looking in while the window bar looks back, and
goes. His shadow crosses the tarmac under him. Where he stops is measured,
not picked: raycasts from the main shot to thirteen of his joints over a
grid of stops (`.work/exterior/probe_hero.js`) — the first stop had a
mullion of the bay cutting him in half; at x -10.2, z -12.5 nothing covers
him, no mullion, no tree, no patron's head. The airliner is 36 m of
wingspan 330 m out and 110 m up: you catch it over the roofs from the glass.

Cost, measured on the main pass: +13 draw calls, +31 % triangles on desktop
(707 k), +19 % on a phone (505 k, where the far kerbs lose their parked cars
and the trees stop at 60 m).

## The design pass (2026) — "l'Atelier"

The room was rebuilt as ONE design language — Brussels warm minimalism — in
place of five (bistro brass, diner rug, rustic beams, corporate trophy wall,
a museum cash register). The full brief, space by space and in French, is
[`DIRECTION_ARTISTIQUE_2026.md`](DIRECTION_ARTISTIQUE_2026.md). The system in
one table:

| Role | Material |
|---|---|
| walls, ceiling | limewash, warm white |
| the stage (back wall behind the bar) | deep olive tadelakt — a face reads on a dark ground |
| built-in joinery (bar front, cabinet, window bar, doors) | light oak; the bar front is real fluted geometry |
| service tops | travertine |
| floor | smoked-oak point de Hongrie |
| everything you can move | walnut and blackened bronze, cognac leather seats |
| metals | bronze for structure, stainless for the machine, brushed brass only where a hand goes |

What it changed, and the mechanisms behind it:

- **Nothing moved.** Chairs, tables, stools, lamp globes and the plant are
  rebuilt from the model's own bounding boxes (`CAFE.boxes`, filled at parse by
  `CAPTURE`), never from typed coordinates. Seat heights, centres, cups and
  waiter stands are identical; measured, not assumed (seats .503, stools
  .8051, tops .8025). Table feet are capped at the radius of the cast-iron
  discs they replace.
- **The loader re-dresses the model by role**: `REMAT` (object → material),
  `HIDE` (dropped at parse), `CAPTURE` (boxes kept). `boxUV()` writes world-metre
  UVs for every architectural material — the model's own were at random scales,
  and the front wall had none.
- **Light with a source**: opal globes over the bar and a big one over Simon's
  table (the key spot hangs inside it), a cove along the olive wall, bronze
  picture lights on the press frames, a glowing toe kick under the bar.
- **Baked light**: `applyLightMaps()` paints the cove wash, the picture-light
  pools, the daylight on the parquet and the ceiling halos into canvas light
  maps (irradiance, on `uv2` in world metres). They follow the bar's hours
  (`dimLightMaps()`).
- **The environment is a model of the new room** (`buildEnvironment()`) and
  feeds diffuse as well as specular — it is the bounce light; the street gets
  its own sky environment (`streetEnvironment`), and there is a real sky dome.
- **Post**: fitted ACES (Hill, with matrices) instead of the one-line
  approximation, the `atelier` grade, and depth-only **SSAO** on "high".
- **Removed**: the round rug, the ceiling fan, the neon tube, two poster prints,
  the brass sconces, the cash register, the chalkboard (now a typeset menu
  board, CLOSED side kept). **Added**: a slat raft over the tables, one large
  canvas, a bird of paradise, a tablet till.

Cost, scene pass: 771 draw calls against 758, 238k triangles against 215k on
desktop; 489 / 214k against 476 / 189k on a phone, where the big textures and
the light maps are painted at half size.

### DA audit, phase 1 (2026-09-29)

The quick wins of a ten-axis art-direction audit, applied:

- **The interview shot is a ~30 mm, not a ~21 mm.** fov 40 (was 52), camera
  at 1.32 m (was 1.42), 15 cm closer and aimed 25 cm left of Simon, so he
  sits right of centre where the guest's shoulder and the section panel
  leave the frame free; the whole menu stays in. The lens is **level with a
  shift** (`setViewOffset`) instead of tilted down, so verticals stay
  vertical; `levelK` blends that off for the chase camera. Portrait keeps
  its framing (and gets the shift). The Superman stop was re-probed from the
  new shot: 13/13 joints visible at x −10.2 / z −12.5, unchanged.
- **Two bar globes frame the menu** instead of three cutting it
  (`BAR_GLOBES`, x −.10 and 2.95: the only slots where a globe clears both
  the left TV and the board from every gameplay camera). The model's cables
  are hidden, each globe's stem runs to the rail, the bulbs follow.
- **Steam is one noise ribbon** turned to the lens, not five spheres.
- **The espresso machine faces the barista.** It stood with its groups on
  the customer side; the parser now bakes a half-turn into those objects
  (`MACHINE_TURN`) so they still merge by material. Brushed stainless
  (roughness map + a painted reflection panorama, `STEEL_ENV`), upturned
  cups on the warmer, a brass maker's plate on the room side.
- **Viennoiserie**: a swept, rolled, vertex-baked croissant
  (`croissantGeo`) on Simon's plate, and the empty glass case on the counter
  holds two slate trays of croissants and pains au chocolat.
- **The fridge** is anthracite inside, lit by LED strips (jambs, top, every
  shelf edge), with juice bottles on its floor and a dielectric reflection
  over its door.
- **Roughness maps** where there were none: floor, travertine and walnut
  derive theirs from their own paint plus a wear field
  (`roughFromCanvas`, idle-time like the normals); leather and steel get
  painted ones. Opal globes darken at the limb and show a hot centre; the
  raft's felt is a warm grey, each slat ±5%.
- **The reader** at the window bar sits three-quarters to the room.

Cost, scene pass from the interview shot (`perf.js`, 1440×810): 292 draw
calls against 333 (the tighter lens culls more), 770k triangles against
747k, one light fewer, 78 shader programs against 68. Phone (390×844):
257 / 591k against 269 / 564k.

### DA audit, phase 2 (2026-09-29)

- **Baked light.** The floor, ceiling and four walls carry light computed in
  Blender Cycles from the page's own geometry, materials and lights (six
  JPG light maps, 169 KB). Mixed lighting: the sky through both glazings,
  the cove, LEDs and screens and the bounce of every real-time light are
  baked; the real-time lights keep their direct light and shadows. How to
  re-bake: [`gi/tools/README.md`](gi/tools/README.md).
- **Room reflections.** With the bake on, the room is photographed into a
  cube once; it lights everything unbaked (people, furniture) in place of the
  old environment "maquette", and the floor and a layer over all the glass
  read it box-projected, so the windows' streak lands where the windows are.
- **Edges**: the counter top, window bar, vitrine base and shelf are rebuilt
  as soft slabs (5 mm).
- **Traces of life**: water carafes and glasses, a spoon and a torn sugar
  stick, yesterday's cups, crumbs and a newspaper at an empty table, a
  takeaway cup, a notebook, a jacket on a chair, flowers, umbrellas by the
  door, a cast-iron radiator, an extinguisher, an exit sign, a notice board
  and signage in French and Dutch, wear on the floor where people stand.
- **Service**: the back bar is gone and the counter is 12 cm shallower on
  the barista's side (her aisle: 23–35 cm → 61–69 cm); the stool in front of
  the till is gone; "Commandez ici · Bestel hier", "Retrait · Afhalen", a
  water station, opening hours on the glass.
- **Outside**: one weather (the street's sun is the room's, late afternoon
  in the west), three passers-by on the café's pavement, bikes, a terrace
  and an A-board.

- **Scanned materials**: oak, walnut, travertine, limewash and leather take
  the relief, the sheen and the fine detail of CC0 scans (1.3 MB), overlaid on
  the painted colours so the palette does not move; the floor keeps its point
  de Hongrie with real oak grain cut into every plank.

### DA audit, phase 3 (2026-09-29)

The premium phase, with free tools only (the audit's Character Creator,
MetaHuman, Marvelous Designer and mocap are paid; none was bought):

- **Eyes**: a clearcoat cornea over an sRGB iris (it was read as linear —
  grey, dull eyes); the room's windows and globes are the catchlight.
- **Skin**: wrapped, warm terminator on the direct lights; oilier T-zone.
- **Hands**: fingers curled at rest (a bend modelled at dress time — the rig
  has no finger bones); Simon's palms now lie flat on his table (the arm
  solver turns the forearm).
- **Hair**: dark roots on the scalp under every style, a frayed silhouette
  instead of a shell's edge.
- **Clothes**: the blazer is woven wool with lapels and a button (it shaded
  as a rib-knit cardigan), the shirt has its placket, knit ribs follow the
  body (they drew contour rings), static folds at the elbows, waist, lap and
  knees.
- **The espresso machine** is modelled: rounded steel body on feet,
  cup-warmer tray and rail, polished back panel, steam knobs; steel reflects
  the room.

Not done, on purpose: physically correct light units (the baked GI and
every light were calibrated in three's units; switching would re-light the
room for no visible gain) and SMAA (the FXAA pass stays).

### DA audit, phase 4 (2026-09-29)

- **The mobile budget.** Shadow maps re-render one frame in three on a phone
  (one in two on a desktop) instead of every frame; far eyelids are hidden;
  small props stop casting on a phone; the traces of life share one
  material. A phone's frame went from 298 draw calls to ~185 on average
  (main pass 157, shadow passes 83 every third frame); a desktop's from 331
  to ~250.
- **The room's sound**, all synthesised (no file): room tone, the street
  through the glass, a walla of distant talk, and the bar cued by the
  barista — grinder, portafilter knock, pump, steam, the cup she serves —
  the door's bell, cars, cups set down. *Taken off the page the next day
  (see below); it now only scores the trailer.*
- **The trailer and the share image** ([`film/`](film/README.md)): the real
  scene filmed frame by frame at a fixed step, scored with the same synth
  offline, cut and titled in Blender; `og.jpg` re-rendered from today's
  café (it still showed the capsule people).

Not done, and why: a Gaussian-splat capture of a real Brussels street and a
look-dev review against photographs of a real café both need someone on
location with a camera.

### Fixes of 2026-09-30

Four reports from Simon, on the live café:

- **"The courier has no arms" — and nobody else past 6 m did either.** The
  lighter body (LOD1, `pp_lod.py`) kept the head and neck exactly as LOD0,
  but decimated the WHOLE body at .34 with them only weighted: the head
  alone is more than a third of the triangles, so the collapse ate every
  arm, hand, leg and foot to reach its target. Clothes hid the legs; a
  tee showed the missing forearms. The collapse now runs on a selection —
  everything but the head, neck and hands — at .34 of that (body LOD1
  15.9 k → 11.5 k triangles, every bone leading vertices again), and the
  build fails if a bone loses more than 85 % of what it led.
- **"The back of the van has a bug."** Doors open, the bay showed a white
  starburst on its bulkhead — the new cab's rear cap on the same plane,
  z-fighting — and a bright blue floor 36 cm above the deck: the skirt,
  `bandeau_bas.0`, was a solid box the full width of the van. The bulkhead
  stands 5 cm clear of the cab, the skirt lost its top face, and the load
  floor sits at y .84 over the twin tyres and their well, as in any box
  van, with the skirt's rear face as the step under it.
- **"No more background noise."** The room's sound is off the page (the
  synthesiser lives in `film/sound.js`, for the trailer only); the mute
  button is "Mute Simon's voice" again.
- **"Latency."** The frame is fill-bound: on an M4, pixelRatio 2 in a
  1024×768 window ran 39 fps, 1.5 61, 1 105 — about 8 ms a megapixel. A
  Retina window at full screen (3024×1720) ran 24 fps with one frame in
  ten over 80 ms, and a GPU-bound page queues its frames, so input showed
  late. The post chain now renders at a scale of the canvas that a
  **resolution governor** picks from the measured frame rate (45 fps floor,
  steps .85/.72/.61/.52, never under one pixel per CSS pixel, a failed step
  up is never retried); FXAA upscales into the untouched canvas (resizing
  the canvas froze the page 0.6–1.1 s a time). Same window: 24 → 48 fps,
  frames over 100 ms 24 → 2 in 20 s. `?fullres` turns it off; so does
  automation (`navigator.webdriver`), and `film.js` / `cdp.js` pass it. The
  TV overlay no longer rebuilds a mip chain it never samples, 15 times a
  second.

Cost, scene pass from the interview shot: 323 draw calls against 300,
849k triangles against 829k on desktop; 292 / 646k against 263 / 625k on a
phone.

## The switch — "is the bar open?"

One public endpoint, doing two jobs. The **load ping** asks whether the bar is
open; every ping after it only reports, and its answer is deliberately ignored.

```
GET  https://jarvis.ndashiz.be/api/vc/ping?e=open&s=<session>&l=<lang>&r=<ref>
→    200  {"open": true}          Cache-Control: no-store
                                  Access-Control-Allow-Origin: https://ndashiz.be
                                  Vary: Origin
```

Absolute, and **cross-origin**: the café is on GitHub Pages, the switch is on the
VPS. The grant is scoped to this one route — see "The CORS contract" below, which
is the part of this feature most likely to be broken by a well-meaning edit.

| Param | Values | What it is |
|---|---|---|
| `e` | `open` `enter` `section` `read` `cv` `cvdl` `linkedin` `hb` | what happened |
| `i` | the ten section keys · `press-property` `press-sport` `press-business` · `plaque` `tv` `jukebox` | what it happened *to* |
| `s` | eight lowercase alphanumerics | groups pings into one visit |
| `d` | whole seconds, **cumulative**, capped at 21 600 (6 h) | how long, so far |
| `l` | `en` `fr` | |
| `r` | `linkedin` `github` `google` `direct` `other` | bucketed in the browser |
| `c` | `^[a-z0-9][a-z0-9-]{0,15}$` | campaign tag off a shared link |
| `k` | `1` | one of Simon's own devices — count nothing |

`e` and `i` are closed enums, revalidated server-side; anything else is dropped on
the floor. The endpoint never answers 4xx or 5xx — a malformed query gets a 200
and the switch, because the café must not be able to break itself.

### The two free-text fields, and what actually keeps them safe

An earlier version of this file said there was **no free-text field anywhere**,
and leaned on that as the reason a public, unauthenticated, unthrottled endpoint
was safe. That is no longer true: `s` and `c` are both invented by the visitor.
The argument has to be made properly now, because it is the only thing standing
between this route and everyone on the internet.

A charset bound is not enough on its own — it still lets one caller write an
unlimited number of *distinct* keys, and it is distinct keys that grow a file.
Both fields are bounded by **cardinality** as well:

- `s` — sessions live in a ring of 400, aged out after 30 days. A flood of
  invented ids costs the least recently *active* rows and nothing else. Evicting
  by age of creation instead would throw away tabs that are still beating.
- `c` — at most 24 distinct slugs a day; the 25th and beyond land in `other`.

One trap worth naming, because it cost a real fix. `constructor` satisfies the
campaign pattern — eleven lowercase letters. Read back with a plain `map[key]` it
returns `Object.prototype.constructor`, which is not nullish, so `?? 0` never
fires and `Object + 1` quietly turns a counter into a string that grows by a
character per ping. The server reads **own properties only**. Anything keyed by
text a stranger supplies has to.

### It fails open, and that is the whole design

The field is called `open`, not `closed`, and the client test is exactly:

```js
if (d && d.open === false) markClosed();
```

Strictly `false`. Every other outcome on earth — DNS failure, 502, an adblocker
eating the request, malformed JSON, `fetch` missing, the 2 s timeout firing,
Cloudflare not routed yet — leaves the café **open**. A resume that disappears
because a server hiccuped is worse than one that stays open when it was meant to
be shut.

Only the **load** ping honours the answer. Everything sent afterwards ignores it:
a visitor already seated is not thrown out because Simon flipped the sign
mid-sentence.

### One visit, not one request

`s` is eight characters from the CSPRNG, invented when the page loads. It is a
grouping key, never a secret: it is **never stored**, not even in
`sessionStorage`, so it dies with the tab and a reload is honestly a new visit.

The server counts a visit per **arrival**, not per request. Booking the language,
the referrer and the campaign once per visit rather than once per ping is the
whole point: counted per ping, a talkative visitor who opened six sections
registered as six people "from LinkedIn", and the question was always how many
*people* came from LinkedIn.

### How long they stayed

Heartbeats every 15 s, not an unload beacon. This system already fails silently
by design; the last thing it needs is a measurement that only ever fires at the
one moment a browser is least likely to run anything. A heartbeat that landed is
a fact, the last one to land *is* the answer, and losing the final few seconds is
the entire cost.

`d` is **cumulative, never a delta** — "since the start, this many seconds". The
server adds only what has grown since it last heard, so a duplicated, delayed or
dropped heartbeat costs precision and never correctness, and a replayed old value
can never push a total backwards.

The clock only runs on a tab that is visible and has been touched in the last
three minutes, and a single gap longer than 60 s is discarded outright: a laptop
coming out of sleep reports one enormous interval, and that is not time anybody
spent looking at a café.

Two flushes exist outside the interval, and both are load-bearing:

- **`PING.focus(item)`** flushes *first*, then re-aims the clock. Closing a
  newspaper eight seconds after the last heartbeat has to record eight seconds
  against **that** newspaper, not against whatever is opened next.
- **`visibilitychange`** flushes when the tab goes hidden — on mobile, very often
  the last moment the page runs at all. It passes an explicit "these seconds were
  watched" flag, because by the time the listener fires the page is *already*
  hidden and the accrual test would otherwise throw away the exact slice it is
  there to save. Without that flag the flush is a no-op and every mobile visit
  quietly loses its last partial window. Both flushes are covered by mutation, in
  `test/ping.test.js` — deleting either one turns the suite red.

### What was open, and for how long

`e=read&i=<key>` says a thing on the walls was opened; the heartbeats that follow
carry the same `i` and say for how long. One is a count, the other a duration,
and they are separate events on purpose — a heartbeat naming an item must not be
read as a fresh opening every fifteen seconds.

Room objects carry a **stable key**, not their title: `addReadable` takes one
explicitly. Titles are prose — "The Daily Salfari — sport" — rewritten whenever
the copy is, and a rewritten title would silently open a brand-new counter and
orphan the old one. Both televisions share the key `tv`: they show the same feed,
and "did anyone watch the television" is one question rather than two.

The jukebox is counted but **not** timed. Its panel is not a zoom — it can stay
open while the visitor walks the room — so pointing the dwell clock at it would
credit it every second until something else was opened. It takes the `read`
count and leaves the clock where it was. Timing it properly needs a decision
about what "open while walking away" should mean, and that is parked, not
forgotten.

### Simon's own devices

Two mechanisms, because they answer different problems.

`localhost` and friends are **never** counted, with nothing to arm and nothing to
remember. Local development pings the real backend on purpose — a cross-origin
browser blocks the *response*, never the *request* — so without this every dev
reload and every headless run lands in the public counters. That has already
happened for real, which is why the test asserts it host by host.

Anywhere else, a device arms itself once with `?crew=<token>`, keeps the flag in
`localStorage`, and strips the token back out of the address bar so a link shared
by accident does not hand the exemption to a stranger. `?crew=off` disarms.

And for what is already counted, the Jarvis side has **"that was me"**: it takes
back from a visit exactly what it contributed — same seconds, same items, same
language, referrer and campaign — once, idempotently, and never below zero. That
is why a visit is booked to the day it *started*: the credit and the debit have
to share one day key, or a visit spanning midnight is added to two days and taken
back from one.

### Where the ping lives, and why it is its own `<script>`

`index.html` has three script blocks: the `VC` shell, **the ping**, then the café.
The ping sits between the other two on purpose.

Not inside the shell: a syntax error anywhere in that IIFE leaves `window.VC`
undefined, and `VC` is what swaps in the text resume when the 3D fails. A visit
counter must never be able to take the fallback down with it, and a separate
`<script>` is a parser boundary — the worst that block can do is not run.

Not after the scene either: the answer decides whether the café opens at all, and
the scene paints its first frame as soon as `three.min.js` has parsed. Firing
from where it is starts the request while those 600 kB are still on the wire, so
the answer normally lands while the welcome card is still up.

The scene reads it through a shim,
`const PING = window.VCPing || {tap(){}, whenClosed(){}, focus(){}}`, so a café
whose ping block never ran is simply an uncounted café. Add a method to `VCPing`
and it goes in the shim too, or the fallback path throws where the real one works.

### The CORS contract — the fragile part

The café and the switch are on different origins, so the whole feature rests on
one grant, set on one route in `jarvis/backend/src/routes/vc.ts`:

```
Access-Control-Allow-Origin: https://ndashiz.be
Vary: Origin
Cross-Origin-Resource-Policy: cross-origin
(and Access-Control-Allow-Credentials explicitly REMOVED)
```

Three things about it are easy to get wrong, and each was verified against the
running server rather than assumed:

**It must stay a CORS *simple request*** — a `GET` with no custom header. A
preflight from `ndashiz.be` is answered by Jarvis's global `cors()` before any
route is reached, and comes back *without* an `Allow-Origin`, so a preflight can
never be made to work here. Change the ping to a `POST`, or add a
`Content-Type`, and the switch dies **silently and permanently**: everything
fails open, so nothing on either side reports it. `deploy-virtualcoffee.sh`
greps for both mistakes. It is also why every field above travels in the query
string, however unfashionable that looks.

**Do not add `ndashiz.be` to `ALLOWED_ORIGINS`.** It is the obvious-looking
shortcut and it is the dangerous one: the global `cors()` applies
`credentials: true` to every allowlisted origin on *every* route, which would
hand any page on that host — including LazyPO's deliberately ungated
`/pro/quiz.html` — credentialed access to all the owner-gated Jarvis APIs with
the session cookie.

**`Access-Control-Allow-Credentials` must be absent.** The global `cors()` emits
it on every response, including ones it grants no origin to. Next to our own
`Allow-Origin` it would turn this public route into a credentialed cross-origin
grant, so the route strips it explicitly. There is a test asserting the header is
*not* there.

### Privacy

A small audience log on Simon's own server, and nothing else: when a visit
started, roughly how long it lasted, which sections and which things on the walls
were opened, the referrer bucketed into one of five words, and a campaign tag if
the link carried one. No cookie, no third party, no analytics product, and
`access_log off` on the `location /api/vc/` block in
`jarvis/deploy/nginx-jarvis-root.conf` — with no HTTP logger in the Jarvis backend
either, so **no IP address is written down anywhere**. nginx is also told not to
forward `X-Real-IP` / `X-Forwarded-For` to the backend: it has no use for them.

That one nginx line is load-bearing for a public promise. If the vhost is ever
replaced without it, the sentence printed on the CV becomes false.

`document.referrer` is bucketed *in the browser*, before anything leaves the page.
The URL itself never travels — the useful fact is "LinkedIn", not which post.

Per-visit lines are deleted after 30 days, daily totals after 90.

If the browser sends **Global Privacy Control** or **Do Not Track**, none of it
happens: the visit is counted once and the request carries `e=open` and nothing
else — no grouping key, no language, no referrer, no timing, no tag, and no
further ping for anything they click. There are no heartbeats at all.

**The note printed on the CV is the contract, not this file.** It is in
`index.html`, in both languages, and it says all of the above in the second
person. When the code and that note disagree, the note is what a visitor read —
so the code is what has to move. A privacy claim nobody can read is decoration;
one that has quietly stopped being true is worse.

## When the bar is closed

Simon can shut the café from the Jarvis UI. The closed state is theatre, and it
reuses the room rather than adding to it: the people are gone (walkers, barista,
the sitter, the reader — and Simon, his coffee, his croissant and his sheet of
paper), two of the three pendants are out and the third burns low over the
counter, the key light and the daylight shafts are off, the window has gone
night-blue and the fog is tighter. The chairs, tables and plants stay exactly
where they were — that is what makes it read as *closed* rather than as
*unfinished*. Since the design pass the room's bounce light is its environment
map, so closing also swaps in a night one (`buildEnvironment(true)`), turns
the baked light maps down to a night light and lights the street lamps; the
drinks fridge stays lit, as fridges do.

The menu board is the same board, repainted: `drawMenu()` branches on
`cafeClosed` and draws **CLOSED** instead of the menu. It is the board a real
café flips at closing time, so the closed state costs no new asset.

Three rules held it together, and they are easy to break by accident:

- **Closing the bar never hides the text resume.** The CV is the point of the
  page. The pill stays, the panel stays, and the closed card's only button goes
  straight to it. `VC.textOnly()` looks like the obvious tool and is the wrong
  one — it *hides* the pill and force-opens the panel, which is the no-WebGL
  path, not this one.
- **All closed copy lives in `DATA.en.closed` and `HOWTO.en.closed`**, beside
  the open copy — `closeCafe()` repaints the sign, the prompt, the menu board
  and the how-to card from those objects.
- **Reusing `#howto` as the closed card means undoing both of its hiding
  places.** The enter handler adds `.hide` *and* sets `display:none` on a 450 ms
  timer; clearing one and not the other leaves a card that is present and
  invisible.

`prefers-reduced-motion` is respected here as everywhere else: the one remaining
lamp breathes very slightly, and holds perfectly steady when motion is reduced.

### Trying the closed café locally

The ping is an absolute url, so a static stub in the page's own folder no longer
intercepts it, and from `localhost` the real endpoint is CORS-refused anyway.
Two ways to see the closed room:

**Override the response in devtools.** Network tab → right-click the `ping`
request → *Override content*, return `{"open":false}`, reload. Nothing to edit,
nothing to revert.

**Or point the ping at a local file**, temporarily, in `index.html`:

```bash
printf '{"open":false}' > /tmp/ping.json && npx serve -l 4321 . & npx serve -l 4322 /tmp
```

…then change the fetch url to `http://localhost:4322/ping.json` and reload.

**Revert it before committing.** `deploy-virtualcoffee.sh` greps for the real
host precisely because a stray local url would kill the switch in production
without a single visible symptom — everything fails open, so nothing complains.

## The parts that are not obvious

### Everything is vendored — never add a CDN tag

three.js and the three webfonts are committed to the repo. The prototype loaded
both from `cdnjs` and `fonts.googleapis.com`; they were pulled in-repo for three
reasons: no visitor IP handed to a third party from an EU personal site, no
outage in someone else's CDN taking the page down, and — the practical one —
**the fonts are painted into `<canvas>` textures**, so their arrival has to be
deterministic (see below).

### Fonts must be loaded *before* the textures are baked

The resume sheet and the menu board are `CanvasTexture`s drawn with
`ctx.fillText`. A canvas draw does not wait for a webfont: it silently bakes
whatever face is available and never repaints. `document.fonts.ready` is not
enough either — it resolves when nothing is *pending*, and a face used only
inside a canvas is never requested at all.

So `VC.fontsReady` explicitly `document.fonts.load()`s every face the textures
use, and the scene repaints both textures once it settles.

### `VC` is deliberately outside the 3D script

`index.html` has three scripts. The first builds `window.VC` — the text resume
panel and the WebGL probe. The second is
[the ping](#where-the-ping-lives-and-why-it-is-its-own-script). The third is
the café.

The split exists because **the shell has to survive the scene failing**. No
WebGL, a blocklisted driver, a dead GPU process, `three.min.js` not loading —
in every one of those cases the text resume becomes the whole page, and its
open/close pill still has to work. If it lived in the scene's script it would
die with it.

The scene bails out early:

```js
if(!VC.hasWebGL) return;                 // VC already swapped in the text resume
if(typeof THREE==="undefined"){ VC.textOnly("three.js failed to load"); return; }
```

which is the only reason that script is wrapped in an IIFE. Its body keeps the
prototype's flat indentation on purpose, so the diff against the original stays
readable.

### The text resume is not a fallback, it is the second half of the site

It is what a screen reader reads, what a keyboard user gets, what a crawler
indexes, and what a visitor without WebGL sees. It ships as **static markup**
rather than being generated from the `DATA` object, so a bot that never runs
the 3D still reads the whole CV.

The cost is two copies of the content. **When the CV changes, update both** —
`DATA` (drawn on the 3D sheet, and spoken) and the static block in `#cv-text`.

### Stacking order

`overlays 12 · sign 20 · prompt 20 · dialogue box 23 · subtitles 24 · skip 25 ·
how-to 50 · text resume 60 · tools 70`

The tools cluster is on top of everything on purpose: the resume pill has to be
reachable from inside the text resume and from the welcome card, both of which
cover the screen.

### The speech bubble is clamped, not free-floating

It is pinned over Simon's head by projecting a 3D point each frame, anchored
`translate(-50%,-100%)`. The longest answer is taller than the gap between his
head and the top of the window, so the position is clamped to the viewport and
the café sign fades out while a bubble is up.

## The jukebox — silent disco

On the front wall, between the press frames and the plant, stands a jukebox.
It is a room object like the plaque and the televisions — same hint bubble,
same tap — but what opens is a player, not a picture: pick a track and it
hands out **wireless headsets**. Your character puts one on, five regulars
put down what they were doing, walk over one by one, take a headset off the
rail as they arrive, and dance **to the actual audio** — a per-frame RMS
drives head, shoulders, hips and knees, each dancer on an individual phase,
rate and amplitude so the five are visibly together and never in sync. The
barista never leaves the bar, and the reader never looks up from her book,
because in every real café one person ignores the party.

The framing — headsets everywhere, one transmitter — is what keeps the
audio honest. The gain chain is

```
elements → track gains (crossfade) → analyser → distance → duck → volume → mute → out
```

with the analyser tapped **upstream** of every gain: the crowd dances to the
track itself, not to how loud you currently hear it, so walking away, muting
or ducking never stops the dance. Distance is camera → transmitter: full
inside 3 m, floored at 25 % past 12 m — the signal weakens, it never cuts,
and the dancers stay at the box rather than following you. Any voice clip —
mp3 or browser-voice fallback — ducks the music to 20 % in ~300 ms and
releases half a second after the line ends: when Simon starts talking over
running music, Simon wins. The other direction is not a duck but a cut:
**pressing play while he is mid-sentence stops him**, exactly like the skip
pill, because the click is the visitor's answer and two voices sharing one
pair of ears is not deference. Only real gestures do it — the auto-advance
at the end of a track never silences a narration it happens to overlap. The
music mute is its own pill in the HUD (the note), separate from Simon's;
each silences only its own graph.

**Sitting down at the table ends the party — all of it.** The table is where
Simon talks, and the voice does not share the room, so arriving at the seat
with the headset on runs the very exit the eject pill runs: every headset
off, the five walk home to positions and orientations recorded once at
scene init (`JB_HOME`, never recomputed — recomputing is how positions
drift across cycles; mid-arrival dancers turn around from wherever they
are), the music fades out — never cuts — and every gain returns to nominal.
The panel exit and the HUD eject pill still work from anywhere. The user
volume survives in `localStorage` (`vc:musicVol`). This overrides US-10,
which kept the music running in the headset at the seated level.

The jukebox plays **four tracks, all Simon's own songs**, supplied as
finished masters and his to publish: *Balance Sheet Heart*, *The Verdict
Is The Prod*, *Arbitrage* and *It's the PO*. They took the slot the README
predicted — "adding a real track later is one file under `audio/music/`
plus one line in the `MUSIC` map" — and the three `preprocess_music.py`
renders (disco, funk, lo-fi in a few hundred lines of numpy at −14 LUFS)
left to make room. The script stays as their source, and git keeps the
files. Every `bpm` in the map was measured from the audio, never assumed,
because the dancers' groove clock reads it and a wrong guess is visible on
five bodies at once; when the onset grid and the accent structure disagree
by an octave, the crowd dances the felt beat (Balance Sheet Heart: eighths
at 152, felt 76; It's the PO: a flat 172 grid, danced at its half).

**And you can see that it plays**: a CD sits in the jukebox's glass dome
and spins while a track is on air — asymmetric glints on purpose, a
perfectly radial disc would rotate invisibly — winding down on pause
instead of freezing. The panel's now-playing row carries the same disc in
CSS, animated by the same `playing` state. While a track is on air the
three counter pendants trade their warm white for **nightclub gels** —
three hue wheels a third of a turn apart, intensity riding the track's
real level, the warm café points ducking to a third so the colour owns
the room, the opal globes themselves taking the gel, and the trophy
cabinet's LED strips plus three wall washes over the press frames running
the same wheel half a turn out of phase (the strips are the only meshes
left on the shared bulb material, kept apart from the pendants' SPECIAL
clones — tint one, touch nothing else) — and the crowd dances on spots spread so **no two dancers can
ever touch**, looking at **you** three glances out of four. The HUD's way
out is a labelled button — "⏏ Stop the music" — because a bare headset
glyph made people guess.
`window.__jukebox()` dumps the whole state — mode, gains, per-dancer phase —
next to `__agents()` and `__guest()`.

## Voice

One key = one clip = one mp3, and the same key is the counter event:

```
welcome · seated · reclick
experience_open_a · experience_open_b · experience_body
education · skills · certifications · languages
personal · ai · banking · howibuilt · outro
```

`DATA.en.speech[key]` holds the words and `AUDIO.en[key]` the file. The text is
the recording script, the subtitle track and the browser-voice fallback all at
once, so **it must match the mp3 word for word** — change one, re-record the
other.

A missing file falls back to TTS, and so does one that fails to load
(`audioEl.onerror`), so the café is complete and speakable before a single clip
is recorded. Drop `audio/en/<key>.mp3` in and that key stops falling back, with
nothing else to change.

The **v1 recordings are parked in `audio/en/v1/`** rather than deleted. They
carry the older, shorter scripts under the same filenames: left where they
were, they would have played underneath v2 subtitles.

A section is one clip or several. `sectionClips()` owns that: work experience
returns `experience_open_b` (if education has already been heard) or
`experience_open_a`, then `experience_body`, and a repeat gets `reclick` in
front. Only a clip that reaches its **own** end advances the chain — hush him
and the section stays unheard, because the green marker promises you heard the
whole thing.

### Mute

The speaker pill — the only one left in the tools bar — or the `M` key cuts the
voice, and the choice is remembered in `localStorage["vc:muted"]`: sound off is
a first-class way to read this page, not a failure state.

It is **not** `audioEl.muted`. The lipsync drives Simon's jaw from the real
audio amplitude through an `AnalyserNode`, so cutting the element would freeze
his mouth mid-sentence and make the café look broken. Instead a single master
`GainNode` sits **after** the analyser: muted, the analyser still sees the full
signal, so he keeps talking and the subtitles keep running — you just cannot
hear him. The element is only muted directly in the fallback where
`createMediaElementSource` threw and there is no graph at all (`audioRouted`),
and the TTS path sets `utterance.volume` so `onend` still paces the captions.

### Subtitles

Spoken sections are captioned, GTA-style: white text, no box, hard shadow,
bottom-centred. The mp3s carry no cue track, so sentences are spread pro-rata
by character count over `audioEl.duration` (±0.4 s — fine for captions); the
TTS fallback captions per uttered sentence. That closes the gap the recordings
had opened for anyone with sound off or hard of hearing — the **text resume**
remains the full readable version, and carries the "Off the clock" content too.

## Credits

- Scanned surfaces (`tex/scan/`), all **CC0**: oak veneer 02, black walnut
  veneer 02, brown leather and white plaster 02 from
  [Poly Haven](https://polyhaven.com); Travertine 009 from
  [ambientCG](https://ambientcg.com). Prepared by `tex/scan/prep_scans.py`.

three.js — MIT. Space Grotesk, Inter, Caveat — SIL Open Font License 1.1.
