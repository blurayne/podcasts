# Production Plan — Podcast / Doku-Feature "Die Frau vor dem Recht"

Turn the transcript
`podcast.md` into one finished,
listenable **Doku-Feature MP3** (~35–40 min, two voices, no dialogue) generated
via the ElevenLabs API and assembled with `ffmpeg`.

This job is fully separate from the Hörspiel series (`out/scene1/`, owned by
another process). Everything here lives under `out/die-frau-vor-dem-recht/S01-01/podcast/`.

## Cast (voice_ids verified 2026-07-02)

| Rolle | Beschreibung im Skript | Stimme | voice_id |
|---|---|---|---|
| **STIMME 1** | Erzählung, roter Faden, ruhig/präzise, weiblich, mittleres Register | **Mila Winter – Narration (expressive & assured)** | `dCnu06FiOZma2KVNUoPZ` |
| **STIMME 2** | Quellen & Einordnung, dunkler/getragener, männlich | **Gerry – Composed and Strong** | `fehqjfT0R2fGKeUX2YeE` |

The two voices are clearly distinct (bright expressive female vs. composed
dark male). STIMME 2 carries all source quotes („…") and the „Einordnung:"
research notes.

## Model choice: `eleven_multilingual_v2`

Rationale — decided after a 4-sample A/B test (`out/die-frau-vor-dem-recht/S01-01/podcast/_modeltest/`, both
voices, one narration + one source-quote line, v2 vs v3):

- The transcript contains **no audio tags** (unlike the v3 Hörspiel), so v3's
  main advantage (tag-driven emotion) is irrelevant here.
- For 22k chars of continuous long-form narration, **v2 is more consistent and
  safer against audio-tag artifacts / hallucinated whispers** — exactly the
  brief's fallback guidance.
- Test durations were even and comparable (S1: v2 8.8s / v3 9.3s; S2: v2 16.6s
  / v3 15.9s), no runaway generation or dead air. v2's pacing was marginally
  tighter and steadier — the right trade for a 40-minute feature.
- Em-dashes (—) and German quotation marks („…") render as natural
  micro-pauses in v2 without being spoken.

Voice settings: default `stability=0.5, similarity_boost=0.8, speaker_boost`.
Source-quote / „Einordnung" segments for STIMME 2 are rendered with slightly
**higher stability (0.6)** so the "read aloud, slightly slower, footnote-like"
delivery stays steady.

## Parsing the transcript & cues

`scripts/s01e01_podcast.py` parses the markdown into an **ordered event list**:

- **Speaker segments**: a line `**STIMME 1:**` / `**STIMME 2:**` sets the
  active voice; the following non-empty, non-cue, non-heading paragraph(s)
  become spoken segments (one TTS stem per paragraph, so long acts stay
  chunked and idempotent). STIMME 1 → Mila, STIMME 2 → Gerry.
- **Cues** (bracketed, never spoken), parsed by prefix:
  - `[MUSIK: …]` → music event. `ausblenden` / `aus` / `ausklingen` =
    fade the current bed out; otherwise start/refresh the title-motif bed.
  - `[ATMO: …]` → ambient bed event (the prose after the colon is the SFX
    prompt). Runs ducked under following speech until the next act/atmo change.
  - `[PAUSE]` → ~0.8 s extra silence at that point.
- **Headings** (`#`, `##`), the front-matter block, `---` rules, the
  `[ENDE …]` marker and the whole `## PRODUKTIONSNOTIZEN` section are dropped.
- Markdown emphasis (`**`, `*`) is stripped from spoken text. German quote
  marks are kept (they read as natural pauses).

There are exactly **3 distinct [ATMO] cues** and the music is one recurring
**title motif** (Cold Open, Akt IV→V transition area, Finale) plus two short
transition stingers (`[MUSIK: kurzer Trenner]`, `[MUSIK: Übergang …]`). We
generate distinct beds per distinct prompt and reuse (skip-existing) elsewhere.

## Music / SFX approach (Eleven Music + SFX generation)

Per the Produktionsnotizen: **sparse** music, a recurring title motif, **no
music under source quotes**, atmo only at the 3 marked spots, dezent.

- **Music** (`el.music`, Eleven Music):
  - `title_motif` — dark sparse title motif, single instrument over a dark pad,
    solemn, no vocals. Used at Cold Open, and (faded) at Finale + closing.
  - `transition` — short neutral riser/trenner used for `[MUSIK: kurzer
    Trenner]` (Akt III→IV) and `[MUSIK: Übergang, heller werdend]` (Akt VI),
    lighter/rising, short.
- **SFX / ATMO** (`el.sfx`, loopable short beds, looped in ffmpeg to length):
  - `atmo_tower` — „Wind, ein Fluss, sehr fern ein Ruf" (Cold Open).
  - `atmo_thing` — „Feuer, entfernte Schmiede, Versammlungsgemurmel" (Akt II).
  - `atmo_sea` — „Meer, Möwen, Tauwerk, dann ein Hof, Vieh, Schritte auf Holz"
    (Akt IV).
  - Each generated at a fixed short duration (~10 s), then `-stream_loop`ed and
    ducked ~ -18 dB under the narration via `sidechaincompress`.

## Assembly pipeline (ffmpeg, `/usr/bin/ffmpeg`)

1. TTS every speaker paragraph → `out/die-frau-vor-dem-recht/S01-01/podcast/voices/NN_stimmeX_slug.mp3`
   (idempotent, `skip_existing`).
2. Generate the 3 atmo SFX → `out/die-frau-vor-dem-recht/S01-01/podcast/sfx/`, and the 2 music beds →
   `out/die-frau-vor-dem-recht/S01-01/podcast/music/`.
3. Build the **speech bus**: normalize each stem to 44.1k stereo, concatenate
   in transcript order with natural gaps (base ~0.45 s between paragraphs,
   larger at act boundaries, `[PAUSE]` adds ~0.8 s). Record each segment's start
   time so cues can be placed on the timeline.
4. **Atmo**: for each [ATMO] span, loop its bed across the covered speech,
   volume ~0.28, and duck it under the speech bus (`sidechaincompress`).
5. **Music**: place `title_motif` (faded in/out) at the Cold Open and again at
   the Finale/closing; place the short `transition` bed at the two trenner
   points. Music is faded and never overlaps a source-quote segment.
6. `amix` speech + atmo + music (normalize=0), then a single
   `loudnorm=I=-16:TP=-1.5:LRA=11` pass; export MP3 (libmp3lame `-q:a 2`).

Two phases like `s01e01_scene1.py`: `gen` (spend credits once) and `mix`
(ffmpeg only, re-runnable free). ffmpeg/ffprobe auto-picked, preferring
`/usr/bin/*`.

## Credit estimate

- Spoken text ≈ **22,356 chars** ≈ 22,356 credits (multilingual_v2 = 1 cr/char).
- SFX: 3 beds at fixed short duration — a few hundred credits total.
- Music: 2 beds (Eleven Music, cost varies) — order of a few hundred to ~1k.
- Model A/B test already spent: ~700 chars.
- **Total ≈ 23–24k credits.** Balance before: **131,877** (Creator, 132,072
  limit). Comfortable headroom even with the sibling job running. Everything
  uses `--skip-existing`, so re-runs cost nothing.

## Output

- Stems: `out/die-frau-vor-dem-recht/S01-01/podcast/voices/`, `out/die-frau-vor-dem-recht/S01-01/podcast/sfx/`, `out/die-frau-vor-dem-recht/S01-01/podcast/music/`.
- Work files: `out/die-frau-vor-dem-recht/S01-01/podcast/work/`.
- **Final: `out/die-frau-vor-dem-recht/S01-01/podcast/podcast.mp3`.**
