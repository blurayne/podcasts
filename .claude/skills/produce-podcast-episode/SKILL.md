---
name: produce-podcast-episode
description: Operator guide for producing a podcast or Hörspiel episode from a YAML spec + markdown transcript via scripts/produce.py. Triggers on: create podcast episode, produce Hörspiel, render audio, write YAML spec, gen mix all, produce.py.
---

# Producing a podcast or Hörspiel episode

**Read `SPEC.md` first.** It is the single authoritative contract for the YAML schema, the engine CLI (`gen`/`mix`/`all`/`book`/`parse`), stem naming, caching rules, and the credit-safe migration requirements. This skill summarizes the workflow and gives quick-reference examples; `SPEC.md` governs every detail.

> **⚠ Mandatory cost gate.** Before any `gen` or `all` run, ALWAYS calculate the episode's full cost — credits **and** approximate USD (Creator plan ≈ $22 / 100,000 credits ≈ $0.00022/credit) — present the itemized breakdown to the user, and get their explicit confirmation. Never start a paid generation without this. Details in Step 4.

---

## End-to-end workflow (mirrors SPEC §8)

**Step 1 — Transcript.** Write or obtain the episode transcript as a `.md` file. Place it under `series/<series>/<episode>/` (podcast: `podcast.md`; Hörspiel scene: `szene-N.md` or `hoerspiele.md`). Wrap the parseable body in exactly one `<!-- start -->` / `<!-- end -->` HTML-comment pair — the engine only reads lines between those markers and errors if they are absent.

**Step 2 — YAML spec.** Write the per-episode YAML spec file (e.g. `podcast.yaml` or `scene1.yaml`) next to the transcript. The spec holds only production config — voices, model, SFX/music prompts, cue_rules, gaps, output path. The transcript holds all dialogue. See SPEC §4 for the full schema; see the condensed examples below.

**Step 3 — Sanity-check without spending.** Run `scripts/produce.py <spec.yaml> parse`. This prints the parsed event list, segment count, and character count. No API calls are made. Use this to confirm the parse is correct, that speaker names match, and that cue rules fire where expected.

**Step 4 — Calculate cost and get confirmation (MANDATORY).** Always compute the episode's full cost before starting `gen`, and ask the user to confirm. (a) Run `scripts/produce.py <spec> parse` to get the exact TTS character count. (b) Run `scripts/el.py balance` for the remaining pool. (c) Estimate: TTS = 1 credit/char; SFX = 40 credits/second (fixed `dur`) or 200/generation (`auto`); music ≈ 900 credits/minute. (d) Present an **itemized breakdown in credits AND approximate USD** (Creator plan ≈ $22 / 100,000 credits ≈ $0.00022/credit — label it an estimate), plus the resulting balance after the spend. (e) Get explicit user approval. **Never run `gen` or `all` on a spec without existing stems until the user confirms the spend.**

**Measured benchmark (eleven_v3, 2026-07 — use for estimates).** The real rate on this account is **≈ 0.55 credits/char** (not the nominal 1.0), i.e. **~$0.00012/char**. A full 138-segment / 18.5k-char / ~26-min episode cost **~10,200 credits (~$2.24)** and rendered in **~4.8 min** end-to-end (gen + mix) → **~64 chars/sec, ~29 segments/min, ~5× realtime** (mix adds ~30–60 s; SFX/music are one-off adds). Predict a new episode: **cost ≈ chars × 0.55 cr**, **time ≈ chars ÷ 64 s + ~1 min**.

**⚠ Balance lag — leave headroom.** The `el.py balance` endpoint LAGS real spend: a freshly-read balance can over-report available credits because the previous render's cost hasn't fully registered. Do NOT plan to spend more than ~70% of a just-read balance in one batch, and **render big batches sequentially** (let the balance settle between episodes) rather than in parallel — two ~$4 features nearly overran a read-$9.88 balance and one stopped at `quota_exceeded` mid-gen because the prior render's cost was still settling. A `quota_exceeded` stop is safe/idempotent: top up credits and re-run `all` (cached stems skip; only the remainder + mix costs).

**Step 5 — Generate and mix.** Run `scripts/produce.py <spec.yaml> gen` to call the ElevenLabs API (idempotent — `skip_existing` everywhere). Then `scripts/produce.py <spec.yaml> mix` to assemble the final MP3 with ffmpeg (free, always re-runnable). Or use `all` to do both in one shot. For Hörspiel, `book` renders the audiobook variant + `.txt`.

```bash
# New episode — full run (requires user confirmation before this step):
scripts/produce.py series/quarks-for-kids/wusl-gusl.yaml gen
scripts/produce.py series/quarks-for-kids/wusl-gusl.yaml mix

# Or in one shot:
scripts/produce.py series/quarks-for-kids/wusl-gusl.yaml all
```

---

## New episode vs. re-mixing an existing one

**New episode (no stems exist):** follow all five steps above. `gen` will spend credits; confirm the estimate with the user before running it.

