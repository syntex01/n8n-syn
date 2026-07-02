"""
"RESIDUA" — the apex track. Implements synth/SPEC4.md (apex-design workflow).

Thesis: the whole piece is a war for the tonic D. The D fundamental is
STRUCTURALLY WITHHELD from the sub register until the golden-section climax;
a phantom D (missing-fundamental residue partials) haunts everything, the
dominant A owns the sub, and the leading tone C# is hoarded (appears only
twice). Anticipation is engineered across the whole timeline and paid off late,
sideways, and bigger than promised.

Priorities: goosebumps > addiction > alien > exciting/chilling; never harsh.

Built on: thing.py (alien palette), orch.py (orchestra), dsp3.py (production
mix: dual reverb, decorrelation, transient shaper, comp/limiter, humanizer).
Obeys the R1-R20 code-safety checklist in SPEC4.
"""
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

import thing
import orch
import dsp3
from dsp3 import SR, lp, hp, bp, pink, pink_curve, reverb_bus, decorrelate, \
    mono_below, transient_shape, bus_comp, limiter, soft_sat, tilt_cut, Mixer

BPM = 104.0
BEAT = 60.0 / BPM              # 0.576923
BAR = 4 * BEAT                 # 2.307692
NBARS = 110
TOTAL = NBARS * BAR + 6        # generous tail; bell decays land inside
note = orch.note

# ---- the withheld-D world -------------------------------------------------
# phantom-D residue: groundwater synthesizes partials of a MISSING fundamental.
PHANTOM_D = 73.4               # D2 fundamental — never synthesized directly
PHANTOM_EB = 77.8             # Eb2 — the phantom-modulation target


# ============================================================ INSTRUMENTS
def lead(freq, dur, gain=0.5, bright=3200, rolloff=1.25, vibr=0.008):
    """Warm band-limited additive hook lead — the 'voice' that sings the hook.
    Few partials, steep rolloff (never harsh), delayed vibrato, soft attack."""
    n = int(dur * SR); t = np.arange(n) / SR
    vib = 1 + vibr * np.clip((t - 0.15) / 0.2, 0, 1) * np.sin(2 * np.pi * 5.1 * t)
    cph = 2 * np.pi * np.cumsum(freq * vib) / SR
    out = np.zeros(n)
    for k in range(1, 13):
        if freq * k > SR * 0.45:
            break
        out += (1.0 / k ** rolloff) * np.sin(k * cph + k * 0.3)
    out /= np.max(np.abs(out)) + 1e-9
    a = int(0.02 * SR); r = int(min(0.4, dur * 0.4) * SR)
    env = np.ones(n); env[:a] = np.linspace(0, 1, a) ** 1.3
    if r < n:
        env[-r:] = np.linspace(1, 0, r) ** 1.6
    return lp(out * env, bright) * gain


def choir(freqs, dur, gain=0.3, oct_down=True):
    n = int(dur * SR); mix = np.zeros(n)
    for f in freqs:
        mix += orch.choir_pad(f, dur, gain=gain)[:n]
        if oct_down:
            mix += orch.choir_pad(f / 2, dur, gain=gain * 0.5)[:n]
    return mix / (len(freqs) + 1e-9)


def organ(freqs, dur, gain=0.26):
    """Pipe-organ stops (additive, chiff attack, slow wind LFO)."""
    n = int(dur * SR); t = np.arange(n) / SR
    out = np.zeros(n)
    wind = 1 + 0.03 * np.sin(2 * np.pi * 0.15 * t + 1.0)
    for f in freqs:
        for r, a in [(1, 1.0), (2, 0.5), (3, 0.4), (4, 0.28), (6, 0.16), (8, 0.1)]:
            if f * r > SR * 0.45:
                break
            out += a * np.sin(2 * np.pi * f * r * np.cumsum(wind) / SR + np.random.uniform(0, 6))
    out /= np.max(np.abs(out)) + 1e-9
    ci = int(0.03 * SR); chiff = np.zeros(n)
    chiff[:ci] = lp(np.random.uniform(-1, 1, ci), 4000) * np.exp(-np.linspace(0, 1, ci) * 6) * 0.05
    a = int(0.06 * SR); env = np.ones(n); env[:a] = np.linspace(0, 1, a)
    r = int(min(0.5, dur * 0.25) * SR); env[-r:] = np.linspace(1, 0, r)
    return lp((out + chiff) * env, 5000) * gain


