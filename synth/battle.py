"""
"GRAVEWATER — WAR" : darker, creepier, battle-leaning rework of Gravewater Pulse.

Same fused world (orchestra + beat + the invented dark palette) but:
 - DARKER: D Phrygian, the bII (Eb) dread move, tritone stabs, low register.
 - BATTLE: driving taiko/war-drums, relentless staccato string ostinato, brass
   stabs, choir chant octaves, snare rolls -> charges.
 - MORE / SHORTER subsections: ~11 fast-changing sections (10-18 s each).
 - MORE CREEPY PALETTE up front: rebec snarls, fragmenting ghost-choir, cracked
   bells as anvils, whisper-cloud, Shepard risers, missing-room, caught breath.

100 BPM, ~2:50. Built on orch.py + the thing.py palette; war-drum kit local.
"""
import numpy as np
from scipy.signal import fftconvolve

from orch import (note, t_of, lp, hp, bp, adsr, strings_sus, strings_stac,
                  pizz, brass, choir_pad, timpani)
from thing import (Bus, SR, tilt, osat, pink_walk, make_ir,
                   groundwater, mantle, revenant_bell, cold_bell_larynx,
                   chorus_many, psithura, cribra, stairwell, missing_room,
                   pleura, PRIME, NOMINAL, QUINT)

rng = np.random.default_rng(41)
BPM = 100.0
BEAT = 60.0 / BPM               # 0.6
BAR = 4 * BEAT                  # 2.4
STEP = BEAT / 4.0               # 0.15
NBARS = 72
TOTAL = NBARS * BAR + 3         # ~175.8

# Dark Phrygian world. Roots per bar (i - bII - bVII - i dread cycle).
CYCLE_ROOT = ["D", "Eb", "C", "D"]
CHORD = {  # power/triad voicings (dark, low)
    "D": ["D2", "A2", "D3", "F3", "A3"],
    "Eb": ["Eb2", "Bb2", "Eb3", "G3", "Bb3"],
    "C": ["C2", "G2", "C3", "E3", "G3"],
}
SUBROOT = {"D": "D1", "Eb": "D#1", "C": "C1"}

# Dark modal battle theme (brass/choir), D Phrygian: rises and falls, ends open.
THEME = [("D4", 0, 1), ("Eb4", 1, 1), ("F4", 2, 1), ("D4", 3, 1),
         ("A4", 4, 1.5), ("G4", 5.5, 0.5), ("F4", 6, 1), ("E4", 7, 1),
         ("F4", 8, 1), ("D4", 9, 1), ("Eb4", 10, 1), ("C4", 11, 1),
         ("D4", 12, 2), ("A3", 14, 2)]

DRUM = Bus(TOTAL); SUB = Bus(TOTAL); MUS = Bus(TOTAL); PAL = Bus(TOTAL)
kick_times = []


def bt(bar, b=0.0):
    return bar * BAR + b * BEAT


# ---- war-drum kit --------------------------------------------------------
def big_kick(gain=1.0):
    dur = 0.4; t = t_of(dur)
    pitch = 160 * np.exp(-t * 30) + 46
    body = np.sin(2 * np.pi * np.cumsum(pitch) / SR) * np.exp(-t * 5.5)
    click = lp(rng.uniform(-1, 1, len(t)), 5000) * np.exp(-t * 120) * 0.4
    return np.tanh((body + click) * 1.6) * gain


def taiko(freq=95, gain=0.9):
    dur = 0.5; t = t_of(dur)
    pitch = freq * (1 + 0.4 * np.exp(-t * 18))
    body = np.sin(2 * np.pi * np.cumsum(pitch) / SR) + 0.4 * np.sin(2 * np.pi * 2 * np.cumsum(pitch) / SR)
    noise = lp(rng.uniform(-1, 1, len(t)), 900) * np.exp(-t * 22) * 0.5
    return np.tanh((body * np.exp(-t * 5.5) + noise) * 1.3) * gain


def sub808(name, dur, gain=0.9):
    f = note(name); t = t_of(dur)
    pitch = f + (f * 3) * np.exp(-t * 30)
    body = np.sin(2 * np.pi * np.cumsum(pitch) / SR)
    env = np.exp(-t * 2.0) * (1 - np.exp(-t * 200))
    return lp(np.tanh(body * env * 1.4), 130) * gain


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
    divs = [4, 8, 8, 16, 16, 16, 16, 16]
    for bi in range(int(bars * 4)):
        div = divs[min(bi, len(divs) - 1)]
        for j in range(div):
            tt = bt(bar_lo) + (bi + j / div) * BEAT
            DRUM.add(snare(0.5) * 0.5, tt, gain * (0.4 + 0.6 * bi / (bars * 4)), 0.5, 0.1)


