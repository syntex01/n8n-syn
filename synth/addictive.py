"""
RESIDUA — addiction-first rework (implements the workflow build spec).

The apex RESIDUA read as "boring / not addicting" because its withheld-tonic
design deliberately WITHHOLDS resolution — anti-replay. This rework inverts the
priority order to ADDICTING > exciting > alien/chilling, per the multi-agent
build spec derived from REPORT.md / research-sources.md:

 - THE HOOK up front by ~0:04: arch rise D-F-A -> ascending m6 LEAP into a held
   F5 belt -> b2 sigh (Eb +12c, the alien fingerprint) -> HARD tonic resolve.
   Foreground bright lead voice; choir only a quiet doubler. Recurs every 2 bars.
 - GROOVE that never drops out: half-time (140 BPM), medium-syncopation kick,
   backbeat snare, persistent 8th+16th hats, kick-bass interlock, driving reese.
 - Frequent PAYOFFS: tonic lands every 2 bars; 5 section payoffs every 13-27 s.
 - MESA loudness (flat high floor, one big drop as the peak) + 3-tier sidechain
   so kick/pad/lead breathe without a dynamic-range hole.
 - Alien demoted from structural (RESIDUA's beatless "Eye", withheld ending) to
   surface texture: timbre, the b2 leap, counter-hooks (vox_glottis, revenant
   bells, cribra ticks). No beatless section anywhere.

Built on the crusade2 foundation (Bus / sc_env / master() dual-reverb + de-harsh
+ dark-tilt + limiter chain), not dsp3 — dsp3 is a mix toolkit with no
instruments; crusade2 already mirrors its production chain and carries the full
orchestral + invented-alien palette. D Phrygian, 140 BPM half-time, 84 bars ~2:28.
Passes synth/qa.py §10 addiction gates (onset floor, beat continuity, hook-early,
mesa 3-8 dB, loudness floor, dark centroid, no-harsh, tonic resolve).
"""
import numpy as np
from scipy.signal import fftconvolve

import dsp2
from orch import (note, t_of, lp, hp, bp, adsr, strings_sus, strings_stac, brass, choir_pad,
                  _additive, vib)
from thing import (Bus, SR, tilt, osat, pink_walk, make_ir,
                   groundwater, mantle, revenant_bell, cold_bell_larynx,
                   chorus_many, psithura, cribra, stairwell, missing_room,
                   pleura, vox_glottis, PRIME, NOMINAL, QUINT)

rng = np.random.default_rng(40000)
BPM = 140.0                    # addiction rework: half-time feel
BEAT = 60.0 / BPM
BAR = 4 * BEAT
STEP = BEAT / 4.0
NBARS = 84
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
LEAD = Bus(TOTAL)              # foreground earworm hook bus
kick_times = []
pump_times = []               # steady 1/4 pump for the pad sidechain


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
    """Short build: snare roll + riser + REVERSE-SWELL air riser into the cut."""
    snare_roll(b0, nbars, 0.5)
    DRUM.add(riser(nbars * BAR, 0.5), bt(b0), 1.0, 0.5, 0.2)
    DRUM.add(rev_swell(nbars * BAR, 0.42), bt(b0), 1.0, 0.5, 0.25)   # #3 REVERSE SWELL
    if horn:
        for b in range(b0, b0 + nbars):
            war_horn(CYCLE_ROOT[b % 4], BAR * 0.8, b, 0, 0.3)


