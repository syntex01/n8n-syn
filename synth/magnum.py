"""
"Afterglow / Ashfall" — the magnum opus.

Implements synth/SPEC.md (produced by the design workflow): a ~4 min dark,
melancholic, warm instrumental. D minor Aeolian->Phrygian, 60 BPM 6/8,
120 x 2s bars. Falling-minor-6th motif (D5->F4->G4->F4->E4) that lands on the
2nd and never resolves; golden-ratio catharsis at ~148 s; JI-leaning warm
additive timbres; 1/f humanization; de-harsh warm master.

Built on the validated warm toolkit in dsp.py (no aliased oscillators; spectral
centroid held low). Every structural choice traces to the spec's theory tags.
"""

import numpy as np
from scipy.signal import fftconvolve

import dsp
from dsp import (SR, t_of, lowpass, highpass, bandpass, highshelf_cut,
                 warm_osc, sine, adsr, swell, pink, pink_curve, chorus,
                 tape_wow, soft_sat)

BPM = 60
EIGHTH = 60 / (BPM * 3)      # 6/8: 6 eighths per bar
BAR = 6 * EIGHTH             # = 2.0 s
TOTAL = 240.0
CLIMAX = 0.618034 * TOTAL    # ~148.3 s

rng = np.random.default_rng(20240701)

# --------------------------------------------------------------- pitch
_SEMI = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def note(name):
    """Scientific pitch (A4=440). 'D2','Bb2','C#4','Eb2' -> Hz."""
    i = 1
    acc = 0
    if len(name) > 1 and name[1] in "#b":
        acc = 1 if name[1] == "#" else -1
        i = 2
    midi = 12 * (int(name[i:]) + 1) + _SEMI[name[0]] + acc
    return 440.0 * 2 ** ((midi - 69) / 12.0)


