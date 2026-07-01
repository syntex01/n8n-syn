The spec is already fully realized in the prompt. My task is to produce the FINAL, concrete, implementable BUILD SPEC. I'll write it directly as structured markdown, grounding every decision in the vetted palette. No repo work is needed.

# THE THING THAT ALMOST BREATHES
### FINAL BUILD SPEC — numpy/scipy synthesis, sr = 48000, stereo, ~230 s

---

## 0. GLOBALS

| Field | Value | Justification (one line) |
|---|---|---|
| **Title** | *The Thing That Almost Breathes* | Names the core percept: near-life that never resolves — the uncanny hook. |
| **Duration** | 230 s (+ ~6 s decay tail) | Long enough for habituation to set in and be defeated by 1/f novelty. |
| **Pulse** | Free-time, no meter | Metric grids are the arcade tell; unpredictable onsets keep orienting attention alive. |
| **Global rate hierarchy** | breath 0.15–0.25 Hz / section 20–55 s / macro-arc 230 s | Nested 1/f self-similarity reads as "one organism at three zooms," not sequenced. |
| **Tuning** | Spectral/just, locked to REVENANT BELL prime = 130.0 Hz | Inharmonic timbres make 12-TET add undesigned beating; tune to the spectrum (Sethares). |
| **Roots/partials** | hum 65, prime 130, tierce 156 (×1.2), quint 195, nominal 260, deciem 325 Hz | Bell's own partials become the pitch lattice; consonance becomes a dial, not an accident. |
| **"Key/mode"** | Bell-spectral minor (tierce 1.2 = minor third) | The only culturally-loaded color; everything else is spectral. |
| **Peak time** | 0.618 × 230 ≈ **142 s** | Golden-section climax = maximally satisfying yet non-countable placement. |
| **Section lengths (s)** | 34 – 21 – 34 – 21 – 55 – 34 – 21 (+tail) | Fibonacci-ish; adjacent ratios ≈ φ → proportional relation without equality/repetition. |
| **Master sr / internal** | 48 kHz out; nonlinearities at 4–8× oversample | Anti-alias guarantee for every tanh/Chebyshev/feedback stage. |
| **Target spectral centroid** | **≈ 950–1150 Hz** (whole-mix, time-avg), climax peak ≤ 1600 Hz | Dark, un-piercing; keeps energy out of the 2–5 kHz fatigue valley. |

**One universal rule (the deepest anti-arcade decision):** every modulation source — density, detune, formant centers, bow pressure, pan, gain — is a **1/f random-walk** (`cumsum` of low-passed white noise), never a periodic sine LFO. Periodic modulation is the #1 "toy" tell; 1/f drift is the #1 "alive" cue.

---

## 1. THE RECURRING GESTURE — "THE SINKING VOWEL"

A pitched thing descends ~a minor third while the audible material barely moves.

- **Realization:** GROUNDWATER residue f0 sweeps 30 → 24 Hz (Schouten phantom bass, minor third ≈ 316 cents = ratio 24/30·... ~ tuned to land near hum·(4/5)) while upper partials hold absolute frequency; coupled to one VOX GLOTTIS / THROATLESS formant sinking toward ~200 Hz.
- **Math of the descent:** `f0(t) = 30·(24/30)^(t/T)` (log-linear glide).
- **Why:** a perceptual paradox (descent without descent) can't be fully modelled, so repetition-suppression never completes → each recurrence re-triggers orienting attention. Memorable (one nameable illusion), strange (physically impossible), never cheesy (timbre + phantom pitch, not notes).
- **Appearances:** §1 GROUNDWATER sub · §3 VOX GLOTTIS vowel · §5 CHORUS OF THE MANY (mass sinking). Same gesture, three timbral costumes.

---

## 2. INSTRUMENT PALETTE — FINALIZED SYNTHESIS RECIPES

All recipes are the **corrected/vetted** versions. Shared safety net at the end of this section.