def charge(b0, nbars, energy, chant_phrase=None, chant_oct=0, hit="braam", alien=True):
    """A charge: full war drums + ostinato + organ + sub; the DROP gets a
    sub-drop + a big impact (braam/anvil); metal anvils on fills; ring-growl bed."""
    DRUM.add(crash(0.55), bt(b0), 1.0, 0.5, 0.2); toll(b0, 73.4, 0.5)
    DRUM.add(subdrop(0.7), bt(b0), 1.0, 0.5, 0.08)                # #2 SUB DROP on the drop
    if hit == "braam":
        PAL.add(braam(0.55), bt(b0), 1.0, 0.5, 0.3)              # #1 BRAAM impact
    elif hit == "anvil":
        PAL.add(anvil(0.5), bt(b0), 1.0, 0.5, 0.3)               # #4 ANVIL CLANG
    for b in range(b0, b0 + nbars):
        war_drums(b, energy, gallop=True, fill=(b % 4 == 3))
        ostinato(b, CYCLE_ROOT[b % 4], energy)
        play_sub(b, 1, 0.95)
        if b % 4 == 3:                                            # #4 anvil on fills
            PAL.add(anvil(0.3), bt(b, 3.5), 1.0, rng.uniform(0.35, 0.65), 0.25)
    play_organ(b0, nbars, 0.2, octv=0)
    if chant_phrase is not None:
        chant(chant_phrase, b0, 0.46, octv=chant_oct, vary=True)
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
    if chant_phrase is not None:
        chant(chant_phrase, b0, 0.34, octv=0, vary=True)


def centerpiece(b0, nbars):
    """THE EYE (~30s): eerie, ominous suspended middle. Beat gone. A slow,
    augmented statement of the chant theme floats over dread drone, gong,
    distant thunder, fragmenting ghost-choir and a Shepard descent; a reverse-
    swell + roll at the end launches the climax. Dead-calm contrast before the
    biggest payoff (dynamic-contrast / peak-end research)."""
    dur = nbars * BAR
    # dread bed
    PAL.add(groundwater(dur, 30.0, 24.0, 0.42), bt(b0), 1.0, 0.5, 0.25)   # the sinking-vowel gesture
    PAL.add(mantle(dur, 0.3), bt(b0), 1.0, 0.5, 0.2)
    PAL.add(missing_room(dur, 97.5, 0.34), bt(b0), 1.0, 0.5, 0.42)
    PAL.add(chorus_many(dur, NOMINAL, 0.4), bt(b0), 1.0, 0.5, 0.4)        # fusion->fragmentation
    PAL.add(stairwell(dur, 0.3), bt(b0), 1.0, 0.5, 0.3)                   # Shepard dread descent
    tl, tr = thunder(dur, 0.35); PAL.add_st(tl, tr, bt(b0), 1.0, 0.3)
    PAL.add(gong(0.45), bt(b0), 1.0, 0.5, 0.45)                           # struck at the threshold
    PAL.add(ring_growl(46, dur, 0.2), bt(b0 + 4), 1.0, 0.5, 0.2)
    PAL.add(metal_scrape(dur, 0.16), bt(b0), 1.0, 0.6, 0.3)
    # slow, solemn, AUGMENTED theme (doubled note durations) on choir + organ
    slow = [(nm, bb * 2, dur2 * 2.0, vw) for nm, bb, dur2, vw in CHANT_C]
    for nm, bb, d, vw in slow:
        f = note(nm)
        CHOIR.add(chant_note(f, d * BEAT * 0.95, vw, 0.4), bt(b0, bb), 1.0, 0.5, 0.45)
        CHOIR.add(chant_note(f / 2, d * BEAT * 0.95, vw, 0.26), bt(b0, bb), 1.0, 0.5, 0.4)
        MUS.add(organ_tone(f, d * BEAT * 0.9, 0.14), bt(b0, bb), 1.0, 0.5, 0.34)
    # a couple of tolls + a single dark cluster swell for menace
    toll(b0, 73.4, 0.5); toll(b0 + nbars - 3, PRIME, 0.45)
    cluster(["D3", "Eb3", "A3"], 4, b0 + nbars - 4, 0.2)
    # launch: reverse-swell + accelerating roll over the last 2 bars
    DRUM.add(rev_swell(2 * BAR, 0.5), bt(b0 + nbars - 2), 1.0, 0.5, 0.25)
    snare_roll(b0 + nbars - 2, 2, 0.5)
    tl2, tr2 = shards(1.6, 0.3); PAL.add_st(tl2, tr2, bt(b0 + nbars - 1), 1.0, 0.3)


