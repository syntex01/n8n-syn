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
NBARS = 72
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


def ostinato(bar, root, energy=1.0):
    fifth = {"D": "A", "Eb": "Bb", "C": "G"}[root]
    for s in range(16):
        nm = (root + "3") if s % 4 != 2 else (fifth + "3")
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


def build_bars(b0, nbars, horn=True):
    """A short 2-bar build: snare roll + riser + optional horn + alien accent."""
    snare_roll(b0, nbars, 0.5)
    DRUM.add(riser(nbars * BAR, 0.6), bt(b0), 1.0, 0.5, 0.2)
    if horn:
        for b in range(b0, b0 + nbars):
            war_horn(CYCLE_ROOT[b % 4], BAR * 0.8, b, 0, 0.3)
    PAL.add(alien_zap(0.35, up=True), bt(b0 + nbars, -0.5 * STEP), 1.0, 0.5, 0.25)


def charge(b0, nbars, energy, chant_phrase=None, chant_oct=0, alien=True):
    """A charge: full war drums + ostinato + organ + sub, optional chant + alien accents."""
    DRUM.add(crash(0.55), bt(b0), 1.0, 0.5, 0.2); toll(b0, 73.4, 0.5)
    for b in range(b0, b0 + nbars):
        war_drums(b, energy, gallop=True, fill=(b % 4 == 3))
        ostinato(b, CYCLE_ROOT[b % 4], energy)
        play_sub(b, 1, 0.95)
    play_organ(b0, nbars, 0.2, octv=0)
    if chant_phrase is not None:
        chant(chant_phrase, b0, 0.46, octv=chant_oct, vary=True)
    if alien:
        PAL.add(ring_growl(55, nbars * BAR, 0.22), bt(b0), 1.0, 0.5, 0.2)
        for k in range(nbars // 2):
            PAL.add(alien_zap(0.28), bt(b0 + 2 * k + 1, rng.uniform(0, 3)), 1.0, rng.uniform(0.3, 0.7), 0.3)


def creep_break(b0, nbars, chant_phrase=None):
    """Short creepy/alien interlude between charges (no drums)."""
    PAL.add(chorus_many(nbars * BAR, NOMINAL, 0.42), bt(b0), 1.0, 0.5, 0.4)
    PAL.add(metal_scrape(nbars * BAR, 0.28), bt(b0), 1.0, 0.55, 0.3)
    PAL.add(glitch(nbars * BAR, 220, 0.22), bt(b0), 1.0, 0.45, 0.25)
    PAL.add(psithura(nbars * BAR, 0.34), bt(b0), 1.0, 0.6, 0.15)
    toll(b0, PRIME, 0.4)
    if chant_phrase is not None:
        chant(chant_phrase, b0, 0.34, octv=0, vary=True)


print("building GRAVEWATER — CRUSADE ...")

# ==================== ARRANGEMENT — FAST CYCLES (72 bars) ====================
# §0 CATHEDRAL INTRO (0-3): organ swell, toll, alien bed, one chant-B fragment
for nm in ["D2", "A2", "D3", "A3"]:
    MUS.add(organ_tone(note(nm), 4 * BAR, 0.22), bt(0), 1.0, 0.5, 0.32)
PAL.add(missing_room(10, 97.5, 0.4), 0, 1.0, 0.5, 0.42)
PAL.add(groundwater(10, 36.7, 36.7, 0.4), 0, 1.0, 0.5, 0.22)
PAL.add(metal_scrape(8, 0.24), 1.0, 1.0, 0.6, 0.3)
toll(0, 73.4, 0.55)
chant(CHANT_B[:5], 2, 0.32, octv=0)

# Fast cycles: 2-bar build -> 6-bar charge, with 2-bar creep breaks. Chant varied
# per cycle and given a rest in cycle 3 (variety, not "everywhere").
build_bars(4, 2)
charge(6, 6, 1.0, chant_phrase=CHANT_A, chant_oct=0)          # cycle 1  (chant A)
creep_break(12, 2, chant_phrase=None)

build_bars(14, 2)
charge(16, 6, 1.08, chant_phrase=CHANT_B, chant_oct=0)        # cycle 2  (chant B, urgent)
creep_break(22, 2, chant_phrase=CHANT_A[:4])

build_bars(24, 2)
charge(26, 6, 1.12, chant_phrase=None, alien=True)            # cycle 3  (chant RESTS; alien-forward)
PAL.add(ring_growl(48, 6 * BAR, 0.26), bt(26), 1.0, 0.5, 0.2)
for b in range(26, 32, 2):
    war_horn(CYCLE_ROOT[b % 4], 0.5, b, 0, 0.3)
creep_break(32, 2, chant_phrase=None)

# §CLIMAX cycle (34-49): longer charge, chant C + choir, golden peak ~bar 44 (~112s)
build_bars(34, 2)
charge(36, 10, 1.22, chant_phrase=CHANT_C, chant_oct=1)       # chant C, up an octave
chant(CHANT_C, 36, 0.34, octv=0)                              # + octave-below layer
for nm in CHORD["D"][2:]:
    CHOIR.add(choir_pad(note(nm) * 2, 8 * BAR, 0.22), bt(36), 1.0, 0.5, 0.32)
for b in range(36, 46, 2):
    war_horn(CYCLE_ROOT[b % 4], 0.6, b, 0, 0.34)
for nm in ["D3", "Ab3"]:                                       # tritone dread stab at apex
    MUS.add(brass(note(nm), 0.7, 0.3), bt(44), 1.0, 0.5, 0.2)
PAL.add(alien_zap(0.4), bt(43, 3), 1.0, 0.5, 0.3)

# §COLLAPSE (46-49 overlaps end of climax): alien collapse
creep_break(46, 4, chant_phrase=CHANT_A[:4])
PAL.add(alien_zap(0.45, dur=1.2), bt(46), 1.0, 0.5, 0.3)
PAL.add(groundwater(10, 36.7, 30.0, 0.4), bt(46), 1.0, 0.5, 0.25)

# §FINAL CHARGE (50-63): biggest, chant C + B, relentless
build_bars(49, 1)
charge(50, 14, 1.25, chant_phrase=CHANT_C, chant_oct=1)
for ph in (50, 58):
    chant(CHANT_B, ph, 0.36, octv=0, vary=True)
    for b in range(ph, ph + 6, 2):
        war_horn(CYCLE_ROOT[b % 4], 0.6, b, 0, 0.34)
for nm in CHORD["D"][2:]:
    CHOIR.add(choir_pad(note(nm) * 2, 14 * BAR, 0.2), bt(50), 1.0, 0.5, 0.32)

# §REQUIEM OUTRO (64-71): organ fades, lone chant, toll, sink, caught breath
for nm in ["D2", "A2", "D3", "F3"]:
    MUS.add(organ_tone(note(nm), 8 * BAR, 0.2), bt(64), 1.0, 0.5, 0.34)
PAL.add(groundwater(20, 36.7, 28.0, 0.4), bt(64), 1.0, 0.5, 0.25)
PAL.add(mantle(20, 0.24), bt(64), 1.0, 0.5, 0.2)
PAL.add(metal_scrape(16, 0.18), bt(64), 1.0, 0.55, 0.35)
chant(CHANT_A, 65, 0.34, octv=0, vary=True)
toll(66, 73.4, 0.5); toll(69, 55.0, 0.5)
PAL.add(pleura(18, 0.5, caught=True), bt(67), 1.0, 0.5, 0.15)


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
    # faster cycles -> more frequent build/drop swings in the curve
    pts = [(0, -19), (10, -15), (20, -6), (30, -12), (40, -6), (50, -12), (60, -5),
           (72, -11), (90, -5), (112, -4), (120, -13), (128, -5), (160, -12), (184, -40)]
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
