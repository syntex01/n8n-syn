"""
Advanced synthesis primitives for the invented dark palette (prototype).

These are the non-"arcady" synthesis families: modal/physical resonators,
granular textures, chaotic oscillators, uncanny formant-voice, and subharmonic
/ difference-tone drones. All band-limited (sine-based cores), all evolving.
Validated here before wiring into the composition once the design spec lands.
"""
import numpy as np
from scipy.signal import butter, sosfilt

SR = 44100
rng = np.random.default_rng(3)


def t_of(d):
    return np.arange(int(d * SR)) / SR


def lp(x, c, o=4):
    return sosfilt(butter(o, min(c, SR / 2 - 100) / (SR / 2), "low", output="sos"), x)


def bp(x, lo, hi, o=2):
    return sosfilt(butter(o, [max(20, lo) / (SR / 2), min(hi, SR / 2 - 100) / (SR / 2)],
                          "band", output="sos"), x)


# ---- modal resonator bank (struck / bowed inharmonic objects) ---------------
# Preset partial ratios (the MATH of vibrating bodies):
MODES = {
    "free_bar":  [1.0, 2.756, 5.404, 8.933, 13.34],        # xylophone/glass bar
    "bell":      [1.0, 2.0, 2.4, 3.0, 4.5, 5.33, 6.66],    # minor-3rd bell hum
    "waterphone": [1.0, 1.732, 2.646, 3.316, 4.2, 5.61],   # irrational-ish, eerie
    "cracked":   [1.0, 2.09, 3.11, 4.63, 6.02, 7.51],      # detuned/damaged
}


def modal(freq, dur, preset="bell", damp=3.0, excite="strike", bright=1.0, seed=0):
    r = np.random.default_rng(seed)
    t = t_of(dur); out = np.zeros(len(t))
    ratios = MODES[preset]
    for i, rt in enumerate(ratios):
        f = freq * rt
        if f > SR / 2 - 200:
            break
        # higher modes decay faster (physical) and are quieter
        dec = damp * (1 + 0.5 * i)
        amp = bright ** i / (1 + i) ** 1.2
        if excite == "strike":
            env = np.exp(-t * dec)
        else:  # bow / friction: sustained, noisy amplitude (never fully steady)
            n = lp(r.standard_normal(len(t)), 8)
            env = (0.6 + 0.4 * (n / (np.max(np.abs(n)) + 1e-9))) * np.exp(-t * dec * 0.15)
        out += amp * env * np.sin(2 * np.pi * f * t + r.uniform(0, 6.28))
    return out / (np.max(np.abs(out)) + 1e-9)


# ---- granular cloud (breath / whisper / shards in the dark) -----------------
def granular(dur, base=200.0, density=30, grain_ms=70, pitch_spread=0.5,
             kind="sine", seed=0):
    r = np.random.default_rng(seed)
    n = int(dur * SR); out = np.zeros(n)
    n_grains = int(density * dur)
    gl = int(grain_ms / 1000 * SR)
    win = np.hanning(gl)
    for _ in range(n_grains):
        at = int(r.uniform(0, max(1, n - gl)))
        f = base * 2 ** (r.uniform(-pitch_spread, pitch_spread))
        tg = np.arange(gl) / SR
        if kind == "sine":
            g = np.sin(2 * np.pi * f * tg)
        else:  # breath: band-limited noise grain
            g = bp(r.standard_normal(gl), f * 0.7, f * 2.2)
        out[at:at + gl] += win * g * r.uniform(0.3, 1.0)
    return out / (np.max(np.abs(out)) + 1e-9)