### 2.1 GROUNDWATER — residue-pitch ghost drone
- **Signal flow:** `partials Σ aₙ·sin(phase_n) → oversampled_tanh(drive 0.35) → spectral tilt (1-pole shelf, fc 250 Hz, −4 dB/oct) → Butterworth HP 26 Hz → amp env`.
- **Partials:** n·f0 for n ∈ {3,4,5,6}; f0 swept 30→24 Hz; **29/f0 never synthesized** (ear supplies residue). `aₙ = n^−1.3 · (1 + rw(0.05 Hz, ±0.12))`.
- **Phase:** `phase_n = 2π·cumsum(n·f0[n])/sr` (time-varying → must integrate, not f·t) + per-partial random-walk phase drift.
- **Params:** drive 0.35 (was 0.7 — kills "buzzy organ"); tanh 2× oversampled.
- **Evolution:** log-glide of f0; decorrelated amp/phase drift → nothing static.
- **Psych:** residue pitch (Schouten) is the load-bearing mechanism; cubic-difference tone (2f1−f2) reinforces; Tartini quadratic tone is a level-dependent bonus only.
- **Guard:** all sines; tanh oversampled + tilted; HP 26 Hz; top partial 174 Hz → no aliasing.

### 2.2 MANTLE — subharmonic breather (the breathing floor)
- **Flow:** `subbank + beat-pair + body → soft(0.5) → HP 24 Hz → LP 400 Hz → breath env`.
- **Subs (direct synthesis, no division tricks):** fc=110 Hz → sin(fc/k) for k∈{2,3,4} = 55, 36.7, 27.5 Hz; equal-power crossfade k=2→k=4 over the section.
- **Body (inharmonic, sub-400):** 110,165,220,247,290,355 Hz with steep rolloff (survives LP, avoids "telephone" thinness).
- **Beat pair:** 27.5 + 28.4 Hz → 0.9 Hz throb.
- **Breath env:** asymmetric `0.5+0.5·((1−cos(∫f_br))/2)^1.5`, f_br 0.25→0.15 Hz ("tires").
- **Psych:** frequency code (low=large=threat); ~0.2 Hz asymmetric AM → agent detection; asymmetry defeats habituation. 27.5 Hz is audible+felt, not infrasonic.
- **Guard:** direct-synth subs (no alias); tanh drive 0.5; LP 400 Hz.

### 2.3 SPLIT-HORIZON — beating-tension drone
- **Flow:** per pair `sin(f) + sin(f+δ(t))` at f ∈ {65, 97.5, 130 Hz} → `soft(0.4) → HP 26 → LP 600 → 6 s raised-cos swell`.
- **δ cap (corrected):** per-pair `δ_max = 0.25·ERB(f)` ≈ 8–10 Hz (NOT 18); `δ(t)=0.6·(δ_max/0.6)^tri(t)`, triangle 0→1→0 over 50 s. Overshooting ERB → mechanical flutter (arcade fail).
- **Free sub:** 65 & 97.5 (2:3) throw a 32.5 Hz difference tone.
- **Psych:** walks up/down the Plomp–Levelt dissonance curve — controlled anxiety oscillation with exact target.
- **Guard:** pure sines ≤130+δ; per-partial amp drift so nothing is a "test tone"; LP 600.

### 2.4 REVENANT BELL — cracked-bell strike
- **Flow (additive, method A):** `Σ aₖ·exp(−t/τₖ)·sin(2π fₖ t + φ0) + rattle → tilt → HP`.
- **Modes:** ratios ×prime {0.5,1.0,1.2,1.5,2.0,2.5}, each `×(1±0.015)` crack detune. `aₖ`: hum/prime loud, tierce −4 dB, uppers −8…−14 dB. `τₖ=Qₖ/(π fₖ)`, hum Q≈3000, uppers Q≈300.
- **Strike:** 2–3 ms raised-cosine (not Dirac → no broadband splatter). Double strike 40–120 ms apart, different detune seeds.
- **Rattle:** high partial ~6.3×prime, amp `×(1+0.6·|BP-noise|)`, retriggering short exp decays whose **grain envelope hits zero at every retrigger**; bandpassed below fatigue band.
- **Psych:** tierce minor-third (culturally funereal); sub-3% detune = "wrong bell," not atonal; predictive-coding violation on a schematized object.
- **Guard:** all sines; raised-cosine onset; SOS if any high-Q resonator form used.

