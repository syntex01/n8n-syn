# synth — alien-but-catchy soundtrack engine (v2)

A dependency-light (numpy + scipy + stdlib `wave`) synth that renders a ~3:13
modern pop/electronic track engineered for **catchiness and replay-craving**,
grounded in the verified psychoacoustics in [`../REPORT.md`](../REPORT.md).
Design thesis: **alien skin, human skeleton — addictive, not trance.**

## Run

```bash
pip install numpy scipy
python3 engine.py soundtrack.wav      # ~9s render, stereo 44.1kHz, ~3:13
python3 overview.py soundtrack.wav overview.png   # waveform + section map (needs matplotlib)
```

Deterministic (seeded).

## What it bakes in (v2)

- **The "Axis" minor vamp** (Am–F–C–G) — one of the stickiest progressions —
  with real harmonic *movement* (not a drone), so it stays catchy not hypnotic.
- **A repeated earworm hook**: a conventional arch contour that *leaps* up to a
  long held peak note (the peak gets a small +15-cent **alien** lean for
  identity), with a call-and-response answer phrase.
- **Multiple anticipation→drop cycles** (the dopaminergic engine): two builds
  with accelerating snare rolls + filter-opening risers, into escalating drops,
  plus a half-time bridge reset before the biggest final drop.
- **Modern "cool" production**: supersaw leads/chords, **sidechain pump** locked
  to the kick, wide Haas stereo, FM plucks, vocal-chop-style formant stabs,
  16th-note arps, drop **impacts** (crash + sub-boom + noise hit).
- **Full drum kit**: punchy kick, layered clap/snare, closed+open hats, toms,
  fills; four-on-the-floor in drops, broken beat in verses, half-time bridge.
- **Octave-bounce bassline** for groove movement; low-mids carved so the hook
  and bass each breathe.
- **Unresolved earworm tail**: ends hanging on the alien peak note (open loop).

## Structure
`Intro → Verse A → Build → DROP 1 → Verse B → Build → DROP 2 → Bridge → FINAL DROP → Outro`
(96 bars @ 122 BPM). See `overview.png`.

## Files
- `engine.py` — synth + arrangement (every effect annotated inline).
- `overview.py` — renders the waveform/energy/section visualization.
- `research-sources.md` — verified sources, claims, and the refuted/avoided ones.
