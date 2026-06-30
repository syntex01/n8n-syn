# synth — alien-but-clicking soundtrack engine

A dependency-light (numpy + stdlib `wave`) additive/subtractive synth that
renders a ~2:34 stereo track engineered around the verified psychoacoustics in
[`../REPORT.md`](../REPORT.md). Design thesis: **alien skin, human skeleton.**

## Run

```bash
pip install numpy
python3 engine.py soundtrack.wav
```

Output: `soundtrack.wav` (stereo, 44.1 kHz, ~2:34). Deterministic (seeded).

## What it bakes in

- **7-limit just-intonation** tuning — consonant skeleton, alien 7/6, 11/8,
  7/4 intervals on the surface.
- **Anticipation→resolution** arcs: two breakdown→drop cycles (the dopaminergic
  craving/payoff engine).
- **Medium-syncopation groove** (the urge-to-move sweet spot) + swing micro-timing.
- **Earworm hook**: conventional arch contour with a leap onto the alien 7/4;
  alternating subtle variations; left **unresolved** at the end (open loop).
- **Inharmonic bell pads** (otherworldly, still pitched) vs a clean singable lead.
- **Sub-bass** body coupling; **real rhythmic AM entrainment** (no binaural myth);
  **register-lift + shimmer** frisson at the drops.

## Files
- `engine.py` — the synth + arrangement (each effect annotated inline).
- `research-sources.md` — verified sources, claims, and the refuted/avoided ones.
