# Episode 2 Production Plan — „Der Parallelbogen"

Produce, from `series/die-frau-vor-dem-recht/S01-02/`, in the same style as Episode 1:

1. **4 standalone Hörspiele** (Islam scenes 1–4) — full cast + SFX + music + `eleven_v3`,
   in **short form**: the dramatized play **+ a strongly-condensed tl;dr** of the
   „Historische Einordnung" (not the full analysis).
2. **1 podcast feature** „Der Parallelbogen" — two-voice Doku-Feature (like Ep. 1's
   podcast) that **embeds the 4 Hörspiel plays** at the `>>> HÖRSPIEL-EINLAGE` marks.

Interpretation of your note *„für den podcast bitte die hörspiele in kurzform (nur das
hörspiel, betrachtung der quellen stark verkürzt in tl;dr)"*: the Hörspiele are the
**plays only** inside the podcast; the source-examination is delivered as a short
**tl;dr** in the standalone versions (and via the feature's own STIMME-2 „Einordnung"
in the podcast). Per the scripts' Produktionsnotizen, the full Einordnungen are **not**
part of the feature.

## Cast (studio-quality `professional` voices, rendered v3)

**Feature / continuity (same as Ep. 1):**
- **STIMME 1 / ERZÄHLSTIMME** = Mila Winter `dCnu06FiOZma2KVNUoPZ` (female narrator)
- **STIMME 2 / Quellen** = Wolf Spencer `2OcnG4mH3jIMtWz3vKus` (male)

**Scene 1 — Die Kauffrau von Mekka**
| Role | Voice |
|---|---|
| KHADIDSCHA (kauffrau, ~40, composed) | Lea `7eVMgwCnXydb3CikjV7a` |
| NAFISA (confidante, playful) | Leonie `uvysWDLbKpA4XvpD3GI6` |
| MAISARA (servant, m) | Otto `FTNCalFNG5bRnkkaP5Ug` |

**Scene 2 — Die Lehrerin der Männer**
| KARIMA (aged scholar, unbending) | Amira `FOfJ2PMgU6HOGbNYnzto` |
| AL-CHATIB (scholar ~55) | Gerry `fehqjfT0R2fGKeUX2YeE` |
| JUNGER GELEHRTER (impatient, m) | Albert `f2yUVfK5jdm78zlpcZ8C` |

**Scene 3 — Vor dem Kadi**
| FATMA (widow ~35, determined) | Ellen `BIvP0GN1cAtSRTxNHnWS` |
| KADI (judge, sachlich) | Andreas `ZgTblco1F8U3zN77c5Rj` |
| MEHMED (brother, agitated) | Otto `FTNCalFNG5bRnkkaP5Ug` |
| SCHREIBER (murmuring scribe) | Jorin `wloRHjPaKZv3ucH7TQOT` |

**Scene 4 — Der Schleier, dreimal** (triptych)
| MARJAM young (1936, ~20) | Lana Weiss `rAmra0SCIYOxYmRNDSm3` |
| MARJAM old (grandmother) | Amira `FOfJ2PMgU6HOGbNYnzto` |
| GENDARM (1936, official) | Gerry `fehqjfT0R2fGKeUX2YeE` |
| SIMIN (1979, ~30) | Ellen `BIvP0GN1cAtSRTxNHnWS` |
| NILUFAR (2022, ~20) | Leonie `uvysWDLbKpA4XvpD3GI6` |
| ZEITANSAGE (dry time-stamps) | Wolf Spencer `2OcnG4mH3jIMtWz3vKus` |

v3 audio tags map the stage directions (`[whispers]`, `[shouting]`, `[sarcastic]`,
`[angry]`, `[sighs]`, `[calm]`) as in Episode 1.

## Standalone Hörspiele (short form)
Per scene: intro music → play (dialogue + ATMO/SFX + reverb where apt) → **~30–45s
tl;dr Einordnung** (narrated by STIMME 1, condensing the [belegt]/[plausibel]/
[umstritten] verdicts) → outro music. Output `out/die-frau-vor-dem-recht/S01-02/scene{1..4}/…mp3` (+ `_audiobook.mp3` + import `.txt`).

## Podcast „Der Parallelbogen"
Two-voice feature (Mila + Wolf), parsing the transcript like Ep. 1's podcast, **plus**:
- `>>> HÖRSPIEL-EINLAGE N` → splice in that scene's **play** audio (reuse the play stem
  from the standalone build), with a short music/atmo hand-off.
- **Scene 5** („Die Verheiratung der Tochter — 2026") has **no script** (it lives in the
  LaTeX study PDF, ch. 12) → its slot is **omitted**; STIMME 1's surrounding moderation
  is kept so the argument still lands. *(Flagged — say the word and I'll extract/author it.)*
- Music: reuse Ep. 1 title motif **+ an added oud/ney color** (per Produktionsnotizen).
- Strip `\emph{…}` LaTeX artifacts from the transcript text.
- Output `out/die-frau-vor-dem-recht/S01-02/podcast/podcast.mp3`.

## Engineering
- Extend `scripts/hoerspiel.py`: allow a per-scene `analysis_override` (explicit tl;dr
  paragraphs) and a free-standing source (not `hoerspiele.md`). Add `scripts/s01e02_scene{1..4}.py` specs.
- New `scripts/s01e02_podcast.py` (from `s01e01_podcast.py`): new SRC + voices,
  `>>>`-marker splicing of play audio, `\emph` stripping, oud/ney music prompt.
- Idempotent (`skip_existing`); auto-picked ffmpeg; music already at −10%.

## Credit estimate (82,309 remaining)
~8k (4 plays) + ~2k (tl;dr) + ~12–14k (feature narration) + SFX/music ≈ **~25–28k**. Fits.

## Order
Produce the 4 standalone Hörspiele first (reviewable), then assemble the podcast that
embeds their plays. Document the pipeline in `AGENTS.md` when done.
