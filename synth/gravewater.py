"""
"GRAVEWATER PULSE" — implements synth/SPEC3.md.

A catchy, production-ready dark-neoclassical piece: orchestral lead (piano,
strings, pizz, harp, brass, choir, timpani) + a modern beat (kick, clap, hats,
808 sub, sidechain) with the invented dark palette from "The Thing That Almost
Breathes" woven in as background/accents. D minor, 84 BPM, 3:03, golden-section
peak. Every choice traces to the spec's research/craft tags.

Buses are frequency-slotted so "a lot happens but it fits"; the palette sits
6-10 dB under the lead, dark-tilted and reverb-far ("behind glass").
"""
import numpy as np
from scipy.signal import fftconvolve

from orch import (note, t_of, lp, hp, bp, adsr, strings_sus, strings_stac,
                  pizz, harp, piano, brass, choir_pad, timpani)
from thing import (Bus, SR, tilt, osat, pink_walk, make_ir,
                   groundwater, mantle, revenant_bell, cold_bell_larynx,
                   chorus_many, psithura, cribra, stairwell, missing_room,
                   pleura, PRIME, NOMINAL, QUINT)

rng = np.random.default_rng(23)
BPM = 84.0
BEAT = 60.0 / BPM               # 0.7143
BAR = 4 * BEAT                  # 2.8571
STEP = BEAT / 4.0               # 16th
TOTAL = 64 * BAR + 3            # ~186

# ---- harmony: Dm - Bb - F - Am7 (axis minor vamp)
CYCLE = [
    ["A1", "D3", "F3", "A3", "D4"],     # Dm
    ["A#1", "D3", "F3", "A#3"],         # Bb
    ["F1", "C3", "F3", "A3"],           # F
    ["A1", "E3", "G3", "C4", "A4"],     # Am7
]
ROOTS = ["D1", "A#1", "F1", "A1"]

# ---- hook (D minor): signature ascending m6 A4->F5, arch, ends on the 5th
HOOK = [
    ("A4", 0, 1.5), ("D5", 1.5, 0.5), ("F5", 2.0, 0.5), ("E5", 2.5, 1.5),
    ("D5", 4, 1), ("F5", 5, 0.5), ("E5", 5.5, 0.5), ("D5", 6, 1), ("C5", 7, 0.5), ("D5", 7.5, 0.5),
    ("A4", 8, 1.5), ("C5", 9.5, 0.5), ("D5", 10, 1), ("A4", 11, 1),
    ("G4", 12, 0.5), ("A4", 12.5, 0.5), ("C5", 13, 1), ("A4", 14, 2),
]
COUNTER = [("F3", 0, 2), ("E3", 2, 2), ("D3", 4, 2), ("F3", 6, 2),
           ("C3", 8, 2), ("A3", 10, 2), ("E3", 12, 2), ("G3", 14, 2)]

# ---- buses (frequency-slotted; separate for per-group sidechain)
DRUM = Bus(TOTAL); SUB = Bus(TOTAL); ORCH = Bus(TOTAL)
MEL = Bus(TOTAL); PAL = Bus(TOTAL)
kick_times = []


def beat_at(bar, b=0.0):
    return bar * BAR + b * BEAT


# ---- beat kit (warm, band-limited; controlled highs) --------------------
def kick(gain=1.0):
    dur = 0.34; t = t_of(dur)
    pitch = 150 * np.exp(-t * 34) + 50
    body = np.sin(2 * np.pi * np.cumsum(pitch) / SR) * np.exp(-t * 6.5)
    click = lp(rng.uniform(-1, 1, len(t)), 5500) * np.exp(-t * 130) * 0.35
    return np.tanh((body + click) * 1.5) * gain


def kick808(name, dur, gain=0.9):
    f = note(name); t = t_of(dur)
    pitch = f + (f * 3) * np.exp(-t * 30)          # short pitch transient
    body = np.sin(2 * np.pi * np.cumsum(pitch) / SR)
    env = np.exp(-t * 1.8) * (1 - np.exp(-t * 200))
    return lp(np.tanh(body * env * 1.4), 120) * gain


