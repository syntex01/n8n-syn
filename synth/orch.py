"""
Synthesized orchestral instruments (band-limited, warm) for the neoclassical
piece. Additive/subtractive, cumsum-phase (supports vibrato & glide), ensemble
detune for realism. No aliasing, no arcady preset timbres.
"""
import numpy as np
from scipy.signal import butter, sosfilt

SR = 44100
rng = np.random.default_rng(5)
_SEMI = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def note(name):
    i = 1; acc = 0
    if len(name) > 1 and name[1] in "#b":
        acc = 1 if name[1] == "#" else -1; i = 2
    midi = 12 * (int(name[i:]) + 1) + _SEMI[name[0]] + acc
    return 440.0 * 2 ** ((midi - 69) / 12.0)


def t_of(d):
    return np.arange(int(d * SR)) / SR


def lp(x, c, o=4):
    return sosfilt(butter(o, min(c, SR / 2 - 100) / (SR / 2), "low", output="sos"), x)


def hp(x, c, o=2):
    return sosfilt(butter(o, max(20, c) / (SR / 2), "high", output="sos"), x)


def bp(x, lo, hi, o=2):
    return sosfilt(butter(o, [max(20, lo) / (SR / 2), min(hi, SR / 2 - 100) / (SR / 2)],
                          "band", output="sos"), x)


