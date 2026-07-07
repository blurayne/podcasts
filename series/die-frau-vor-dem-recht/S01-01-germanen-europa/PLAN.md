# Production Plan — "Die Frau vor dem Recht" Hörspiel series

Turn `hoerspiele.md` into **three produced audio dramas** (Hörspiele) with distinct
character voices, atmosphere/sound effects, and intro/outro music — all generated
via the ElevenLabs API and assembled with `ffmpeg`.

## Approved decisions (2026-07-02)

| Decision | Choice |
|---|---|
| **Scope** | Full analysis narrated — dramatized scene **+** the "Historische Einordnung" as a spoken epilogue |
| **TTS model** | `eleven_v3` (expressive; audio-tag emotion for the stage directions) |
| **Music** | Eleven Music — intro **+** outro bed per scene |
| **Order** | Scene 1 first → **user review** → Scenes 2 & 3 |

**Voice policy:** cast **only studio-quality voices** (ElevenLabs `category:
professional`) and render with **`eleven_v3`**. No `premade`/low-fidelity voices.

## Cast (voices)

The narrator **SPRECHER/IN = Apollo (Documentary & TV)** is the single continuous
voice across all three scenes. All voices are German-native voices already on the
account. Casting is provisional and may be swapped after the Scene 1 preview.

**Scene 1 — Das Thing (rechtsrheinische Germanen, ~90 n. Chr.)**
| Role | Voice | Note |
|---|---|---|
| SPRECHER/IN | Apollo – Documentary & TV | doc framing + narrated analysis |
| SEGIMER (princeps, ~45) | Gerry – Composed & Strong (rhine franconian) | dignified leader |
| DER PRIESTER | Andreas – Pleasant German | grave authority |
| FOLKWIN (young, hot-headed) | Otto | pushed hot via v3 tags |
| WALUBURG (seeress) | Ellen – Serious, Direct + **reverb in post** | speaks "from a distance" |
| SWANHILD (in-married wife) | Leonie | careful, firm |
| STIMMEN DER VERSAMMLUNG | *SFX crowd, not TTS* | murmur / spear-clash roar |

**Scene 2 — Die Verheiratung (fränkisch-karolingisch, frühes 9. Jh.)**
| Role | Voice |
|---|---|
| SPRECHER/IN | Apollo |
| HAIMO (Grundbesitzer, Muntwalt) | Otto |
| ADELHEID (wife / mother) | Leonie |

**Scene 3 — Die Frau, die zur Waffe greift (Island, ~980)**
| Role | Voice |
|---|---|
| SPRECHER/IN | Apollo |
| THORGERD (húsfreyja, ~35) | Ellen |
| ERSTER DIEB | Bartholomeus Bösewicht – Grim & Gruesome |
| GRIM (old servant) | Andreas (aged via v3) |

## Production pipeline (per scene)

1. **Parse** the scene from `hoerspiele.md` into an ordered script of segments:
   `narration`, `dialogue{speaker, text, emotion}`, `cue{sfx description}`,
   plus the `analysis` paragraphs for the narrated epilogue.
2. **Map stage directions → v3 audio tags** (see table below); strip the raw
   parenthetical directions from spoken text.
3. **TTS** each narration/dialogue segment → per-line MP3 stems in `voices/`.
4. **SFX** atmosphere beds via `POST /v1/sound-generation` → `sfx/`
   (AI-duration = 200 cr flat for long beds; fixed short durations for stingers).
5. **Music** intro + outro via `POST /v1/music` → `music/`.
6. **Assemble in ffmpeg**: dialogue on a timeline with natural pauses; atmos bed
   ducked under speech (sidechain/volume automation); SFX placed at cue points;
   reverb on Waluburg; music at the intro/outro transitions; loudness-normalized
   (`loudnorm`, target ≈ -16 LUFS); export `sceneN_<slug>.mp3`.
7. **QA**: check durations, listen, regenerate any weak line.

## Stage-direction → v3 audio-tag mapping

| German direction | v3 tag / technique |
|---|---|
| (laut) | `[shouting]` |
| (leiser, unsicher) | `[hesitant]` / `[whispers]` |
| (ruhig, mit Autorität) | `[calm]` |
| (höhnisch) | `[sarcastic]` / `[mocking]` |
| (nach einer Pause) | `…` ellipsis / short silence in edit |
| (erschüttert) | `[shaken]` |
| crowd grollen / raunen | SFX, not TTS |

## Credit budget — 132,072 credits available (Creator tier, upgraded 2026-07-02)

| Scene | Drama | Analysis | SFX+Music | **Total** |
|---|---|---|---|---|
| **Scene 1** | 2,234 | 3,381 | ~1,590 | **~7,205** |
| Scene 2 | 2,127 | 3,338 | ~1,590 | ~7,055 |
| Scene 3 | 1,307 | 8,009 | ~1,590 | ~10,906 |
| Gesamtbewertung (optional closing) | — | 3,019 | — | ~3,019 |

After the upgrade to **Creator (132,072 credits)** all three scenes (~25,000
credits combined incl. music/SFX) fit comfortably in one cycle. We still produce
**Scene 1 first for review**, then Scenes 2 & 3.

## Output structure

```
out/
  scene1/
    voices/   # per-line TTS stems
    sfx/      # atmosphere + effect beds
    music/    # intro / outro
    scene1.mp3   # final mixed master
```

## Risks / fallbacks

- **v3 determinism** — if a line renders poorly, regenerate; fall back to
  `eleven_multilingual_v2` for stubborn lines.
- **v3 audio tags in German** — verify tags aren't spoken aloud; drop tag if so.
- **SFX auto-duration** caps ~22 s — loop/extend beds in ffmpeg for longer scenes.
- **Music credit cost varies by plan** — confirm the pre-generation credit
  estimate before committing each music generation.

## Execution phases

- **Phase 1 (now):** Produce Scene 1 → deliver `scene1.mp3` for review.
- **Phase 2 (after review + quota reset):** Produce Scene 2.
- **Phase 3:** Produce Scene 3 (+ optional narrated Gesamtbewertung closing).
- **After building:** document the exact working pipeline in `AGENTS.md`.
