# Agent instructions — audiobook project

## ElevenLabs API key

The ElevenLabs API key lives in a `.env` file in the project root, as the
variable `ELEVENLABS_API_KEY`.

### Loading the key

Source `.env` with `allexport` enabled so the assignment is exported into the
environment automatically (a plain `source` will **not** export it):

```bash
set -a; source ./.env; set +a
```

### Do not read the file

Never read, `cat`, print, or otherwise reveal the contents of `.env`. Load it
only via the `source` command above. If you need to confirm the key is present,
check the variable indirectly (e.g. its length) rather than printing its value:

```bash
[ -n "$ELEVENLABS_API_KEY" ] && echo "key loaded (${#ELEVENLABS_API_KEY} chars)"
```

### Testing that the key works

After sourcing, verify the key against the ElevenLabs API without exposing it.
The `xi-api-key` header carries the key; the response body does not contain it:

```bash
set -a; source ./.env; set +a
curl -s -o /tmp/eleven_resp.json -w "HTTP %{http_code}\n" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  https://api.elevenlabs.io/v1/user/subscription
```

`HTTP 200` means the key is valid. `HTTP 401` means it is missing or invalid.

## Project conventions (standing instructions)

- **Record instructions here.** Whenever the user gives a standing instruction,
  write it down in this file (`AGENTS.md`). `CLAUDE.md` is a symlink to it.
- **Always embed Google Drive audio as an iframe.** When a Google Drive link is
  provided for audio, embed it using an `<iframe>` with the `/preview` URL
  (e.g. `https://drive.google.com/file/d/<ID>/preview`) at `height:80px` inside
  an `.audio-wrap` block, and add a "Drive ↗" link button alongside it. Never
  use a bare link in place of an embed.
