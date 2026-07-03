# `el` — ElevenLabs API CLI

A small Python CLI + importable library used by the audiobook / podcast
production pipeline. It wraps the ElevenLabs HTTP API so scripts never hand-roll
requests. Source: [`scripts/el.py`](scripts/el.py).

## Setup

The key is read from `$ELEVENLABS_API_KEY`. Load it (never read the file):

```bash
set -a; source ./.env; set +a
```

No third-party Python deps — standard library only. Run with `python3 scripts/el.py …`.

## Commands

| Command | What it does |
|---|---|
| `balance` | Print tier + credits used / limit / **remaining** (JSON) |
| `voices [--grep TEXT]` | List account voices as `voice_id  name` (optionally filtered) |
| `models` | List available models (`model_id | name`) |
| `tts` | Text-to-speech → MP3 |
| `sfx` | Sound-effect generation → MP3 |
| `music` | Eleven Music generation → MP3 |

### `tts`
```bash
python3 scripts/el.py tts \
  --voice Apollo \                 # voice_id OR unique name substring
  --text "Guten Tag." \            # or: --text-file path.txt
  --out out/line.mp3 \
  --model eleven_v3 \              # default eleven_v3
  --stability 0.5 \
  --skip-existing                  # don't regenerate (saves credits) if file exists
```

### `sfx`
```bash
python3 scripts/el.py sfx \
  --prompt "wind over an open field, distant cowbells" \
  --out out/atmo.mp3 \
  --duration 6 \                   # omit → AI decides length (flat 200 credits)
  --skip-existing
```

### `music`
```bash
python3 scripts/el.py music \
  --prompt "dark solemn ritual drone, distant war horn" \
  --out out/intro.mp3 \
  --length-ms 26000 \
  --skip-existing
```

## Library use (import)

The orchestrators (`scripts/s01e01_scene1.py`, `scripts/s01e01_podcast.py`)
import it directly:

```python
import el
el.balance()                                  # {'tier','used','limit','remaining'}
el.resolve_voice("Apollo")                    # -> voice_id (id passed through as-is)
el.tts("wcGcDDfRHvH6LR9p07u4", text, "l.mp3", model="eleven_v3", skip_existing=True)
el.sfx("a wooden knock", "k.mp3", duration=2, skip_existing=True)
el.music("soft drone", "m.mp3", 20000, skip_existing=True)
```

`--skip-existing` / `skip_existing=True` treats any existing file >2 KB as done,
so **re-runs never re-spend credits** — generation is idempotent.

## Credit costs (shared pool, see `balance`)

| Product | Cost |
|---|---|
| TTS | 1 credit / character |
| Sound Effects | 200 / generation (AI duration) or 40 / second (fixed) |
| Eleven Music | ~900 credits / minute |

## Behaviour notes

- `--voice` accepts a raw `voice_id` (used directly, no lookup) or a unique
  case-insensitive **name substring** (errors if it matches 0 or >1 voices).
- Transient HTTP errors (429/5xx) are retried up to 4× with backoff.
- Output MP3 is `mp3_44100_128` (API default).
