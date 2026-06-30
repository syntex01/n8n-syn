"""Render a waveform + energy + section-map overview PNG of the track."""
import sys
import wave

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SR = 44100
BPM = 122.0
BAR = 4 * 60 / BPM

SECTIONS = [
    (0, 8, "Intro", "#2b3a55"), (8, 16, "Verse A", "#3a5068"),
    (16, 20, "Build", "#7a4f9e"), (20, 36, "DROP 1", "#e0533d"),
    (36, 44, "Verse B", "#3a5068"), (44, 48, "Build", "#7a4f9e"),
    (48, 68, "DROP 2", "#e0533d"), (68, 76, "Bridge", "#3f7a6a"),
    (76, 92, "FINAL DROP", "#f08030"), (92, 96, "Outro", "#2b3a55"),
]


def main(path, out):
    w = wave.open(path, "rb"); n = w.getnframes(); sr = w.getframerate()
    d = np.frombuffer(w.readframes(n), dtype="<i2").astype(float) / 32767
    d = d.reshape(-1, 2); mono = d.mean(1); dur = n / sr
    t = np.arange(n) / sr

    # downsample envelope for waveform
    win = 512
    m = len(mono) // win
    env = np.abs(mono[:m * win]).reshape(m, win).max(1)
    te = np.linspace(0, dur, m)
    # rms energy per 0.25s
    rw = int(0.25 * sr); rm = len(mono) // rw
    rms = np.sqrt((mono[:rm * rw].reshape(rm, rw) ** 2).mean(1))
    tr = np.linspace(0, dur, rm)

    fig, ax = plt.subplots(2, 1, figsize=(14, 6), height_ratios=[2, 1])
    fig.patch.set_facecolor("#0e1117")
    for a in ax:
        a.set_facecolor("#0e1117")
        for sp in a.spines.values():
            sp.set_color("#444")
        a.tick_params(colors="#aaa")

    ax[0].fill_between(te, env, -env, color="#5ad1e6", lw=0)
    ax[0].set_ylim(-1, 1); ax[0].set_xlim(0, dur)
    ax[0].set_title("alien-but-catchy  —  waveform & arrangement", color="#eee", fontsize=13)
    ax[0].set_yticks([])
    for b0, b1, label, col in SECTIONS:
        x0, x1 = b0 * BAR, b1 * BAR
        ax[0].axvspan(x0, x1, color=col, alpha=0.22)
        ax[0].text((x0 + x1) / 2, 0.86, label, ha="center", va="top",
                   color="#fff", fontsize=8, fontweight="bold")
        ax[0].axvline(x0, color="#222", lw=0.6)

    ax[1].fill_between(tr, rms, color="#f0a030", alpha=0.8, lw=0)
    ax[1].plot(tr, rms, color="#ffd27f", lw=0.8)
    ax[1].set_xlim(0, dur); ax[1].set_ylim(0, rms.max() * 1.1)
    ax[1].set_ylabel("energy (RMS)", color="#aaa", fontsize=9)
    ax[1].set_xlabel("time (s)", color="#aaa", fontsize=9)
    ax[1].set_yticks([])

    plt.tight_layout()
    fig.savefig(out, dpi=110, facecolor=fig.get_facecolor())
    print("wrote", out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "soundtrack.wav",
         sys.argv[2] if len(sys.argv) > 2 else "overview.png")