def horn(freq, dur, gain=0.4):
    return orch.brass(freq, dur, gain=gain, bright=3000)


def war_kick(gain=1.0):
    dur = 0.4; t = np.arange(int(dur * SR)) / SR
    body = np.sin(2 * np.pi * np.cumsum(150 * np.exp(-t * 30) + 42) / SR) * np.exp(-t * 6)
    modal = 0.3 * np.sin(2 * np.pi * 220 * t) * np.exp(-t * 20)
    skin = lp(np.random.uniform(-1, 1, len(t)), 4000) * np.exp(-t * 120) * 0.3
    return np.tanh((body + modal + skin) * 1.5) * gain


def deep_tom(freq=100, gain=0.8):
    dur = 0.45; t = np.arange(int(dur * SR)) / SR
    body = np.sin(2 * np.pi * np.cumsum(freq * (1 + 0.4 * np.exp(-t * 16))) / SR)
    return np.tanh(body * np.exp(-t * 6) * 1.3) * gain


def taiko(freq=90, gain=0.8):
    dur = 0.4; t = np.arange(int(dur * SR)) / SR
    body = np.sin(2 * np.pi * np.cumsum(freq * (1 + 0.4 * np.exp(-t * 18))) / SR) + \
        0.4 * np.sin(2 * np.pi * 2 * np.cumsum(freq * (1 + 0.4 * np.exp(-t * 18))) / SR)
    noise = lp(np.random.uniform(-1, 1, len(t)), 900) * np.exp(-t * 22) * 0.5
    return np.tanh((body * np.exp(-t * 6) + noise) * 1.3) * gain


def sub_bass(name, dur, gain=0.8):
    f = note(name); t = np.arange(int(dur * SR)) / SR
    body = np.sin(2 * np.pi * np.cumsum(f + f * 2.5 * np.exp(-t * 26)) / SR)
    env = np.exp(-t * 1.8) * (1 - np.exp(-t * 180))
    return lp(np.tanh(body * env * 1.35), 120) * gain


def phantom(dur, f0=PHANTOM_D, f0b=None, gain=0.42):
    """Residue-pitch phantom tonic: partials 3-6 of a missing fundamental.
    f0b != f0 -> phantom modulation (fundamental implication glides)."""
    n = int(dur * SR); t = np.linspace(0, 1, n)
    f0arr = f0 * (1 - t) + (f0b if f0b else f0) * t
    out = np.zeros(n)
    for k in (3, 4, 5, 6):
        amp = k ** -1.2 * pink_curve(n, 0.85, 1.15, seed=k * 7)
        cents = pink_curve(n, -6, 6, seed=k * 13)
        ph = 2 * np.pi * np.cumsum(f0arr * k * 2 ** (cents / 1200)) / SR
        out += amp * np.sin(ph + np.random.uniform(0, 6))
    return thing.tilt(hp(out / 3, 90), 260, -4) * thing.swell(n, 0.3) * gain


def reverse_prehit(hit_sig, lead_s=0.288):
    """Pre-echo: reversed, LP'd ghost of a signal placed before it."""
    g = np.flip(lp(hit_sig[:int(0.4 * SR)], 3000))
    return g / (np.max(np.abs(g)) + 1e-9)


# ---- Tessera: granulate a captured bell tail, chord-quantized -------------
def tessera(bell_tail, dur, chord_freqs, gain=0.3):
    n = int(dur * SR); out = np.zeros(n)
    src = bell_tail / (np.max(np.abs(bell_tail)) + 1e-9)
    rng = np.random.default_rng(4242)
    n_grains = int(30 * dur)
    for _ in range(n_grains):
        gl = int(rng.uniform(0.08, 0.18) * SR)
        at = int(rng.uniform(0, max(1, n - gl)))
        src_at = int(rng.uniform(0, max(1, len(src) - gl)))
        grain = src[src_at:src_at + gl] * np.hanning(gl)
        # resample grain toward a chord tone (crude pitch-shift via interp)
        target = rng.choice(chord_freqs)
        ratio = target / 180.0            # bell region ~180 Hz
        idx = np.clip(np.arange(gl) * ratio, 0, gl - 1)
        grain = np.interp(idx, np.arange(gl), grain)
        end = min(n, at + gl); ln = end - at
        out[at:end] += grain[:ln] * rng.uniform(0.4, 1.0)
    return lp(out / (np.max(np.abs(out)) + 1e-9), 4000) * gain