### 2.5 COLD BELL LARYNX — the bell that inhales
- **Flow:** 2-op FM (mod ratio 1.4, β 1.2→0.2 over 2.5 s) → Chebyshev odd bank {1,0.5,0.25,0.12} → **complementary-envelope crossfade** → tilt.
- **Reverse-swell (corrected — not literal reversal):** bright path gain `e^{−t/τ}`, breath path gain `(1−e^{−t/τ})`, τ=2.2 s; envelopes sum to 1 → constant loudness, spectrum migrates bright→breathy. Breath path emphasizes ≥1-octave **unpitched** noise band 80–200 Hz.
- **Pitch:** ±15-cent OU drift.
- **Psych:** hard prior that struck things decay; anti-decay swell reads as impossible/supernatural.
- **Guard:** β decays fast; Chebyshev input clamped `|g·x|≤0.98`; 8× oversample on shaper; noise bandpassed.

### 2.6 VOX GLOTTIS — the almost-speaking dead
- **Flow (source–filter):** Rosenberg glottal pulse (f0 80–160 Hz) → jitter/shimmer → 5 parallel Klatt formant biquads → lip-radiation diff `y=x−0.97x[n-1]` + fixed 7 kHz shelf → per-block crossfaded coeffs.
- **Formant biquad:** `r=exp(−π·BW/fs)`, `θ=2π F/fs`, `a1=−2r cosθ`, `a2=r²`, `b0=1−a1−a2` (DC-unity). BW≈50+0.1·F.
- **Jitter/shimmer:** J≈0.015 (period), S≈0.05 (amp), both 12 Hz LP-noise driven (above-healthy → strained/unwell inference).
- **Vowel morph:** random walk through /u/,/o/,/a/,/e/,/ə/ over 4–12 s, log-Hz interp, never landing (edge of intelligibility).
- **Guard:** Rosenberg generated at **4× oversample + anti-alias LP 0.45·fs_os + resample_poly** (closure-instant slope discontinuity aliases otherwise); coeffs crossfaded, not hot-swapped.

### 2.7 THROATLESS — voice with no body (cross-synthesis, connective tissue)
- **Flow:** modulator = resonant BP sweeps on noise (formant envelope via **LPC order 14**); carrier = any source (noise / CRIBRA ticks / MURMELWURM grains); `gain=|M_env|/max(|C_env|,0.08·max|C_env|)`, clamp `≤8`, 1-pole smooth α=0.7 across frames; `Y=C·gain`; ISTFT (N=2048, hop=512, Hann, COLA).
- **Role:** imposes vowel formants onto *other instruments* → one instrument audibly becomes another across a boundary (cross-synthesis as narrative).
- **Psych:** source–filter violation (vocal-tract filter, no glottal source) fires the speech detector while breaking the production model; pareidolia. Stay at edge of intelligibility.
- **Guard:** relative-floor division (kills musical-noise sparkle); gain clamp + smoothing; carrier pre-LP 7 kHz; −3 dB/oct output tilt.

### 2.8 PSITHURA — breathing whisper-cloud
- **Flow:** grains windowed **out of a pre-filtered continuous pink bed** (perf + coherence) → 2–3 formant BPs (F1 500–900, F2 1300–1900, F3 2400–3000, Q 4–9) → Gaussian window (τ 40–120 ms, σ=τ/6) → OLA.
- **Breath:** density λ(t)=λ_max·breath(t), λ_max≈30/s; **convex-rising / asymmetric** swells on some breaths (real auditory looming, not symmetric cosine). Poisson onsets `dt=−ln(U)/λ`.
- **Air band:** narrow wandering BP 5–7 kHz Q≈2, **exhale-gated**, ≤ −18 dBFS (continuous HF hiss is the fatiguing case).
- **Space:** **dry** (high direct/reverb ratio = proximity).
- **Psych:** looming bias + near-field/peripersonal intrusion (<1 m = threat).
- **Guard:** filtered noise + Gaussian windows (no clicks); every sinusoidal grain gets `φ0~U(0,2π)`.