def drift(n):
    """±3-6 cent slow (pink) random-walk detune multiplier — within-note life."""
    cents = pink_curve(max(8, n // 2000), -5, 5)
    cents = np.interp(np.linspace(0, len(cents) - 1, n), np.arange(len(cents)), cents)
    return 2 ** (cents / 1200.0)


# --------------------------------------------------------------- 3-plane stage
class Stage:
    def __init__(self):
        n = int((TOTAL + 5) * SR)
        self.dry = np.zeros((2, n))
        self.wet = np.zeros((2, n))   # reverb send bus
        self.n = n

    def add(self, sig, at, gain=1.0, pan=0.5, send=0.2):
        i = int(at * SR)
        if i >= self.n or i < 0:
            return
        j = min(self.n, i + len(sig))
        s = sig[:j - i]
        gl, gr = gain * np.sqrt(1 - pan), gain * np.sqrt(pan)
        self.dry[0, i:j] += gl * s
        self.dry[1, i:j] += gr * s
        self.wet[0, i:j] += gl * send * s
        self.wet[1, i:j] += gr * send * s


ST = Stage()


def place(sig, at, gain=1.0, pan=0.5, send=0.2, jitter=0.0):
    if jitter:
        at = at + float(rng.standard_normal()) * jitter
    # per-note micro-dynamics: ±1.5 dB pink
    gain *= 10 ** (float(rng.uniform(-1.5, 1.5)) / 20.0 * 0.5)
    ST.add(sig, max(0.0, at), gain, pan, send)


# --------------------------------------------------------------- instruments
def i_pad(freq, dur, gain=0.18, rolloff=2.0, layers=3, lp=2500):
    n = int(dur * SR)
    out = np.zeros(n)
    for L in range(layers):
        det = 2 ** ((L - (layers - 1) / 2) * 5 / 1200.0)   # ±5 cents layers
        w = warm_osc(freq * det, dur, rolloff=rolloff, partials=12)
        out += w[:n]
    out /= layers
    out *= drift(n)[:n] if False else 1.0
    lfo = 1 + 0.10 * np.sin(2 * np.pi * 0.13 * t_of(dur) + rng.uniform(0, 6))  # slow swell
    env = adsr(n, a=1.1, d=0.6, s=0.92, r=min(1.6, dur * 0.25))   # hold flat, short release
    return lowpass(out * env * lfo, lp) * gain


def i_choir(freq, dur, gain=0.16, lp=3000):
    n = int(dur * SR)
    src = warm_osc(freq, dur, rolloff=1.8, partials=8)[:n]
    vib = 1 + 0.006 * np.sin(2 * np.pi * 5.0 * t_of(dur))
    src = src * vib
    form = (1.0 * bandpass(src, 500, 750) + 0.5 * bandpass(src, 850, 1200)
            + 0.25 * bandpass(src, 2100, 2700))
    env = adsr(n, a=0.9, d=0.5, s=0.88, r=min(1.6, dur * 0.25))
    return lowpass(form * env, lp) * gain


def i_cello(freq, dur, gain=0.2):
    n = int(dur * SR)
    body = warm_osc(freq, dur, rolloff=1.6, partials=8)[:n] * drift(n)
    # delayed vibrato onset (~0.4s)
    t = t_of(dur)
    vdepth = np.clip((t - 0.4) / 0.4, 0, 1) * 0.008
    body = body * (1 + vdepth * np.sin(2 * np.pi * 4.5 * t))
    # bow noise enveloped WITH the attack (decays into sustain)
    bow = lowpass(rng.uniform(-1, 1, n), 800) * np.exp(-t * 6) * 0.03
    env = adsr(n, a=0.45, d=0.4, s=0.88, r=min(1.6, dur * 0.3))
    return lowpass((body + bow) * env, 4000) * gain


def i_felt(freq, dur, gain=0.5):
    """Felt keys: inharmonic partials, per-partial decay (highs die first),
    soft felt thump. Carries the motif."""
    n = int(dur * SR)
    t = t_of(dur)
    B = 0.0004
    tau1 = max(0.6, dur * 0.7)
    out = np.zeros(n)
    for k in range(1, 7):
        fk = k * freq * np.sqrt(1 + B * k * k)
        if fk > SR / 2 - 100:
            break
        ak = (1.0 / k ** 1.6)
        out += ak * np.sin(2 * np.pi * fk * t) * np.exp(-t / (tau1 / k))
    out /= np.max(np.abs(out)) + 1e-9
    # felt thump: LP noise burst <=300 Hz, ~20 ms
    thn = int(0.02 * SR)
    thump = np.zeros(n)
    thump[:thn] = lowpass(rng.uniform(-1, 1, thn), 300) * np.exp(-np.linspace(0, 1, thn) * 5)
    atk = int(0.010 * SR)
    aenv = np.ones(n); aenv[:atk] = np.linspace(0, 1, atk) ** 1.3
    return (out * aenv + 0.25 * thump) * gain


def i_bell(freq, dur, gain=0.12):
    n = int(dur * SR); t = t_of(dur)
    out = np.zeros(n)
    for k, r in [(1, 1.0), (2.76, 0.5), (5.4, 0.25)]:
        f = freq * r
        if f > SR / 2 - 100:
            continue
        out += (1.0 / (k)) * np.sin(2 * np.pi * f * t) * np.exp(-t / (dur * 0.5))
    return lowpass(out / (np.max(np.abs(out)) + 1e-9), 3000) * gain


def i_sub(freq, dur, gain=0.5):
    n = int(dur * SR)
    w = sine(freq, dur) + 0.13 * sine(freq * 2, dur)
    env = adsr(n, a=0.15, d=0.4, s=0.9, r=min(3.0, dur * 0.4))
    return lowpass(soft_sat(w * env, 1.05), 120) * gain


def heartbeat(gain=0.5):
    dur = 0.42; n = int(dur * SR); t = t_of(dur)
    f = 40 + 15 * np.exp(-t * 80)      # 55->40 Hz, ~12 ms drop
    ph = 2 * np.pi * np.cumsum(f) / SR
    env = np.exp(-t * 6)
    atk = int(0.004 * SR); env[:atk] *= np.linspace(0, 1, atk)
    return soft_sat(np.sin(ph) * env, 1.1) * gain


def mallet(freq, gain=0.4):
    dur = 0.05; t = t_of(dur)
    return np.sin(2 * np.pi * freq * t) * np.exp(-t * 30) * gain


def reverse_swell(freq, dur, gain=0.25):
    n = int(dur * SR)
    w = warm_osc(freq, dur, rolloff=2.2, partials=10)[:n]
    return lowpass(w, 2000) * swell(n, 0.9) * gain


# --------------------------------------------------------------- reverb (conv)
def make_ir(seed, rt60=3.6, predelay_ms=25, damp=4200):
    n = int(rt60 * SR)
    r = np.random.default_rng(seed)
    ir = r.standard_normal(n) * np.exp(-np.linspace(0, 1, n) * (6.9 / 1.0))
    ir = lowpass(ir, damp)
    # progressive darkening: extra LP on the tail
    ir[n // 2:] = lowpass(ir[n // 2:], 2200)
    pd = int(predelay_ms / 1000 * SR)
    ir = np.concatenate([np.zeros(pd), ir])
    return ir / (np.sqrt(np.sum(ir ** 2)) + 1e-9)


def convolve_reverb(wet_stereo):
    irL = make_ir(1, damp=4200)
    irR = make_ir(2, damp=4000)
    outL = fftconvolve(wet_stereo[0], irL)[:wet_stereo.shape[1]]
    outR = fftconvolve(wet_stereo[1], irR)[:wet_stereo.shape[1]]
    return np.stack([outL, outR])


# =============================================================== ARRANGEMENT
def chord(notes, at, dur, inst="pad", gain=1.0, pan=0.5, send=0.3, spread=0.0):
    """Play a chord voicing (list of note names) on an instrument."""
    for idx, nm in enumerate(notes):
        f = note(nm)
        p = pan + spread * ((idx / max(1, len(notes) - 1)) - 0.5)
        p = min(0.9, max(0.1, p))
        if inst == "pad":
            sig = i_pad(f, dur, gain=0.16 * gain)
        elif inst == "choir":
            sig = i_choir(f, dur, gain=0.14 * gain)
        elif inst == "cello":
            sig = i_cello(f, dur, gain=0.16 * gain)
        else:
            sig = i_pad(f, dur, gain=0.14 * gain)
        place(sig, at, 1.0, p, send)


def bass_drone(root_names, at, dur, gain=0.5, send=0.08):
    for nm in root_names:
        place(i_sub(note(nm), dur, gain=gain), at, 1.0, 0.5, send)


def play_motif(at, variant="full", gain=0.5, send=0.35, transpose=1.0):
    """Motif M and its transformations. Returns end time."""
    if variant == "full":       # D5 F4 G4 F4 E4 -- falling m6, ends on 2 (E)
        seq = [("D5", 0.5), ("F4", 1.0), ("G4", 0.45), ("F4", 0.45), ("E4", 1.8)]
    elif variant == "incomplete":   # first 2-3 notes trailing into reverb
        seq = [("D5", 0.5), ("F4", 1.6)]
    elif variant == "inverted":     # rising reach that collapses (false hope)
        seq = [("F4", 0.5), ("A4", 0.5), ("D5", 0.9), ("C5", 0.45), ("A4", 1.4)]
    elif variant == "augmented":    # doubled durations (peak, ceremonial)
        seq = [("D5", 1.0), ("F4", 2.0), ("G4", 0.9), ("F4", 0.9), ("E4", 3.0)]
    elif variant == "fragment":     # G F E eroding
        seq = [("G4", 0.45), ("F4", 0.45), ("E4", 1.6)]
    elif variant == "final":        # just E, foregrounded last image
        seq = [("E4", 2.4)]
    t = at
    for nm, d in seq:
        f = note(nm) * transpose
        place(i_felt(f, d + 0.4, gain=gain), t, 1.0, 0.46, send, jitter=0.010)
        t += d
    return t


print("building Afterglow / Ashfall ...")

# ---- Continuous D drone spine (grounding floor) — under A and E, thinned mid.
def drone(at, dur, gain, names=("D1", "D2", "A2")):
    for nm in names:
        place(i_sub(note(nm), dur, gain=gain), at, 1.0, 0.5, 0.05)


# ===== SECTION A : Numb / Emergence (0-35 s) — drone + incomplete motif germ
drone(0, 36, gain=0.22)
A_chords = [
    (["D2", "A2", "E4", "A4"], 0, 8),          # Dm(add9) no-3rd
    (["Bb2", "F3", "A4", "E5"], 8, 8),         # Bbmaj7#11
    (["G2", "D3", "A4", "Bb4"], 16, 8),        # Gm(add9)
    (["D2", "A2", "E4", "A4"], 24, 5),         # Dsus2
    (["D2", "A2", "F4", "A4"], 29, 6),         # -> Dm (the F reveal ~bar14/28s)
]
for nm, b, dur in A_chords:
    chord(nm, b * BAR, dur * BAR, inst="pad", gain=0.5, send=0.35, spread=0.4)
# incomplete motif germs, trailing into reverb
play_motif(14, "incomplete", gain=0.32, send=0.5)
play_motif(24, "incomplete", gain=0.34, send=0.5)
place(reverse_swell(note("A4"), 4, gain=0.15), 31, 1.0, 0.5, 0.5)

# ===== SECTION B : Longing / Growth (35-92 s) — full motif, appoggiaturas
SPINE = [
    (["D2", "A2", "F4", "E5"], "Dm(add9)"),
    (["Bb2", "A3", "D4", "F4"], "Bbmaj7"),
    (["C2", "A3", "E4", "A4"], "Fmaj7/C"),
    (["G2", "A3", "Bb4", "A5"], "Gm(add9)"),
]
b = 17.5
loop_bars = 8
while b < 46:
    for k, (nm, _) in enumerate(SPINE):
        at = b * BAR
        if at >= 92:
            break
        chord(nm, at, 2 * BAR, inst="pad", gain=1.0, send=0.3, spread=0.4)
        if k == 0:   # choir enters on the tonic of each loop
            chord(nm[2:], at, 2 * BAR, inst="choir", gain=0.9, send=0.45, spread=0.5)
        b += 2
# bass follows roots
for at, rn in [(35, "D2"), (43, "Bb2"), (51, "C2"), (59, "G2"),
               (67, "D2"), (75, "Bb2"), (83, "C2")]:
    bass_drone([rn], at, 8, gain=0.4)
# secondary theme (cello): A3 C4 D4 E4, one note/bar, the rising foil
for i, nm in enumerate(["A3", "C4", "D4", "E4"]):
    place(i_cello(note(nm), 2 * BAR, gain=0.2), 40 + i * 3, 1.0, 0.4, 0.3)
# full motif statements with G->F appoggiatura leaning
for at in [38, 52, 66, 80]:
    play_motif(at, "full", gain=0.42, send=0.4)
# Dorian glimmer (B natural) buried, then extinguished by Am7b5
place(i_choir(note("B4"), 3, gain=0.08), 74, 1.0, 0.6, 0.5)
chord(["A2", "Eb4", "G4", "C5"], 77, 3 * BAR, inst="pad", gain=0.7, send=0.35)

# ===== SECTION C : Descent / Pre-climax (92-148 s) — Phrygian, deny cadence
C_chords = [
    (["D2", "A2", "F4"], 46, 5),                  # Dm
    (["Eb2", "Bb2", "D4", "G4"], 51, 5),          # Ebmaj7 (Neapolitan bII)
    (["G2", "D3", "Bb4"], 56, 5),                 # Gm
    (["Bb2", "F3", "Db4", "F4"], 61, 5),          # Bbm (chromatic mediant)
    (["Eb2", "Bb2", "G4"], 66, 4),                # Eb
    (["D2", "A2", "F4"], 70, 4),                  # Dm (Phrygian half-cadence)
]
for nm, bb, dur in C_chords:
    at = bb * BAR
    chord(nm, at, dur * BAR, inst="pad", gain=1.3, send=0.32, spread=0.4)
    chord(nm[-2:], at, dur * BAR, inst="choir", gain=0.95, send=0.5, spread=0.5)
    bass_drone([nm[0]], at, dur * BAR, gain=0.45)
    place(i_cello(note(nm[0]) * 2, dur * BAR, gain=0.2), at, 1.0, 0.55, 0.3)  # sustain fills C
# register climb: inverted motif (desperate reach) mid-C
play_motif(104, "inverted", gain=0.4, send=0.42)
play_motif(120, "inverted", gain=0.42, send=0.42, transpose=1.0)
# THE one clean canonical motif statement, just before the peak
play_motif(140, "full", gain=0.5, send=0.35)
# heartbeat begins quietly in C, building
for i in range(int((92) / 2), int(148 / 2)):
    t = i * 2.0
    if t >= 92:
        place(heartbeat(gain=0.18 + 0.25 * (t - 92) / 56), t, 1.0, 0.5, 0.05, jitter=0.012)
# reverse swell rising into the peak
place(reverse_swell(note("D4"), 6, gain=0.3), 141, 1.0, 0.5, 0.4)
place(reverse_swell(note("A4"), 5, gain=0.22), 143, 1.0, 0.5, 0.45)

# ===== ★ THE BREAK / PEAK (~146-150 s) — silence gap -> unprepared bII bloom
# approach chords
chord(["G2", "D3", "A4", "Bb4"], 144, 2 * BAR, inst="pad", gain=1.0, send=0.3)
chord(["Bb2", "D4", "F4", "A4", "C5"], 146, 1.5, inst="pad", gain=1.0, send=0.3)
# reserved leading-tone chord A7 (the ONE dominant), brief
chord(["A2", "C#4", "G4"], 147.5, 0.7, inst="pad", gain=0.9, send=0.3)
# --- silence/held breath 0.5 s : nothing scheduled 148.2 -> 148.7 ---
# THE HIT at ~148.7: unprepared Eb (bII, Neapolitan) bloom + sub D1
PEAK = 148.7
chord(["Eb2", "Bb2", "G4", "Bb4"], PEAK, 8.0, inst="pad", gain=1.55, send=0.4, spread=0.5)
chord(["G4", "Bb4"], PEAK, 8.0, inst="choir", gain=1.15, send=0.55, spread=0.6)  # cello dropped at apex
bass_drone(["D1", "D2"], PEAK, 8.0, gain=0.85)
place(i_bell(note("D6"), 5, gain=0.14), PEAK, 1.0, 0.6, 0.7)
# single exposed suspension: hold E5 over Eb, resolve down to D5
place(i_felt(note("E5"), 2.0, gain=0.5), PEAK + 0.1, 1.0, 0.5, 0.4)
place(i_felt(note("D5"), 3.0, gain=0.45), PEAK + 1.9, 1.0, 0.5, 0.4)
# augmented motif under the bed
play_motif(PEAK + 0.5, "augmented", gain=0.34, send=0.4)
# soft mallet + tom mark the arrival (peak only)
place(mallet(note("D5"), gain=0.25), PEAK, 1.0, 0.4, 0.3)
place(lowpass(sine(90, 0.25) * np.exp(-t_of(0.25) * 10), 200) * 0.4, PEAK, 1.0, 0.5, 0.1)

# ===== SECTION D : Collapse / Aftermath (156-204 s) — strip away, no tonic
# sudden density cut right after the bloom decays
D_chords = [
    (["G2", "D3", "Bb4"], 78, 6),
    (["Bb2", "F3", "D4"], 84, 6),
    (["Eb2", "Bb2", "G4"], 90, 6),
    (["G2", "D3", "A4"], 96, 6),
]
for nm, bb, dur in D_chords:
    at = bb * BAR
    chord(nm, at, dur * BAR, inst="pad", gain=0.8, send=0.4, spread=0.4)
    bass_drone([nm[0]], at, dur * BAR, gain=0.32)
# motif returns "wounded" (fragment, lower, hesitant)
play_motif(162, "fragment", gain=0.34, send=0.5)
play_motif(178, "fragment", gain=0.3, send=0.55)
play_motif(192, "inverted", gain=0.26, send=0.55)
# heartbeat fading through D
for i in range(78, 102):
    t = i * 2.0
    place(heartbeat(gain=max(0.05, 0.32 * (204 - t) / 48)), t, 1.0, 0.5, 0.05, jitter=0.012)

# ===== SECTION E : Afterglow / open loop (204-240 s) — eroded, unresolved
drone(204, 38, gain=0.18)
E_chords = [
    (["G2", "D3", "A4", "Bb4"], 102, 6),      # Gm(add9)
    (["Bb2", "A3", "D4", "F4"], 108, 6),      # Bbmaj7
    (["D2", "A2", "E4", "A4"], 114, 6),       # Dm(add9)
]
for nm, bb, dur in E_chords:
    chord(nm, bb * BAR, dur * BAR, inst="pad", gain=0.5, send=0.5, spread=0.4)
# eroded motif fragments
play_motif(212, "fragment", gain=0.3, send=0.55)
play_motif(224, "fragment", gain=0.24, send=0.6)
# foregrounded final fragment ~232-235 s (the last image)
play_motif(232, "final", gain=0.4, send=0.5)
# final sonority: Dsus2 no-3rd, held; melody's last pitch = E4, decays to silence
chord(["D2", "A2", "A3", "E4"], 235, 5.0, inst="pad", gain=0.6, send=0.6, spread=0.3)
place(i_felt(note("E4"), 4.0, gain=0.34), 235.5, 1.0, 0.5, 0.5)


# =============================================================== MIX / MASTER
def peaking_cut(x, lo, hi, db):
    g = 1 - 10 ** (db / 20.0)
    return x - g * bandpass(x, lo, hi)


def low_shelf(x, fc, db):
    return x + (10 ** (db / 20.0) - 1) * lowpass(x, fc)


def asym_sat(x, a=1.2, b=0.15):
    return np.tanh(a * (x + b)) - np.tanh(a * b)


def compress(x, thr=0.72, ratio=1.5):
    """Gentle glue only — preserve the 12-16 dB emotional dynamic range."""
    env = np.maximum(lowpass(np.abs(x), 22), 1e-6)
    gain = np.ones_like(env)
    over = env > thr
    gain[over] = (thr + (env[over] - thr) / ratio) / env[over]
    return x * lowpass(gain, 40)


def loudness_curve(n):
    """Macro dynamic arc (spec S10): quiet numb A -> rising B/C -> towering
    phi peak -> sudden collapse -> long fade. dB breakpoints over time."""
    pts = [(0, -15), (18, -12.5), (35, -11), (92, -8.5), (140, -2),
           (148.7, 0), (150.5, -1.5), (156, -8.5), (180, -9.5), (204, -11),
           (232, -13), (240, -20)]
    ts = np.array([p[0] for p in pts]); db = np.array([p[1] for p in pts])
    t = np.arange(n) / SR
    return 10 ** (np.interp(t, ts, db) / 20.0)


def master(dry, wet):
    print("  rendering reverb (convolution) ...")
    wetr = convolve_reverb(wet)
    mix = dry + 0.9 * wetr
    lc = loudness_curve(mix.shape[1])       # macro dynamic arc
    mix = mix * lc
    out = []
    for ch in range(2):
        x = mix[ch]
        x = highpass(x, 25, 2)
        x = peaking_cut(x, 2400, 3800, -2.5)     # tame harsh band (3k dip)
        x = highshelf_cut(x, 3600, -3)           # pink tilt
        x = lowpass(x, 15500, 4)                 # air cut
        x = low_shelf(x, 120, 1.5)               # body / tape head-bump
        x = asym_sat(x * 1.1, 1.15, 0.15)        # warmth (2nd-harmonic)
        x = lowpass(x, 8000, 2)                  # post-sat de-harsh
        x = compress(x, thr=0.5, ratio=2.0)
        x = tape_wow(x, rate=0.6, depth_ms=1.6)
        out.append(x)
    L, R = out
    fl = lowpass(pink(len(L)), 6000) * 0.002     # ducked tape-hiss floor
    L, R = L + fl, R + fl
    m = max(np.max(np.abs(L)), np.max(np.abs(R))) + 1e-9
    L, R = L / m * 0.89, R / m * 0.89            # ~-1 dBFS headroom
    # gentle fades
    fi = int(0.8 * SR); fo = int(4.0 * SR)
    for x in (L, R):
        x[:fi] *= np.linspace(0, 1, fi) ** 1.5
        x[-fo:] *= np.linspace(1, 0, fo) ** 1.4
    return np.stack([L, R])


def write_wav(path, stereo):
    import wave
    data = (np.clip(stereo.T, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(data.tobytes())


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "afterglow.wav"
    stereo = master(ST.dry, ST.wet)
    write_wav(out, stereo)
    dur = stereo.shape[1] / SR
    print(f"wrote {out}  ({dur:.1f}s, stereo {SR}Hz)")