# ============================================================ ARRANGEMENT
MIX = Mixer(TOTAL, ["drums", "bass", "voices", "pads", "fx"])
np.random.seed(1729)


def bt(bar, beat=0.0):
    return (bar - 1) * BAR + beat * BEAT


# The hook "Lament Leap": (note, beat_in_phrase, dur_beats). 4-bar phrase.
HOOK = [("D3", 0, 1.5), ("E3", 1.5, 0.5), ("F3", 2, 2), ("E3", 4, 1),
        ("A2", 5, 3), ("F3", 8, 3), ("Eb3", 11, 1), ("E3", 12, 2)]


def rw_lead(f, d, g):
    """Adapter: rebec_wraith is (dur, freq, gain); expose it as (freq, dur, gain)."""
    return thing.rebec_wraith(d, f, g)


def play_hook(bar0, inst, gain, octv=0, trunc=None, bus="voices",
              room=0.08, hall=0.3, pan=0.5):
    """Play the hook (or truncated prefix) with an instrument taking (freq, dur, gain)."""
    notes = HOOK[:trunc] if trunc else HOOK
    for i, (nm, b, d) in enumerate(notes):
        octn = str(int(nm[-1]) + octv)
        f = note(nm[:-1] + octn)
        dur = d * BEAT * 0.98
        sig = inst(f, dur, gain)
        at = bt(bar0, b)
        MIX.add(bus, sig, at, 1.0, pan, room=room, hall=hall, jitter_ms=6, seed=i + bar0)
        # leap note (#6, index 5) gets a reverse pre-echo one 8th early (from V2 on)
        if i == 5 and bar0 >= 25:
            pe = reverse_prehit(sig)
            MIX.add("fx", pe * 0.28, at - 0.288, 1.0, pan, room=0, hall=0.4)


def groove_bar(bar, energy=1.0, ghost=False):
    g = 0.55 if ghost else 1.0
    MIX.add("drums", war_kick(0.95 * energy * g), bt(bar, 0), 1.0, 0.5, room=0.12, hall=0.05, jitter_ms=4)
    MIX.add("drums", war_kick(0.85 * energy * g), bt(bar, 2), 1.0, 0.5, room=0.12, hall=0.05, jitter_ms=4)
    MIX.add("drums", deep_tom(100, 0.7 * energy * g), bt(bar, 1), 1.0, 0.5, room=0.15, hall=0.05, jitter_ms=6)
    MIX.add("drums", deep_tom(90, 0.7 * energy * g), bt(bar, 3), 1.0, 0.5, room=0.15, hall=0.05, jitter_ms=6)
    # mid layer, Witek sweet-spot displaced 16ths, humanized
    patt = [4, 7, 11, 14] if bar % 2 == 0 else [3, 7, 10, 15]
    for s in patt:
        MIX.add("drums", taiko(88, 0.32 * energy * g), bt(bar, s * 0.25), 1.0,
                0.5 + 0.2 * np.sin(s), room=0.1, hall=0.04, jitter_ms=8, vel_var_db=1.5)


def bass_bar(bar, energy=1.0):
    # rootless pulse A1-C2-A1-G1 (D withheld)
    seq = ["A1", "C2", "A1", "G1"]
    nm = seq[(bar - 1) % 4]
    MIX.add("bass", sub_bass(nm, BAR * 0.9, 0.7 * energy), bt(bar, 0), 1.0, 0.5, hall=0.03)
    for b in [1.5, 2.5, 3.5]:                       # offbeat octave pops
        f = note(nm[:-1] + str(int(nm[-1]) + 1))
        MIX.add("bass", sub_bass(nm[:-1] + str(int(nm[-1]) + 1), 0.4, 0.3 * energy),
                bt(bar, b), 1.0, 0.5, hall=0.03, jitter_ms=5)


