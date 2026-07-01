"""
"GRAVEWATER — GRIMDARK" : the 40K-grade version.

Gothic / grimdark militarism, grand and ominous:
 - CATHEDRAL PIPE ORGAN (additive organ-stops) as the harmonic monolith.
 - Monastic MALE CHOIR CHANT with Latin-vowel syllables (formant morphing),
   doubled an octave down = the "Imperium" chant.
 - WAR-HORN brass fanfares (root+fifth+octave power stacks) & tone-cluster dread.
 - Tolling CATHEDRAL BELLS, martial taiko, snare charges.
 - The invented creepy palette still lurks (ghost-choir, snarls, whispers,
   missing-room, caught breath).
Grand form, lots of gestures. D Phrygian, 96 BPM, ~3:00.
"""
import numpy as np
from scipy.signal import fftconvolve

from orch import (note, t_of, lp, hp, bp, adsr, strings_sus, strings_stac, brass, choir_pad)
from thing import (Bus, SR, tilt, osat, make_ir,
                   groundwater, mantle, revenant_bell, cold_bell_larynx,
                   chorus_many, psithura, cribra, stairwell, missing_room,
                   pleura, PRIME, NOMINAL, QUINT)

rng = np.random.default_rng(1487)
BPM = 96.0
BEAT = 60.0 / BPM               # 0.625
BAR = 4 * BEAT                  # 2.5
STEP = BEAT / 4.0
NBARS = 72
TOTAL = NBARS * BAR + 4         # ~184

CYCLE_ROOT = ["D", "Eb", "C", "D"]          # i - bII - bVII - i (Phrygian dread)
CHORD = {"D": ["D2", "A2", "D3", "F3", "A3"], "Eb": ["Eb2", "Bb2", "Eb3", "G3", "Bb3"],
         "C": ["C2", "G2", "C3", "E3", "G3"]}
SUBROOT = {"D": "D1", "Eb": "D#1", "C": "C1"}
VOWELS = {"ah": (700, 1150, 2600), "eh": (530, 1700, 2480), "oh": (500, 840, 2410),
          "oo": (330, 870, 2240), "ee": (300, 2100, 2900)}

# Solemn chant theme (D Phrygian): (note, start_beat, dur_beats, vowel)
CHANT = [("D3", 0, 1.5, "ah"), ("F3", 1.5, 0.5, "eh"), ("E3", 2, 1, "ah"), ("D3", 3, 1, "oh"),
         ("C3", 4, 1.5, "ah"), ("D3", 5.5, 0.5, "eh"), ("Eb3", 6, 1, "oh"), ("D3", 7, 1, "ah"),
         ("A3", 8, 1.5, "ah"), ("G3", 9.5, 0.5, "eh"), ("F3", 10, 1, "oh"), ("E3", 11, 1, "ee"),
         ("D3", 12, 2, "ah"), ("A2", 14, 2, "oo")]

DRUM = Bus(TOTAL); SUB = Bus(TOTAL); MUS = Bus(TOTAL); CHOIR = Bus(TOTAL); PAL = Bus(TOTAL)
kick_times = []


def bt(bar, b=0.0):
    return bar * BAR + b * BEAT


# ---- gothic instruments --------------------------------------------------
def organ_tone(freq, dur, gain=0.3):
    """Pipe-organ stops (8'/4'/2â…”'/2'/...) — additive, band-limited, chiff attack."""
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


def chant_note(freq, dur, vowel, gain):
    n = int(dur * SR); t = t_of(dur)
    vibr = 1 + 0.012 * np.sin(2 * np.pi * 5.0 * t) * np.clip((t - 0.2) / 0.3, 0, 1)
    cph = np.cumsum(freq * vibr) / SR
    src = np.zeros(n)
    for k in range(1, 16):
        if freq * k > SR / 2 - 200:
            break
        src += (1.0 / k ** 1.2) * np.sin(2 * np.pi * k * cph)
    F1, F2, F3 = VOWELS[vowel]
    out = (1.0 * bp(src, F1 * 0.85, F1 * 1.15) + 0.6 * bp(src, F2 * 0.85, F2 * 1.15)
           + 0.3 * bp(src, F3 * 0.85, F3 * 1.15))
    env = adsr(n, 0.06, 0.15, 0.85, min(0.45, dur * 0.3))
    return lp(out * env, 4200) / (np.max(np.abs(out)) + 1e-9) * gain


