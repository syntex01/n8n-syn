The permission-handler bug persists in this session as well (all tool parameters stripped), so like the judges I finalize from the design texts, the audit brief, and the verdicts — which are complete for this purpose. Signature verification against `/home/user/n8n-syn/synth/*.py` is delegated to the implementation step and encoded in the checklist below.

# FINAL BUILD SPEC — "RESIDUA"

**Base: Design 1 (unanimous winner, all three lenses). Mandatory grafts merged: D4 hoarded leading tone + phantom modulation; D2 replay seam + exposure ledger + Pavlov pre-echo; D3 Tessera + Pneuma Triad; D2/D3/D4 breath-locked master bus. Optional graft included: Glossa intelligibility ramp (low-risk parameter on vox_glottis).**

---

## 0. GLOBALS

| Parameter | Value |
|---|---|
| Title | RESIDUA |
| Duration | 110 bars = 253.846 s = 4:13.85. `TOTAL_SAMPLES = int(round(110 * BAR * SR))` (R4); bell tails end inside the buffer |
| Tempo / meter | 104 BPM, 4/4. `BEAT = 60/104 = 0.576923 s`, `BAR = 2.307692 s`. Bar N starts at `(N-1)*BAR` |
| SR / format | 48 kHz stereo, 16-bit TPDF-dithered WAV |
| Key | D minor, structurally withheld: **no D fundamental below 110 Hz anywhere before 2:37.5** (one carved exception, §4-Eye). Sub register belongs to the dominant pedal A1 (55 Hz) until the hit |
| Tuning treatment | 12-TET base. Character detune only: groundwater per-partial 1/f walks ±3–8 cents; vox_glottis ±18-cent drift; horn pairs 6–10 cents; string section σ=8 cents. **No stretched-tuning system** (D3's dual lattice rejected on risk — Tessera and Pneuma carry the alien quota instead). Split_horizon beat-rate macro is the roughness/tension dial (0.5→7 Hz), snapping to pure intervals at releases |
| Hoarded pitch | **C# is banned track-wide** except two events (§5). The hook's dominant is always Asus4 or A5 (open fifth) — never the third. The whole track is a war for the two semitones around the withheld D: C# below (promised, broken) and E♭ above (feared, granted) |
| Golden section | 0.618 × 253.846 = 156.88 s; bar 69 downbeat = 156.92 s. The engineered silence sits on it |
| Chill events | C1 "The Visitor" 1:41.5 · C2 "The One" 2:37.5 (peak) · C3 "The Last Breath" 3:46.2 |

**Global breath bus (graft G-breath):** one control array `breath(t)` (asymmetric inhale 40% / exhale 60%, raised-cosine), period = 2 bars in all body sections, stretching to 13 s across the Eye, accelerating 13 s → 3 s through bars 62–68, **frozen mid-inhale for the entire 577 ms silence**, released as an exhale-shaped envelope on the C2 hit. It multiplies (sub-perceptually): pad/drone gain ±1.5 dB, hall send ±15%, pads-bus LP ±800 Hz, stereo width ±3%. `np.interp` breakpoints; pleura's caught-breath in the silence is placed exactly on the frozen inhale.

---

## 1. THE HOOK — "The Lament Leap"

4 bars, 9 events, range A2–F3, arch contour, one signature interval. **Pitch and rhythm verbatim at every complete exposure**; only orchestration, register (octave lift at C2 only), and harmony underneath change.

| # | Note | Position (bar.beat) | Duration | Harmony under | Function |
|---|---|---|---|---|---|
| 1 | D3 | 1.1 | dotted quarter | Dm (no root <D3) | rise |
| 2 | E3 | 1.2.5 | eighth | Dm | rise |
| 3 | F3 | 1.3 | half | Dm | crest |
| 4 | E3 | 2.1 | quarter | Gm(add9) | settle |
| 5 | A2 | 2.2 | dotted half | Gm(add9) | the coiled spring |
| 6 | **F3** | 3.1 | dotted half | **E♭ major (♭II)** | **SIGNATURE: A2→F3 ascending minor 6th, landing on beat 1 as a major-9th appoggiatura over E♭** — leap + appoggiatura fused, at the phrase's golden point |
| 7 | E♭3 | 3.4 | quarter | E♭ | appoggiatura resolves down by step |
| 8 | E3 | 4.1 | half | **Asus4 → A5 (open fifth — no C#, ever)** | chromatic lift E♭→E; ends on degree 2, natively unresolved |
| 9 | (breath) | 4.3 | half rest | A5 | Zeigarnik gap |

The hook's bar 3 pre-seeds the C2 shock chord (E♭ major) at every pass — seven subliminal rehearsals of the "unprepared" bloom.

**EXPOSURE LEDGER (D2's bookkeeping grafted onto D1's material).** One Wundt deviation per pass from V3 onward — never zero, never two:

| Pass | Bars / time | Form | Complete? | Costume / deviation |
|---|---|---|---|---|
| T1 | 3–6 / 0:05 | bars 1–2 only, as residue-partial amplitude emphasis inside groundwater (no notes, no source) | teaser | subliminal seeding + micro-Zeigarnik |
| C | 9–12 / 0:18.5 | canonical, clean, whole | ✓ | rebec_wraith, plain |
| V1 | 13–16 / 0:27.7 | verbatim | ✓ | + low choir shadow −12 dB |
| V2 | 25–28 / 0:55.4 | verbatim, groove under | ✓ | bass+low-choir doubling; **pre-echo device activates** (§7) |
| V3 | 33–36 / 1:13.8 | deviation: note 4 displaced to the offbeat | ✓ | choir double |
| V4 | 41–44 / 1:32.3 | verbatim, **transposed to B♭ minor** | ✓ | solo vox_glottis → C1 fusion |
| F1 | 53–61 / Eye | inverted + fragmented (≤4 notes, never completes) + hook-as-filter at 1/8 speed | ✗ | cold_bell_larynx over Tessera |
| F2 | 62–67 / build | notes 1–3 only, looping low-string/organ ostinato, never completing | ✗ | under the B♭ pedal |
| V5 | 71–74 / 2:41.5 | verbatim, **octave up (D4 start), home key at last** | ✓ definitive | tutti — "THAT'S the song" |
| V6 | 75–78 / 2:50.8 | deviation: appoggiatura F4 **held two extra beats** (suspension over E♭) before falling; one displaced drum accent | ✓ | tutti |
| W | 97–99 / 3:41.5 | **truncated on note 7 (E♭3)**; the pre-echo for note 8 fires and note 8 never sounds | withheld | solo voice, dry |

7 complete exposures (mere-exposure liking, no two orchestrated alike), 4 incomplete (open loops).

---

## 2. FORM TABLE

Energy: 0–10. Lever codes from the psychology map (A anticipation, B frisson stack, D silence→hit, E voice entrance, F fusion/fragmentation, G earworm, H groove, J repetition-variation, K peak-end, L Zeigarnik, M contrast, O phantom pitch, P Shepard, Q roughness, T excitation transfer).

| Bars | Time | Section | Enters | Exits | Energy | Levers |
|---|---|---|---|---|---|---|
| 1–8 | 0:00–0:18.5 | **SEED** | groundwater (phantom D, fundamental absent), missing_room comb void, 3 cribra ticks (ITD-panned), hook tease T1, breath bus starts | — | 1 | O, G-tease |
| 9–20 | 0:18.5–0:46.2 | **FIRST STATEMENT** | rebec_wraith (C, V1), heartbeat kick on 1+3, mantle on A1 (bar 13, 2-bar breath lock), split_horizon at 0.5 Hz | — | 3 | G, J, A (trust build: grows and pays on-grid into the groove) |
| 21–36 | 0:46.2–1:23.1 | **GROOVE** | full kit (§8), bass pulse A1-C2-A1-G1 (rootless), **Pneuma Triad enters −30 dB**, sidechain pump, hook V2+V3, pre-echo device | — | 6 | H, G, J, I |
| 37–40 | 1:23.1–1:32.3 | **FILL + THEFT (false drop)** | 1-bar accelerating fill (floored increment) → bars 38–40 textural strip: groundwater + missing_room + one pleura breath only | groove kit, bass, Pneuma | 2 | A (payoff stolen), M |
| 41–52 | 1:32.3–2:00.0 | **C1 — THE VISITOR** | solo vox_glottis in B♭ minor → chorus_many fusion → hall bloom → mantle glide A1→G♭1; deflation bars 47–51; **bar 52 beat 1 (1:57.7): single revenant_bell strike — its tail is captured in-render for Tessera** | fill debris | 7→3 | B (6 triggers), E, F, T |
| 53–61 | 2:00.0–2:20.8 | **THE EYE** (−30 dB RMS) | **Tessera bed** (chord-quantized granulation of the C1 bell tail — the Eye is the inside of the bell that ended the Visitor), groundwater reduced under it, cold_bell_larynx F1, psithura close/dry, hook-as-filter, heartbeat decelerating 72→54 BPM, Pneuma resurfaces as the loudest living thing, breath bus at 13 s. **Bars 57–58: THE PRIVATE RESOLUTION** (§5) | choir, hall | 1 | M, O, N, S; miniature B |
| 62–68 | 2:20.8–2:36.9 | **DREAD BUILD** (16.2 s) | B♭ (♭VI) pedal grind, F2 ostinato, war drums accelerating 8ths→trip-8ths→16ths (bars 62/64/66, backbeat dropped bar 67), stairwell Shepard (dark-tilted, only use), split_horizon 1→7 Hz, string-bus filter 800 Hz→6 kHz, **tuned IR pre-singing E♭2/G3/B♭3**, **phantom modulation: groundwater residue partials crossfade D→E♭ across the 7 bars**, Pneuma desyncs to panic breathing, breath bus 13 s→3 s. **Bar 68 (2:34.6): THE BLAZE — A major with C#4 exposed on top** (§5) | Eye textures | 8→9.5 | A, P, Q, T, O-inverted |
| 69 beat 1 | 2:36.90–2:37.48 | **THE SILENCE** (577 ms, golden section) | pleura breath −38 dB dead center; reversed LP'd pre-echo of the hit rising −50→−30 dB; breath bus frozen mid-inhale | EVERYTHING (3 ms fades; reverb returns ducked −60 dB in 5 ms) | 0 | D |
| 69.2–78 | 2:37.48–2:56.1 | **C2 — THE ONE** (peak) | 8-trigger hit (§4); hook V5 at 2:41.5 with **the hoarded resolution: ♭II→i collapse + first D bass of the piece (D2→D1)**; V6 | silence | 10 | B (8 triggers), G, K-peak |
| 79–84 | 2:56.1–3:13.8 | **AFTERGLOW / FRAGMENTATION** | chorus_many splits into 24 detuned individuals; Dm→B♭maj7→Gm(add9); heartbeat only; width 0.9→0.5 over 6 bars | tutti, one layer per bar | 6→3 | F-inverse |
| 85–96 | 3:13.8–3:41.5 | **RECESSION** | half-time groove ghost (anchor only, −18 dB, LP 1.2 kHz); hook callback on rebec_wraith (85–88); distant chant phrase (89–92, hall-drowned); dissolve (93–96); **sub A1 finally releases — nothing in the sub** | drums, chant, mantle | 2 | J, unease-by-absence |
| 97–104 | 3:41.5–3:59.9 | **C3 — THE LAST BREATH** | solo vox_glottis (same patch as C1) hook W; soft ♭VI bloom at note 6; truncation at note 7; ghost pre-echo of note 8; one cracked revenant_bell | voice mid-phrase | 3 | B-whispered, E, L |
| 105–110 | 3:59.9–4:13.8 | **TAIL + REPLAY SEAM** | bell decay into phantom; true D fundamental (73.4 Hz) fades in 4:00–4:06 at −34 dB, fades out 4:06–4:11 — granted, then revoked; **bars 109–110: texture bit-identical to bar 1's seed** (same rng seeds, same generator calls, matched gain) so replay reads as continuation | bell, the tonic itself | 1→0 | L×3, O, replay seam |

RMS arc (per-4-bar, machine-verified): −30 → −24 → −16 → −14 (C1) → −30 (Eye) → −26→−13 (build) → −inf/−38 (silence) → −10 short-term, −1 dBTP peaks (C2) → −16 → −22 → −26 (C3) → −34 dBFS.

---

## 3. THE CHILL MOMENTS — second-by-second anatomy

### C1 — "THE VISITOR" (1:32.3–2:00.0; bloom at 1:41.5, 40% of runtime)

- **−9 s (1:23.1):** groove executes the 1-bar fill promising a drop — the drop is STOLEN.
- **−9→0 s (bars 38–40):** near-silence: groundwater + missing_room + one pleura breath. RMS −32, width 0.3. Aroused, then stranded.
- **0 s (1:32.3):** first solo voice of the track — vox_glottis, dry, close (room send 8%, +3 dB @ 200 Hz, LP 6 kHz), hook notes 1–5 in **B♭ minor** (unprepared chromatic mediant against the phantom D). Jitter ±0.6%, shimmer ±0.5 dB, LF glottal pulse, aspiration gated by open phase, ±18-cent drift.
- **+9.2 s (1:41.5, on note 6, the m6 leap F2→D♭3):** THE BLOOM — chorus_many fuses 22 voices out of the one voice over 350 ms (onset scatter 10–40 ms, vibrato-onset delays 0.3–1.2 s); hall opens 0→full over 500 ms **through the B♭m-tuned IR**; width 0.3→1.4 in 80 ms; mantle slides A1→G♭1. Voicing: G♭1 / G♭2–D♭3 / B♭3–D♭4–F4 (formants shelved −4 dB above 2 k) / solo D♭4 on top. All added energy 60–800 Hz.
- **+14→+25 s:** deflation — choir thins voice by voice (staggered breaths), G♭maj7 → Asus → Gm(add9). Texture resolves; harmony does not.
- **+25.4 s (bar 52.1, 1:57.7):** ONE revenant_bell strike closes the Visitor. Render captures its last 2.5 s → Tessera source.
- Triggers: voice entrance, unprepared mediant, textural expansion, appoggiatura-on-leap, space opening, sub event = **6 stacked**.

### C2 — "THE ONE" (silence 2:36.90; hit 2:37.48)

- **−16 s (2:20.8):** dread build begins (form table row). Three simultaneous subliminal primings run: (1) tuned IR quietly ringing E♭2/G3/B♭3; (2) **phantom modulation** — groundwater's residue partials crossfade from implying D (146.8/220.2/293.7/367.1 Hz) to implying E♭ (155.6/233.3/311.1/388.9 Hz) linearly across bars 62–68, inaudible as an event; (3) the hook's seven prior E♭ bars. The shock chord is objectively unprepared and triply pre-heard.
- **−2.3 s (bar 68, 2:34.6):** **THE BLAZE** — war horns + organ strike A major, C#4 exposed on top: the first C# in fortissimo history of the track, screaming V→i, C#→D promised on the downbeat of 69—
- **0 s (2:36.90):** hard cut of EVERYTHING (3 ms raised-cosine fades; both reverb returns ducked −60 dB in 5 ms). 577 ms = one beat, ON the golden section.
- **Inside the silence:** (1) pleura caught-breath, bone dry, center, −38 dB, on the frozen inhale; (2) time-reversed, LP-2 kHz copy of the hit's own first 300 ms rising −50→−30 dB, ending 1 sample before the hit.
- **+577 ms (2:37.48, beat 2 — one beat late):** THE HIT, 8 triggers at once:
  1. tutti **E♭ MAJOR** (♭II) — breaks the C#→D promise a semitone HIGH;
  2. mantle B♭1→E♭1 glide (58.3→38.9 Hz, 350 ms) + kick body 55→38 Hz — first sub departure from the dominant;
  3. width mono→1.5 in 80 ms (velvet-decorrelated hall, largest space of the track);
  4. loud+DARK tutti: chorus_many(24) + organ 16′+8′ + horns (+40-cent overshoot) + strings; voicing E♭1/E♭2/B♭2/E♭3/G3/B♭3/E♭4 — single third, nothing above E♭4, tilt −4.5 dB/oct above 2 kHz;
  5. revenant_bell crown strike, modes <2.4 kHz;
  6. **2:41.5 (bar 71): hook V5 octave up; E♭ collapses ♭II→i to D minor under the pickup while the bass plays D2→D1 — THE HOARDED RESOLUTION, the first true tonic fundamental at second 161**;
  7. appoggiatura F4 as 9th over E♭ (bar 73) with full choir;
  8. V6 (bars 75–78) with the held-suspension deviation.
- **Release:** 10 bars of full statement (peak-end memory), then controlled fragmentation — never a cliff.

### C3 — "THE LAST BREATH" (3:41.5–3:48.2)

- **Before:** sub silent for the first time since 0:27; only phantom D + soft Gm(add9) pad; RMS −26; width 0.4.
- **3:41.5:** same vox_glottis patch as C1 (recognition), intimate, dry, begins hook W in home register. **Glossa graft:** intelligibility parameter (syllable-rate × formant-bandwidth) ramps 0.55→0.85 across the phrase — it ends "about to say something."
- **3:46.2 (note 6, the leap):** soft unprepared ♭VI bloom — Gm(add9)→B♭maj7, hall opens gently, width 0.4→1.1 — a whispered replica of C2's mechanism; simultaneously the true D fundamental begins its first-ever fade-in beneath.
- **3:47.6:** the reverb-only pre-echo for note 8 (E3) blooms, exactly as it has before every leap since V2—
- **3:47.9:** the voice stops ON NOTE 7 (E♭3). Note 8 never comes. The trained anticipation fires into nothing.
- **3:48.2:** ONE cracked revenant_bell strike, dark, two-position excitation, 20+ s decay. Tail: tonic granted 4:00–4:06, revoked 4:06–4:11; seam bars 109–110.

---

## 4. HARMONY

| Section | Progression / voicing notes |
|---|---|
| Seed / statements / groove | Hook loop: \|\| Dm \| Gm(add9) \| E♭ (♭II) \| Asus4→A5 \|\| — a Neapolitan half-cadence that never resolves to i. Dm voiced rootless below D3; A chord ALWAYS sus4 or open fifth (C# ban) |
| C1 | B♭ minor region: B♭m → **G♭maj7 bloom** (♭VI-within-the-shifted-world) → Asus → Gm(add9). Bloom voicing: G♭1 / G♭2–D♭3 / B♭3–D♭4–F4 / D♭4 |
| Eye | Gm(add9) color tones only over phantom D (iv over a tonic that isn't there). Tessera grain-quantization targets: G–B♭–D–A per 2 bars, drifting to G–B♭–C–D bars 59–61 |
| **Eye bars 57–58, THE PRIVATE RESOLUTION (graft)** | cold_bell_larynx sounds a lone pianissimo **C#3→D3** — the only V→i gesture before the climax — while groundwater's true D2 fundamental fades in for exactly 2 bars at ≤−42 dBFS, then withdraws. The withheld-tonic FFT gate carves this one window (§10) |
| Build | B♭ pedal (♭VI) vs phantom D; F2 ostinato (D–E–F) on top; **bar 68: A major, C#4 exposed** (horns+organ) — the second and last C#, betrayed |
| C2 | **E♭ major** (♭II, triple-primed) → ♭II→i Phrygian collapse to **D minor** at bar 71 with first D bass (the single hoarded resolution) → hook loop octave-up, V6 suspension deviation |
| Afterglow / recession | Dm → B♭maj7 → Gm(add9); chant callback over Gm |
| C3 / tail | Gm(add9) → **B♭maj7** soft bloom; final pad is ♭VI; the ♭II→V loop is never cadenced; tonic fades in and back out. Three open loops: melodic (note 8), harmonic (no cadence), spectral (revoked tonic) |

Borrowed-chord inventory: E♭ (♭II Neapolitan, hook + climax), B♭/B♭maj7 (♭VI pedal + blooms), G♭maj7 (♭VI of the B♭m excursion), A major (the banned V-with-third, twice only).

---

## 5. THE HOARDED LEADING TONE (rule restated for the implementer)

`assert`: no pitch class C# in any melodic/harmonic voice anywhere EXCEPT (a) bars 57–58 cold_bell_larynx C#3→D3 pianissimo; (b) bar 68 A-major blaze. All A-chords elsewhere are sus4/open-5th. E♭ (♭II) and C# are the two chromatic neighbors of the withheld D: the Eye grants the lower-neighbor resolution privately; the blaze promises it publicly and the track pays with the upper neighbor instead.

---

## 6. INSTRUMENTATION — synthesis recipes

Only allowed raw sources: dsp band-limited additive osc + FFT-shaped pink noise (R1).

**Reuse + mandated upgrades (from audit §1–2):**

| Voice | Asset | Upgrade |
|---|---|---|
| Phantom tonic | `thing.groundwater` | per-partial 1/f detune walks ±3–8 c; independent L/R phases; **partial-set crossfade lane for phantom modulation (D→E♭ vectors)**; true-fundamental fade envelopes (bars 57–58 window; tail 4:00–4:11) |
| Sub pedal / breath clock | `thing.mantle` | breath locked to 2-bar clock → exports the global breath control array; sidechain-ducked; glides A1→G♭1 (C1), B♭1→E♭1 (C2) via cumsum phase (R8) |
| Solo voice | `thing.vox_glottis` | jitter ±0.6% (1/f), shimmer ±0.5 dB, LF glottal pulse, aspiration gated by open phase, ±18 c drift; **new `intelligibility` param**: syllable rate 2→4.5 Hz × formant-bandwidth narrow/wide, F2 capped 2.0 kHz, F3 dark at 2.3 kHz −12 dB |
| Choir | `thing.chorus_many` | per-voice vibrato-onset delay 0.3–1.2 s, onset scatter 10–40 ms, formant offsets ±5%, breath noise −24 dB, staggered dropouts; fusion (C1) and fragmentation (afterglow) modes |
| Eye inhabitant | `thing.cold_bell_larynx` | reversed-exp inhale gain-follow + 500→300 Hz formant glide; carries F1 and the private C#3→D3 |
| Bells | `thing.revenant_bell` | velocity noise-burst excitation (2–8 ms, LP ∝ velocity), inharmonicity drift, T60 ∝ 1/f^0.7, two-position strikes, odd/even mode stereo split, modes <2.4 kHz |
| Riser | `thing.stairwell` | raised-cosine log-f window tilted dark (≤−12 dB above 2 kHz); parallel band-limited noise riser; used once |
| Roughness dial | `thing.split_horizon` | beat-rate macro 0.5→7 Hz; snaps to pure interval at each release |
| Textures | `missing_room`, `psithura`, `cribra`, `pleura` | comb delay modulated ±0.3%, fed from the bus; ticks with per-event azimuth + ITD (sin(az)·0.6 ms) + near-field EQ; pleura owns the silence |
| Hook lead | `thing.rebec_wraith` | as-is, room send only |
| Orchestra | `orch` strings/organ/horns/timpani | strings: 14–16 true voices, σ=8 c, onset scatter 15–60 ms, delayed 1/f vibrato, bow-noise pink −30 dB, shared 60 ms corpus IR (3–5 peaks 200–800 Hz); organ: one shared 0.15 Hz wind LFO + 30 ms octave-up speech transients; horns: +30–60 c attack overshoot, chiff, paired 6–10 c beating |
| Drums / chant | `crusade5` patterns | 3-layer velocity drum recipe (§8); chant: consonant noise-bursts through tiny-room IR, phrase-final 20–40 c falls, octave double −9 dB |

**New instruments (grafted, concrete DSP):**

1. **TESSERA (D3)** — Eye harmonic bed. Two-pass render: capture the last 2.5 s of the bar-52 revenant_bell buffer. Granulate: 80–180 ms Hann grains, ~30 grains/s, 12–18× time stretch, each grain resampled (`np.interp`) to the nearest current chord target (G/B♭/D/A set), per-grain random azimuth with matched ITD. Chord changes = re-quantization targets. Reuses the existing dsp2 granular engine; no phase vocoder.
2. **PNEUMA TRIAD (D3)** — three FFT-pink breath layers, formant biquad pairs at (350,900)/(500,1200)/(300,800) Hz, asymmetric inhale (40%, LP 1.5 kHz)/exhale (60%, LP 3 kHz tilted), periods 3:4:5 breaths per 4-bar phrase, unison inhale on every phrase downbeat, panned L/C/R with matched ITD. −30 dB under the groove; foreground creature in the Eye; period drift to 3.2:4:4.7 (panic) in the build. All energy <2 kHz.
3. **HOOK-AS-FILTER (D1)** — time-varying resonant bandpass (Q≈30), center swept along the hook's pitch trajectory at 1/8 speed via `np.interp` breakpoints, per-block biquad coefficient interpolation (`sosfilt` block-wise), applied to groundwater, −20 dB, Eye only.
4. **TUNED IRs (D1)** — per-section hall IR = pink-burst × exp decay, plus 3–4 exponentially decaying sinusoids at chord-tone frequencies at −18 dB rel.: build IR tuned E♭2/G3/B♭3; C1 IR tuned to B♭m modes; sends crossfaded at boundaries.
5. **PRE-ECHO ENGINE (D2 + D1, one device family at two scales)** — (a) per-leap: convolve each leap-landing note with the hall IR, reverse the tail, place a reverb-only ghost one 8th (0.288 s) before the dry onset at −20 dB, LP 5 kHz, from V2 onward — including the orphaned note-8 ghost at 3:47.6; (b) structural: the silence's reversed hit pre-echo (np.flip + butter LP 2 kHz).

**Render-order dependencies (two-pass plan):** 1) render C2 hit → derive silence pre-echo; 2) render bar-52 bell → Tessera; 3) render all dry leap notes + hall IRs → leap pre-echoes; 4) assemble master; 5) bars 109–110 seam = re-call seed generators with bar-1 seeds and gains, verify `np.array_equal` on the texture stems.

