# SPEC — YAML-driven podcast/Hörspiel production engine

Authoritative spec for the generic audio-production engine and its per-episode
YAML specs. **Skills and agents MUST read this file before planning or creating
an episode.** It is the single source of truth for the schema, the engine CLI,
script conventions, and the credit-safe migration rules.

Related: [`AGENTS.md`](AGENTS.md) (standing conventions), [`docs/API-CLI.md`](docs/API-CLI.md)
(the `el` ElevenLabs CLI), the skill `.claude/skills/produce-podcast-episode/`.

---

## 1. What the engine is

One generic engine — **`scripts/produce.py`** — renders a finished MP3 from:

- a **markdown transcript** (the human-readable play/feature; dialogue lives here), **plus**
- a per-episode **YAML spec** (all production knobs: voices, model, SFX/music
  prompts, cue rules, gaps, output).

It replaces the old per-episode Python scripts. Invocation:

```bash
scripts/produce.py <spec.yaml> gen        # spend credits: TTS + SFX + music (idempotent)
scripts/produce.py <spec.yaml> mix        # ffmpeg assembly only — free, re-runnable
scripts/produce.py <spec.yaml> all        # gen + mix (+ book for hoerspiel)
scripts/produce.py <spec.yaml> book       # hoerspiel only: audiobook render + .txt
scripts/produce.py <spec.yaml> parse      # debug: print the parsed event list, no API calls
```

`hoerspiel.py` is **kept as a shared library**; `produce.py` builds a
`hoerspiel.Scene` from a `kind: hoerspiel` spec and delegates to it.

---

## 2. Script conventions (apply to every script in `scripts/`)

- **uv shebang, always:** first line is exactly
  ```python
  #!/usr/bin/env -S uv run --script
  ```
  Scripts are executable (`chmod +x`) and run as `scripts/foo.py …` or
  `uv run --script scripts/foo.py …`. Do **not** use `#!/usr/bin/env python3`.
- **Dependencies via PEP 723 inline metadata.** If a script needs a third-party
  package, declare it in a metadata block right under the shebang; `uv` provisions
  an ephemeral, cached env automatically. Example (`produce.py`):
  ```python
  #!/usr/bin/env -S uv run --script
  # /// script
  # requires-python = ">=3.12"
  # dependencies = ["pyyaml"]
  # ///
  ```
  Stdlib-only scripts (e.g. `el.py`) still get the shebang but need only
  `requires-python` (or no metadata block at all).
- **Import `el` for all ElevenLabs calls.** Never hand-roll HTTP. Sibling import:
  `sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import el`.
- **ffmpeg auto-pick:** choose the first working binary from
  `env FFMPEG_BIN` → `PATH` → `/usr/bin/ffmpeg` (same helper as the existing scripts).
- **Idempotency:** every generator call passes `skip_existing=True`. Re-runs must
  never re-spend credits.

---

## 3. Transcript parse window — `<!-- start -->` / `<!-- end -->`

The engine parses **only** the markdown between these two HTML-comment markers:

```markdown
<!-- start -->
## 0 · INTRO
**SPRECHER:** …
…
<!-- end -->
```

- `<!-- start -->` — parsing begins on the **line after** this marker.
- `<!-- end -->` — parsing stops on the **line before** this marker.
- Exactly one of each per transcript. If markers are absent the engine errors
  (no silent whole-file parse). This replaces the old `body_start`/`body_end`
  line-prefix matching.

---

## 4. YAML schema

Common fields first; then podcast-only and hoerspiel-only sections. Unknown
fields are an error (typo protection). All paths are repo-root-relative.

### 4.1 Common

