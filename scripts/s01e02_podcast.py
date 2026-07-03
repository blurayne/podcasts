#!/usr/bin/env python3
"""Produce Episode 2 — „Der Parallelbogen" (Doku-Feature that EMBEDS 5 Hörspiele).

Like s01e01_podcast.py, but:
  * source = the Parallelbogen transcript,
  * STIMME 1 = Mila Winter, STIMME 2 = Wolf Spencer (continuity with Ep. 1),
  * `>>> HÖRSPIEL-EINLAGE N` markers splice in out/die-frau-vor-dem-recht/S01-02/sceneN/sceneN_play.mp3,
  * LaTeX artifacts (\\emph{…}, \\enquote{…}, \\S …) are stripped,
  * title motif carries a Middle-Eastern (oud/ney) color, music already at -10%.

Run:  python3 scripts/s01e02_podcast.py gen|mix|all|parse
Needs the 5 Hörspiele built first (they export the *_play.mp3 stems).
"""
import os, re, sys, subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import el

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC  = os.path.join(ROOT, "series", "die-frau-vor-dem-recht", "S01-02", "podcast.md")
OUT  = os.path.join(ROOT, "out", "die-frau-vor-dem-recht", "S01-02", "podcast")
VOX  = os.path.join(OUT, "voices"); SFXD = os.path.join(OUT, "sfx")
MUSD = os.path.join(OUT, "music");  WORK = os.path.join(OUT, "work")
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
    "STIMME 1": "dCnu06FiOZma2KVNUoPZ",  # Mila Winter (narration) — continuity
    "STIMME 2": "2OcnG4mH3jIMtWz3vKus",  # Wolf Spencer (sources/Einordnung) — continuity
}

SFX = {
    "atmo_thing": {"prompt": "Ambient bed: a crackling open fire, a distant blacksmith "
                             "hammering, a low murmur of a gathered crowd, no music, "
                             "seamless loop", "dur": 12},
    "atmo_tower": {"prompt": "Ambient bed: gentle wind over an open landscape, a wide "
                             "slow river, very distant a single faint human call, no "
                             "music, seamless loop", "dur": 12},
    "atmo_sea":   {"prompt": "Ambient bed: sea waves, gulls, creaking ship rigging, no "
                             "music, seamless loop", "dur": 12},
}
MUSIC = {
    "title_motif": {"prompt": "Solemn documentary title motif with a Middle-Eastern "
                              "color: a low sustained dark pad with an oud or ney figure "
                              "over it, slow, contemplative, cinematic, no drums, no vocals",
                              "ms": 24000},
    "transition":  {"prompt": "Short neutral documentary transition with a faint oud "
                              "note over a soft rising sustained tone, unobtrusive, no vocals",
                              "ms": 8000},
}

def music_action(text):
    t = text.lower().strip()
    if "titelmotiv" in t or "titelmotif" in t:
        return ("motif", "title_motif")
    if t in ("aus", "aus.") or t.startswith("aus.") or t.startswith("aus ") or "ausblenden" in t:
        return ("stop", None)
    if "trenner" in t or "übergang" in t or "uebergang" in t:
        return ("stinger", "transition")
    return ("motif", "title_motif")

# ---------------------------------------------------------------- text cleanup
def delatex(s):
    s = re.sub(r"\\enquote\{([^}]*)\}", r"„\1“", s)
    s = re.sub(r"\\(?:emph|textbf|textit|textsc)\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\S~?", "§", s)
    s = s.replace("\\,", " ").replace("\\ ", " ").replace("\\%", "%")
    s = re.sub(r"\\[a-zA-Z]+\{([^}]*)\}", r"\1", s)   # any remaining \cmd{arg}
    s = re.sub(r"\\[a-zA-Z]+", "", s)                  # bare \cmd
    return s

def strip_md(s):
    s = delatex(s)
    s = re.sub(r"\*\*([^*]*)\*\*", r"\1", s)
    s = re.sub(r"\*([^*]*)\*", r"\1", s)
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)     # markdown links -> text
    return s.strip()

def _slug(s, n=28):
    s = re.sub(r"[„“”\"'()]", "", strip_md(s)).lower()
    s = re.sub(r"[^a-z0-9äöüß]+", "-", s).strip("-")
    return s[:n].strip("-") or "seg"

