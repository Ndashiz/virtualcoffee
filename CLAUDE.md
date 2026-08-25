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
3. **Write the numbers into the commit.** "It looks fine" is how the waiter
   shipped walking through a customer.

Two mechanisms keep bodies apart, and they are not interchangeable:

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