def chant(phrase_bar, gain=0.4, octv=0, pan=0.5, bass_double=True):
    for nm, b, dur, vw in CHANT:
        f = note(nm) * 2 ** octv
        CHOIR.add(chant_note(f, dur * BEAT * 0.95, vw, gain), bt(phrase_bar, b), 1.0, pan, 0.4)
        if bass_double:
            CHOIR.add(chant_note(f / 2, dur * BEAT * 0.95, vw, gain * 0.6), bt(phrase_bar, b), 1.0, pan, 0.35)


def war_horn(root, dur, bar, b=0.0, gain=0.4):
    """Power fanfare: root + fifth + octave low brass."""
    fifth = {"D": "A", "Eb": "Bb", "C": "G"}[root]
    for nm in [root + "2", fifth + "2", root + "3"]:
        MUS.add(brass(note(nm), dur, gain), bt(bar, b), 1.0, 0.5, 0.2)


def cluster(names, dur_bars, bar, gain=0.26):
    for nm in names:
        MUS.add(organ_tone(note(nm), dur_bars * BAR, gain), bt(bar), 1.0, 0.5, 0.3)


def toll(bar, root=73.4, gain=0.5, b=0.0):
    PAL.add(revenant_bell(14, root, gain, seed=int(bar * 5 + b)), bt(bar, b), 1.0, 0.5, 0.45)


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
        acc = 0.32 if s % 4 == 0 else 0.19
        MUS.add(strings_stac(note(nm), 0.14, acc * energy), bar * BAR + s * STEP, 1.0, 0.5, 0.1)
    MUS.add(strings_stac(note(root + "2"), BEAT, 0.3 * energy), bt(bar, 0), 1.0, 0.5, 0.08)


def play_organ(start_bar, nbars, gain=0.24, octv=0):
    for b in range(nbars):
        r = CYCLE_ROOT[b % 4]
        for nm in CHORD[r][1:4]:
            MUS.add(organ_tone(note(nm) * 2 ** octv, BAR * 0.99, gain), bt(start_bar + b), 1.0, 0.5, 0.3)


def play_sub(start_bar, nbars, gain=0.9):
    for b in range(nbars):
        SUB.add(sub808(SUBROOT[CYCLE_ROOT[b % 4]], BAR * 0.95, gain), bt(start_bar + b), 1.0, 0.5, 0.02)


print("building GRAVEWATER — GRIMDARK ...")

# ==================== ARRANGEMENT (72 bars, ~3:00) ====================
# §1 CATHEDRAL (0-5): organ swell, tolling bell, distant chant, missing room
for nm in ["D2", "A2", "D3", "A3"]:
    MUS.add(organ_tone(note(nm), 5 * BAR, 0.22), bt(0), 1.0, 0.5, 0.32)
PAL.add(missing_room(13, 97.5, 0.4), 0, 1.0, 0.5, 0.42)
PAL.add(groundwater(13, 36.7, 36.7, 0.4), 0, 1.0, 0.5, 0.22)
toll(0, 73.4, 0.55); toll(3, 73.4, 0.45)
PAL.add(psithura(13, 0.3), 0, 1.0, 0.6, 0.15)
chant(1, 0.3, octv=0, pan=0.5)                      # distant first chant

