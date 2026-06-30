"""
Catchy soundtrack engine v2  --  "addictive, not trance".

A dependency-light (numpy + scipy + stdlib wave) synth that renders a ~3 min
modern pop/electronic track engineered for catchiness and replay-craving,
grounded in the verified research (see ../REPORT.md):

  * dopaminergic ANTICIPATION -> RESOLUTION  -> multiple build/drop cycles
  * EARWORM recipe: conventional arch contour + a signature leap, repeated
    with subtle variation, left unresolved at the end (open loop)
  * the "Axis" minor vamp (i-VI-III-VII) -- one of the stickiest progressions
  * MOVEMENT over drone (chords change, bass walks, arps run) so it stays
    catchy rather than hypnotic
  * SIDECHAIN pump locked to the kick  = the modern "cool" groove feel

v2 priorities vs v1: catchier hooks, far more events (fills, risers, impacts,
arps, vocal-chop stabs, counter-melodies), real drum kit, harmonic motion.
"""

import struct
import wave

import numpy as np
from scipy.signal import butter, lfilter, sosfilt

SR = 44100
BPM = 122.0
BEAT = 60.0 / BPM
STEP = BEAT / 4.0          # 16th grid
BAR = BEAT * 4
ROOT = 220.0               # A3

# ---------------------------------------------------------------- note helpers
# 12-TET (catchiness lives in equal temperament), root A. Semitone offsets.
NOTE = {  # name -> semitones from A
    "A": 0, "A#": 1, "B": 2, "C": 3, "C#": 4, "D": 5, "D#": 6,
    "E": 7, "F": 8, "F#": 9, "G": 10, "G#": 11,
}


def hz(name, octave=0, cents=0.0):
    semis = NOTE[name] + 12 * octave + cents / 100.0
    return ROOT * 2 ** (semis / 12.0)


