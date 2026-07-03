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
- **Use the `el` CLI for all ElevenLabs requests.** Never hand-roll HTTP calls;
  use `scripts/el.py` (CLI + importable library). It is documented in
  [`docs/API-CLI.md`](docs/API-CLI.md). Always pass `--skip-existing` / `skip_existing=True`
  so re-runs never re-spend credits.
- **Declare every tool in `mise.toml`.** Tools used: `python`, `ffmpeg`
  (+`ffprobe`), `jq`, `curl`.
- **ffmpeg:** the mise-managed `ffmpeg` symlink may be broken (missing `libav*`
  shared libs). A working system ffmpeg is at `/usr/bin/ffmpeg` (v4.4.2). The
  orchestrators auto-pick the first working `ffmpeg`/`ffprobe`
  (env `FFMPEG_BIN` > `PATH` > `/usr/bin`), so builds run regardless.
- **Watch the credit pool.** TTS, SFX and Music all draw from one shared balance
  (`python3 scripts/el.py balance`). Flag the user if credits run low.
- **Voices: studio-quality only, preferably v3.** Only cast **studio-quality**
  voices — ElevenLabs `category: professional` (professionally recorded) — and
  render with the **`eleven_v3`** model. Do **not** use `premade` / low-fidelity
  voices. Check a voice's category with `python3 scripts/el.py voices` +
  `GET /v1/voices/{id}` before casting.

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