**Re-mixing an existing episode (stems cached under `out/`):** skip `gen` entirely. Run only `parse` (to verify the spec) and then `mix` — this is free and safe to repeat as many times as needed. Never delete or rename cached stems; a single changed character in the spoken text changes the slug and orphans the cached file.

**Migration from a legacy per-episode script:** write the YAML spec, verify with `parse` that segment count and per-segment text exactly match the legacy script's output, then run only `mix`. Delete the legacy script only after parity is confirmed. See SPEC §7 for the exact rules.

---

## Minimal `kind: podcast` YAML example

```yaml
slug:  quarks-for-kids/wusl-gusl       # output dir = out/<slug>/
kind:  podcast
title: "Wusl Gusl — Schrumpfomat 3000"

# Default model is eleven_v3. Use eleven_multilingual_v2 only when a voice
# is specifically tuned for it (e.g. Wusl Gusl character voice).
model: eleven_v3

speakers:
  WUSL:
    voice_id:    xOrwxaQJaTlyIgWk33GY
    speaker_key: woozle                # used in stem filename — copy verbatim from legacy if migrating
    stability:   0.05
    similarity:  0.05
    style:       0.70
    speed:       1.08
    speaker_boost: true
  CO1:
    voice_id:    rDBaN5ZF8ukjsiAjsmmU
    speaker_key: co1
    stability:   0.5
    similarity:  0.8

audio_tags:                            # German stage direction → v3 inline tag (only used with eleven_v3)
  lacht:    "[laughs]"
  flüstert: "[whispers]"
  ruhig:    "[calm]"
  leiser:   "[softly]"
  rechnet:  ""                         # empty string = strip this cue entirely

sfx:
  pling: { prompt: "bright short metallic ping, no reverb tail", dur: 2 }

music:
  title_motif: { prompt: "playful kids-science theme, no vocals, sense of wonder", ms: 10000 }
  bed:         { prompt: "calm ambient science background, gentle low synth hum, loopable, no melody", ms: 32000 }

cue_rules:
  - { keywords: ["pling", "ton-akzent"],            sfx: pling }
  - { keywords: ["sirren"],                          music: title_motif, action: intro }
  - { keywords: ["ausblenden"],                      action: outro }
  - { keywords: ["kurz hoch"],                       music: title_motif, action: stinger }
  - { keywords: ["sanfte musik"],                    action: bed_on }

gaps:
  base:     0.55
  switch:   0.90
  sfx_tail: 0.35
  act:      1.60
  pause:    0.80

output:
  final: podcast.mp3
  loudnorm: "I=-16:TP=-1.5:LRA=11"
```

---

## Minimal `kind: hoerspiel` YAML example

```yaml
slug:  die-frau-vor-dem-recht/S01-02/scene1
kind:  hoerspiel
title: "Der Parallelbogen — Szene 1"
model: eleven_v3

speakers:
  MAISARA:
    voice_id:    <voice_id>
    speaker_key: maisara
    stability:   0.45
    similarity:  0.85
  SPRECHER:
    voice_id:    <voice_id>
    speaker_key: sprecher
    stability:   0.55
    similarity:  0.80

sfx:
  atmo_base: { prompt: "bazaar ambience, distant crowd murmur, light wind", auto: true }

gaps:
  base:  0.55
  switch: 0.90

output:
  final: scene1.mp3
  loudnorm: "I=-16:TP=-1.5:LRA=11"
  audiobook_loudnorm: "I=-19:TP=-3:LRA=11"

hoerspiel:
  name: scene1
  narrator_role: SPRECHER
  narr_heraus: "Wie realistisch ist diese Szene? Eine kurze Einordnung."
  bed_sfx: atmo_base
  reverb_roles: []
  analysis_list:
    - "Der Kern ist mehrfach belegt — die Quellen bestätigen ..."
  display:
    SPRECHER: "ERZÄHLER"
  drama:
    - { id: "00_narr_in", who: SPRECHER, gap: 0.0, text: "Mekka, dreißig Jahre vor der Hidschra." }
    - { cue: atmo_base, gain: 0.8 }
    - { id: "01_maisara", who: MAISARA, gap: 0.6, text: "Herrin — die Ballen sind verladen." }
```

---

## Model selection

**Default: `eleven_v3`.** This is the required model for all new productions. It supports inline audio-tag acting, which is the primary expressiveness tool. Do not omit the model field — set it explicitly in every spec.

**`eleven_multilingual_v2`:** use only when a specific voice is tuned for this model (e.g. the Wusl Gusl character voice `xOrwxaQJaTlyIgWk33GY`, which is trained on v2). When this model is active, all inline `[...]` cues are automatically stripped; expressiveness must come from voice `stability`/`style`/`speed` settings alone.