CUE_RE   = re.compile(r"^\[(MUSIK|ATMO|PAUSE)(?::\s*(.*?))?\]\s*$", re.S)
SPK_RE   = re.compile(r"^\*\*(STIMME [12])\s*:\*\*\s*$")
SCENE_RE = re.compile(r"^>>>\s*\*\*HÖRSPIEL-EINLAGE\s*(\d)")

def parse():
    lines = open(SRC, encoding="utf-8").read().splitlines()
    events = []; cur_voice = None; idx = 0; act = "COLD OPEN"
    in_body = False; stop = False
    for raw in lines:
        s = raw.strip()
        if stop:
            break
        if not in_body:
            if s.startswith("## COLD OPEN"):
                in_body = True; events.append({"t": "act", "title": "COLD OPEN"})
            continue
        if s.startswith("## PRODUKTIONSNOTIZEN"):
            break
        if s.startswith("[ENDE"):
            stop = True; continue
        if not s or s == "---":
            continue
        m = re.match(r"^##\s+(AKT [IVX]+|FINALE|COLD OPEN)(?:\s*[—-]\s*(.*))?$", s)
        if m:
            act = (m.group(1) + (" — " + m.group(2) if m.group(2) else "")).strip()
            events.append({"t": "act", "title": act}); cur_voice = None; continue
        sc = SCENE_RE.match(s)
        if sc:
            events.append({"t": "scene", "n": int(sc.group(1))}); cur_voice = None; continue
        if s.startswith("#"):
            continue
        cm = CUE_RE.match(s)
        if cm:
            kind, arg = cm.group(1), (cm.group(2) or "").strip()
            if kind == "PAUSE":
                events.append({"t": "pause"})
            elif kind == "MUSIK":
                action, bed = music_action(arg)
                events.append({"t": "music", "action": action, "bed": bed, "raw": arg})
            elif kind == "ATMO":
                a = arg.lower()
                bed = ("atmo_sea" if ("meer" in a or "möwen" in a) else
                       "atmo_thing" if ("feuer" in a or "thing" in a or "schmiede" in a) else
                       "atmo_tower")
                events.append({"t": "atmo", "bed": bed, "raw": arg})
            continue
        sm = SPK_RE.match(s)
        if sm:
            cur_voice = sm.group(1); continue
        if cur_voice is None:
            continue
        text = strip_md(s)
        if not text:
            continue
        events.append({"t": "speech", "voice": VOICES[cur_voice], "who": cur_voice,
                       "text": text, "idx": idx, "act": act})
        idx += 1
    return events

# ---------------------------------------------------------------- helpers
def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(" ".join(cmd[:6]) + " ...\n" + r.stderr[-1800:] + "\n")
        raise SystemExit(f"command failed ({r.returncode})")
    return r

def dur(path):
    r = subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    return float(r.stdout.strip())

def stem_path(ev):
    who = "s1" if ev["who"] == "STIMME 1" else "s2"
    return os.path.join(VOX, f"{ev['idx']:03d}_{who}_{_slug(ev['text'])}.mp3")

def play_path(n):
    return os.path.join(ROOT, "out", "die-frau-vor-dem-recht", "S01-02", f"scene{n}", f"scene{n}_play.mp3")

# ---------------------------------------------------------------- GEN
def phase_gen():
    events = parse()
    speech = [e for e in events if e["t"] == "speech"]
    scenes = [e for e in events if e["t"] == "scene"]
    print(f"== parsed: {len(speech)} speech segs, {sum(len(e['text']) for e in speech)} chars, "
          f"{len(scenes)} embedded scenes ==")
    missing = [e["n"] for e in scenes if not os.path.exists(play_path(e["n"]))]
    if missing:
        print(f"   NOTE: play stems not yet built for scenes {missing} (build the Hörspiele first)")
    print("== voices ==")
    for ev in speech:
        out = stem_path(ev)
        stab = 0.60 if ev["who"] == "STIMME 2" else 0.50
        if el._exists(out):
            print(f"  skip: {os.path.basename(out)}")
        else:
            el.tts(ev["voice"], ev["text"], out, model=MODEL, stability=stab, skip_existing=True)
            print(f"  ok  : {os.path.basename(out)} ({len(ev['text'])}c)")
    print("== sfx ==")
    for name, spec in SFX.items():
        out = os.path.join(SFXD, name + ".mp3")
        el.sfx(spec["prompt"], out, duration=spec["dur"], skip_existing=True)
        print(f"  {'skip' if el._exists(out) else 'ok  '}: sfx:{name}")
    print("== music ==")
    for name, spec in MUSIC.items():
        out = os.path.join(MUSD, name + ".mp3")
        el.music(spec["prompt"], out, spec["ms"], skip_existing=True)
        print(f"  {'skip' if el._exists(out) else 'ok  '}: music:{name}")
    print("GEN DONE")