# ---- pattern helpers -----------------------------------------------------
def war_drums(bar, energy=1.0, gallop=True, fill=False, halftime=False):
    DRUM.add(big_kick(0.95 * energy), bt(bar, 0), 1.0, 0.5, 0.05); kick_times.append(bt(bar, 0))
    if not halftime:
        DRUM.add(big_kick(0.7 * energy), bar * BAR + 10 * STEP, 1.0, 0.5, 0.05); kick_times.append(bar * BAR + 10 * STEP)
    # taiko gallop: 8th + two 16ths feel
    steps = [0, 3, 4, 6, 7, 8, 11, 12, 14, 15] if gallop else [0, 4, 8, 12]
    for s in steps:
        acc = 1.0 if s % 4 == 0 else 0.6
        DRUM.add(taiko(95 if s % 8 < 4 else 78, 0.7 * acc * energy), bar * BAR + s * STEP,
                 1.0, 0.5 + 0.25 * np.sin(s), 0.08)
    DRUM.add(snare(0.8 * energy), bar * BAR + 8 * STEP, 1.0, 0.5, 0.12)   # backbeat
    if fill:
        for j, s in enumerate([12, 13, 14, 15]):
            DRUM.add(taiko(140 - j * 16, 0.8), bar * BAR + s * STEP, 1.0, 0.4 + 0.04 * j, 0.1)


def ostinato(bar, root, energy=1.0, octv=0):
    """Relentless staccato-string ostinato on root + fifth (battle drive)."""
    fifth = {"D": "A", "Eb": "Bb", "C": "G"}[root]
    for s in range(16):
        nm = (root + str(3 + octv)) if s % 4 != 2 else (fifth + str(3 + octv))
        acc = 0.34 if s % 4 == 0 else 0.2
        MUS.add(strings_stac(note(nm), 0.15, acc * energy), bar * BAR + s * STEP, 1.0, 0.5, 0.1)
    # low cello pedal doubling
    MUS.add(strings_stac(note(root + "2"), BEAT, 0.3 * energy), bt(bar, 0), 1.0, 0.5, 0.08)


def play_prog(inst, start_bar, nbars, gain, lowskip=1, pan=0.5, send=0.16, hpf=None):
    for b in range(nbars):
        r = CYCLE_ROOT[b % 4]
        for nm in CHORD[r][lowskip:]:
            sig = inst(note(nm), BAR * 0.98, gain)
            if hpf:
                sig = hp(sig, hpf)
            MUS.add(sig, bt(start_bar + b), 1.0, pan, send)


def play_sub(start_bar, nbars, gain=0.9):
    for b in range(nbars):
        SUB.add(sub808(SUBROOT[CYCLE_ROOT[b % 4]], BAR * 0.95, gain), bt(start_bar + b), 1.0, 0.5, 0.02)


def play_theme(inst, phrase_bar, gain, octv=0, pan=0.5, send=0.16):
    for nm, b, dur in THEME:
        MUS.add(inst(note(nm) * 2 ** octv, dur * BEAT * 0.98, gain), bt(phrase_bar, b), 1.0, pan, send)


def brass_stabs(bar, root, gain=0.4):
    for s in (0, 6, 10):
        for nm in CHORD[root][2:4]:
            MUS.add(brass(note(nm), 0.3, gain), bar * BAR + s * STEP, 1.0, 0.55, 0.18)


def choir_chord(bar, root, dur_bars, gain=0.3, octv=0):
    for nm in CHORD[root][2:]:
        PAL.add(choir_pad(note(nm) * 2 ** octv, dur_bars * BAR, gain), bt(bar), 1.0, 0.5, 0.35)


def anvil(bar, b=0.0, gain=0.4):
    PAL.add(revenant_bell(8, PRIME, gain, seed=int(bar * 7 + b)), bt(bar, b), 1.0, 0.5, 0.4)


print("building GRAVEWATER — WAR ...")

# ==================== ARRANGEMENT — 11 short sections (72 bars) ====================
# §1 CREEP (0-4 | 0-12s): missing room, sub, ticks, distant snarl, whisper
PAL.add(missing_room(12, 97.5, 0.4), 0, 1.0, 0.5, 0.4)
PAL.add(groundwater(12, 36.7, 36.7, 0.45), 0, 1.0, 0.5, 0.22)
cl, cr = cribra(12, 0.5); PAL.add_st(cl, cr, 0, 0.8, 0.3)
PAL.add(psithura(12, 0.3), 0, 1.0, 0.62, 0.15)
PAL.add(revenant_bell(10, QUINT, 0.3, seed=1), 6, 1.0, 0.5, 0.45)

