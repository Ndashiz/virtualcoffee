# Virtual Coffee

An interactive 3D résumé. You sit across a café table from Simon, his CV is
lying on the table, and tapping a section makes him tell you about it out loud —
in his own recorded voice. Tap Simon himself and he orders a round of beers for
the off-the-record version. Bilingual EN / FR.

**Live** : <https://ndashiz.be/virtualcoffee/>

## How it is served

The café **used to be** a GitHub Pages project site. It is not any more: the
**VPS** serves it now, at the same URL. That move is what makes the switch below
possible — Simon needs to be able to close the bar, and Pages has no backend.

```
git push                            →  GitHub                (source of truth)
ssh vps, deploy-virtualcoffee.sh    →  /var/www/virtualcoffee/
Cloudflare  ndashiz.be/virtualcoffee*  ──→  the VPS           (Origin Rule — see below)
```

Three pieces, three owners:

| Piece | Lives at | Put there by |
|---|---|---|
| The static site | `/var/www/virtualcoffee/` | `jarvis/deploy/deploy-virtualcoffee.sh` |
| The nginx vhost | `/etc/nginx/sites-enabled/virtualcoffee` | `jarvis/deploy/nginx-virtualcoffee.conf`, copied by hand |
| The API | Jarvis backend, `127.0.0.1:3007`, route `/api/vc/ping` | `jarvis/deploy/deploy.sh` |

nginx maps `/virtualcoffee/api/` onto `/api/vc/`, so the page reaches its API as
the **relative** url `api/ping`. Static site and API therefore share one origin
*and* one path prefix: **there is no CORS in this feature**, nothing to add to
an allowlist, and the same line of client code works in local dev and in prod.

### The Cloudflare step — Simon's job, not the deploy script's

`ndashiz.be` is a Cloudflare-proxied domain whose origin is still GitHub Pages.
Copying the files onto the VPS changes **nothing** for the public until
Cloudflare is told to send `/virtualcoffee*` there. Two ways to do that:

**Option A — an Origin Rule in the dashboard. Recommended.**

1. **DNS** → add `vps` · `A` · *the VPS IP* · proxy status **DNS only** (grey
   cloud). This record exists only to be the rule's target; proxying it would
   put the traffic through Cloudflare twice.
2. **Rules → Origin Rules → Create rule**, name it `virtualcoffee → VPS`.
   Custom expression:
   ```
   (http.host eq "ndashiz.be" and starts_with(http.request.uri.path, "/virtualcoffee"))
   ```
   Action: **DNS Record → Rewrite to → `vps.ndashiz.be`**. Leave the Host header
   and the SNI alone, so the origin still sees `ndashiz.be` and the vhost in
   `nginx-virtualcoffee.conf` matches.
3. **SSL/TLS** must be **Full** or **Full (strict)**. Install a Cloudflare
   **Origin Certificate** for `ndashiz.be` on the VPS — *not* certbot. certbot's
   HTTP-01 challenge is served from `/.well-known/acme-challenge/`, which this
   rule does **not** route to the VPS, so it cannot succeed; the Origin
   Certificate is issued from the dashboard with no challenge at all and lasts
   15 years.
4. **Caching → Purge** the `/virtualcoffee/` prefix once. Cloudflare is holding
   the old Pages copy and will keep serving it otherwise.

**Option B — a Worker route.** Add the route `ndashiz.be/virtualcoffee*` to a
Worker that re-fetches `https://vps.ndashiz.be` + path. It works, and it is the
wrong tool here: a Worker only ships via `wrangler deploy` (pushing to `main`
deploys nothing), it puts a JS hop in front of every mp3 and every ping, and the
only Worker on this zone today is the LazyPO auth gate on `ndashiz.be/pro/*` —
routing a public résumé through an auth gate and a CSP that has already broken
production twice is a trade with no upside. Keep them apart.

**If neither is done**, nothing looks broken, which is the trap. The public keeps
getting the GitHub Pages copy; `api/ping` resolves to a Pages 404, the response
is not JSON, and — by design — **the café stays open**. What is silently lost:
the switch does nothing, the Jarvis dashboard counts zero visitors, and the copy
in `/var/www/` quietly drifts away from the one people actually see.

### Still true after the move

- **The LazyPO Cloudflare Worker does not apply here.** Its route is
  `ndashiz.be/pro/*`, so `/virtualcoffee/` gets no auth gate, no CSP and none of
  its security headers. Nothing on this page needs them.
