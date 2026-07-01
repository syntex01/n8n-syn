"""
"GRAVEWATER — CRUSADE" : grimdark 40K, iterated.

Fixes/asks from the last pass:
 - CHANT reworked: 3 distinct phrases (varied contour/rhythm/vowels) + consonant
   articulation so it reads as words, deployed SELECTIVELY (given rests) instead
   of one loop everywhere; small per-repeat ornaments = optimal surprise.
 - MORE ALIEN / CUSTOM NOISES: metal scrape, ring-mod growl, alien zap, glitch
   stutter, chaotic voice, granular shards — as accents/transitions.
 - FASTER CYCLES: short 2-bar build -> 6-bar charge cycles that repeat with
   variation -> more frequent anticipation->reward (dopamine research), tighter
   repetition-with-variation (earworm), groove-sweet-spot syncopation.
Grounded in REPORT.md / research-sources.md. D Phrygian, 96 BPM, ~3:04.
"""
import numpy as np
from scipy.signal import fftconvolve

import dsp2
from orch import (note, t_of, lp, hp, bp, adsr, strings_sus, strings_stac, brass, choir_pad)
from thing import (Bus, SR, tilt, osat, pink_walk, make_ir,
                   groundwater, mantle, revenant_bell, cold_bell_larynx,
                   chorus_many, psithura, cribra, stairwell, missing_room,
                   pleura, PRIME, NOMINAL, QUINT)

rng = np.random.default_rng(40000)
BPM = 96.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
STEP = BEAT / 4.0
NBARS = 88
TOTAL = NBARS * BAR + 4

CYCLE_ROOT = ["D", "Eb", "C", "D"]
CHORD = {"D": ["D2", "A2", "D3", "F3", "A3"], "Eb": ["Eb2", "Bb2", "Eb3", "G3", "Bb3"],
         "C": ["C2", "G2", "C3", "E3", "G3"]}
SUBROOT = {"D": "D1", "Eb": "D#1", "C": "C1"}
VOWELS = {"ah": (700, 1150, 2600), "eh": (530, 1700, 2480), "oh": (500, 840, 2410),
          "oo": (330, 870, 2240), "ee": (300, 2100, 2900), "aw": (620, 980, 2500)}

# Three distinct chant phrases (D Phrygian). (note, start_beat, dur, vowel)
CHANT_A = [("D3", 0, 1.5, "ah"), ("F3", 1.5, 0.5, "eh"), ("E3", 2, 1, " oh".strip()), ("D3", 3, 1, "oh"),
           ("C3", 4, 1.5, "ah"), ("D3", 5.5, 0.5, "eh"), ("Eb3", 6, 1, "oo"), ("D3", 7, 1, "ah")]
CHANT_B = [("A3", 0, 0.5, "ah"), ("Bb3", 0.5, 0.5, "eh"), ("A3", 1, 0.5, "ah"), ("G3", 1.5, 0.5, "oh"),
           ("F3", 2, 1, "aw"), ("G3", 3, 0.5, "eh"), ("A3", 3.5, 0.5, "ah"),
           ("D3", 4, 1, "oo"), ("F3", 5, 1, "ah"), ("E3", 6, 1, "eh"), ("D3", 7, 1, "ah")]
CHANT_C = [("D4", 0, 2, "ah"), ("C4", 2, 1, "oh"), ("Bb3", 3, 1, "ah"),
           ("A3", 4, 2, "aw"), ("F3", 6, 1, "eh"), ("A3", 7, 1, "ah"),
           ("Eb4", 8, 2, "oo"), ("D4", 10, 1, "ah"), ("C4", 11, 1, "eh"),
           ("D4", 12, 2.5, "ah"), ("A3", 14.5, 1.5, "oo")]
# NEW soaring B-theme (D natural-minor, higher/wider than the chant) for the
# 'hero anthem' passage; a distinct second melody for contrast + recurrence.
B_THEME = [("A4", 0, 2), ("D5", 2, 1.5), ("C5", 3.5, 0.5), ("A4", 4, 2),
           ("F4", 6, 2), ("G4", 8, 1.5), ("A4", 9.5, 0.5), ("Bb4", 10, 2),
           ("A4", 12, 1), ("F4", 13, 1), ("D4", 14, 2)]
HERO_ROOT = ["D", "Bb", "F", "C"]          # brighter lift (borrows natural-minor E)
HERO_CH = {"D": ["D3", "F3", "A3"], "Bb": ["Bb2", "D3", "F3"],
           "F": ["F2", "A2", "C3"], "C": ["C3", "E3", "G3"]}

DRUM = Bus(TOTAL); SUB = Bus(TOTAL); MUS = Bus(TOTAL); CHOIR = Bus(TOTAL); PAL = Bus(TOTAL)
kick_times = []


def bt(bar, b=0.0):
    return bar * BAR + b * BEAT


# ---- improved chant (articulated, varied) --------------------------------
def chant_note(freq, dur, vowel, gain, glide_from=None):
    n = int(dur * SR); t = t_of(dur)
    f0 = np.full(n, freq)
    if glide_from:
        gl = int(min(n, 0.12 * SR)); f0[:gl] = np.linspace(glide_from, freq, gl)   # portamento
    vibr = 1 + 0.012 * np.sin(2 * np.pi * 5.2 * t) * np.clip((t - 0.18) / 0.25, 0, 1)
    cph = np.cumsum(f0 * vibr) / SR
    src = np.zeros(n)
    for k in range(1, 16):
        if freq * k > SR / 2 - 200:
            break
        src += (1.0 / k ** 1.2) * np.sin(2 * np.pi * k * cph)
    F1, F2, F3 = VOWELS.get(vowel, VOWELS["ah"])
    out = (1.0 * bp(src, F1 * 0.85, F1 * 1.15) + 0.6 * bp(src, F2 * 0.85, F2 * 1.15)
           + 0.3 * bp(src, F3 * 0.85, F3 * 1.15))
    out /= np.max(np.abs(out)) + 1e-9
    # consonant onset: a short filtered-noise articulation so syllables read as words
    cn = int(0.018 * SR); cons = np.zeros(n)
    cf = rng.choice([1400, 2600, 700, 4000])
    cons[:cn] = bp(rng.standard_normal(cn), cf * 0.7, cf * 1.3) * np.exp(-np.linspace(0, 1, cn) * 6) * 0.4
    env = adsr(n, 0.05, 0.15, 0.85, min(0.45, dur * 0.3))
    return lp(out * env + cons, 4300) * gain


