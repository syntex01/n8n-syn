# Alien-but-Clicking Music: Research Synthesis & Design

A deep-research sweep (108 agents: fan-out web search → source extraction →
3-vote adversarial verification → synthesis) on what makes music "addicting"
and what lets *genuinely novel* sound still click with the human brain.
**25 claims verified, 24 confirmed (mostly unanimous 3-0), 1 refuted.** All
retained findings rest on primary peer-reviewed sources.

---

## 1. The verified core: an "optimal-surprise" reward engine

**Music is addicting because abstract sound hijacks the same dopamine reward
circuit as food, sex, and money — and the trigger is *prediction*, not the
sound itself.**

- **Dopamine is causal, not correlational.** PET imaging shows endogenous
  dopamine release in the striatum at peak pleasure ("chills"). Crucially,
  giving people **levodopa** (more dopamine) *increased* musical pleasure,
  while **risperidone** (a dopamine blocker) *reduced* it — a direct causal
  chain. (Salimpoor et al. 2011, *Nat Neurosci*; Ferreri et al. 2019, *PNAS*.)
- **Anticipation and pleasure are anatomically split.** Dopamine release in
  the **caudate** happens during the *anticipation*; release in the **nucleus
  accumbens** happens at the *peak*. The wanting and the liking are separate
  systems — so you can engineer the craving (the build) and the payoff (the
  drop) independently. (Salimpoor et al. 2011.)
- **The accumbens literally prices music.** NAcc activity while hearing a
  *previously-unheard* track predicts how much real money people will pay for
  it. Reward value is computed from prediction, before familiarity. (Salimpoor
  et al. 2013, *Science*.)
- **Pleasure = the interplay of uncertainty × surprise.** Chord pleasantness
  is jointly, *non-linearly* predicted by predictive uncertainty (entropy,
  before) and surprise (information content, after) **and their interaction** —
  not by surprise alone. (Cheung et al. 2019, *Current Biology*.)
- **The inverted-U "sweet spot."** Liking peaks at *intermediate* predictive
  complexity — too predictable is boring, too random is noise. (Gold et al.
  2019, *PNAS*.)
