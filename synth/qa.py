"""
Addiction-first QA harness (implements the workflow build spec, §10).

Beyond the acoustic-safety checks (peak / clip / clicks / centroid / harsh /
stereo) it asserts the crave-replay gates the addiction spec demands:

  - onset-density FLOOR   : >= 4.0 onsets/s in EVERY 3 s window (bars 4-80)
  - beat continuity       : max percussive inter-onset gap <= 1.9 s (bars 4-80)
  - hook-early            : a pitched onset in 250-750 Hz before t = 7.0 s
  - section dynamic range : loudest/quietest sustained section in 1.4x-2.5x
                            (=3-8 dB) -- present but NOT an art-music valley
  - loudness FLOOR        : min 4 s-window RMS (bars 4-80) >= 0.60 x peak window
  - spectral centroid     : global 900-2200 Hz; no section centroid > 3000 Hz
  - harsh energy          : 2.8-5 kHz < 4% of total
  - tonic resolution      : last 3 s dominated by pitch-class D

Usage: python3 qa.py track.wav [bar0 bar1 ... custom section bars]
The default section map matches addictive.py (140 BPM, 84 bars).
"""
import sys
import wave

import numpy as np
from scipy.signal import butter, sosfilt

BPM = 140.0
BAR = 4 * 60.0 / BPM            # 1.714286 s

# sustained sections (bar0, bar1, label) — cold-open & outro excluded on purpose
DEFAULT_SECTIONS = [
    (4, 12, "chorus1"), (12, 20, "verse1"), (20, 28, "chorus2"),
    (28, 36, "verse2"), (36, 44, "frisson"), (48, 64, "bigdrop"),
    (64, 72, "verse3"), (72, 80, "reprise"),
]
BODY = (4 * BAR, 80 * BAR)      # analysis window for the floor gates


def load(path):
    w = wave.open(path, "rb")
    n, sr = w.getnframes(), w.getframerate()
    d = np.frombuffer(w.readframes(n), dtype="<i2").astype(float) / 32767
    return d.reshape(-1, 2), sr


def centroid(x, sr):
    X = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    fr = np.fft.rfftfreq(len(x), 1 / sr)
    return float(np.sum(fr * X) / (np.sum(X) + 1e-9))


def band_frac(x, sr, lo, hi):
    sos = butter(4, [lo / (sr / 2), hi / (sr / 2)], "band", output="sos")
    b = sosfilt(sos, x)
    return float(np.sum(b ** 2) / (np.sum(x ** 2) + 1e-9))


def bandpass(x, sr, lo, hi):
    sos = butter(4, [lo / (sr / 2), hi / (sr / 2)], "band", output="sos")
    return sosfilt(sos, x)