# ---------------------------------------------------------------- envelopes
def adsr(n, a=0.005, d=0.08, s=0.7, r=0.1, curve=2.0):
    a_n = max(1, int(a * SR)); d_n = max(1, int(d * SR)); r_n = max(1, int(r * SR))
    if a_n + d_n + r_n >= n:
        env = np.ones(n)
        h = max(1, n // 6)
        env[:h] = np.linspace(0, 1, h)
        env[-h:] = np.linspace(env[-h], 0, h)
        return env
    sus_n = n - a_n - d_n - r_n
    env = np.empty(n)
    env[:a_n] = np.linspace(0, 1, a_n)
    env[a_n:a_n + d_n] = s + (1 - s) * (np.linspace(1, 0, d_n) ** curve)
    env[a_n + d_n:a_n + d_n + sus_n] = s
    env[a_n + d_n + sus_n:] = s * (np.linspace(1, 0, r_n) ** curve)
    return env


def perc_env(n, decay=12.0):
    t = np.linspace(0, 1, n)
    return np.exp(-t * decay)


def t_of(dur):
    return np.arange(int(dur * SR)) / SR


# ---------------------------------------------------------------- filters
def lowpass(x, cutoff, order=4):
    cutoff = max(20.0, min(cutoff, SR / 2 - 100))
    sos = butter(order, cutoff / (SR / 2), btype="low", output="sos")
    return sosfilt(sos, x)


def highpass(x, cutoff, order=2):
    cutoff = max(20.0, min(cutoff, SR / 2 - 100))
    sos = butter(order, cutoff / (SR / 2), btype="high", output="sos")
    return sosfilt(sos, x)


def env_lowpass(x, c_start, c_end, order=3):
    """Time-varying lowpass (filter sweep) -- approximated by crossfading a
    few static bands. Cheap but gives the 'opening filter' rise that makes
    builds feel cool."""
    n = len(x)
    bands = 12
    out = np.zeros(n)
    cs = np.linspace(c_start, c_end, bands)
    win = n // bands
    for i, c in enumerate(cs):
        seg = slice(i * win, (i + 1) * win if i < bands - 1 else n)
        out[seg] = lowpass(x, c, order)[seg]
    return out


def soft_clip(x, drive=1.0):
    return np.tanh(x * drive)


# ---------------------------------------------------------------- oscillators
def _phase(freq, dur):
    return 2 * np.pi * freq * t_of(dur)


def saw(freq, dur, harmonics=None):
    """Fast phase-based ramp saw in [-1, 1]. Aliasing above the (always
    applied) lowpass is inaudible, and this renders ~100x faster than the
    additive sum -- crucial for iterating on the arrangement."""
    t = t_of(dur)
    p = t * freq
    return 2.0 * (p - np.floor(0.5 + p))


def square(freq, dur, harmonics=None):
    t = t_of(dur)
    p = t * freq
    return np.where((p - np.floor(p)) < 0.5, 1.0, -1.0)


def sine(freq, dur):
    return np.sin(_phase(freq, dur))


def supersaw(freq, dur, voices=7, detune=0.18, harmonics=None):
    """Detuned stacked saws -> the big, lush, 'cool' EDM lead/chord sound."""
    t = t_of(dur)
    out = np.zeros(len(t))
    spread = np.linspace(-detune, detune, voices)
    for i, d in enumerate(spread):
        f = freq * 2 ** (d / 12.0)
        p = t * f + i * 0.13      # per-voice phase offset -> thick unison
        out += 2.0 * (p - np.floor(0.5 + p))
    return out / voices * 1.3


def fm(freq, dur, ratio=2.0, index=4.0, idx_decay=4.0):
    """2-op FM -> bell/pluck/metallic tones. index decays for a pluck attack."""
    t = t_of(dur)
    mod = np.sin(2 * np.pi * freq * ratio * t) * index * np.exp(-t * idx_decay)
    return np.sin(2 * np.pi * freq * t + mod)


# ---------------------------------------------------------------- drum kit
def kick(dur=0.4, amp=1.0, punch=1.0):
    t = t_of(dur)
    pitch = (160 * punch) * np.exp(-t * 32) + 48
    phase = 2 * np.pi * np.cumsum(pitch) / SR
    body = np.sin(phase) * np.exp(-t * 7.5)
    click = (np.random.uniform(-1, 1, len(t)) * np.exp(-t * 800)) * 0.5
    return amp * soft_clip(body + click, 1.5)


def snare(dur=0.22, amp=1.0):
    t = t_of(dur)
    tone = (np.sin(2 * np.pi * 190 * t) + np.sin(2 * np.pi * 280 * t)) * np.exp(-t * 22)
    noise = highpass(np.random.uniform(-1, 1, len(t)), 1500) * np.exp(-t * 18)
    return amp * soft_clip(0.5 * tone + 0.9 * noise, 1.2)


def clap(dur=0.3, amp=1.0):
    n = int(dur * SR)
    out = np.zeros(n)
    noise = highpass(np.random.uniform(-1, 1, n), 1200)
    # 3 quick bursts + tail = the classic clap
    for off, g in [(0, 1.0), (0.009, 0.9), (0.018, 0.8)]:
        i = int(off * SR)
        env = np.zeros(n); env[i:] = np.exp(-np.linspace(0, 1, n - i) * 40)
        out += g * noise * env
    tail = noise * np.exp(-np.linspace(0, 1, n) * 12) * 0.5
    return amp * (out + tail)


def hat(dur=0.05, amp=0.5, open_=False):
    n = int(dur * SR)
    noise = highpass(np.random.uniform(-1, 1, n), 7000)
    env = np.exp(-np.linspace(0, 1, n) * (6 if open_ else 28))
    return amp * noise * env


def crash(dur=1.6, amp=0.7):
    n = int(dur * SR)
    noise = highpass(np.random.uniform(-1, 1, n), 4000)
    env = np.exp(-np.linspace(0, 1, n) * 3.5)
    return amp * noise * env


def tom(freq=160, dur=0.28, amp=0.8):
    t = t_of(dur)
    pitch = freq * (1 + 0.6 * np.exp(-t * 20))
    phase = 2 * np.pi * np.cumsum(pitch) / SR
    return amp * np.sin(phase) * np.exp(-t * 9)


def riser(dur, amp=0.6, kind="noise"):
    n = int(dur * SR)
    t = np.linspace(0, 1, n)
    if kind == "noise":
        x = np.random.uniform(-1, 1, n)
        x = env_lowpass(x, 300, 12000)
        env = t ** 2
        return amp * x * env
    # tonal uplifter: rising sine sweep
    f = 200 * 2 ** (t * 4)
    phase = 2 * np.pi * np.cumsum(f) / SR
    return amp * np.sin(phase) * (t ** 1.5)


def downlifter(dur=1.2, amp=0.5):
    n = int(dur * SR)
    t = np.linspace(0, 1, n)
    f = 1800 * 2 ** (-t * 4)
    phase = 2 * np.pi * np.cumsum(f) / SR
    return amp * np.sin(phase) * np.exp(-t * 1.5)


def snare_roll(bars, bar_i, gain=0.5):
    """Accelerating snare roll into a drop -- a huge anticipation device."""
    events = []
    divs = [4, 4, 8, 8, 16, 16]  # subdivisions per beat, accelerating
    pos = 0.0
    for beat_i in range(int(bars * 4)):
        div = divs[min(beat_i, len(divs) - 1)]
        for j in range(div):
            t = (bar_i * 4 + beat_i) * BEAT + j * (BEAT / div)
            g = gain * (0.5 + 0.5 * (beat_i / (bars * 4)))
            events.append((t, g))
    return events


# ---------------------------------------------------------------- mix bus
class Bus:
    def __init__(self, total_sec):
        self.n = int(total_sec * SR)
        self.L = np.zeros(self.n)
        self.R = np.zeros(self.n)

    def add(self, sig, at_sec, gain=1.0, pan=0.5):
        i = int(at_sec * SR)
        if i >= self.n:
            return
        j = min(self.n, i + len(sig))
        seg = sig[:j - i]
        self.L[i:j] += gain * (1 - pan) * 2 ** 0.5 * seg * 0.7071
        self.R[i:j] += gain * pan * 2 ** 0.5 * seg * 0.7071


def make_sidechain(total_sec, kick_times, depth=0.85, attack=0.004, release=0.18):
    """Volume-duck envelope that dips on each kick and recovers -> pump."""
    n = int(total_sec * SR)
    env = np.ones(n)
    a_n = int(attack * SR); r_n = int(release * SR)
    duck = np.concatenate([
        np.linspace(1, 1 - depth, a_n),
        1 - depth + depth * (1 - np.exp(-np.linspace(0, 5, r_n))),
    ])
    for kt in kick_times:
        i = int(kt * SR)
        if i >= n:
            continue
        j = min(n, i + len(duck))
        env[i:j] = np.minimum(env[i:j], duck[:j - i])
    return env


def delay(sig, time, feedback=0.35, mix=0.3, n_echo=6):
    out = sig.copy()
    d = int(time * SR)
    for k in range(1, n_echo + 1):
        g = mix * feedback ** (k - 1)
        shifted = np.zeros_like(sig)
        if d * k < len(sig):
            shifted[d * k:] = sig[:-d * k]
        out += g * shifted
    return out


def _comb(x, d, g):
    """Feedback comb y[n]=x[n]+g*y[n-d], computed fast: the d interleaved
    phase groups are each a cheap 1st-order IIR (len-2 denominator)."""
    out = np.empty_like(x)
    for r in range(d):
        out[r::d] = lfilter([1.0], [1.0, -g], x[r::d])
    return out


def reverb(sig, mix=0.2, decay=0.5):
    out = sig.copy()
    for dl, g in [(0.0297, 0.78), (0.0371, 0.74), (0.0411, 0.7), (0.0437, 0.66)]:
        d = int(dl * SR)
        out += mix * _comb(sig, d, g * decay)
    return out / (1 + mix * 4)


# ============================================================ COMPOSITION
CHORDS = {
    "Am": ["A", "C", "E"],
    "F":  ["F", "A", "C"],
    "C":  ["C", "E", "G"],
    "G":  ["G", "B", "D"],
}
SEQ = ["Am", "F", "C", "G"]          # the "Axis" minor vamp -- maximally sticky
BASS_ROOT = {"Am": "A", "F": "F", "C": "C", "G": "G"}

# Earworm hook: identical rhythm every bar (sticky), an arch contour that
# LEAPS up to a long held "peak" note (step 4) -- and that peak gets a small
# +15-cent "alien" lean for identity. (name, octave, step, len_steps)
HOOK = [
    # bar 0 (Am)
    [("E", 1, 0, 3), ("A", 1, 3, 1), ("C", 2, 4, 4), ("B", 1, 8, 2), ("A", 1, 10, 2), ("E", 1, 12, 4)],
    # bar 1 (F)
    [("F", 1, 0, 3), ("A", 1, 3, 1), ("C", 2, 4, 4), ("A", 1, 8, 2), ("F", 1, 10, 2), ("C", 2, 12, 4)],
    # bar 2 (C)
    [("G", 1, 0, 3), ("C", 2, 3, 1), ("E", 2, 4, 4), ("D", 2, 8, 2), ("C", 2, 10, 2), ("G", 1, 12, 4)],
    # bar 3 (G)
    [("G", 1, 0, 3), ("B", 1, 3, 1), ("D", 2, 4, 4), ("B", 1, 8, 2), ("G", 1, 10, 2), ("D", 2, 12, 4)],
]
# call-and-response answer phrase (sparse, an octave up, fills the gaps)
RESP = [
    [("A", 2, 14, 2)], [("C", 3, 14, 2)], [("E", 3, 14, 2)], [("D", 3, 13, 3)],
]


def render():
    np.random.seed(11)
    total_bars = 96
    total_sec = total_bars * BAR + 4.0
    drums = Bus(total_sec)   # dry
    pump = Bus(total_sec)    # bass + chords (heavy sidechain)
    music = Bus(total_sec)   # lead + arp + vox (light sidechain)
    kick_times = []
    SWING = 0.045 * STEP

    def st(bar, step):
        tt = bar * BAR + step * STEP
        return tt + (SWING if step % 2 == 1 else 0.0)

    def add_wide(bus, sig, at, gain, haas_ms=11, spread=0.85):
        """Haas-style stereo widener: same signal, tiny delay on one side,
        panned apart -> the big 'cool' wide pad/lead image."""
        d = int(haas_ms / 1000 * SR)
        bus.add(sig, at, gain, pan=1 - spread)
        sigR = np.concatenate([np.zeros(d), sig[:-d]]) if d < len(sig) else sig
        bus.add(sigR, at, gain, pan=spread)

    # ----------------------------------------------------------- instruments
    def i_bass(name, octv, dur_steps, bar, step, gain=0.9):
        f = hz(name, octv)
        dur = dur_steps * STEP * 0.96
        n = int(dur * SR)
        s = lowpass(saw(f, dur, 14), 900)
        sub = sine(f / 2, dur) * 0.9
        env = adsr(n, 0.004, 0.06, 0.8, 0.05)
        w = (0.7 * s[:n] + sub[:n]) * env
        pump.add(soft_clip(w, 1.3), st(bar, step), gain, 0.5)

    def i_chord(chord, dur_steps, bar, step, gain=0.5, bright=2600, octv=0, stab=False):
        freqs = [hz(t, octv) for t in CHORDS[chord]]
        dur = dur_steps * STEP * (0.5 if stab else 1.0)
        n = int(dur * SR)
        w = np.zeros(n)
        for f in freqs:
            ss = supersaw(f, dur, voices=5, detune=0.13)
            w += ss[:n]
        w = highpass(lowpass(w, bright), 180)   # carve low-mids -> bass+lead breathe
        env = adsr(n, 0.004 if stab else 0.02, 0.12, 0.2 if stab else 0.7,
                   0.08 if stab else 0.25)
        add_wide(pump, w * env / len(freqs), st(bar, step), gain)

    def i_lead(name, octv, dur_steps, bar, step, gain=0.5, pan=0.5, alien=0.0):
        f = hz(name, octv, cents=alien)
        dur = dur_steps * STEP * 0.98
        n = int(dur * SR)
        w = lowpass(supersaw(f, dur, voices=7, detune=0.16), 5200)
        env = adsr(n, 0.008, 0.1, 0.78, 0.07)
        w = delay(w[:n] * env, BEAT * 0.75, feedback=0.28, mix=0.16)
        add_wide(music, w, st(bar, step), gain, haas_ms=7, spread=0.72)

    def i_pluck(name, octv, dur_steps, bar, step, gain=0.45, pan=0.5):
        f = hz(name, octv)
        dur = max(dur_steps * STEP, 0.2)
        n = int(dur * SR)
        w = 0.7 * fm(f, dur, ratio=2.0, index=3.2, idx_decay=9) + 0.3 * saw(f, dur, 12)
        env = adsr(n, 0.002, 0.13, 0.0, 0.09)
        music.add(lowpass(w[:n], 5200) * env, st(bar, step), gain, pan)

    def i_arp(name, octv, bar, step, gain=0.32, pan=0.5):
        i_pluck(name, octv, 1, bar, step, gain, pan)

    def i_vox(name, octv, dur_steps, bar, step, gain=0.5, pan=0.5):
        f = hz(name, octv)
        dur = dur_steps * STEP
        n = int(dur * SR)
        base = saw(f, dur, 30)[:n]

        def bp(x, lo, hi):
            sos = butter(2, [lo / (SR / 2), hi / (SR / 2)], btype="band", output="sos")
            return sosfilt(sos, x)
        form = 1.0 * bp(base, 600, 1000) + 0.7 * bp(base, 1100, 1600) + 0.6 * bp(base, 250, 500)
        env = adsr(n, 0.03, 0.1, 0.7, 0.12)
        w = delay(form * env, BEAT * 0.5, 0.22, 0.2)
        music.add(w * 0.7, st(bar, step), gain, pan)

    # ----------------------------------------------------------- drums
    def place(sample, bar, step, gain=1.0, pan=0.5):
        drums.add(sample, st(bar, step), gain, pan)

    def kick_at(bar, step, amp=0.95):
        tt = st(bar, step)
        drums.add(kick(amp=amp), tt, 1.0, 0.5)
        kick_times.append(tt)

    def drums_four(bar, energy=1.0, fill=False, ohat=True):
        for s in [0, 4, 8, 12]:
            kick_at(bar, s, 0.95 * energy)
        for s in [4, 12]:
            place(clap(), bar, s, 0.85 * energy)
        for s in range(1, 16, 2):
            place(hat(), bar, s, 0.26 * energy, pan=0.5 + 0.18 * np.sin(s))
        if ohat:
            for s in [2, 6, 10, 14]:
                place(hat(open_=True), bar, s, 0.2 * energy)
        if fill:
            for j, s in enumerate([12, 13, 14, 15]):
                place(tom(190 - j * 28, amp=0.85), bar, s, 0.85)

    def drums_verse(bar, energy=0.8):
        kick_at(bar, 0, 0.9 * energy); kick_at(bar, 7, 0.55 * energy); kick_at(bar, 10, 0.55 * energy)
        place(clap(), bar, 4, 0.7 * energy); place(clap(), bar, 12, 0.7 * energy)
        for s in range(2, 16, 4):
            place(hat(), bar, s, 0.22 * energy)

    def drums_half(bar, energy=0.9):
        kick_at(bar, 0, 1.0 * energy)
        place(snare(), bar, 8, 0.9 * energy)
        for s in [2, 6, 10, 14]:
            place(hat(), bar, s, 0.24 * energy)

    def roll_into(bar_lo, bars, gain=0.5):
        for tt, g in snare_roll(bars, bar_lo, gain):
            drums.add(snare(dur=0.14, amp=g), tt, 1.0, 0.5)

    # ----------------------------------------------------------- helpers
    def chord_of(bar):
        return SEQ[bar % 4]

    def play_bass(bar, energy=1.0, busy=True):
        c = chord_of(bar); root = BASS_ROOT[c]
        # (step, len, octave) -- octave bounce on the off-beats gives the
        # bassline movement/catch instead of a static root.
        pat = ([(0, 2, -1), (6, 2, 0), (8, 2, -1), (11, 1, 0), (14, 2, -1)]
               if busy else [(0, 4, -1), (8, 4, -1)])
        for s, ln, octv in pat:
            i_bass(root, octv, ln, bar, s, gain=0.85 * energy)

    def play_chords(bar, gain=0.5, bright=2600, stab=False, octv=0):
        c = chord_of(bar)
        if stab:
            for s in [0, 6, 10]:
                i_chord(c, 2, bar, s, gain=gain, bright=bright, stab=True, octv=octv)
        else:
            i_chord(c, 16, bar, 0, gain=gain, bright=bright, octv=octv)

    def play_hook(bar4_start, gain=0.5, octave_shift=0, response=False):
        for b in range(4):
            bar = bar4_start + b
            for (name, octv, step, ln) in HOOK[b]:
                i_lead(name, octv + octave_shift, ln, bar, step,
                       gain=gain, pan=0.5)
            if response:
                for (name, octv, step, ln) in RESP[b]:
                    i_lead(name, octv + octave_shift, ln, bar, step, gain=gain * 0.6, pan=0.62)

    def play_hook_pluck(bar4_start, gain=0.4):
        for b in range(4):
            bar = bar4_start + b
            for (name, octv, step, ln) in HOOK[b]:
                i_pluck(name, octv, max(ln, 1), bar, step, gain=gain, pan=0.42)

    def play_arp(bar, gain=0.3):
        tones = CHORDS[chord_of(bar)]
        seq = [(tones[0], 1), (tones[1], 1), (tones[2], 1), (tones[0], 2),
               (tones[1], 2), (tones[2], 2), (tones[0], 2), (tones[1], 1)] * 2
        for s in range(16):
            name, octv = seq[s]
            i_arp(name, octv, bar, s, gain=gain, pan=0.5 + 0.3 * np.sin(s * 1.3))

    def play_vox(bar, gain=0.5, octv=1):
        tones = CHORDS[chord_of(bar)]
        hits = [(0, tones[2], 2), (3, tones[0], 1), (6, tones[1], 2), (10, tones[2], 2), (12, tones[0], 3)]
        for s, name, ln in hits:
            i_vox(name, octv, ln, bar, s, gain=gain, pan=0.5 + 0.12 * np.sin(s))

    def crash_at(bar):
        # impact stack: crash + sub-boom + noise hit -> the drop lands hard.
        drums.add(crash(), bar * BAR, 0.55, 0.5)
        nb = int(1.2 * SR)
        boom = sine(46, 1.2) * np.exp(-np.linspace(0, 1, nb) * 4)
        drums.add(soft_clip(boom, 1.4) * 0.6, bar * BAR, 1.0, 0.5)
        nn = int(0.5 * SR)
        nz = highpass(np.random.uniform(-1, 1, nn), 3000) * np.exp(-np.linspace(0, 1, nn) * 7)
        drums.add(nz * 0.35, bar * BAR, 1.0, 0.5)

    def downlift(bar):
        music.add(downlifter(BAR * 0.9), bar * BAR, 0.4, 0.5)

    # ================================================ ARRANGEMENT (96 bars)
    # INTRO (0-7): atmosphere, opening filter, no beat -> tease.
    for bar in range(0, 8):
        play_chords(bar, gain=0.32, bright=900 + bar * 320)
    play_hook_pluck(4, gain=0.32)   # tease the hook quietly
    music.add(riser(BAR * 2, 0.28, "noise"), 6 * BAR, 0.5, 0.5)

    # VERSE A (8-15): groove, bass, plucked hook, sparse vox.
    for bar in range(8, 16):
        drums_verse(bar, energy=0.85)
        play_bass(bar, energy=0.85, busy=True)
        play_chords(bar, gain=0.3, bright=2200, stab=True)
    play_hook_pluck(8, gain=0.42); play_hook_pluck(12, gain=0.42)
    for bar in [10, 11, 14, 15]:
        play_vox(bar, gain=0.32)

    # PREDROP 1 (16-19): build + accelerating snare roll + riser, beat cuts out.
    for bar in range(16, 19):
        play_chords(bar, gain=0.34, bright=1500 + (bar - 16) * 900, stab=True)
        play_bass(bar, energy=0.8, busy=False)
    roll_into(16, 4, gain=0.45)
    music.add(riser(BAR * 4, 0.5, "noise"), 16 * BAR, 0.6, 0.5)
    music.add(riser(BAR * 3, 0.4, "tone"), 16 * BAR, 0.4, 0.5)
    downlift(19)

    # DROP 1 / CHORUS (20-35): full kit, sidechain pump, supersaw hook.
    crash_at(20)
    for bar in range(20, 36):
        drums_four(bar, energy=1.0, fill=(bar % 8 == 7), ohat=True)
        play_bass(bar, energy=1.0, busy=True)
        play_chords(bar, gain=0.42, bright=3200)
    for s in [20, 24, 28, 32]:
        play_hook(s, gain=0.52, response=(s >= 28))
    for bar in range(28, 36):
        play_arp(bar, gain=0.26)

    # VERSE B (36-43): strip back, NEW texture -> "more happening": vox-chop
    # lead, busier percussion, plucked counter-melody.
    for bar in range(36, 44):
        drums_verse(bar, energy=0.95)
        play_bass(bar, energy=0.95, busy=True)
        play_chords(bar, gain=0.3, bright=2400, stab=True)
        play_vox(bar, gain=0.5)
    play_hook_pluck(36, gain=0.4); play_hook_pluck(40, gain=0.4)
    for bar in range(40, 44):
        play_arp(bar, gain=0.22)

    # PREDROP 2 (44-47): bigger build.
    for bar in range(44, 47):
        play_chords(bar, gain=0.36, bright=1600 + (bar - 44) * 1000, stab=True)
        play_bass(bar, energy=0.85, busy=False)
    roll_into(44, 4, gain=0.55)
    music.add(riser(BAR * 4, 0.6, "noise"), 44 * BAR, 0.65, 0.5)
    music.add(riser(BAR * 4, 0.45, "tone"), 44 * BAR, 0.45, 0.5)
    downlift(47)

    # DROP 2 (48-67): biggest -> hook + arp + response + vox stacked.
    crash_at(48)
    for bar in range(48, 68):
        drums_four(bar, energy=1.1, fill=(bar % 8 == 7))
        play_bass(bar, energy=1.05, busy=True)
        play_chords(bar, gain=0.44, bright=3600)
        play_arp(bar, gain=0.24)
    for s in [48, 52, 56, 60, 64]:
        play_hook(s, gain=0.54, octave_shift=(1 if s >= 60 else 0), response=True)
    for bar in [50, 54, 58, 62, 66]:
        play_vox(bar, gain=0.34)

    # BRIDGE (68-75): half-time, emotional, breakdown -> reset before final.
    for bar in range(68, 76):
        drums_half(bar, energy=0.9)
        play_bass(bar, energy=0.7, busy=False)
        play_chords(bar, gain=0.4, bright=1800 + (bar - 68) * 180)
    play_hook(68, gain=0.4)
    for bar in [70, 71, 74, 75]:
        play_vox(bar, gain=0.4, octv=1)
    roll_into(74, 2, gain=0.5)
    music.add(riser(BAR * 2, 0.5, "noise"), 74 * BAR, 0.6, 0.5)

    # FINAL DROP (76-91): everything, octave-up hook, max energy.
    crash_at(76)
    for bar in range(76, 92):
        drums_four(bar, energy=1.15, fill=(bar % 8 == 7))
        play_bass(bar, energy=1.1, busy=True)
        play_chords(bar, gain=0.45, bright=3800)
        play_arp(bar, gain=0.28)
    for s in [76, 80, 84, 88]:
        play_hook(s, gain=0.56, octave_shift=1, response=True)
        play_hook(s, gain=0.3, octave_shift=0)
    for bar in range(76, 92):
        if bar % 2 == 0:
            play_vox(bar, gain=0.3)

    # OUTRO (92-95): filter down, hook echo left UNRESOLVED on the alien peak.
    for bar in range(92, 96):
        play_chords(bar, gain=0.34, bright=2600 - (bar - 92) * 550)
    play_hook_pluck(92, gain=0.4)
    # final hang on the 5th, no resolution to tonic -> the open-loop earworm tail
    i_lead("E", 2, 8, 95, 4, gain=0.5)

    # ============================================== MIX
    sc_pump = make_sidechain(total_sec, kick_times, depth=0.8)
    sc_music = make_sidechain(total_sec, kick_times, depth=0.35)
    L = drums.L + pump.L * sc_pump + music.L * sc_music
    R = drums.R + pump.R * sc_pump + music.R * sc_music
    L = reverb(L, mix=0.16); R = reverb(R, mix=0.16)
    L = highpass(L, 28); R = highpass(R, 28)
    stereo = np.stack([L, R])
    stereo = stereo / (np.max(np.abs(stereo)) + 1e-9) * 0.92
    stereo = soft_clip(stereo, 1.1)
    stereo = stereo / (np.max(np.abs(stereo)) + 1e-9) * 0.95
    fi = int(0.5 * SR); fo = int(3 * SR)
    stereo[:, :fi] *= np.linspace(0, 1, fi)
    stereo[:, -fo:] *= np.linspace(1, 0, fo)
    return stereo


def write_wav(path, stereo):
    data = (np.clip(stereo.T, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(data.tobytes())


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "soundtrack.wav"
    stereo = render()
    write_wav(out, stereo)
    print(f"wrote {out}  ({stereo.shape[1] / SR:.1f}s, stereo {SR}Hz)")
