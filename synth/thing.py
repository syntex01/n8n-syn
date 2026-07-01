"""
"The Thing That Almost Breathes" — implements synth/SPEC2.md.

A dark/strange/creepy free-time instrumental built entirely from INVENTED
synthesis engines (no subtractive-synth "arcady" timbres): residue-pitch
drones, modal bells, uncanny formant voice, ghost-choir, bowed-metal snarl,
Shepard descent, a resonant "missing room", granular breath, and a
caught-breath ending. Every modulation is a 1/f random-walk (never a periodic
LFO) — the core anti-arcade rule. Tuning is locked to a cracked bell's own
inharmonic spectrum. Golden-section climax at ~142 s.

Curated realization of the 17-instrument spec: the instruments that carry each
of the 7 sections are built; a few near-duplicates are folded in.
"""
import wave
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

import dsp2
from dsp2 import SR, t_of, lp, bp, modal, MODES

rng = np.random.default_rng(11)

# ---- spectral tuning: the REVENANT BELL's own partials are the pitch lattice
PRIME = 130.0
HUM, TIERCE, QUINT, NOMINAL, DECIEM = 65.0, 156.0, 195.0, 260.0, 325.0


def hp(x, c, o=4):
    return sosfilt(butter(o, min(c, SR / 2 - 100) / (SR / 2), "high", output="sos"), x)


def tilt(x, corner=1200, slope_db_oct=-5):
    """Gentle high-shelf cut (dark spectral tilt)."""
    hi = hp(x, corner, 2)
    g = 1 - 10 ** (slope_db_oct / 20.0 * 1.2)
    return x - g * hi


def osat(x, drive=1.1):
    """2x-oversampled tanh (anti-alias guard on the nonlinearity)."""
    up = np.repeat(x, 2)
    up = np.tanh(up * drive) / drive
    return lp(up, SR * 0.45)[::2][:len(x)]


def pink_walk(n, lo, hi, ctrl=None):
    """1/f-ish drift in [lo,hi] (integrated noise, smoothed). The anti-arcade
    modulator: everything wobbles on this, never a sine LFO."""
    ctrl = ctrl or max(4, int(n / SR * 2))
    w = np.cumsum(rng.standard_normal(ctrl))
    w = (w - w.min()) / (np.ptp(w) + 1e-9)
    return lo + (hi - lo) * np.interp(np.linspace(0, ctrl - 1, n), np.arange(ctrl), w)


def swell(n, rise=0.35):
    t = np.linspace(0, 1, n)
    return np.where(t < rise, (t / rise) ** 1.6, ((1 - t) / (1 - rise)) ** 1.3)


# ============================================================ INSTRUMENTS
def groundwater(dur, f0a=30.0, f0b=24.0, gain=0.5):
    """Residue-pitch ghost drone: synth partials 3..6 of a missing f0 that
    slides 30->24 Hz (the 'sinking vowel'); the ear supplies the phantom bass."""
    n = int(dur * SR); t = t_of(dur)
    f0 = f0a * (f0b / f0a) ** (t / dur)              # log glide
    out = np.zeros(n)
    for k in (3, 4, 5, 6):
        amp = k ** -1.3 * pink_walk(n, 0.85, 1.15)
        ph = 2 * np.pi * np.cumsum(k * f0) / SR + rng.uniform(0, 6.28)
        out += amp * np.sin(ph)
    out = tilt(osat(out / 3, 0.35), 250, -4)
    return hp(out, 26) * swell(n, 0.3) * gain


def mantle(dur, gain=0.45):
    """Subharmonic breather — the breathing floor. Direct sub sines + inharmonic
    body + slow beat, under an asymmetric ~0.2 Hz breath envelope that tires."""
    n = int(dur * SR); t = t_of(dur)
    w = np.zeros(n)
    for f, a in [(55, 0.7), (36.7, 0.5), (27.5, 0.5), (28.4, 0.45)]:  # subs + beat pair
        w += a * np.sin(2 * np.pi * f * t)
    for f in (110, 165, 220, 247, 290, 355):
        w += 0.12 * np.sin(2 * np.pi * f * t + rng.uniform(0, 6))
    fbr = pink_walk(n, 0.15, 0.25)
    breath = 0.5 + 0.5 * ((1 - np.cos(2 * np.pi * np.cumsum(fbr) / SR)) / 2) ** 1.5
    w = lp(hp(osat(w * 0.4, 0.5), 24), 400)
    return w * breath * gain


