<!-- Final addiction-first build spec — synthesized by workflow wf_0e643d10 (multi-agent: research + 3 designs + 2 adversarial reviews + synthesis). Implemented in synth/addictive.py; gates in synth/qa.py. -->

# RESIDUA — FINAL BUILD SPEC (addiction-first rework)

**Priority order baked into every decision: ADDICTING > exciting > alien/chilling > all else.** Dark and alien, never harsh, but catchy and groovy from ~0:04 and engaging the whole way — no boring stretches, no beatless holes.

## 0. Build setup (do this first)
- `cp /home/user/n8n-syn/synth/crusade2.py /home/user/n8n-syn/synth/residua.py` — inherit all instruments, `Bus`, `sc_env`, `master()`, `write_wav`.
- Extend imports:
  - from `orch`: add `_additive, vib` (for `lead()`).
  - from `thing`: add `vox_glottis` (alien counter-hook).
- Everything else needed is already imported in crusade2. **Do NOT import from `engine.py`** — its hook helpers are nested in `render()` and cannot be imported; the hook is rebuilt on a new module-level `lead()` + `chant_note()`.

## 1. Global parameters
| Param | Value |
|---|---|
| **Title** | **RESIDUA** |
| **Tempo** | **140 BPM, half-time feel** — `BEAT=0.42857s`, `BAR=1.71429s`, `STEP=0.10714s`, 16 steps/bar |
| **Key/mode** | **D Phrygian** (D E♭ F G A B♭ C); keep `CYCLE_ROOT=["D","Eb","C","D"]` (i–♭II–♭VII–i), `CHORD`, `SUBROOT`, `VOWELS` |
| **Length** | **NBARS = 84**, `TOTAL = NBARS*BAR + 4` ≈ **148 s = 2:28** |
| **Buses** | keep DRUM/SUB/MUS/CHOIR/PAL; **add `LEAD = Bus(TOTAL)`** for the foreground hook |
| **Loop** | ends on held D → cold-opens on D = seamless replay |

---

## 2. THE HOOK — "the D-Phrygian Sigh" (the #1 addiction fix)

2-bar core, 16 steps/bar (steps 0–31). Format `(note, start_step, len_steps)`. This is the verified earworm winner (common rise-fall arch + **one marked leap** into a **held belt peak** + Phrygian ♭2 sigh + **hard tonic resolve**).

```
HOOK = [
  ("D4",  0, 3),   # tonic — home            293.66 Hz
  ("F4",  3, 3),   # b3 — rise               349.23
  ("A4",  6, 2),   # 5th — SYNCOPATED push (&-of-2)   440.00
  ("F5",  8, 8),   # ★PEAK — ASC. m6 LEAP A4->F5, held half-note   698.46
  ("Eb5",16, 3),   # b2 lean (+12c microtonal) — the alien sigh    626.6 (=622.25*2^(12/1200))
  ("D5", 19, 3),   # octave — Eb5->D5 half-step resolve   587.33
  ("A4", 22, 2),   # 5th
  ("F4", 24, 4),   # b3
  ("D4", 28, 4),   # ★TONIC resolve — held to barline    293.66
]
```
- **Contour:** `D–F–A ↑ | ⟶m6⟶ F5(held peak) | Eb–D ↓ (sigh) | A–F–D (home)`. Range D4–F5 = a tenth (wide, singable). Rhythm identical every loop (sticky); the single syncopated push is the A4 on step 6.
- **Signature interval:** ascending **minor sixth A4→F5 (8 semitones) into a held half-note peak** — the one uncommon leap that makes it hum-able, not just nod-able.
- **Alien fingerprint inside the reward zone:** the ♭2 sigh F5→**E♭5**→D5, with **+12c** on E♭5 applied to the frequency directly: `note("Eb5") * 2**(12/1200.0)` (chant_note/lead take freq — there is no `cents` kwarg).
- **Resolution:** lands hard on D every 2 bars — fixes RESIDUA's withheld/open-loop sin.

**Timbre — new bright `lead()` is the foreground voice; `chant_note()` is only a doubler mixed 3–4 dB UNDER it** (de-cinema fix: a diffuse choir alone buries an F5 belt). `lead()` = detuned band-limited additive saw + delayed vibrato → formant bp(300–1400) presence → fast-attack ADSR with **sustain held** → `osat` grit → `lp(5200)`. Never raw/harsh.

