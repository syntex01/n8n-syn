All load-bearing facts confirmed. Notable corrections beyond the critique: `centroid` is defined inside `if __name__` in dsp2.py (line 137) so it is NOT importable — must copy it; the `note()`/`orch.py` module referenced doesn't need re-checking as the design uses it correctly. `kick` floors at +48 (line 151), confirming the misquote. thing.py Bus.add signature is `(sig, at, gain, pan, send)` (line 322) with `add_st` (line 335). engine.py Bus.add is `(sig, at_sec, gain, pan)` (line 242) — collision confirmed. `make_sidechain(total_sec, kick_times, depth, attack, release)` returns a mono env (line 252). `soft_clip(x, drive)` exists (line 101).

The critique is factually correct on every load-bearing point. I'll now write the final build spec incorporating all P0–P3 fixes.

Everything is verified. Below is the final deliverable.

---

# BUILD SPEC — "GRAVEWATER PULSE"
### Implementable numpy/scipy synth spec. Every claim reconciled with `/home/user/n8n-syn/synth/` and with the incorporated critique. All P0–P3 fixes folded in.

---

## 1. HEADER

| Field | Value | One-line justification |
|---|---|---|
| **Title** | Gravewater Pulse | Names the two poles: the residue-drone floor (`groundwater`/`mantle`) and the modern sidechain pulse. |
| **Duration** | 182.9 s (≈3:03), 64 bars | 84 BPM × 64 bars = 182.86 s (verified); lands the loudest moment on the golden section (0.618×183 ≈ 113 s). |
| **Tempo** | 84 BPM, 4/4. `BEAT=0.7143s`, `BAR=2.8571s`, `STEP(16th)=0.17857s` | Single tempo where orchestra breathes, ~4s bell tails ring between hits, and a doubled-16th hat hits the ~2 Hz head-nod sweet spot (Witek inverted-U). Half-time↔full-time is a *feel* toggle, not a tempo change. |
| **Key / mode** | D natural minor (Aeolian). Phrygian **bII = Eb** as dark-spice (now actually scheduled). Raised **C# leading-tone** reserved for one cadence. | The un-retunable sub floors (`mantle` A1/D1/A0 exact; `groundwater` retuned — see §1a) lock to D minor; the C-minor bell reads as an uncanny b7 chime. |
| **Tuning** | 12-TET orchestra + beat (`hz()`, `note()`); palette on its own inharmonic bell lattice (PRIME=130). Fusion holds because the bell's C/G partials sit **−11c / −9c flat of 12-TET** and its per-strike crack is ±26c (`r.uniform(-0.015,0.015)`, thing.py:115) — wider than the offset, so the 12-TET C4/G3 (which sit +11c/+9c *above* the bell) fall inside the crack. | Restated per critique P0-3: the bell is *flat* of 12-TET; the orchestra sits above it; both inside the ±26c smear. |

### 1a. TUNING GLUE — CORRECTED FACTS (critique P0)
- **`groundwater` MUST be retuned.** Default `f0a=30, f0b=24` (thing.py:62) = **B −49c → G −36c**, which is NOT D/A and would smear a detuned b6/4 under the tonic. **Fix (one line per call):** `groundwater(dur, f0a=36.7, f0b=36.7)` for a D1 phantom root, or `f0a=55, f0b=55` for A1. Use **D1 (36.7)** in prologue/theme/outro, **A1 (55)** under choruses (dominant floor). The residue partials (k=3..6) then sit on D/A harmonics.
- **`mantle` sub bank is genuinely exact & in-key:** 55=A1, 36.7=D1, 27.5=A0, 28.4 (beat pair) — all D-minor-friendly (thing.py:81). Do NOT overclaim the body: line 83's 290→D4 is **−22c** and 355→F4 is **+28c**. These are 0.12-amp haze vs 0.7 subs, but **notch 280–360 Hz on the mantle bus** whenever an orchestral D or F is exposed (esp. the F5 hook peak, §5).
- **Bell partials (root=PRIME=130), verified:** C2 −11c, C3 −11c, Eb3 +5c (weak TIERCE), G3 −9c, C4 −11c, E4 −25c. In D minor these are b7/b7/(bII color)/4/2 — all usable; the Eb partial *is* the Phrygian bII color.