def chant(phrase, phrase_bar, gain=0.42, octv=0, pan=0.5, bass=True, vary=False):
    prev = None
    for i, (nm, b, dur, vw) in enumerate(phrase):
        f = note(nm) * 2 ** octv
        if vary and i > 0 and rng.random() < 0.25:      # occasional ornament (optimal surprise)
            vw = rng.choice(list(VOWELS))
        gfrom = (note(prev) * 2 ** octv) if (vary and prev and rng.random() < 0.3) else None
        CHOIR.add(chant_note(f, dur * BEAT * 0.95, vw, gain, gfrom), bt(phrase_bar, b), 1.0, pan, 0.4)
        if bass:
            CHOIR.add(chant_note(f / 2, dur * BEAT * 0.95, vw, gain * 0.55), bt(phrase_bar, b), 1.0, pan, 0.35)
        prev = nm


# ---- NEW alien / custom noises -------------------------------------------
def metal_scrape(dur, gain=0.3):
    """Industrial resonant friction: noise through a wandering resonant band,
    ring-modulated by a low tone -> metallic beating. LP-tamed (not harsh)."""
    n = int(dur * SR); nz = rng.standard_normal(n)
    c = pink_walk(n, 700, 2800)
    out = np.zeros(n); seg = 16; w = n // seg
    for s in range(seg):
        sl = slice(s * w, (s + 1) * w if s < seg - 1 else n)
        fc = float(np.median(c[sl])); out[sl] = bp(nz, fc * 0.8, fc * 1.25)[sl]
    ring = 0.5 + 0.5 * np.sin(2 * np.pi * 47 * t_of(dur))
    return tilt(lp(out * ring, 4200), 1200, -5) * gain / (np.max(np.abs(out)) + 1e-9)


def ring_growl(freq, dur, gain=0.35):
    """Ring-modulated low growl: inharmonic sidebands = threat/roughness."""
    t = t_of(dur)
    car = np.sin(2 * np.pi * freq * t)
    mod = np.sin(2 * np.pi * freq * 1.414 * t)
    out = car * (0.5 + 0.5 * mod) + 0.3 * np.sin(2 * np.pi * freq * 2.7 * t) * mod
    env = adsr(len(t), 0.05, 0.2, 0.8, min(0.5, dur * 0.3))
    return lp(np.tanh(out * env * 1.2), 2500) * gain


def alien_zap(gain=0.4, dur=0.7, up=False):
    """Metallic pitch-swept zap (down = collapse, up = alarm). Gated, LP-tamed."""
    t = t_of(dur)
    f = (80 * 2 ** (t * 4.5)) if up else (2000 * 2 ** (-t * 4.5) + 55)
    ph = 2 * np.pi * np.cumsum(f) / SR
    metal = np.sin(ph) + 0.5 * np.sin(2.76 * ph) + 0.3 * np.sin(5.4 * ph)
    env = np.exp(-t * 3.5) * (1 - np.exp(-t * 300)) if not up else (t ** 1.5)
    return lp(metal / 1.8 * env, 5000) * gain


def glitch(dur, base=220, gain=0.3, rate=14):
    """Rhythmic stutter of a metallic tone -> mechanical malfunction texture."""
    n = int(dur * SR); out = np.zeros(n); gl = int(SR / rate)
    for i in range(0, n - gl, gl):
        if rng.random() < 0.7:
            f = base * rng.choice([1, 1, 1.5, 2, 0.5, 2.76])
            tg = np.arange(gl) / SR
            g = (np.sin(2 * np.pi * f * tg) + 0.4 * np.sin(2 * np.pi * f * 2.76 * tg)) * np.hanning(gl)
            out[i:i + gl] += g * rng.uniform(0.3, 1.0)
    return lp(out, 5000) * gain


# ---- cinematic accents (replace the squeaky zaps) ------------------------
def braam(gain=0.4, dur=1.8):
    t = t_of(dur); out = np.zeros(len(t))
    for f in [73.4, 73.9, 110.0, 146.8, 155.6]:      # D2 detuned + A2 + D3 + Eb3 cluster
        for k in range(1, 14):
            if f * k > SR / 2 - 200:
                break
            out += (1 / k ** 1.1) * np.sin(2 * np.pi * f * k * t + rng.uniform(0, 6))
    env = np.clip(t / 0.25, 0, 1) * np.exp(-np.maximum(0, t - 0.6) * 1.6)
    return lp(np.tanh(out / 6 * env * 1.3), 3200) * gain


def subdrop(gain=0.7, dur=1.4):
    t = t_of(dur)
    body = np.sin(2 * np.pi * np.cumsum(100 * np.exp(-t * 10) + 33) / SR) * np.exp(-t * 2.5)
    click = lp(rng.uniform(-1, 1, len(t)), 3500) * np.exp(-t * 80) * 0.35
    return lp(np.tanh((body + click) * 1.5), 400) * gain


def rev_swell(dur, gain=0.45):
    n = int(dur * SR); t = np.linspace(0, 1, n); nz = rng.standard_normal(n); out = np.zeros(n)
    cs = np.linspace(500, 7000, 10); w = n // 10
    for i, c in enumerate(cs):
        sl = slice(i * w, (i + 1) * w if i < 9 else n); out[sl] = lp(nz, c)[sl]
    out *= t ** 2; ce = int(0.02 * SR); out[-ce:] *= np.linspace(1, 0, ce)
    return out * gain


def anvil(gain=0.35, dur=1.4):
    t = t_of(dur); out = np.zeros(len(t)); base = 190
    for r, a, dc in [(1, 1, 3), (2.1, 0.6, 5), (3.4, 0.5, 7), (4.7, 0.35, 9), (6.3, 0.25, 12)]:
        out += a * np.exp(-t * dc) * np.sin(2 * np.pi * base * r * t + rng.uniform(0, 6))
    oa = int(0.002 * SR); out[:oa] *= np.linspace(0, 1, oa)
    return lp(out / 2.5, 4500) * gain