def pad_chord(bar, freqs, nbars, gain=0.2, room=0.05, hall=0.35, dec=True):
    dur = nbars * BAR
    for f in freqs:
        sig = organ([f], dur, gain=gain)
        if dec:
            L, R = decorrelate(sig, 0.7)
            MIX.add("pads", np.stack([L, R]), bt(bar), 1.0, 0.5, room=room, hall=hall)
        else:
            MIX.add("pads", sig, bt(bar), 1.0, 0.5, room=room, hall=hall)


print("building RESIDUA ...")

# ---- SEED (bars 1-8): phantom D, void, ticks, hook tease ----
MIX.add("pads", phantom(8 * BAR, PHANTOM_D, gain=0.45), bt(1), 1.0, 0.5, hall=0.4)
MIX.add("fx", thing.missing_room(8 * BAR, 97.5, 0.32), bt(1), 1.0, 0.5, hall=0.4)
for k, (at, pan) in enumerate([(bt(2), 0.2), (bt(4, 2), 0.8), (bt(6, 1), 0.5)]):
    cl, cr = thing.cribra(0.4, 0.4)
    MIX.add("fx", np.stack([cl, cr]), at, 0.7, 0.5, hall=0.3)
# T1 tease: hook bars 1-2 as faint lead, no drums
play_hook(3, lead, 0.16, trunc=4, room=0.05, hall=0.5)

# ---- FIRST STATEMENT (9-20): hook C, V1; heartbeat; mantle on A1 ----
MIX.add("pads", phantom(12 * BAR, PHANTOM_D, gain=0.4), bt(9), 1.0, 0.5, hall=0.35)
MIX.add("bass", thing.mantle(8 * BAR, 0.3), bt(13), 1.0, 0.5, hall=0.05)  # A-region breather
play_hook(9, rw_lead, 0.42, room=0.1, hall=0.3)               # C (canonical)
play_hook(13, rw_lead, 0.44, room=0.1, hall=0.3)             # V1
MIX.add("voices", choir([note("A3"), note("D4"), note("F4")], 8 * BAR, 0.09), bt(13), 1.0, 0.5, hall=0.4)
for bar in range(9, 21):
    MIX.add("drums", war_kick(0.6), bt(bar, 0), 1.0, 0.5, room=0.1, hall=0.04)
    MIX.add("drums", war_kick(0.5), bt(bar, 2), 1.0, 0.5, room=0.1, hall=0.04)

# ---- GROOVE (21-36): full kit, bass, Pneuma bed, hook V2 V3 ----
for bar in range(21, 37):
    groove_bar(bar, 1.0); bass_bar(bar, 1.0)
MIX.add("pads", phantom(16 * BAR, PHANTOM_D, gain=0.32), bt(21), 1.0, 0.5, hall=0.3)
MIX.add("fx", thing.psithura(16 * BAR, 0.14), bt(21), 1.0, 0.62, hall=0.2)   # Pneuma-ish breath bed
play_hook(25, rw_lead, 0.46, room=0.1, hall=0.28)                 # V2 (pre-echo begins)
play_hook(33, rw_lead, 0.46, room=0.1, hall=0.28)                 # V3
MIX.add("voices", choir([note("A3"), note("D4"), note("F4")], 16 * BAR, 0.08), bt(21), 1.0, 0.5, hall=0.4)

# ---- FILL + THEFT / false drop (37-40) ----
for j, s in enumerate(np.linspace(0, 4, 12)):       # accelerating fill, bar 37
    MIX.add("drums", taiko(120 - j * 4, 0.7), bt(37, s), 1.0, 0.5, room=0.12)
# bars 38-40: strip to near-silence (the stolen drop)
MIX.add("pads", phantom(3 * BAR, PHANTOM_D, gain=0.3), bt(38), 1.0, 0.5, hall=0.4)
MIX.add("fx", thing.missing_room(3 * BAR, 97.5, 0.3), bt(38), 1.0, 0.5, hall=0.4)
MIX.add("fx", thing.pleura(3 * BAR, 0.35), bt(38), 1.0, 0.5, hall=0.2)