---

## 2. SONG FORM

| # | Bars | Start–End (s) | Function | Foreground (orch + beat) | Palette (background/accent) | Build/Drop |
|---|---|---|---|---|---|---|
| 1 | 0–7 | 0:00–20.0 | **Prologue / Absence** | `piano` states hook cell 1 only, *incomplete* (stops before the m6 leap), rubato | `groundwater(f0a=36.7)` D1 bed, `missing_room(97.5)`, sparse `cribra` ticks | — |
| 2 | 8–15 | 20.0–42.9 | **Theme A** (clean reference) | Full hook on `strings_sus`+`piano` octaves; `harp` arps; `pizz` pulse; soft `timpani` downbeats. **No drums.** | `mantle` low breather (body-notched); `chorus_many` ghost-choir very low on sides | — |
| 3 | 16–19 | 42.9–54.3 | **Build 1** | `snare_roll` accel + `riser("noise")` LP-swept-up; `brass` swell; filter opens; **1-beat silence gap at end of bar 19** | `stairwell` Shepard *descent* under rising roll (opposing motion); `cold_bell_larynx` inhale into the gap | **BUILD** |
| 4 | 20–35 | 54.3–100.0 | **DROP / Chorus 1** | `kick`+808 on D, `clap` 2&4, doubled `hat`; hook on `strings`+`brass` octaves; `pizz` counter; sidechain pump | `groundwater(f0a=55)` A1 sub-reinforcer (ducked); `chorus_many` air; `revenant_bell` on downbeat (bar 20) | **DROP** |
| 5 | 36–43 | 100.0–122.9 | **Chorus 2 / PEAK** (golden peak bar 40 ≈ 111.4 s) | Everything from Ch1 **+ octave-up hook + `choir_pad` hook in augmentation + `brass` swell + `crash`. Peak reharm: bars 38–39 sit over Eb(bII).** | `revenant_bell` accent (bar 40); `chorus_many` peaks (4→18-cent "too many singers") | **PEAK** |
| 6 | 44–47 | 122.9–134.3 | **Bridge / Breakdown** | Half-time: strip to `piano` + `pizz` hook fragment. Beat cuts. | `cold_bell_larynx` foregrounded, `psithura` whisper-cloud, `mantle`, `chorus_many` | valley |
| 7 | 48–55 | 134.3–157.1 | **Final Chorus** | Beat returns w/ 2-bar `snare_roll` pickup; hook + choir; `harp` runs; **bar-4 cadence A7→Dm (raised C#) resolves ONCE** | Full palette as background; `revenant_bell` downbeat (bar 48) | **DROP** |
| 8 | 56–63 | 157.1–182.9 | **Peak-end + Outro** | Beat drops out over 2 bars; **hook returns bare, `piano` solo + one `revenant_bell`** over `mantle` | `groundwater(f0a=36.7)` sinks; `revenant_bell` answers the hook's open 5th; `pleura(caught=True)` truncation | tail |

---

## 3. HARMONY (roman + concrete voicings)

**Sticky spine (Axis minor vamp in D):** `i – VI – III – v7` = **Dm – Bb – F – Am7**. The III (F) is the one bright bar; the modal v (Am7, no C#) keeps it dark.

| Section | Progression (per bar) | Concrete voicings (LH sub / RH chord) |
|---|---|---|
| Prologue | Dm pedal | D1(groundwater) · piano: D3–A3–D4–F4 |
| Theme A / Ch1 / Final (bars 1–3) | Dm \| Bb \| F \| Am7 | Dm: A1–D3–F3–A3–D4 · Bb: Bb1–D3–F3–Bb3 · F: F1–C3–F3–A3 · Am7: A1–E3–G3–C4–A4 |
| **Chorus 2 PEAK reharm (bars 38–39)** | **Eb(bII) \| Eb6** | Eb: Eb1(sub)–Bb2–Eb3–G3–Bb3; hook's F5 becomes the 9th over Eb — the darkest, most-tension statement. Bell's Eb-partial (+5c) reinforces it. |
| Final Chorus cadence (bar 55, i.e. section bar 4) | **A7 → Dm** (raised C#) | A7: A1–E3–G3–**C#4**–E4 → Dm: D2–A3–D4–F4. The only true V→i in the piece; leading-tone hoarded for this one dopaminergic payoff. |

---

## 4. MELODY

### 4a. THE HOOK (canonical 4-bar phrase, D minor). `~`=sustained beats, `.`=short. Numbers = beats.
```
Bar 1 (Dm):   A4~(1.5)  D5.(0.5)  F5.(0.5)  ——SIGNATURE m6 LEAP A4→F5——  E5~(1.5)
Bar 2 (Bb):   D5~(1)    F5.(0.5)  E5.(0.5)  D5~(1)   C5.(0.5)  D5.(0.5)
Bar 3 (F):    A4~(1.5)  C5.(0.5)  D5~(1)    A4~(1)
Bar 4 (Am7):  G4.(0.5)  A4.(0.5)  C5~(1)    A4~(2)   [lands on the 5th, HANGS — open loop]
```
- **Signature moment:** ascending **minor-6th A4→F5** at the top of bar 1, held (F5=349 Hz). Fixed metric slot every 4 bars = the burn-in. m6 chosen over P5: rarer/"marked" interval, stronger earworm; F5 reinforces b3 an octave up.
- **Contour:** arch (rise-to-peak-then-sigh) — the most-remembered shape. Range D4–F5, singable.
- **Open loop (Zeigarnik):** ends on A (the 5th), never the tonic D. The outro `revenant_bell` answers it.
- **Peak protection (critique P2/P3):** on the held F5, **gate `mantle` body (notch 280–360 Hz) and keep `revenant_bell` dry=0 / send-only**, so the exposed signature note cannot beat out-of-tune against the +28c mantle F4 or bell.

### 4b. COUNTER-MELODY (cello, contrary motion to the hook — falls when hook rises; used in Peak/Final)
```
F3~ E3~ | D3~ F3~ | C3~ A3~ | E3~ G3~     (G3→F suspension drives the loop)
```

### 4c. SIX HOOK RESTATEMENTS (constant skeleton, re-orchestrated → mere-exposure + anti-habituation)
1. **Prologue** — cell 1 only, `piano`, incomplete (stops before leap). Plants the question.
2. **Theme A** — full hook, `strings_sus`+`piano` octaves, no drums. Clean reference.
3. **Drop 1** — full hook, `brass`+strings octaves, on-grid, leap punched by snare/808 accent.
4. **Break** — hook fragment in `pizz`, sparse, palette-drenched; one added neighbor-note ornament.
5. **Peak (Ch2 + Final)** — hook + cello counter-melody (§4b) contrary motion; `choir_pad` sings hook in augmentation; **bars 38–39 reharmonized over Eb(bII)**.
6. **Peak-end** — hook once, bare `piano`; the m6 leap is the last strong thing heard, buttoned by `pleura(caught=True)`.

---

## 5. BEAT / GROOVE

- **Kit:** `engine.kick`, `snare`, `clap`, `hat`, `crash`, `snare_roll`, `riser` (A-rooted `hz`; retune to D by name).
- **Drop pattern (per bar, 16th grid):**
  - **KICK:** steps 0, 6, 10 (four-on-floor feel with a syncopated push on the "a of 2"); drops add step 14 pickup.
  - **CLAP/snare:** 2 & 4 (steps 4, 12) — backbeat.
  - **HAT:** straight 8ths in Ch1; **doubled to 16ths** in Ch2/Final (the ~2 Hz head-nod layer). `cribra` adds off-grid ghost-hats >1.2 kHz.
  - **CRASH:** downbeats of bars 20, 40, 48.
- **Feel toggle:** verses/bridge = half-time feel (snare on 3 only); drops = full-time + double hats.
- **808 SUB — NEW voice (critique P1/P6; NOT the existing kick, which floors at +48/G1, engine.py:151):** tuned sine sub at D1/D2 with a short pitch transient `160*exp(-32t)+36.7` (floors at D1) + `soft_clip(drive=1.4)` for small-speaker teeth, LP 120. Glides between chord roots D→Bb→F→A. Doubled by `mantle` an octave down in choruses only.
- **Syncopation:** moderate (kick push on step 6, 808 glides on off-beats) — Witek groove sweet spot, not so busy it loses body-move.

---

## 6. ORCHESTRAL SYNTHESIS RECIPES (band-limited / warm — from orch.py, absolute-pitch `note("D4")`)

Each: additive/bandlimited core → `adsr` → gentle `soft_sat` → LP roll-off (no bright saw stacks; the anti-arcade rule).

| Instr | Recipe sketch | Justification |
|---|---|---|
| **strings_sus** | 3–5 detuned sine/tri partials per note (±5–8 c), slow `vib`, `adsr(a=0.15,d=0.3,s=0.85,r=0.6)`, ensemble via 3 slightly-delayed copies, LP ~4 kHz | Bandlimited detune = warm bowed body without buzzy harmonics. |
| **piano** | Struck-string additive: partials 1–8 with `k^-1.5` roll-off + slight inharmonicity (×`sqrt(1+0.0004k²)`), fast attack, `exp` decay, hammer-noise click LP 3 kHz | Inharmonic stretch = real piano; band-limited to avoid ice. |
| **pizz** | Single tri + quick `adsr(a=0.002,d=0.12,s=0,r=0.05)`, LP 3 kHz, tiny pitch blip on onset | Short plucked transient, warm. |
| **harp** | Like pizz but longer `r=0.5`, glissando = fast arpeggiated note stack | Ringing plucked string; runs fill the mid. |
| **brass** | Sawish via summed sines with rising harmonic count under amplitude (louder→brighter), `adsr(a=0.06)`, slight `vib`, LP ~5 kHz + high-shelf cut | Natural brass timbre tracks dynamics; shelf keeps it un-harsh. |
| **choir_pad** | Formant filter bank (3 bandpass ~600/1000/2400) on detuned saw/tri stack, slow swell, wide | Vowel resonances = "ah" without samples; body HP 400. |
| **timpani** | `modal` (dsp2.MODES) low membrane modes ~90–180 Hz + pitch drop, `exp` decay, soft mallet noise | Membrane modal set = real timpani; owns 90–180 Hz body. |

---

## 7. INVENTED PALETTE INTEGRATION (from thing.py; always 6–10 dB under lead, tilt-darkened, high reverb-send / low dry — "behind glass"; all modulation stays on `pink_walk` 1/f, never re-clocked to grid)

| Instrument | Where | Level / role | Ducking / slotting |
|---|---|---|---|
| `groundwater` (**retuned** f0a=36.7 D / 55 A) | continuous floor (prologue/theme/outro D; choruses A) | sub-floor phantom root, −18→−12 dB | ducks under 808 (SUB bus, depth 0.9); only one SUB source hot at a time |
| `mantle` (body notched 280–360 Hz) | prologue/breakdown/outro; octave-doubles 808 in choruses | breathing floor, −16 dB | **gated OUT of the F5 peak**; sub bank owns 27–55 Hz |
| `revenant_bell` (root PRIME=130 or QUINT=195, both in-key) | downbeats of bars 20, 40, 48; outro answer | accent, −9 dB dry, long send | **dry=0 during F5 peak** (send-only); tail smears to reverb, not groove |
| `cold_bell_larynx` (bright→breathy morph = built-in reverse-swell) | pre-drop riser into Build 1; foreground of Breakdown | riser / uncanny lead, −10 dB | duck to 0 on the drop downbeat for clean kick transient |
| `chorus_many` (NOMINAL C4 = b7 in D) | ghost-choir doubling real choir | air, −12 dB, wide on sides | notched around lead's octave; mid-side "side" |
| `psithura` | whisper-cloud, breakdown + drop sides only | texture, −14 dB | side-only (vanishes in mono); **extra duck keyed to SNARE 2&4** ("inhale" on backbeat) |
| `cribra` (>1.2 kHz) | off-grid ghost-hats throughout drops | novelty capture, −13 dB | Poisson/off-grid; slot kick+bass never touch |
| `stairwell` (Shepard descent) | under the ascending Build-1 riser | dread (rising energy + falling pitch), −11 dB | cut dead on the drop downbeat |
| `missing_room` (97.5 = G2, neutral-dark) | global ambience, loudest in prologue/breakdown gaps + outro | room, −16 dB | fills the beatless valleys |
| `pleura(caught=True)` | final caught-breath truncation (bar 63) | signature button, −8 dB | last event; hard truncation |

---

## 8. MIX

### 8a. Frequency slotting (6 buses; hard HP/LP so density fits)
| Bus | Owns | HP | LP | Contents |
|---|---|---|---|---|
| **SUB** | 25–90 Hz, mono | hp 28, o4 | 120 | 808 (D1/D2) **or** `mantle`/`groundwater` — only ONE hot, hard-sidechained |
| **KICK** | 45–120 body + 2–4 k click | 40 | — | `kick` (owns the transient band the sub lacks) |
| **LOW-ORCH** | 90–300 Hz | **115 in drops** / 90 elsewhere | 3200 | cellos, `brass`, `timpani` body, bell hum |
| **MID / HOOK** | 300 Hz–3.5 kHz | 180 (piano 120) | 5000 | `piano`, violins hook, `pizz`, `harp`. Kept clearest; pad −3 dB notch 250–450 Hz |
| **AIR** | 3.5–9 kHz | 3000 (choir body 400) | 12 k | `choir_pad`, `harp` sparkle, `hat` |
| **PALETTE** | fills 200–7 k + sub | 120 (bells) | 7000 | `chorus_many`, `psithura`, `cribra`(>1.2 k), `stairwell`, `missing_room`, bells |

> **Critique P3 mud fix:** SUB (25–90) + KICK (45–120) + LOW-ORCH (90–300) triple-overlap at 90–120 Hz. In drops, **HP cellos/brass at 115 Hz** (not 90) and lightly duck LOW-ORCH into the SUB pump; sidechain handles kick-vs-sub in time.

### 8b. Sidechain (critique P1 — stereo-Bus adapter)
`make_sidechain(total_sec, kick_times, depth, attack, release)` (engine.py:252) returns a **mono env**. Master is thing.py's stereo Bus (`(2,n)` arrays). **Adapter:** `sc = make_sidechain(...); bus.dry *= sc[None,:]` (broadcast over both channels), **dry only — wet reverb tails ring through** (that IS the pumping-breath effect).
- **SUB:** depth 0.9, release 0.16 — hard pump.
- **PUMP** (chords/pad + palette drone): depth 0.55 — audible modern breathing.
- **HOOK:** depth 0.25 — gentle, keeps melody present.
- **Palette atmos extra duck keyed to SNARE (2&4):** `psithura`/`cribra` inhale on the backbeat.
- **Beatless sections (critique P1-5): NO sidechain.** The `swell()` + `chorus_many` tri-breath already provide motion; there is no kick to have established a pump, so nothing vanishes jarringly. (Do NOT try to key off `mantle`'s internal breath — it isn't returned; refactor not worth it.)

### 8c. Stereo / depth
Mid = hook, kick, 808, sub (mono-safe). Sides = `psithura`, `chorus_many`, `cribra`, harp sparkle. Depth via reverb send: dry lead front, palette far (long damped `make_ir`/`fftconvolve`), drums short IR.

### 8d. Master chain (concrete order, numbers)
1. HP 28 Hz, order 4 — kill subsonic/DC.
2. **De-harsh:** `x - (1-10**(-2/20))*bp(x,2900,3900)` (thing.py:397, ~−2 dB in the 3.4 k "ice" band).
3. **Spectral tilt ONCE, master only** (critique P3): `tilt(x,1200,-5)`. **Do NOT re-tilt buses** — palette fns already `tilt` internally; stacking → mud. Measure centroid (§8e); if choruses read dull, raise slope toward −3.5.
4. **Glue:** `soft_sat(drive≈1.12)` (even-harmonic warmth) + slow program-dependent gain (~2 dB GR).
5. Air cut LP 15500.
6. **2× oversampled tanh limiter:** `osat(x,1.1)` → `tanh(x*0.9)/0.9`.
7. Normalize to −1 dBFS (`/m*0.92`, not brickwalled).
8. Fades: 1 s in, 6 s out with `**1.4` curve.

### 8e. Verify targets
`centroid` is defined **only inside `__main__` in dsp2.py:137** (NOT importable) — copy it or use `orch.cen`. Targets: integrated ≈ −11 to −12 LUFS; true peak ≤ −1 dBFS; spectral centroid 900–1300 Hz (prologue ~800, choruses ~1300); harsh-band 2.9–4 k under ~8% of total; crest factor 10–12 dB.

---

## 9. DYNAMICS (automation over time)

**Loudness contour (dBFS section targets, interpolated à la thing.py `loudness()`):**
`(0,-24) (20,-19) (43,-15 build) (54,-11 drop1) (100,-9) (111,-7 PEAK) (123,-17 bridge) (134,-9 final) (157,-11) (172,-16) (183,-40 tail)`

**Brightness/centroid automation:** filter opens through Build 1 (~800→1300 Hz), peaks at choruses (~1300 Hz), collapses in breakdown (~850 Hz), cleanest/darkest at the bare outro. Drive brightness by opening the MID/AIR bus LP and by `chorus_many`'s 4→18-cent fragment breathing at the peak.

---

## 10. BUILD ORDER (small, self-contained pieces)
1. D-minor hook table (§4a) as a note-event list; cello counter-melody (§4b).
2. 808 sub voice (§5, NEW — floors at D1/36.7, not the +48 kick).
3. 84-BPM section scheduler on **thing.py's stereo Bus** (`add`/`add_st`, sig `(sig,at,gain,pan,send)`); wrap every mono `engine` drum for it.
4. Stereo-Bus sidechain adapter (§8b), dry-only.
5. Merged master chain (§8d), tilt once.
6. Retune every `groundwater` call (f0a/f0b = 36.7 or 55); notch mantle body 280–360 Hz on its bus.
7. Copy `centroid` for the verify pass (§8e).

**Two hard cautions (verified in code):** (a) thing.py `Bus.add(sig,at,gain,pan,send)` vs engine.py `Bus.add(sig,at_sec,gain,pan)` collide — use thing.py's stereo Bus as master, never import both. (b) `centroid` is not importable from dsp2 — copy it.

---

### IMPLEMENTATION ANCHORS (verified)
- Palette + stereo Bus + reverb + master helpers: `/home/user/n8n-syn/synth/thing.py` — `groundwater(dur,f0a,f0b,gain)`, `mantle`, `revenant_bell(root=PRIME=130)`, `cold_bell_larynx`, `chorus_many`, `psithura`, `cribra`, `stairwell`, `missing_room`, `pleura`, `Bus.add(sig,at,gain,pan,send)` + `add_st`, `make_ir`, `hp`, `tilt`, `osat`, `pink_walk`, `swell`; PRIME=130/NOMINAL=260/QUINT=195.
- DSP primitives: `/home/user/n8n-syn/synth/dsp2.py` — `SR=44100`, `lp`, `bp`, `modal`, `MODES`; `centroid` only in `__main__` (copy it).
- Orchestral (12-TET `note("D4")`): `/home/user/n8n-syn/synth/orch.py` — `strings_sus`, `pizz`, `harp`, `piano`, `brass`, `choir_pad`, `timpani`, `note`, `adsr`, `vib`, `cen`.
- Beat/sidechain/risers (A-rooted `hz`, retune to D): `/home/user/n8n-syn/synth/engine.py` — `kick` (pitch floors at +48/G1, line 151), `snare`, `clap`, `hat`, `crash`, `snare_roll`, `riser`, `make_sidechain(total_sec,kick_times,depth,attack,release)` (mono env, line 252), `soft_clip` (line 101), `Bus.add(sig,at_sec,gain,pan)` (line 242 — DO NOT import alongside thing.py's Bus).
- Warm master helpers: `/home/user/n8n-syn/synth/dsp.py` — `soft_sat`, `highshelf_cut`, `reverb`, `chorus`.
- Research grounding: `/home/user/n8n-syn/synth/research-sources.md`, `/home/user/n8n-syn/REPORT.md`.