def gong(gain=0.4, dur=2.4):
    t = t_of(dur); out = np.zeros(len(t)); base = 70
    for _ in range(18):
        r = rng.uniform(1, 9)
        out += (1 / r) * np.exp(-t * rng.uniform(1.2, 3.5)) * np.sin(2 * np.pi * base * r * t + rng.uniform(0, 6))
    oa = int(0.004 * SR); out[:oa] *= np.linspace(0, 1, oa)
    return lp(out / 4 * (1 + 0.15 * np.sin(2 * np.pi * 3.3 * t)), 3800) * gain


def choir_stab(gain=0.4, dur=1.0):
    t = t_of(dur); n = len(t); src = np.zeros(n)
    for f in [146.8, 220, 293.7]:
        for k in range(1, 14):
            if f * k > SR / 2 - 200:
                break
            src += (1 / k ** 1.2) * np.sin(2 * np.pi * f * k * t)
    out = bp(src, 600, 1000) + 0.6 * bp(src, 1000, 1500) + 0.3 * bp(src, 2200, 2900)
    env = np.clip(t / 0.04, 0, 1) * np.exp(-t * 4)
    return lp(out / 3 * env, 4200) * gain


def dark_whoosh(dur=1.4, gain=0.45):
    n = int(dur * SR); t = np.linspace(0, 1, n); nz = rng.standard_normal(n); out = np.zeros(n)
    cs = np.linspace(6000, 300, 10); w = n // 10
    for i, c in enumerate(cs):
        sl = slice(i * w, (i + 1) * w if i < 9 else n); out[sl] = lp(nz, c)[sl]
    out *= (0.3 + 0.7 * np.sin(np.pi * t))
    return out * gain


def shards(dur=1.4, gain=0.4):
    n = int(dur * SR); L = np.zeros(n); R = np.zeros(n)
    for _ in range(60):
        gl = int(rng.uniform(0.03, 0.09) * SR); at = int(rng.uniform(0, max(1, n - gl - 1)))
        f = rng.uniform(400, 2600); tg = np.arange(gl) / SR
        g = np.sin(2 * np.pi * f * tg) * np.hanning(gl) * rng.uniform(0.2, 1)
        end = min(n, at + gl); ln = end - at; pan = rng.uniform(0, 1)
        L[at:end] += g[:ln] * np.sqrt(1 - pan); R[at:end] += g[:ln] * np.sqrt(pan)
    m = max(np.max(np.abs(L)), np.max(np.abs(R))) + 1e-9
    return lp(L, 4200) / m * gain, lp(R, 4200) / m * gain


def thunder(dur=2.4, gain=0.5):
    n = int(dur * SR); t = np.linspace(0, 1, n)

    def one(seed):
        r = np.random.default_rng(seed); nz = r.standard_normal(n)
        rum = lp(nz, 180) * (0.4 + 0.6 * np.sin(np.pi * t))
        sub = np.sin(2 * np.pi * 38 * np.arange(n) / SR) * np.exp(-t * 1.5) * 0.4
        crack = lp(r.uniform(-1, 1, n), 600) * np.exp(-t * 3) * 0.3
        return np.tanh((rum + sub + crack) * 1.3)
    a = one(int(dur * 100) + 1); b = one(int(dur * 100) + 2)
    ma = max(np.max(np.abs(a)), np.max(np.abs(b))) + 1e-9
    return a / ma * gain, b / ma * gain


# ---- gothic instruments --------------------------------------------------
def organ_tone(freq, dur, gain=0.3):
    t = t_of(dur); out = np.zeros(len(t))
    for r, a in [(1, 1.0), (2, 0.55), (3, 0.42), (4, 0.32), (5, 0.13), (6, 0.2), (8, 0.13)]:
        if freq * r > SR / 2 - 200:
            break
        out += a * np.sin(2 * np.pi * freq * r * t + rng.uniform(0, 6))
    out /= np.max(np.abs(out)) + 1e-9
    chiff = np.zeros(len(t)); ci = int(0.03 * SR)
    chiff[:ci] = lp(rng.uniform(-1, 1, ci), 4000) * np.exp(-np.linspace(0, 1, ci) * 6) * 0.06
    env = adsr(len(t), 0.08, 0.2, 0.92, min(0.5, dur * 0.25))
    return lp((out + chiff) * env, 5200) * gain


def war_horn(root, dur, bar, b=0.0, gain=0.4):
    fifth = {"D": "A", "Eb": "Bb", "C": "G"}[root]
    for nm in [root + "2", fifth + "2", root + "3"]:
        MUS.add(brass(note(nm), dur, gain), bt(bar, b), 1.0, 0.5, 0.2)


def cluster(names, dur_bars, bar, gain=0.24):
    for nm in names:
        MUS.add(organ_tone(note(nm), dur_bars * BAR, gain), bt(bar), 1.0, 0.5, 0.3)


def toll(bar, root=73.4, gain=0.5, b=0.0):
    PAL.add(revenant_bell(14, root, gain, seed=int(bar * 5 + b)), bt(bar, b), 1.0, 0.5, 0.45)


# ---- war-drum kit --------------------------------------------------------
def big_kick(gain=1.0):
    dur = 0.4; t = t_of(dur)
    body = np.sin(2 * np.pi * np.cumsum(160 * np.exp(-t * 30) + 46) / SR) * np.exp(-t * 5.5)
    click = lp(rng.uniform(-1, 1, len(t)), 5000) * np.exp(-t * 120) * 0.4
    return np.tanh((body + click) * 1.6) * gain


def taiko(freq=95, gain=0.9):
    dur = 0.5; t = t_of(dur); pitch = freq * (1 + 0.4 * np.exp(-t * 18))
    body = np.sin(2 * np.pi * np.cumsum(pitch) / SR) + 0.4 * np.sin(2 * np.pi * 2 * np.cumsum(pitch) / SR)
    noise = lp(rng.uniform(-1, 1, len(t)), 900) * np.exp(-t * 22) * 0.5
    return np.tanh((body * np.exp(-t * 5.5) + noise) * 1.3) * gain


