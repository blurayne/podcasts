# Audiobook Production Pipeline

AI-driven audio production pipeline for German podcast and radio-play series. Uses ElevenLabs (TTS, SFX, music) and ffmpeg to generate fully mixed episodes from Markdown scripts.

## Series

### Die Frau vor dem Recht (S01)

Historical documentary podcast + Hörspiel series on the legal status of women across cultures and centuries.

| Episode | Title | Scenes | Podcast |
|---------|-------|--------|---------|
| S01-01 | Germanen bis Moderne | 3 Hörspiele | ✓ |
| S01-02 | Der Parallelbogen (Islam) | 5 Hörspiele | ✓ |

Podcast voices: STIMME 1 = Mila Winter, STIMME 2 = Wolf Spencer.

### Quarks for Kids

Kids' science podcast. Episode 1: *„Kleiner geht's nicht"* — a journey from cells to quarks.

## Repository Layout

```
series/<show>/S01-0N/     — source Markdown (scripts, studie/)
out/<show>/S01-0N/        — generated stems + final mixes (via Git LFS)
scripts/                  — production scripts (el.py, hoerspiel.py, s01e0*.py)
docs/                     — API docs, research, templates
```

Per episode output:
- `sceneN.mp3` — full radio play (drama + atmo + music)
- `sceneN_play.mp3` — drama-only stem (embedded in podcast)
- `sceneN_audiobook.mp3` — clean narration read
- `podcast/podcast.mp3` — documentary feature

## Setup

```bash
# Install tools via mise
mise install

# Load ElevenLabs API key
set -a; source ./.env; set +a

# Check balance
python3 scripts/el.py balance
```

Requires: Python 3, ffmpeg, jq, curl. The mise-managed ffmpeg symlink may be broken — a working system binary at `/usr/bin/ffmpeg` is used as fallback automatically.

## Producing an Episode

Each script supports `gen | mix | book | all`:

```bash
# Generate voices/SFX/music stems
python3 scripts/s01e02_scene1.py gen

# Mix final audio
python3 scripts/s01e02_scene1.py mix

# Build audiobook read
python3 scripts/s01e02_scene1.py book

# All three in sequence
python3 scripts/s01e02_scene1.py all
```

Build the Hörspiele before the podcast (the podcast embeds the `*_play.mp3` stems):

```bash
for s in 1 2 3 4 5; do python3 scripts/s01e02_scene${s}.py all; done
python3 scripts/s01e02_podcast.py all
```

## Key Scripts

| Script | Purpose |
|--------|---------|
| `scripts/el.py` | ElevenLabs CLI + importable library (TTS, SFX, music, voices, balance) |
| `scripts/hoerspiel.py` | Reusable Hörspiel engine — drives all S01-02 scenes |
| `scripts/s01e01_scene1.py` | S01-01 Szene 1 (self-contained, predates the engine) |
| `scripts/s01e01_scene{2,3}.py` | S01-01 Szenen 2–3 (engine specs) |
| `scripts/s01e01_podcast.py` | S01-01 podcast |
| `scripts/s01e02_scene{1–5}.py` | S01-02 Szenen 1–5 |
| `scripts/s01e02_podcast.py` | S01-02 podcast (embeds Hörspiele, oud/ney motif) |

## Voice Policy

Only **studio-quality** voices (`category: professional` in ElevenLabs) rendered with model `eleven_v3`. Check before casting:

```bash
python3 scripts/el.py voices --grep <name>
```

Always pass `--skip-existing` to avoid re-spending credits on already-generated files.

## Git LFS

MP3 files are tracked with Git LFS (`*.mp3 filter=lfs diff=lfs merge=lfs -text`).