```yaml
slug:  quarks-for-kids/wusl-gusl    # REQUIRED. output dir = out/<slug>/
kind:  podcast                      # REQUIRED. "podcast" | "hoerspiel"
title: "Wusl Gusl — Schrumpfomat 3000"       # REQUIRED. human label
model: eleven_multilingual_v2       # OPTIONAL. default: eleven_v3

speakers:                           # REQUIRED. role name (as in transcript) → voice
  WUSL:
    voice_id:   xOrwxaQJaTlyIgWk33GY   # REQUIRED
    speaker_key: woozle                # REQUIRED. used in stem filename — see §6
    stability:  0.05                   # OPTIONAL (default 0.5)
    similarity: 0.05                   # OPTIONAL (default 0.8)
    style:      0.70                   # OPTIONAL (omit → not sent to API)
    speed:      1.08                   # OPTIONAL (omit → not sent to API)
    speaker_boost: true                # OPTIONAL (default true)
    reverb:     false                  # OPTIONAL (hoerspiel; default false)

audio_tags:                         # OPTIONAL. used ONLY when model starts "eleven_v3".
  lacht:    "[laughs]"              # German inline stage direction → v3 tag
  flüstert: "[whispers]"            # value "" = strip that cue
  ruhig:    "[calm]"

sfx:                                # OPTIONAL. key → generation spec
  pling:  { prompt: "bright short metallic ping, no reverb tail", dur: 2 }
  atmo:   { prompt: "bazaar ambience …", auto: true }   # auto → AI duration (flat 200 cr)

music:                              # OPTIONAL. key → generation spec
  title_motif: { prompt: "playful kids-science theme, no vocals", ms: 8000 }

music_gain: 1.0                     # OPTIONAL, default 1.0. Mix-time multiplier applied to
                                    # EVERY music layer (ambient bed, underscore, title motif,
                                    # stinger) uniformly; speech is untouched. 0.8 = music 20%
                                    # quieter, 0.5 = half, 1.2 = 20% louder. Free to change +
                                    # re-mix (no re-gen). Absent = engine defaults unchanged.

gaps:                               # OPTIONAL. seconds. defaults shown
  base:     0.55                    # same speaker, consecutive lines
  switch:   0.90                    # speaker change
  sfx_tail: 0.35                    # after an inline sfx
  act:      1.60                    # at act/section boundaries (podcast)
  pause:    0.80                    # explicit [PAUSE] cue

output:
  final: podcast.mp3                # REQUIRED. filename under out/<slug>/
  loudnorm: "I=-16:TP=-1.5:LRA=11"  # OPTIONAL. default shown
```

### 4.2 Inline cue handling (model-driven)

Each spoken segment may contain inline `` `[stage direction]` `` cues. Handling
is chosen automatically from `model`:

- `model` starts with **`eleven_v3`** → replace each `` `[key]` `` with
  `audio_tags[key]` (unknown key → stripped).
- any other model (e.g. **`eleven_multilingual_v2`**) → **strip all** inline
  `` `[...]` `` cues (no audio tags).

**Ordering rule (critical for cache reuse):** apply inline transformation **first**, then compute the filename slug from the resulting text. This reproduces existing stem names (§6).

**Built-in TTS normalization (`_normalize_tts`, always on):** the final spoken text also passes through a punctuation normalizer before it is sent to ElevenLabs. It maps the ellipsis `…` (U+2026) → `.` and cleans up doubled periods / spaces-before-punctuation / leading dots. Reason (measured): `…` makes `eleven_multilingual_v2` insert a long dead-air gap that a low-stability voice fills with breaths/artifacts; a period is a clean short beat. The em-dash `—` measures clean and is left untouched. It is a no-op for text without `…` or stray spacing. Since `_slug` is punctuation-insensitive, this does **not** change stem filenames — so editing/adding it requires force-regenerating affected lines (delete their stems) until content-hash caching lands.

### 4.3 Cue rules — standalone cue lines → events

A line that is *only* a `` `[...]` `` cue becomes an event. Rules are tried in
order; **first match wins**; all listed `keywords` must appear (lowercased,
substring) in the cue text. `null`/no match → ignored.

```yaml
cue_rules:
  - { keywords: ["schwupp"],                    sfx: schwupp }
  - { keywords: ["fanfare"],                    music: title_motif, action: intro }
  - { keywords: ["musik","geheimnisvoller"],    music: mystery_bed, action: bed_on }
  - { keywords: ["ausblenden"],                 action: outro }
  - { keywords: ["pling"],                      sfx: pling }
```

Supported `action` values: `intro` (start title motif + ambient bed), `outro` (motif + fade bed out), `bed_on` (with `music: <key>` → a low-volume faded **underscore** of that named music at this point, e.g. a mysterious pad under a climax; keyless → start/refresh the ambient bed), `stinger` (one-shot transition), or omitted with `sfx:` (place that sfx inline).

### 4.4 Podcast-only fields