# ==================== ADDICTION REWORK: hook, groove, bass ====================
# THE HOOK "D-Phrygian Sigh": (note, start_step, len_steps), 2-bar/32-step core.
# Arch rise (D-F-A) -> ascending m6 LEAP into held F5 belt -> b2 sigh (Eb+12c) ->
# hard tonic resolve. Same rhythm every loop (sticky); ends on D (no open loop).
HOOK = [("D4", 0, 3), ("F4", 3, 3), ("A4", 6, 2), ("F5", 8, 8),
        ("Eb5", 16, 3), ("D5", 19, 3), ("A4", 22, 2), ("F4", 24, 4), ("D4", 28, 4)]
RESP = [("F6", 28, 2), ("Eb6", 30, 2)]           # high ghost answer (biggest choruses only)


def lead(freq, dur, gain=0.6, bright=5200, detune=8, drive=1.12):
    """Bright FOREGROUND earworm voice: detuned band-limited additive saw +
    delayed vibrato -> formant presence -> fast attack, SUSTAIN HELD -> osat grit."""
    n = int(dur * SR); f = vib(freq, n, rate=5.4, depth_cents=7, delay=0.16)
    out = sum(_additive(f * 2 ** (d / 1200.0), 40, 1.0) for d in (-detune, 0, detune)) / 3
    out = 1.0 * bp(out, 300, 1400) + 0.6 * out
    env = adsr(n, 0.008, 0.06, 0.9, min(0.14, dur * 0.3))
    return lp(osat(out * env, drive), bright) * gain


def reese(name, dur, gain=0.5, cut=(300, 650), drive=1.3):
    """Driving dark bass: 3 detuned saws in octave 2, pink-walk filter wobble."""
    f = note(name); n = int(dur * SR); t = t_of(dur); saw = np.zeros(n)
    for d in (-11, 0, 11):
        fk = f * 2 ** (d / 1200.0); cph = 2 * np.pi * fk * t
        for k in range(1, 30):
            if fk * k > SR / 2 - 200:
                break
            saw += (1.0 / k) * np.sin(k * cph)
    saw /= 3
    fc = pink_walk(n, cut[0], cut[1]); seg = 12; out = np.zeros(n); w = n // seg
    for s in range(seg):
        sl = slice(s * w, (s + 1) * w if s < seg - 1 else n)
        out[sl] = lp(saw, float(np.median(fc[sl])))[sl]
    env = adsr(n, 0.006, 0.05, 0.95, min(0.08, dur * 0.3))
    return osat(out * env, drive) * gain


def hat(gain=0.32, open_=False):
    d = 0.18 if open_ else 0.05; t = t_of(d)
    # darker/rounder hat (lp 10k) so a persistent 16th layer never gets sizzly/harsh
    return lp(hp(rng.standard_normal(len(t)), 6500) * np.exp(-t * (12 if open_ else 45)), 10000) * gain


def _hz(nm, octv=0):
    f = note(nm) * 2 ** octv
    if nm.startswith("Eb") or nm.startswith("C#"):     # microtonal lean on the sigh/leading tone
        f *= 2 ** (12 / 1200.0)
    return f


def play_hook(bar, octv=0, gain=0.6, doubler=False, resp=False, cadence=False,
              bell=True, ticks=True):
    """Write the hook to LEAD (foreground). cadence=True swaps the Eb5 sigh for
    C#5->D5 (the hoarded raised-7th V->i). Rings a bell on the F5 peak."""
    notes = list(HOOK)
    if cadence:
        notes = [("C#5" if nm == "Eb5" else nm, s, l) for (nm, s, l) in notes]
    for nm, s, ln in notes:
        f = _hz(nm, octv)
        dur = ln * STEP * 0.98
        at = bt(bar) + s * STEP
        LEAD.add(lead(f, dur, gain), at, 1.0, 0.5, 0.16)
        if doubler and ln >= 3:                        # choir doubler 4 dB under, held notes only
            CHOIR.add(chant_note(f, dur, "ah", gain * 0.4), at, 1.0, 0.5, 0.3)
        if bell and nm == "F5":                        # bell rings the belt peak
            PAL.add(revenant_bell(1.6, note("F3"), 0.32, seed=bar), at, 1.0, 0.6, 0.4)
    if resp:
        for nm, s, ln in RESP:
            LEAD.add(lead(_hz(nm, 0), ln * STEP, gain * 0.4, bright=6000), bt(bar) + s * STEP, 1.0, 0.7, 0.3)
    if ticks:
        for s in (5, 13, 21, 27):
            cl, cr = cribra(0.12, 0.3)
            PAL.add_st(cl, cr, bt(bar) + s * STEP, 0.5, 0.2)