def clap(gain=1.0):
    dur = 0.3; t = t_of(dur); n = len(t)
    noise = lp(hp(rng.uniform(-1, 1, n), 1100), 7500)
    out = np.zeros(n)
    for off, g in [(0, 1), (0.009, 0.9), (0.018, 0.8)]:
        i = int(off * SR); e = np.zeros(n); e[i:] = np.exp(-np.linspace(0, 1, n - i) * 42)
        out += g * noise * e
    return (out + noise * np.exp(-np.linspace(0, 1, n) * 12) * 0.4) * gain


def hat(gain=0.4, open_=False):
    dur = 0.09 if open_ else 0.045; t = t_of(dur)
    nz = bp(rng.uniform(-1, 1, len(t)), 4200, 8000)
    return nz * np.exp(-t * (7 if open_ else 30)) * gain


def crash(gain=0.5):
    dur = 1.5; t = t_of(dur)
    return lp(rng.uniform(-1, 1, len(t)), 8500) * np.exp(-t * 3.0) * gain


def riser(dur, gain=0.6):
    n = int(dur * SR); t = np.linspace(0, 1, n)
    bands = 10; nz = rng.uniform(-1, 1, n); out = np.zeros(n); cs = np.linspace(400, 8000, bands); w = n // bands
    for i, c in enumerate(cs):
        sl = slice(i * w, (i + 1) * w if i < bands - 1 else n); out[sl] = lp(nz, c)[sl]
    fp = 200 * 2 ** (t * 3.5); tonal = np.sin(2 * np.pi * np.cumsum(fp) / SR) * (t ** 1.6) * 0.35
    return (out * t ** 2 + tonal) * gain


def snare_roll(bar_lo, bars, gain=0.5):
    divs = [4, 4, 8, 8, 16, 16, 16, 16]
    for bi in range(int(bars * 4)):
        div = divs[min(bi, len(divs) - 1)]
        for j in range(div):
            tt = beat_at(bar_lo) + (bi + j / div) * BEAT
            g = gain * (0.5 + 0.5 * bi / (bars * 4))
            DRUM.add(clap(0.5) * 0.6, tt, g, 0.5, 0.12)


# ---- placement helpers ---------------------------------------------------
def play_mel(fn, phrase_bar, gain, notes=HOOK, octv=0, pan=0.5, send=0.14, bus=MEL, upto=None):
    for nm, bt, dur in notes:
        if upto is not None and bt >= upto:
            continue
        f = note(nm) * 2 ** octv
        bus.add(fn(f, dur * BEAT * 0.98, gain), beat_at(phrase_bar, bt), 1.0, pan, send)


def play_prog(fn, start_bar, nbars, gain, lowskip=1, pan=0.5, send=0.18, bus=ORCH, hpf=None):
    for b in range(nbars):
        chord = CYCLE[b % 4]
        for nm in chord[lowskip:]:
            sig = fn(note(nm), BAR * 0.98, gain)
            if hpf:
                sig = hp(sig, hpf)
            bus.add(sig, beat_at(start_bar + b), 1.0, pan, send)


def play_808(start_bar, nbars, gain=0.9):
    for b in range(nbars):
        f = kick808(ROOTS[b % 4], BAR * 0.95, gain)
        SUB.add(f, beat_at(start_bar + b), 1.0, 0.5, 0.02)