- **`robots.txt` cannot live in this repo.** Crawlers only read
  `ndashiz.be/robots.txt`, still served by `Ndashiz/ndashiz.github.io` — the
  Origin Rule only diverts `/virtualcoffee*`. Same for a sitemap entry.

## Layout

```
index.html          Everything: markup, CSS, the VC shell, the 3D café
fonts.css           @font-face for the three self-hosted families
fonts/*.woff2       Space Grotesk · Inter · Caveat (latin + latin-ext)
three.min.js        three.js r134, vendored
audio/en/*.mp3      Simon's recorded voice, one file per section (~4.6 MB)
og.jpg              1200×630 share card, rendered from the scene itself
favicon.svg
.nojekyll           skip the Jekyll build on Pages
```

No build step, no bundler, no dependencies to install. Open `index.html` or:

```bash
npx serve -l 4321 .
```

There is no API in front of that, so the ping 404s, the café stays open, and
nothing in the console says otherwise — which is exactly the production
behaviour when the backend is down. That is the point, not a gap.

## The switch — "is the bar open?"

One public endpoint, called once on load:

```
GET  api/ping?e=<event>&l=<lang>&r=<ref>
→    200  {"open": true}          Cache-Control: no-store
```

Relative url, always. `api/ping` resolves against `/virtualcoffee/`, so it hits
the VPS in production and the local server in dev with no build-time
substitution and no environment variable.

Everything it can carry is a closed enum, validated again server-side, and
anything else is dropped on the floor:

| Param | Values |
|---|---|
| `e` | `open` `enter` `cv` `intro` `experience` `education` `skills` `certifications` `languages` `contact` `outro` `about` |
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
Cloudflare not routed yet — leaves the café **open**. A résumé that disappears
because a server hiccuped is worse than one that stays open when it was meant to
be shut.

Only the **load** ping honours the answer. The pings sent when you sit down, open
a section or open the text résumé deliberately ignore it: a visitor already
seated is not thrown out because Simon flipped the sign mid-sentence.

### Where the ping lives, and why it is its own `<script>`

`index.html` now has three script blocks: the `VC` shell, **the ping**, then the
café. The ping sits between the other two on purpose.

Not inside the shell: a syntax error anywhere in that IIFE leaves `window.VC`
undefined, and `VC` is what swaps in the text résumé when the 3D fails. A visit
counter must never be able to take the fallback down with it, and a separate
`<script>` is a parser boundary — the worst that block can do is not run.

Not after the scene either: the answer decides whether the café opens at all,
and the scene paints its first frame as soon as `three.min.js` has parsed.
Firing from where it is starts the request while those 600 kB are still on the
wire, so the answer normally lands while the welcome card is still up.

The scene reads it through a shim, `const PING = window.VCPing || {tap(){}, whenClosed(){}}`,
so a café whose ping block never ran is simply an uncounted café.

### Privacy

Counters, on Simon's own server, and nothing else. No cookie, no third party, no
analytics product, and `access_log off` on the API location in
`nginx-virtualcoffee.conf` — with no HTTP logger in the Jarvis backend either, so
**no IP address is written down anywhere**. nginx is also told not to forward
`X-Real-IP` / `X-Forwarded-For` to the backend: it has no use for them.

`document.referrer` is bucketed into one of five words *in the browser*, before
anything leaves the page. The URL itself never travels — the useful fact is
"LinkedIn", not which post.

If the browser sends **Global Privacy Control** or **Do Not Track**, the page
still asks the switch — a visitor has to be told the bar is closed either way,
and that answer is a fact about Simon, not about them — but the request then
carries `e=open` and nothing else: no language, no referrer, and no further ping
for anything they click. The same sentence is in the text résumé itself, in both
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

- **Closing the bar never hides the text résumé.** The CV is the point of the
  page. The pill stays, the panel stays, and the closed card's only button goes
  straight to it. `VC.textOnly()` looks like the obvious tool and is the wrong
  one — it *hides* the pill and force-opens the panel, which is the no-WebGL
  path, not this one.
- **All closed copy lives in `DATA[lang].closed` and `HOWTO[lang].closed`.**
  `applyLang()` repaints the sign, the prompt, the chalkboard and the how-to card
  from those objects on every EN↔FR click. Text written straight into the DOM
  survives exactly until someone taps FR, and then silently reverts.
- **Reusing `#howto` as the closed card means undoing both of its hiding
  places.** The enter handler adds `.hide` *and* sets `display:none` on a 450 ms
  timer; clearing one and not the other leaves a card that is present and
  invisible.

`prefers-reduced-motion` is respected here as everywhere else: the one remaining
lamp breathes very slightly, and holds perfectly steady when motion is reduced.