### 2.9 PLEURA — near-field breath membrane
- **Flow:** pink bed → time-varying throat BP (center random-walk 300–1200 Hz, **per-block coeff update + crossfade**) + exhale-gated air shelf (capped) → Hann grains (τ 60–150 ms) → asymmetric breath env (rise ~0.25 s, fall ~0.9 s) → faint 40–70 Hz sub tied to exhale (RMS ≤ −18 dB).
- **Caught breath:** occasional sudden envelope truncation → alarm spike; the **final event of the piece**.
- **Psych:** breathing biological-motion prior → life detection; 40–70 Hz = low-frequency chest/proximity cue (not infrasonic).
- **Guard:** filtered noise + Hann; per-block filter crossfade (no zipper clicks); master HP 28 Hz.

### 2.10 CRIBRA — sparse ticks in the dark
- **Flow (corrected):** grain = **damped inharmonic modal ping** `Σ_{k=1..3} aₖ·e^{−t/Tₖ}·sin(2π f rₖ t + φ0)`, ratios ~{1,2.7,5.1}, T60 5–15 ms, RC window rise > 2 ms (delivers wood/insect, kills the sine "beep").
- **Schedule:** sparse Poisson λ 0.1–0.6/s (one tick every 2–10 s); amplitude log-uniform (rare loud one); per-grain pan `U(−1,1)`; distance via per-grain LP + one 7–30 ms early reflection.
- **Evolution:** λ slowly rises over minutes; occasional 2–4-tick micro-cluster (<200 ms) = movement.
- **Psych:** involuntary orienting / novelty capture (rare, spatially unpredictable, non-repeating → resists habituation, re-triggers threat appraisal); silence-contrast amplifies salience.
- **Guard:** finite partials; rise >2 ms (no click); f ≤ 4 kHz.

### 2.11 MURMELWURM / MURMURATION — swarm grain-cloud
- **Flow:** pitched sine grains (3 partials f,2.01f,3.02f), Hann τ 20–60 ms, **random φ0 per grain** (critical — kills comb/pulse buzz & validates √N level math). Density λ 100–400/s driven by **1/f pink control**. Optionally pass grain bus through 2–3 formant BPs (~500/1500/2500 Hz) → reads vocal (MURMELWURM whisper-choir).
- **Pitch:** scale degree + **slow 1/f per-voice walk ±30–40 cents** on top of ±15-cent fusion jitter (total spread <50 cents so it still fuses). Voices capped 8–12.
- **Chaos option (MURMELWURM):** logistic map r 3.7→3.99 drives detune variance; period-3 window at r≈3.828 = eerie near-order.
- **Level:** `1/√(λτ)` normalization (incoherent √N sum).
- **Psych:** auditory fusion into a super-object; one↔many streaming ambiguity (fragmentation = scariest instant). "Swarm agency" = aesthetic intent, not cited effect.
- **Guard:** pure sines + Hann; pink-noise DC bin guarded; global LP ~6 kHz.

### 2.12 CHORUS OF THE MANY — detuned ghost-choir
- **Flow:** N=8 independent VOX GLOTTIS voices; f0ᵢ=f0·2^(cᵢ/1200), cᵢ~N(0,σ), **independent jitter seeds** per voice; shared vowel target with 0–400 ms random per-voice lag (ragged arrival); dark convolution reverb (synth IR, T60 3–5 s, LP 4 kHz).
- **σ breathes 4→18→4 cents:** choir coalesces into one unison then **fragments into many** (the unsettling moment). Beat between voices ≈ f0·(2^(Δc/1200)−1) ≈ sub-Hz to few Hz (below roughness).
- **Psych:** numerosity/entitativity; ASA fusion↔segregation flip; funereal choir schema.
- **Guard:** 1/√N gain + soft limiter; smooth glottal sources; dark IR prevents massed-HF harshness.

### 2.13 REBEC WRAITH — bowed-metal snarl (climax color)
- **Flow:** feedback-FM core (β 0.35) + inharmonic op `0.30·sin(2π·1.51f t)` (color only) **+ `0.22·sin(2π·2.05f t)`** (beats 2f at ≈8 Hz → true Plomp–Levelt roughness) → Chebyshev Gaussian bank (k0 4→6) → 2 formant BPs [220,1800] → tilt → decimate.
- **Growl burst (corrected):** jitter interval (3.5–5 s) **and depth** (β_peak 1.0–1.2, g_peak 0.8–0.9); during burst **lower tilt corner 1.2 kHz→0.9 kHz** so it darkens/roughens (a real animal growl darkens, not brightens); randomize burst envelope shape.
- **Psych:** roughness at its exact peak; frequency code; nonlinear distress-vocalization salience.
- **Guard:** β≤1.3; Chebyshev input clamped ≤0.98; 8× oversample; bursts transient (≤0.6 s) so no sustained fatigue.