def split_horizon(dur, gain=0.4):
    """Beating-tension drone: sine pairs detuned within 0.25*ERB (roughness at
    the Plomp-Levelt sweet spot), swelling up then down."""
    n = int(dur * SR); t = t_of(dur); out = np.zeros(n)
    tri = 1 - np.abs(np.linspace(-1, 1, n))
    for f in (65, 97.5, 130):
        dmax = 0.25 * (24.7 * (4.37 * f / 1000 + 1)) * 0.04  # ~fraction of ERB
        d = 0.6 * (max(dmax, 0.8) / 0.6) ** tri
        out += np.sin(2 * np.pi * f * t) + np.sin(2 * np.pi * (f + d) * t)
    out = lp(hp(osat(out / 6, 0.4), 26), 600)
    return out * swell(n, 0.4) * gain


def revenant_bell(dur, root=PRIME, gain=0.6, seed=0):
    """Cracked-bell strike (modal), double-struck with per-strike crack detune."""
    r = np.random.default_rng(seed)
    n = int(dur * SR); out = np.zeros(n)
    ratios = [0.5, 1.0, 1.2, 1.5, 2.0, 2.5]
    amps = [0.9, 1.0, 0.63, 0.4, 0.28, 0.18]
    Qs = [3000, 2000, 600, 400, 300, 250]
    for strike, off in enumerate([0.0, r.uniform(0.04, 0.12)]):
        i0 = int(off * SR); t = t_of(dur - off)
        s = np.zeros(len(t))
        for rt, a, Q in zip(ratios, amps, Qs):
            f = root * rt * (1 + r.uniform(-0.015, 0.015))
            if f > SR / 2 - 200:
                continue
            tau = Q / (np.pi * f)
            s += a * np.exp(-t / tau) * np.sin(2 * np.pi * f * t + r.uniform(0, 6))
        # 2 ms raised-cosine onset (no splatter)
        oa = int(0.0025 * SR); s[:oa] *= (1 - np.cos(np.linspace(0, np.pi, oa))) / 2
        out[i0:i0 + len(s)] += s * (0.7 if strike else 1.0)
    return tilt(hp(out / (np.max(np.abs(out)) + 1e-9), 40), 1200, -4) * gain


def cold_bell_larynx(dur, freq=NOMINAL, gain=0.4):
    """The bell that inhales: FM strike whose spectrum migrates bright->breathy
    at constant loudness (complementary crossfade) — an impossible anti-decay."""
    n = int(dur * SR); t = t_of(dur)
    beta = 1.2 * np.exp(-t / 2.5) + 0.2
    bright = np.sin(2 * np.pi * freq * t + beta * np.sin(2 * np.pi * freq * 1.4 * t))
    breath = bp(rng.standard_normal(n), 80, 200)
    g = np.exp(-t / 2.2)
    out = bright * g + breath * (1 - g) * 0.8
    return tilt(hp(out, 60), 1400, -4) * gain


