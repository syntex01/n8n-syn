"""
"EREBUS" — dark + epic, driving, addictive. Not warm; clean-but-not-harsh.

Pivot from the ambient sad piece: this is felt in the body and engineered to
be addictive, using verified psychology + a few "advanced" perceptual tricks:

  * ANTICIPATION -> REWARD: build/riser/impact -> drop. The drop is the
    dopaminergic payoff; two escalating drops + a final one (peak-end rule).
  * GROOVE entrainment: half-time backbeat + driving 16th sub/bass; sidechain
    "pump" locked to the kick = the felt, danceable breathe.
  * SUB-BASS embodiment: 35-60 Hz sub + chest-hit impacts = physically felt.
  * DARK vs EPIC contrast: C-minor dark groove sections vs bright bVI/bIII
    "epic lift" climaxes -- contrast itself is the emotional lever.
  * SHEPARD/Risset glissando in the breaks: an endlessly-rising tone = mounting
    dread/tension the listener feels but can't place (an "advanced" illusion).
  * A short, repeated pentatonic HOOK (low interval-entropy = burns in).

Clean not harsh: anti-aliased oscillators, tamed 3-5 kHz, air cut ~16.5 kHz,
controlled hat levels, soft limiting (no hard clip).
"""

import wave
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

import dsp
from dsp import (SR, t_of, lowpass, highpass, bandpass, warm_osc, bl_saw,
                 sine, adsr, soft_sat, chorus)

BPM = 96
BEAT = 60.0 / BPM
STEP = BEAT / 4.0          # 16th
BAR = BEAT * 4             # 2.5 s
rng = np.random.default_rng(7)

_SEMI = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def note(name):
    i = 1; acc = 0
    if len(name) > 1 and name[1] in "#b":
        acc = 1 if name[1] == "#" else -1; i = 2
    midi = 12 * (int(name[i:]) + 1) + _SEMI[name[0]] + acc
    return 440.0 * 2 ** ((midi - 69) / 12.0)


# ------------------------------------------------------------- oscillators
def supersaw(freq, dur, voices=7, detune=0.14):
    """Anti-aliased detuned saw stack (PolyBLEP) -> big but not aliased/harsh."""
    out = np.zeros(int(dur * SR))
    for i in range(voices):
        d = (i - (voices - 1) / 2) / (voices - 1) * detune
        s = bl_saw(freq * 2 ** (d / 12.0), dur)
        out[:len(s)] += s
    return out / voices


# ------------------------------------------------------------- voices
def i_sub(freq, dur, gain=0.9):
    n = int(dur * SR)
    w = sine(freq, dur) + 0.16 * sine(freq * 2, dur)
    env = adsr(n, 0.006, 0.1, 0.9, 0.14)
    return lowpass(soft_sat(w * env, 1.1), 150) * gain


def i_bass(freq, dur, gain=0.55):
    n = int(dur * SR)
    w = 0.7 * supersaw(freq, dur, 3, 0.1)[:n] + sine(freq, dur)
    env = adsr(n, 0.004, 0.08, 0.7, 0.06)
    return lowpass(soft_sat(w * env, 1.15), 850) * gain


def i_chord(freqs, dur, gain=0.4, bright=4200):
    bright = min(bright, 3600)          # keep chords out of the harsh band
    n = int(dur * SR); w = np.zeros(n)
    for f in freqs:
        w += supersaw(f, dur, 5, 0.13)[:n]
    w = highpass(lowpass(w, bright), 180)
    env = adsr(n, 0.02, 0.2, 0.8, 0.3)
    return w * env / len(freqs) * gain


def i_lead(freq, dur, gain=0.5, bright=5500):
    bright = min(bright, 4400)          # present lead, not piercing
    n = int(dur * SR)
    w = lowpass(supersaw(freq, dur, 7, 0.16)[:n], bright)
    env = adsr(n, 0.01, 0.12, 0.8, 0.12)
    return w * env * gain