```yaml
speech_tempo: 0.90        # OPTIONAL. ffmpeg atempo on the speech bus (1.0 = none)
strip_latex:  true        # OPTIONAL. strip \emph{…} etc. from spoken text before TTS
replace:                  # OPTIONAL. spoken-text substitutions applied before slug+TTS.
  "Moderator": "Beni"     #   ordered, case-sensitive regex → replacement. Use for
                          #   pronunciation fixes and in-dialogue renames
                          #   (Moderator→Beni). Slug is computed from the REPLACED text,
                          #   so changing a rule invalidates only the affected cached stems.
einlagen:                 # OPTIONAL. embed rendered Hörspiel plays into the feature
  1: out/die-frau-vor-dem-recht/S01-02/scene1/scene1_play.mp3
  2: out/die-frau-vor-dem-recht/S01-02/scene2/scene2_play.mp3
  # transcript marker `>>> HÖRSPIEL-EINLAGE N` splices in einlagen[N] at that point

intro_audio:  series/quarks-for-kids/wusl-gusl-intro.mp3 # OPTIONAL. ROOT-relative path.
              # If set, this audio file is inserted as the very first piece on the speech
              # bus, followed by a GAP_SWITCH gap, before any speech.
bridge_audio: series/quarks-for-kids/wusl-gusl-intro.mp3 # OPTIONAL. ROOT-relative path.
              # If set, inserted (preceded and followed by a gap) at every `##`-level
              # section boundary EXCEPT the first section (no bridge before the opener).
              # The parser emits a {"t":"bridge"} event at each such boundary; the mixer
              # splices in GAP_SWITCH + bridge_audio + GAP_SFX at that point.
              # Missing file → warning + skip (no crash).
```

### 4.4.1 Spoken-text markdown stripping (`strip_md`)

`strip_md` runs on every dialogue line before TTS and is implemented using `markdown-it-py` (declared in the PEP 723 `dependencies` block). It parses **inline tokens only** (`MarkdownIt().parseInline(…)`) so block rules (lists, headers) cannot mangle dialogue.

- **Bold** (`**x**` / `__x__`, `strong` tokens) → inner text UPPERCASED, but only for short spans (≤4 words AND ≤30 chars); longer bold spans → inner text unchanged (don't shout whole sentences).
- **Italic/emphasis** (`*x*` / `_x_`, `em` tokens) → inner text only (markup stripped).
- **Inline code**, links, strikethrough, HTML → inner text only (markup stripped).
- Returns clean text with no markdown characters.
- The module-level `STRIP_MD = True` gate and call site `strip_md(rest) if STRIP_MD else rest` are preserved.

Example: `strip_md('Ein **Molekül** ist *klein*, siehe **Alles besteht aus kleineren Dingen.**')` → `Ein MOLEKÜL ist klein, siehe Alles besteht aus kleineren Dingen.`

### 4.5 Hörspiel-only section

For `kind: hoerspiel` the drama is authored **inline** in the spec (this is how
the current dramas exist, and copying them verbatim guarantees stem-path reuse —
see §7). Dialogue for *new* Hörspiele may still be authored inline here.

```yaml
hoerspiel:
  name: scene1                 # REQUIRED. file basename → scene1.mp3 / _play.mp3 / _audiobook.mp3 / .txt
  narrator_role: SPRECHER      # role that reads the Einordnung epilogue
  narr_heraus: "Wie realistisch ist diese Szene? Eine kurze Einordnung."
  bed_sfx: atmo_base           # which sfx key is the looped ambient bed
  reverb_roles: []             # roles rendered with reverb (e.g. a seeress "from afar")
  narr_out_id: "16_narr_out"   # OPTIONAL. cache-compat override for the narr-out stem basename

  # analysis epilogue — ONE of:
  analysis_list:               # explicit tl;dr paragraphs (Ep.2 short form)
    - "Der Kern ist mehrfach belegt …"
  # …OR parsed from a source markdown's „Historische Einordnung" (Ep.1):
  # source_md:  series/die-frau-vor-dem-recht/S01-01/hoerspiele.md
  # scene_index: 1

  display:                     # role → display name in the audiobook .txt
    SPRECHER: "ERZÄHLER"

  drama:                       # ordered list; items are speech, or cue dicts
    - { id: "00_narr_in", who: SPRECHER, gap: 0.0, text: "Mekka, dreißig Jahre …" }
    - { cue: atmo_base, gain: 0.8 }
    - { id: "01_maisara", who: MAISARA, gap: 0.6, text: "Herrin — die Ballen …" }

