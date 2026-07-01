# THE MAGNUM OPUS — Final Build Spec
## "Afterglow / Ashfall" — from-scratch numpy/scipy synth, ~4:04

> This spec incorporates the adversarial critique. All P0 signal-chain bugs are fixed, the motif-encoding hedge (P1) is adopted, distinctiveness moves (P2) are folded in, theory claims are relabeled for honesty (P3), and every underspecified synth item (P4) is now concrete. Every major decision carries a one-line theory justification.

---

## 0. GOVERNING PRINCIPLE

**Warmth is the precondition for the sadness to land.** Harsh 2–8 kHz energy triggers acoustic aversion (ISO 226 sensitivity peaks ~3–4 kHz via ear-canal resonance); a defended listener will not surrender to being-moved, and the sad-music paradox (Huron; Sachs/Habibi) only operates when the listener feels safe. *(The "infant-cry/startle" framing is dropped as unproven analogy; the 3–4 kHz cut is justified from ISO 226 loudness-discomfort data alone.)*

**Three hard laws (root-cause fixes for the old harshness):**
1. **No aliased oscillators.** Every tone is additive (sum of sines), hard-capping partials at `k_max = floor(0.45·SR/f0)`.  *(Aliasing above Nyquist folds into the aversion band; capping prevents it.)*
2. **Steep partial rolloff, `a_k ∝ 1/k^s`, s ≈ 2.0** (~−12 dB/oct, triangle-like), partials 2–3 boosted ×1.3 for body; effectively nothing past the ~8th partial.  *(A dark spectral centroid keeps energy out of the aversion band.)*
3. **Percussion = filtered sine/triangle bodies + low-passed noise only.** No high-passed hiss, no bright transients.  *(Bright transients are the arcade/harsh signature.)*

Plus continuous canvas: pink spectral tilt, a reconciled 3 kHz dip, **one** oversampled asymmetric saturator, damped dark reverb, slow onsets (≥15 ms).

---

## 1. FUNDAMENTALS

