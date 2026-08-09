# Virtual Coffee

An interactive 3D résumé. You sit across a café table from Simon, his CV is
lying on the table, and tapping a section makes him tell you about it out loud.
Bilingual EN / FR.

**Live** : <https://ndashiz.be/virtualcoffee/>

## How it is served

`ndashiz.be` is a GitHub Pages custom domain owned by the **user** site repo
`Ndashiz/ndashiz.github.io`. Every other repo on the account is published as a
*project* site underneath it, at `ndashiz.be/<repo-name>/`. So this repo being
named `virtualcoffee` is what produces the URL — renaming the repo moves the
site.

```
git push  →  GitHub Pages (main, /)  →  ndashiz.be/virtualcoffee/
                                         └── ~1–2 min build, then Cloudflare cache (~10 min)
```

Two things worth knowing:

- **The LazyPO Cloudflare Worker does not apply here.** Its route is
  `ndashiz.be/pro/*`, so `/virtualcoffee/` gets no auth gate, no CSP and none of
  its security headers. Nothing on this page needs them — it is a public,
  read-only, backend-free résumé.
- **`robots.txt` cannot live in this repo.** Crawlers only read
  `ndashiz.be/robots.txt`, which is served by `Ndashiz/ndashiz.github.io`.
  Same for a sitemap entry.

## Layout

```
index.html          Everything: markup, CSS, the VC shell, the 3D café
fonts.css           @font-face for the three self-hosted families
fonts/*.woff2       Space Grotesk · Inter · Caveat (latin + latin-ext)
three.min.js        three.js r134, vendored
og.jpg              1200×630 share card, rendered from the scene itself
favicon.svg
.nojekyll           skip the Jekyll build on Pages
```

No build step, no bundler, no dependencies to install. Open `index.html` or:

```bash
npx serve -l 4321 .
```

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

`index.html` has two scripts. The first one builds `window.VC` — the EN/FR
toggle, the `<html lang>` attribute, the text résumé panel, the WebGL probe.
The second is the café.

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
indexes, and what a visitor without WebGL sees. Both languages ship as **static
markup** rather than being generated from the `DATA` object, so a bot that never
runs the 3D still reads the whole CV.

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

Speech uses the browser's `SpeechSynthesis`, picking the best available voice for
`en-GB` / `fr-FR` (preferring neural/premium/Google/Siri faces). Quality varies a
lot per OS. `AUDIO[lang][section]` is an escape hatch: point it at an mp3 and
that section plays a recording instead.

```js
AUDIO.fr.experience = "audio/exp-fr.mp3";
```

## Credits

three.js — MIT. Space Grotesk, Inter, Caveat — SIL Open Font License 1.1.