def adsr(n, a, d, s, r, curve=2.0):
    a_n = max(1, int(a * SR)); d_n = max(1, int(d * SR)); r_n = max(1, int(r * SR))
    if a_n + d_n + r_n >= n:
        e = np.ones(n); h = max(1, n // 4)
        e[:h] = np.linspace(0, 1, h); e[-h:] = np.linspace(e[-h], 0, h); return e
    su = n - a_n - d_n - r_n; e = np.empty(n)
    e[:a_n] = np.linspace(0, 1, a_n) ** 1.2
    e[a_n:a_n + d_n] = s + (1 - s) * np.linspace(1, 0, d_n) ** curve
    e[a_n + d_n:a_n + d_n + su] = s
    e[a_n + d_n + su:] = s * np.linspace(1, 0, r_n) ** curve
    return e


def _additive(f_t, partials, rolloff, phase0=0.0):
    """Sum band-limited partials with a (possibly time-varying) f_t array."""
    out = np.zeros(len(f_t))
    cph = np.cumsum(f_t) / SR
    for k in range(1, partials + 1):
        if np.max(f_t) * k > SR / 2 - 200:
            break
        out += (1.0 / k ** rolloff) * np.sin(2 * np.pi * k * cph + phase0 * k)
    return out


def vib(freq, n, rate=5.2, depth_cents=8, delay=0.35):
    t = np.arange(n) / SR
    on = np.clip((t - delay) / 0.3, 0, 1)
    return freq * 2 ** (on * depth_cents / 1200.0 * np.sin(2 * np.pi * rate * t))


# ---------------------------------------------------------------- instruments
def strings_sus(freq, dur, gain=0.4, voices=5, bright=3800, rolloff=1.15):
    """Ensemble sustained strings: detuned bowed voices, vibrato, bow noise."""
    n = int(dur * SR); out = np.zeros(n)
    for v in range(voices):
        det = (v - (voices - 1) / 2) * 6 / 1200.0
        f = vib(freq * 2 ** det, n, rate=5.0 + 0.4 * v, depth_cents=7)
        out += _additive(f, 22, rolloff, phase0=rng.uniform(0, 6))
    out /= voices
    bow = lp(rng.standard_normal(n), 3000) * 0.02 * np.exp(-t_of(dur) * 4)
    env = adsr(n, 0.18, 0.3, 0.85, min(1.2, dur * 0.3))
    return lp((out + bow) * env, bright) * gain


def strings_stac(freq, dur=0.28, gain=0.5):
    n = int(dur * SR)
    f = np.full(n, freq)
    out = _additive(f, 18, 1.2)
    env = adsr(n, 0.01, 0.09, 0.3, 0.12)
    return lp(out * env, 4200) * gain


def pizz(freq, dur=0.5, gain=0.5):
    n = int(dur * SR); t = t_of(dur)
    out = np.zeros(n)
    for k in range(1, 12):
        if freq * k > SR / 2 - 200:
            break
        out += (1.0 / k ** 1.1) * np.exp(-t * (5 + k * 0.7)) * np.sin(2 * np.pi * freq * k * t)
    env = np.exp(-t * 6) * (1 - np.exp(-t * 500))
    return lp(out * env, 5000) * gain


def harp(freq, dur=1.4, gain=0.45):
    n = int(dur * SR); t = t_of(dur)
    out = np.zeros(n)
    for k in range(1, 16):
        if freq * k > SR / 2 - 200:
            break
        out += (1.0 / k ** 1.25) * np.exp(-t * (2.2 + k * 0.35)) * np.sin(2 * np.pi * freq * k * t)
    env = (1 - np.exp(-t * 600))
    return lp(out * env, 6000) * gain


def piano(freq, dur=2.2, gain=0.55):
    """Felt-ish grand: inharmonic partials, per-partial decay, hammer thump."""
    n = int(dur * SR); t = t_of(dur); B = 0.0004
    out = np.zeros(n)
    for k in range(1, 12):
        fk = k * freq * np.sqrt(1 + B * k * k)
        if fk > SR / 2 - 200:
            break
        out += (1.0 / k ** 1.15) * np.exp(-t / (max(0.5, dur * 0.55) / k)) * np.sin(2 * np.pi * fk * t)
    out /= np.max(np.abs(out)) + 1e-9
    thn = int(0.02 * SR); thump = np.zeros(n)
    thump[:thn] = lp(rng.standard_normal(thn), 400) * np.exp(-np.linspace(0, 1, thn) * 5)
    atk = int(0.008 * SR); ae = np.ones(n); ae[:atk] = np.linspace(0, 1, atk) ** 1.3
    return (out * ae + 0.2 * thump) * gain


def brass(freq, dur, gain=0.4, bright=3200):
    """Warm brass swell: richer harmonics, attack bloom, gentle sat, formant."""
    n = int(dur * SR)
    f = vib(freq, n, rate=4.6, depth_cents=6, delay=0.25)
    out = _additive(f, 16, 0.95)
    out = np.tanh(out * 1.4) * 0.8                     # brass 'blat', gentle
    out = 1.0 * bp(out, 700, 2000) + 0.6 * out          # formant emphasis
    env = adsr(n, 0.12, 0.2, 0.85, min(1.0, dur * 0.3))
    return lp(out * env, bright) * gain


def choir_pad(freq, dur, gain=0.3, vowel=(600, 1000, 2400)):
    n = int(dur * SR)
    f = vib(freq, n, rate=5.0, depth_cents=9, delay=0.4)
    src = _additive(f, 12, 1.3)
    F1, F2, F3 = vowel
    out = 1.0 * bp(src, F1 * 0.85, F1 * 1.15) + 0.6 * bp(src, F2 * 0.85, F2 * 1.15) + \
        0.3 * bp(src, F3 * 0.85, F3 * 1.15)
    env = adsr(n, 0.4, 0.4, 0.85, min(1.5, dur * 0.35))
    return lp(out * env, 4200) * gain


def timpani(freq=90, dur=0.7, gain=0.7):
    t = t_of(dur)
    pitch = freq * (1 + 0.5 * np.exp(-t * 12))
    ph = 2 * np.pi * np.cumsum(pitch) / SR
    body = np.sin(ph) + 0.3 * np.sin(2 * ph)
    noise = lp(rng.standard_normal(len(t)), 1200) * np.exp(-t * 25) * 0.3
    return np.tanh((body * np.exp(-t * 5) + noise) * 1.2) * gain


if __name__ == "__main__":
    def cen(x):
        X = np.abs(np.fft.rfft(x * np.hanning(len(x)))); fr = np.fft.rfftfreq(len(x), 1 / SR)
        return np.sum(fr * X) / (np.sum(X) + 1e-9)
    tests = {
        "strings_sus": strings_sus(note("D4"), 2.0),
        "strings_stac": strings_stac(note("A4")),
        "pizz": pizz(note("D3")),
        "harp": harp(note("A4")),
        "piano": piano(note("D4")),
        "brass": brass(note("D3"), 2.0),
        "choir_pad": choir_pad(note("A4"), 2.0),
        "timpani": timpani(),
    }
    for k, s in tests.items():
        print(f"{k:14s} finite={np.all(np.isfinite(s))} peak={np.max(np.abs(s)):.2f} centroid={cen(s):5.0f}Hz")
    print("orch.py OK")