output:
  final: scene1.mp3
  loudnorm: "I=-16:TP=-1.5:LRA=11"
  audiobook_loudnorm: "I=-19:TP=-3:LRA=11"
```

---

## 5. Engine CLI & behavior

- `gen` — TTS every speech segment (per-speaker settings from §4.1), generate
  every `sfx`/`music` key. All idempotent (`skip_existing`). For `kind:
  hoerspiel`, delegates to `hoerspiel.phase_gen(scene, model=<spec.model>)`.
- `mix` — ffmpeg assembly: speech bus with §4 gaps, inline SFX at cue points,
  music motif/stinger overlays and ambient bed via `adelay`, `speech_tempo`,
  final `loudnorm`. Free and re-runnable. Hörspiel also exports `<name>_play.mp3`.
- `book` — hoerspiel only: audiobook variant + `<name>_audiobook.txt`.
- `all` — `gen` then `mix` (then `book` for hoerspiel).
- `parse` — print the parsed event list and segment/char counts; **no API calls**.
  Use it to validate a spec and to compare against a legacy script during migration.

---

## 6. Output layout & stem naming (idempotency contract)

```
out/<slug>/
  voices/   sfx/   music/   work/
  <output.final>            # the finished master
  <name>_play.mp3 <name>_audiobook.mp3 <name>_audiobook.txt   # hoerspiel extras
```

- **Podcast speech stems:** `voices/{idx:03d}_{speaker_key}_{slug32}.mp3`, where
  `idx` is the 0-based speech order, `speaker_key` comes from §4.1, and `slug32`
  is the first 32 chars of the slugified spoken text **after** inline-cue
  transformation (§4.2). Matching this formula exactly is what lets migrated
  episodes reuse cached stems with **zero re-spend**.
- **Hörspiel speech stems:** `voices/<id>.mp3`, where `id` is the drama item's
  literal `id` field.

---

### 6.1 Asset formats & caching efficiency

- **Respect caches; never regenerate.** Every TTS/SFX/music call passes `skip_existing=True`; `mix` reuses whatever `gen` produced. Do not delete or rename cached stems.
- **Compress assets; keep quality high.** Generated assets (TTS/SFX/music) are MP3 from the API — keep them as-is. The final master is MP3 (`libmp3lame -q:a 2`, ~190 kbps VBR) unless a lossless deliverable is explicitly requested.
- **Lossless only where required — use FLAC, not WAV.** ffmpeg intermediates in `work/` (normalized stems, silences, the speech bus, looped beds) stay lossless to avoid generational artifacts across concat/amix/loudnorm, but are written as **FLAC** (lossless *and* ~50% smaller), never WAV. Reach for uncompressed PCM only if a filter genuinely requires it.

## 7. Migration rules (credit safety — MANDATORY)

Every existing episode is already produced; its stems are cached under `out/`.

- **Never re-`gen` a produced episode.** Migrate by writing its YAML spec, then
  verify with `mix` (free) and `parse` only.
- A spec is **parity-correct** when `produce.py <spec> parse` yields the same
  speech-segment count and per-segment text (hence identical slugs → identical
  stem paths) as the legacy script's own `parse`. Verify before deleting anything.
- Copy legacy values **verbatim** into the spec: exact `gaps`, `speech_tempo`,
  `strip_latex`, cue keyword sets, `speaker_key` abbreviations, and (hoerspiel)
  the full `drama` list with original `id`s. A single changed character in the
  spoken text changes the slug and orphans the cached stem.
- The only episode that legitimately spends credits during this work is a new
  episode (no stems exist yet), and its `gen` is **gated on explicit
  user confirmation** (watch `scripts/el.py balance`).
- Delete a legacy script **only after** its spec is parity-verified.

---

## 8. How a skill/agent uses this spec to create an episode

1. Write/obtain the transcript `.md`; wrap the body in `<!-- start -->` /
   `<!-- end -->` (§3).
2. Write the YAML spec next to the transcript, conforming to §4. Pick `model`
   (default v3; use v2 only when a voice is tuned for it). Fill `speakers`,
   `sfx`, `music`, `cue_rules`, `gaps`, `output`.
3. `produce.py <spec> parse` — sanity-check segments/chars, no spend.
4. Check `scripts/el.py balance`; confirm the estimated spend with the user.
5. `produce.py <spec> gen` then `mix` (or `all`). Re-runs are free/idempotent.
