#!/usr/bin/env python3
"""el — a small ElevenLabs API CLI + library for the audiobook pipeline.

Reads the API key from $ELEVENLABS_API_KEY (source ./.env with `set -a` first).
Usable two ways:

  * CLI:      python3 scripts/el.py balance
              python3 scripts/el.py voices --grep german
              python3 scripts/el.py tts   --voice Apollo --text "Hallo" --out a.mp3
              python3 scripts/el.py sfx    --prompt "wind over a field" --duration 6 --out w.mp3
              python3 scripts/el.py music  --prompt "dark drone" --length-ms 20000 --out m.mp3

  * library:  import el; el.tts("Apollo", "Hallo", "a.mp3", skip_existing=True)

Every generator supports --skip-existing so re-runs never re-spend credits.
"""
import argparse, json, os, re, sys, time, urllib.request, urllib.error

API = "https://api.elevenlabs.io/v1"
DEFAULT_MODEL = "eleven_v3"
_MIN_BYTES = 2000                       # smaller than this == treat as not generated


def _key():
    k = os.environ.get("ELEVENLABS_API_KEY")
    if not k:
        sys.exit("ELEVENLABS_API_KEY not set — run:  set -a; source ./.env; set +a")
    return k


def _req(method, path, *, json_body=None, accept="application/json", raw=False, timeout=180):
    data = json.dumps(json_body).encode() if json_body is not None else None
    headers = {"xi-api-key": _key(), "Accept": accept}
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(API + path, data=data, method=method, headers=headers)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                body = r.read()
            return body if raw else json.loads(body.decode())
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="replace")
            if e.code in (429, 500, 502, 503) and attempt < 3:
                time.sleep(3 * (attempt + 1)); continue
            sys.exit(f"HTTP {e.code} {method} {path}: {msg[:400]}")
        except urllib.error.URLError:
            if attempt < 3:
                time.sleep(3 * (attempt + 1)); continue
            raise


# ---------------------------------------------------------------- read helpers
def list_voices():   return _req("GET", "/voices")["voices"]
def list_models():   return _req("GET", "/models")
def subscription():  return _req("GET", "/user/subscription")

def balance():
    s = subscription()
    return {"tier": s.get("tier"), "used": s["character_count"],
            "limit": s["character_limit"],
            "remaining": s["character_limit"] - s["character_count"]}

def resolve_voice(name_or_id):
    """Accept a raw voice_id (used as-is, no API call) or a unique name substring."""
    if re.fullmatch(r"[A-Za-z0-9]{18,}", name_or_id):
        return name_or_id
    hits = [v for v in list_voices() if name_or_id.lower() in v["name"].lower()]
    if len(hits) == 1:
        return hits[0]["voice_id"]
    if not hits:
        sys.exit(f"no voice matches {name_or_id!r}")
    sys.exit("ambiguous voice, matches: " + ", ".join(v["name"] for v in hits))


# ---------------------------------------------------------------- generators
def _exists(path):
    return os.path.exists(path) and os.path.getsize(path) > _MIN_BYTES

def _write(path, data):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)

def tts(voice, text, out, *, model=DEFAULT_MODEL, stability=0.5, similarity=0.8,
        speaker_boost=True, skip_existing=False):
    if skip_existing and _exists(out):
        return out
    body = {"text": text, "model_id": model,
            "voice_settings": {"stability": stability, "similarity_boost": similarity,
                               "use_speaker_boost": speaker_boost}}
    _write(out, _req("POST", f"/text-to-speech/{resolve_voice(voice)}",
                     json_body=body, accept="audio/mpeg", raw=True))
    return out

def sfx(prompt, out, *, duration=None, prompt_influence=0.4, skip_existing=False):
    if skip_existing and _exists(out):
        return out
    body = {"text": prompt, "prompt_influence": prompt_influence}
    if duration:
        body["duration_seconds"] = duration
    _write(out, _req("POST", "/sound-generation", json_body=body,
                     accept="audio/mpeg", raw=True))
    return out

def music(prompt, out, length_ms, *, skip_existing=False):
    if skip_existing and _exists(out):
        return out
    _write(out, _req("POST", "/music", json_body={"prompt": prompt,
                     "music_length_ms": length_ms}, accept="audio/mpeg", raw=True))
    return out


# ---------------------------------------------------------------- CLI
def main(argv=None):
    p = argparse.ArgumentParser(prog="el", description="ElevenLabs API CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("balance", help="credits remaining")
    pv = sub.add_parser("voices", help="list account voices"); pv.add_argument("--grep")
    sub.add_parser("models", help="list models")

    pt = sub.add_parser("tts", help="text to speech")
    pt.add_argument("--voice", required=True, help="voice_id or unique name substring")
    g = pt.add_mutually_exclusive_group(required=True)
    g.add_argument("--text"); g.add_argument("--text-file")
    pt.add_argument("--out", required=True)
    pt.add_argument("--model", default=DEFAULT_MODEL)
    pt.add_argument("--stability", type=float, default=0.5)
    pt.add_argument("--skip-existing", action="store_true")

    ps = sub.add_parser("sfx", help="sound effect")
    ps.add_argument("--prompt", required=True); ps.add_argument("--out", required=True)
    ps.add_argument("--duration", type=float, help="seconds (omit = AI decides, flat 200 cr)")
    ps.add_argument("--skip-existing", action="store_true")

    pm = sub.add_parser("music", help="music generation")
    pm.add_argument("--prompt", required=True); pm.add_argument("--out", required=True)
    pm.add_argument("--length-ms", type=int, required=True)
    pm.add_argument("--skip-existing", action="store_true")

    a = p.parse_args(argv)
    if a.cmd == "balance":
        print(json.dumps(balance(), indent=2))
    elif a.cmd == "voices":
        for v in list_voices():
            if not a.grep or a.grep.lower() in v["name"].lower():
                print(f'{v["voice_id"]}  {v["name"]}')
    elif a.cmd == "models":
        for m in list_models():
            print(m["model_id"], "|", m.get("name"))
    elif a.cmd == "tts":
        if a.skip_existing and _exists(a.out):
            print("skip", a.out); return
        text = a.text if a.text else open(a.text_file, encoding="utf-8").read()
        tts(a.voice, text, a.out, model=a.model, stability=a.stability)
        print("wrote", a.out)
    elif a.cmd == "sfx":
        if a.skip_existing and _exists(a.out):
            print("skip", a.out); return
        sfx(a.prompt, a.out, duration=a.duration); print("wrote", a.out)
    elif a.cmd == "music":
        if a.skip_existing and _exists(a.out):
            print("skip", a.out); return
        music(a.prompt, a.out, a.length_ms); print("wrote", a.out)


if __name__ == "__main__":
    main()