def sub808(name, dur, gain=0.9):
    f = note(name); t = t_of(dur)
    body = np.sin(2 * np.pi * np.cumsum(f + f * 3 * np.exp(-t * 30)) / SR)
    return lp(np.tanh(body * (np.exp(-t * 2.0) * (1 - np.exp(-t * 200))) * 1.4), 130) * gain


def snare(gain=1.0):
    dur = 0.24; t = t_of(dur)
    tone = (np.sin(2 * np.pi * 190 * t) + np.sin(2 * np.pi * 270 * t)) * np.exp(-t * 24)
    noise = lp(hp(rng.uniform(-1, 1, len(t)), 1000), 8000) * np.exp(-t * 15)
    return np.tanh((0.5 * tone + 0.95 * noise) * 1.2) * gain


def crash(gain=0.5):
    dur = 1.5; t = t_of(dur)
    return lp(rng.uniform(-1, 1, len(t)), 8500) * np.exp(-t * 3.0) * gain


def riser(dur, gain=0.6):
    n = int(dur * SR); t = np.linspace(0, 1, n); nz = rng.uniform(-1, 1, n)
    out = np.zeros(n); cs = np.linspace(400, 8000, 10); w = n // 10
    for i, c in enumerate(cs):
        sl = slice(i * w, (i + 1) * w if i < 9 else n); out[sl] = lp(nz, c)[sl]
    fp = 200 * 2 ** (t * 3.5)
    return (out * t ** 2 + np.sin(2 * np.pi * np.cumsum(fp) / SR) * t ** 1.6 * 0.35) * gain


def snare_roll(bar_lo, bars, gain=0.5):
    divs = [4, 8, 8, 16, 16, 16]
    for bi in range(int(bars * 4)):
        div = divs[min(bi, len(divs) - 1)]
        for j in range(div):
            DRUM.add(snare(0.5) * 0.5, bt(bar_lo) + (bi + j / div) * BEAT,
                     gain * (0.4 + 0.6 * bi / (bars * 4)), 0.5, 0.1)


def war_drums(bar, energy=1.0, gallop=True, fill=False):
    DRUM.add(big_kick(0.95 * energy), bt(bar, 0), 1.0, 0.5, 0.05); kick_times.append(bt(bar, 0))
    DRUM.add(big_kick(0.7 * energy), bar * BAR + 10 * STEP, 1.0, 0.5, 0.05); kick_times.append(bar * BAR + 10 * STEP)
    steps = [0, 3, 4, 6, 7, 8, 11, 12, 14, 15] if gallop else [0, 4, 8, 12]
    for s in steps:
        acc = 1.0 if s % 4 == 0 else 0.6
        DRUM.add(taiko(95 if s % 8 < 4 else 78, 0.7 * acc * energy), bar * BAR + s * STEP, 1.0, 0.5 + 0.25 * np.sin(s), 0.08)
    DRUM.add(snare(0.8 * energy), bar * BAR + 8 * STEP, 1.0, 0.5, 0.12)
    if fill:
        for j, s in enumerate([12, 13, 14, 15]):
            DRUM.add(taiko(140 - j * 16, 0.8), bar * BAR + s * STEP, 1.0, 0.4 + 0.04 * j, 0.1)


def ostinato(bar, root, energy=1.0, variant=0):
    """variant 0 = relentless 16ths; 1 = gallop (medium-syncopation groove
    sweet-spot); 2 = straight 8ths with octave accents. Rotating per cycle =
    repetition-with-variation (avoids habituation)."""
    fifth = {"D": "A", "Eb": "Bb", "C": "G"}[root]
    if variant == 1:
        steps = [0, 3, 4, 6, 7, 8, 11, 12, 14, 15]
    elif variant == 2:
        steps = list(range(0, 16, 2))
    else:
        steps = list(range(16))
    for s in steps:
        octn = "4" if (variant == 2 and s % 8 == 0) else "3"
        nm = (root + octn) if s % 4 != 2 else (fifth + octn)
        MUS.add(strings_stac(note(nm), 0.14, (0.32 if s % 4 == 0 else 0.19) * energy),
                bar * BAR + s * STEP, 1.0, 0.5, 0.1)
    MUS.add(strings_stac(note(root + "2"), BEAT, 0.3 * energy), bt(bar, 0), 1.0, 0.5, 0.08)


def play_organ(start_bar, nbars, gain=0.22, octv=0):
    for b in range(nbars):
        for nm in CHORD[CYCLE_ROOT[b % 4]][1:4]:
            MUS.add(organ_tone(note(nm) * 2 ** octv, BAR * 0.99, gain), bt(start_bar + b), 1.0, 0.5, 0.3)


def play_sub(start_bar, nbars, gain=0.9):
    for b in range(nbars):
        SUB.add(sub808(SUBROOT[CYCLE_ROOT[b % 4]], BAR * 0.95, gain), bt(start_bar + b), 1.0, 0.5, 0.02)


def dread_riser(dur, gain=0.5):
    """Build tension WITHOUT the game-y charge-up sweep: airy filtered-noise
    swell + detuned low tones creeping up ~2 semitones (dread, not laser)."""
    n = int(dur * SR); t = np.linspace(0, 1, n)
    nz = rng.uniform(-1, 1, n); noise = np.zeros(n); cs = np.linspace(300, 7000, 10); w = n // 10
    for i, c in enumerate(cs):
        sl = slice(i * w, (i + 1) * w if i < 9 else n); noise[sl] = lp(nz, c)[sl]
    cluster = np.zeros(n)
    for base in [73.4, 110.0, 146.8]:
        for det in [-7, 0, 6]:
            f = base * 2 ** ((det + t * 200) / 1200.0)      # slow ~2-semitone creep
            cluster += np.sin(2 * np.pi * np.cumsum(f) / SR)
    return (noise * t ** 2 * 0.6 + lp(cluster / 9, 2500) * (0.2 + 0.8 * t ** 1.5)) * gain


