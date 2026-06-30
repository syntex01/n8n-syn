"""
Psychoacoustic soundtrack engine.

A self-contained additive/subtractive synth (numpy + stdlib wave only) that
bakes in the effects surfaced by the deep-research sweep on what makes music
"addicting" and what lets genuinely novel ("alien") sound still click with the
human brain. Each effect is annotated in the section that implements it.

Design thesis: OPTIMAL SURPRISE. The reward system fires hardest on the
just-barely-resolvable, not the predictable or the random. So: alien skin,
human skeleton. Unfamiliar surface (7/11-limit just-intonation tuning,
inharmonic bell timbres) wrapped around universal hooks the brain locks onto
(entrainable pulse, anticipation->resolution arcs, the groove syncopation
sweet-spot, sub-bass body coupling, a sticky repeated melodic hook).
"""

import math
import struct
import wave

import numpy as np

SR = 44100


# ----------------------------------------------------------------------------
# Tuning  -- "alien but clicking"
# 7- and 11-limit just intonation. Pure harmonic-series ratios are MAXIMALLY
# consonant (low roughness -> the brain reads them as "in tune" / it clicks),
# yet the 7- and 11-limit steps (7/6, 11/8, 7/4) sit between the 12-TET cracks
# and sound distinctly alien to Western-trained ears. Consonant skeleton,
# unfamiliar surface.
# ----------------------------------------------------------------------------
RATIOS = {
    "1": 1 / 1, "9/8": 9 / 8, "7/6": 7 / 6, "5/4": 5 / 4,
    "11/8": 11 / 8, "3/2": 3 / 2, "7/4": 7 / 4, "2": 2 / 1,
    "9/4": 9 / 4, "5/2": 5 / 2, "3": 3 / 1, "7/2": 7 / 2,
}
BASE = 220.0  # A3 root


def hz(name, octave_shift=0):
    return BASE * RATIOS[name] * (2 ** octave_shift)


# ----------------------------------------------------------------------------
# Envelopes & helpers
# ----------------------------------------------------------------------------
def adsr(n, a=0.01, d=0.1, s=0.7, r=0.2):
    """Sample-accurate ADSR over n samples; times in seconds."""
    a_n = max(1, int(a * SR)); d_n = max(1, int(d * SR)); r_n = max(1, int(r * SR))
    env = np.zeros(n)
    if a_n + d_n + r_n >= n:
        # short note: just attack+release triangle
        h = n // 2
        env[:h] = np.linspace(0, 1, h)
        env[h:] = np.linspace(1, 0, n - h)
        return env
    sus_n = n - a_n - d_n - r_n
    env[:a_n] = np.linspace(0, 1, a_n)
    env[a_n:a_n + d_n] = np.linspace(1, s, d_n)
    env[a_n + d_n:a_n + d_n + sus_n] = s
    env[a_n + d_n + sus_n:] = np.linspace(s, 0, r_n)
    return env


def t_arr(dur):
    return np.arange(int(dur * SR)) / SR


def soft_clip(x, drive=1.0):
    return np.tanh(x * drive)


# ----------------------------------------------------------------------------
# Voices
# ----------------------------------------------------------------------------
def additive_tone(freq, dur, partials=8, inharm=0.0, decay=1.6,
                  detune=0.0, amp=1.0, env=None):
    """Additive voice. inharm>0 stretches partials -> bell/metallic ALIEN
    timbre (inharmonic spectra read as 'otherworldly' but stay pitched).
    inharm=0 -> pure harmonic series (singable, earworm-friendly lead).
    """
    t = t_arr(dur)
    out = np.zeros(len(t))
    for k in range(1, partials + 1):
        # stretched-partial inharmonicity (Fletcher-style) for alien color
        pf = freq * k * math.sqrt(1 + inharm * k * k)
        pf *= (1 + detune * (k - 1))
        out += (1.0 / (k ** decay)) * np.sin(2 * np.pi * pf * t)
    if env is None:
        env = adsr(len(t), 0.012, 0.18, 0.55, 0.25)
    return amp * out * env


def sub_bass(freq, dur, amp=1.0):
    """Low sine with a fast pitch-drop transient. Sub-bass (~40-70 Hz)
    couples to the body, not just the ear -- the felt, embodied pulse that
    drives entrainment and the urge to move."""
    t = t_arr(dur)
    pitch_env = freq * (1 + 1.5 * np.exp(-t * 30))  # click-y attack
    phase = 2 * np.pi * np.cumsum(pitch_env) / SR
    env = adsr(len(t), 0.004, 0.08, 0.6, 0.18)
    body = np.sin(phase)
    return amp * soft_clip(body * env, 1.4)