- **REFUTED (so we don't build on it):** the strong claim that musical reward-
  prediction-errors *causally drive* pleasure was knocked down (0-3). RPEs are
  established for *learning* and NAcc *correlation* — not as the proven cause
  of the felt pleasure. (de Fleurian, PNAS.)

## 2. Groove — the urge to move has a measurable peak

- **Medium syncopation wins.** Pleasure and the urge to move both follow an
  inverted-U against rhythmic syncopation: **medium** beats low (boring) and
  high (chaotic). (Witek et al. 2014, *PLOS ONE*.)
- **Move-pleasure are nearly the same axis** (r ≈ .96, verified 2-1).
- Groove is the same predictability×surprise sweet-spot as §1, in the time
  domain. (Matthews/Cameron/Spiech/Witek 2022.)
- Groove **needs time to build** (10 s > 1 s excerpts) — though catchiness can
  land instantly. So: a short hook hooks fast; the *groove* rewards staying.

## 3. Earworms — the recipe for stickiness

- **Common contour + uncommon leaps.** Sticky tunes pair a *conventional*
  global rise-fall shape with a few *unusual* interval jumps. Familiar
  skeleton, surprising detail. (Jakubowski et al. 2017.)
- **Faster tempo** raises stickiness. (Same.)
- **Dose-dependent:** more repetition → stronger earworm. (Repetition study.)
- **Near-universal target:** >90% of people get earworms at least weekly;
  most are neutral-to-pleasant.

## 4. The key to "alien yet clicking": statistical learning

- The brain builds an internal statistical model of whatever music it's
  exposed to (enculturation), then predicts against it. "In tune" / "clicks"
  is *learned*, not fixed. (Pearce 2018, *Ann. NYAS*; Vuust et al. 2018.)
- **This is the whole lever:** keep the *deep universal scaffolds* (a strong
  pulse, arch contours, repetition, consonant resolution) and break only the
  *learned conventions* (12-TET tuning, timbre, specific intervals). Novelty
  lands *inside* the reward zone instead of outside it.
- **Timbre can rewrite consonance.** A 2024 *Nature Communications* study found
  consonance preference is reshapeable by timbre — listeners can even be made
  to prefer *inharmonic* sounds. "Pleasant" is more plastic than assumed —
  which is exactly why an alien palette can still feel good.

## 5. The myth we deliberately avoided

**Binaural / isochronic beats as a mind-control / trance lever are NOT
supported** by the verified literature. We use only *real* rhythmic
entrainment (the auditory system tracking a periodic amplitude envelope) and
build nothing on the binaural-beats claim. Flagged as an evidence gap, not a
settled tool.

## 6. Evidence gaps (honest limits)

The sweep was strongest on domains 1–3 and 8 (reward, groove, earworms,
prediction). Thinner verified coverage on: trance/entrainment specifics,
frisson beyond the dopamine finding, deep timbre/tuning psychoacoustics,
cross-cultural universals, and sub-bass/ASMR. The inverted-U's *location* is
individual- and culture-dependent (found in only 15/57 studies, Chmiel &
Schubert 2017). Earworm features are correlational, not causal.

---

## 7. Design principles → how the track implements them

The soundtrack (`synth/engine.py` → `soundtrack.wav`, 2:34, 104 BPM) is a
direct application. **Thesis: alien skin, human skeleton.**

| Principle (from evidence) | Implementation in the track |
|---|---|
| Dopaminergic **anticipation→resolution** (§1) | Two breakdown→drop cycles: tension pads + rising noise sweeps that *withhold* the beat, then the full drop *delivers* it. The 2nd breakdown is longer → bigger payoff. |
| **Caudate-wanting vs NAcc-liking are separable** | The *build* (riser, gap) engineers wanting; the *drop* (octave-lifted hook + sub) engineers liking. |
| **Optimal surprise / inverted-U** (§1) | Mostly-consonant 7-limit just intonation (low roughness = "clicks"), with alien 7/6, 11/8, 7/4 intervals injected as the surprise. |
| **Medium-syncopation groove** (§2) | Kick on strong beats **plus** "&"-pushes (steps 6, 11) — deliberately medium, not on-grid, not chaotic. Swing micro-timing humanizes it. |
| **Earworm = common contour + uncommon leap** (§3) | The hook is a conventional rise-fall arch whose memorable leap lands on the *alien* 7/4. |
| **Subtle variation on repeats** (§3, §1) | `hook` and `hook_var` alternate — same skeleton, one note nudged each loop (familiar-but-fresh). |
| **Alien-but-pleasant via plastic consonance/timbre** (§4) | Inharmonic, stretched-partial bell pads (otherworldly yet pitched); clean harmonic lead so the melody stays singable. |
| **Frisson / register lift** (§1 chills) | At each drop the hook jumps up an octave with added high shimmer — a classic chills trigger. |
| **Real rhythmic entrainment, NOT binaural** (§5) | Slow amplitude-modulation on the pad locks to the pulse. No binaural beats anywhere. |
| **Body coupling** | Sub-bass (~40–70 Hz) with a pitch-drop transient on the downbeats. |
| **Zeigarnik / open loop** (§3) | The track ends *unresolved* — the hook hangs on the alien 7/4, never returning to the tonic, so it keeps replaying in your head. |

---

## 8. Ethics (flagged, per the brief)

These levers are genuine and dual-use. The same dopaminergic-anticipation and
optimal-surprise mechanisms that make music *moving* are what make it
*compulsive*; pushed hard (and especially if ever personalized to an
individual's learned sweet-spot) they raise real manipulation concerns. This
project treats them as **craft for making music people love**, not as a
behavioral exploit — there is no subliminal content, no deception, and the
"addiction" here is the ordinary, benign pull of a good song. Worth keeping in
view if this is ever taken toward personalization or persuasion.

*Full source list and verification votes: `synth/research-sources.md`.*