# §2 CHANT VERSE (6-13): monastic chant over organ pedal + slow taiko + bell tolls
play_organ(6, 8, 0.2)
chant(6, 0.42, octv=0); chant(10, 0.42, octv=0)
for b in range(6, 14):
    DRUM.add(taiko(70, 0.5), bt(b, 0), 1.0, 0.5, 0.06); kick_times.append(bt(b, 0))
    DRUM.add(taiko(70, 0.3), bt(b, 2), 1.0, 0.5, 0.06)
    if b % 4 == 0:
        toll(b, 73.4, 0.4)
PAL.add(chorus_many(20, NOMINAL, 0.22), bt(6), 1.0, 0.5, 0.4)

# §3 HORN CALL / BUILD (14-17): war-horn fanfare, snare roll, riser, choir swell
for b in range(14, 18):
    war_horn(CYCLE_ROOT[b % 4], BAR, b, 0, 0.34)
play_organ(14, 4, 0.22)
snare_roll(15, 3, 0.5)
DRUM.add(riser(4 * BAR, 0.6), bt(14), 1.0, 0.5, 0.2)
PAL.add(stairwell(4 * BAR, 0.3), bt(14), 1.0, 0.5, 0.3)

# §4 WAR CHARGE I (18-25): drums + ostinato + organ + chant octaves + horns
DRUM.add(crash(0.5), bt(18), 1.0, 0.5, 0.2); toll(18, 73.4, 0.5)
for b in range(18, 26):
    war_drums(b, 1.05, gallop=True, fill=(b % 4 == 3))
    ostinato(b, CYCLE_ROOT[b % 4], 1.0)
    play_sub(b, 1, 0.9)
play_organ(18, 8, 0.2)
chant(18, 0.44, octv=0); chant(22, 0.44, octv=0)
for b in range(18, 26, 2):
    war_horn(CYCLE_ROOT[b % 4], 0.5, b, 0, 0.3)
PAL.add(groundwater(20, 36.7, 36.7, 0.32), bt(18), 1.0, 0.5, 0.18)

# §5 DREAD BREAK (26-29): tone-cluster, ghost-choir, snarl, tolling bell
cluster(["D3", "Eb3", "A3", "Bb3"], 4, 26, 0.24)     # menacing cluster
PAL.add(chorus_many(10, NOMINAL, 0.42), bt(26), 1.0, 0.5, 0.4)
PAL.add(revenant_bell(10, PRIME, 0.42, seed=26), bt(26), 1.0, 0.5, 0.45)
PAL.add(psithura(10, 0.36), bt(26), 1.0, 0.6, 0.15)
PAL.add(cold_bell_larynx(9, QUINT, 0.4), bt(27), 1.0, 0.5, 0.4)
chant(27, 0.3, octv=0)

# §6 WAR CHARGE II (30-37): bigger; chant theme + choir + horns + drums
DRUM.add(crash(0.55), bt(30), 1.0, 0.5, 0.2); toll(30, 73.4, 0.5)
for b in range(30, 38):
    war_drums(b, 1.12, gallop=True, fill=(b % 4 == 3))
    ostinato(b, CYCLE_ROOT[b % 4], 1.05)
    play_sub(b, 1, 0.95)
play_organ(30, 8, 0.22)
chant(30, 0.46, octv=1); chant(34, 0.46, octv=1)     # chant up an octave
chant(30, 0.32, octv=0); chant(34, 0.32, octv=0)
for b in range(30, 38, 2):
    war_horn(CYCLE_ROOT[b % 4], 0.5, b, 0, 0.32)

# §7 CHOIR CLIMAX (38-47): everything; grand; PEAK ~ bar 43 (~112s golden-ish)
DRUM.add(crash(0.6), bt(38), 1.0, 0.5, 0.2); toll(38, 73.4, 0.55); toll(42, 73.4, 0.5)
for b in range(38, 48):
    war_drums(b, 1.22, gallop=True, fill=(b % 4 == 3))
    ostinato(b, CYCLE_ROOT[b % 4], 1.15)
    play_sub(b, 1, 1.0)
play_organ(38, 10, 0.24)
for ph in (38, 42, 46):
    chant(ph, 0.5, octv=1); chant(ph, 0.34, octv=0)