def i_choir(freq, dur, gain=0.3):
    n = int(dur * SR)
    src = warm_osc(freq, dur, rolloff=1.5, partials=10)[:n]
    src *= (1 + 0.006 * np.sin(2 * np.pi * 5.0 * t_of(dur)))
    form = (bandpass(src, 500, 800) + 0.6 * bandpass(src, 900, 1400)
            + 0.3 * bandpass(src, 2000, 2900))
    env = adsr(n, 0.15, 0.3, 0.85, 0.5)
    return lowpass(form * env, 4200) * gain


def i_pad(freq, dur, gain=0.22):
    n = int(dur * SR)
    w = warm_osc(freq, dur, rolloff=1.7, partials=12)[:n]
    env = adsr(n, 0.5, 0.4, 0.9, min(1.5, dur * 0.3))
    return lowpass(w * env, 3200) * gain


# ------------------------------------------------------------- drums
def kick(gain=1.0):
    dur = 0.36; t = t_of(dur)
    pitch = 150 * np.exp(-t * 34) + 48
    ph = 2 * np.pi * np.cumsum(pitch) / SR
    body = np.sin(ph) * np.exp(-t * 6.5)
    click = lowpass(rng.uniform(-1, 1, len(t)), 6000) * np.exp(-t * 120) * 0.4
    return soft_sat(body + click, 1.5) * gain


def snare(gain=1.0):
    dur = 0.28; t = t_of(dur)
    tone = (np.sin(2 * np.pi * 180 * t) + np.sin(2 * np.pi * 260 * t)) * np.exp(-t * 24)
    noise = lowpass(highpass(rng.uniform(-1, 1, len(t)), 900), 8000) * np.exp(-t * 16)
    return soft_sat(0.5 * tone + 0.95 * noise, 1.15) * gain


def hat(gain=0.4, open_=False):
    dur = 0.09 if open_ else 0.045; t = t_of(dur)
    nz = bandpass(rng.uniform(-1, 1, len(t)), 4200, 7800)   # lower cap -> less sibilant
    return nz * np.exp(-t * (7 if open_ else 30)) * gain


def tom(freq=120, gain=0.8):
    dur = 0.3; t = t_of(dur)
    pitch = freq * (1 + 0.7 * np.exp(-t * 16))
    ph = 2 * np.pi * np.cumsum(pitch) / SR
    return np.sin(ph) * np.exp(-t * 7) * gain


def boom(gain=1.0):
    dur = 1.6; t = t_of(dur)
    pitch = 60 * np.exp(-t * 3) + 32
    ph = 2 * np.pi * np.cumsum(pitch) / SR
    sub = np.sin(ph) * np.exp(-t * 2.2)
    nz = lowpass(rng.uniform(-1, 1, len(t)), 2500) * np.exp(-t * 5) * 0.4
    return soft_sat(sub + nz, 1.2) * gain


def crash(gain=0.5):
    dur = 1.4; t = t_of(dur)
    return lowpass(rng.uniform(-1, 1, len(t)), 9000) * np.exp(-t * 3.2) * gain


def env_lowpass(x, c0, c1, bands=10):
    n = len(x); out = np.zeros(n); cs = np.linspace(c0, c1, bands); win = n // bands
    for i, c in enumerate(cs):
        seg = slice(i * win, (i + 1) * win if i < bands - 1 else n)
        out[seg] = lowpass(x, c)[seg]
    return out


def riser(dur, gain=0.6):
    n = int(dur * SR); t = np.linspace(0, 1, n)
    nz = env_lowpass(rng.uniform(-1, 1, n), 400, 9000)
    swell = t ** 2
    fp = 200 * 2 ** (t * 4)                    # rising pitched layer
    ph = 2 * np.pi * np.cumsum(fp) / SR
    tonal = np.sin(ph) * (t ** 1.6) * 0.4
    return (nz * swell + tonal) * gain