def play_hook_pluck(bar, octv=0, gain=0.4, apex=False):
    """Quiet octave-down pluck version of the hook for verses (keeps it present)."""
    notes = list(HOOK)
    if apex:                                           # verse-2 variation: bigger leap A4->C5
        notes = [("C5", 8, 8) if nm == "F5" else (nm, s, l) for (nm, s, l) in notes]
    for nm, s, ln in notes:
        f = _hz(nm, octv - 1)
        dur = max(0.14, ln * STEP * 0.9)
        LEAD.add(lead(f, dur, gain, bright=3600, drive=1.05), bt(bar) + s * STEP, 1.0, 0.42, 0.14)


def groove_bar(bar, energy=1.0, density="chorus"):
    """Half-time groove, medium-syncopation sweet spot; pulse NEVER absent."""
    ks = [0, 6, 10]
    if density in ("chorus", "drop"):
        ks = ks + [14]
    if density == "drop":
        ks = sorted(set(ks + [3]))
    for s in ks:
        DRUM.add(big_kick(0.95 * energy), bt(bar) + s * STEP, 1.0, 0.5, 0.06)
        kick_times.append(bt(bar) + s * STEP)
    DRUM.add(snare(0.9 * energy), bt(bar) + 8 * STEP, 1.0, 0.5, 0.12)
    if density in ("chorus", "drop"):
        DRUM.add(snare(0.4 * energy), bt(bar) + 12 * STEP, 1.0, 0.5, 0.12)
    # persistent hats: 8ths (accented) + a quieter 16th layer -> onset density
    # never drops out, so nothing ever feels sparse/boring.
    for s in range(0, 16, 2):
        DRUM.add(hat(0.34 * energy, open_=(s == 14)), bt(bar) + s * STEP, 1.0,
                 0.5 + 0.18 * np.sin(s), 0.05)
    sixteenths = range(1, 16, 2) if density in ("chorus", "drop") else range(1, 16, 4)
    for s in sixteenths:
        DRUM.add(hat(0.16 * energy), bt(bar) + s * STEP, 1.0, 0.5 - 0.2 * np.sin(s), 0.04)
    for s in (0, 8):                                   # dark body weight
        DRUM.add(taiko(90, 0.5 * energy), bt(bar) + s * STEP, 1.0, 0.5, 0.08)
    for s in (7, 15):                                  # alien ghost ticks (novelty, keeps ear engaged)
        cl, cr = cribra(0.1, 0.28 * energy); DRUM.add_st(cl, cr, bt(bar) + s * STEP, 0.6, 0.06)
    for beat in range(4):                              # feed the steady pad pump
        pump_times.append(bt(bar) + beat * BEAT)


def bass_bar(bar, root, energy=1.0, reese_on=True):
    """sub808 on kick steps (kick-bass interlock) + driving reese 8ths."""
    for s in (0, 6, 10):
        SUB.add(sub808(SUBROOT[root], 0.5, 0.75 * energy), bt(bar) + s * STEP, 1.0, 0.5, 0.02)
    if reese_on:
        for s in range(0, 16, 2):
            SUB.add(reese(root + "2", STEP * 2 * 0.95, 0.28 * energy), bt(bar) + s * STEP, 1.0, 0.5, 0.03)


GROOVE_BARS = []