for b in range(38, 48, 2):
    war_horn(CYCLE_ROOT[b % 4], 0.6, b, 0, 0.34)
for nm in CHORD["D"][2:]:
    CHOIR.add(choir_pad(note(nm) * 2, 4 * BAR, 0.24), bt(38), 1.0, 0.5, 0.32)
# tritone dread stab at apex
for nm in ["D3", "Ab3"]:
    MUS.add(brass(note(nm), 0.7, 0.3), bt(43), 1.0, 0.5, 0.2)

# §8 COLLAPSE (48-51): strip to organ pedal + chant fragment + snarl
for nm in ["D2", "A2", "D3"]:
    MUS.add(organ_tone(note(nm), 4 * BAR, 0.22), bt(48), 1.0, 0.5, 0.32)
PAL.add(missing_room(10, 97.5, 0.4), bt(48), 1.0, 0.5, 0.42)
PAL.add(revenant_bell(9, PRIME, 0.42, seed=48), bt(48), 1.0, 0.5, 0.45)
PAL.add(psithura(9, 0.34), bt(48), 1.0, 0.6, 0.15)
chant(49, 0.34, octv=0)

# §9 FINAL CHARGE (52-63): biggest, relentless, full gothic force
DRUM.add(crash(0.62), bt(52), 1.0, 0.5, 0.2); toll(52, 73.4, 0.55)
snare_roll(51, 1, 0.5)
for b in range(52, 64):
    war_drums(b, 1.25, gallop=True, fill=(b % 4 == 3))
    ostinato(b, CYCLE_ROOT[b % 4], 1.2)
    play_sub(b, 1, 1.0)
play_organ(52, 12, 0.24)
for ph in (52, 56, 60):
    chant(ph, 0.5, octv=1); chant(ph, 0.34, octv=0)
    for b in range(ph, ph + 4, 2):
        war_horn(CYCLE_ROOT[b % 4], 0.6, b, 0, 0.34)
for nm in CHORD["D"][2:]:
    CHOIR.add(choir_pad(note(nm) * 2, 12 * BAR, 0.2), bt(52), 1.0, 0.5, 0.32)

# §10 REQUIEM OUTRO (64-71): organ fades, lone chant, tolling bell, sink, caught breath
for nm in ["D2", "A2", "D3", "F3"]:
    MUS.add(organ_tone(note(nm), 8 * BAR, 0.2), bt(64), 1.0, 0.5, 0.34)
PAL.add(groundwater(20, 36.7, 28.0, 0.4), bt(64), 1.0, 0.5, 0.25)
PAL.add(mantle(20, 0.24), bt(64), 1.0, 0.5, 0.2)
chant(65, 0.36, octv=0)
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
    pts = [(0, -20), (15, -16), (33, -9), (45, -6), (65, -13), (75, -6), (95, -9),
           (112, -4), (120, -14), (130, -5), (160, -12), (184, -40)]
    ts = np.array([p[0] for p in pts]); db = np.array([p[1] for p in pts])
    return 10 ** (np.interp(np.arange(n) / SR, ts, db) / 20.0)


def master():
    print("  mixing ...")
    n = DRUM.n
    scH = sc_env(n, kick_times, 0.82)[None, :]
    scP = sc_env(n, kick_times, 0.4)[None, :]
    scC = sc_env(n, kick_times, 0.18)[None, :]     # choir barely ducked (stays grand)
    dry = DRUM.dry + SUB.dry * scH + MUS.dry * scP + CHOIR.dry * scC + PAL.dry * scP
    wet = DRUM.wet + SUB.wet + MUS.wet + CHOIR.wet + PAL.wet
    irL, irR = make_ir(1, rt60=5.0), make_ir(2, rt60=5.0)   # cathedral tail
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
    out = sys.argv[1] if len(sys.argv) > 1 else "grimdark.wav"
    write_wav(out, st)
    print(f"wrote {out}  ({st.shape[1] / SR:.1f}s, stereo {SR}Hz)")