def play_beat(bar, energy=1.0, dbl_hat=False, fill=False, halftime=False):
    DRUM.add(kick(0.95 * energy), beat_at(bar, 0), 1.0, 0.5, 0.05); kick_times.append(beat_at(bar, 0))
    if not halftime:
        for s in (6, 10):
            DRUM.add(kick(0.7 * energy), bar * BAR + s * STEP, 1.0, 0.5, 0.05); kick_times.append(bar * BAR + s * STEP)
    claps = [12] if halftime else [4, 12]
    for s in claps:
        DRUM.add(clap(0.85 * energy), bar * BAR + s * STEP, 1.0, 0.5, 0.14)
    steps = range(0, 16, 1) if dbl_hat else range(0, 16, 2)
    for s in steps:
        DRUM.add(hat(0.16 * energy, open_=(s in (6, 14))), bar * BAR + s * STEP, 1.0,
                 0.5 + 0.18 * np.sin(s), 0.05)
    if fill:
        for j, s in enumerate([12, 13, 14, 15]):
            DRUM.add(timpani(120 - j * 8, 0.2, 0.6), bar * BAR + s * STEP, 1.0, 0.5, 0.1)


print("building GRAVEWATER PULSE ...")

# ============================== ARRANGEMENT (64 bars) ==============================
# §1 PROLOGUE (0-7): incomplete piano hook, groundwater D1 bed, missing room, ticks
PAL.add(groundwater(20, 36.7, 36.7, 0.5), 0, 1.0, 0.5, 0.22)
PAL.add(missing_room(20, 97.5, 0.32), 0, 1.0, 0.5, 0.4)
cl, cr = cribra(20, 0.4); PAL.add_st(cl, cr, 0, 0.7, 0.3)
play_mel(piano, 0, 0.5, octv=0, upto=2.0, send=0.2)       # cell 1 only, incomplete
play_mel(piano, 4, 0.45, octv=0, upto=2.0, send=0.2)

# §2 THEME A (8-15): full hook strings+piano, harp arps, pizz pulse, timpani, no drums
PAL.add(mantle(23, 0.26), 8, 1.0, 0.5, 0.2)
PAL.add(chorus_many(23, NOMINAL, 0.32), 8, 1.0, 0.5, 0.4)
for ph in (8, 12):
    play_mel(strings_sus, ph, 0.42, octv=0, send=0.16)
    play_mel(piano, ph, 0.4, octv=0, pan=0.45, send=0.14)
play_prog(strings_sus, 8, 8, 0.22, lowskip=1, send=0.2)
for b in range(8, 16):                                    # harp arps + pizz pulse
    chord = CYCLE[b % 4]
    for j, nm in enumerate(chord[1:]):
        MEL.add(harp(note(nm) * 2, 1.2, 0.28), bar_h := beat_at(b, j * 0.75), 1.0, 0.6, 0.2)
    for s in (0, 4, 8, 12):
        ORCH.add(pizz(note(chord[0]) * 2, 0.4, 0.3), b * BAR + s * STEP, 1.0, 0.4, 0.12)
    DRUM.add(timpani(note(chord[0]) * 1, 0.5, 0.35), beat_at(b), 1.0, 0.5, 0.1)

# §3 BUILD 1 (16-19): snare roll accel + riser + brass swell; stairwell descent; gap
play_prog(strings_sus, 16, 4, 0.28, lowskip=1, send=0.2)
for b in range(16, 20):
    ORCH.add(brass(note(CYCLE[b % 4][1]), BAR, 0.3), beat_at(b), 1.0, 0.5, 0.2)
snare_roll(16, 3.5, 0.5)
DRUM.add(riser(4 * BAR, 0.6), beat_at(16), 1.0, 0.5, 0.2)
PAL.add(stairwell(4 * BAR, 0.3), beat_at(16), 1.0, 0.5, 0.3)
PAL.add(cold_bell_larynx(6, NOMINAL, 0.35), beat_at(18.5), 1.0, 0.5, 0.4)
# (1-beat silence gap: nothing scheduled bar 19 beat 3-4)

# §4 DROP 1 / CHORUS (20-35): beat + 808 + hook strings/brass + pizz counter + palette
PAL.add(groundwater(46, 55, 55, 0.4), beat_at(20), 1.0, 0.5, 0.18)   # A1 dominant floor
PAL.add(chorus_many(46, NOMINAL, 0.28), beat_at(20), 1.0, 0.5, 0.4)
DRUM.add(crash(0.5), beat_at(20), 1.0, 0.5, 0.2)
PAL.add(revenant_bell(10, PRIME, 0.5, seed=20), beat_at(20), 1.0, 0.55, 0.45)
for b in range(20, 36):
    play_beat(b, energy=1.0, dbl_hat=False, fill=(b % 8 == 7))
    play_808(b, 1, 0.9)
    play_prog(strings_sus, b, 1, 0.2, lowskip=1, send=0.18, hpf=115)