def downlifter(dur=1.4, gain=0.5):
    n = int(dur * SR); t = np.linspace(0, 1, n)
    f = 1600 * 2 ** (-t * 4)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 1.6) * gain


def shepard(dur, up=True, cycles=2.0, gain=0.4, fmin=48.0, octs=7):
    """Risset/Shepard glissando: the illusion of endless rising (or falling)
    pitch -> mounting, placeless tension. Advanced + felt."""
    n = int(dur * SR); t = np.arange(n) / SR
    prog = (t / dur) * cycles * (1 if up else -1)
    out = np.zeros(n)
    for k in range(octs):
        pos = ((k / octs) + prog) % 1.0
        f = fmin * 2 ** (pos * octs)
        amp = 0.5 - 0.5 * np.cos(2 * np.pi * pos)      # fade at extremes
        ph = 2 * np.pi * np.cumsum(f) / SR
        out += amp * np.sin(ph)
    return lowpass(out / octs, 6000) * gain


# ------------------------------------------------------------- mixer
class Mix:
    def __init__(self, total):
        self.n = int(total * SR)
        self.dry = np.zeros((2, self.n))
        self.pump = np.zeros((2, self.n))     # sidechained bus
        self.wet = np.zeros((2, self.n))
        self.kicks = []

    def add(self, sig, at, gain=1.0, pan=0.5, bus="dry", send=0.14):
        i = int(at * SR)
        if i < 0 or i >= self.n:
            return
        sig = np.asarray(sig, float).copy()
        fd = int(0.003 * SR)
        if len(sig) > 3 * fd:
            sig[:fd] *= np.linspace(0, 1, fd); sig[-fd:] *= np.linspace(1, 0, fd)
        j = min(self.n, i + len(sig)); s = sig[:j - i]
        gl, gr = gain * np.sqrt(1 - pan), gain * np.sqrt(pan)
        tgt = self.pump if bus == "pump" else self.dry
        tgt[0, i:j] += gl * s; tgt[1, i:j] += gr * s
        self.wet[0, i:j] += gl * send * s; self.wet[1, i:j] += gr * send * s

    def kick(self, at, gain=1.0):
        self.add(kick(gain), at, 1.0, 0.5, "dry", 0.05)
        self.kicks.append(at)


M = Mix(200)


def sidechain(depth=0.72, rel=0.26):
    n = M.n; env = np.ones(n)
    a = int(0.004 * SR); r = int(rel * SR)
    duck = np.concatenate([np.linspace(1, 1 - depth, a),
                           1 - depth + depth * (1 - np.exp(-np.linspace(0, 5, r)))])
    for kt in M.kicks:
        i = int(kt * SR); j = min(n, i + len(duck))
        if i < n:
            env[i:j] = np.minimum(env[i:j], duck[:j - i])
    return env


def make_ir(seed, rt60=2.4, predelay_ms=18, damp=6000):
    n = int(rt60 * SR); r = np.random.default_rng(seed)
    ir = r.standard_normal(n) * np.exp(-np.linspace(0, 1, n) * 6.9)
    ir = lowpass(ir, damp)
    pd = int(predelay_ms / 1000 * SR)
    ir = np.concatenate([np.zeros(pd), ir])
    return ir / (np.sqrt(np.sum(ir ** 2)) + 1e-9)


def reverb(wet):
    irL, irR = make_ir(1), make_ir(2)
    return np.stack([fftconvolve(wet[0], irL)[:wet.shape[1]],
                     fftconvolve(wet[1], irR)[:wet.shape[1]]])


# =============================================================== ARRANGEMENT
CH = {"Cm": ["C4", "Eb4", "G4"], "Ab": ["Ab3", "C4", "Eb4"],
      "Eb": ["Eb4", "G4", "Bb4"], "Bb": ["Bb3", "D4", "F4"]}
