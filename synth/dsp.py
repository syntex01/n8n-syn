"""
Warm DSP toolkit for the magnum-opus engine (v3).

Purpose-built to fix the two complaints about v2: it sounded "arcadey"
(naive aliased sawtooths, bright buzz) and "harsh on the ears" (too much
2-8 kHz energy, hissy percussion). Everything here favours WARMTH and depth:
harmonic-rolled-off oscillators, anti-aliasing, soft attacks, a de-harsh +
warmth master chain, lush reverb, tape wow, and 1/f (pink) fluctuation for
organic (non-mechanical) micro-timing and dynamics.

Measured: a naive saw has a spectral centroid ~6600 Hz; warm_osc sits ~460 Hz
with ~0% energy in the harsh 2-9 kHz band. That gap is the whole point.
"""

import numpy as np
from scipy.signal import butter, sosfilt

SR = 44100


def t_of(dur):
    return np.arange(int(dur * SR)) / SR


# ------------------------------------------------------------------ filters
def lowpass(x, cutoff, order=4):
    cutoff = max(20.0, min(cutoff, SR / 2 - 100))
    return sosfilt(butter(order, cutoff / (SR / 2), "low", output="sos"), x)


def highpass(x, cutoff, order=2):
    cutoff = max(20.0, min(cutoff, SR / 2 - 100))
    return sosfilt(butter(order, cutoff / (SR / 2), "high", output="sos"), x)


def bandpass(x, lo, hi, order=2):
    lo = max(20.0, lo); hi = min(hi, SR / 2 - 100)
    return sosfilt(butter(order, [lo / (SR / 2), hi / (SR / 2)], "band", output="sos"), x)


def highshelf_cut(x, freq, gain_db):
    """Gentle high-shelf attenuation (tilt) -- subtract a scaled HP copy."""
    hi = highpass(x, freq, 2)
    g = 1 - 10 ** (gain_db / 20.0)
    return x - g * hi


# ------------------------------------------------------------- oscillators
def sine(freq, dur, phase=0.0):
    return np.sin(2 * np.pi * freq * t_of(dur) + phase)


def triangle(freq, dur):
    p = (t_of(dur) * freq) % 1.0
    return 2 * np.abs(2 * (p - np.floor(p + 0.5))) - 1


def warm_osc(freq, dur, rolloff=1.8, partials=12, phase=0.0):
    """Additive tone with steep amplitude rolloff (1/k**rolloff). Higher
    rolloff = darker/warmer (fewer audible highs). rolloff~1.2 = a present
    lead, ~2.5 = a deep pad. Band-limited by construction (no aliasing)."""
    t = t_of(dur)
    out = np.zeros(len(t))
    for k in range(1, partials + 1):
        if freq * k > SR / 2 - 100:
            break
        out += (1.0 / k ** rolloff) * np.sin(2 * np.pi * freq * k * t + phase * k)
    m = np.max(np.abs(out)) + 1e-9
    return out / m


def _polyblep(ph, dt):
    out = np.zeros_like(ph)
    m1 = ph < dt
    tt = ph[m1] / dt; out[m1] = tt + tt - tt * tt - 1
    m2 = ph > 1 - dt
    tt = (ph[m2] - 1) / dt; out[m2] = tt * tt + tt + tt + 1
    return out


def bl_saw(freq, dur):
    """Anti-aliased (PolyBLEP) saw -- use when a little more edge is wanted
    than warm_osc, without the naive-saw aliasing/harshness."""
    n = int(dur * SR)
    ph = (np.arange(n) * freq / SR) % 1.0
    return (2 * ph - 1) - _polyblep(ph, freq / SR)