**Studio-quality voices only.** Cast only voices with `category: professional` (ElevenLabs "professionally recorded"). Never cast `premade` or low-fidelity voices. Check category with `python3 scripts/el.py voices` and inspect the voice detail if unsure. See `VOICES.md` for saved voice IDs and their known settings.

---

## Voice settings and IDs

Voice IDs come from `python3 scripts/el.py voices` (lists all account voices with their IDs) or from `VOICES.md` (this project's saved cast). The relevant voice settings under each speaker in the YAML:

- **`stability`** (0–1): lower = more expressive/varied; higher = more consistent/monotone. Kids' characters and high-energy hosts typically use 0.05–0.15; narrators 0.45–0.60.
- **`similarity`** (0–1): how closely the output resembles the reference recording. 0.8 is the default; lower values allow more tonal variation.
- **`style`** (0–1): style exaggeration (v3 only). Omit if not needed; high values (0.7) add strong emotional colouring.
- **`speed`** (0.5–2.0): playback rate relative to the voice's natural tempo. Omit to use the API default.
- **`speaker_boost`** (bool, default true): ElevenLabs speaker boost flag.

---

## Cue mapping (standalone cue lines → events)

A transcript line that is *only* a backtick-wrapped cue — e.g. `` `[Fanfare]` `` — becomes an event, not spoken text. The engine tests each `cue_rules` entry in order; the first entry whose **all** listed `keywords` appear (lowercased substring) in the cue text fires. Unmatched cues are silently ignored.

```yaml
cue_rules:
  - { keywords: ["pling"],         sfx: pling }                          # inline SFX: inserts the sound at this point
  - { keywords: ["fanfare"],       music: title_motif, action: intro }   # start title motif + bed
  - { keywords: ["ausblenden"],    action: outro }                        # motif reprise + fade bed out
  - { keywords: ["sanfte musik"],  action: bed_on }                      # (re)start the ambient bed quietly
  - { keywords: ["stinger"],       music: transition, action: stinger }  # one-shot transition
```

Supported `action` values: `intro` (play title motif, start ambient bed), `outro` (play title motif, fade bed out), `bed_on` (start or resume named bed), `stinger` (one-shot transition), or omit `action` and use `sfx:` alone for an inline sound effect placed at that position in the speech bus.

**Atmosphere looping — keep it natural.** Do not tight-loop a short sound (< ~3 s) as an ambient bed: repeating it back-to-back a few times sounds obviously mechanical. Prefer a longer generated bed (e.g. a 30 s loopable pad), or scatter the short sound across the span with **randomized silence gaps** between repeats so it feels natural. (Engine note: for continuous beds, generate a longer source; reserve short one-shots for punctual SFX rather than repeated atmosphere.)

---

## Credit and cache discipline (SPEC §6.1, §7)

`skip_existing=True` is passed to every `el.tts` / `el.sfx` / `el.music` call in the engine. Any output file >2 KB is treated as done and skipped. This means `gen` is fully idempotent — interrupted runs pick up where they left off and **re-runs never re-spend credits**.

Never regenerate a produced episode. Every episode in `out/` already has cached stems; only `mix` (free) is needed to adjust the final master. Do not delete, rename, or move cached stems — stem filename slugs are computed from the spoken text, and a single changed character produces a different filename, orphaning the cached audio.

The `mix` phase writes ffmpeg intermediates to `out/<slug>/work/` as **FLAC** (lossless, ~50% smaller than WAV) and writes the final master as high-quality MP3 (`libmp3lame -q:a 2`, ~190 kbps VBR). Never use WAV for intermediates unless a specific filter requires uncompressed PCM.

Check the shared credit pool before any `gen` run: `python3 scripts/el.py balance`. TTS, SFX, and music all draw from the same balance. Alert the user if credits are running low.

---

## ffmpeg auto-pick and uv shebang

The engine auto-selects the first working ffmpeg binary from: `$FFMPEG_BIN` env var → `PATH` → `/usr/bin/ffmpeg`. The mise-managed symlink may be broken (missing shared libs); the system binary at `/usr/bin/ffmpeg` (v4.4.2) is always the fallback. No manual configuration is needed.

All scripts in `scripts/` use the uv shebang `#!/usr/bin/env -S uv run --script` (never `#!/usr/bin/env python3`). Third-party dependencies (e.g. `pyyaml` in `produce.py`) are declared via PEP 723 inline metadata directly in the script; uv provisions an ephemeral cached environment automatically. Run scripts as `scripts/produce.py <args>` or `uv run --script scripts/produce.py <args>`.

---

## Quick reference: `produce.py` commands

| Command | What it does | Spends credits? |
|---|---|---|
| `parse` | Print parsed event list + segment/char counts | No |
| `gen` | TTS all speech segments; generate SFX and music | Yes (idempotent) |
| `mix` | ffmpeg assembly → final MP3 | No |
| `all` | `gen` + `mix` (+ `book` for hoerspiel) | Yes (idempotent) |
| `book` | Hoerspiel only: audiobook variant + `.txt` | No |