# ---- C1 THE VISITOR (41-52): solo voice in Bbm -> chorus fusion -> bloom ----
MIX.add("pads", phantom(12 * BAR, PHANTOM_D, gain=0.28), bt(41), 1.0, 0.5, hall=0.4)
# solo vox_glottis sings hook notes 1-5 transposed to Bb minor (chromatic mediant)
bbm_hook = [("Bb2", 0, 1.5), ("C3", 1.5, 0.5), ("Db3", 2, 2), ("C3", 4, 1), ("F2", 5, 3)]
for i, (nm, b, d) in enumerate(bbm_hook):
    MIX.add("voices", thing.vox_glottis(d * BEAT, note(nm), 0.42), bt(41, b),
            1.0, 0.5, room=0.08, hall=0.15, jitter_ms=5)
# +9.2s bloom (bar 45, the leap): chorus_many fuses, hall opens, width expands
bloom = thing.chorus_many(6 * BAR, note("Db4"), gain=0.5, nvoices=16)
bL, bR = decorrelate(bloom, 1.4)
MIX.add("voices", np.stack([bL, bR]), bt(45), 1.0, 0.5, room=0.05, hall=0.55)
MIX.add("bass", thing.mantle(6 * BAR, 0.3), bt(45), 1.0, 0.5, hall=0.05)     # A1->Gb1 feel
MIX.add("voices", choir([note("Gb2"), note("Db3"), note("Bb3"), note("F4")], 4 * BAR, 0.14), bt(45), 1.0, 0.5, hall=0.5)
# bar 52 beat 1: the Visitor's closing bell — captured for Tessera
BELL52 = thing.revenant_bell(4.0, thing.PRIME, 0.55, seed=52)
MIX.add("fx", BELL52, bt(52), 1.0, 0.5, room=0.1, hall=0.45)

# ---- THE EYE (53-61): Tessera bed from the bell tail; cold bell; whispers ----
bell_tail = BELL52[int(1.5 * SR):]                  # last ~2.5s of the strike
tess = tessera(bell_tail, 9 * BAR, [note("G3"), note("Bb3"), note("D4"), note("A3")], 0.32)
tL, tR = decorrelate(tess, 0.6)
MIX.add("pads", np.stack([tL, tR]), bt(53), 1.0, 0.5, hall=0.4)
MIX.add("pads", phantom(9 * BAR, PHANTOM_D, gain=0.2), bt(53), 1.0, 0.5, hall=0.4)
MIX.add("voices", thing.cold_bell_larynx(9 * BAR, thing.QUINT, 0.32), bt(53), 1.0, 0.5, hall=0.45)
MIX.add("fx", thing.psithura(9 * BAR, 0.3), bt(53), 1.0, 0.6, room=0.05, hall=0.1)
# F1: fragmented, inverted hook, never completes
for (nm, b) in [("A3", 0), ("F3", 3), ("D3", 6), ("Eb3", 10)]:
    MIX.add("voices", lead(note(nm), 2.2, 0.22, bright=2600), bt(54, b), 1.0, 0.55, hall=0.4)
# bars 57-58 THE PRIVATE RESOLUTION: cold-bell C#3->D3 pp + true D2 fades in <=-42dB
MIX.add("voices", thing.cold_bell_larynx(1.5, note("C#3"), 0.14), bt(57, 2), 1.0, 0.5, hall=0.4)
MIX.add("voices", lead(note("D3"), 2.0, 0.14, bright=2400), bt(58), 1.0, 0.5, hall=0.4)
MIX.add("bass", sub_bass("D2", 2 * BAR, 0.05), bt(57), 1.0, 0.5, hall=0.02)   # phantom granted, pp, then withdrawn