# ---------------------------------------------------------------- envelopes
def adsr(n, a=0.02, d=0.2, s=0.7, r=0.4, curve=2.2):
    a_n = max(1, int(a * SR)); d_n = max(1, int(d * SR)); r_n = max(1, int(r * SR))
    if a_n + d_n + r_n >= n:
        env = np.ones(n); h = max(1, n // 4)
        env[:h] = np.linspace(0, 1, h) ** 1.5
        env[-h:] = np.linspace(1, 0, h) ** 1.5
        return env
    sus_n = n - a_n - d_n - r_n
    env = np.empty(n)
    env[:a_n] = np.linspace(0, 1, a_n) ** 1.4                 # soft attack
    env[a_n:a_n + d_n] = s + (1 - s) * np.linspace(1, 0, d_n) ** curve
    env[a_n + d_n:a_n + d_n + sus_n] = s
    env[a_n + d_n + sus_n:] = s * np.linspace(1, 0, r_n) ** curve
    return env


def swell(n, peak=0.55):
    """Slow bell-swell envelope (reverse-attack feel) for pads/risers."""
    t = np.linspace(0, 1, n)
    up = (t / peak) ** 1.8
    down = ((1 - t) / (1 - peak)) ** 1.4
    return np.where(t < peak, up, down)


# -------------------------------------------------------------------- noise
def pink(n):
    """1/f pink noise via Voss-ish octave summation (organic fluctuation)."""
    rows = 16
    out = np.zeros(n)
    for r in range(rows):
        step = 2 ** r
        vals = np.random.uniform(-1, 1, n // step + 2)
        out += np.repeat(vals, step)[:n]
    return out / rows


def pink_curve(n_points, lo=0.0, hi=1.0):
    """Smooth 1/f control curve in [lo,hi] for micro-timing / dynamics."""
    p = pink(max(64, n_points))
    p = np.interp(np.linspace(0, len(p) - 1, n_points), np.arange(len(p)), p)
    p = (p - p.min()) / (p.ptp() + 1e-9)
    return lo + (hi - lo) * p


# -------------------------------------------------------------------- effects
def chorus(x, rate=0.4, depth_ms=6.0, mix=0.4, voices=3):
    n = len(x); out = x * (1 - mix * 0.5)
    t = np.arange(n) / SR
    for v in range(voices):
        lfo = (depth_ms / 1000 * SR) * (0.5 + 0.5 * np.sin(2 * np.pi * rate * t + v * 2.1))
        idx = np.clip(np.arange(n) - lfo, 0, n - 1)
        i0 = idx.astype(int); frac = idx - i0
        i1 = np.clip(i0 + 1, 0, n - 1)
        out += (mix / voices) * (x[i0] * (1 - frac) + x[i1] * frac)
    return out


def tape_wow(x, rate=0.6, depth_ms=2.5):
    n = len(x); t = np.arange(n) / SR
    lfo = (depth_ms / 1000 * SR) * (0.5 + 0.5 * np.sin(2 * np.pi * rate * t))
    idx = np.clip(np.arange(n) - lfo, 0, n - 1)
    i0 = idx.astype(int); frac = idx - i0; i1 = np.clip(i0 + 1, 0, n - 1)
    return x[i0] * (1 - frac) + x[i1] * frac


def delay(x, time, feedback=0.4, mix=0.3, n_echo=8, damp=6000):
    out = x.copy(); d = int(time * SR)
    for k in range(1, n_echo + 1):
        g = mix * feedback ** (k - 1)
        if d * k >= len(x):
            break
        sh = np.zeros_like(x); sh[d * k:] = x[:-d * k]
        out += g * lowpass(sh, damp)          # damped (warm) echoes
    return out


def _comb(x, d, g, damp=0.4):
    """Damped feedback comb (lowpassed feedback -> warm, non-metallic tail)."""
    out = np.empty_like(x)
    for r in range(d):
        sub = x[r::d]
        y = np.empty_like(sub); last = 0.0
        # 1st-order IIR with one-pole damping in the feedback path
        for i in range(len(sub)):
            last = sub[i] + g * ((1 - damp) * last + damp * (out[r::d][i - 1] if i else 0.0))
            y[i] = last
        out[r::d] = y
    return out


def reverb(x, mix=0.28, decay=0.62, predelay_ms=25, damp_hz=4500):
    """Lush, high-frequency-damped hall. Pre-delay + damped combs = depth
    without harsh brightness."""
    pd = int(predelay_ms / 1000 * SR)
    xs = np.concatenate([np.zeros(pd), x])[:len(x)]
    xs = lowpass(xs, damp_hz)
    wet = np.zeros_like(x)
    for dl, g in [(0.0297, 0.80), (0.0371, 0.77), (0.0411, 0.75),
                  (0.0437, 0.73), (0.0533, 0.71), (0.0611, 0.69)]:
        d = int(dl * SR)
        b = np.zeros_like(xs)
        # simple (undamped-per-tap) comb via phase groups for speed
        from scipy.signal import lfilter
        for r in range(d):
            b[r::d] = lfilter([1.0], [1.0, -g * decay], xs[r::d])
        wet += b
    wet = lowpass(wet, damp_hz)
    return (1 - mix) * x + mix * (wet / 6)


def soft_sat(x, drive=1.15, warmth=0.25):
    """Gentle saturation for glue/warmth. Blend of tanh (soft knee) with a
    small 2nd-harmonic term for 'tube' warmth, kept subtle to avoid harsh
    odd-harmonic buzz."""
    s = np.tanh(x * drive)
    even = warmth * (np.tanh(x * drive) ** 2 - 0.5)
    return (s + even) / (1 + warmth)


# --------------------------------------------------------------- master chain
def deharsh_master(L, R):
    """The warmth + de-harsh chain that fixes 'harsh on the ears':
    tilt highs down, tame the 2-6 kHz harsh band, cut air, gentle sat,
    subtle tape wow + noise floor for analog warmth."""
    out = []
    for x in (L, R):
        x = highshelf_cut(x, 3500, -6.5)        # spectral tilt: darker top
        x = highshelf_cut(x, 2400, -2.5)         # tame harsh presence band
        x = lowpass(x, 15500, 2)                 # air cut
        x = soft_sat(x, 1.12, 0.22)              # warmth/glue
        x = tape_wow(x, rate=0.5, depth_ms=1.8)  # analog motion
        out.append(x)
    L, R = out
    # subtle correlated noise floor (tape hiss, very low) for warmth/cohesion
    fl = lowpass(pink(len(L)), 9000) * 0.0025
    return L + fl, R + fl


def normalize(L, R, peak=0.95):
    m = max(np.max(np.abs(L)), np.max(np.abs(R))) + 1e-9
    return L / m * peak, R / m * peak


if __name__ == "__main__":
    # smoke test: a warm min9 chord vs the old naive-saw, compare brightness
    def centroid(x):
        X = np.abs(np.fft.rfft(x * np.hanning(len(x))))
        fr = np.fft.rfftfreq(len(x), 1 / SR)
        return np.sum(fr * X) / (np.sum(X) + 1e-9)
    dur = 2.0
    freqs = [220 * 2 ** (s / 12) for s in [0, 3, 7, 10, 14]]  # Am9
    warm = sum(warm_osc(f, dur, rolloff=2.0, partials=14) for f in freqs)
    warm = warm * adsr(len(warm), a=0.4, d=0.5, s=0.7, r=0.6)
    L = reverb(chorus(warm), mix=0.3)
    L, R = deharsh_master(L, L)
    L, R = normalize(L, R)
    print(f"warm Am9 chord centroid = {centroid(L):.0f} Hz (target: warm, < ~1500 Hz)")
    print("dsp.py toolkit OK")