**Alien counter-hook / answer (anti-habituation, in EVERY chorus — not garnish):**
- `revenant_bell` rings the **F5 peak** and `cold_bell_larynx`/`vox_glottis` fragment answers over the **D-resolve** (upper register, wide-panned) — replaces Design 2's plain high echo.
- `cribra` alien ticks (stereo → `add_st`) accent the off-beats.
- `RESP = [("F6",28,2),("Eb6",30,2)]` optional high ghost over the resolve in the two biggest choruses only.

**Recurrence schedule (Rule 2: ≤8 bars, ≥60% coverage → this hits ~82%):**
| Section | Hook treatment |
|---|---|
| Cold open | full statement, clean, foreground, by **~0:04** |
| Chorus 1 | every 2 bars, base; revenant_bell on peak, cribra ticks |
| Verse 1 | every 2 bars as **quiet octave-down pluck-lead**; vox_glottis counter-hook answers |
| Chorus 2 | every 2 bars + RESP alien answer; brighter organ bed |
| Verse 2 | pluck + **variation** (apex A4→C5 once = bigger leap); ring_growl bed |
| **Frisson lift** | peak F5 **+15c lean + octave choir_pad double + shards shimmer** = the chill |
| **Big drop** | **octave-up lead + organ octave-down + war_horn 3rd-below harmony + bell shimmer**; second-wind variant at bar 56 |
| Verse 3 | base, layers pulled, groove+hook kept |
| Drop reprise | octave-up; final approach uses the **hoarded C#5→D5 (raised 7th, true V→i)** — see §5 |
| Outro | base; **final statement resolves HARD to D4, held** |

---

## 3. GROOVE — persistent, medium-syncopation, never absent (Rules 3 & 7)

Steps: 0=beat1, 4=beat2, 8=beat3, 12=beat4. New `groove_bar(bar, energy, density)` → DRUM + `kick_times`.

| Layer | Reuse fn | Pattern (steps) | Notes |
|---|---|---|---|
| **Kick** | `big_kick()` | base `[0,6,10]`; +`[14]` pickup in choruses; +`[3]` in the big drop only | Half-time syncopation sweet spot; pushes around the beat-3 snare. Feeds `kick_times`. |
| **Backbeat** | `snare()` | `[8]`; ghost `snare*0.4` at `[12]` in choruses/drop | The half-time neck-snap. |
| **Hats (pulse surrogate)** | new `hat()` | 8th `[0,2,4,6,8,10,12,14]`; 16ths for **part** of the bar in the drop; open-hat only occasional `[14]` | **Never drops out** — this is the "beat never gone" guarantee. |
| **Dark body** | `taiko(95/78)` | `[0,8]` low in mix (NOT the 10-hit gallop) | Weight without marching. |
| **Alien perc** | `cribra()` (→`add_st`) | sprinkled, incl. choruses | Habituation-resistant novelty; ≤~20%. |

**Bass** — new `bass_bar(bar, root, energy)` → SUB:
- **SUB** `sub808(SUBROOT[root], …)` on kick steps `[0,6,10]` → **kick-bass interlock**; tonic D1 sounds on bars 1 & 4 of every cycle (tonic present constantly).
- **REESE** new `reese()`: 3 detuned saws in octave 2 (D2/E♭2/C2), 8th-note rhythm, **LP 300–650 Hz with `pink_walk` filter wobble** (alien movement, not a sine LFO), `osat` grit. The driving dark bass; choruses + drop.
- **GRIT** `ring_growl()` low gain under the big drop only.

**Sidechain — 3-tier "breathing" (rewire `master()`):**
```
pump_times = [bt(b,beat) for b in GROOVE_BARS for beat in (0,1,2,3)]   # steady 1/4 pump
scB    = sc_env(n, kick_times, 0.80, rel=0.12)   # bass ↔ kick (tight interlock)
scPad  = sc_env(n, pump_times, 0.45, rel=0.20)   # MUS/CHOIR/PAL pump/breathe
scLead = sc_env(n, kick_times, 0.15, rel=0.10)   # hook barely ducks (stays forward)
dry = DRUM.dry + SUB.dry*scB + MUS.dry*scPad + CHOIR.dry*scPad + PAL.dry*scPad + LEAD.dry*scLead
```
`GROOVE_BARS` = all bars except the 1-bar pre-drop cut and the outro tail.