### 2.14 THE ENDLESS STAIRWELL — Shepard/Risset descent
- **Flow:** K=7 octave-spaced sines, computed at **sample rate**; `f_i[n]=f0·2^(((n/(sr·T_oct))+i·K_span/K) mod K_span)`, K_span=8, **T_oct 15–25 s (glacial)**; Gaussian log-freq window `f_c≈375 Hz, σ≈1.3 oct`, force `a_i=0` for f>0.45·sr. Phase `2π·cumsum(f_i)/sr`. ±0.3% inharmonic detune + slow tremolo. **−6 dB/oct tilt, low level.**
- **Second-order illusion:** drift f_c up while tones fall.
- **Psych:** Shepard–Risset paradox → eternal-motion / denied-resolution tension (requires no resolving event around it — satisfied by §4 context).
- **Guard:** pure sines capped <0.45·fs with inaudible amp at Nyquist; glacial+dark = dread not SFX.

### 2.15 THE MISSING ROOM — resonant void with holes
- **Flow:** noise (HP 60/LP 6 kHz) → **lossy feedback comb** `y[n]=x[n]+g·LP1(y[n−D])`, D=round(sr/f_pitch), **g≤0.93** sustained (0.97 brief climax only), slew g ≤0.02/s → output LP ~5 kHz. STFT notches: 2–3 Gaussian dips w 30–80 Hz that **sweep 200–3000 Hz and snap open/closed** (motion makes absence audible; static notches are inaudible). Freeze: hold |Y0| N frames, independent φ~U(0,2π) per bin/frame.
- **Psych:** moving spectral absence reads as something-removed; freeze = loss of temporal coherence → "time stopped."
- **Guard:** linear IIR (no alias); |g|<1 stable; intra-loop LP kills metallic whistle; subtractive notches can't add harsh content.

### 2.16 TESSELLA — time-smeared shards
- **Flow:** synth inharmonic bell source (partials 1,2.76,5.40,8.93; f₁≤700 Hz) → STFT → freeze magnitude slice + **randomize phase per bin** → iSTFT short Tukey segment (τ 150–600 ms), p=0.3 time-reversed, resample_poly to r∈{0.5,0.667,1,1.5} → **post-LP 10 kHz**. τ/pitch driven by 1/f melt (progressively longer/lower).
- **Psych:** phase-randomization removes onsets → temporal disorientation; reversed envelope violates decay prior.
- **Guard:** finite partials; resample_poly only; post-LP 10 kHz.

### 2.17 TIEFENZUG — self-modulating sub-creature
- **Flow:** self-mod feedback FM, **f0≈90 Hz** (so period-doubled f0/2≈45 Hz is audible for scream-cue), β env 0.6→0.9π; **feedback-path pole g≈0.6–0.7**; run osc at **4× (8× when β>2), decimate ftype='fir'**; asymmetric shaper `tanh(a·y+0.2·y²)`; SOS LP ~300 Hz + shelf. Two instances ~1.005× detuned, **decorrelated/panned** (avoid 0.86 Hz cancellation holes); swell period **~4–5 s** (genuine breath).
- **Psych:** low-frequency dread; breath-rate entrainment; subharmonic = distress/scream salience.
- **Guard:** oversampling is the real anti-alias guard (not the 1-pole); serial inner loop.

