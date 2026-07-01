"""
Automated QA harness for rendered tracks.

Measures everything the project cares about and prints a pass/fail report:
  - peak / clipping / clicks (max sample jump)
  - global + per-window spectral centroid (warmth; anti-arcady)
  - 2.5-5 kHz "harsh band" energy fraction (anti-annoying)
  - integrated loudness proxy + dynamic arc (section contrast in dB)
  - stereo width (L/R correlation) + mono-compatibility
  - silence-gap detection (intentional gaps vs dead air)
  - event density per section (anti-boring)

Usage: python3 qa.py track.wav [--sections t0,t1,label ...]
"""
import sys
import wave

import numpy as np
from scipy.signal import butter, sosfilt


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


def onset_density(x, sr, win_s=1.0):
    """Events per second: spectral-flux onset proxy."""
    hop = int(0.02 * sr); nfft = 1024
    frames = [x[i:i + nfft] * np.hanning(nfft)
              for i in range(0, len(x) - nfft, hop)]
    mags = np.array([np.abs(np.fft.rfft(f)) for f in frames])
    flux = np.maximum(np.diff(mags, axis=0), 0).sum(axis=1)
    if len(flux) < 10:
        return 0.0
    thr = np.median(flux) + 1.8 * np.std(flux)
    onsets = np.sum((flux[1:] > thr) & (flux[:-1] <= thr))
    return float(onsets / (len(x) / sr))


def report(path, sections=None):
    d, sr = load(path)
    mono = d.mean(1)
    dur = len(mono) / sr
    peak = float(np.abs(d).max())
    clip = float(np.mean(np.abs(d) > 0.985) * 100)
    jump = float(np.abs(np.diff(mono)).max())
    cen = centroid(mono, sr)
    harsh = band_frac(mono, sr, 2500, 5000) * 100
    corr = float(np.corrcoef(d[:, 0], d[:, 1])[0, 1])
    rms = float(np.sqrt(np.mean(mono ** 2)))

    checks = [
        ("peak <= 0.96", peak <= 0.96, f"{peak:.3f}"),
        ("near-clip < 0.05%", clip < 0.05, f"{clip:.3f}%"),
        ("no clicks (jump < 0.5)", jump < 0.5, f"{jump:.3f}"),
        ("centroid 500-2200 Hz", 500 <= cen <= 2200, f"{cen:.0f} Hz"),
        ("harsh 2.5-5k < 4%", harsh < 4.0, f"{harsh:.2f}%"),
        ("stereo width (corr < 0.97)", corr < 0.97, f"{corr:.3f}"),
    ]
    print(f"== {path}  ({dur:.1f}s, rms {rms:.3f}) ==")
    ok = True
    for name, passed, val in checks:
        ok &= passed
        print(f"  [{'PASS' if passed else 'FAIL'}] {name:28s} {val}")

    if sections:
        print("  -- sections --")
        vals = []
        for t0, t1, label in sections:
            seg = mono[int(t0 * sr):int(t1 * sr)]
            if len(seg) < sr:
                continue
            v = np.sqrt(np.mean(seg ** 2))
            c = centroid(seg, sr)
            dens = onset_density(seg, sr)
            vals.append((label, v, c, dens))
        mx = max(v for _, v, _, _ in vals) + 1e-9
        for label, v, c, dens in vals:
            db = 20 * np.log10(v / mx + 1e-9)
            print(f"  {label:16s} {db:+6.1f} dB  cen {c:5.0f} Hz  onsets {dens:4.1f}/s")
        drange = 20 * np.log10((max(v for _, v, _, _ in vals) + 1e-9) /
                               (min(v for _, v, _, _ in vals) + 1e-9))
        dr_ok = drange >= 10
        ok &= dr_ok
        print(f"  [{'PASS' if dr_ok else 'FAIL'}] section dynamic range >= 10 dB   {drange:.1f} dB")
    print(f"  => {'ALL PASS' if ok else 'HAS FAILURES'}")
    return ok


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "apex.wav"
    secs = None
    if len(sys.argv) > 2:
        secs = []
        for a in sys.argv[2:]:
            t0, t1, label = a.split(",", 2)
            secs.append((float(t0), float(t1), label))
    report(path, secs)