# ---- chaotic voice (logistic-map-modulated, living/unstable) ----------------
def chaotic_voice(freq, dur, r_param=3.72, depth_cents=45, ctrl_hz=60, seed=0):
    """A sine whose pitch wanders on a logistic-map trajectory: pitched but
    never-repeating -> the ear can't habituate. Sine core = band-limited."""
    r = np.random.default_rng(seed)
    n = int(dur * SR)
    n_ctrl = int(ctrl_hz * dur) + 2
    x = r.uniform(0.2, 0.8); seq = np.empty(n_ctrl)
    for i in range(n_ctrl):
        x = r_param * x * (1 - x); seq[i] = x
    cents = (seq - 0.5) * 2 * depth_cents
    cents = np.interp(np.linspace(0, n_ctrl - 1, n), np.arange(n_ctrl), cents)
    f = freq * 2 ** (cents / 1200.0)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph)


# ---- uncanny formant voice (source-filter, jitter+shimmer) ------------------
VOWELS = {  # (F1, F2, F3) Hz
    "a": (700, 1220, 2600), "e": (400, 2000, 2550),
    "i": (300, 2100, 3000), "o": (450, 800, 2600), "u": (325, 700, 2530),
}


def voice(freq, dur, vowel="o", whisper=False, seed=0):
    r = np.random.default_rng(seed)
    t = t_of(dur); n = len(t)
    # jitter (pitch instability) + drift -> uncanny, not-quite-human
    jit = np.interp(np.linspace(0, 200, n), np.arange(200),
                    lp(r.standard_normal(200), 4) * 12)   # ±cents
    f = freq * 2 ** (jit / 1200.0)
    if whisper:
        src = r.standard_normal(n)
    else:  # band-limited glottal-ish source (few harmonics, steep rolloff)
        src = np.zeros(n)
        for k in range(1, 14):
            if freq * k > SR / 2 - 200:
                break
            src += (1.0 / k ** 1.3) * np.sin(2 * np.pi * np.cumsum(f * k) / SR)
    F1, F2, F3 = VOWELS[vowel]
    out = 1.0 * bp(src, F1 * 0.9, F1 * 1.1) + 0.6 * bp(src, F2 * 0.9, F2 * 1.1) + \
        0.35 * bp(src, F3 * 0.9, F3 * 1.1)
    shimmer = 1 + 0.06 * np.interp(np.linspace(0, 150, n), np.arange(150),
                                   lp(r.standard_normal(150), 4))
    return lp(out * shimmer, 4500) / (np.max(np.abs(out)) + 1e-9)


# ---- subharmonic / difference-tone drone (chest-felt, ghost pitch) ----------
def drone(freq, dur, beat=1.2, seed=0):
    t = t_of(dur)
    o = np.sin(2 * np.pi * freq * t) + np.sin(2 * np.pi * (freq + beat) * t)   # slow beat
    sub = 0.7 * np.sin(2 * np.pi * (freq / 2) * t) + 0.4 * np.sin(2 * np.pi * (freq / 3) * t)
    diff = 0.5 * np.sin(2 * np.pi * abs(freq - (freq * 1.5 - freq)) * t)  # placeholder low
    w = o + sub
    return lp(w, 3000) / (np.max(np.abs(w)) + 1e-9)


if __name__ == "__main__":
    def centroid(x):
        X = np.abs(np.fft.rfft(x * np.hanning(len(x))))
        fr = np.fft.rfftfreq(len(x), 1 / SR)
        return np.sum(fr * X) / (np.sum(X) + 1e-9)
    tests = {
        "modal bell (strike)": modal(220, 3.0, "bell", damp=1.2),
        "modal waterphone bow": modal(180, 3.0, "waterphone", excite="bow"),
        "granular breath": granular(3.0, 300, kind="noise"),
        "chaotic voice": chaotic_voice(150, 3.0),
        "formant voice 'o'": voice(160, 3.0, "o"),
        "whisper voice": voice(200, 3.0, "a", whisper=True),
        "subharmonic drone": drone(70, 3.0),
    }
    for name, s in tests.items():
        ok = np.all(np.isfinite(s))
        print(f"{name:24s} finite={ok}  peak={np.max(np.abs(s)):.2f}  centroid={centroid(s):5.0f}Hz")
    print("dsp2 primitives OK")
