#!/usr/bin/env python3
"""
preprocess_music.py — the jukebox's three tracks, composed in code.

Why synthesis and not licensed tracks: the site is public (LinkedIn
visitors) and the spec calls rights on the music a BLOCKING item. A track
rendered by this script has no rights question at all — the composition
and the render both live in this repo, the same way every texture in the
café is painted by its own code. Drop-in replacements are trivial later:
one file under audio/music/ + one line in the MUSIC map in index.html.

What it does:
  1. renders three originals with a small numpy DAW (no scipy, no deps
     beyond numpy: filters run in the frequency domain per note)
  2. loudness-matches them (same RMS target ≈ -14 LUFS ballpark, the
     spec's number — the point is that no track jumps out of the set)
  3. encodes M4A/AAC 128 kbps via afconvert (macOS built-in; the spec
     allows "MP3 128 kbps or M4A/AAC audio-only")
  4. prints the exact durations to copy into the MUSIC map

Run from the repo root:  python3 preprocess_music.py
Outputs:  audio/music/<key>.m4a   (WAVs go to a temp dir, never committed)
"""
import math, os, subprocess, tempfile, wave
import numpy as np

SR = 44100
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio", "music")
RMS_TARGET = 10 ** (-14 / 20)      # -14 dBFS RMS ≈ the -14 LUFS the spec asks for

rng = np.random.default_rng(20260822)   # same seed → same tracks, bit for bit

# ---------------------------------------------------------------- helpers
def hz(midi): return 440.0 * 2 ** ((midi - 69) / 12)

def fft_filter(x, kind, f1, f2=None, order=2):
    """Butterworth-magnitude filtering via rFFT — static cutoff per note,
    which is all a 2-second event needs. No scipy on this machine."""
    n = len(x)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    f = np.maximum(f, 1e-6)
    if kind == "lp":
        H = 1 / np.sqrt(1 + (f / f1) ** (2 * order))
    elif kind == "hp":
        H = 1 / np.sqrt(1 + (f1 / f) ** (2 * order))
    else:  # bp
        H = (1 / np.sqrt(1 + (f1 / f) ** (2 * order))) * \
            (1 / np.sqrt(1 + (f / f2) ** (2 * order)))
    return np.fft.irfft(X * H, n)

def adsr(n, a, d, s, r):
    """attack/decay in seconds, s = sustain level, r = release seconds.
    Release is carved out of the tail, so an event stays its length."""
    t = np.arange(n) / SR
    total = n / SR
    env = np.where(t < a, t / max(a, 1e-4),
          np.where(t < a + d, 1 + (s - 1) * (t - a) / max(d, 1e-4), s))
    rel = np.clip((total - t) / max(r, 1e-4), 0, 1)
    return env * rel

def saw(ph):  return 2.0 * (ph % 1.0) - 1.0
def tri(ph):  return 2.0 * np.abs(2.0 * (ph % 1.0) - 1.0) - 1.0
def sqr(ph):  return np.sign(np.sin(2 * np.pi * ph))

def phase(freq, n):
    if np.isscalar(freq):
        return np.arange(n) * (freq / SR)
    return np.cumsum(freq) / SR

# ---------------------------------------------------------------- drums
def d_kick(dur=0.28, punch=110, base=47, sweep=26, decay=9.5):
    n = int(dur * SR); t = np.arange(n) / SR
    f = base + punch * np.exp(-t * sweep)
    x = np.sin(2 * np.pi * phase(f, n)) * np.exp(-t * decay)
    click = rng.standard_normal(int(0.004 * SR)) * 0.5
    x[:len(click)] += fft_filter(click, "hp", 1500)
    return x * 1.15

def d_snare(dur=0.22, tone=190, bright=7500):
    n = int(dur * SR); t = np.arange(n) / SR
    noise = fft_filter(rng.standard_normal(n), "bp", 900, bright) * np.exp(-t * 21)
    body = np.sin(2 * np.pi * phase(tone, n)) * np.exp(-t * 30)
    return noise * 0.85 + body * 0.5