---

## 7. GROOVE (bars 21–36; ghost version 85–96)

- **ANCHOR (machine-tight, never displaced):** kick on beats 1+3 — 3 layers: sine pitch-drop 55→38 Hz/80 ms exp (cumsum phase), modal shell 3–5 modes 150–400 Hz, filtered-noise skin LP 4 kHz 5–15 ms; velocity crossfades cutoff + drop-depth, never gain-only. Deep-tom backbeat on 2+4 (no bright snare).
- **BASS:** A1–C2–A1–G1 pulse (rootless — D withheld), root 8ths + offbeat octave pops; sub sine <90 Hz mono + tanh-warmed mid layer; locked to kick.
- **MID LAYER (Witek sweet spot, ~40% of onsets displaced, humanized ±8 ms / ±1.5 dB):** frame-drum/mid-tom 2-bar pattern — bar A 16th-positions {4,7,11,14}, bar B {3,7,10,15}.
- **GHOST:** cribra ticks at offbeat 16ths {2,6,8,12,16}, −18 dB, near-field ITD.
- **Sidechain:** drum bus → follower (attack 5 ms, release 250 ms, one-pole) ducks all drones/pads −3 dB. Drum bus → transient shaper (fast 1 ms − slow 30 ms, +4 dB max) → tanh at 4× oversample → ROOM reverb only (predelay 5 ms).
- **Fills/accels:** bar 37 fill and build drums use `dt = max(dt*accel, DT_MIN)` (R3).