def groove_span(b0, b1, energy=1.0, density="chorus", reese_on=True):
    for bar in range(b0, b1):
        groove_bar(bar, energy, density)
        bass_bar(bar, CYCLE_ROOT[bar % 4], energy, reese_on)
        GROOVE_BARS.append(bar)


print("building RESIDUA (addiction rework) ...")

# ==== ARRANGEMENT (84 bars, 140 BPM half-time) — hook & groove FORWARD ====
def organ_bed(b0, nbars, gain=0.16, octv=0):
    for b in range(b0, b0 + nbars):
        for nm in CHORD[CYCLE_ROOT[b % 4]][1:4]:
            MUS.add(organ_tone(note(nm) * 2 ** octv, BAR * 0.99, gain), bt(b), 1.0, 0.5, 0.28)


def choir_bed(b0, nbars, gain=0.14, octv=1):
    for nm in ["D4", "F4", "A4"]:
        CHOIR.add(choir_pad(note(nm) * 2 ** (octv - 1), nbars * BAR, gain), bt(b0), 1.0, 0.5, 0.35)


# §A COLD OPEN (0-3, 0:00-0:07): the HOOK, clean & foreground, from the top
PAL.add(groundwater(4 * BAR, 36.7, 36.7, 0.28), bt(0), 1.0, 0.5, 0.2)   # phantom-D color bed
play_hook(0, gain=0.62, bell=True, ticks=True)
play_hook(2, gain=0.64, doubler=True)
for bar in (2, 3):                                                     # pulse ramps in by ~0:04
    groove_bar(bar, 0.75, density="verse"); bass_bar(bar, CYCLE_ROOT[bar % 4], 0.7, reese_on=False)
    GROOVE_BARS.append(bar)

# §B CHORUS 1 (4-11, 0:07-0:20): full groove + hook every 2 bars
groove_span(4, 12, energy=1.0, density="chorus")
organ_bed(4, 8, 0.16); choir_bed(4, 8, 0.12)
for ph in (4, 6, 8, 10):
    play_hook(ph, gain=0.62, doubler=(ph in (4, 8)))

# §C VERSE 1 (12-19, 0:20-0:34): pulse kept, hook as octave-down pluck, alien counter-hook
groove_span(12, 20, energy=0.9, density="verse")
organ_bed(12, 8, 0.16)
choir_bed(12, 8, 0.09)                                                # steady floor through the transition
PAL.add(groundwater(8 * BAR, 36.7, 36.7, 0.24), bt(12), 1.0, 0.5, 0.25)
PAL.add(psithura(8 * BAR, 0.2), bt(12), 1.0, 0.62, 0.15)
for ph in (12, 14, 16, 18):
    play_hook_pluck(ph, gain=0.5)
for (nm, b) in [("A4", 4), ("G4", 8), ("F4", 12)]:                    # vox_glottis counter-hook answer
    MUS.add(vox_glottis(2 * BEAT, note(nm), 0.24), bt(13, b), 1.0, 0.62, 0.2)
DRUM.add(riser(2 * BAR, 0.4), bt(18), 1.0, 0.5, 0.2)                  # build 18-19

# §D CHORUS 2 (20-27, 0:34-0:48): PAYOFF #2 — full + high RESP answer + brighter bed
DRUM.add(subdrop(0.6), bt(20), 1.0, 0.5, 0.08); PAL.add(braam(0.4), bt(20), 1.0, 0.5, 0.3)
groove_span(20, 28, energy=1.05, density="chorus")
organ_bed(20, 8, 0.18); choir_bed(20, 8, 0.14)
for ph in (20, 22, 24, 26):
    play_hook(ph, gain=0.64, doubler=True, resp=(ph in (20, 24)))