### Shared safety net (baked into every engine)
- Every partial is an explicit `sin` or a filtered/SOS resonator (high-Q → **SOS, never `[b,a]`**).
- All nonlinearities (tanh, Chebyshev, feedback-FM, period-doubling) **oversampled 4–8× → anti-alias LP → decimate (`resample_poly`/`decimate ftype='fir'`)**.
- All grain windows Gaussian/Hann/Tukey/raised-cosine, zero-ended (no clicks); rise >2 ms for ticks.
- **All modulation = 1/f random-walk, never periodic sine.**
- Time-varying pitch/filters: integrate phase (`cumsum`), crossfade filter states per block (no hot-swap).
- Master spectral tilt −4…−6 dB/oct; narrow **dynamic** notch (Q≈2) around 3–4 kHz only if metering shows buildup (do NOT gouge 2–5 kHz).

---

## 3. FORM — sections, times, content, tension

| § | Start–End (s) | Affect | Lead instruments | Psych lever |
|---|---|---|---|---|
| 1 | 0–34 | Absence / under-the-floor | GROUNDWATER (motif #1), THE MISSING ROOM (moving notches) | Missing fundamental; silence-as-contrast; dread by withholding. |
| 2 | 34–55 | First presence | CRIBRA (sparse modal pings), GROUNDWATER bed | Involuntary orienting / novelty capture; silence makes one tick land. |
| 3 | 55–89 | Almost-speech (motif #1→#2) | VOX GLOTTIS / THROATLESS (formant morph), PSITHURA (dry, looming) | Source–filter violation; looming bias; peripersonal intrusion. |
| 4 | 89–110 | Withdrawal (trough) | THE ENDLESS STAIRWELL (glacial, dark), MANTLE floor | Dynamic contrast sets up climax; Shepard plants denied-resolution tension. |
| 5 | 110–165 | **Climax** (φ-peak ≈142) | CHORUS OF THE MANY (motif #3, σ 4→18¢), REBEC WRAITH growls, SPLIT-HORIZON into roughness, TIEFENZUG inhaling | Numerosity flip; roughness peak; frequency code; distress subharmonics. |
| 6 | 165–199 | Impossible bell / release-that-isn't | REVENANT BELL + COLD BELL LARYNX (reverse-swell), TESSELLA (backward shards) | Expectation violation on schematized object; anti-decay = supernatural. |
| 7 | 199–230+ | Receding into silence | GROUNDWATER (last descent), MANTLE breath tiring, THE MISSING ROOM frozen, PLEURA caught-breath | Habituation used deliberately; removed low-end = floor drops out; silence as final instrument. |

**Tension arc:** slow rise §1→§3, deliberate trough §4, golden-section peak at 142 s inside §5, non-resolving collapse §6, long exhale §7. **Recurring gesture** (Sinking Vowel) at §1 / §3 / §5, each in a new timbral costume.

---

## 4. ARRANGEMENT / DIVERSITY

- **Excitation rotation (strongest identity cue):** no-onset drone (§1) → impulsive ticks (§2) → breath/continuous voice (§3) → continuous glissando (§4) → friction+strike swarm (§5) → struck-then-reversed (§6) → breath fading (§7). Every neighbor is a different physical action.
- **Register rotation:** sub → high sparse → mid vocal → mid dark → full-spectrum → mid bell+sub → sub then gone.
- **Q/material rotation:** glass very-high-Q vs bone low-Q vs bell mixed → same gesture reads as different substances.
- **Morphing, not cutting:** THROATLESS imposes VOX GLOTTIS formants onto CRIBRA ticks or MURMELWURM grains → one instrument becomes another across a boundary. CHORUS σ 4→18→4¢ tells "unity dissolving into many" in timbre alone.
- **Novelty budget:** each section introduces exactly one new timbre and retires one → continuous novelty, working-memory-friendly. The **only** thing allowed to repeat is the motif (in a new costume each time).

---

## 5. LOW-END & SPACE

- **Sub is structural:** GROUNDWATER residue 24–30 Hz + TIEFENZUG 45–90 Hz at chest/room-resonance frequencies (low = large = threat; felt before heard). **Master HP 28 Hz** protects speakers and stays responsibly above true infrasound — unease from *low-and-felt*, not an infrasound myth.
- **Space = distance instrument:** intimate voices (PSITHURA, PLEURA) **dry / near-field** (in-your-space); bells and choir in **dark synth reverb** (T60 3–5 s, LP to ~4 kHz so massed highs never accumulate) = far/cavernous. Contrast between dry-close and wet-far is a spatial narrative: threat moves from across-the-room (§6) to against-your-neck (§3, §7).
- **Silence:** §1/§2 mostly negative space; §4 a deliberate withdrawal. Contrast makes §5 overwhelming and §7's cutoff a physical drop. **Last sound = a caught breath (truncation)** — the piece ends on an absence the body braces for.

---

## 6. MASTER CHAIN (exact order, frequencies)

Sum all voices (each RMS-normalized, √N-managed) → then:

1. **DC block / HP** — Butterworth SOS, 4th order, **28 Hz** (kills sub-infrasound + DC).
2. **Spectral tilt** — 1-pole high shelf, corner **~1.2 kHz**, slope **−4 to −6 dB/oct** above it (highs sit back; sets dark centroid).
3. **Dynamic de-harsh notch** — parametric peaking EQ, **center 3.4 kHz, Q≈2**, gain reduction *only when* 3–4 kHz band energy exceeds threshold (envelope-follower driven). Narrow + dynamic — never a static 2–5 kHz gouge (that band carries tierce/rattle articulation).
4. **Depth saturation** — `tanh(1.1·x)/1.1` at **4× oversample → LP 0.45·fs_os → decimate**; adds glue/warmth, no hard corner, no alias.
5. **Reverb (parallel send, far bus only)** — synthesized IR = decorrelated exp-decayed filtered noise, **T60 3–5 s, IR LP 4 kHz**, `fftconvolve`; dry voices bypass. Wet/dry per-section automated (near in §3/§7, far in §6).
6. **Soft ceiling / limiter** — `tanh(0.9·x)/0.9`, then peak-normalize to **−3 dBFS**.

**Target spectral centroid:** whole-mix time-average **950–1150 Hz**; instantaneous peak at climax **≤ 1600 Hz**. Verify by metering; if 2–5 kHz accumulates, step 3 engages before step 2 is touched.

**Order rationale:** HP first (remove rumble before any nonlinearity manufactures IMD from it) → tilt to shape spectrum → dynamic notch to catch fatigue → saturation for depth (post-tilt so it warms the shaped signal) → reverb for space → limiter last (catch peaks after everything).

---

## 7. DYNAMICS — loudness/brightness automation over time

All curves are **1/f-drifted** around these targets (no straight lines, no periodic wobble):

| Time (s) | RMS loudness (rel dBFS) | Brightness (tilt corner / centroid) | Note |
|---|---|---|---|
| 0–34 | −26 → −22 | dark (corner 900 Hz, centroid ~800) | absence bed rises slowly |
| 34–55 | −24, ticks peak −12 | dark; ticks momentarily brighter | tick transients punctuate |
| 55–89 | −20 → −16 | mid (centroid ~1000), convex swells | voice/whisper foreground, looming |
| 89–110 | −24 → −28 | darkest (corner 750, centroid ~700) | withdrawal trough (sets up climax) |
| 110–142 | −16 → **−8 (peak at 142)** | rising to centroid ~1500 (cap 1600) | golden-section climax; REBEC bursts duck their own corner *down* |
| 142–165 | −8 → −14 | falling | climax decays/fragments |
| 165–199 | −16 → −20 | mid-dark (centroid ~950) | impossible bell; constant-loudness spectral inversion |
| 199–230 | −22 → −∞ | darkening to sub-only, then HP-removed | long exhale; breath tires; caught-breath truncation ends it |

**Loudness is relative:** the §4 trough at −28 is the setup that makes the §5 peak at −8 read as overwhelming. **Brightness tracks loudness but the climax caps at 1600 Hz centroid** — density and roughness carry the peak, not treble, so it never turns arcade-bright. The final fade removes the sub last, so the ending is the floor dropping out.

---

**Structure at a glance:** Absence → First Presence → Almost-Speech (motif) → Withdrawal → Climax/Many (motif, φ-peak ≈142 s) → Impossible Bell → Receding-into-silence. One gesture in three costumes; golden/Fibonacci form; tuning locked to the instruments' own inharmonic spectra; roughness dialed to the exact Plomp–Levelt peak (0.25·ERB); low-end felt, space as distance, silence as the final instrument. Every recipe is the vetted/corrected version — directly codeable in numpy/scipy.