- **README links to the live site.** `README.md` must always link the published GitHub Pages page (<https://blurayne.github.io/podcasts/>) near the top.
- **index.html links back to the repo.** The Pages site (`index.html`) must keep a visible link back to the GitHub repository (<https://github.com/blurayne/podcasts>) — currently in the footer.
- **Brand is Wusl Gusl (original name).** The kids' show was renamed from „Woozle Goozle" to **Wusl Gusl** to avoid the „Woozle Goozle" trademark. The produced `wusl-gusl.mp3` lives in the git-ignored `out/` dir and is never committed (same as all produced audio).
- **Use the `el` CLI for all ElevenLabs requests.** Never hand-roll HTTP calls;
  use `scripts/el.py` (CLI + importable library). It is documented in
  [`docs/API-CLI.md`](docs/API-CLI.md). Always pass `--skip-existing` / `skip_existing=True`
  so re-runs never re-spend credits.
- **Generic engine + YAML specs.** Produce every episode with `scripts/produce.py <spec.yaml> gen|mix|all` driven by a per-episode YAML spec (production config) plus a markdown transcript (dialogue). The schema, engine CLI, and credit-safe migration rules are the authoritative contract in [`SPEC.md`](SPEC.md) — read it before creating or changing any episode. The reusable skill is `.claude/skills/produce-podcast-episode/`.
- **uv shebang on every script.** Every file in `scripts/` starts with `#!/usr/bin/env -S uv run --script` (never `#!/usr/bin/env python3`). Declare any third-party deps via PEP 723 inline metadata (`# /// script … dependencies = [...] # ///`); uv provisions a cached ephemeral env automatically. `produce.py` uses this to load `pyyaml`.
- **Declare every tool in `mise.toml`.** Tools used: `uv`, `python`, `ffmpeg` (+`ffprobe`), `jq`, `curl`; plus `tectonic` (+ system `pdfinfo`) for the study PDFs.
- **Study PDFs — LaTeX „Observatory" layout.** The series' companion study PDFs (the „Bände") are compiled with the XeTeX/`tectonic` pipeline and the shared Observatory layout (fonts, colours, confidence chips, box types) documented in [`LAYOUT-STUDIES.md`](LAYOUT-STUDIES.md). Read it before compiling, restyling, or adding a Band.
- **ffmpeg:** the mise-managed `ffmpeg` symlink may be broken (missing `libav*`
  shared libs). A working system ffmpeg is at `/usr/bin/ffmpeg` (v4.4.2). The
  orchestrators auto-pick the first working `ffmpeg`/`ffprobe`
  (env `FFMPEG_BIN` > `PATH` > `/usr/bin`), so builds run regardless.
- **Watch the credit pool.** TTS, SFX and Music all draw from one shared balance
  (`python3 scripts/el.py balance`). Flag the user if credits run low. When reporting any spend or estimate, **also give the approximate cost in USD** (Creator plan ≈ $22 per 100,000 credits ≈ $0.00022/credit; label it an estimate).
- **Respect caches; be efficient; compress assets, keep quality high.** Never regenerate cached stems (`skip_existing` everywhere; `mix` reuses whatever `gen` produced). Keep generated assets and finals as high-quality MP3 (`libmp3lame -q:a 2`); use FLAC (lossless *and* ~50% smaller) for ffmpeg intermediates in `work/` — never bulky WAV — and stay uncompressed PCM only where a filter genuinely requires it.
- **Don't tight-loop short atmosphere sounds.** A short sound (< ~3 s) used as an ambient/atmosphere bed must not repeat back-to-back a few times — it reads as an obvious loop. Prefer a longer generated bed, or scatter the short sound across the span with **randomized silence gaps** between plays so the repeats feel natural rather than mechanical.
- **Voices: studio-quality only, preferably v3.** Only cast **studio-quality**
  voices — ElevenLabs `category: professional` (professionally recorded) — and
  render with the **`eleven_v3`** model. Do **not** use `premade` / low-fidelity
  voices. Check a voice's category with `python3 scripts/el.py voices` +
  `GET /v1/voices/{id}` before casting.
- **Licensing: GPLv3 code / CC BY-SA 4.0 content.** The repo is licensed per
  component — software under GPL-3.0-or-later, creative works (transcripts,
  studies, produced audio) under CC BY-SA 4.0 — as outlined in `LICENSE.md`
  (full texts in `LICENSES/`). Keep `LICENSE.md` in sync when adding new kinds
  of assets or third-party material.
- **Einspieler → produce analog + splice, with light music.** When an episode's source includes Einspieler / Hörspielszenen, produce them the same way (embedded scenes) and splice them into the podcast at their docking points (`>>> HÖRSPIEL-EINLAGE N` markers via the `einlagen:` mechanism). Also add short, dezent music underlay (Untermalung) at fitting transitions/moments.

## Repository layout

Series = `die-frau-vor-dem-recht`, Season 01. Folge 1 = `S01-01` (Germanen/Europa),
Folge 2 = `S01-02` („Der Parallelbogen"). Per episode there are Hörspiel-Szenen + one podcast.

- root: `AGENTS.md` (+ `CLAUDE.md` symlink), `mise.toml`, `.env`.
- `docs/` — `API-CLI.md`, `INTFEM-ANALYSIS.md`, `NO-WOKE.md`, `RESTRUCTURE-PLAN.md`,
  `studio-api-access-request.md`, `templates/`.
- `series/die-frau-vor-dem-recht/S01-0N/` — per-episode **sources**: `hoerspiele.md`
  (Ep.1, Szenen 1–3 in einer Datei) or `szene-*.md` (Ep.2), `podcast.md`, `PLAN.md`,
  `PODCAST-PLAN.md` (Ep.1), `studie/`.
- `out/die-frau-vor-dem-recht/S01-0N/{scene1…,podcast}/` — stems (`voices/ sfx/ music/`)
  + finals `sceneN.mp3`, `sceneN_play.mp3`, `sceneN_audiobook.mp3` (+`.txt`), `podcast/podcast.mp3`.

## Scripts

- `scripts/produce.py` — the generic YAML-driven engine (`gen`/`mix`/`all`/`book`/`parse`) that renders any `kind: podcast` or `kind: hoerspiel` episode from a YAML spec + markdown transcript. See [`SPEC.md`](SPEC.md). It supersedes the per-episode scripts: each episode now has a `*.yaml` spec beside its source, and the legacy `s01e0*` / `quarks_*` entry-point scripts are being retired (parity-verified via `parse`/`mix`, then deleted).
- `scripts/el.py` — ElevenLabs API CLI/library (see `docs/API-CLI.md`).
- `scripts/hoerspiel.py` — reusable Hörspiel engine (`gen`/`mix`/`book`/`all`) driven by a
  `Scene` spec. Model `eleven_v3`; inline v3 audio tags (`[shouting]`,`[whispers]`,`[calm]`,
  `[sarcastic]`,`[angry]`,`[sighs]`). `Scene(slug=…, name=…, source_md=…, analysis=[…])`:
  `slug`=out subdir (nested), `name`=file basename, `source_md`=ROOT-relative md for the full
  Einordnung parse (Ep.1), `analysis`=explicit tl;dr (Ep.2). `phase_mix` also exports
  `<name>_play.mp3` (play-only stem the feature splices in).
- **S01-01** (Germanen/Europa): `s01e01_scene1.py` (self-contained, predates the engine),
  `s01e01_scene2.py`, `s01e01_scene3.py` (engine specs), `s01e01_podcast.py`.
- **S01-02** („Der Parallelbogen"): `s01e02_scene1.py … s01e02_scene5.py` (short-form:
  play + tl;dr `analysis=[…]`), `s01e02_podcast.py` (two-voice feature that embeds each play
  at its `>>> HÖRSPIEL-EINLAGE N` marker, strips LaTeX, oud/ney title motif).
- Continuity across both podcasts: STIMME 1 = Mila Winter, STIMME 2 = Wolf Spencer.