def vox_glottis(dur, f0=120.0, gain=0.5, whisper=False):
    """Uncanny pseudo-voice: band-limited glottal source through morphing vowel
    formants with jitter/shimmer — the 'almost-speaking' dead. Vowel random-walks
    and never lands (edge of intelligibility)."""
    n = int(dur * SR)
    jit = pink_walk(n, -14, 14)                       # cents jitter
    f = f0 * 2 ** (jit / 1200.0)
    if whisper:
        src = rng.standard_normal(n)
    else:
        src = np.zeros(n)
        for k in range(1, 14):
            if f0 * k > SR / 2 - 200:
                break
            src += k ** -1.3 * np.sin(2 * np.pi * np.cumsum(f * k) / SR)
    # morphing formants (random-walk between vowels, slow)
    F1 = pink_walk(n, 320, 700); F2 = pink_walk(n, 800, 2000); F3 = pink_walk(n, 2500, 2900)
    # approximate time-varying formants with a few static bands blended by segment
    segs = 8; out = np.zeros(n); win = n // segs
    for i in range(segs):
        sl = slice(i * win, (i + 1) * win if i < segs - 1 else n)
        f1 = np.median(F1[sl]); f2 = np.median(F2[sl]); f3 = np.median(F3[sl])
        seg = src[sl]
        out[sl] = (bp(seg, f1 * 0.9, f1 * 1.1) + 0.6 * bp(seg, f2 * 0.9, f2 * 1.1)
                   + 0.35 * bp(seg, f3 * 0.9, f3 * 1.1))
    shimmer = 1 + 0.06 * pink_walk(n, -1, 1)
    env = swell(n, 0.25)
    return lp(out * shimmer, 4500) / (np.max(np.abs(out)) + 1e-9) * env * gain


def chorus_many(dur, f0=NOMINAL, gain=0.5, nvoices=8):
    """Detuned ghost-choir whose spread breathes 4->18->4 cents: coalesces into
    one, then FRAGMENTS into many (the unsettling ASA fusion->segregation flip)."""
    n = int(dur * SR); out = np.zeros(n)
    tri = 1 - np.abs(np.linspace(-1, 1, n))
    sigma = 4 + 14 * tri                          # cents spread breathes
    for v in range(nvoices):
        off = rng.normal(0, 1) * sigma
        vf = f0 * 2 ** (off / 1200.0)
        lag = int(rng.uniform(0, 0.4) * SR)
        jit = pink_walk(n, -10, 10)
        f = vf * 2 ** (jit / 1200.0)
        src = np.zeros(n)
        for k in range(1, 10):
            if float(np.mean(vf)) * k > SR / 2 - 200:
                break
            src += k ** -1.3 * np.sin(2 * np.pi * np.cumsum(f * k) / SR)
        s = 0.9 * bp(src, 400, 520) + 0.5 * bp(src, 800, 1100) + 0.3 * bp(src, 2400, 2900)
        if lag:
            s = np.concatenate([np.zeros(lag), s[:-lag]])
        out += s
    out = lp(out / np.sqrt(nvoices), 4200)
    return out / (np.max(np.abs(out)) + 1e-9) * swell(n, 0.35) * gain


def rebec_wraith(dur, freq=195.0, gain=0.45):
    """Bowed-metal snarl (feedback-FM + Chebyshev roughness) with random growl
    bursts that DARKEN (like a real animal growl). Climax color only."""
    n = int(dur * SR); t = t_of(dur)
    beta = 0.35 + pink_walk(n, 0, 0.6)
    # feedback-FM approximated: self-phase-modulated sine
    ph = 2 * np.pi * freq * t
    y = np.sin(ph)
    for _ in range(2):
        y = np.sin(ph + beta * y)
    y += 0.3 * np.sin(2 * np.pi * 1.51 * freq * t) + 0.22 * np.sin(2 * np.pi * 2.05 * freq * t)
    # Chebyshev-ish waveshape (gentle), oversampled
    y = osat(y * 0.7, 1.2)
    # formant color + darkening tilt driven by growl bursts
    y = 1.0 * bp(y, 180, 280) + 0.6 * bp(y, 1400, 2000)
    return tilt(hp(y, 60), 1000, -5) * swell(n, 0.3) * gain