def riser_toll(dur, gain=0.5):
    """Accelerating cathedral-bell tolls (one array). Gaps shrink but floor at
    0.12 s so the loop always advances/terminates."""
    n = int(dur * SR); out = np.zeros(n); t = 0.0; gap = 0.9
    while t < dur - 0.1:
        b = revenant_bell(min(2.2, dur - t + 1.5), 73.4, gain, seed=int(t * 97) + 1)
        i = int(t * SR); e = min(n, i + len(b)); out[i:e] += b[:e - i]
        gap = max(0.12, gap * 0.8); t += gap
    return out


def riser_ghost(dur, gain=0.5):
    """Ghost-choir swell (eerie vocal build)."""
    x = chorus_many(dur, NOMINAL, gain); t = np.linspace(0, 1, len(x))
    return x * t ** 1.4


def riser_roll(dur, gain=0.5):
    """Accelerating taiko roll (percussive build, no tone)."""
    n = int(dur * SR); out = np.zeros(n); divs = [2, 3, 4, 6, 8, 12, 16]; seg = dur / len(divs)
    for k, dv in enumerate(divs):
        for j in range(int(dv)):
            at = int((k * seg + j * seg / dv) * SR)
            h = taiko(90, 0.5 * (0.4 + 0.6 * k / len(divs)))
            e = min(n, at + len(h)); out[at:e] += h[:e - at]
    return out * gain


def pick_riser(kind, dur, gain=0.5):
    return {"dread": dread_riser, "toll": riser_toll, "ghost": riser_ghost,
            "roll": riser_roll}.get(kind, dread_riser)(dur, gain)


def build_bars(b0, nbars, kind="dread", horn=True):
    """Short build using a ROTATING riser type (variation across cycles)."""
    if kind != "roll":                          # 'roll' IS the percussive build
        snare_roll(b0, nbars, 0.45)
    DRUM.add(pick_riser(kind, nbars * BAR, 0.5), bt(b0), 1.0, 0.5, 0.22)
    DRUM.add(rev_swell(nbars * BAR, 0.34), bt(b0), 1.0, 0.5, 0.25)
    if horn:
        for b in range(b0, b0 + nbars):
            war_horn(CYCLE_ROOT[b % 4], BAR * 0.8, b, 0, 0.3)