def kick(dur=0.32, amp=1.0):
    t = t_arr(dur)
    pitch = 110 * np.exp(-t * 26) + 42
    phase = 2 * np.pi * np.cumsum(pitch) / SR
    env = np.exp(-t * 9)
    click = np.exp(-t * 220) * 0.6
    return amp * soft_clip((np.sin(phase) + click) * env, 1.6)


def hat(dur=0.06, amp=0.5, lp=False):
    n = int(dur * SR)
    noise = np.random.uniform(-1, 1, n)
    # crude high-pass: subtract running mean
    k = 8
    sm = np.convolve(noise, np.ones(k) / k, mode="same")
    hp = noise - sm
    env = np.exp(-np.linspace(0, 1, n) * (18 if not lp else 9))
    return amp * hp * env


def noise_riser(dur, amp=0.6):
    """Filtered-noise sweep up in amplitude+brightness. The ANTICIPATION
    device: rising tension that primes a prediction the brain then craves to
    see resolved (ITPRA / reward-prediction)."""
    n = int(dur * SR)
    noise = np.random.uniform(-1, 1, n)
    bright = np.linspace(0.02, 1.0, n)  # open the filter over time
    out = np.zeros(n)
    prev = 0.0
    # one-pole low-pass with rising cutoff -> "opening" sweep
    for i in range(n):
        a = bright[i]
        prev = prev + a * (noise[i] - prev)
        out[i] = prev
    env = np.linspace(0, 1, n) ** 2
    return amp * out * env


# ----------------------------------------------------------------------------
# Effects
# ----------------------------------------------------------------------------
def am_entrain(sig, rate, depth=0.18):
    """Amplitude modulation at a fixed rate. REAL rhythmic entrainment (the
    auditory system tracks periodic amplitude envelopes) -- deliberately NOT
    the binaural-beats myth, which the verification pass flagged as weak."""
    t = np.arange(len(sig)) / SR
    lfo = 1 - depth + depth * np.sin(2 * np.pi * rate * t)
    return sig * lfo


def schroeder_reverb(sig, mix=0.25):
    """Cheap feedback-comb + allpass reverb for space/immersion."""
    out = sig.copy()
    for delay_ms, g in [(29.7, 0.78), (37.1, 0.74), (41.1, 0.7), (43.7, 0.66)]:
        d = int(delay_ms / 1000 * SR)
        buf = np.zeros(len(sig) + d)
        buf[:len(sig)] = sig
        for i in range(d, len(buf)):
            buf[i] += g * buf[i - d]
        out += mix * buf[:len(sig)]
    return out / (1 + mix * 4)


def stereo_widen(left, right, ms=12):
    d = int(ms / 1000 * SR)
    r = np.concatenate([np.zeros(d), right[:-d]]) if d < len(right) else right
    return left, r


# ----------------------------------------------------------------------------
# Sequencing
# ----------------------------------------------------------------------------
class Track:
    def __init__(self, total_sec):
        self.n = int(total_sec * SR)
        self.buf = np.zeros(self.n)

    def add(self, sig, at_sec, gain=1.0):
        i = int(at_sec * SR)
        j = min(self.n, i + len(sig))
        if i < self.n:
            self.buf[i:j] += gain * sig[:j - i]
        return self