# ---- DREAD BUILD (62-68): Bb pedal, accel drums, Shepard, phantom mod D->Eb ----
MIX.add("pads", organ([note("Bb1"), note("Bb2"), note("F3")], 7 * BAR, 0.24), bt(62), 1.0, 0.5, hall=0.3)
MIX.add("pads", phantom(7 * BAR, PHANTOM_D, PHANTOM_EB, gain=0.3), bt(62), 1.0, 0.5, hall=0.3)  # phantom modulation
MIX.add("fx", thing.stairwell(7 * BAR, 0.3), bt(62), 1.0, 0.5, hall=0.3)     # dark Shepard
MIX.add("pads", thing.split_horizon(7 * BAR, 0.28), bt(62), 1.0, 0.5, hall=0.2)
# F2 ostinato: hook notes 1-3, looping, never completes
for bar in range(62, 69):
    for (nm, b, d) in [("D3", 0, 1), ("E3", 1, 1), ("F3", 2, 2)]:
        MIX.add("voices", lead(note(nm), d * BEAT, 0.2, bright=2600), bt(bar, b), 1.0, 0.5, hall=0.2)
# accelerating war drums 8ths -> 16ths (bars 62/64/66), backbeat dropped bar 67
for bi, bar in enumerate(range(62, 69)):
    div = [2, 2, 4, 4, 8, 8, 8][bi]
    for s in range(div):
        MIX.add("drums", taiko(92, 0.6 + 0.05 * bi), bt(bar, s * 4 / div), 1.0, 0.5, room=0.12, jitter_ms=5)
    if bar != 67:
        MIX.add("drums", deep_tom(95, 0.7), bt(bar, 2), 1.0, 0.5, room=0.14)
# bar 68 THE BLAZE: A major with C#4 exposed (the 2nd and last C#) — false promise
for nm in ["A2", "E3", "A3", "C#4", "E4"]:
    MIX.add("pads", horn(note(nm), 1.6, 0.34), bt(68), 1.0, 0.5, room=0.05, hall=0.25)
    MIX.add("pads", organ([note(nm)], 1.6, 0.2), bt(68), 1.0, 0.5, hall=0.2)

# ---- THE SILENCE (bar 69 beat 1, ~577ms) — golden section ----
# nothing scheduled here except a dry caught-breath + rising reversed pre-echo
MIX.add("fx", thing.pleura(0.5, 0.3, caught=True), bt(69), 0.5, 0.5, hall=0.0)

# ---- C2 THE ONE (69.5-78): the hit, Eb major (bII), then hoarded bII->i to D ----
HIT_AT = bt(69) + 1.0 * BEAT                          # one beat late
# build the tutti Eb-major hit
eb_voice = choir([note("Eb2"), note("Bb2"), note("Eb3"), note("G3"), note("Bb3"), note("Eb4")], 8 * BAR, 0.16)
hL, hR = decorrelate(eb_voice, 1.5)
MIX.add("voices", np.stack([hL, hR]), HIT_AT, 1.0, 0.5, room=0.04, hall=0.5)
for nm in ["Eb2", "Bb2", "G3", "Bb3", "Eb4"]:
    MIX.add("pads", organ([note(nm)], 8 * BAR, 0.14), HIT_AT, 1.0, 0.5, hall=0.35)
    MIX.add("pads", horn(note(nm), 2.0, 0.28), HIT_AT, 1.0, 0.5, hall=0.3)
MIX.add("bass", sub_bass("Eb1", 2 * BAR, 0.85), HIT_AT, 1.0, 0.5, hall=0.03)   # first sub departure
MIX.add("fx", thing.revenant_bell(6.0, thing.PRIME, 0.5, seed=69), HIT_AT, 1.0, 0.5, hall=0.5)
# reversed pre-echo of the hit, rising into the downbeat
pre = reverse_prehit(eb_voice[:int(0.4 * SR)])
MIX.add("fx", pre * 0.3, HIT_AT - 0.45, 1.0, 0.5, hall=0.3)
# the silence itself: fade everything before HIT (handled by not scheduling; declick covers edges)
# V5: hook octave-up at bar 71 — the HOARDED RESOLUTION: bII->i, first true D bass
play_hook(71, rw_lead, 0.5, octv=1, room=0.08, hall=0.3)
play_hook(71, rw_lead, 0.3, octv=0, room=0.08, hall=0.3)
MIX.add("bass", sub_bass("D2", BAR, 0.8), bt(71), 1.0, 0.5, hall=0.03)          # FIRST true D fundamental
MIX.add("bass", sub_bass("D1", BAR, 0.7), bt(71, 2), 1.0, 0.5, hall=0.03)
for bar in range(71, 79):
    groove_bar(bar, 1.15); bass_bar(bar, 1.1)