for ph in (20, 24, 28, 32):
    play_mel(strings_sus, ph, 0.5, octv=0, send=0.14)
    play_mel(brass, ph, 0.32, octv=0, pan=0.55, send=0.16)
    play_mel(pizz, ph, 0.3, notes=COUNTER, pan=0.4, send=0.12)

# §5 CHORUS 2 / PEAK (36-43): octave-up hook + choir augmentation + crash; peak bar40
DRUM.add(crash(0.55), beat_at(36), 1.0, 0.5, 0.2)
for b in range(36, 44):
    play_beat(b, energy=1.12, dbl_hat=True, fill=(b % 8 == 7))
    play_808(b, 1, 0.95)
    play_prog(strings_sus, b, 1, 0.22, lowskip=1, send=0.18, hpf=115)
for ph in (36, 40):
    play_mel(strings_sus, ph, 0.52, octv=1, send=0.14)   # octave-up
    play_mel(strings_sus, ph, 0.3, octv=0, send=0.14)
    play_mel(brass, ph, 0.34, octv=0, pan=0.55, send=0.16)
    play_mel(choir_pad, ph, 0.3, octv=0, pan=0.5, send=0.3)   # choir sings hook
    play_mel(pizz, ph, 0.3, notes=COUNTER, pan=0.4, send=0.12)
DRUM.add(crash(0.5), beat_at(40), 1.0, 0.5, 0.2)
PAL.add(revenant_bell(10, PRIME, 0.5, seed=40), beat_at(40), 1.0, 0.5, 0.45)

# §6 BRIDGE / BREAKDOWN (44-47): half-time, piano+pizz fragment, palette foreground
PAL.add(cold_bell_larynx(11, QUINT, 0.4), beat_at(44), 1.0, 0.5, 0.4)
PAL.add(psithura(11, 0.35), beat_at(44), 1.0, 0.62, 0.15)
PAL.add(mantle(11, 0.28), beat_at(44), 1.0, 0.5, 0.2)
PAL.add(chorus_many(11, NOMINAL, 0.3), beat_at(44), 1.0, 0.5, 0.4)
play_mel(piano, 44, 0.5, octv=0, send=0.2)
play_mel(pizz, 46, 0.34, notes=HOOK, octv=0, pan=0.45, send=0.14)

# §7 FINAL CHORUS (48-55): beat returns, hook+choir, harp runs, A7->Dm cadence bar55
DRUM.add(crash(0.55), beat_at(48), 1.0, 0.5, 0.2)
PAL.add(revenant_bell(10, PRIME, 0.5, seed=48), beat_at(48), 1.0, 0.5, 0.45)
PAL.add(groundwater(23, 55, 55, 0.38), beat_at(48), 1.0, 0.5, 0.18)
snare_roll(47, 1.0, 0.5)
for b in range(48, 56):
    play_beat(b, energy=1.15, dbl_hat=True, fill=(b % 8 == 7))
    # final-chorus cadence: bar 55 uses A7 (with C#) -> resolves; else vamp
    if b == 55:
        for nm in ["E3", "G3", "C#4", "E4"]:
            ORCH.add(strings_sus(note(nm), BAR, 0.22), beat_at(b), 1.0, 0.5, 0.18)
        SUB.add(kick808("A1", BAR, 0.9), beat_at(b), 1.0, 0.5, 0.02)
    else:
        play_prog(strings_sus, b, 1, 0.22, lowskip=1, send=0.18, hpf=115)
        play_808(b, 1, 0.92)