# ---------------------------------------------------------------- MIX
def norm(inp, outp, extra=""):
    filt = "aformat=sample_rates=44100:channel_layouts=stereo"
    if extra:
        filt = extra + "," + filt
    run([FF, "-y", "-i", inp, "-af", filt, outp])

def silence(secs, outp):
    run([FF, "-y", "-f", "lavfi", "-t", f"{secs:.3f}", "-i", "anullsrc=r=44100:cl=stereo", outp])

GAP_BASE, GAP_ACT, GAP_SWITCH, GAP_PAUSE, GAP_SCENE = 0.70, 1.60, 0.95, 1.00, 1.20
SPEECH_TEMPO = 1.0

def build_timeline(events):
    pieces = []; t = 0.0; prev_who = None; pending_extra = 0.0
    atmo_open = None; atmo_spans = []; music_events = []
    def add_silence(sec):
        nonlocal t
        if sec <= 0: return
        sp = os.path.join(WORK, f"sil_{len(pieces)}.wav"); silence(sec, sp)
        pieces.append(sp); t += sec
    for ev in events:
        k = ev["t"]
        if k == "act":
            if atmo_open is not None:
                atmo_spans.append((atmo_open[0], atmo_open[1], t)); atmo_open = None
            pending_extra = max(pending_extra, GAP_ACT); continue
        if k == "pause":
            pending_extra += GAP_PAUSE; continue
        if k == "atmo":
            if atmo_open is not None:
                atmo_spans.append((atmo_open[0], atmo_open[1], t))
            atmo_open = (ev["bed"], t); continue
        if k == "music":
            music_events.append((ev["action"], ev["bed"], t)); continue
        if k == "scene":
            if atmo_open is not None:
                atmo_spans.append((atmo_open[0], atmo_open[1], t)); atmo_open = None
            add_silence(GAP_SCENE)
            p = play_path(ev["n"])
            if os.path.exists(p):
                w = os.path.join(WORK, f"scene_{ev['n']}.wav"); norm(p, w)
                pieces.append(w); t += dur(w)
                print(f"   embedded scene {ev['n']} ({dur(w):.1f}s)")
            else:
                print(f"   WARN scene {ev['n']} play missing -> skipped")
            add_silence(GAP_SCENE); prev_who = None; continue
        if k == "speech":
            gap = GAP_BASE
            if prev_who is not None and ev["who"] != prev_who:
                gap = max(gap, GAP_SWITCH)
            gap += pending_extra; pending_extra = 0.0
            if prev_who is None and not pieces:
                gap = 0.0
            add_silence(gap)
            w = os.path.join(WORK, "n_" + os.path.basename(stem_path(ev)) + ".wav")
            norm(stem_path(ev), w, "" if SPEECH_TEMPO == 1.0 else f"atempo={SPEECH_TEMPO}")
            pieces.append(w); t += dur(w); prev_who = ev["who"]; continue
    if atmo_open is not None:
        atmo_spans.append((atmo_open[0], atmo_open[1], t))
    add_silence(1.2)
    bus = os.path.join(WORK, "speech_bus.wav")
    inputs = []
    for p in pieces:
        inputs += ["-i", p]
    n = len(pieces)
    fc = "".join(f"[{i}:a]" for i in range(n)) + f"concat=n={n}:v=0:a=1[o]"
    run([FF, "-y", *inputs, "-filter_complex", fc, "-map", "[o]", bus])
    return bus, dur(bus), atmo_spans, music_events

