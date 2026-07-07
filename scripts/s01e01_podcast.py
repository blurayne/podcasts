#!/usr/bin/env python3
"""Produce the Doku-Feature podcast "Die Frau vor dem Recht".

Two phases (like s01e01_scene1.py):
  gen  -> parse the transcript and generate every voice / SFX / music stem via
          the ElevenLabs API (idempotent: skips any stem that already exists &
          is non-empty, so credits are only ever spent once per stem).
  mix  -> assemble the stems into
          out/podcast/podcast.mp3 with ffmpeg.

Run:  python3 scripts/s01e01_podcast.py gen
      python3 scripts/s01e01_podcast.py mix
      python3 scripts/s01e01_podcast.py all
      python3 scripts/s01e01_podcast.py parse   # dump the parsed event list

Cast:
  STIMME 1 = Mila Winter (dCnu06FiOZma2KVNUoPZ), red thread — kept
  STIMME 2 = male voice 2OcnG4mH3jIMtWz3vKus, source quotes + „Einordnung" — replaces Gerry
Model: eleven_v3 (studio-quality-voice policy; prefer v3).

Re-run after changing STIMME 2's voice: delete the STIMME 2 stems first so they
regenerate (the voice_id is not part of the stem filename) —
  rm out/die-frau-vor-dem-recht/S01-01/podcast/voices/*_s2_*.mp3 && python3 scripts/s01e01_podcast.py all
STIMME 1 (Mila Winter) stems are kept as-is.
"""
import os, re, sys, subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import el  # the ElevenLabs API CLI/library

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC  = os.path.join(ROOT, "series", "die-frau-vor-dem-recht", "S01-01", "podcast.md")
OUT  = os.path.join(ROOT, "out", "die-frau-vor-dem-recht", "S01-01", "podcast")
VOX  = os.path.join(OUT, "voices")
SFXD = os.path.join(OUT, "sfx")
MUSD = os.path.join(OUT, "music")
WORK = os.path.join(OUT, "work")
for d in (VOX, SFXD, MUSD, WORK):
    os.makedirs(d, exist_ok=True)


def _pick(cands):
    for c in [c for c in cands if c]:
        try:
            subprocess.run([c, "-version"], capture_output=True, check=True)
            return c
        except Exception:
            pass
    raise SystemExit("no working ffmpeg/ffprobe found")

# system ffmpeg first: the mise-managed ffmpeg is broken (missing shared libs)
FF      = _pick([os.environ.get("FFMPEG_BIN"), "/usr/bin/ffmpeg", "ffmpeg"])
FFPROBE = _pick([os.environ.get("FFPROBE_BIN"), "/usr/bin/ffprobe", "ffprobe"])
MODEL   = "eleven_v3"

VOICES = {
    "STIMME 1": "dCnu06FiOZma2KVNUoPZ",  # Mila Winter – expressive narration (kept)
    "STIMME 2": "2OcnG4mH3jIMtWz3vKus",  # male voice (user-provided) — replaces Gerry
}

# ---------------------------------------------------------------- SFX / Music
# 3 distinct [ATMO] beds (loopable), keyed so the parser can attach them.
SFX = {
    "atmo_tower": {"prompt": "Ambient bed: gentle wind over an open landscape, a "
                             "wide slow river flowing, very distant a single faint "
                             "human call, no music, seamless loop", "dur": 12},
    "atmo_thing": {"prompt": "Ambient bed: a crackling open fire, a distant "
                             "blacksmith hammering iron, a low murmur of a gathered "
                             "crowd of people, no music, seamless loop", "dur": 12},
    "atmo_sea":   {"prompt": "Ambient bed: sea waves, crying seagulls, creaking "
                             "ship rigging, then a farmyard with cattle and slow "
                             "footsteps on wooden planks, no music, seamless loop",
                             "dur": 12},
}
MUSIC = {
    "title_motif": {"prompt": "Sparse solemn documentary title motif: a single "
                              "sustained dark instrument over a low ominous pad, "
                              "slow, contemplative, cinematic, no drums, no vocals",
                              "ms": 24000},
    "transition":  {"prompt": "Short neutral documentary transition: a soft rising "
                              "sustained tone, gently brightening, contemplative, "
                              "unobtrusive, no vocals", "ms": 8000},
}