# §2 PULSE BUILD (5-9 | 12-24s): sub heartbeat, stairwell rise, string swell, riser
PAL.add(stairwell(5 * BAR, 0.34), bt(5), 1.0, 0.5, 0.3)
PAL.add(mantle(12, 0.3), bt(5), 1.0, 0.5, 0.2)
play_prog(strings_sus, 5, 5, 0.2, lowskip=2, send=0.2)
for b in range(5, 10):
    DRUM.add(taiko(70, 0.5), bt(b, 0), 1.0, 0.5, 0.06); kick_times.append(bt(b, 0))
    DRUM.add(taiko(70, 0.35), bt(b, 2), 1.0, 0.5, 0.06)
DRUM.add(riser(4 * BAR, 0.6), bt(6), 1.0, 0.5, 0.2)
snare_roll(8, 2, 0.45)

# §3 WAR CHARGE 1 (10-17 | 24-43s): full war drums + ostinato + brass stabs + sub
DRUM.add(crash(0.5), bt(10), 1.0, 0.5, 0.2); anvil(10)
for b in range(10, 18):
    war_drums(b, 1.0, gallop=True, fill=(b % 4 == 3))
    ostinato(b, CYCLE_ROOT[b % 4], 1.0)
    brass_stabs(b, CYCLE_ROOT[b % 4], 0.34)
    play_sub(b, 1, 0.9)
PAL.add(groundwater(19, 36.7, 36.7, 0.35), bt(10), 1.0, 0.5, 0.18)
PAL.add(chorus_many(19, NOMINAL, 0.24), bt(10), 1.0, 0.5, 0.4)

# §4 CREEP BREAK (18-21 | 43-53s): drums cut, fragmenting ghost-choir, snarl, whisper
PAL.add(chorus_many(10, NOMINAL, 0.4), bt(18), 1.0, 0.5, 0.4)
PAL.add(revenant_bell(10, PRIME, 0.4, seed=18), bt(18), 1.0, 0.5, 0.45)
PAL.add(psithura(10, 0.38), bt(18), 1.0, 0.6, 0.15)
PAL.add(cold_bell_larynx(9, QUINT, 0.4), bt(19), 1.0, 0.5, 0.4)
play_theme(strings_sus, 18, 0.3, octv=0, send=0.2)

# §5 WAR CHARGE 2 (22-29 | 53-72s): bigger + theme on brass + choir octaves
DRUM.add(crash(0.55), bt(22), 1.0, 0.5, 0.2); anvil(22)
for b in range(22, 30):
    war_drums(b, 1.1, gallop=True, fill=(b % 4 == 3))
    ostinato(b, CYCLE_ROOT[b % 4], 1.05)
    play_sub(b, 1, 0.95)
play_theme(brass, 22, 0.36, octv=0, pan=0.55)
play_theme(brass, 26, 0.36, octv=0, pan=0.45)
choir_chord(22, "D", 4, 0.28, octv=0); choir_chord(26, "Eb", 4, 0.28)
PAL.add(chorus_many(19, NOMINAL, 0.22), bt(22), 1.0, 0.5, 0.4)

# §6 TENSION BREAK (30-33 | 72-82s): hemiola stabs, cracked bells, stairwell, riser
for b in range(30, 34):
    for s in (0, 3, 6, 9, 12):                     # 3-against-4 hemiola stabs
        MUS.add(strings_stac(note("D3"), 0.14, 0.3), b * BAR + s * STEP, 1.0, 0.5, 0.1)
    anvil(b, 0)
PAL.add(stairwell(4 * BAR, 0.34), bt(30), 1.0, 0.5, 0.3)
DRUM.add(riser(4 * BAR, 0.65), bt(30), 1.0, 0.5, 0.2)
snare_roll(32, 2, 0.5)

# §7 CLIMAX (34-43 | 82-106s): everything; theme choir+brass; tritone stab; PEAK ~99s
DRUM.add(crash(0.6), bt(34), 1.0, 0.5, 0.2); anvil(34)
for b in range(34, 44):
    war_drums(b, 1.2, gallop=True, fill=(b % 4 == 3))
    ostinato(b, CYCLE_ROOT[b % 4], 1.15)
    brass_stabs(b, CYCLE_ROOT[b % 4], 0.34)
    play_sub(b, 1, 1.0)
play_theme(brass, 34, 0.4, octv=0, pan=0.55)
play_theme(choir_pad, 34, 0.34, octv=1, pan=0.5, send=0.3)
play_theme(strings_sus, 38, 0.34, octv=1, send=0.16)
choir_chord(34, "D", 4, 0.3, octv=1); choir_chord(38, "Eb", 4, 0.3, octv=1)
# tritone dread stab at the apex
for nm in ["D3", "Ab3"]:
    MUS.add(brass(note(nm), 0.6, 0.3), bt(40), 1.0, 0.5, 0.2)