ROOT = {"Cm": "C2", "Ab": "Ab1", "Eb": "Eb2", "Bb": "Bb1"}
PROG = ["Cm", "Ab", "Eb", "Bb"]

# Hook: C-minor pentatonic (C Eb F G Bb), a rising-to-held epic contour.
# (note, offset_s within a 2-bar/5s window, dur_s)
HOOK = [("G4", 0.0, 0.55), ("Bb4", 0.55, 0.5), ("C5", 1.05, 1.05),
        ("Bb4", 2.1, 0.4), ("G4", 2.5, 0.5), ("F4", 3.0, 0.5), ("G4", 3.5, 1.4)]


def bt(bar, step):
    return bar * BAR + step * STEP


def hook(at, gain=0.5, oct=0, bright=5500, pan=0.5):
    for nm, off, d in HOOK:
        f = note(nm) * (2 ** oct)
        M.add(i_lead(f, d + 0.15, gain=gain, bright=bright), at + off, 1.0, pan,
              "dry", 0.22)


def chord_bar(name, bar, dur_bars=2, gain=0.4, bright=4200, epic=False):
    freqs = [note(n) for n in CH[name]]
    if epic:
        freqs = freqs + [note(CH[name][0]) * 2]     # add octave -> bigger
    M.add(i_chord(freqs, dur_bars * BAR, gain=gain, bright=bright),
          bar * BAR, 1.0, 0.5, "pump", 0.22)


def bass_bar(name, bar, dur_bars=2, gain=0.55, drive=True):
    r = note(ROOT[name])
    M.add(i_sub(r, dur_bars * BAR, gain=0.9), bar * BAR, 1.0, 0.5, "pump", 0.03)
    if drive:                       # driving 16th/8th mid-bass, sidechained
        pat = [0, 3, 4, 6, 8, 11, 12, 14]
        for s in pat:
            for k in range(dur_bars):
                M.add(i_bass(r * 2, STEP * 1.6, gain=gain), bt(bar + k, s),
                      1.0, 0.5, "pump", 0.04)


def groove(bar, energy=1.0, epic=False, dense_hats=True):
    M.kick(bt(bar, 0), 1.0 * energy)
    M.kick(bt(bar, 10), 0.8 * energy)              # syncopated push
    if epic:
        M.kick(bt(bar, 6), 0.6 * energy)
    M.add(snare(0.95 * energy), bt(bar, 8), 1.0, 0.5, "dry", 0.18)   # half-time backbeat
    if epic:
        M.add(boom(0.7 * energy), bt(bar, 8), 1.0, 0.5, "dry", 0.2)
    if dense_hats:
        for s in range(16):
            if s % 2 == 1 or s in (4, 12):
                M.add(hat(0.15 * energy, open_=(s in (6, 14))), bt(bar, s),
                      1.0, 0.5 + 0.2 * np.sin(s), "dry", 0.06)


def tom_fill(bar):
    for j, s in enumerate([8, 10, 12, 13, 14, 15]):
        M.add(tom(150 - j * 14, gain=0.8), bt(bar, s), 1.0, 0.4 + 0.03 * j, "dry", 0.12)


def impact(bar):
    M.add(boom(1.0), bar * BAR, 1.0, 0.5, "dry", 0.25)
    M.add(crash(0.5), bar * BAR, 1.0, 0.5, "dry", 0.3)


print("building EREBUS ...")

# INTRO (0-7): dark drone + sub + filtered hook teaser + rising tension
for bar in range(0, 8):
    chord_bar(PROG[bar % 4], bar, 1, gain=0.28, bright=1400 + bar * 300)
    M.add(i_sub(note("C1"), BAR, gain=0.5), bar * BAR, 1.0, 0.5, "pump", 0.03)
M.add(i_pad(note("C3"), 8 * BAR, gain=0.16), 0, 1.0, 0.5, "dry", 0.3)
hook(2 * BAR, gain=0.22, bright=2200)               # muffled teaser
M.add(riser(2 * BAR, 0.4), 6 * BAR, 1.0, 0.5, "dry", 0.25)