- **Title:** *Afterglow / Ashfall*
- **Total duration:** 240.000 s body + ~4 s reverb tail ≈ **4:04**
- **Tempo:** **60 BPM**, dotted-quarter felt pulse.  *(60/min sits at the low edge of resting HR → downward entrainment = calm + mournful, without dropping below ~45 where pulse coherence collapses.)*
- **Meter:** **6/8 (compound triple)**.  *(Triplet subdivision is lilting/lullaby-like — the "being-cared-for" half of the paradox — and softens transient placement, killing the square martial duple feel.)*
- **Key/Mode:** **D minor**, Aeolian core → Phrygian at the peak → one Dorian glimmer.  *(D1≈36.7 Hz drone sits chest-resonant yet above the ~30 Hz mud floor; Aeolian's flat-VII refuses to resolve = modern/haunting; Phrygian ♭2 = doom-gravity; a single Dorian ♮6 = false hope.)*

**Timing constants (exact):**
```
SR      = 48000
BPM     = 60
EIGHTH  = 60 / (BPM*3) = 0.333333 s     # 6/8: 6 eighths per bar
BAR     = 6 * EIGHTH   = 2.000000 s     # bars land on round seconds
OS       = 4                            # oversample factor for nonlinearities
```

---

## 2. FORM

240 s body = **120 bars × 2.000 s**. Golden-section climax:
```
CLIMAX = 0.618034 × 240 = 148.33 s ≈ 2:28
```
*(φ placement is a compositional heuristic — not a settled empirical law; its real justification is "late enough for tension to accrue, early enough to leave an afterglow.")*

| Sec | Name | Start–End (s) | Bars | Dur (s) | Fib group | Function | Target affect |
|---|---|---|---|---|---|---|---|
| **A** | Numb / Emergence | 0–35 | 0–17.5 | 35 | 8 | drone + tonic + **incomplete** motif germ | anesthetized, floating |
| **B** | Longing / Growth | 35–92 | 17.5–46 | 57 | 13 | full motif; appoggiaturas begin; rising sequence; Dorian glimmer revoked | yearning, nostalgia |
| **C** | Descent / Pre-climax | 92–148 | 46–74 | 56 | 13 | Phrygian darkening; register climb; **one clean canonical motif statement**; deny every cadence | dread + reaching |
| **★** | **THE BREAK** | ~146–150 | ~73–75 | — | — | silence-gap (dry+wet muted) → unprepared ♭II bloom → single exposed suspension + sub | catharsis / kama muta (PEAK) |
| **D** | Collapse / Aftermath | 148–204 | 74–102 | 56 | 13 | sudden strip-away; motif returns "wounded"; no tonic | loss, aftermath |
| **E** | Afterglow (open loop) | 204–240 | 102–120 | 36 | 8 | emptier A-texture; motif eroded; **foregrounded final fragment ~232–235 s**; unresolved; dark reverb to silence | reflective, haunted |

Fib envelope up to peak **8 : 13 : 13** (35:57:56), then mirror **13 : 8** (56:36) — palindromic contour. **One peak only** (peak-end rule rewards a single unambiguous maximum).

**Fibonacci phrase groupings (within sections):** phrases nest as 2+3, 3+5, 5+8 bars (adjacent Fibonacci numbers) rather than square 4+4/8+8 — non-square phrasing avoids the "arcadey" periodicity.

---

## 3. HARMONY (all D minor)

### 3a. The spine (burn-in loop, Aeolian, no cadence)
```
i(add9)      ♭VImaj7      ♭IIImaj7/♭VII        iv(add9)
Dm(add9)     B♭maj7       Fmaj7 /C             Gm(add9)
```
- **No dominant / no leading tone → never resolves → mind keeps waiting → replay craving.**  *(Zeigarnik / unresolved expectation — Meyer/Huron ITPRA.)*
- **Common-tone A** threads i→♭VI→♭III as one sustained pedal voice.  *(Parsimonious voice-leading = smoothness = warmth — Cohn, neo-Riemannian.)*
- **Slow harmonic rhythm** (1 chord / 2–4 bars in A → suspended time), quickening through B–C.

### 3b. Voicing law (warmth-critical)
- **Wide low spacing:** bass = root octave + fifth (**D2 + A2**, beatless 2:3 drone). **Thirds live high, D4–D5 octave.** No close minor thirds below ~D3.  *(Low close thirds render muddy; integer-ratio low end stays beatless.)*
- **Withhold the 3rd (F)** in the intro's first chords → tonal ambiguity → the F's arrival is the first "yes, this is grief."

### 3c. Concrete section voicings (note spellings)

| Sec | Progression (roman → spelling / voicing) |
|---|---|
| **A** | Dm(add9) no-3rd `[D2 A2 E4 A4]` → B♭maj7♯11 `[B♭2 F3 A4 E5]` → Gm(add9) `[G2 D3 A4 B♭4]` → Dsus2→Dm `[D2 A2 E4→F4]` (bar ~8: sus2→m3 first reveals the mode) |
| **B** | spine loop `Dm(add9) [D2 A2 F4 E5]` → `B♭maj7 [B♭2 A3(pedal) D4 F4]` → `Fmaj7/C [C2 A3 E4 A4]` → `Gm(add9) [G2 A3 B♭4 A5]`; **Dorian glimmer** = a **B♮** buried inside the choir formant, immediately extinguished by **Am7♭5 (vø)** `[A2 E♭4 G4 C5]` |
| **C** | `Dm [D2 A2 F4]` → **E♭maj7 (♭II Neapolitan)** `[E♭2 B♭2 D4 G4]` → `Gm [G2 D3 B♭4]` → **B♭m (chromatic mediant)** `[B♭2 F3 D♭4 F4]` → `E♭ [E♭2 B♭2 G4]` → `Dm` (Phrygian half-cadence) |
| **★** | `Gm(add9)/iv [G2 D3 A4 B♭4]` → `B♭maj9 [B♭2 D4 F4 A4 C5]` → **E♭ (♭II, ff)** `[E♭2 B♭2 G4 B♭4]` reached via **one reserved leading-tone chord A7 `[A2 C#4 G4]`** → `Dm(add9)` with **9th (E) hanging on top, no root-position melodic tonic**; peak chord carries a **septimal 7:4** color on its dominant approach |
| **E** | `Gm(add9)` → `B♭maj7` → `Dm(add9)` → **final `Dsus2` no-3rd, held** = `[D2 A2 A3 E4]` — **minor 3rd (F) DELIBERATELY OMITTED**; melody's last note = **E (the 2nd)**, then fades |

*(Neapolitan = darkest classic borrowing; chromatic-mediant Gm→B♭m = non-functional third motion = "floor drops out"; the leading tone appears exactly once so its pull is an event, not a cliché.)*

### 3d. Tuning → JI centers + micro-drift
- **Just-intonation partial centers per chord:** m3 6:5, P5 3:2, octave 2:1, m6 8:5, and a **septimal 7:4** promoted from a one-off to a **recurring "wrong-but-right" signature** (appears in B, C, and the peak).  *(12-TET minor thirds are ~16¢ sharp and beat audibly = roughness; JI locks phase = beatless = warm.)*
- **On top:** ±3–6¢ smoothed random-walk detune per voice.  *(JI removes fast beating between notes; micro-drift adds slow within-note life — two scales, non-contradictory.)*
- **Retune glide:** interpolate JI ratios over a **10–50 ms glide** at chord changes.  *(Instantaneous per-chord retuning causes pitch clicks; ensembles glide anyway.)*
- *(432 Hz is rejected as audiophile folklore; JI is kept because it is grounded in beat-rate minimization.)*

---

## 4. MELODY

### 4a. Canonical motif **M** (D minor)
```
Notes:   D5  →   F4         →  G4    →  F4   →  E4 (held, decays)
Degree:  5?..→   ♭3         →  4     →  ♭3   →  2   (relative to D)
   (registral: D5 is high tonic; falls a MINOR 6th to F4)
Rhythm:  ♩.  →   𝅗𝅥 (dotted)  →  ♪.   →  ♪    →  𝅗𝅥. (ring, unresolved)
Motion:  —   ↓ minor 6th   ↑ M2   ↓ m2   ↓ m2
```
- **Signature interval = falling minor 6th D5→F4 (8:5).**  *(The canonical longing/loss leap; one salient leap among small steps = high recall salience.)*
- **Thwarted recovery:** lifts F→G, sinks G→F→E, **lands on scale-degree 2 (E), never tonic.**  *(Predicted return to D is denied — the prediction error is what aches and sticks — ITPRA.)*
- **Appoggiatura seed:** G4 (4th) leans on F4 (♭3) — the "tears" step-down in miniature.
- 5 notes, 4 pitch classes (D F G E), ≤1.5 s, singable.  *(Low interval-entropy + ≤4 pitch classes + short phrase = strong involuntary rehearsal. The earlier "Kolmogorov complexity" claim is dropped for this measurable proxy.)*

### 4b. Deployment + the encoding hedge (P1)
- State M ~7–9× total; in A present it **incomplete** (first 2–3 notes trailing into reverb).  *(Incomplete repetition weaponizes the Zeigarnik effect — the brain keeps trying to close the phrase = the rehearsal engine.)*
- **State M in its complete, canonical form EXACTLY ONCE — late in Section C, just before the peak — then withhold completion everywhere else.**  *(A hook must be encoded cleanly once before incompletion can create craving; pure incompletion risks never forming the template to crave.)*

### 4c. Transformations
- **Inversion** (C): falling m6 → rising (F4→D5), desperate reach that collapses = false hope.
- **Augmentation** (peak): double all durations; the falling 6th becomes a slow ceremonial descent under the full bed.
- **Fragmentation** (E): reduce to `G→F→E`, then just `E`, eroding to silence; the **final clean fragment is foregrounded ~232–235 s**, a deliberate last image (not an anonymous fade).  *(Peak-end rule: the "end" anchor should be salient.)*
- **Macro contour:** whole-piece register/dynamics trace M — rise A→C to apex, then two-step fall mirrors the sigh at the largest scale.  *(Self-similar shape at three scales compounds recognition — Gestalt good-continuation.)*

### 4d. Appoggiatura / suspension locations (exact)
- **B, bars ~20, 26, 34:** G4→F4 appoggiatura on the downbeat of each spine restatement.
- **C, bar ~60:** inverted-motif suspension — a held A4 over the E♭maj7 becomes the ♯11, resolving down to G4.
- **★ peak:** **ONE single, stark, exposed suspension** — hold **E5 over the E♭ chord** (it is the dissonant maj7-of-♭II), resolve down to **D5** on the next beat.  *(The stacked "sigh-chain" is the trailer-music cliché; a single exposed suspension reads as more devastating — restraint over pile-up. Implementation: hold one voice's frequency constant while the pad chord moves underneath, then step down.)*
- **Peak stack thinned:** at the apex, **drop the cello** — piano + choir + sub only.  *(The maximalist sad-stack flirts with kitsch; subtraction reads as emotional honesty.)*

### 4e. Secondary theme
A rising **counter-line** introduced in B, in the cello register: `A3 → C4 → D4 → E4` (scale-degrees 5-♭7-1-2), slow (one note per bar). It is the "reaching upward" foil to M's fall; at the peak it is **inverted downward** so both lines collapse together.

### 4f. The unresolved ending
Final sonority `Dsus2` = `[D2 A2 A3 E4]`, **no 3rd**; melody's last sounded pitch is **E4 (the 2nd)** which then decays into dark reverb to silence.  *(The defining emotional note — the minor 3rd — is absent; the mind supplies it and keeps supplying it, an open Zeigarnik loop.)*

---

## 5. SOUND DESIGN

Every voice: `additive_tone(a_k∝1/k², s=2.0, k_max guard, phase-random, ±3–6¢ drift)` → per-voice HP 30–40 Hz → tone LP → soft attack env (≥15 ms).

| Voice | Recipe | Role | Plane |
|---|---|---|---|
| **Sub-drone / bass (P6)** | sine `[1]` + `[2]`@−18 dB; LP ~120 Hz; **mono** | D1/D2 grounding floor | NEAR mono |
| **Sub-heartbeat kick (P1)** | 55→40 Hz sine, 12 ms pitch-drop, atk 4 ms / dec 180 ms, oversampled soft `tanh`; **NO click/noise**; **±5–15 ms pink micro-timing jitter + ±velocity variation**; drops out entirely in A/E | felt pulse ≈60/min | NEAR mono |
| **Warm pad (P2)** | additive s=2.0, 2–3 layers ±5¢, slow cutoff LFO 0.1–0.2 Hz, LP ~2.5 kHz | harmonic bed | MID |
| **Felt keys (P3)** *(renamed from "piano" — 3 partials reads as a soft mallet/Rhodes, not a grand)* | fundamental + partials via **inharmonicity `f_k = k·f0·√(1+B·k²)`, B≈0.0004**; **per-partial decay `τ_k = τ_1/k`** (highs die first); atk 6–15 ms; **felt thump = LP'd noise burst ≤300 Hz, 20 ms**; 2–3 s decay | the motif/hook | NEAR, ~15% off-center |
| **Bowed cello (P4)** | additive s=1.6, partials 1–8; atk 300–600 ms; vibrato 4.5 Hz ±8¢ (delayed onset); **bow-noise = LP'd noise @800 Hz enveloped WITH the attack transient (decays into sustain), ×0.03** | sustained emotion | MID |
| **Choir / formant pad** | additive 1–8 → 3 bandpass formants (F1 600, F2 1000, F3 2400 Hz; weights 1/0.5/0.25) → LP **3 kHz** (capped, not 3.5); subtle formant wander + pitch vibrato so it reads as "voice"; **carries the peak and hides the Dorian ♮6** | wordless voice, empathy/attachment | MID/FAR |
| **Glass bell (P5)** | 2–3 inharmonic sine partials, long decay, heavy reverb, LP **3 kHz** (capped down from 6 during peak); lives FAR so HF diffuses | rare high "star" points | FAR |
| **Soft mallet / low tom / brush (P7)** | mallet: 400 Hz sine burst 40 ms; tom: 90 Hz sine pitch-drop 250 ms; brush: **LP'd noise @800 Hz** swelled | organic percussion, **peak only** | MID |
| **Reverse-swell (P7b)** | any pad note, `env[::-1]` | non-harsh riser into peak | FAR |

---

## 6. PERCUSSION (non-harsh approach)

- Rhythm from **felt low-frequency pulses + soft mallets + LP-noise swells only**; **zero 2–8 kHz spit ever.**  *(Bright transients are the arcade/harsh tell.)*
- **No drums until the D-approach (~2:00).** Before that, the only pulse is the quiet sub-heartbeat kick.  *(Withholding percussion keeps A/B in suspended, low-arousal time.)*
- Sub-heartbeat kick gets **pink micro-timing jitter + velocity variation** so it is never a machine grid.  *(An exactly-isochronous 60/min pulse is the last "arcadey" element; 1/f jitter humanizes it.)*

---

## 7. SPACE (3-plane stage + warm dark reverb)

Depth via (a) reverb wet, (b) pre-delay, (c) HF rolloff, (d) level:
- **NEAR** (piano/kick/bass): wet 0.10–0.15, pre-delay 30–40 ms, mono/narrow, full HF.  *(Longer pre-delay + precedence keeps them articulate and "in front" — Haas.)*
- **MID** (pads/cello): wet 0.30, pre-delay 20–30 ms.
- **FAR** (bells/swells/tails): wet 0.55, pre-delay 8–15 ms, LP ~1.8 kHz, wide.

**Reverb = Schroeder/Freeverb (all numpy):** 4–8 parallel feedback combs (fb 0.7–0.84, **mutually-prime delay lengths** to kill flutter) → 2 series allpass (g≈0.5) → **one-pole LP inside each comb feedback path (damp 0.3–0.5)** so the tail darkens as it decays. RT60 ~3–4 s. L/R comb delays offset ±30 samples for a decorrelated wide tail. **Bass+kick mono <150 Hz.**  *(Damped comb feedback = warm not metallic; mutually-prime lengths remove periodic flutter ring.)*

**Delay:** stereo ping-pong at **dotted-eighth vs the 6/8**, feedback ~0.4, **LP each feedback tap @3 kHz** so echoes darken as they fade.  *(The hook "rings in the mind" while staying dark.)*

**Slow modulation:** ~0.1–0.2 Hz LFO on pad amplitude + cutoff.  *(A slow modulation rate lowers perceived arousal — framed as arousal reduction, not literal "respiratory entrainment," which is only hypothesized.)*

---

## 8. THE PEAK (Section ★, ~2:26 → 2:28 → release)

Converge every dimension at one instant (peak-end rule):
1. **Registral ascent** to the highest note of the piece (~octave above M's home).  *(Height = arousal.)*
2. **Textural accumulation** one voice per bar in the final approach; **but the cello is dropped from the apex** (thinned stack).
3. **Controlled swell:** raise pad level + reverb send + slowly open LP — **capped at ~3 kHz, never past the dip.** Crescendo via **density and dynamics, not treble.** Peak ~−8 dBFS, ~12–16 dB above intro.  *(Loudness without brightness is the whole warmth trick at max energy.)*
4. **A silence/held breath (0.3–0.6 s) before the downbeat — and this gap MUST mute the reverb RETURN too** (duck the wet bus, or use a dry pre-gap), or the Section-C tail bleeds through and the "held breath" does not exist.  *(A gap sharpens prediction error — Huron; the reverb-mute is the concrete implementation trap.)*
5. **The hit:** downbeat on the **unprepared ♭II (E♭, Neapolitan) / brief major bloom**, reached via the one reserved leading-tone chord (A7); the **single exposed suspension** (E5→D5) fires here; **low root/sub enters (D1)** = the chest-felt somatic component.  *(kama muta — chills/tears/chest-warmth after struggle — Fiske et al.)*
6. **Release:** do **NOT** resolve to root-position tonic. **Cut density suddenly** (½-bar near-silence) and let the big chord *decay* rather than cadence.  *(Huge arrival → immediate stripping-away = loss/aftermath.)*

---

## 9. MIX / MASTER (exact DSP order)

Per voice → bus → master. **Every nonlinearity is oversampled `OS=4×` (upsample → nonlinearity → LP → downsample) with a mandatory LP after it** — this is the single most important fix; without it the "warmth" chain manufactures aliased harshness.

```
PER VOICE:
  additive_tone(a_k∝1/k², k_max guard, phase-rand, ±3–6¢ drift, JI retune-glide)
  → HP 30–40 Hz (butter sos)
  → tone LP 2.5–5 kHz (+ slow filter env)
  → amp env: attack 1−e^(−t/τ) ≥15 ms (pads 0.8–1.5 s), release e^(−t/τ) 2–4 s
  → [formant bandpasses if choir]

BUS:
  sum voices
  (NO bus saturator — the double-tanh is removed; only ONE saturation stage exists, in master)
  → reverb (predelay + damped-comb + allpass; wet LP ~5 kHz)
  → ping-pong delay (feedback LP @3 kHz)

MASTER (sosfilt single-pass for shelves — NOT sosfiltfilt, which doubles dB & order):
  1.  HP 25 Hz (butter, order 2)
  2.  3 kHz dip: −2 dB, Q≈2–3           # reconciled with step 3
  3.  hi-shelf −3 dB above ~3.5–4 kHz    # pink-ish tilt
      # summed magnitude at 3.2 kHz verified ≤ −4 dB (no over-scoop / muffle)
  4.  LP ~15.5 kHz (butter order 4)      # remove brittle air
  5.  low-shelf +1.5 dB @ ~120 Hz        # body / tape head-bump
  6.  warm_sat — ASYMMETRIC, OVERSAMPLED 4×:
          y = tanh(a*(x+b)) - tanh(a*b),  a≈1.2, b≈0.15
          (bias term yields genuine 2nd-harmonic content, not pure odd)
          up×4 → curve → LP 8 kHz → down×4
  7.  gentle comp ~2:1, GR 2–3 dB, atk ~30 ms, rel ~250 ms   # glue, no pump
  8.  tape wow (0.6 Hz ±0.15%) + flutter (6 Hz ±0.03%)
          via CUBIC (Catmull-Rom) fractional-delay resample on a modulated read index
          (its inherent HF loss is intentional / on-brand)
  9.  pink noise floor:
          A/B/E exposed passages → LP ≤6 kHz AND ducked with program level
          so it never becomes the loudest/brightest exposed element
          (~−60 dBFS under the bed)
  10. soft limiter → −1.0 dBFS peak, target ~−15 LUFS  # never slam to 0
```
- Spectral centroid target: **300–800 Hz**; guard 3–4 kHz at all times.
- *(Corrected from critique: `tanh` alone gives ODD harmonics — the biased curve above yields real even/2nd-harmonic warmth; oversampling + post-LP kills the aliasing hole; a single saturator avoids cascaded-clipper IMD; single-pass shelves avoid doubled attenuation; reconciled dip+shelf avoids a "blanket over the speakers" dull failure.)*
- **Loudness note:** with peak −8 dBFS and 12–16 dB range, the intro sits ~−20 to −24 dBFS; at −15 LUFS integrated this is correct for an art piece but will feel quiet on phone speakers (by design, not competitive-loud).

---

## 10. DYNAMICS / AUTOMATION

- **Loudness arc:** A ≈ −22 LUFS-short-term → rising through B/C → **peak ~−8 dBFS at 148 s** → sudden −10 dB drop into D → slow decay through E to silence. Single unambiguous maximum (peak-end).
- **Brightness arc:** LP cutoff opens **2.5 kHz (A) → cap 3 kHz (peak)**, never further; crescendo carried by density, not treble.  *(Warmth preserved at maximum energy.)*
- **Reverb/space automation:** wet send rises A→peak (space "opens" as it swells), the pre-peak gap **mutes the wet return**, then D→E the wet grows again and RT60 lengthens as instruments thin, so the final fragment dissolves into the longest, darkest tail.

---

## 11. 1/f (PINK-NOISE) FLUCTUATION

- **Micro-timing:** each note onset offset by a **pink-noise sequence** (generate via Voss–McCartney or `1/√f`-filtered white noise), scaled to **±5–15 ms**; applied to melody, kick, and mallet onsets.  *(1/f timing variation matches the fluctuation statistics of human musical performance — makes it read as organic, not metronomic.)*
- **Micro-dynamics:** per-note velocity/amplitude scaled by an independent pink-noise sequence, ±1.5 dB.
- **Detune drift:** the ±3–6¢ per-voice drift is itself a **low-passed (pink-tilted) random walk**, not white jitter, so pitch wanders slowly and naturally.
- *(All three are cheap in numpy: `pink = irfft(rfft(white) / sqrt(f))`; use one seed per stream.)*

---

## 12. WHY THIS HITS ALL FOUR GOALS

- **Dark & melancholic:** 60 BPM sub-heartbeat; D Aeolian→Phrygian; JI 6:5 thirds + recurring septimal 7:4; falling-m6 sigh ending on the hanging 2nd; D1 drone.
- **Addictive / burned-in:** one WM-sized motif recursed at three scales + mirror-Fibonacci form; **one clean canonical statement to seed the template**, incompletion everywhere else to drive craving; one engineered peak + foregrounded final fragment (peak-end).
- **Leaves them thinking:** φ climax at ~148 s → ~90 s afterglow; every cadence denied (ITPRA); final chord omits the 3rd and melody ends on the 2nd → open Zeigarnik loop.
- **Warm / easy on the ears (old harshness fixed):** 1/k² band-limited additive (zero aliasing); reconciled 3 kHz dip + pink tilt; damped dark reverb; JI beatless intervals; **single oversampled asymmetric saturator** (real even harmonics, no aliasing, no cascaded IMD); centroid held 300–800 Hz. **Organic not arcadey:** 1/f micro-timing/dynamics/detune, non-square Fibonacci phrasing, compound triplet feel, humanized kick, mutually-prime reverb delays.

**One-line render summary:**
`D-min Aeolian→Phrygian, 60 BPM 6/8, 120×2s bars = 240s + tail. Motif D–F–G–F–E (falling m6, ends on 2), stated clean ONCE pre-peak, else incomplete. Spine i(add9)–♭VImaj7–♭III/♭VII–iv, no cadence, JI+septimal-7:4 signature, retune-glide. A(0–35 numb) → B(35–92 longing, appoggiaturas, choir-hidden Dorian glimmer revoked) → C(92–148 Phrygian/Neapolitan, clean motif, deny cadences) → ★peak ~148s (silence-gap with WET MUTED → unprepared ♭II bloom via reserved A7 + single exposed E5→D5 suspension + D1 sub, cello dropped, NO tonic) → D(148–204 collapse) → E(204–240 eroded motif, foregrounded fragment ~232s, end on Dsus2 no-3rd, melody on E, dark reverb to silence). All voices additive 1/k² band-limited, JI+pink micro-drift, damped dark comb-reverb; master: single-pass shelves, reconciled 3 kHz dip+tilt, ONE oversampled asymmetric tanh, cubic wow/flutter, ducked pink floor, −1 dBFS / −15 LUFS. All nonlinearities oversampled 4×; 1/f jitter on timing/dynamics/detune.`