### Trying the closed café locally

No backend needed — stub the endpoint as a static file:

```bash
mkdir -p api && printf '{"open":false}' > api/ping
npx serve -l 4321 .
```

`fetch(...).json()` does not care about the content type, so the page reads it as
the real answer and closes the bar. Delete `api/` to reopen it; it is
`.gitignore`d so it can never be deployed by accident.

## The parts that are not obvious

### Everything is vendored — never add a CDN tag

three.js and the three webfonts are committed to the repo. The prototype loaded
both from `cdnjs` and `fonts.googleapis.com`; they were pulled in-repo for three
reasons: no visitor IP handed to a third party from an EU personal site, no
outage in someone else's CDN taking the page down, and — the practical one —
**the fonts are painted into `<canvas>` textures**, so their arrival has to be
deterministic (see below).

### Fonts must be loaded *before* the textures are baked

The résumé sheet and the chalkboard menu are `CanvasTexture`s drawn with
`ctx.fillText`. A canvas draw does not wait for a webfont: it silently bakes
whatever face is available and never repaints. `document.fonts.ready` is not
enough either — it resolves when nothing is *pending*, and a face used only
inside a canvas is never requested at all.

So `VC.fontsReady` explicitly `document.fonts.load()`s every face the textures
use, and the scene repaints both textures once it settles.

### `VC` is deliberately outside the 3D script

`index.html` has three scripts. The first builds `window.VC` — the EN/FR toggle,
the `<html lang>` attribute, the text résumé panel, the WebGL probe. The second
is [the ping](#where-the-ping-lives-and-why-it-is-its-own-script). The third is
the café.

The split exists because **the shell has to survive the scene failing**. No
WebGL, a blocklisted driver, a dead GPU process, `three.min.js` not loading —
in every one of those cases the text résumé becomes the whole page, and its
language toggle still has to work. If the toggle lived in the scene's script it
would die with it.

The scene subscribes with `VC.onLang(fn)` and bails out early:

```js
if(!VC.hasWebGL) return;                 // VC already swapped in the text résumé
if(typeof THREE==="undefined"){ VC.textOnly("three.js failed to load"); return; }
```

which is the only reason that script is wrapped in an IIFE. Its body keeps the
prototype's flat indentation on purpose, so the diff against the original stays
readable.

### The text résumé is not a fallback, it is the second half of the site

It is what a screen reader reads, what a keyboard user gets, what a crawler
indexes, what a visitor without WebGL sees, and — since the recordings removed
the subtitles — the only way to *read* any of this. Both languages ship as
**static markup** rather than being generated from the `DATA` object, so a bot
that never runs the 3D still reads the whole CV.

The cost is two copies of the content. **When the CV changes, update both** —
`DATA` (drawn on the 3D sheet, and spoken) and the `[data-cvlang]` blocks.

### Stacking order

`overlays 12 · sign 20 · bubble 25 · how-to 50 · text résumé 60 · tools 70`

The tools cluster is on top of everything on purpose: the language toggle has to
be reachable from inside the text résumé and from the welcome card, both of
which cover the screen.

### The speech bubble is clamped, not free-floating

It is pinned over Simon's head by projecting a 3D point each frame, anchored
`translate(-50%,-100%)`. The longest answer is taller than the gap between his
head and the top of the window, so the position is clamped to the viewport and
the café sign fades out while a bubble is up.

## Voice

`AUDIO[lang][section]` maps a section to a recording. English is fully recorded
in Simon's own voice (`audio/en/*.mp3`); **French has no recordings yet**, so
every FR section falls back to the browser's `SpeechSynthesis`, which picks the
best available `fr-FR` voice and sounds noticeably more robotic. `skills` has no
mp3 in either language and always falls back.

To record more, drop the file in and add the key:

```js
AUDIO.fr.experience = "audio/fr/experience.mp3";
```

A missing key falls back to TTS, and so does a file that fails to load
(`audioEl.onerror`), so a broken path degrades rather than going silent.

### There are no subtitles

The recordings replaced the on-screen speech bubble the prototype used to have.
Anyone with sound off, in a quiet office, or hard of hearing now gets nothing
from the spoken sections — which is precisely why the **text résumé** matters,
and why it carries the "Off the clock" content too. It is not a full transcript
of what Simon says, though: the spoken sections are longer and more personal
than the CV. A real transcript panel is the obvious next step if that gap
matters.

## Credits

three.js — MIT. Space Grotesk, Inter, Caveat — SIL Open Font License 1.1.