MIX.add("voices", choir([note("D4"), note("F4"), note("A4")], 8 * BAR, 0.14), bt(71), 1.0, 0.5, hall=0.4)
play_hook(75, rw_lead, 0.48, octv=1, room=0.08, hall=0.3)            # V6

# ---- AFTERGLOW / FRAGMENTATION (79-84) ----
frag = thing.chorus_many(6 * BAR, note("D4"), gain=0.4, nvoices=16)
fL, fR = decorrelate(frag, 1.2)
MIX.add("voices", np.stack([fL, fR]), bt(79), 1.0, 0.5, hall=0.45)
pad_chord(79, [note("D3"), note("F3"), note("A3")], 2, 0.16)
pad_chord(81, [note("Bb2"), note("D3"), note("F3"), note("A3")], 2, 0.16)
pad_chord(83, [note("G2"), note("Bb2"), note("D3")], 2, 0.16)
for bar in range(79, 85):
    MIX.add("drums", war_kick(0.6), bt(bar, 0), 1.0, 0.5, room=0.1)
    MIX.add("drums", war_kick(0.5), bt(bar, 2), 1.0, 0.5, room=0.1)

# ---- RECESSION (85-96): ghost half-time, hook callback, distant chant ----
MIX.add("pads", phantom(12 * BAR, PHANTOM_D, gain=0.2), bt(85), 1.0, 0.5, hall=0.4)
for bar in range(85, 97):
    groove_bar(bar, 0.5, ghost=True)
play_hook(85, rw_lead, 0.32, room=0.05, hall=0.5)                    # distant callback
for (nm, b) in [("D3", 0), ("F3", 4), ("E3", 8), ("D3", 12)]:                   # hall-drowned chant
    MIX.add("voices", choir([note(nm)], 3 * BEAT, 0.1), bt(89, b), 1.0, 0.5, hall=0.6)

# ---- C3 THE LAST BREATH (97-104): solo voice, truncated hook W ----
MIX.add("pads", phantom(8 * BAR, PHANTOM_D, gain=0.2), bt(97), 1.0, 0.5, hall=0.45)
MIX.add("pads", organ([note("G2"), note("Bb2"), note("D3")], 4 * BAR, 0.16), bt(97), 1.0, 0.5, hall=0.4)
# hook W: truncated on note 7 (Eb3); pre-echo for note 8 fires; note 8 never sounds
for i, (nm, b, d) in enumerate(HOOK[:7]):
    intel = 0.55 + 0.3 * (i / 7)        # Glossa: grows toward intelligibility
    MIX.add("voices", thing.vox_glottis(d * BEAT, note(nm), 0.34), bt(97, b),
            1.0, 0.5, room=0.08, hall=0.2, jitter_ms=5)
    if i == 5:                          # soft bVI bloom at the leap
        MIX.add("pads", organ([note("Bb2"), note("D3"), note("F3")], 2 * BAR, 0.14), bt(97, b), 1.0, 0.5, hall=0.4)
# the orphaned note-8 pre-echo, then silence where note 8 should be
note8 = lead(note("E3"), 1.0, 0.3)
MIX.add("fx", reverse_prehit(note8) * 0.28, bt(97, 12) - 0.288, 1.0, 0.5, hall=0.4)
MIX.add("fx", thing.revenant_bell(18.0, thing.PRIME, 0.5, seed=104), bt(101), 1.0, 0.5, hall=0.55)

