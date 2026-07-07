#!/usr/bin/env python3
"""Produce Quarks for Kids — Episode 1: „Kleiner geht's nicht".

Two-voice kids' science podcast.
  LINA      = Hope      (tnSpp4vdxKPjI9w0GnoV) — upbeat and clear
  DR. FUNKE = Jorin     (wloRHjPaKZv3ucH7TQOT) — captivating and soft

Run:  python3 scripts/quarks_e01_podcast.py gen|mix|all
"""
import os, re, sys, subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import el

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC  = os.path.join(ROOT, "series", "quarks-for-kids", "podcast-kleiner-gehts-nicht.md")
OUT  = os.path.join(ROOT, "out", "quarks-for-kids", "e01")
VOX  = os.path.join(OUT, "voices")
SFXD = os.path.join(OUT, "sfx")
MUSD = os.path.join(OUT, "music")
WORK = os.path.join(OUT, "work")
for d in (VOX, SFXD, MUSD, WORK):
    os.makedirs(d, exist_ok=True)

def _pick(cands):
    for c in [c for c in cands if c]:
        try:
            subprocess.run([c, "-version"], capture_output=True, check=True); return c
        except Exception:
            pass
    raise SystemExit("no working ffmpeg/ffprobe found")

FF      = _pick([os.environ.get("FFMPEG_BIN"), "/usr/bin/ffmpeg", "ffmpeg"])
FFPROBE = _pick([os.environ.get("FFPROBE_BIN"), "/usr/bin/ffprobe", "ffprobe"])
MODEL   = "eleven_v3"

VOICES = {
    "LINA":      "tnSpp4vdxKPjI9w0GnoV",  # Hope — upbeat and clear
    "DR. FUNKE": "wloRHjPaKZv3ucH7TQOT",  # Jorin — captivating and soft
}

SFX = {
    "pling": {
        "prompt": "A short bright metallic ping or chime, like a tiny bell struck once, "
                  "clean and resonant, no reverb tail, very short",
        "dur": 2,
    },
}

MUSIC = {
    "title_motif": {
        "prompt": "Upbeat curious science podcast theme: playful piano over a light synth pad, "
                  "sense of wonder and discovery, bright and warm, suitable for a kids' science "
                  "show, no vocals, no drums",
        "ms": 10000,
    },
    "transition": {
        "prompt": "Short airy science podcast transition: a soft ascending synth chime, "
                  "two to three notes, light and curious, no vocals",
        "ms": 3000,
    },
    "bed": {
        "prompt": "Calm ambient science background bed: gentle low synth hum with subtle cosmic "
                  "texture, barely audible, unobtrusive, loopable, no rhythm, no melody, no vocals",
        "ms": 32000,
    },
}

# German stage direction → ElevenLabs v3 English inline tag (or empty = strip)
V3_MAP = {
    "lacht":           "[laughs]",
    "flüstert":        "[whispers]",
    "leiser":          "[softly]",
    "lächelt hörbar":  "[smiling]",
    "lächelnd":        "[smiling]",
    "ruhig":           "[calm]",
    "rechnet":         "",
}

def apply_v3(text):
    """Replace `[DE stage dir]` with ElevenLabs v3 tag or remove."""
    def _sub(m):
        key = m.group(1).strip().lower()
        return V3_MAP.get(key, "")
    return re.sub(r"`\[([^\]]+)\]`", _sub, text).strip()

def strip_md(s):
    s = re.sub(r"\*\*([^*]*)\*\*", r"\1", s)
    s = re.sub(r"\*([^*]*)\*",     r"\1", s)
    return s.strip()

def _slug(s, n=32):
    s = re.sub(r'[„""\"\'()\[\]]+', "", strip_md(s)).lower()
    s = re.sub(r"[^a-z0-9äöüß]+", "-", s).strip("-")
    return s[:n].strip("-") or "seg"

# Matches:  **LINA:** rest…  or  **DR. FUNKE:** rest…  (colon is inside the **)
SPEAKER_RE   = re.compile(r"^\*\*(LINA|DR\. FUNKE):\*\*\s*(.*)", re.S)
PURE_CUE_RE  = re.compile(r"^`\[([^\]]+)\]`\s*$")

