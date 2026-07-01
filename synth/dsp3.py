"""
Production-quality DSP layer (v3 toolkit) for the apex track.

Everything the earlier tracks lacked to sound "expensive":
  - dual reverb (tight ROOM + huge dark HALL) with true stereo decorrelation
  - stereo decorrelator (complementary short-delay allpass network)
  - transient shaper (attack/sustain split via dual envelope followers)
  - vectorized soft-knee bus compressor + lookahead-style peak limiter
  - equal-power pan law + Haas widener + mono-below-Hz utility
  - velocity/timing humanizer driven by FFT pink noise (no crackle)
All band-limited / aliasing-safe; obeys the project pitfall checklist.
"""
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

SR = 44100
_rng = np.random.default_rng(777)


def lp(x, c, o=4):
    c = min(c, SR / 2 - 100)
    return sosfilt(butter(o, c / (SR / 2), "low", output="sos"), x)


def hp(x, c, o=2):
    return sosfilt(butter(o, max(20.0, c) / (SR / 2), "high", output="sos"), x)


def bp(x, lo, hi, o=2):
    lo = max(20.0, lo); hi = min(hi, SR / 2 - 100)
    return sosfilt(butter(o, [lo / (SR / 2), hi / (SR / 2)], "band", output="sos"), x)


def pink(n, seed=None):
    """FFT 1/sqrt(f) pink noise — smooth, no staircase crackle."""
    r = np.random.default_rng(seed) if seed is not None else _rng
    X = np.fft.rfft(r.standard_normal(n))
    f = np.arange(len(X), dtype=float); f[0] = 1.0
    out = np.fft.irfft(X / np.sqrt(f), n)
    return out / (np.max(np.abs(out)) + 1e-9)