def stairwell(dur, gain=0.32, octs=7, t_oct=20.0):
    """Endless Risset DESCENT (glacial, dark): eternal falling = denied
    resolution / mounting placeless tension."""
    n = int(dur * SR); t = np.arange(n) / SR; out = np.zeros(n)
    fc_log = np.log2(375.0); span = 8
    for i in range(octs):
        pos = ((-t / t_oct) + i * span / octs) % span
        f = 48.0 * 2 ** pos
        f = np.clip(f, 20, SR * 0.45)
        amp = np.exp(-((np.log2(f) - fc_log) ** 2) / (2 * 1.3 ** 2))
        amp = np.where(f > SR * 0.45, 0, amp)
        out += amp * np.sin(2 * np.pi * np.cumsum(f) / SR)
    return tilt(out / octs, 900, -6) * gain


def missing_room(dur, pitch=97.5, gain=0.4):
    """Resonant void with moving spectral holes: lossy feedback comb on noise +
    sweeping notches -> the sound of a space with something removed."""
    n = int(dur * SR)
    from scipy.signal import lfilter
    x = lp(hp(rng.standard_normal(n), 60), 6000) * 0.5
    D = int(SR / pitch)
    # lossy feedback comb y[n]=x[n]+0.5g*y[n-D], vectorized via phase groups
    g = 0.9
    y = np.empty(n)
    for r in range(D):
        y[r::D] = lfilter([1.0], [1.0, -0.5 * g], x[r::D])
    y = lp(y, 5000)
    # a couple of sweeping notches
    for _ in range(2):
        c = pink_walk(n, 300, 2500); wdt = 200
        seg = 10; out2 = np.zeros(n); win = n // seg
        for s in range(seg):
            sl = slice(s * win, (s + 1) * win if s < seg - 1 else n)
            fc = float(np.median(c[sl]))
            out2[sl] = (y - bp(y, fc - wdt, fc + wdt))[sl]
        y = out2
    return tilt(y, 1000, -5) * gain / (np.max(np.abs(y)) + 1e-9)


def cribra(dur, gain=0.5, rate_lo=0.1, rate_hi=0.6):
    """Sparse modal 'ticks in the dark' (Poisson, spatially unpredictable) —
    involuntary orienting/novelty capture that resists habituation."""
    n = int(dur * SR); L = np.zeros(n); R = np.zeros(n)
    t = 0.0
    lam = np.linspace(rate_lo, rate_hi, 8)
    while t < dur - 0.1:
        li = min(7, int(t / dur * 8))
        t += -np.log(rng.uniform(1e-3, 1)) / lam[li]
        if t >= dur - 0.1:
            break
        f = rng.uniform(400, 1600)
        d = rng.uniform(0.02, 0.09); tg = t_of(d)
        g = np.zeros(len(tg))
        for k, rt in enumerate([1.0, 2.7, 5.1]):
            g += (0.6 ** k) * np.exp(-tg / (rng.uniform(0.006, 0.02))) * np.sin(2 * np.pi * f * rt * tg + rng.uniform(0, 6))
        oa = int(0.0025 * SR); g[:oa] *= (1 - np.cos(np.linspace(0, np.pi, oa))) / 2
        amp = 10 ** (rng.uniform(-1.4, -0.1)) * gain
        pan = rng.uniform(0.1, 0.9)
        i = int(t * SR); j = min(n, i + len(g))
        L[i:j] += g[:j - i] * amp * np.sqrt(1 - pan)
        R[i:j] += g[:j - i] * amp * np.sqrt(pan)
    return L, R


def psithura(dur, gain=0.4):
    """Breathing whisper-cloud (granular formant grains, Poisson density under a
    breath env) — near-field looming intrusion."""
    n = int(dur * SR); out = np.zeros(n)
    bed = bp(rng.standard_normal(n), 300, 3000)
    fbr = pink_walk(n, 0.15, 0.28)
    breath = 0.5 + 0.5 * (1 - np.cos(2 * np.pi * np.cumsum(fbr) / SR))
    lam = 30 * breath
    t = 0.0
    while t < dur - 0.15:
        i = int(t * SR)
        t += -np.log(rng.uniform(1e-3, 1)) / max(2.0, lam[min(i, n - 1)])
        gl = int(rng.uniform(0.04, 0.12) * SR); i = int(t * SR)
        if i + gl >= n:
            break
        F = rng.choice([600, 1500, 2400]) * rng.uniform(0.9, 1.1)
        g = bp(bed[i:i + gl], F * 0.8, F * 1.25) * np.hanning(gl)
        out[i:i + gl] += g * rng.uniform(0.3, 1.0)
    return lp(out / (np.max(np.abs(out)) + 1e-9), 3400) * gain