def loop_bed(src, length, vol, outp):
    run([FF, "-y", "-stream_loop", "-1", "-i", src, "-t", f"{length:.3f}",
         "-af", f"volume={vol},afade=t=in:st=0:d=1.2,"
                f"afade=t=out:st={max(0,length-1.5):.3f}:d=1.5,"
                "aformat=sample_rates=44100:channel_layouts=stereo", outp])

def delayed(src, start, outp, vol=1.0):
    ms = int(start * 1000)
    run([FF, "-y", "-i", src, "-af",
         f"volume={vol},adelay={ms}|{ms},aformat=sample_rates=44100:channel_layouts=stereo", outp])

def phase_mix():
    events = parse()
    print("== build speech timeline ==")
    bus, blen, atmo_spans, music_events = build_timeline(events)
    print(f"   bus {blen:.1f}s; atmo {len(atmo_spans)}; music {len(music_events)}")
    layers = [bus]
    for i, (bed, a, b) in enumerate(atmo_spans):
        src = os.path.join(SFXD, bed + ".mp3")
        if not el._exists(src):
            print(f"   WARN missing atmo {bed}"); continue
        looped = os.path.join(WORK, f"atmo_{i}_loop.wav"); loop_bed(src, max(2.0, b - a), 0.28, looped)
        ducked = os.path.join(WORK, f"atmo_{i}_duck.wav")
        run([FF, "-y", "-i", looped, "-i", bus, "-filter_complex",
             "[0:a][1:a]sidechaincompress=threshold=0.02:ratio=8:attack=5:release=300[o]",
             "-map", "[o]", ducked])
        placed = os.path.join(WORK, f"atmo_{i}_placed.wav"); delayed(ducked, a, placed)
        layers.append(placed); print(f"   atmo {bed} @ {a:.1f}-{b:.1f}s")

    def next_stop_after(tt):
        c = [e[2] for e in music_events if e[0] == "stop" and e[2] > tt]
        return min(c) if c else None

    mi = 0
    for action, bed, at in music_events:
        if action == "stop":
            continue
        src = os.path.join(MUSD, bed + ".mp3")
        if not el._exists(src):
            print(f"   WARN missing music {bed}"); continue
        placed = os.path.join(WORK, f"mus_{mi}_placed.wav")
        tmp = os.path.join(WORK, f"mus_{mi}_bed.wav")
        if action == "motif":
            stop_at = next_stop_after(at); full = dur(src)
            length = full if stop_at is None else max(4.0, min(full, stop_at - at))
            run([FF, "-y", "-i", src, "-t", f"{length:.3f}", "-af",
                 f"volume=0.495,afade=t=in:st=0:d=2.0,"  # music -10%
                 f"afade=t=out:st={max(0,length-3.0):.3f}:d=3.0,"
                 "aformat=sample_rates=44100:channel_layouts=stereo", tmp])
        else:
            length = dur(src)
            run([FF, "-y", "-i", src, "-af",
                 f"volume=0.405,afade=t=in:st=0:d=1.0,"  # music -10%
                 f"afade=t=out:st={max(0,length-2.0):.3f}:d=2.0,"
                 "aformat=sample_rates=44100:channel_layouts=stereo", tmp])
        delayed(tmp, at, placed); layers.append(placed)
        print(f"   music {action}:{bed} @ {at:.1f}s"); mi += 1

    print("== final mix ==")
    inputs = []
    for p in layers:
        inputs += ["-i", p]
    n = len(layers)
    fc = ("".join(f"[{i}:a]" for i in range(n)) +
          f"amix=inputs={n}:normalize=0:dropout_transition=0[m];"
          "[m]loudnorm=I=-16:TP=-1.5:LRA=11[o]")
    final = os.path.join(OUT, "podcast.mp3")
    run([FF, "-y", *inputs, "-filter_complex", fc, "-map", "[o]",
         "-codec:a", "libmp3lame", "-q:a", "2", final])
    print("FINAL:", final, f"({dur(final):.1f}s)")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd == "parse":
        for e in parse():
            print(e["t"], e.get("who") or e.get("title") or e.get("n") or e.get("raw", ""),
                  ("| " + e["text"][:60]) if e["t"] == "speech" else "")
        sys.exit(0)
    if cmd in ("gen", "all"):
        phase_gen()
    if cmd in ("mix", "all"):
        phase_mix()