def render():
    np.random.seed(7)  # determinism (Math.random/Date are unavailable anyway)
    BPM = 104
    beat = 60.0 / BPM
    step = beat / 4.0           # 16th-note grid
    bar = beat * 4
    swing = 0.055 * step        # microtiming: humanizing swing on off-beats

    TOTAL_BARS = 64
    TOTAL = TOTAL_BARS * bar + 6.0
    L = Track(TOTAL)
    R = Track(TOTAL)

    def step_time(bar_i, s):
        t = bar_i * bar + s * step
        if s % 2 == 1:          # swing the off-16ths
            t += swing
        return t

    # ----- The HOOK (earworm): compact arch contour + a distinctive leap.
    # Sticky melodies tend to be a rising-then-falling arch at a brisk tempo
    # with one memorable interval jump. The leap here lands on the alien 7/4.
    hook = [  # (scale degree, octave, step index, length-in-steps)
        ("1", 1, 0, 2), ("5/4", 1, 2, 2), ("3/2", 1, 4, 2),
        ("7/4", 1, 6, 3), ("3/2", 1, 9, 1), ("5/4", 1, 10, 2),
        ("9/8", 1, 12, 2), ("1", 1, 14, 2),
    ]
    # A subtle VARIATION used on repeats -> optimal surprise / mere-exposure:
    # same skeleton, one note nudged so each loop is familiar-but-fresh.
    hook_var = [
        ("1", 1, 0, 2), ("5/4", 1, 2, 2), ("3/2", 1, 4, 2),
        ("7/4", 1, 6, 3), ("11/8", 1, 9, 1), ("5/4", 1, 10, 2),
        ("7/6", 1, 12, 2), ("1", 1, 14, 2),
    ]

    def play_hook(bar_i, notes, gain=0.5, inharm=0.0, oct_shift=0):
        for deg, octv, s, ln in notes:
            f = hz(deg, octv + oct_shift)
            dur = ln * step * 1.05
            env = adsr(int(dur * SR), 0.008, 0.06, 0.6, ln * step * 0.5)
            tone = additive_tone(f, dur, partials=6, inharm=inharm,
                                  decay=1.3, amp=gain, env=env)
            t = step_time(bar_i, s)
            # ping-pong placement for width
            (L if (s // 2) % 2 == 0 else R).add(tone, t, 1.0)
            (R if (s // 2) % 2 == 0 else L).add(tone, t, 0.6)

    # ----- Pad / drone: inharmonic, slow AM entrainment, establishes the
    # alien tonal world and a hypnotic steady-state bed.
    def play_pad(bar_i, n_bars, degs, gain=0.22):
        dur = n_bars * bar
        mix = np.zeros(int(dur * SR))
        for deg, octv in degs:
            f = hz(deg, octv)
            env = adsr(int(dur * SR), 0.8, 0.5, 0.85, 1.2)
            mix += additive_tone(f, dur, partials=10, inharm=0.0015,
                                 decay=1.1, amp=gain, env=env)
        mix = am_entrain(mix, rate=beat and (1.0 / beat) / 2, depth=0.12)  # half-beat pulse
        t = bar_i * bar
        L.add(mix, t, 0.9)
        R.add(mix, t, 0.9)

    # ----- Groove: the SYNCOPATION SWEET-SPOT. Medium syncopation maximizes
    # the pleasurable urge to move -- not the rigid on-beat (boring) nor fully
    # off (chaotic). Kick mostly on strong beats, with anticipatory pushes.
    kick_steps = [0, 6, 8, 11]          # the "&" pushes create the pull
    hat_steps = [2, 4, 6, 10, 12, 14, 15]
    sub_steps = [0, 8, 11]

    def play_groove(bar_i, energy=1.0):
        for s in kick_steps:
            L.add(kick(amp=0.9 * energy), step_time(bar_i, s))
            R.add(kick(amp=0.9 * energy), step_time(bar_i, s))
        for s in hat_steps:
            h = hat(amp=0.32 * energy, lp=(s % 4 == 0))
            pan = 0.5 + 0.4 * math.sin(s)
            L.add(h, step_time(bar_i, s), pan)
            R.add(h, step_time(bar_i, s), 1 - pan)
        for s in sub_steps:
            deg = "1" if s != 11 else "7/6"   # alien sub-note on the push
            sb = sub_bass(hz(deg, -1), beat * 0.9, amp=0.8 * energy)
            L.add(sb, step_time(bar_i, s)); R.add(sb, step_time(bar_i, s))

    def shimmer(bar_lo, bar_hi, gain=0.12):
        # ASMR-adjacent high sparkle / frisson topping
        for bar_i in range(bar_lo, bar_hi):
            for s in [1, 5, 9, 13]:
                f = hz("5/2", 1) * (1 + 0.001 * s)
                sp = additive_tone(f, step * 2, partials=3, inharm=0.01, amp=gain)
                L.add(sp, step_time(bar_i, s), 0.7)
                R.add(sp, step_time(bar_i, s + 1), 0.7)

    def grooves(bar_lo, n, energy=1.0):
        for i in range(n):
            play_groove(bar_lo + i, energy=energy)

    # ========================= ARRANGEMENT (64 bars) =========================
    # Sectioned to build & release tension repeatedly -- the anticipation
    # architecture that drives dopaminergic craving + replay.

    # INTRO (0-3): drone establishes the alien tonal world + slow entrainment.
    play_pad(0, 4, [("1", 0), ("3/2", 0), ("7/4", 0)], gain=0.26)
    L.add(noise_riser(bar * 0.9, 0.18), 3 * bar); R.add(noise_riser(bar * 0.9, 0.18), 3 * bar)

    # BUILD 1 (4-7): groove enters low-energy; first hook statement.
    for i in range(4):
        play_groove(4 + i, energy=0.6 + 0.1 * i)
    play_pad(4, 4, [("1", 0), ("5/4", 0), ("3/2", 0)], gain=0.2)
    play_hook(6, hook, gain=0.42)

    # GROOVE A (8-15): full groove + hook repeated with subtle variation
    # (optimal surprise: same skeleton, one note nudged each loop).
    grooves(8, 8, energy=1.0)
    play_pad(8, 8, [("1", 0), ("3/2", 0), ("9/8", 0)], gain=0.16)
    for j, bar_i in enumerate([8, 10, 12, 14]):
        play_hook(bar_i, hook if j % 2 == 0 else hook_var, gain=0.5)

    # BREAKDOWN 1 (16-19): beat drops out, 11/8 tension pad + long riser.
    play_pad(16, 4, [("1", 0), ("11/8", 0), ("7/4", 0)], gain=0.28)
    play_hook(17, hook_var, gain=0.3, inharm=0.004)  # ghostly inharmonic echo
    L.add(noise_riser(bar * 2.0, 0.5), 18 * bar); R.add(noise_riser(bar * 2.0, 0.5), 18 * bar)

    # DROP 1 / CHORUS (20-27): frisson -- everything hits, hook lifts an octave
    # (register lift = chills trigger), consonant resolution after 11/8 tension.
    grooves(20, 8, energy=1.15)
    play_pad(20, 8, [("1", 0), ("5/4", 0), ("3/2", 0), ("2", 0)], gain=0.2)
    for bar_i in [20, 22, 24, 26]:
        play_hook(bar_i, hook, gain=0.55, oct_shift=1)   # the lift
        play_hook(bar_i, hook, gain=0.3)                  # doubled low
    shimmer(20, 28)

    # GROOVE B (28-35): keep the energy, alternate hook/variation, alien sub.
    grooves(28, 8, energy=1.05)
    play_pad(28, 8, [("1", 0), ("7/6", 0), ("3/2", 0)], gain=0.17)  # 7/6 alien color
    for j, bar_i in enumerate([28, 30, 32, 34]):
        play_hook(bar_i, hook_var if j % 2 == 0 else hook, gain=0.5,
                  oct_shift=1 if j == 3 else 0)
    shimmer(32, 36, gain=0.08)

    # BREAKDOWN 2 (36-43): deeper + longer -- max anticipation before the big
    # drop. Inharmonic ghost-hook, two stacked risers, all-tension tuning.
    play_pad(36, 8, [("1", 0), ("11/8", 0), ("7/4", 0), ("9/4", 0)], gain=0.3)
    play_hook(38, hook, gain=0.32, inharm=0.006)
    play_hook(40, hook_var, gain=0.3, inharm=0.01, oct_shift=1)
    L.add(noise_riser(bar * 3.5, 0.55), 40 * bar); R.add(noise_riser(bar * 3.5, 0.55), 40 * bar)

    # DROP 2 / FINAL CHORUS (44-55): the biggest payoff. Octave-lifted hook +
    # low double + counter-shimmer; highest energy; longest sustained groove.
    grooves(44, 12, energy=1.2)
    play_pad(44, 12, [("1", 0), ("5/4", 0), ("3/2", 0), ("2", 0), ("5/2", 0)], gain=0.19)
    for bar_i in [44, 46, 48, 50, 52, 54]:
        play_hook(bar_i, hook, gain=0.55, oct_shift=1)
        play_hook(bar_i, hook_var, gain=0.28)
    shimmer(44, 56, gain=0.13)

    # OUTRO (56-63): strip back to drone + groove decaying; hook left UNRESOLVED
    # on the alien 7/4 (no return to tonic) -> the open loop / Zeigarnik tail
    # that keeps replaying in the head after the track ends.
    play_pad(56, 8, [("1", 0), ("3/2", 0)], gain=0.24)
    for i in range(4):
        play_groove(56 + i, energy=max(0.2, 0.7 - 0.13 * i))
    play_hook(58, [("1", 1, 0, 2), ("5/4", 1, 2, 2), ("3/2", 1, 4, 2),
                   ("7/4", 1, 6, 6)], gain=0.5)
    play_hook(61, [("3/2", 1, 0, 2), ("7/4", 1, 4, 8)], gain=0.4)  # hangs on 7/4

    # ========================= MASTER =========================
    left, right = L.buf, R.buf
    left = schroeder_reverb(left, mix=0.22)
    right = schroeder_reverb(right, mix=0.22)
    left, right = stereo_widen(left, right, ms=11)

    # gentle master bus glue + brickwall-ish soft limit
    stereo = np.stack([left, right])
    peak = np.max(np.abs(stereo))
    stereo = stereo / (peak + 1e-9) * 0.9
    stereo = soft_clip(stereo, 1.15)
    stereo = stereo / (np.max(np.abs(stereo)) + 1e-9) * 0.95

    # 3s fade in / 4s fade out
    fi = int(3 * SR); fo = int(4 * SR)
    stereo[:, :fi] *= np.linspace(0, 1, fi)
    stereo[:, -fo:] *= np.linspace(1, 0, fo)
    return stereo


def write_wav(path, stereo):
    data = (np.clip(stereo.T, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "soundtrack.wav"
    stereo = render()
    write_wav(out, stereo)
    dur = stereo.shape[1] / SR
    print(f"wrote {out}  ({dur:.1f}s, {stereo.shape[1]} frames, stereo {SR}Hz)")