def onset_times(x, sr, hop_s=0.01, nfft=2048, delta=0.06, min_gap_s=0.045):
    """Spectral-flux onset detector with adaptive peak-picking; returns onset
    times in seconds. Tuned to catch a persistent hat/kick pulse."""
    hop = int(hop_s * sr)
    n_frames = 1 + max(0, (len(x) - nfft) // hop)
    win = np.hanning(nfft)
    mags = np.empty((n_frames, nfft // 2 + 1))
    for i in range(n_frames):
        seg = x[i * hop:i * hop + nfft] * win
        mags[i] = np.abs(np.fft.rfft(seg))
    flux = np.maximum(np.diff(mags, axis=0), 0).sum(axis=1)
    if len(flux) < 5:
        return np.array([])
    flux = flux / (flux.max() + 1e-9)
    # moving-average adaptive floor (~0.12 s)
    w = max(1, int(0.12 / hop_s))
    kernel = np.ones(w) / w
    mavg = np.convolve(flux, kernel, mode="same")
    times = []
    last = -1e9
    min_gap = min_gap_s / hop_s
    for i in range(1, len(flux) - 1):
        if (flux[i] > mavg[i] + delta and flux[i] >= flux[i - 1]
                and flux[i] > flux[i + 1] and (i - last) >= min_gap):
            times.append((i + 1) * hop_s)   # +1: flux index -> frame index
            last = i
    return np.array(times)


def report(path, sections=None):
    d, sr = load(path)
    mono = d.mean(1)
    dur = len(mono) / sr
    peak = float(np.abs(d).max())
    clip = float(np.mean(np.abs(d) > 0.985) * 100)
    jump = float(np.abs(np.diff(mono)).max())
    cen = centroid(mono, sr)
    harsh = band_frac(mono, sr, 2800, 5000) * 100
    corr = float(np.corrcoef(d[:, 0], d[:, 1])[0, 1])
    rms = float(np.sqrt(np.mean(mono ** 2)))

    ons = onset_times(mono, sr)
    body_lo, body_hi = BODY[0], min(BODY[1], dur)

    # onset-density floor: every 3 s window in the body has >= 4.0 onsets/s
    win, step = 3.0, 0.5
    dens_min, dens_at = 1e9, 0.0
    t = body_lo
    while t + win <= body_hi:
        c = np.sum((ons >= t) & (ons < t + win)) / win
        if c < dens_min:
            dens_min, dens_at = c, t
        t += step
    dens_ok = dens_min >= 4.0

    # beat continuity: max inter-onset gap in the body
    body_ons = ons[(ons >= body_lo) & (ons <= body_hi)]
    gaps = np.diff(body_ons) if len(body_ons) > 1 else np.array([0.0])
    max_gap = float(gaps.max()) if len(gaps) else 0.0
    gap_ok = max_gap <= 1.9

    # hook-early: pitched onset in 250-750 Hz before 7.0 s
    lead_band = bandpass(mono[:int(9 * sr)], sr, 250, 750)
    lead_ons = onset_times(lead_band, sr, delta=0.04)
    first_hook = float(lead_ons[0]) if len(lead_ons) else 1e9
    hook_ok = first_hook < 7.0

    # loudness floor: min 4 s-window RMS in body >= 0.60 x max window
    wl = int(4 * sr)
    rms_wins = []
    times_w = []
    i = int(body_lo * sr)
    while i + wl <= int(body_hi * sr):
        seg = mono[i:i + wl]
        rms_wins.append(np.sqrt(np.mean(seg ** 2)))
        times_w.append(i / sr)
        i += int(0.5 * sr)
    rms_wins = np.array(rms_wins)
    floor_ratio = float(rms_wins.min() / (rms_wins.max() + 1e-9)) if len(rms_wins) else 0.0
    floor_at = float(times_w[int(np.argmin(rms_wins))]) if len(rms_wins) else 0.0
    floor_ok = floor_ratio >= 0.60

    # tonic resolution: last 3 s dominated by pitch-class D
    tail = mono[int((dur - 3) * sr):]
    Xt = np.abs(np.fft.rfft(tail * np.hanning(len(tail))))
    ft = np.fft.rfftfreq(len(tail), 1 / sr)
    d_energy = sum(band_frac(tail, sr, f * 0.97, f * 1.03) for f in (73.4, 146.8, 293.7))
    peak_f = float(ft[np.argmax(Xt)])
    tonic_ok = min(abs(peak_f - 146.8), abs(peak_f - 293.7), abs(peak_f - 73.4)) < 8.0 or d_energy > 0.35

    checks = [
        ("peak <= 0.96", peak <= 0.96, f"{peak:.3f}"),
        ("near-clip < 0.05%", clip < 0.05, f"{clip:.3f}%"),
        ("no clicks (jump < 0.5)", jump < 0.5, f"{jump:.3f}"),
        ("centroid 900-2200 Hz", 900 <= cen <= 2200, f"{cen:.0f} Hz"),
        ("harsh 2.8-5k < 4%", harsh < 4.0, f"{harsh:.2f}%"),
        ("stereo width (corr < 0.97)", corr < 0.97, f"{corr:.3f}"),
        ("onset floor >= 4.0/s (3s win)", dens_ok, f"{dens_min:.1f}/s @ {dens_at:.0f}s"),
        ("beat gap <= 1.9 s", gap_ok, f"{max_gap:.2f} s"),
        ("hook-early (< 7.0 s)", hook_ok, f"{first_hook:.2f} s"),
        ("loudness floor >= 0.60x", floor_ok, f"{floor_ratio:.2f}x @ {floor_at:.0f}s"),
        ("tonic resolve (D) at end", tonic_ok, f"peak {peak_f:.0f}Hz Dfrac {d_energy:.2f}"),
    ]
    print(f"== {path}  ({dur:.1f}s, rms {rms:.3f}, {len(ons)} onsets = {len(ons)/dur:.1f}/s) ==")
    ok = True
    for name, passed, val in checks:
        ok &= passed
        print(f"  [{'PASS' if passed else 'FAIL'}] {name:30s} {val}")

    secs = sections or [(b0 * BAR, b1 * BAR, lab) for b0, b1, lab in DEFAULT_SECTIONS]
    print("  -- sustained sections --")
    vals = []
    for t0, t1, label in secs:
        seg = mono[int(t0 * sr):int(t1 * sr)]
        if len(seg) < sr:
            continue
        v = np.sqrt(np.mean(seg ** 2))
        c = centroid(seg, sr)
        so = ons[(ons >= t0) & (ons < t1)]
        dens = len(so) / (t1 - t0)
        vals.append((label, v, c, dens))
    mx = max(v for _, v, _, _ in vals) + 1e-9
    hi_cen_ok = True
    for label, v, c, dens in vals:
        db = 20 * np.log10(v / mx + 1e-9)
        hi_cen_ok &= c <= 3000
        print(f"  {label:10s} {db:+6.1f} dB  cen {c:5.0f} Hz  onsets {dens:4.1f}/s")
    ratio = (max(v for _, v, _, _ in vals) + 1e-9) / (min(v for _, v, _, _ in vals) + 1e-9)
    drange_db = 20 * np.log10(ratio)
    dr_ok = 1.4 <= ratio <= 2.5
    ok &= dr_ok and hi_cen_ok
    print(f"  [{'PASS' if dr_ok else 'FAIL'}] section range 1.4-2.5x (3-8 dB)   {ratio:.2f}x ({drange_db:.1f} dB)")
    print(f"  [{'PASS' if hi_cen_ok else 'FAIL'}] no section centroid > 3000 Hz")
    print(f"  => {'ALL PASS' if ok else 'HAS FAILURES'}")
    return ok


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "addictive.wav"
    report(path)