PAL.add(chorus_many(24, NOMINAL, 0.26), bt(34), 1.0, 0.5, 0.4)

# §8 DARK COLLAPSE (44-47 | 106-115s): sudden strip, missing room, snarl, sink
PAL.add(missing_room(10, 97.5, 0.42), bt(44), 1.0, 0.5, 0.4)
PAL.add(groundwater(10, 36.7, 30.0, 0.4), bt(44), 1.0, 0.5, 0.25)
PAL.add(revenant_bell(9, PRIME, 0.45, seed=44), bt(44), 1.0, 0.5, 0.45)
PAL.add(psithura(9, 0.36), bt(44), 1.0, 0.6, 0.15)
play_theme(strings_sus, 44, 0.26, octv=0, send=0.25)

# §9 FINAL CHARGE (48-59 | 115-144s): biggest, relentless
DRUM.add(crash(0.6), bt(48), 1.0, 0.5, 0.2); anvil(48)
snare_roll(47, 1, 0.5)
for b in range(48, 60):
    war_drums(b, 1.22, gallop=True, fill=(b % 4 == 3))
    ostinato(b, CYCLE_ROOT[b % 4], 1.2)
    brass_stabs(b, CYCLE_ROOT[b % 4], 0.36)
    play_sub(b, 1, 1.0)
for ph in (48, 52, 56):
    play_theme(brass, ph, 0.4, octv=0, pan=0.55)
    play_theme(choir_pad, ph, 0.34, octv=1, send=0.3)
choir_chord(48, "D", 4, 0.3, octv=1); choir_chord(52, "Eb", 4, 0.3, octv=1); choir_chord(56, "C", 4, 0.3, octv=1)
PAL.add(chorus_many(29, NOMINAL, 0.24), bt(48), 1.0, 0.5, 0.4)

# §10 AFTERMATH (60-71 | 144-172s): drums fade, lone anvil, groundwater sinks, caught breath
for b in (60, 61):
    war_drums(b, max(0.3, 0.9 - (b - 60) * 0.4), gallop=False)
    play_sub(b, 1, 0.7)
PAL.add(groundwater(28, 36.7, 28.0, 0.42), bt(60), 1.0, 0.5, 0.25)
PAL.add(mantle(28, 0.26), bt(60), 1.0, 0.5, 0.2)
PAL.add(missing_room(28, 97.5, 0.3), bt(60), 1.0, 0.5, 0.4)
play_theme(strings_sus, 62, 0.3, octv=0, send=0.3)
anvil(66, 0, 0.5)
PAL.add(pleura(20, 0.5, caught=True), bt(63), 1.0, 0.5, 0.15)


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
    pts = [(0, -24), (12, -18), (24, -8), (43, -13), (53, -7), (72, -13),
           (82, -6), (99, -4), (106, -15), (115, -5), (144, -12), (172, -40)]
    ts = np.array([p[0] for p in pts]); db = np.array([p[1] for p in pts])
    return 10 ** (np.interp(np.arange(n) / SR, ts, db) / 20.0)


def master():
    print("  mixing ...")
    n = DRUM.n
    scH = sc_env(n, kick_times, 0.85)[None, :]
    scP = sc_env(n, kick_times, 0.45)[None, :]
    dry = DRUM.dry + SUB.dry * scH + MUS.dry * scP + PAL.dry * scP
    wet = DRUM.wet + SUB.wet + MUS.wet + PAL.wet
    irL, irR = make_ir(1), make_ir(2)
    wetr = np.stack([fftconvolve(wet[0], irL)[:n], fftconvolve(wet[1], irR)[:n]])
    mix = (dry + 0.9 * wetr) * loudness(n)
    out = []
    for ch in range(2):
        x = mix[ch]
        x = hp(x, 30, 4)
        x = x - (1 - 10 ** (-2.5 / 20)) * bp(x, 2800, 4200)   # de-harsh
        x = tilt(x, 1300, -4.5)
        x = lp(x, 15500, 4)
        x = osat(x, 1.14)
        x = np.tanh(x * 0.9) / 0.9
        out.append(x)
    L, R = out
    m = max(np.max(np.abs(L)), np.max(np.abs(R))) + 1e-9
    L, R = L / m * 0.94, R / m * 0.94
    fi = int(0.5 * SR); fo = int(5.0 * SR)
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
    out = sys.argv[1] if len(sys.argv) > 1 else "battle.wav"
    write_wav(out, st)
    print(f"wrote {out}  ({st.shape[1] / SR:.1f}s, stereo {SR}Hz)")