def classify_cue(text):
    """Return event dict for a standalone cue line, or None to ignore."""
    t = text.lower()
    if "pling" in t or "ton-akzent" in t:
        return {"t": "sfx", "key": "pling"}
    if "ausblenden" in t:
        return {"t": "music", "action": "outro"}     # outro motif + bed fade
    if "sirren" in t or "reinzoomen" in t:
        return {"t": "music", "action": "intro"}     # title motif + bed on
    if "kurz hoch" in t or ("kurz" in t and "weg" in t):
        return {"t": "music", "action": "stinger"}   # transition stinger
    if "sanfte musik" in t or "musik kommt zurück" in t:
        return {"t": "music", "action": "bed_on"}    # (re)start bed quietly
    return None  # "Musikbett wird ernster" etc. → keep current bed, ignore


# ---------------------------------------------------------------- PARSE
def parse():
    lines = open(SRC, encoding="utf-8").read().splitlines()
    events = []; idx = 0; in_body = False
    for raw in lines:
        s = raw.strip()
        if not in_body:
            if s.startswith("## 0"):
                in_body = True
            continue
        if s.startswith("### Kurz"):   # stop at the cue-sheet table
            break
        if not s or s == "---":
            continue
        if s.startswith("#"):
            continue

        # standalone cue
        m = PURE_CUE_RE.match(s)
        if m:
            ev = classify_cue(m.group(1))
            if ev:
                events.append(ev)
            continue

        # speaker line  (**LINA:** text  or  **DR. FUNKE:** text)
        sm = SPEAKER_RE.match(s)
        if not sm:
            continue
        who, rest = sm.group(1), sm.group(2).strip()
        if not rest:
            continue
        text = apply_v3(strip_md(rest))
        if not text:
            continue
        events.append({"t": "speech", "who": who,
                        "voice": VOICES[who], "text": text, "idx": idx})
        idx += 1

    return events


# ---------------------------------------------------------------- helpers
def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(" ".join(str(x) for x in cmd[:6]) + "\n" + r.stderr[-1500:] + "\n")
        raise SystemExit(f"command failed ({r.returncode})")
    return r