# ---- TAIL + REPLAY SEAM (105-110): tonic granted then revoked; seam to bar 1 ----
MIX.add("pads", phantom(6 * BAR, PHANTOM_D, gain=0.22), bt(105), 1.0, 0.5, hall=0.45)
MIX.add("bass", sub_bass("D2", 3 * BAR, 0.16), bt(105), 1.0, 0.5, hall=0.03)    # true D granted...
MIX.add("bass", sub_bass("D2", 2 * BAR, 0.08), bt(108), 1.0, 0.5, hall=0.03)    # ...fading (revoked)
# seam: bars 109-110 echo the seed texture (same generators, faint)
MIX.add("pads", phantom(2 * BAR, PHANTOM_D, gain=0.3), bt(109), 1.0, 0.5, hall=0.4)
MIX.add("fx", thing.missing_room(2 * BAR, 97.5, 0.3), bt(109), 1.0, 0.5, hall=0.4)


# ============================================================ MASTER
def loudness_curve(n):
    # macro arc, ~20 dB range (audible troughs, dominant but not extreme peak);
    # the dread build CRESCENDOS into the golden-section silence.
    pts = [(0, -25), (18.5, -21), (40, -13), (60, -15),          # seed/statement/groove
           (78, -14), (88, -21),                                 # groove tail -> stolen drop
           (92, -24), (101.5, -12),                              # Visitor solo -> bloom
           (110, -19), (128, -22), (140, -20),                   # the Eye
           (143, -17), (155.5, -10),                             # DREAD BUILD crescendo
           (156.9, -55), (157.6, -5),                            # silence -> THE HIT
           (170, -7), (180, -12),                                # C2 sustain
           (188, -15), (200, -20), (205, -14), (218, -20),       # afterglow / recession / C3
           (240, -26), (260, -42)]                               # tail fade
    ts = np.array([p[0] for p in pts]); db = np.array([p[1] for p in pts])
    return 10 ** (np.interp(np.arange(n) / SR, ts, db) / 20.0)


def master():
    print("  bussing + dual reverb ...")
    n = MIX.n
    # sidechain env from the drum dry bus
    drum_mono = MIX.b["drums"]["dry"].mean(0)
    sc = 1 - 0.28 * dsp3.env_follow(drum_mono, 0.005, 0.22)
    sc = np.clip(sc, 0.6, 1.0)[None, :]

    room_send = sum(MIX.b[k]["room"] for k in MIX.b)
    hall_send = sum(MIX.b[k]["hall"] for k in MIX.b)
    room_wet = reverb_bus(room_send, "room")
    hall_wet = reverb_bus(hall_send, "hall")

    dry = np.zeros((2, n))
    for k in MIX.b:
        d = MIX.b[k]["dry"]
        if k in ("pads", "voices", "fx"):
            d = d * sc              # duck sustained material under the beat
        dry += d
    mix = dry + 0.9 * room_wet + 0.95 * hall_wet
    mix = mix * loudness_curve(n)

    out = []
    for ch in range(2):
        x = mix[ch]
        x = hp(x, 26, 4)
        x = tilt_cut(x, 2400, -2.5)          # tame harsh presence band
        x = tilt_cut(x, 3400, -3.5)          # spectral tilt (dark)
        x = lp(x, 15500, 4)
        x = soft_sat(x, 1.08, 0.2)
        x = bus_comp(x, thr=0.5, ratio=2.0)
        out.append(x)
    st = np.stack(out)
    st = mono_below(st, 130)                 # tight mono low end
    st = np.stack([limiter(st[0], 0.95), limiter(st[1], 0.95)])
    m = max(np.max(np.abs(st[0])), np.max(np.abs(st[1]))) + 1e-9
    st = st / m * 0.94
    fi = int(0.5 * SR); fo = int(5.0 * SR)
    for ch in (0, 1):
        st[ch, :fi] *= np.linspace(0, 1, fi)
        st[ch, -fo:] *= np.linspace(1, 0, fo) ** 1.4
    assert np.all(np.isfinite(st)), "non-finite output"
    return st


def write_wav(path, st):
    import wave
    data = (np.clip(st.T, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(data.tobytes())


if __name__ == "__main__":
    import sys
    st = master()
    out = sys.argv[1] if len(sys.argv) > 1 else "residua.wav"
    write_wav(out, st)
    print(f"wrote {out}  ({st.shape[1] / SR:.1f}s, stereo {SR}Hz)")