---

## 8. MIX / MASTER

**Buses:** drums / bass / voices / pads-drones / FX-close. Sends only, never 100% insert reverb.

**Frequency slots:** <90 Hz: mantle + groundwater + kick only, strictly mono; HP butter-2 @ 90–150 Hz on everything else; spectral tilt −3 to −6 dB/oct above 2 kHz on all bright sources; **2.5–5 kHz mix-level STFT guard: band capped at −12 dB relative to full-band, build FAILS on breach.**

**Dual reverb:** ROOM 0.5–0.8 s (pink-burst × exp(−t/0.15), LP 8 kHz, predelay 5 ms) — drums, chant consonants, ticks; HALL 4.5 s frequency-dependent T60 (5 s <500 Hz → 1.5 s @8 kHz via STFT per-band decay, predelay 25 ms) — strings, choirs, horns, bells, organ — **with the tuned-IR variants per §6.4**. Hall L/R decorrelated with two 15 ms velvet-noise convolutions; mono-check <3 dB combing below 500 Hz.

**Stereo staging — three fixed depth planes:** CLOSE (dry, <10% send): solo voice, hook lead, cribra/pleura/psithura; MID (room): drums, bass mids, consonants; FAR (hall): orchestra, choir, bells. Width automated as a musical parameter: 0.3 (pre-C1) → 1.4 (C1 bloom) → 0.3–0.4 (Eye, near-mono) → mono (silence) → 1.5 (C2) → 0.9→0.5 (afterglow) → 0.4 → 1.1 (C3 bloom). Every section boundary automates ≥3 parameters (send, bus LP, width) over 2–8 bars via `np.interp`.