# BUILD 1 (8-15): pulse, hats build, bass, riser+impact -> drop
for i, bar in enumerate(range(8, 16)):
    name = PROG[bar % 4]
    chord_bar(name, bar, 1, gain=0.3, bright=2000 + i * 250)
    bass_bar(name, bar, 1, gain=0.4 + 0.02 * i, drive=(i >= 3))
    if i >= 2:
        for s in range(0, 16, 2):
            M.add(hat(0.14 + 0.02 * i), bt(bar, s), 1.0, 0.5, "dry", 0.05)
    M.kick(bt(bar, 0), 0.7)
tom_fill(15)
M.add(riser(4 * BAR, 0.6), 12 * BAR, 1.0, 0.5, "dry", 0.3)
M.add(downlifter(1.2, 0.5), 16 * BAR, 1.0, 0.5, "dry", 0.2)

# DROP 1 — DARK GROOVE (16-31): half-time groove, sub, hook, sidechain
impact(16)
for bar in range(16, 32):
    name = PROG[bar % 4]
    groove(bar, energy=1.0, epic=False)
    chord_bar(name, bar, 1, gain=0.42, bright=3600)
    bass_bar(name, bar, 1, gain=0.55, drive=True)
    if bar % 8 == 7:
        tom_fill(bar)
for at in [16, 18, 20, 22, 24, 26, 28, 30]:
    hook(at * BAR, gain=0.5, bright=5200)

# BREAK (32-39): strip to choir + pad; Shepard tone rising; big impact out
for bar in range(32, 40):
    name = PROG[bar % 4]
    for f in [note(n) for n in CH[name]]:
        M.add(i_choir(f, 2 * BAR, gain=0.24), bar * BAR, 1.0, 0.5, "dry", 0.4)
    M.add(i_sub(note(ROOT[name]), BAR, gain=0.4), bar * BAR, 1.0, 0.5, "pump", 0.03)
M.add(shepard(8 * BAR, up=True, cycles=3, gain=0.32), 32 * BAR, 1.0, 0.5, "dry", 0.2)
M.add(riser(4 * BAR, 0.7), 36 * BAR, 1.0, 0.5, "dry", 0.3)
M.add(downlifter(1.4, 0.6), 40 * BAR, 1.0, 0.5, "dry", 0.2)

# DROP 2 — EPIC (40-55): big drums, epic bright chords, hook octave up, choir
impact(40)
for bar in range(40, 56):
    name = PROG[bar % 4]
    groove(bar, energy=1.1, epic=True)
    chord_bar(name, bar, 1, gain=0.46, bright=4800, epic=True)
    bass_bar(name, bar, 1, gain=0.6, drive=True)
    for f in [note(n) for n in CH[name]]:
        M.add(i_choir(f * 2, 1 * BAR, gain=0.14), bar * BAR, 1.0, 0.5, "dry", 0.35)
    if bar % 8 == 7:
        tom_fill(bar)
for at in [40, 42, 44, 46, 48, 50, 52, 54]:
    hook(at * BAR, gain=0.5, oct=1, bright=6000)      # the epic lift
    hook(at * BAR, gain=0.28, oct=0, bright=4800)

# BRIDGE (56-63): dark breakdown, ominous, lone lead, rebuild
for bar in range(56, 64):
    name = PROG[bar % 4]
    chord_bar(name, bar, 1, gain=0.3, bright=2200)
    M.add(i_sub(note(ROOT[name]), BAR, gain=0.5), bar * BAR, 1.0, 0.5, "pump", 0.03)
    if bar in (56, 58, 60):
        M.add(boom(0.5), bar * BAR, 1.0, 0.5, "dry", 0.2)