def dur(path):
    r = subprocess.run(
        [FFPROBE, "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True)
    return float(r.stdout.strip())

def norm(inp, outp, extra=""):
    filt = "aformat=sample_rates=44100:channel_layouts=stereo"
    if extra:
        filt = extra + "," + filt
    run([FF, "-y", "-i", inp, "-af", filt, outp])

def silence(secs, outp):
    run([FF, "-y", "-f", "lavfi", "-t", f"{secs:.3f}",
         "-i", "anullsrc=r=44100:cl=stereo", outp])

def stem_path(ev):
    who = "lina" if ev["who"] == "LINA" else "funke"
    return os.path.join(VOX, f"{ev['idx']:03d}_{who}_{_slug(ev['text'])}.mp3")


# ---------------------------------------------------------------- GEN
def phase_gen():
    events = parse()
    speech = [e for e in events if e["t"] == "speech"]
    print(f"== parsed: {len(speech)} speech segs, "
          f"{sum(len(e['text']) for e in speech)} chars ==")
    print("== voices ==")
    for ev in speech:
        out = stem_path(ev)
        stab = 0.55 if ev["who"] == "LINA" else 0.48
        if el._exists(out):
            print(f"  skip: {os.path.basename(out)}")
        else:
            el.tts(ev["voice"], ev["text"], out, model=MODEL,
                   stability=stab, skip_existing=True)
            print(f"  ok  : {os.path.basename(out)} ({len(ev['text'])}c)")
    print("== sfx ==")
    for name, spec in SFX.items():
        out = os.path.join(SFXD, name + ".mp3")
        if not el._exists(out):
            el.sfx(spec["prompt"], out, duration=spec["dur"], skip_existing=True)
            print(f"  ok  : sfx:{name}")
        else:
            print(f"  skip: sfx:{name}")
    print("== music ==")
    for name, spec in MUSIC.items():
        out = os.path.join(MUSD, name + ".mp3")
        if not el._exists(out):
            el.music(spec["prompt"], out, spec["ms"], skip_existing=True)
            print(f"  ok  : music:{name}")
        else:
            print(f"  skip: music:{name}")
    print("GEN DONE")


# ---------------------------------------------------------------- MIX
GAP_BASE   = 0.55   # gap between consecutive lines of same speaker
GAP_SWITCH = 0.90   # gap when speaker changes
GAP_SFX    = 0.35   # tail after an sfx pling

def build_timeline(events):
    """Build speech bus (WAV concat), collect overlay timestamps."""
    pieces = []; t = 0.0; prev_who = None
    bed_on = False; bed_start = None; bed_spans = []
    overlays = []   # (kind, key, t_seconds)  kind in {motif,stinger}

    def add_sil(sec):
        nonlocal t
        if sec <= 0: return
        p = os.path.join(WORK, f"sil_{len(pieces)}.wav")
        silence(sec, p); pieces.append(p); t += sec

    for ev in events:
        k = ev["t"]

        if k == "music":
            action = ev["action"]
            if action == "intro":
                overlays.append(("motif", "title_motif", t))
                bed_start = t; bed_on = True
            elif action == "stinger":
                overlays.append(("stinger", "transition", t))
            elif action == "bed_on":
                if not bed_on:
                    bed_start = t; bed_on = True
            elif action == "outro":
                if bed_on:
                    bed_spans.append((bed_start, t)); bed_on = False
                overlays.append(("motif", "title_motif", t))
            continue

        if k == "sfx":
            sfx_p = os.path.join(SFXD, ev["key"] + ".mp3")
            if os.path.exists(sfx_p):
                w = os.path.join(WORK, f"sfx_{len(pieces)}.wav")
                norm(sfx_p, w); pieces.append(w); t += dur(w)
                add_sil(GAP_SFX)
            continue

        if k == "speech":
            gap = GAP_BASE
            if prev_who is not None and ev["who"] != prev_who:
                gap = GAP_SWITCH
            if prev_who is None and not pieces:
                gap = 0.0
            add_sil(gap)
            w = os.path.join(WORK, "n_" + os.path.basename(stem_path(ev)) + ".wav")
            norm(stem_path(ev), w)
            pieces.append(w); t += dur(w); prev_who = ev["who"]

    if bed_on:
        bed_spans.append((bed_start, t))
    add_sil(1.2)

    # concat speech bus
    bus = os.path.join(WORK, "speech_bus.wav")
    n = len(pieces)
    inputs = []
    for p in pieces: inputs += ["-i", p]
    fc = "".join(f"[{i}:a]" for i in range(n)) + f"concat=n={n}:v=0:a=1[o]"
    run([FF, "-y", *inputs, "-filter_complex", fc, "-map", "[o]", bus])
    return bus, t, bed_spans, overlays


def loop_bed(length, vol, outp):
    src = os.path.join(MUSD, "bed.mp3")
    fade_out = max(0.0, length - 3.0)
    run([FF, "-y", "-stream_loop", "-1", "-i", src,
         "-t", f"{length:.3f}",
         "-af", f"volume={vol},"
                f"afade=t=in:st=0:d=2.0,"
                f"afade=t=out:st={fade_out:.3f}:d=3.0,"
                "aformat=sample_rates=44100:channel_layouts=stereo",
         outp])


def phase_mix():
    events = parse()
    bus, total, bed_spans, overlays = build_timeline(events)
    print(f"   speech bus: {total:.1f}s")

    layers = ["-i", bus]
    delay_ms = []   # None = no delay (full-length pad), int = ms offset

    # ambient bed segments — use adelay so we avoid generating a silence pad
    for i, (s, e) in enumerate(bed_spans):
        seg = os.path.join(WORK, f"bed_seg_{i}.wav")
        loop_bed(e - s, 0.10, seg)
        layers += ["-i", seg]; delay_ms.append(int(s * 1000))

    # motif / stinger overlays
    for kind, key, ts in overlays:
        src = os.path.join(MUSD, key + ".mp3")
        w   = os.path.join(WORK, f"ov_{kind}_{len(delay_ms)}.wav")
        norm(src, w)
        layers += ["-i", w]; delay_ms.append(int(ts * 1000))

    out_path = os.path.join(OUT, "podcast.mp3")

    if not delay_ms:
        run([FF, "-y", "-i", bus,
             "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", out_path])
        print(f"MIX DONE → {out_path}"); return

    n_extra = len(delay_ms)
    n_total = 1 + n_extra
    filter_parts = []
    for i, d in enumerate(delay_ms):
        idx = i + 1
        filter_parts.append(f"[{idx}:a]adelay={d}|{d}[l{idx}]")
    mixed = "[0:a]" + "".join(f"[l{i+1}]" for i in range(n_extra))
    fc = (";".join(filter_parts)
          + f";{mixed}amix=inputs={n_total}:normalize=0:duration=first[mix]"
          + ";[mix]loudnorm=I=-16:TP=-1.5:LRA=11[out]")
    run([FF, "-y", *layers,
         "-filter_complex", fc, "-map", "[out]",
         out_path])
    print(f"MIX DONE → {out_path}")


# ---------------------------------------------------------------- MAIN
if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd in ("gen", "all"): phase_gen()
    if cmd in ("mix", "all"): phase_mix()