def charge(b0, nbars, energy, chant_phrase=None, chant_oct=0, hit="braam",
           alien=True, ostv=0, counter=False):
    """A charge: war drums + ostinato(variant) + organ + sub; drop gets sub-drop
    + braam/anvil; anvils on fills; optional contrary-motion counter-melody."""
    DRUM.add(crash(0.55), bt(b0), 1.0, 0.5, 0.2); toll(b0, 73.4, 0.5)
    DRUM.add(subdrop(0.7), bt(b0), 1.0, 0.5, 0.08)
    if hit == "braam":
        PAL.add(braam(0.55), bt(b0), 1.0, 0.5, 0.3)
    elif hit == "anvil":
        PAL.add(anvil(0.5), bt(b0), 1.0, 0.5, 0.3)
    for b in range(b0, b0 + nbars):
        war_drums(b, energy, gallop=True, fill=(b % 4 == 3))
        ostinato(b, CYCLE_ROOT[b % 4], energy, variant=ostv)
        play_sub(b, 1, 0.95)
        if b % 4 == 3:
            PAL.add(anvil(0.3), bt(b, 3.5), 1.0, rng.uniform(0.35, 0.65), 0.25)
    play_organ(b0, nbars, 0.2, octv=0)
    if chant_phrase is not None:
        chant(chant_phrase, b0, 0.46, octv=chant_oct, vary=True)
    if counter:                                    # contrary-motion cello counter-line
        for j, nm in enumerate(["A3", "G3", "F3", "E3", "F3", "D3", "Eb3", "D3"]):
            MUS.add(strings_sus(note(nm), 2 * BEAT, 0.16), bt(b0 + j // 2, (j % 2) * 2), 1.0, 0.42, 0.2)
    if alien:
        PAL.add(ring_growl(50, nbars * BAR, 0.2), bt(b0), 1.0, 0.5, 0.2)


def creep_break(b0, nbars, chant_phrase=None):
    """Short creepy interlude between charges (no drums): gong + thunder +
    shards + ghost-choir + scrape."""
    dur = nbars * BAR
    PAL.add(chorus_many(dur, NOMINAL, 0.42), bt(b0), 1.0, 0.5, 0.4)
    PAL.add(metal_scrape(dur, 0.26), bt(b0), 1.0, 0.55, 0.3)
    PAL.add(gong(0.4), bt(b0), 1.0, 0.5, 0.4)                     # #5 GONG WASH
    tl, tr = thunder(dur, 0.4); PAL.add_st(tl, tr, bt(b0), 1.0, 0.3)   # #10 THUNDER
    sl, sr = shards(min(dur, 1.4), 0.28); PAL.add_st(sl, sr, bt(b0, 1.0), 1.0, 0.3)  # #7 SHARDS
    PAL.add(psithura(dur, 0.32), bt(b0), 1.0, 0.6, 0.15)
    toll(b0, PRIME, 0.4)
    # cohesion: a low organ pedal (D2+A2) sustains through the break so the
    # harmonic anchor never fully drops out between charges (no choppy gaps)
    for nm in ["D2", "A2"]:
        MUS.add(organ_tone(note(nm), dur, 0.13), bt(b0), 1.0, 0.5, 0.3)
    if chant_phrase is not None:
        chant(chant_phrase, b0, 0.34, octv=0, vary=True)


# eerie descending "sigh" motif unique to the Eye (ends on the leading-tone C#
# = unresolved dread). (note, start_beat, dur_beats, vowel)
EYE_MOTIF = [("A4", 0, 2, "oo"), ("G4", 2, 1, "ah"), ("F4", 3, 1, "eh"),
             ("E4", 4, 2, "oh"), ("D4", 6, 1.5, "ah"), ("C#4", 7.5, 2.5, "oo")]


def centerpiece(b0, nbars):
    """THE EYE (~30s), now a 4-EVENT mini-arc (dead-calm contrast before the
    payoff). i) void/held-breath; ii) an EXPOSED eerie solo 'sigh' motif on
    uncanny voice + inhaling bell; iii) the ghost-choir AWAKENS (fusion->
    fragmentation) with a chromatic dread descent + heartbeat creeping in;
    iv) accelerating tolls + dread riser LAUNCH into the climax."""
    dur = nbars * BAR
    # --- continuous dread bed (whole Eye) ---
    PAL.add(groundwater(dur, 30.0, 24.0, 0.4), bt(b0), 1.0, 0.5, 0.25)     # sinking-vowel gesture
    PAL.add(mantle(dur, 0.28), bt(b0), 1.0, 0.5, 0.2)
    PAL.add(missing_room(dur, 97.5, 0.34), bt(b0), 1.0, 0.5, 0.42)
    PAL.add(metal_scrape(dur, 0.14), bt(b0), 1.0, 0.62, 0.3)

    # i) VOID / held breath (bars 0-2): near silence + one distant toll + ticks
    toll(b0, 73.4, 0.5)
    cl, cr = cribra(3 * BAR, 0.4); PAL.add_st(cl, cr, bt(b0), 0.8, 0.35)

    # ii) EXPOSED SOLO (bars 2-6): eerie 'sigh' motif on uncanny voice + inhaling bell
    for nm, bb, d, vw in EYE_MOTIF:
        f = note(nm)
        CHOIR.add(chant_note(f, d * BEAT * 0.95, vw, 0.5), bt(b0 + 2, bb), 1.0, 0.5, 0.5)   # exposed, wet
    PAL.add(cold_bell_larynx(6, QUINT, 0.34), bt(b0 + 2), 1.0, 0.5, 0.45)                    # inhaling bell doubles it
    PAL.add(psithura(6 * BAR, 0.3), bt(b0 + 2), 1.0, 0.62, 0.15)

    # iii) THE AWAKENING (bars 6-10): ghost-choir swells to fragmentation, chromatic
    #      dread descent on strings, ring-growl rises, heartbeat creeps in, gong
    PAL.add(chorus_many(6 * BAR, NOMINAL, 0.5), bt(b0 + 6), 1.0, 0.5, 0.4)
    PAL.add(gong(0.5), bt(b0 + 6), 1.0, 0.5, 0.45)
    tl, tr = thunder(6 * BAR, 0.35); PAL.add_st(tl, tr, bt(b0 + 6), 1.0, 0.3)
    PAL.add(ring_growl(46, 6 * BAR, 0.24), bt(b0 + 6), 1.0, 0.5, 0.2)
    PAL.add(stairwell(6 * BAR, 0.3), bt(b0 + 6), 1.0, 0.5, 0.3)              # Shepard descent
    for j, nm in enumerate(["A3", "G#3", "G3", "F#3", "F3", "E3"]):          # chromatic dread descent
        MUS.add(strings_sus(note(nm), 1.4 * BEAT, 0.16), bt(b0 + 6 + j * 0.66), 1.0, 0.5, 0.3)
    for k in range(4):                                                       # heartbeat creeping in
        DRUM.add(subdrop(0.3 + 0.08 * k, 0.8), bt(b0 + 7 + k, 0), 1.0, 0.5, 0.06)
    # the augmented theme (choir + organ) underneath the awakening
    for nm, bb, dur2, vw in CHANT_C[:7]:
        f = note(nm)
        CHOIR.add(chant_note(f, dur2 * 2 * BEAT * 0.95, vw, 0.3), bt(b0 + 6, bb), 1.0, 0.5, 0.45)
        MUS.add(organ_tone(f, dur2 * 2 * BEAT * 0.9, 0.12), bt(b0 + 6, bb), 1.0, 0.5, 0.34)

    # iv) LAUNCH (bars 10-12): dark cluster + accelerating tolls + dread riser + roll
    cluster(["D3", "Eb3", "A3", "Bb3"], 3, b0 + 9, 0.22)
    for j, tb in enumerate([0, 1.2, 2.1, 2.7, 3.1]):                         # accelerating tolls
        toll(b0 + 10, 73.4, 0.4 + 0.05 * j, b=tb)
    DRUM.add(dread_riser(2 * BAR, 0.5), bt(b0 + 10), 1.0, 0.5, 0.24)
    DRUM.add(rev_swell(2 * BAR, 0.5), bt(b0 + 10), 1.0, 0.5, 0.25)
    snare_roll(b0 + 10, 2, 0.5)
    sl2, sr2 = shards(1.6, 0.3); PAL.add_st(sl2, sr2, bt(b0 + 11), 1.0, 0.3)


# ----------------------------- NEW passages (variety) ---------------------
def organ_toccata(b0, nbars):
    """Gothic pipe-organ toccata interlude: fast arpeggiated figuration over a
    pedal, no drums -> a distinct cathedral texture between charges."""
    PAL.add(missing_room(nbars * BAR, 97.5, 0.3), bt(b0), 1.0, 0.5, 0.4)
    toll(b0, 73.4, 0.45)
    for b in range(b0, b0 + nbars):
        r = CYCLE_ROOT[b % 4]
        MUS.add(organ_tone(note(r + "2"), BAR * 0.99, 0.22), bt(b), 1.0, 0.5, 0.3)   # pedal
        tones = CHORD[r][2:] + CHORD[r][2:][::-1]                                     # up-down
        for s in range(8):
            nm = tones[s % len(tones)]
            MUS.add(organ_tone(note(nm) * 2, BEAT * 0.5, 0.13), bt(b, s * 0.5),
                    1.0, 0.5 + 0.25 * np.sin(s * 1.3), 0.32)
    PAL.add(chorus_many(nbars * BAR, NOMINAL, 0.2), bt(b0), 1.0, 0.5, 0.4)


def hero_passage(b0, nbars):
    """Half-time 'hero anthem': the soaring B-theme on brass+strings+choir over a
    brighter Dm-Bb-F-C lift; grand, emotional contrast to the relentless charges."""
    for b in range(b0, b0 + nbars):
        DRUM.add(big_kick(0.9), bt(b, 0), 1.0, 0.5, 0.06); kick_times.append(bt(b, 0))
        DRUM.add(snare(0.8), bt(b, 2), 1.0, 0.5, 0.12)                 # half-time backbeat
        DRUM.add(taiko(80, 0.4), bt(b, 1), 1.0, 0.5, 0.08); DRUM.add(taiko(80, 0.4), bt(b, 3), 1.0, 0.5, 0.08)
        play_sub(b, 1, 0.85)
        r = HERO_ROOT[b % 4]
        for nm in HERO_CH[r]:
            MUS.add(strings_sus(note(nm), BAR * 0.98, 0.2), bt(b), 1.0, 0.5, 0.22)
            MUS.add(organ_tone(note(nm), BAR * 0.98, 0.11), bt(b), 1.0, 0.5, 0.3)
    for ph in range(b0, b0 + nbars, 4):
        for nm, bb, d in B_THEME:
            MUS.add(brass(note(nm), d * BEAT * 0.95, 0.28), bt(ph, bb), 1.0, 0.55, 0.2)
            MUS.add(strings_sus(note(nm), d * BEAT * 0.95, 0.18), bt(ph, bb), 1.0, 0.45, 0.2)
        for nm in ["D4", "F4", "A4"]:
            CHOIR.add(choir_pad(note(nm), 4 * BAR, 0.16), bt(ph), 1.0, 0.5, 0.32)


def march_feature(b0, nbars):
    """Drum-forward taiko march (call-and-response toms + horn stabs), building
    intensity into the climax. Percussion is the lead here."""
    for b in range(b0, b0 + nbars):
        DRUM.add(big_kick(0.95), bt(b, 0), 1.0, 0.5, 0.06); kick_times.append(bt(b, 0))
        for bp2 in [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5]:
            acc = 1.0 if bp2 % 1 == 0 else 0.55
            DRUM.add(taiko(95 if bp2 % 2 < 1 else 78, 0.62 * acc), bt(b, bp2),
                     1.0, 0.5 + 0.2 * np.sin(bp2 * 3), 0.08)
        if b % 2 == 1:                                                 # tom fill (response)
            for j, bp2 in enumerate([3, 3.25, 3.5, 3.75]):
                DRUM.add(taiko(150 - j * 16, 0.7), bt(b, bp2), 1.0, 0.4 + 0.04 * j, 0.1)
        play_sub(b, 1, 0.9)
        for bp2 in (0, 3):                                             # horn stabs
            war_horn(CYCLE_ROOT[b % 4], 0.4, b, bp2, 0.26)
    PAL.add(ring_growl(50, nbars * BAR, 0.2), bt(b0), 1.0, 0.5, 0.2)
    snare_roll(b0 + nbars - 1, 1, 0.5)


print("building GRAVEWATER — CRUSADE V ...")

# ============ ARRANGEMENT — fast cycles -> EYE centerpiece -> climax (72 bars) ============
# §0 CATHEDRAL INTRO (0-3)
for nm in ["D2", "A2", "D3", "A3"]:
    MUS.add(organ_tone(note(nm), 4 * BAR, 0.22), bt(0), 1.0, 0.5, 0.32)
PAL.add(missing_room(10, 97.5, 0.4), 0, 1.0, 0.5, 0.42)
PAL.add(groundwater(10, 36.7, 36.7, 0.4), 0, 1.0, 0.5, 0.22)
PAL.add(gong(0.35), 0.5, 1.0, 0.5, 0.4)
toll(0, 73.4, 0.55)
chant(CHANT_B[:5], 2, 0.32, octv=0)
# CALLBACK: faintly foreshadow the Eye's 'sigh' motif in the intro (plants the
# hook so its full statement in the Eye + outro lands as recognition)
for nm, bb, d, vw in EYE_MOTIF[:4]:
    CHOIR.add(chant_note(note(nm), d * BEAT * 0.95, vw, 0.16), bt(2, bb), 1.0, 0.5, 0.5)

# CYCLE 1 (4-11)
build_bars(4, 2, kind="dread")
charge(6, 6, 1.0, chant_phrase=CHANT_A, chant_oct=0, hit="braam", ostv=0)

# §ORGAN TOCCATA interlude (12-15) — NEW gothic solo texture, no drums
organ_toccata(12, 4)

# CYCLE 2 (16-23)
build_bars(16, 2, kind="toll")
charge(18, 6, 1.08, chant_phrase=CHANT_B, chant_oct=0, hit="anvil", ostv=1)

# §HERO ANTHEM (24-31) — NEW half-time B-theme lift, grand contrast
hero_passage(24, 8)

# CYCLE 3 (32-39)
build_bars(32, 2, kind="roll")
charge(34, 6, 1.12, chant_phrase=None, hit="braam", alien=True, ostv=2)
for b in range(34, 40, 2):
    war_horn(CYCLE_ROOT[b % 4], 0.5, b, 0, 0.3)

# §THE EYE — eerie centerpiece (40-51 ≈ 100-130 s)
centerpiece(40, 12)

# §MARCH FEATURE (52-55) — NEW drum-forward taiko march charging into the climax
march_feature(52, 4)

# §CLIMAX (56-63): chant C + B-theme + choir + horns; peak ~bar 58 (~145s)
charge(56, 8, 1.26, chant_phrase=CHANT_C, chant_oct=1, hit="braam", ostv=1, counter=True)
chant(CHANT_C, 56, 0.32, octv=0)
for ph in (56, 60):                                          # B-theme rides the climax too
    for nm, bb, d in B_THEME:
        MUS.add(brass(note(nm), d * BEAT * 0.9, 0.26), bt(ph, bb), 1.0, 0.55, 0.2)
for nm in CHORD["D"][2:]:
    CHOIR.add(choir_pad(note(nm) * 2, 8 * BAR, 0.22), bt(56), 1.0, 0.5, 0.32)
for nm in ["D3", "Ab3"]:                                     # tritone dread stab
    MUS.add(brass(note(nm), 0.7, 0.3), bt(58), 1.0, 0.5, 0.2)
PAL.add(choir_stab(0.4), bt(58), 1.0, 0.5, 0.3)

# §COLLAPSE (64-65): sub-drop + dark whoosh
DRUM.add(subdrop(0.7), bt(64), 1.0, 0.5, 0.08)
DRUM.add(dark_whoosh(2 * BAR, 0.4), bt(64), 1.0, 0.5, 0.2)
PAL.add(groundwater(6, 36.7, 30.0, 0.4), bt(64), 1.0, 0.5, 0.25)
PAL.add(chorus_many(6, NOMINAL, 0.38), bt(64), 1.0, 0.5, 0.4)
toll(64, PRIME, 0.4)

# §FINAL CHARGE (66-77): biggest, chant C + B-theme + counter-melody
build_bars(65, 1, kind="ghost")
charge(66, 12, 1.28, chant_phrase=CHANT_C, chant_oct=1, hit="braam", ostv=1, counter=True)
for ph in (66, 72):
    chant(CHANT_B, ph, 0.36, octv=0, vary=True)
    for nm, bb, d in B_THEME:                                # B-theme reprised over the final
        MUS.add(brass(note(nm) * 2, d * BEAT * 0.9, 0.24), bt(ph, bb), 1.0, 0.58, 0.2)
for nm in CHORD["D"][2:]:
    CHOIR.add(choir_pad(note(nm) * 2, 12 * BAR, 0.2), bt(66), 1.0, 0.5, 0.32)

# §REQUIEM OUTRO (78-87): organ fades, lone chant, sigh-motif reprise, caught breath
for nm in ["D2", "A2", "D3", "F3"]:
    MUS.add(organ_tone(note(nm), 10 * BAR, 0.2), bt(78), 1.0, 0.5, 0.34)
PAL.add(groundwater(24, 36.7, 28.0, 0.4), bt(78), 1.0, 0.5, 0.25)
PAL.add(mantle(24, 0.24), bt(78), 1.0, 0.5, 0.2)
PAL.add(gong(0.4), bt(80), 1.0, 0.5, 0.45)
chant(CHANT_A, 79, 0.34, octv=0, vary=True)
for nm, bb, d, vw in EYE_MOTIF:                              # CALLBACK / peak-end
    CHOIR.add(chant_note(note(nm), d * BEAT * 0.95, vw, 0.34), bt(82, bb), 1.0, 0.5, 0.5)
PAL.add(cold_bell_larynx(6, QUINT, 0.3), bt(82), 1.0, 0.5, 0.45)
toll(80, 73.4, 0.5); toll(85, 55.0, 0.5)
PAL.add(pleura(18, 0.5, caught=True), bt(83), 1.0, 0.5, 0.15)


# ==================== MIX / MASTER ====================
def sc_env(n, times, depth, rel=0.14):
    env = np.ones(n); a = int(0.004 * SR); r = int(rel * SR)
    duck = np.concatenate([np.linspace(1, 1 - depth, a),
                           1 - depth + depth * (1 - np.exp(-np.linspace(0, 5, r)))])
    for kt in times:
        i = int(kt * SR); j = min(n, i + len(duck))
        if i < n:
            env[i:j] = np.minimum(env[i:j], duck[:j - i])
    return env


def loudness(n):
    # intro -> cycle1 -> TOCCATA -> cycle2 -> HERO -> cycle3 -> EYE -> MARCH ->
    # climax -> collapse -> final -> requiem
    pts = [(0, -19), (10, -13), (20, -6),                 # intro + charge 1
           (30, -11), (38, -11),                          # organ toccata (no drums, mid)
           (45, -10), (52, -5), (60, -8),                 # charge 2
           (62, -7), (70, -5), (80, -9),                  # HERO anthem (grand, half-time)
           (88, -5), (98, -8),                            # charge 3
           (102, -18), (110, -16), (120, -11), (127, -6),  # THE EYE (void -> launch)
           (132, -6), (139, -4),                          # march feature (building)
           (146, 0), (158, -4),                           # CLIMAX peak
           (162, -13),                                    # collapse
           (168, -3), (192, -5),                          # final charge
           (198, -11), (220, -42)]                        # requiem fade
    ts = np.array([p[0] for p in pts]); db = np.array([p[1] for p in pts])
    return 10 ** (np.interp(np.arange(n) / SR, ts, db) / 20.0)


def _loudness_unused(n):
    pts = [(0, -19)]
    ts = np.array([p[0] for p in pts]); db = np.array([p[1] for p in pts])
    return 10 ** (np.interp(np.arange(n) / SR, ts, db) / 20.0)


def master():
    print("  mixing ...")
    n = DRUM.n
    scH = sc_env(n, kick_times, 0.82)[None, :]
    scP = sc_env(n, kick_times, 0.4)[None, :]
    scC = sc_env(n, kick_times, 0.18)[None, :]
    dry = DRUM.dry + SUB.dry * scH + MUS.dry * scP + CHOIR.dry * scC + PAL.dry * scP
    wet = DRUM.wet + SUB.wet + MUS.wet + CHOIR.wet + PAL.wet
    irL, irR = make_ir(1, rt60=5.0), make_ir(2, rt60=5.0)
    wetr = np.stack([fftconvolve(wet[0], irL)[:n], fftconvolve(wet[1], irR)[:n]])
    mix = (dry + 1.0 * wetr) * loudness(n)
    out = []
    for ch in range(2):
        x = mix[ch]
        x = hp(x, 30, 4)
        x = x - (1 - 10 ** (-2.5 / 20)) * bp(x, 2800, 4200)
        x = tilt(x, 1300, -4.5)
        x = lp(x, 15500, 4)
        x = osat(x, 1.14)
        x = np.tanh(x * 0.9) / 0.9
        out.append(x)
    L, R = out
    m = max(np.max(np.abs(L)), np.max(np.abs(R))) + 1e-9
    L, R = L / m * 0.94, R / m * 0.94
    fi = int(0.6 * SR); fo = int(6.0 * SR)
    for x in (L, R):
        x[:fi] *= np.linspace(0, 1, fi); x[-fo:] *= np.linspace(1, 0, fo) ** 1.4
    return np.stack([L, R])


def write_wav(path, st):
    import wave
    data = (np.clip(st.T, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(data.tobytes())


if __name__ == "__main__":
    import sys
    st = master()
    out = sys.argv[1] if len(sys.argv) > 1 else "crusade.wav"
    write_wav(out, st)
    print(f"wrote {out}  ({st.shape[1] / SR:.1f}s, stereo {SR}Hz)")
