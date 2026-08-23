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
tap away, and leaving is not quitting — stand up mid-visit (the sit-down blend,
run backwards), wander the room, and the moment you take the chair again the
box reopens exactly as you left it, green markers, tier and all. The outro
adds the LinkedIn link and ends the visit. When Simon finishes that outro the
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
person.obj          Male NPC body — base mesh cut into 15 rig segments (~550 KB)
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
produces. Faces merge into one mesh per material (~55 draw calls); materials
are assigned by the model's French `usemtl` names (`chene_sol`, `laiton`,
`marbre`, …) and dressed with the same procedural canvas textures as before —
the chalkboard still repaints through `drawMenu()`, closed side included. If
the fetch fails, the room is gone but the table, Simon and the resume are all
procedural: the conversation survives on a bare parquet.

The map also carries what the room could never show before: a **front wall**
with Simon's trophy cabinet (PSPO, PSM I, Dynamics 365, Azure, the Solvay
diploma, Le Wagon), and a **real outside** — a parking lot with a van and a
car, and a treeline — visible through the storefront. The trophy labels ship as
baked PNG under `tex/` because they carry awarded titles and vendor marks;
everything else stays procedural.

The map's three framed press clippings are **dropped** in the preprocessor
(`DROP_NAMES`), and the pair `drawPress()` used to paint on the back wall went
with them: a café papered with invented headlines about its own owner reads as
bragging. What hangs on that wall now is one small plaque — *Employee of the
Month*, awarded to a man nobody in the room has ever met — painted by
`drawEotm()`, and, back by popular demand under the three sconces, three
frames of **The Daily Salfari** (`drawArticle()`): the building he rebuilt
alone, the first triathlon, the one-man web-and-AI studio. The rule was never
"no press" — it was "no invented press", and those three actually happened.
Like the plaque they are registered readables: walk up and they open full
size, article legible, ink illustration and all. The preprocessor also squares up the eight wheels (the export
mounts them sideways), copies the ICE CUBE lettering onto the van's rear doors,
moves the plant off the one run of wall a toilet door fits on, and clones the
van one parking bay over for a second firm — BravoReno the electrician, whose
livery the scene paints (`drawBravo()`).

**The van has a driver now.** On a slow loop (~50 s, most of it spent with
the tailgate shut so the lettering stays a readable poster), the ICE CUBE
courier appears from behind the cab, swings the two rear leaves open — they
are real doors now, split on the ICE|CUBE seam, each carrying its half of the
decal — takes two printed bags of ice off the sill, and carries them across
the lot, down the kerb and along the whole glazed shopfront, dead lateral to
the room, before vanishing past the front-wall corner (the service door is
implied off-frame: in this set the front door opens into the shot, so nobody
delivers through it). The return trip is the tell that sells it: hands free,
arms swinging in opposition, longer stride, +18% pace, chin up — against the
loaded walk out, leaned back, arms pinned dead straight, short heavy steps,
eyes on the pavement. He pauses half a second at the van before shoving both
leaves shut, then walks back around the nose to the cab. Behind the doors the
scene builds the cargo bay the model never had (the closed box's own rear
face is stripped at load): dark walls, a pale alu deck, a part-worked pallet,
and one 6500 K strip across the head of the opening — the only cold light in
a warm scene, which is what reads as refrigeration. One mark, three supports:
the same canvas letters his shirt (chest and back, straddling the torso
cylinder's UV seam) and the bags, while the van keeps its baked PNG.

**Two televisions, one feed** — HENRY TV, sound off: six stories on an
eight-second loop (a 48-second "video", which is what the player's scrub bar
actually measures), a presenter whose mouth moves, and a ticker carrying only
real quotes. Three stories run a graph; three run a picture instead — the EU
ring of stars for the AMLR file, a keyword card for tonight's programme, and a
chief executive at a lectern for the fine.

Walk up to a screen or the plaque and a bubble says it opens; click and
`openZoom()` re-runs the painter at 2× into a full-screen canvas rather than
blowing up the wall texture, so the ticker is legible — a second of "connecting
to the live", then the picture, a progress bar and the current story. One big
arrow sends it back.

`person.obj` is currently **retired** (`USE_PERSON_MESH=false` in the scene):
the segmented base-mesh bodies read as ragged mannequins next to the capsule
cast, so the capsule people are the look again — consistent with Simon, who
was always bespoke. The whole swap pipeline is still in the file and the asset
still ships, for a future better-cut mesh: it is a decimated base mesh cut
offline into fifteen segments, each exported **in the local space of the rig
joint that carries it**, so the swap is just "remove the cylinder under this
joint, add this mesh under the same joint" and every behaviour written for the
capsules (gaze, turn-taking, sip, walk, `reskin()`) drives either body
untouched. Flip the flag to try again.

Being the look again, the capsules got the pass they had been owed: **hands
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
night-blue and the fog is tighter. The chairs, tables, rug and plants stay exactly
where they were — that is what makes it read as *closed* rather than as
*unfinished*.

The chalkboard is the same slate, repainted: `drawMenu()` branches on
`cafeClosed` and draws **CLOSED / FERMÉ** instead of *La Carte*. It is the board
a real café flips at closing time, so the closed state costs no new asset.

Three rules held it together, and they are easy to break by accident:

- **Closing the bar never hides the text resume.** The CV is the point of the
  page. The pill stays, the panel stays, and the closed card's only button goes
  straight to it. `VC.textOnly()` looks like the obvious tool and is the wrong
  one — it *hides* the pill and force-opens the panel, which is the no-WebGL
  path, not this one.
- **All closed copy lives in `DATA.en.closed` and `HOWTO.en.closed`**, beside
  the open copy — `closeCafe()` repaints the sign, the prompt, the chalkboard
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

The resume sheet and the chalkboard menu are `CanvasTexture`s drawn with
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
the room, and the three wall sconces over the diploma wall running the
same wheel half a turn out of phase (their bulbs share one material,
kept apart from the pendants' SPECIAL clones — tint one, touch nothing
else) — and the crowd dances on spots spread so **no two dancers can
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

three.js — MIT. Space Grotesk, Inter, Caveat — SIL Open Font License 1.1.