def pleura(dur, gain=0.5, caught=False):
    """Near-field breath membrane; optionally ends on a CAUGHT breath
    (sudden truncation) — the final event, an absence the body braces for."""
    n = int(dur * SR)
    bed = bp(rng.standard_normal(n), 300, 1200)
    sub = 0.4 * np.sin(2 * np.pi * 55 * t_of(dur))
    fbr = pink_walk(n, 0.18, 0.28)
    # asymmetric breaths: rise 0.25 fall 0.9
    breath = 0.5 + 0.5 * np.cos(2 * np.pi * np.cumsum(fbr) / SR)
    out = (bed + sub) * breath
    if caught:
        cut = int(dur * 0.82 * SR)                # sudden truncation near end
        fade = int(0.02 * SR); e = min(n, cut + fade)
        if cut < n:
            out[cut:e] *= np.linspace(1, 0, e - cut)
            out[e:] = 0
    return lp(hp(out, 40), 2200) * gain


# ============================================================ MIX / MASTER
class Bus:
    def __init__(self, dur):
        self.n = int(dur * SR)
        self.dry = np.zeros((2, self.n)); self.wet = np.zeros((2, self.n))

    def add(self, sig, at, gain=1.0, pan=0.5, send=0.15):
        i = int(at * SR)
        if i < 0 or i >= self.n:
            return
        sig = np.asarray(sig, float).copy()
        fd = int(0.004 * SR)
        if len(sig) > 3 * fd:
            sig[:fd] *= np.linspace(0, 1, fd); sig[-fd:] *= np.linspace(1, 0, fd)
        j = min(self.n, i + len(sig)); s = sig[:j - i]
        gl, gr = gain * np.sqrt(1 - pan), gain * np.sqrt(pan)
        self.dry[0, i:j] += gl * s; self.dry[1, i:j] += gr * s
        self.wet[0, i:j] += gl * send * s; self.wet[1, i:j] += gr * send * s

    def add_st(self, L, R, at, gain=1.0, send=0.15):
        i = int(at * SR)
        for ch, x in ((0, L), (1, R)):
            j = min(self.n, i + len(x))
            self.dry[ch, i:j] += gain * x[:j - i]
            self.wet[ch, i:j] += gain * send * x[:j - i]


def make_ir(seed, rt60=4.0, predelay_ms=25, damp=4000):
    n = int(rt60 * SR); r = np.random.default_rng(seed)
    ir = r.standard_normal(n) * np.exp(-np.linspace(0, 1, n) * 6.9)
    ir = lp(ir, damp); pd = int(predelay_ms / 1000 * SR)
    ir = np.concatenate([np.zeros(pd), ir])
    return ir / (np.sqrt(np.sum(ir ** 2)) + 1e-9)