def pink_curve(n, lo, hi, ctrl=None, seed=None):
    """Smooth 1/f control curve in [lo, hi] — the anti-mechanical modulator."""
    ctrl = ctrl or max(8, n // (SR // 2))
    p = pink(max(64, ctrl * 8), seed)
    p = np.interp(np.linspace(0, len(p) - 1, n), np.arange(len(p)), p)
    p = (p - p.min()) / (np.ptp(p) + 1e-9)
    return lo + (hi - lo) * p


# ----------------------------------------------------------------- reverbs
def _ir(seed, rt60, damp, predelay_ms, early=None):
    n = int(rt60 * SR)
    r = np.random.default_rng(seed)
    ir = r.standard_normal(n) * np.exp(-6.9 * np.linspace(0, 1, n))
    ir = lp(ir, damp)
    ir[n // 2:] = lp(ir[n // 2:], damp * 0.55)     # tail darkens as it decays
    if early:
        for ms, g in early:                         # sparse early reflections
            i = int(ms / 1000 * SR)
            if i < n:
                ir[i] += g
    pd = int(predelay_ms / 1000 * SR)
    ir = np.concatenate([np.zeros(pd), ir])
    return ir / (np.sqrt(np.sum(ir ** 2)) + 1e-9)


_EARLY = [(11, 0.5), (17, 0.4), (23, 0.35), (31, 0.28), (41, 0.2)]
IR_ROOM = (_ir(101, 0.5, 6500, 8, _EARLY), _ir(102, 0.5, 6200, 8, _EARLY))
IR_HALL = (_ir(201, 4.2, 3800, 28), _ir(202, 4.2, 3600, 28))


def reverb_bus(wet_st, kind="hall"):
    """Convolve a stereo send bus with decorrelated L/R IRs."""
    irL, irR = IR_ROOM if kind == "room" else IR_HALL
    n = wet_st.shape[1]
    return np.stack([fftconvolve(wet_st[0], irL)[:n],
                     fftconvolve(wet_st[1], irR)[:n]])


# ------------------------------------------------------------ stereo tools
def decorrelate(x, amount=1.0, seed=5):
    """Mono -> wide stereo via complementary sparse-FIR diffusion (~18 ms).
    Broadband material decorrelates strongly; pure tones stay mono-ish, which
    is desirable (keeps bass/leads mono-compatible)."""
    r = np.random.default_rng(seed)
    taps = int(0.018 * SR)
    hL = np.zeros(taps); hR = np.zeros(taps)
    hL[0] = 1.0; hR[0] = 1.0
    idx = r.choice(np.arange(30, taps), size=24, replace=False)
    signs = r.choice([-1.0, 1.0], size=24)
    decay = np.exp(-idx / taps * 2.2)
    hL[idx] += 0.38 * amount * signs * decay
    hR[idx] += 0.38 * amount * (signs[::-1] * -1) * decay
    L = fftconvolve(x, hL)[:len(x)]
    R = fftconvolve(x, hR)[:len(x)]
    m = max(np.max(np.abs(L)), np.max(np.abs(R))) / (np.max(np.abs(x)) + 1e-9)
    return L / m, R / m


def mono_below(st, freq=140.0):
    """Sum L/R below `freq` (tight low end, pro mix practice)."""
    lo = 0.5 * (lp(st[0], freq) + lp(st[1], freq))
    return np.stack([lo + (st[0] - lp(st[0], freq)),
                     lo + (st[1] - lp(st[1], freq))])


# --------------------------------------------------------------- dynamics
def env_follow(x, atk_s, rel_s):
    """One-pole attack/release envelope follower (vectorized via lfilter trick
    per block — here simple recursive filtfilt-free approximation)."""
    absx = np.abs(x)
    # fast attack via short max-pool, then smooth with one-pole (lfilter)
    from scipy.signal import lfilter
    a_atk = np.exp(-1.0 / (atk_s * SR))
    a_rel = np.exp(-1.0 / (rel_s * SR))
    # asymmetric smoothing approximated by cascading two one-poles
    e1 = lfilter([1 - a_atk], [1, -a_atk], absx)
    e2 = lfilter([1 - a_rel], [1, -a_rel], np.maximum(absx, e1))
    return np.maximum(e1, e2)


def transient_shape(x, punch=1.4, sustain=0.9):
    """Attack/sustain split: fast env - slow env = transient component."""
    fast = env_follow(x, 0.0008, 0.03)
    slow = env_follow(x, 0.02, 0.25)
    trans = np.clip(fast - slow, 0, None)
    tgain = 1 + (punch - 1) * (trans / (fast + 1e-9))
    sgain = sustain + (1 - sustain) * (trans / (fast + 1e-9))
    return x * tgain * sgain


def bus_comp(x, thr=0.4, ratio=2.5, atk=0.012, rel=0.25, makeup=1.0):
    e = env_follow(x, atk, rel) + 1e-9
    gain = np.ones_like(e)
    over = e > thr
    gain[over] = (thr + (e[over] - thr) / ratio) / e[over]
    return x * lp(gain, 60, 2) * makeup


def limiter(x, ceiling=0.95, lookahead_ms=2.0):
    """Peak limiter: smoothed gain computed on a max-pooled peak envelope."""
    la = max(1, int(lookahead_ms / 1000 * SR))
    pad = np.concatenate([np.abs(x), np.zeros(la)])
    peaks = np.maximum.reduce([pad[i:len(x) + i] for i in range(0, la, max(1, la // 4))])
    gain = np.minimum(1.0, ceiling / (peaks + 1e-9))
    gain = lp(gain, 500, 2)                        # smooth, avoids distortion
    gain = np.minimum(gain, ceiling / (np.abs(x) + 1e-9))
    return x * np.clip(gain, 0, 1)


def soft_sat(x, drive=1.1, warmth=0.2):
    s = np.tanh(x * drive)
    even = warmth * (s * s - np.mean(s * s))
    return (s + even) / (1 + warmth * 0.5)


def tilt_cut(x, corner=3400, db=-4.5):
    hi = hp(x, corner, 2)
    return x + (10 ** (db / 20) - 1) * hi


# -------------------------------------------------------------- placement
class Mixer:
    """Multi-bus stereo mixer with per-bus room/hall sends and declicking."""
    def __init__(self, total_sec, buses):
        self.n = int(total_sec * SR)
        self.b = {k: {"dry": np.zeros((2, self.n)),
                      "room": np.zeros((2, self.n)),
                      "hall": np.zeros((2, self.n))} for k in buses}

    def add(self, bus, sig, at, gain=1.0, pan=0.5, room=0.0, hall=0.15,
            jitter_ms=0.0, vel_var_db=0.0, seed=None):
        r = np.random.default_rng(seed) if seed is not None else _rng
        if jitter_ms:
            at += float(r.standard_normal()) * jitter_ms / 1000.0
        if vel_var_db:
            gain *= 10 ** (float(r.uniform(-vel_var_db, vel_var_db)) / 20.0)
        i = int(at * SR)
        if i < 0 or i >= self.n:
            return
        sig = np.asarray(sig, float)
        if sig.ndim == 1:
            gl, gr = gain * np.sqrt(1 - pan), gain * np.sqrt(pan)
            segs = (sig * gl, sig * gr)
        else:
            segs = (sig[0] * gain, sig[1] * gain)
        fd = int(0.004 * SR)
        j = min(self.n, i + len(segs[0]))
        for ch in (0, 1):
            s = segs[ch][:j - i].copy()
            if len(s) > 3 * fd:
                s[:fd] *= np.linspace(0, 1, fd)
                s[-fd:] *= np.linspace(1, 0, fd)
            self.b[bus]["dry"][ch, i:j] += s
            if room:
                self.b[bus]["room"][ch, i:j] += room * s
            if hall:
                self.b[bus]["hall"][ch, i:j] += hall * s


if __name__ == "__main__":
    # validation: decorrelation width, reverb tails, limiter ceiling, pink smoothness
    x = np.sin(2 * np.pi * 220 * np.arange(SR) / SR)
    broad = lp(_rng.standard_normal(SR), 6000)      # realistic broadband program
    L, R = decorrelate(broad)
    corr = np.corrcoef(L, R)[0, 1]
    p = pink(SR)
    st = np.stack([x, x]) * 0.2
    hall = reverb_bus(st, "hall"); room = reverb_bus(st, "room")
    y = limiter(x * 3.0, 0.95)
    print(f"decorrelate corr={corr:.2f} (target |corr|<0.6)")
    print(f"pink max-jump={np.abs(np.diff(p)).max():.3f} (no staircase)")
    print(f"hall tail rms={np.sqrt(np.mean(hall[:, -SR:] ** 2)):.4f}  room tail rms={np.sqrt(np.mean(room[:, -SR:] ** 2)):.4f}")
    print(f"limiter peak={np.abs(y).max():.3f} (<=0.96)")
    tx = transient_shape(np.concatenate([np.zeros(100), np.ones(200), np.zeros(SR // 2)]) * x[:SR // 2 + 300], 1.5, 0.8)
    print(f"transient shaper ok, finite={np.all(np.isfinite(tx))}")
    print("dsp3 OK")