# §E VERSE 2 (28-35, 0:48-1:02): darker, hook-pluck APEX variation, alien beds
groove_span(28, 36, energy=0.9, density="verse")
organ_bed(28, 8, 0.16)
choir_bed(28, 8, 0.09)                                                # steady floor
PAL.add(ring_growl(46, 8 * BAR, 0.16), bt(28), 1.0, 0.5, 0.2)
PAL.add(metal_scrape(8 * BAR, 0.14), bt(28), 1.0, 0.55, 0.25)
for ph in (28, 30, 32, 34):
    play_hook_pluck(ph, gain=0.5, apex=(ph == 32))
DRUM.add(riser(2 * BAR, 0.45), bt(34), 1.0, 0.5, 0.2)                 # build 34-35

# §F FRISSON LIFT (36-43, 1:02-1:15): THE chill — peak +15c + octave choir + shards
groove_span(36, 44, energy=1.05, density="chorus")
organ_bed(36, 8, 0.17); choir_bed(36, 8, 0.16, octv=2)
for ph in (36, 38, 40, 42):
    play_hook(ph, gain=0.66, doubler=True, resp=True)
    CHOIR.add(choir_pad(note("F5"), 8 * STEP, 0.2), bt(ph) + 8 * STEP, 1.0, 0.5, 0.4)   # octave choir on the belt
    sl, sr = shards(1.2, 0.22); PAL.add_st(sl, sr, bt(ph) + 8 * STEP, 1.0, 0.35)         # shimmer

# §G PRE-DROP (44-47, 1:15-1:21): accel build, filter open, 1-bar kick cut at 47
groove_span(44, 47, energy=1.0, density="chorus")
DRUM.add(riser(3 * BAR, 0.55), bt(44), 1.0, 0.5, 0.25)
DRUM.add(rev_swell(3 * BAR, 0.4), bt(44), 1.0, 0.5, 0.25)
snare_roll(45, 2, 0.5)
for s in range(0, 16, 2):                                            # bar 47: hats+sub keep the pulse, NO kick
    DRUM.add(hat(0.28), bt(47) + s * STEP, 1.0, 0.5, 0.05)
bass_bar(47, CYCLE_ROOT[47 % 4], 0.9, reese_on=True)
DRUM.add(dark_whoosh(BAR, 0.4), bt(47), 1.0, 0.5, 0.2)

# §H BIG DROP (48-63, 1:21-1:48): PAYOFF #4 — max groove, octave-up hook, harmony
PAL.add(braam(0.5), bt(48), 1.0, 0.5, 0.3); DRUM.add(subdrop(0.7), bt(48), 1.0, 0.5, 0.08)
DRUM.add(crash(0.5), bt(48), 1.0, 0.5, 0.2)
groove_span(48, 64, energy=1.2, density="drop")
organ_bed(48, 16, 0.18, octv=-1); choir_bed(48, 16, 0.16, octv=2)
for ph in range(48, 64, 2):
    play_hook(ph, octv=1, gain=0.6, doubler=True, resp=(ph % 4 == 0))     # octave-up belt
    play_hook(ph, octv=0, gain=0.3)                                       # doubled low
for b in range(48, 64, 2):                                                # war-horn 3rd-below harmony
    war_horn(CYCLE_ROOT[b % 4], 0.5, b, 0, 0.28)
DRUM.add(crash(0.5), bt(56), 1.0, 0.5, 0.2); PAL.add(braam(0.4), bt(56), 1.0, 0.5, 0.3)  # second-wind slam

# §I VERSE 3 / COMEDOWN (64-71, 1:48-2:02): layers pulled, groove+hook kept
groove_span(64, 72, energy=0.9, density="verse")
organ_bed(64, 8, 0.16)
choir_bed(64, 8, 0.09)                                                # steady floor
PAL.add(groundwater(8 * BAR, 36.7, 36.7, 0.22), bt(64), 1.0, 0.5, 0.25)
for ph in (64, 66, 68, 70):
    play_hook_pluck(ph, gain=0.5)
DRUM.add(riser(2 * BAR, 0.5), bt(70), 1.0, 0.5, 0.2)                  # build 70-71