# music-cue keyword -> action (parsed from the [MUSIK: ...] text, lowercased)
def music_action(text):
    t = text.lower().strip()
    # An explicit title-motif cue always STARTS/rings the motif, even if it also
    # says "ausklingen lassen" (= let it ring out over the closing credits).
    if "titelmotiv" in t or "titelmotif" in t:
        return ("motif", "title_motif")
    # Pure stop cues: "[MUSIK: ausblenden]", "[MUSIK: aus. Nur Raum.]".
    if t in ("aus", "aus.") or t.startswith("aus.") or t.startswith("aus ") \
       or "ausblenden" in t:
        return ("stop", None)
    if "trenner" in t:
        return ("stinger", "transition")
    if "übergang" in t or "uebergang" in t:
        return ("stinger", "transition")
    # default -> the recurring motif bed
    return ("motif", "title_motif")


# ---------------------------------------------------------------- parser
CUE_RE   = re.compile(r"^\[(MUSIK|ATMO|PAUSE)(?::\s*(.*?))?\]\s*$", re.S)
SPK_RE   = re.compile(r"^\*\*(STIMME [12])\s*:\*\*\s*$")

def strip_md(s):
    s = re.sub(r"\*\*([^*]*)\*\*", r"\1", s)
    s = re.sub(r"\*([^*]*)\*", r"\1", s)
    return s.strip()

def _slug(s, n=28):
    s = re.sub(r"[„“”\"']", "", strip_md(s)).lower()
    s = re.sub(r"[^a-z0-9äöüß]+", "-", s).strip("-")
    return s[:n].strip("-") or "seg"