for ph in (48, 52):
    play_mel(strings_sus, ph, 0.52, octv=1, send=0.14)
    play_mel(brass, ph, 0.32, octv=0, pan=0.55, send=0.16)
    play_mel(choir_pad, ph, 0.3, octv=0, send=0.3)
    for b in range(ph, ph + 4):                          # harp runs
        chord = CYCLE[b % 4]
        for j, nm in enumerate(chord[1:] + [chord[1]]):
            MEL.add(harp(note(nm) * 2, 0.9, 0.2), b * BAR + j * 3 * STEP, 1.0, 0.62, 0.18)

# §8 PEAK-END / OUTRO (56-63): beat drops out, bare piano hook + bell, groundwater sinks
for b in (56, 57):
    play_beat(b, energy=max(0.3, 0.9 - (b - 56) * 0.4), dbl_hat=False)
    play_808(b, 1, 0.7)
PAL.add(groundwater(28, 36.7, 30.0, 0.4), beat_at(56), 1.0, 0.5, 0.25)   # sinks
PAL.add(mantle(28, 0.24), beat_at(56), 1.0, 0.5, 0.2)
play_mel(piano, 58, 0.52, octv=0, send=0.22)
PAL.add(revenant_bell(14, PRIME, 0.5, seed=99), beat_at(61.5), 1.0, 0.5, 0.5)  # answers the hook
PAL.add(pleura(20, 0.5, caught=True), beat_at(59), 1.0, 0.5, 0.15)


# ============================== MIX / MASTER ==============================
def sc_env(n, times, depth, rel=0.16):
    env = np.ones(n); a = int(0.004 * SR); r = int(rel * SR)
    duck = np.concatenate([np.linspace(1, 1 - depth, a),
                           1 - depth + depth * (1 - np.exp(-np.linspace(0, 5, r)))])
    for kt in times:
        i = int(kt * SR); j = min(n, i + len(duck))
        if i < n:
            env[i:j] = np.minimum(env[i:j], duck[:j - i])
    return env


def loudness(n):
    pts = [(0, -24), (20, -19), (43, -14), (54, -10), (100, -9), (111, -7),
           (123, -16), (134, -9), (157, -11), (172, -15), (186, -40)]
    ts = np.array([p[0] for p in pts]); db = np.array([p[1] for p in pts])
    return 10 ** (np.interp(np.arange(n) / SR, ts, db) / 20.0)


def master():
    print("  mixing (sidechain + reverb) ...")
    n = DRUM.n
    scH = sc_env(n, kick_times, 0.9)[None, :]
    scP = sc_env(n, kick_times, 0.55)[None, :]
    scM = sc_env(n, kick_times, 0.25)[None, :]
    dry = DRUM.dry + SUB.dry * scH + ORCH.dry * scP + MEL.dry * scM + PAL.dry * scP
    wet = DRUM.wet + SUB.wet + ORCH.wet + MEL.wet + PAL.wet
    irL, irR = make_ir(1), make_ir(2)
    wetr = np.stack([fftconvolve(wet[0], irL)[:n], fftconvolve(wet[1], irR)[:n]])
    mix = dry + 0.9 * wetr
    mix = mix * loudness(n)
    out = []
    for ch in range(2):
        x = mix[ch]
        x = hp(x, 28, 4)
        x = x - (1 - 10 ** (-2 / 20)) * bp(x, 2900, 3900)   # de-harsh ice band
        x = tilt(x, 1200, -5)                                # spectral tilt ONCE
        x = lp(x, 15500, 4)
        x = osat(x, 1.12)
        x = np.tanh(x * 0.9) / 0.9
        out.append(x)
    L, R = out
    m = max(np.max(np.abs(L)), np.max(np.abs(R))) + 1e-9
    L, R = L / m * 0.92, R / m * 0.92
    fi = int(1.0 * SR); fo = int(6.0 * SR)
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
    out = sys.argv[1] if len(sys.argv) > 1 else "gravewater.wav"
    write_wav(out, st)
    print(f"wrote {out}  ({st.shape[1] / SR:.1f}s, stereo {SR}Hz)")