# §J DROP REPRISE + CADENCE (72-79, 2:02-2:15): PAYOFF #5, the hoarded C#->D V->i
PAL.add(braam(0.5), bt(72), 1.0, 0.5, 0.3); DRUM.add(crash(0.5), bt(72), 1.0, 0.5, 0.2)
groove_span(72, 80, energy=1.18, density="drop")
organ_bed(72, 8, 0.18, octv=-1); choir_bed(72, 8, 0.16, octv=2)
for ph in (72, 74, 76):
    play_hook(ph, octv=1, gain=0.6, doubler=True, resp=True)
play_hook(78, octv=1, gain=0.62, doubler=True, cadence=True)         # C#5->D5 raised-7th resolve
for nm in ["A2", "C#4", "E4"]:                                       # A-major V swell -> D
    MUS.add(war_horn("D", 1.5, 78, 12, 0.0) if False else brass(note(nm), 1.5, 0.3), bt(78) + 12 * STEP, 1.0, 0.5, 0.25)
for nm in ["D3", "F3", "A3"]:                                        # resolve to D at bar 79 downbeat... (into outro)
    MUS.add(brass(note(nm), 1.5, 0.3), bt(79) + 12 * STEP, 1.0, 0.5, 0.25)

# §K OUTRO (80-83, 2:15-2:28): thin drums, final hook resolves HARD to D, held; loop
groove_span(80, 82, energy=0.6, density="verse")
organ_bed(80, 4, 0.14)
play_hook(80, gain=0.6, doubler=True)
# final: hold D (hard resolve, no open loop) + toll + sink + caught breath
LEAD.add(lead(note("D4"), 3.0, 0.55), bt(82), 1.0, 0.5, 0.25)
LEAD.add(lead(note("D3"), 3.0, 0.4), bt(82), 1.0, 0.5, 0.25)
toll(82, 73.4, 0.5)
PAL.add(groundwater(4 * BAR, 36.7, 36.7, 0.3), bt(80), 1.0, 0.5, 0.3)
PAL.add(pleura(3 * BAR, 0.4, caught=True), bt(81), 1.0, 0.5, 0.15)


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
    # MESA: high flat floor (no boring troughs); frequent small peaks at each
    # payoff; only cold-open ramp + final fade go low.
    pts = [(0, -8), (6.9, -2.8),                     # cold-open ramp -> chorus1
           (20.6, -3.0), (32, -3.0),                 # verse1 flat floor
           (34.3, -2.6),                             # chorus2
           (48, -3.0), (59, -3.0),                   # verse2 flat floor
           (61.7, -1.9),                             # frisson lift peak
           (75.4, -2.4),                             # pre-drop
           (82.3, -1.7), (100, -2.0),                # big-drop plateau
           (109.7, -3.0), (121, -3.0),               # verse3 flat floor
           (123.4, -2.2), (135, -2.2),               # reprise
           (137.1, -3.4), (144, -9), (148, -40)]     # outro resolve + fade
    ts = np.array([p[0] for p in pts]); db = np.array([p[1] for p in pts])
    return 10 ** (np.interp(np.arange(n) / SR, ts, db) / 20.0)


def master():
    print("  mixing ...")
    n = DRUM.n
    scB = sc_env(n, kick_times, 0.80, rel=0.12)[None, :]     # bass <-> kick interlock
    scPad = sc_env(n, pump_times or kick_times, 0.45, rel=0.20)[None, :]   # pads breathe on 1/4
    scLead = sc_env(n, kick_times, 0.15, rel=0.10)[None, :]  # hook barely ducks -> stays forward
    dry = (DRUM.dry + SUB.dry * scB + MUS.dry * scPad + CHOIR.dry * scPad
           + PAL.dry * scPad + LEAD.dry * scLead)
    wet = DRUM.wet + SUB.wet + MUS.wet + CHOIR.wet + PAL.wet + LEAD.wet
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
    out = sys.argv[1] if len(sys.argv) > 1 else "addictive.wav"
    write_wav(out, st)
    print(f"wrote {out}  ({st.shape[1] / SR:.1f}s, stereo {SR}Hz)")
