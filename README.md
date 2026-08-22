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
down when he finishes, or the moment you click beside it — no one is made to
sit through the monologue — and the **dialogue box** opens down the left: five
sections — work experience, education, skills, certifications, languages —
each of which Simon talks you through out loud while he looks you in the eye —
his words, read by a voice model (see "Voice"). A section you have heard right through keeps a green
marker; ask for it again and he says so before repeating himself. Work
experience has two openings and picks the one that fits what you have already
heard. Once all five are done a **second tier** opens — off the clock, AI long
term, why banking, how I built this — along with the wrap-up. The box carries
a permanent **See the resume / Download it** row from its first option (seeing
the sheet again or keeping it must never be more than one tap away); the outro
adds the LinkedIn link and ends the visit. When Simon finishes that outro the
barista comes over, says they're closing, and the room empties around you.

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
cafe.obj.txt        The café itself — real 3D model, ~95k tris (5.1 MB, ~980 KB gzipped)
tex/*.png           13 baked label maps — trophy cabinet, diplomas, van (~376 KB)
person.obj          Male NPC body — base mesh cut into 15 rig segments (~550 KB)
fonts.css           @font-face for the three self-hosted families
fonts/*.woff2       Space Grotesk · Inter · Caveat (latin + latin-ext)
three.min.js        three.js r134, vendored
audio/en/*.mp3      The narration, one file per clip (see "Voice")
audio/en/v1/*.mp3   The retired v1 recordings — kept, never loaded
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

One public endpoint, called once on load:

```
GET  https://jarvis.ndashiz.be/api/vc/ping?e=<event>&l=<lang>&r=<ref>
→    200  {"open": true}          Cache-Control: no-store
                                  Access-Control-Allow-Origin: https://ndashiz.be
                                  Vary: Origin
```

Absolute, and **cross-origin**: the café is on GitHub Pages, the switch is on the
VPS. The grant is scoped to this one route — see "The CORS contract" below, which
is the part of this feature most likely to be broken by a well-meaning edit.

Everything it can carry is a closed enum, validated again server-side, and
anything else is dropped on the floor:

| Param | Values |
|---|---|
| `e` | `open` `enter` `cv` `experience` `education` `skills` `certifications` `languages` `personal` `ai` `banking` `howibuilt` `outro` |
| `l` | `en` `fr` |
| `r` | `linkedin` `github` `google` `direct` `other` |

There is **no free-text field anywhere**, on purpose: this endpoint is reachable
by anyone on the internet with no session, and the hard bound on what it can
write is what makes that safe. It also never returns 4xx or 5xx — a malformed
query is answered 200 with the switch, because the café must not be able to
break itself.

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

Only the **load** ping honours the answer. The pings sent when you sit down, open
a section or open the text resume deliberately ignore it: a visitor already
seated is not thrown out because Simon flipped the sign mid-sentence.

### Where the ping lives, and why it is its own `<script>`

`index.html` now has three script blocks: the `VC` shell, **the ping**, then the
café. The ping sits between the other two on purpose.

Not inside the shell: a syntax error anywhere in that IIFE leaves `window.VC`
undefined, and `VC` is what swaps in the text resume when the 3D fails. A visit
counter must never be able to take the fallback down with it, and a separate
`<script>` is a parser boundary — the worst that block can do is not run.

Not after the scene either: the answer decides whether the café opens at all,
and the scene paints its first frame as soon as `three.min.js` has parsed.
Firing from where it is starts the request while those 600 kB are still on the
wire, so the answer normally lands while the welcome card is still up.

The scene reads it through a shim, `const PING = window.VCPing || {tap(){}, whenClosed(){}}`,
so a café whose ping block never ran is simply an uncounted café.

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
greps for both mistakes.

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

Counters, on Simon's own server, and nothing else. No cookie, no third party, no
analytics product, and `access_log off` on the `location /api/vc/` block in
`jarvis/deploy/nginx-jarvis-root.conf` — with no HTTP logger in the Jarvis backend
either, so **no IP address is written down anywhere**. nginx is also told not to
forward `X-Real-IP` / `X-Forwarded-For` to the backend: it has no use for them.

That one nginx line is load-bearing for a public promise. If the vhost is ever
replaced without it, the sentence printed on the CV becomes false.

`document.referrer` is bucketed into one of five words *in the browser*, before
anything leaves the page. The URL itself never travels — the useful fact is
"LinkedIn", not which post.

If the browser sends **Global Privacy Control** or **Do Not Track**, the page
still asks the switch — a visitor has to be told the bar is closed either way,
and that answer is a fact about Simon, not about them — but the request then
carries `e=open` and nothing else: no language, no referrer, and no further ping
for anything they click. The same sentence is in the text resume itself, in both
languages, because a privacy note nobody can read is decoration.

## When the bar is closed

Simon can shut the café from the Jarvis UI. The closed state is theatre, and it
reuses the room rather than adding to it: the people are gone (walkers, barista,
the sitter, the reader — and Simon, his coffee, his croissant and his sheet of
paper), two of the three pendants are out and the third burns low over the
counter, the key light and the daylight shafts are off, the window has gone
night-blue, the fog is tighter, and the dust keeps drifting through the dark as
the only thing still moving. The chairs, tables, rug and plants stay exactly
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

The pill next to "Text resume" (or the `M` key) cuts the voice, and the choice
is remembered in `localStorage["vc:muted"]` — sound off is a first-class way to
read this page, not a failure state.

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
