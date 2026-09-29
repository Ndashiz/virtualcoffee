# film/ — the trailer and the share image

The café filmed as it runs: the real WebGL scene, captured frame by frame at a
fixed time step (no screen recording, so no dropped frames whatever the GPU),
then cut, titled and scored in Blender. Nothing here runs on the page.

| File | What it does |
|---|---|
| `film.js` | Serves the repo, loads the page in chrome-headless-shell (the one in the Playwright cache, driven over the DevTools protocol), takes over `requestAnimationFrame` and the clock (`1/fps` per frame), flies the camera along `path.json` (Catmull-Rom through keys, one list per shot — a new shot is a cut) and writes one PNG per frame. |
| `path.json` | The trailer: a slow dolly along the pavement (bikes, A-board, the storefront), a cut inside, the room from the door to Simon's table, a hold. |
| `sound.js` | The score, as a `PROBE=` script for `gi/tools/cdp.js`: the page's own `ambBuild` rendered in an `OfflineAudioContext` — the street outside, the bell at the cut, the walla, grinder, knocks, pump, cups — to a WAV (`DUMP_DIR`). |
| `title.html` | The end card, rendered transparent by Chrome (`--default-background-color=00000000`). |
| `assemble.py` | Blender 4.5: image sequence + WAV + end card faded in, H.264/AAC MP4, Standard view transform (AgX would re-grade the frames). |

```bash
node film/film.js film/path.json          # env: OUT=frames SEAT=1 W=1920 H=1080 WARM=30000 (~35 min on an M4, SwiftShader)
VC_ROOT=$PWD EXPOSE=ambBuild PROBE=film/sound.js DUMP_DIR=/tmp/film node gi/tools/cdp.js /dev/null
chrome-headless-shell --headless --default-background-color=00000000 --allow-file-access-from-files \
  --window-size=1920,1080 --screenshot=/tmp/film/title.png file://$PWD/film/title.html
/Applications/Blender.app/Contents/MacOS/Blender -b --python film/assemble.py -- frames /tmp/film/trailer_sound.wav /tmp/film/title.png trailer.mp4
```

The MP4 is not committed (it is for LinkedIn, not for the page). `og.jpg` is
the interview shot rendered at 2400×1260 by `gi/tools/cdp.js` and titled
the same way; its URL carries `?v=` so link previews refresh.