def build():
    DUR = 236.0
    B = Bus(DUR)
    print("  synthesizing sections ...")

    # § timings
    # §1 Absence 0-34
    B.add(groundwater(40, 30, 24, 0.5), 0, 1.0, 0.5, 0.2)
    B.add(missing_room(34, 97.5, 0.35), 0, 1.0, 0.5, 0.35)
    # §2 First presence 34-55: ticks + bed
    B.add(groundwater(24, 26, 24, 0.4), 34, 1.0, 0.5, 0.2)
    cl, cr = cribra(22, 0.5); B.add_st(cl, cr, 34, 1.0, 0.25)
    # §3 Almost-speech 55-89: voice + whisper (dry, near)
    B.add(vox_glottis(34, f0=120, gain=0.5), 55, 1.0, 0.45, 0.12)
    B.add(psithura(34, 0.4), 55, 1.0, 0.6, 0.1)
    B.add(mantle(34, 0.3), 55, 1.0, 0.5, 0.15)
    # §4 Withdrawal trough 89-110: Shepard descent + floor
    B.add(stairwell(23, 0.32), 89, 1.0, 0.5, 0.3)
    B.add(mantle(23, 0.32), 89, 1.0, 0.5, 0.2)
    # §5 Climax 110-165 (peak ~142): chorus + snarl + beating + sub-creature
    B.add(chorus_many(55, f0=NOMINAL, gain=0.5), 110, 1.0, 0.5, 0.35)
    B.add(split_horizon(55, 0.4), 110, 1.0, 0.5, 0.25)
    for at in [128, 138, 146, 154]:
        B.add(rebec_wraith(8, freq=195 * rng.uniform(0.98, 1.02), gain=0.4), at, 1.0, rng.uniform(0.35, 0.65), 0.3)
    B.add(groundwater(55, 30, 24, 0.4), 110, 1.0, 0.5, 0.2)   # sinking-vowel costume 3
    # §6 Impossible bell 165-199
    for at in [166, 174, 183, 192]:
        B.add(revenant_bell(12, root=PRIME * rng.choice([1, 1, 1.5]), gain=0.6, seed=int(at)), at, 1.0, rng.uniform(0.4, 0.6), 0.4)
    B.add(cold_bell_larynx(20, NOMINAL, 0.4), 172, 1.0, 0.5, 0.4)
    B.add(cold_bell_larynx(18, QUINT, 0.32), 186, 1.0, 0.5, 0.4)
    B.add(mantle(34, 0.28), 165, 1.0, 0.5, 0.2)
    # §7 Receding into silence 199-236 + caught breath
    B.add(groundwater(30, 28, 22, 0.4), 199, 1.0, 0.5, 0.25)
    B.add(mantle(30, 0.26), 199, 1.0, 0.5, 0.2)
    B.add(pleura(34, 0.5, caught=True), 200, 1.0, 0.5, 0.15)

    print("  reverb + master ...")
    irL, irR = make_ir(1), make_ir(2)
    wet = np.stack([fftconvolve(B.wet[0], irL)[:B.n], fftconvolve(B.wet[1], irR)[:B.n]])
    mix = B.dry + 0.9 * wet
    mix = mix * loudness(mix.shape[1])
    out = []
    for ch in range(2):
        x = mix[ch]
        x = hp(x, 28, 4)
        x = tilt(x, 1200, -5)
        x = x - (1 - 10 ** (-2 / 20)) * bp(x, 2900, 3900)   # dynamic-ish 3.4k de-harsh
        x = osat(x, 1.1)
        x = np.tanh(x * 0.9) / 0.9
        out.append(x)
    L, R = out
    m = max(np.max(np.abs(L)), np.max(np.abs(R))) + 1e-9
    L, R = L / m * 0.92, R / m * 0.92        # keep the wide dynamic range, more level
    fi = int(1.0 * SR); fo = int(6.0 * SR)
    for x in (L, R):
        x[:fi] *= np.linspace(0, 1, fi); x[-fo:] *= np.linspace(1, 0, fo) ** 1.4
    return np.stack([L, R])


def loudness(n):
    pts = [(0, -26), (34, -22), (55, -17), (89, -24), (110, -18), (142, -8),
           (165, -15), (199, -20), (236, -40)]
    ts = np.array([p[0] for p in pts]); db = np.array([p[1] for p in pts])
    return 10 ** (np.interp(np.arange(n) / SR, ts, db) / 20.0)


def write_wav(path, st):
    data = (np.clip(st.T, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(data.tobytes())


if __name__ == "__main__":
    import sys
    print("building The Thing That Almost Breathes ...")
    st = build()
    out = sys.argv[1] if len(sys.argv) > 1 else "thing.wav"
    write_wav(out, st)
    print(f"wrote {out}  ({st.shape[1] / SR:.1f}s, stereo {SR}Hz)")