def d_rim(dur=0.12):
    n = int(dur * SR); t = np.arange(n) / SR
    noise = fft_filter(rng.standard_normal(n), "bp", 1400, 5200) * np.exp(-t * 48)
    body = np.sin(2 * np.pi * phase(420, n)) * np.exp(-t * 60)
    return noise * 0.5 + body * 0.6

def d_hat(dur=0.05, open_=False):
    if open_: dur = 0.32
    n = int(dur * SR); t = np.arange(n) / SR
    x = fft_filter(rng.standard_normal(n), "hp", 6500)
    return x * np.exp(-t * (8 if open_ else 65)) * 0.5

def d_shaker(dur=0.09):
    n = int(dur * SR); t = np.arange(n) / SR
    x = fft_filter(rng.standard_normal(n), "bp", 3800, 9500)
    env = np.minimum(t / 0.02, 1) * np.exp(-t * 34)
    return x * env * 0.5

# ---------------------------------------------------------------- pitched
def i_bass(midi, dur, fc=700, sub=0.55, drive=1.4):
    n = int(dur * SR); f = hz(midi)
    x = saw(phase(f, n)) + sqr(phase(f, n)) * 0.25
    x = fft_filter(x, "lp", fc) * adsr(n, 0.004, 0.09, 0.75, 0.05)
    x += np.sin(2 * np.pi * phase(f / 2, n)) * sub * adsr(n, 0.004, 0.12, 0.8, 0.06)
    return np.tanh(x * drive) * 0.9

def i_epiano(midi, dur, soft=1.0):
    n = int(dur * SR); t = np.arange(n) / SR; f = hz(midi)
    x = (np.sin(2 * np.pi * phase(f, n)) +
         np.sin(2 * np.pi * phase(f * 2.001, n)) * 0.32 * np.exp(-t * 5) +
         np.sin(2 * np.pi * phase(f * 3.997, n)) * 0.10 * np.exp(-t * 8))
    trem = 1 + 0.06 * np.sin(2 * np.pi * 4.7 * t)
    return x * np.exp(-t * 2.6 / soft) * adsr(n, 0.003, 0.2, 0.7, 0.12) * trem * 0.5

def i_clav(midi, dur):
    n = int(dur * SR); f = hz(midi)
    x = sqr(phase(f, n)) * 0.6 + saw(phase(f * 1.004, n)) * 0.5
    x = fft_filter(x, "lp", 2400)
    return x * adsr(n, 0.002, 0.14, 0.12, 0.04) * 0.8

def i_stab(mids, dur, fc=2100):
    n = int(dur * SR)
    x = np.zeros(n)
    for m in mids:
        f = hz(m)
        for det in (0.9965, 1.0, 1.0035):
            x += saw(phase(f * det, n))
    x = fft_filter(x / (len(mids) * 3), "lp", fc)
    return x * adsr(n, 0.004, 0.22, 0.25, 0.08) * 0.95

def i_pad(mids, dur, fc=1150):
    n = int(dur * SR)
    x = np.zeros(n)
    for m in mids:
        f = hz(m)
        for det in (0.995, 1.0, 1.005):
            x += saw(phase(f * det, n))
    x = fft_filter(x / (len(mids) * 3), "lp", fc)
    return x * adsr(n, min(0.6, dur * 0.3), 0.3, 0.8, min(0.8, dur * 0.35)) * 0.8

def i_lead(midi, dur, fc=2600, vib=5.4):
    n = int(dur * SR); t = np.arange(n) / SR
    f = hz(midi) * (1 + 0.007 * np.sin(2 * np.pi * vib * t) * np.minimum(t / 0.25, 1))
    x = saw(phase(f, n)) + saw(phase(f * 1.005, n))
    x = fft_filter(x / 2, "lp", fc)
    return x * adsr(n, 0.02, 0.15, 0.75, 0.1) * 0.8