hook(58 * BAR, gain=0.4, bright=3600)
M.add(shepard(4 * BAR, up=True, cycles=2, gain=0.28), 60 * BAR, 1.0, 0.5, "dry", 0.2)
M.add(riser(4 * BAR, 0.75), 60 * BAR, 1.0, 0.5, "dry", 0.3)
M.add(downlifter(1.4, 0.6), 64 * BAR, 1.0, 0.5, "dry", 0.2)

# FINAL DROP (64-75): biggest, dark + epic combined
impact(64)
for bar in range(64, 76):
    name = PROG[bar % 4]
    groove(bar, energy=1.18, epic=True)
    chord_bar(name, bar, 1, gain=0.48, bright=5000, epic=True)
    bass_bar(name, bar, 1, gain=0.62, drive=True)
    for f in [note(n) for n in CH[name]]:
        M.add(i_choir(f * 2, 1 * BAR, gain=0.16), bar * BAR, 1.0, 0.5, "dry", 0.35)
    if bar % 4 == 3:
        tom_fill(bar)
for at in [64, 66, 68, 70, 72, 74]:
    hook(at * BAR, gain=0.55, oct=1, bright=6200)
    hook(at * BAR, gain=0.3, oct=0, bright=4800)
# final chest-hit + dark tail
impact(76)
M.add(i_sub(note("C1"), 4, gain=0.6), 76 * BAR, 1.0, 0.5, "pump", 0.05)
M.add(i_pad(note("C3"), 5, gain=0.18), 76 * BAR, 1.0, 0.5, "dry", 0.4)


# =============================================================== MASTER
def peaking_cut(x, lo, hi, db):
    g = 1 - 10 ** (db / 20.0)
    return x - g * bandpass(x, lo, hi)


def limiter(x, ceil=0.95):
    return np.tanh(x / (ceil * 1.8)) * ceil * 1.02   # gentle -> keep dynamics


def loudness_curve(n):
    """Contrast arc so builds/breaks drop and the drops SLAM (anticipation
    -> reward). dB over time; ~10 dB swing."""
    pts = [(0, -10), (16, -7), (38, -1.5), (40, -0.5), (78, -1), (82, -8),
           (98, -3.5), (100, -0.2), (138, -0.5), (142, -9), (158, -3.5),
           (160, 0), (188, 0), (200, -30)]
    ts = np.array([p[0] for p in pts]); db = np.array([p[1] for p in pts])
    t = np.arange(n) / SR
    return 10 ** (np.interp(t, ts, db) / 20.0)


def master():
    print("  reverb ...")
    sc = sidechain()
    wet = reverb(M.wet)
    mix = M.dry + M.pump * sc + 0.85 * wet
    mix = mix * loudness_curve(mix.shape[1])     # dynamic contrast
    out = []
    for ch in range(2):
        x = mix[ch]
        x = highpass(x, 28, 2)
        x = peaking_cut(x, 2500, 5500, -4.5)     # strongly tame the harsh band
        x = dsp.highshelf_cut(x, 6500, -3)       # roll off sibilant top
        x = lowpass(x, 15000, 4)                 # air cut (not piercing)
        x = soft_sat(x * 1.03, 1.08)             # glue
        x = limiter(x, 0.95)
        out.append(x)
    L, R = out
    m = max(np.max(np.abs(L)), np.max(np.abs(R))) + 1e-9
    L, R = L / m * 0.97, R / m * 0.97
    fi = int(0.3 * SR); fo = int(3.0 * SR)
    for x in (L, R):
        x[:fi] *= np.linspace(0, 1, fi); x[-fo:] *= np.linspace(1, 0, fo) ** 1.3
    return np.stack([L, R])


def write_wav(path, st):
    data = (np.clip(st.T, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(data.tobytes())


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "erebus.wav"
    st = master()
    write_wav(out, st)
    print(f"wrote {out}  ({st.shape[1] / SR:.1f}s, stereo {SR}Hz)")