def parse():
    """Return an ordered list of events:
       {t:'speech', voice, who, text, idx, act}
       {t:'music', action, bed, raw}
       {t:'atmo',  bed, raw}
       {t:'pause'}
       {t:'act',   title}
    Only content between COLD OPEN and the [ENDE...] marker is used;
    the PRODUKTIONSNOTIZEN section is dropped."""
    lines = open(SRC, encoding="utf-8").read().splitlines()
    events = []
    cur_voice = None
    cur_who = None
    idx = 0
    act = "COLD OPEN"
    in_body = False
    stop = False
    for raw in lines:
        line = raw.rstrip()
        s = line.strip()
        if stop:
            break
        if not in_body:
            if s.startswith("## COLD OPEN"):
                in_body = True
                events.append({"t": "act", "title": "COLD OPEN"})
            continue
        # end markers
        if s.startswith("## PRODUKTIONSNOTIZEN"):
            break
        if s.startswith("[ENDE"):
            stop = True
            continue
        if not s:
            continue
        if s == "---":
            continue
        # act headings like "## AKT I — ..." or "## FINALE — ..."
        m = re.match(r"^##\s+(AKT [IVX]+|FINALE|COLD OPEN)(?:\s*[—-]\s*(.*))?$", s)
        if m:
            act = (m.group(1) + (" — " + m.group(2) if m.group(2) else "")).strip()
            events.append({"t": "act", "title": act})
            cur_voice = None
            continue
        if s.startswith("#"):
            continue
        # cues
        cm = CUE_RE.match(s)
        if cm:
            kind, arg = cm.group(1), (cm.group(2) or "").strip()
            if kind == "PAUSE":
                events.append({"t": "pause"})
            elif kind == "MUSIK":
                action, bed = music_action(arg)
                events.append({"t": "music", "action": action, "bed": bed, "raw": arg})
            elif kind == "ATMO":
                # map the atmo prose to one of our 3 beds by keyword
                a = arg.lower()
                if "meer" in a or "möwen" in a or "tauwerk" in a:
                    bed = "atmo_sea"
                elif "feuer" in a or "schmiede" in a or "versammlung" in a:
                    bed = "atmo_thing"
                else:
                    bed = "atmo_tower"
                events.append({"t": "atmo", "bed": bed, "raw": arg})
            continue
        # speaker marker
        sm = SPK_RE.match(s)
        if sm:
            cur_voice = sm.group(1)
            cur_who = cur_voice
            continue
        # otherwise: spoken paragraph under the current speaker
        if cur_voice is None:
            # front-matter / stray text before first speaker -> ignore
            continue
        text = strip_md(s)
        if not text:
            continue
        events.append({"t": "speech", "voice": VOICES[cur_voice], "who": cur_who,
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


# ---------------------------------------------------------------- GEN phase
def phase_gen():
    events = parse()
    speech = [e for e in events if e["t"] == "speech"]
    total_chars = sum(len(e["text"]) for e in speech)
    print(f"== parsed: {len(speech)} speech segments, {total_chars} chars ==")
    print("== voices ==")
    for ev in speech:
        out = stem_path(ev)
        # STIMME 2 speaks quotes/Einordnung -> a touch more stable / slower feel
        stab = 0.60 if ev["who"] == "STIMME 2" else 0.50
        if el._exists(out):
            print(f"  skip: {os.path.basename(out)}")
        else:
            el.tts(ev["voice"], ev["text"], out, model=MODEL,
                   stability=stab, skip_existing=True)
            print(f"  ok  : {os.path.basename(out)} ({len(ev['text'])}c)")
    print("== sfx (atmo beds) ==")
    for name, spec in SFX.items():
        out = os.path.join(SFXD, name + ".mp3")
        if el._exists(out):
            print(f"  skip: sfx:{name}")
        else:
            el.sfx(spec["prompt"], out, duration=spec["dur"], skip_existing=True)
            print(f"  ok  : sfx:{name}")
    print("== music ==")
    for name, spec in MUSIC.items():
        out = os.path.join(MUSD, name + ".mp3")
        if el._exists(out):
            print(f"  skip: music:{name}")
        else:
            el.music(spec["prompt"], out, spec["ms"], skip_existing=True)
            print(f"  ok  : music:{name}")
    print("GEN DONE")


# ---------------------------------------------------------------- MIX phase
def norm(inp, outp, extra=""):
    filt = "aformat=sample_rates=44100:channel_layouts=stereo"
    if extra:
        filt = extra + "," + filt
    run([FF, "-y", "-i", inp, "-af", filt, outp])

def silence(secs, outp):
    run([FF, "-y", "-f", "lavfi", "-t", f"{secs:.3f}",
         "-i", "anullsrc=r=44100:cl=stereo", outp])

# gaps (seconds) inserted before a speech segment. The feature "lebt von
# Pausen" (Produktionsnotizen), so gaps are generous and the narration is
# time-stretched slightly for a calm, contemplative tempo.
GAP_BASE   = 0.70     # between paragraphs of the same speaker
GAP_ACT    = 1.60     # at an act boundary
GAP_SWITCH = 0.95     # when the speaking voice changes
GAP_PAUSE  = 1.00     # extra for an explicit [PAUSE]
SPEECH_TEMPO = 0.90   # <1 = slower; transparent time-stretch for a ruhiges Tempo

def build_timeline(events):
    """Concatenate speech stems with natural gaps; return
       (bus_wav, total_len, spans) where spans lists atmo/music placements as
       (kind, payload, start_time, end_time)."""
    pieces = []
    t = 0.0
    prev_who = None
    last_act_at = 0.0
    # pending gap additions from act/pause/switch events
    pending_extra = 0.0
    # atmo/music tracking
    atmo_open = None   # (bed, start_time)
    atmo_spans = []
    music_events = []  # (action, bed, time)
    seg_starts = []

    def add_silence(sec):
        nonlocal t
        if sec <= 0:
            return
        sp = os.path.join(WORK, f"sil_{len(pieces)}.wav")
        silence(sec, sp)
        pieces.append(sp)
        t += sec

    for ev in events:
        k = ev["t"]
        if k == "act":
            # close any open atmo at an act boundary
            if atmo_open is not None:
                atmo_spans.append((atmo_open[0], atmo_open[1], t))
                atmo_open = None
            pending_extra = max(pending_extra, GAP_ACT)
            continue
        if k == "pause":
            pending_extra += GAP_PAUSE
            continue
        if k == "atmo":
            # close previous atmo, open a new one starting at current time
            if atmo_open is not None:
                atmo_spans.append((atmo_open[0], atmo_open[1], t))
            atmo_open = (ev["bed"], t)
            continue
        if k == "music":
            if ev["action"] == "stop":
                music_events.append(("stop", None, t))
            else:
                music_events.append((ev["action"], ev["bed"], t))
            continue
        if k == "speech":
            gap = GAP_BASE
            if prev_who is not None and ev["who"] != prev_who:
                gap = max(gap, GAP_SWITCH)
            gap += pending_extra
            pending_extra = 0.0
            if prev_who is None:
                gap = 0.0  # no lead-in silence before the very first line
            add_silence(gap)
            w = os.path.join(WORK, "n_" + os.path.basename(stem_path(ev)) + ".wav")
            tempo = "" if SPEECH_TEMPO == 1.0 else f"atempo={SPEECH_TEMPO}"
            norm(stem_path(ev), w, tempo)
            seg_starts.append((ev["idx"], t))
            pieces.append(w)
            t += dur(w)
            prev_who = ev["who"]
            continue

    # tail + close trailing atmo
    if atmo_open is not None:
        atmo_spans.append((atmo_open[0], atmo_open[1], t))
    add_silence(1.2)

    # concat everything
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


def delayed(src, start, outp, vol=1.0, fin=0.0, fout=0.0):
    """place `src` starting at `start` s on an otherwise-silent stereo track."""
    d = dur(src)
    af = [f"volume={vol}"]
    if fin > 0:
        af.append(f"afade=t=in:st=0:d={fin}")
    if fout > 0:
        af.append(f"afade=t=out:st={max(0,d-fout):.3f}:d={fout}")
    ms = int(start * 1000)
    af.append(f"adelay={ms}|{ms}")
    af.append("aformat=sample_rates=44100:channel_layouts=stereo")
    run([FF, "-y", "-i", src, "-af", ",".join(af), outp])


def phase_mix():
    events = parse()
    print("== build speech timeline ==")
    bus, blen, atmo_spans, music_events = build_timeline(events)
    print(f"   speech bus: {blen:.1f}s; atmo spans={len(atmo_spans)}; "
          f"music events={len(music_events)}")

    layers = [bus]  # first layer is the dry speech bus

    # -- atmo beds: loop across their span, duck under the whole speech bus
    for i, (bed, a, b) in enumerate(atmo_spans):
        span = max(2.0, b - a)
        src = os.path.join(SFXD, bed + ".mp3")
        if not el._exists(src):
            print(f"   WARN missing atmo bed {bed}")
            continue
        looped = os.path.join(WORK, f"atmo_{i}_loop.wav")
        loop_bed(src, span, 0.28, looped)
        # duck the looped atmo under the speech bus
        ducked = os.path.join(WORK, f"atmo_{i}_duck.wav")
        run([FF, "-y", "-i", looped, "-i", bus, "-filter_complex",
             "[0:a][1:a]sidechaincompress=threshold=0.02:ratio=8:attack=5:release=300[o]",
             "-map", "[o]", ducked])
        placed = os.path.join(WORK, f"atmo_{i}_placed.wav")
        delayed(ducked, a, placed, vol=1.0)
        layers.append(placed)
        print(f"   atmo {bed} @ {a:.1f}-{b:.1f}s")

    # -- music: motif at each 'motif' event (fade in/out), stinger at 'stinger',
    #    'stop' events just bound the preceding motif so we clip its length.
    def next_stop_after(t):
        cand = [e[2] for e in music_events if e[0] == "stop" and e[2] > t]
        return min(cand) if cand else None

    mi = 0
    for action, bed, at in music_events:
        if action == "stop":
            continue
        src = os.path.join(MUSD, bed + ".mp3")
        if not el._exists(src):
            print(f"   WARN missing music bed {bed}")
            continue
        placed = os.path.join(WORK, f"mus_{mi}_placed.wav")
        if action == "motif":
            # play the motif at moderate level, faded; clip to next stop if any
            stop_at = next_stop_after(at)
            full = dur(src)
            length = full if stop_at is None else max(4.0, min(full, stop_at - at))
            tmp = os.path.join(WORK, f"mus_{mi}_bed.wav")
            run([FF, "-y", "-i", src, "-t", f"{length:.3f}", "-af",
                 f"volume=0.495,afade=t=in:st=0:d=2.0,"  # music -10%
                 f"afade=t=out:st={max(0,length-3.0):.3f}:d=3.0,"
                 "aformat=sample_rates=44100:channel_layouts=stereo", tmp])
            delayed(tmp, at, placed, vol=1.0)
        else:  # stinger / transition
            tmp = os.path.join(WORK, f"mus_{mi}_bed.wav")
            length = dur(src)
            run([FF, "-y", "-i", src, "-af",
                 f"volume=0.405,afade=t=in:st=0:d=1.0,"  # music -10%
                 f"afade=t=out:st={max(0,length-2.0):.3f}:d=2.0,"
                 "aformat=sample_rates=44100:channel_layouts=stereo", tmp])
            delayed(tmp, at, placed, vol=1.0)
        layers.append(placed)
        print(f"   music {action}:{bed} @ {at:.1f}s")
        mi += 1

    # -- final mix: amix all layers (speech dry, atmo/music placed), loudnorm
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


# ---------------------------------------------------------------- main
if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd == "parse":
        for e in parse():
            if e["t"] == "speech":
                print(f"[speech {e['idx']:03d} {e['who']}] {e['text'][:70]}")
            elif e["t"] == "act":
                print(f"--- ACT: {e['title']}")
            elif e["t"] == "atmo":
                print(f"[ATMO -> {e['bed']}] {e['raw'][:50]}")
            elif e["t"] == "music":
                print(f"[MUSIK -> {e['action']}:{e['bed']}] {e['raw'][:50]}")
            elif e["t"] == "pause":
                print("[PAUSE]")
        sys.exit(0)
    if cmd in ("gen", "all"):
        phase_gen()
    if cmd in ("mix", "all"):
        phase_mix()