**THE NEVER-ABSENT RULE:** groove locked by **~0:07** and the beat is **never gone > 1 bar (1.7 s)**. The only gap is the single pre-drop kick-cut at bar 47 (1.7 s) — hats/sub keep the pulse even there. **No beatless section exists.** (This is the hard line against RESIDUA's Eye.)

---

## 4. FORM TABLE (84 bars; mesa floor + frequent spikes; 1 big drop + 1 kept frisson)

`BAR = 1.714 s`. Energy = % of peak RMS (floor stays HIGH).

| # | Section | Bars | Time | Energy | What plays / payoff |
|---|---|---|---|---|---|
| A | **COLD OPEN** | 0–3 | 0:00–0:07 | 65→80% | Hook CLEAN + foreground by **~0:04**; kick+hat+sub tease; groove locked by 0:07. Alien bed: `groundwater`+`mantle` low. |
| B | **CHORUS 1** | 4–11 | 0:07–0:20 | 100% | Full groove + reese + hook ×4; revenant_bell on peak, cribra ticks. **PAYOFF #1.** |
| C | **VERSE 1** | 12–19 | 0:20–0:34 | 70% | Subtract by layer (beat+bass+hook-pluck stay, floor ≥68%); `groundwater`/`psithura`/`vox_glottis` counter-hook. Build 18–19. |
| D | **CHORUS 2** | 20–27 | 0:34–0:48 | 100% | Full + RESP alien answer + brighter organ. `subdrop`+`braam` entry. **PAYOFF #2.** |
| E | **VERSE 2** | 28–35 | 0:48–1:02 | 72% | Darker: `ring_growl`/`metal_scrape`/`mantle`; hook-pluck **variation** (apex A4→C5). Build 34–35. |
| F | **FRISSON LIFT** | 36–43 | 1:02–1:15 | 105% | **THE kept frisson climax** (register/timbre lift): peak F5 **+15c + octave `choir_pad` double + `shards` shimmer**; groove KEPT. **PAYOFF #3 + CHILL.** |
| G | **PRE-DROP BUILD** | 44–47 | 1:15–1:21 | build | `riser`+`rev_swell`+`snare_roll` accel + filter open; pulse kept; **1-bar kick cut at 47 (1.7 s)** for impact. (≤8 s build.) |
| H | **THE BIG DROP** | 48–63 | 1:21–1:48 | **100% peak** | THE drop: full groove max (kick+snare+part-16th hats+taiko+reese+ring_growl grit); **octave-up hook + organ octave-down + war_horn harmony + bell shimmer**; `braam`+`subdrop`+`crash` on entry; **second-wind cut→slam at bar 56**. **PAYOFF #4.** |
| I | **VERSE 3 / COMEDOWN** | 64–71 | 1:48–2:02 | 74% | Layers pulled, groove+hook kept, space returns. Build 70–71. |
| J | **DROP REPRISE + CADENCE** | 72–79 | 2:02–2:15 | 96% | Big-drop material returns (shorter) → the **hoarded C#5→D5 raised-7th V→i** with A-major brass swell resolving to D. **PAYOFF #5 (end on a high).** |
| K | **OUTRO** | 80–83 | 2:15–2:28 | 70→0 | Drums thin over 2 bars → **final hook resolves HARD to D4, held**; `toll(D)`+`groundwater` sink+`pleura(caught)` tail; D→D loop. |

Payoffs at ~0:07 / 0:34 / 1:02 / 1:21 / 2:02 + in-verse builds → every **13–27 s** (Rule 4). Tension (builds) ≈ 10/84 bars ≈ **12%** → ≥75% gratified (Rule 5). **One big drop (H); one kept frisson climax (F); reprise is a return, not a bigger climax.**

---

## 5. NEW CODE (what to add — the load-bearing bits)

All band-limited, `osat`-guarded, `pink_walk`-modulated (never a sine LFO), ADSR sustain held.

```python
LEAD = Bus(TOTAL)

def lead(freq, dur, gain=0.6, bright=5200, detune=8, drive=1.12):   # bright FOREGROUND earworm voice
    n = int(dur*SR); f = vib(freq, n, rate=5.4, depth_cents=7, delay=0.16)
    out = sum(_additive(f*2**(d/1200.0), 40, 1.0) for d in (-detune,0,detune)) / 3
    out = 1.0*bp(out, 300, 1400) + 0.6*out                # formant presence
    env = adsr(n, 0.008, 0.06, 0.9, min(0.14, dur*0.3))   # fast attack, SUSTAIN HELD
    return lp(osat(out*env, drive), bright) * gain

def reese(name, dur, gain=0.5, cut=(300,650), drive=1.3):  # driving dark bass
    f = note(name); n = int(dur*SR); t = t_of(dur); saw = np.zeros(n)
    for d in (-11,0,11):
        fk = f*2**(d/1200.0); cph = 2*np.pi*fk*t
        for k in range(1,30):
            if fk*k > SR/2-200: break
            saw += (1.0/k)*np.sin(k*cph)
    saw /= 3; fc = pink_walk(n, cut[0], cut[1]); seg=12; out=np.zeros(n); w=n//seg
    for s in range(seg):
        sl = slice(s*w, (s+1)*w if s<seg-1 else n); out[sl] = lp(saw, float(np.median(fc[sl])))[sl]
    env = adsr(n, 0.006, 0.05, 0.95, min(0.08, dur*0.3))
    return osat(out*env, drive) * gain

def hat(gain=0.32, open_=False):                          # persistent pulse surrogate
    d = 0.18 if open_ else 0.05; t = t_of(d)
    return lp(hp(rng.standard_normal(len(t)), 7000) * np.exp(-t*(12 if open_ else 45)), 15000) * gain
```
Schedulers (sketch): `play_hook(bar, variant, octv, gain, cents_on_Eb=12)` writes HOOK to LEAD via `lead()` + quieter `chant_note()` doubler, rings `revenant_bell` on the F5 peak, `add_st`s `cribra` accents, and applies the +12c freq multiply to E♭ notes; `groove_bar(bar, energy, density)` writes §3 kit to DRUM/`kick_times`; `bass_bar(bar, root, energy)` writes `sub808` on `[0,6,10]` + `reese` 8ths. Build `GROOVE_BARS` and `pump_times` while scheduling. For §J only, `play_hook(..., cadence=True)` swaps the E♭5→D5 sigh for **C#5→D5** and adds an A-major `war_horn`/`brass` swell → D (the one hoarded true V→i).

---

## 6. WHAT TO REUSE from residua.py (ex-crusade2)
- **Instruments verbatim:** `big_kick, taiko, sub808, snare, crash, riser, snare_roll, subdrop, braam, rev_swell, anvil, gong, choir_stab, dark_whoosh, shards, thunder, organ_tone, war_horn, brass, toll, cluster, chant_note, chant` (+`CHANT_A/B/C` as sparse alien counter-texture only), `play_organ, play_sub, ostinato`.
- **Alien palette:** `revenant_bell, chorus_many, ring_growl, cribra, psithura, groundwater, mantle, stairwell, missing_room, cold_bell_larynx, pleura, metal_scrape, alien_zap, glitch` (+ newly-imported `vox_glottis`).
- **Infra:** `Bus/add/add_st`, `note/t_of/lp/hp/bp/adsr`, `pink_walk, osat, tilt, make_ir`, `sc_env`, the **entire `master()` chain** (dual reverb + 2.8–4.2 kHz de-harsh + −4.5 dB dark tilt + `lp 15.5k` + `osat` + tanh limiter + mono-below-30), `write_wav`.
- **Data:** `CYCLE_ROOT, CHORD, SUBROOT, VOWELS`, `bt()`.

## 7. WHAT TO CHANGE
- BPM 96→**140**; NBARS 72→**84**; recompute `BAR/BEAT/STEP/TOTAL`.
- Add `LEAD` bus + import `_additive, vib` (orch) and `vox_glottis` (thing).
- Add `lead()`, `reese()`, `hat()`; add `play_hook/groove_bar/bass_bar` schedulers; add `HOOK/RESP` data.
- **Replace the whole arrangement block** (crusade2 lines ~428–493) with §4's form.
- **Rewrite `loudness()`** to the §8 mesa.
- **Rewire `master()` sidechain** to the 3-tier scheme (§3) + add `LEAD.dry*scLead` to the dry sum + build `pump_times`.
- Ration cinematic accents: `braam`/`choir_stab`/`war_horn` allowed at the **big drop + reprise only** (not every chorus) — avoids trailer cliché.

## 8. WHAT TO CUT from RESIDUA (explicit)
- **`centerpiece()` / "The Eye"** (30 s beatless withheld middle) — **DELETED**. No beatless section anywhere; no −13 dB hole.
- **`creep_break()`** beat-removing interludes — **CUT**; verses keep the pulse.
- **`charge()` + `war_drums()`** 10-hit gallop marches — **NOT called**; replaced by half-time `groove_bar` (medium syncopation).
- **The withheld-tonic dogma** — **CUT**. Tonic D lands every 2 bars (hook resolve) + D1 sub constantly + hard D end + one true V→i.
- **Open-loop / 7-4 unresolved ending** — **CUT**; hard tonic resolve.
- **Long cathedral organ intro** — **CUT**; hook+groove by 0:07 (was bar 21).
- **Valley `loudness()`** (−17/−40 troughs) — **REPLACED** by mesa.
- **8-bar requiem fade** — shortened to 2-bar resolve + short tail.
- Alien demoted from **structural** (form/ending) to **surface** (timbre + the ♭2 leap + counter-hook accents), ≤~20% of events.

---

## 9. MIX / LOUDNESS automation (high flat floor — rewrite `loudness()`)
Mesa: sustained-section floor **≥ −5 dB of peak (~71%)**; peaks −2 to −2.5 dB (frisson, drop). No sustained section below −6 dB; only the cold-open ramp-in and final fade go lower. Breakpoints `(sec, dB)`:
```
pts = [(0,-8),(7,-4),(20,-5),(34,-3),(48,-5),(62,-2.5),   # frisson lift peak
       (75,-5),(82,-2),(96,-2.5),                          # big-drop plateau
       (110,-5),(123,-3),                                  # verse3 / reprise cadence
       (137,-4),(144,-8),(148,-40)]                        # outro resolve + fade
```
Keep `master()`'s de-harsh/tilt/`osat`/limiter unchanged. Fade-out only in the last ~4 s over the resolved D. Foreground order: **hook (LEAD) on top**, then kick+sub+backbeat, then pads/choir, palette furthest back.

## 10. QA targets (create `synth/qa.py`)
Analyze the rendered `residua.wav`; assert:
- **Onset density floor:** ≥ **4.0 onsets/s** in every 3 s window across bars 4–80 (excludes cold-open ramp + outro). Catches any accidental hole.
- **Beat continuity:** max percussive inter-onset gap ≤ **1.9 s** (≈1 bar) in bars 4–80; ≤ 4 s absolute anywhere except the final fade.
- **Hook-early:** a pitched onset in the **250–750 Hz** lead band before **t = 7.0 s**.
- **Section dynamic range (present but not extreme):** loudest/quietest sustained-section RMS ratio in **1.4×–2.5× (≈3–8 dB)**. Fail if <1.2× (flat/boring) or >3× (art-music valley).
- **Loudness floor:** min 4 s-window RMS in bars 4–80 ≥ **0.60 ×** peak-window RMS.
- **Spectral centroid:** global centroid **900–2200 Hz** (dark); no section centroid > **3000 Hz** (no bright/arcady section).
- **Harsh energy:** fraction of energy in **2.8–5 kHz < 4%** of total.
- **Tonic resolution:** last 3 s dominated by pitch-class **D** (spectral peak near 146.8/293.7 Hz).

## 11. Code-safety checklist (restated)
- `TOTAL` derived from `NBARS` (`NBARS=84; TOTAL=NBARS*BAR+4`).
- 4 ms declick already in `Bus.add` (applies when `len(sig) > 3*fd`) — keep short one-shots above that or they won't declick.
- **`osat` (2× oversampled tanh) on every new nonlinearity** (`lead`, `reese`); additive partials capped `f*k < SR/2 − 200`.
- **ADSR sustain held** on `lead()` so the F5 half-note peak actually sustains.
- **`pink_walk`, not a sine LFO**, for the reese filter movement (anti-arcade rule).
- **Microtonal lean via frequency multiply** — `note("Eb5")*2**(12/1200)`; `chant_note`/`lead` have no `cents` param.
- **`cribra()` returns stereo** → use `add_st`, never `add`.
- **Do NOT import `engine.py`** hook helpers — they are nested in `render()` and un-importable; the hook is built on `lead()` + `chant_note()`.
- Reuse the existing de-harsh/tilt/`lp 15.5k`/limiter master chain verbatim (guarantees "never harsh").
- New imports required: `_additive, vib` (orch), `vox_glottis` (thing).