**Master chain (in order):** bus comp 2:1 above −12 dBFS (10/300 ms) → tilt EQ (−1.5 dB/oct pivot 700 Hz if needed) → tanh limiter drive 1.05 at 4× oversample (resample_poly 4/1, tanh(1.2x)/tanh(1.2), down, LP 16 kHz) → true-peak ceiling −1 dBFS verified at 4× upsample → TPDF 1-LSB dither → 16-bit.

**Loudness/brightness automation anchors** (time s → short-term RMS dBFS / pads-bus LP Hz):
0→−30/1.2k · 18.5→−24/2k · 46→−16/3.5k · 92→−32/1.5k · 101.5→−14/2.5k · 120→−30/1k · 141→−26/0.8k · 156.9→silence · 157.5→−10/4k (dark-voiced) · 180→−16/2.5k · 221.5→−26/1.5k · 240→−34/1k. Breath bus modulates ±1.5 dB / ±800 Hz around this curve throughout.

---

## 9. FALSE-DROP / SURPRISE PLACEMENTS (anticipation ledger)

| Build | Bars | Promise | Outcome |
|---|---|---|---|
| A | 9–20 | statement grows into groove | **PAYS on-grid, home key** — trust deposit |
| B | 37 | fill promises a bigger drop at bar 38 | **STOLEN** — collapse to near-silence; paid sideways at bar 41 as a solo voice in the wrong key (C1 is itself the frisson) |
| C | 62–68 | everything (Shepard, accel drums, roughness, C# blaze) promises bar 69 beat 1, resolution to D | **DISPLACED + BETRAYED** — silence on the downbeat, hit one beat late, a semitone high (E♭), oversized payoff; the true resolution withheld 4 more seconds until bar 71's ♭II→i |
| Pre-echo | 3:47.6 | ghost announces note 8 as it has 6 times before | **note never comes** |

3 anticipation phases : 2 payoffs; the biggest payoff late, sideways, bigger than promised.

---

## 10. CODE-SAFETY CHECKLIST (build-failing where marked ✗)

1. **R1** Pink noise via FFT shaping only (`spectrum *= 1/np.sqrt(np.maximum(f, f[1]))`); never Voss/np.repeat.
2. **R2** Envelope sustain holds for written duration; `assert len(env) == int(dur*sr)`.
3. **R3** All accelerating loops: `dt = max(dt*accel, DT_MIN)`, DT_MIN ≥ 1 sample; N_MAX guard.
4. **R4** `TOTAL_SAMPLES` from bar count; bell tails verified inside buffer; no silent tail. ✗
5. **R5** Every placement through a declicked bounds-checked `place()` (3–5 ms raised-cosine, `end = min(start+len, len(master))`); impossible to skip. (R9 folded in.)
6. **R6** Every tanh/clip at ≥4× oversampling or followed by LP ≤ 0.45·sr — including "subtle" master drive.
7. **R7** Partial caps recomputed at MAX modulated pitch (mantle glides, bell drift), keep f_k < 0.45·sr.
8. **R8** All pitch sweeps/FM via `np.cumsum(2π·f_inst/sr)`, never f(t)·t.
9. **R10** Render ends with `assert np.all(np.isfinite(master))`; report max|x| + per-band RMS; **2.5–5 kHz guard breach fails the build**. ✗
10. **R11** `np.random.default_rng(seed)` passed explicitly to every generator; seed table logged (the replay seam depends on it).
11. **R12** 2–5 kHz discipline per-source (tilt at synthesis) AND per-mix (guard).
12. **Withheld-tonic gate:** FFT check over 0:00–2:36.9 shows zero D-fundamental energy <110 Hz, **excluding the bars 57–58 window where D2 must be present and ≤ −42 dBFS**. ✗
13. **C# gate:** pitch-class audit of all note events — C# appears exactly twice (bars 57–58 pp; bar 68 ff); all other A-chords are sus4/open-5th. ✗
14. **Silence gate:** 2:36.90–2:37.48 ≤ −55 dBFS except pleura + rising pre-echo; both reverb returns ducked −60 dB within 5 ms. ✗
15. **Seam gate:** bars 109–110 texture stems `np.array_equal` (or ≤ −80 dB null) against bar-1 seed stems. ✗
16. **RMS-arc gate:** per-4-bar RMS printed vs §2 table, ±2 dB tolerance. ✗
17. **Render order:** hit before silence-pre-echo; bar-52 bell before Tessera; dry leap notes + IRs before leap pre-echoes (§6 two-pass plan).
18. **Signature verification first:** the permission-handler bug blocked file reads in all design/judging sessions — before wiring, open `/home/user/n8n-syn/synth/thing.py`, `orch.py`, `dsp.py`, `dsp2.py`, `crusade5.py` and confirm every function name/signature referenced above; adapt call sites, not the design.
19. Mono-compatibility check on decorrelated hall (<3 dB combing below 500 Hz); sub <90 Hz strictly mono.
20. Time-varying biquad (hook-as-filter): per-block coefficient interpolation with state carry-over across blocks; verify no zipper noise (block ≤ 64 samples or coefficient smoothing).

---

**Priority order for any implementation trade-off: goosebumps > addiction > alien > exciting/chilling — never harsh, production quality. If time runs short, cut in this order: Glossa intelligibility ramp → Pneuma build-desync (keep Eye/groove Pneuma) → V6's drum deviation. Never cut: the three chill anatomies, the hoarded C#, the phantom modulation, the silence contents, the replay seam, the pre-echo family, Tessera.**