def i_sine_lead(midi, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    f = hz(midi) * (1 + 0.006 * np.sin(2 * np.pi * 4.8 * t) * np.minimum(t / 0.3, 1))
    x = np.sin(2 * np.pi * phase(f, n)) + 0.18 * np.sin(2 * np.pi * phase(f * 2, n))
    return x * adsr(n, 0.04, 0.3, 0.6, 0.25) * 0.75

def fx_vinyl(dur):
    """sparse crackle bed — the lo-fi track's plate of dust"""
    n = int(dur * SR)
    x = np.zeros(n)
    ticks = rng.integers(0, n, size=int(dur * 9))
    x[ticks] = rng.uniform(-1, 1, size=len(ticks))
    x = fft_filter(x, "bp", 900, 7000)
    x += fft_filter(rng.standard_normal(n), "lp", 400) * 0.02
    return x * 0.35

# ---------------------------------------------------------------- track kit
class Song:
    def __init__(self, bpm, bars, swing=0.0):
        self.bpm, self.swing = bpm, swing
        self.beat = 60.0 / bpm
        self.n = int(bars * 4 * self.beat * SR) + SR
        self.L = np.zeros(self.n); self.R = np.zeros(self.n)

    def t(self, bar, beat):
        """seconds for (bar, beat) with 16th swing on the off-16ths"""
        b = bar * 4 + beat
        sw = 0.0
        frac = (b * 2) % 1        # position inside the 8th, in 16ths
        if abs(frac - 0.5) < 1e-6 and self.swing:
            sw = self.swing * self.beat * 0.25
        return b * self.beat + sw

    def put(self, sig, when, gain=1.0, pan=0.0):
        i = int(when * SR)
        if i < 0 or i >= self.n: return
        seg = sig[:self.n - i]
        gl = gain * min(1, 1 - pan); gr = gain * min(1, 1 + pan)
        self.L[i:i + len(seg)] += seg * gl
        self.R[i:i + len(seg)] += seg * gr

    def echo(self, sig, when, gain, pan, taps, fb, delay_beats):
        self.put(sig, when, gain, pan)
        d = delay_beats * self.beat
        for k in range(1, taps + 1):
            self.put(sig, when + k * d, gain * (fb ** k), -pan if k % 2 else pan)

    def master(self):
        x = np.stack([self.L, self.R])
        # trim trailing silence to the last audible sample + a short tail
        mag = np.max(np.abs(x), axis=0)
        last = np.max(np.nonzero(mag > 1e-4)) if np.any(mag > 1e-4) else self.n - 1
        x = x[:, :min(self.n, last + int(0.4 * SR))]
        rms = np.sqrt(np.mean(x ** 2))
        x *= RMS_TARGET / max(rms, 1e-9)
        x = np.tanh(x * 1.25) / np.tanh(1.25)          # soft ceiling, no hard clip
        n = x.shape[1]
        fade = int(0.03 * SR)
        x[:, :fade] *= np.linspace(0, 1, fade)
        out_fade = int(1.2 * SR)
        x[:, -out_fade:] *= np.linspace(1, 0, out_fade)
        return x

def write_wav(path, x):
    pcm = (np.clip(x, -1, 1) * 32767).astype("<i2").T.reshape(-1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(pcm.tobytes())

# ---------------------------------------------------------------- track 1
def neon_crema():
    """disco-house, 116 bpm — the party track"""
    S = Song(116, 48)
    Am, F, C, G = [57, 60, 64], [53, 57, 60], [55, 60, 64], [55, 59, 62]
    prog = [Am, F, C, G]
    roots = [45, 41, 36, 43]
    basspat = [(0, .5, 0), (.5, .25, 0), (1, .5, 12), (2, .5, 0), (2.75, .25, 12), (3, .5, 0), (3.5, .5, 7)]
    for bar in range(46):
        sec_intro, sec_break = bar < 4, 24 <= bar < 28
        ch = prog[bar % 4]; root = roots[bar % 4]
        if not sec_break:
            for b in range(4):
                S.put(d_kick(), S.t(bar, b), 0.95)
        if not sec_intro and not sec_break:
            for b in (1, 3):
                S.put(d_snare(), S.t(bar, b), 0.55, 0.06)
        for b in range(4):
            S.put(d_hat(open_=True), S.t(bar, b + 0.5), 0.5, 0.22)
            for q in (0, 0.25, 0.75):
                S.put(d_hat(), S.t(bar, b + q), 0.3 + 0.12 * ((b + int(q * 4)) % 2), -0.18)
        if not sec_break:
            for (off, dur, iv) in basspat:
                S.put(i_bass(root + iv, dur * S.beat, fc=820), S.t(bar, off), 0.8)
        if not sec_intro:
            for off in (0.5, 2.5, 3.25):
                S.put(i_stab([m + 12 for m in ch], 0.32 * S.beat), S.t(bar, off), 0.4, 0.2)
        if sec_break or bar >= 40:
            S.put(i_pad([m + 12 for m in ch] + [root + 24], 4 * S.beat), S.t(bar, 0), 0.32, -0.1)
        if 12 <= bar < 24 or 32 <= bar < 40:
            mel = [[76, 74, 72, None], [74, 72, 69, 71], [72, 71, 67, 64], [67, 71, 74, 79]][bar % 4]
            for i, m in enumerate(mel):
                if m is None: continue
                S.echo(i_lead(m, 0.6 * S.beat), S.t(bar, i * 1 + 0.5), 0.34, 0.25, 2, 0.4, 1.5)
    return S

# ---------------------------------------------------------------- track 2
def percolator_funk():
    """clav funk, 102 bpm, swung 16ths"""
    S = Song(102, 44, swing=0.28)
    Em7, A7 = [52, 55, 59, 62], [49, 55, 57, 61]
    for bar in range(42):
        sec_intro, sec_break = bar < 4, 22 <= bar < 26
        ch = Em7 if bar % 4 < 2 else A7
        root = 40 if bar % 4 < 2 else 45
        if not sec_break:
            for off in (0, 1.75, 2.5):
                S.put(d_kick(punch=90, base=52, decay=11), S.t(bar, off), 0.9)
            for b in (1, 3):
                S.put(d_snare(tone=210, bright=6800), S.t(bar, b), 0.5, 0.05)
            if bar % 2 == 1:
                S.put(d_snare(dur=0.1), S.t(bar, 3.75), 0.24, -0.1)
        for b in range(4):
            for q in (0, 0.25, 0.5, 0.75):
                g = 0.34 if q in (0, 0.5) else 0.2
                S.put(d_hat(), S.t(bar, b + q), g, 0.2)
        S.put(d_shaker(), S.t(bar, 2.5), 0.3, -0.3)
        if not sec_break:
            walk = [(0, .75, 0), (1, .25, 0), (1.5, .5, 10), (2, .5, 12), (2.75, .25, 10), (3, .5, 7), (3.5, .5, 3)]
            for (off, dur, iv) in walk:
                S.put(i_bass(root + iv, dur * S.beat, fc=640, drive=1.7), S.t(bar, off), 0.78)
        if not sec_intro:
            for off, up in ((0.5, 0), (1.25, 0), (2.25, 12), (3.5, 0)):
                for m in ch[1:]:
                    S.put(i_clav(m + up, 0.22 * S.beat), S.t(bar, off), 0.3, 0.15)
        if (bar % 8) == 7 and not sec_break:
            S.put(i_stab([m + 12 for m in ch], 0.5 * S.beat, fc=2600), S.t(bar, 3), 0.5, -0.2)
        if sec_break:
            S.put(i_pad([m + 12 for m in ch], 4 * S.beat, fc=900), S.t(bar, 0), 0.3)
        if 26 <= bar < 38:
            riff = [[None, 76, 74, 71], [72, None, 71, 67], [None, 69, 71, 72], [74, None, None, None]][bar % 4]
            for i, m in enumerate(riff):
                if m is None: continue
                S.echo(i_epiano(m, 0.7 * S.beat, soft=0.8), S.t(bar, i + 0.5), 0.5, -0.25, 2, 0.35, 0.75)
    return S

# ---------------------------------------------------------------- track 3
def after_hours_foam():
    """lo-fi, 84 bpm — for the last customers"""
    S = Song(84, 40, swing=0.22)
    Fmaj7, Em7, Dm7, Cmaj7 = [53, 57, 60, 64], [52, 55, 59, 62], [50, 53, 57, 60], [48, 52, 55, 59]
    prog = [Fmaj7, Em7, Dm7, Cmaj7]
    roots = [41, 40, 38, 36]
    S.put(fx_vinyl(S.n / SR - 1), 0, 0.5)
    for bar in range(38):
        sec_intro, sec_break = bar < 2, 20 <= bar < 24
        ch = prog[bar % 4]; root = roots[bar % 4]
        if not sec_break:
            for off in (0, 2.5):
                S.put(d_kick(punch=70, base=44, decay=8), S.t(bar, off), 0.85)
            if bar % 4 == 3:
                S.put(d_kick(punch=70, base=44, decay=8), S.t(bar, 3.5), 0.5)
            for b in (1, 3):
                S.put(d_rim(), S.t(bar, b), 0.5, 0.08)
        for b in range(4):
            for q in (0, 0.5):
                S.put(d_hat(dur=0.04), S.t(bar, b + q), 0.22 + 0.08 * (b % 2), -0.15)
        if not sec_intro:
            # one lazy chord a bar, restruck halfway when the room feels empty
            offs = (0,) if bar % 2 == 0 else (0, 2.5)
            for off in offs:
                for i, m in enumerate(ch):
                    S.put(i_epiano(m + 12, 2.4 * S.beat, soft=1.4),
                          S.t(bar, off) + i * 0.028, 0.42, -0.15 + i * 0.1)
        S.put(i_bass(root, 1.4 * S.beat, fc=420, sub=0.8, drive=1.2), S.t(bar, 0), 0.62)
        S.put(i_bass(root + 7, 0.8 * S.beat, fc=420, sub=0.7, drive=1.2), S.t(bar, 2.5), 0.5)
        if 8 <= bar < 20 or 28 <= bar < 34:
            line = [[None, None, 72, 71], [69, None, None, None], [None, 67, 69, 71], [72, None, 69, None]][bar % 4]
            for i, m in enumerate(line):
                if m is None: continue
                S.echo(i_sine_lead(m, 1.1 * S.beat), S.t(bar, i + 0.5), 0.4, 0.2, 2, 0.32, 1.5)
    return S

# ---------------------------------------------------------------- render
TRACKS = [
    ("neon_crema", "Neon Crema", neon_crema),
    ("percolator_funk", "Percolator Funk", percolator_funk),
    ("after_hours_foam", "After Hours Foam", after_hours_foam),
]

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="vc_music_")
    for key, title, fn in TRACKS:
        print(f"— rendering {title} …")
        x = fn().master()
        wav = os.path.join(tmp, key + ".wav")
        m4a = os.path.join(OUT_DIR, key + ".m4a")
        write_wav(wav, x)
        subprocess.run(["afconvert", "-f", "m4af", "-d", "aac", "-b", "128000",
                        "-q", "127", wav, m4a], check=True)
        dur = x.shape[1] / SR
        size = os.path.getsize(m4a)
        print(f"  {key}.m4a  {dur:6.1f} s  {size/1e6:.2f} MB  "
              f"rms {20*math.log10(np.sqrt(np.mean(x**2))):.1f} dBFS")
    print("done — copy the durations into the MUSIC map in index.html")

if __name__ == "__main__":
    main()
