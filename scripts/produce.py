#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml", "markdown-it-py"]
# ///
"""produce.py — YAML-driven audio production engine for podcast and Hörspiel.

Usage:
    produce.py <spec.yaml> gen|mix|all|book|parse

The spec.yaml file describes all production parameters. See the project docs
for schema details.
"""
import os, re, sys, subprocess
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import el
import hoerspiel

# ---------------------------------------------------------------- ffmpeg auto-pick
def _pick(cands):
    for c in [c for c in cands if c]:
        try:
            subprocess.run([c, "-version"], capture_output=True, check=True); return c
        except Exception:
            pass
    raise SystemExit("no working ffmpeg/ffprobe found")

FF      = _pick([os.environ.get("FFMPEG_BIN"), "ffmpeg", "/usr/bin/ffmpeg"])
FFPROBE = _pick([os.environ.get("FFPROBE_BIN"), "ffprobe", "/usr/bin/ffprobe"])


# ---------------------------------------------------------------- KNOWN KEYS
KNOWN_TOPLEVEL = {
    "slug", "kind", "title", "model", "speakers", "audio_tags", "sfx",
    "music", "gaps", "output", "cue_rules", "speech_tempo", "strip_latex",
    "einlagen", "transcript", "hoerspiel", "stem_slug_len", "replace",
    "intro_audio", "bridge_audio",
}


# ---------------------------------------------------------------- SPEC LOADING
def load_spec(path):
    spec = yaml.safe_load(open(path, encoding="utf-8"))
    required = {"slug", "kind"}
    missing = required - set(spec.keys())
    if missing:
        sys.exit(f"spec missing required keys: {', '.join(sorted(missing))}")
    unknown = set(spec.keys()) - KNOWN_TOPLEVEL
    if unknown:
        sys.exit(f"spec has unknown top-level keys: {', '.join(sorted(unknown))}")
    return spec


# ---------------------------------------------------------------- SLUG HELPER
def _slug(s, n=32):
    """Strip markdown bold, strip punctuation, lowercase, collapse non-alnum to -."""
    s = re.sub(r"\*\*([^*]*)\*\*", r"\1", s)
    s = re.sub(r"\*([^*]*)\*",     r"\1", s)
    s = re.sub(r'[„""\"\'()\[\]]+', "", s).lower()
    s = re.sub(r"[^a-z0-9äöüß]+", "-", s).strip("-")
    return s[:n].strip("-") or "seg"


# ---------------------------------------------------------------- LATEX STRIP
def _strip_latex(text):
    """Remove common LaTeX markup."""
    text = re.sub(r"\$[^$]*\$", "", text)
    text = re.sub(r"\\[a-zA-Z]+\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\[a-zA-Z]+", "", text)
    return text.strip()


STRIP_MD = True   # convert markdown emphasis for TTS (see strip_md)

def strip_md(text):
    """Markdown → TTS text (library-based implementation using markdown-it-py).

    Parse inline tokens so block rules (lists, headers) can't mangle dialogue.
    Bold (`**x**`/`__x__`, strong tokens) → UPPERCASED for short spans
    (<=4 words AND <=30 chars); longer bold spans → inner text unchanged.
    Italic/emphasis (`*x*`/`_x_`), inline code, strikethrough, links → inner
    text only (strip the markup).  Returns clean text with no markdown characters.
    `_slug` lowercases, so this does not change stem filenames.
    """
    from markdown_it import MarkdownIt
    md = MarkdownIt()
    tokens = md.parseInline(text)
    # tokens is a list of Token; the first (and usually only) element has children
    out = []
    in_strong = False
    in_em = False
    strong_buf = []
    em_buf = []

    children = tokens[0].children if tokens else []
    for tok in children:
        t = tok.type
        if t == "softbreak" or t == "hardbreak":
            out.append(" ")
            continue
        if t == "strong_open":
            in_strong = True
            strong_buf = []
            continue
        if t == "strong_close":
            in_strong = False
            inner = "".join(strong_buf)
            if len(inner) <= 30 and len(inner.split()) <= 4:
                out.append(inner.upper())
            else:
                out.append(inner)
            continue
        if t == "em_open":
            in_em = True
            em_buf = []
            continue
        if t == "em_close":
            in_em = False
            out.append("".join(em_buf))
            continue
        if t == "code_inline":
            # Inline code — preserve backtick wrapping so apply_audio_tags can
            # match `[cue]` patterns downstream (its regex expects the backticks).
            content = "`" + tok.content + "`"
            if in_strong:
                strong_buf.append(content)
            elif in_em:
                em_buf.append(content)
            else:
                out.append(content)
            continue
        if t in ("link_open", "link_close", "image", "html_inline"):
            continue
        if t == "text" or t == "html_block":
            content = tok.content
            if in_strong:
                strong_buf.append(content)
            elif in_em:
                em_buf.append(content)
            else:
                out.append(content)
            continue
        # Any other token type — try to grab content if present
        if hasattr(tok, "content") and tok.content:
            content = tok.content
            if in_strong:
                strong_buf.append(content)
            elif in_em:
                em_buf.append(content)
            else:
                out.append(content)

    return "".join(out)


# ---------------------------------------------------------------- INLINE TAG TRANSFORM
def apply_audio_tags(text, audio_tags, model):
    """Replace `[DE stage dir]` with ElevenLabs tag or remove.

    If model starts with 'eleven_v3', apply audio_tags mapping (unknown → strip).
    Otherwise, strip all `[...]` cues.
    """
    use_v3 = model.startswith("eleven_v3")
    def _sub(m):
        key = m.group(1).strip().lower()
        if use_v3:
            return audio_tags.get(key, "")
        return ""
    return re.sub(r"`\[([^\]]+)\]`", _sub, text).strip()


# ---------------------------------------------------------------- SPOKEN-TEXT REPLACE
def apply_replace(text, replace_map):
    """Apply spoken-text substitutions before slug + TTS.

    replace_map: ordered {regex_pattern: replacement}, applied case-sensitively
    in order. Used for pronunciation fixes and in-dialogue renames
    (e.g. Moderator->Beni). Computing the slug from the replaced
    text means changing a rule invalidates only the affected cached stems.
    """
    for pat, repl in replace_map.items():
        text = re.sub(pat, repl, text)
    return text


# ---------------------------------------------------------------- TTS NORMALIZE
NORMALIZE_TTS = True   # normalize punctuation that the TTS renders as long dead-air

def _normalize_tts(text):
    """Normalize TTS-hostile punctuation before sending to ElevenLabs.

    The ellipsis '…' (U+2026) makes eleven_multilingual_v2 insert a long pause
    that a low-stability voice fills with breaths/mumbles/artifacts; a plain
    period is a clean short beat. (The em-dash '—' measures clean — a normal
    short pause — and is left untouched.) Applied to every spoken segment; a
    no-op for text that has no ellipsis and no space-before-punctuation.
    """
    text = text.replace("…", ".")
    text = re.sub(r"\.\s*\.", ".", text)          # collapse consecutive periods
    text = re.sub(r"\s+([.,!?;:])", r"\1", text)  # drop space before punctuation
    text = re.sub(r"^\s*[.\s]+", "", text)         # strip leading dots/space
    text = re.sub(r"\s{2,}", " ", text).strip()
    return text


# ---------------------------------------------------------------- PARSE (PODCAST)
def parse_podcast(spec):
    """Parse transcript and return list of events."""
    transcript_path = os.path.join(ROOT, spec["transcript"])
    lines = open(transcript_path, encoding="utf-8").read().splitlines()

    # Find <!-- start --> and <!-- end --> markers
    start_idx = end_idx = None
    for i, line in enumerate(lines):
        s = line.strip()
        if s == "<!-- start -->":
            start_idx = i
        elif s == "<!-- end -->":
            end_idx = i
            break
    if start_idx is None:
        sys.exit(f"transcript missing <!-- start --> marker: {transcript_path}")
    if end_idx is None:
        sys.exit(f"transcript missing <!-- end --> marker: {transcript_path}")

    body_lines = lines[start_idx + 1 : end_idx]

    model = spec.get("model", "eleven_v3")
    speakers = spec.get("speakers", {})
    audio_tags = spec.get("audio_tags", {})
    cue_rules = spec.get("cue_rules", [])
    do_strip_latex = spec.get("strip_latex", False)
    einlagen = spec.get("einlagen", {})
    slug_len = spec.get("stem_slug_len", 32)
    replace_map = spec.get("replace", {})

    # Build speaker regex from all role names
    role_pattern = "|".join(re.escape(r) for r in speakers.keys())
    SPEAKER_RE = re.compile(rf"^\*\*({role_pattern}):\*\*\s*(.*)", re.S)
    PURE_CUE_RE = re.compile(r"^`\[([^\]]+)\]`\s*$")
    EINLAGE_RE = re.compile(r"^>>>\s*HÖRSPIEL-EINLAGE\s+(\d+)\s*$")

    events = []
    idx = 0
    cur_role = None   # for two-line speaker format: **ROLE:**\ntext on subsequent lines
    first_section = True   # track whether we've seen the first section boundary

    for raw in body_lines:
        s = raw.strip()
        if not s or s == "---":
            continue
        if s.startswith("#"):
            cur_role = None
            # Detect section boundaries (## lines) for bridge events
            if re.match(r"^##\s", s):
                if first_section:
                    first_section = False
                else:
                    events.append({"t": "bridge"})
            continue

        # Hörspiel-Einlage marker
        em = EINLAGE_RE.match(s)
        if em:
            n = int(em.group(1))
            events.append({"t": "einlage", "n": n})
            cur_role = None
            continue

        # Standalone cue line
        m = PURE_CUE_RE.match(s)
        if m:
            cue_text = m.group(1)
            ev = classify_cue(cue_text, cue_rules)
            if ev:
                events.append(ev)
            cur_role = None
            continue

        # Speaker line
        sm = SPEAKER_RE.match(s)
        if sm:
            role, rest = sm.group(1), sm.group(2).strip()
            if rest:
                # inline: **ROLE:** text on same line — reset two-line tracking
                cur_role = None
            else:
                # two-line: **ROLE:**\n then text on following lines
                cur_role = role
                continue
        elif cur_role is not None:
            # text paragraph under a two-line speaker marker (may span multiple paras)
            role = cur_role
            rest = s
            # keep cur_role so subsequent paragraphs under same speaker also match
        else:
            continue

        if not rest:
            continue

        # Apply inline tag transform BEFORE computing slug
        text = apply_audio_tags(strip_md(rest) if STRIP_MD else rest, audio_tags, model)
        if not text:
            continue
        if do_strip_latex:
            text = _strip_latex(text)
        if replace_map:
            text = apply_replace(text, replace_map)
        if NORMALIZE_TTS:
            text = _normalize_tts(text)

        sp_cfg = speakers[role]
        speaker_key = sp_cfg["speaker_key"]
        voice_id = sp_cfg["voice_id"]
        slug_n = _slug(text, slug_len)
        stem = os.path.join(ROOT, "out", spec["slug"], "voices",
                            f"{idx:03d}_{speaker_key}_{slug_n}.mp3")
        events.append({
            "t": "speech",
            "role": role,
            "speaker_key": speaker_key,
            "voice_id": voice_id,
            "text": text,
            "idx": idx,
            "stem": stem,
        })
        idx += 1

    return events


def classify_cue(cue_text, cue_rules):
    """Match cue_text against cue_rules (first-match, all keywords must appear)."""
    t = cue_text.lower()
    for rule in cue_rules:
        keywords = rule.get("keywords", [])
        if all(kw in t for kw in keywords):
            ev = {}
            if "sfx" in rule:
                ev["t"] = "sfx"
                ev["key"] = rule["sfx"]
            elif "action" in rule:
                ev["t"] = "music"
                ev["action"] = rule["action"]
                if "music" in rule:
                    ev["key"] = rule["music"]
            else:
                return None
            return ev
    return None


# ---------------------------------------------------------------- PARSE PHASE (CLI)
def phase_parse(spec):
    events = parse_podcast(spec)
    speech  = [e for e in events if e["t"] == "speech"]
    bridges = [e for e in events if e["t"] == "bridge"]
    other   = [e for e in events if e["t"] not in ("speech", "bridge")]
    print(f"== parse: {len(speech)} speech segments, "
          f"{sum(len(e['text']) for e in speech)} chars, "
          f"{len(bridges)} bridge(s) ==")
    for ev in events:
        if ev["t"] == "speech":
            idx = ev["idx"]
            print(f"  {idx:03d} [{ev['speaker_key']:12s}] {ev['text'][:60]}")
        elif ev["t"] == "sfx":
            print(f"  SFX  {ev['key']}")
        elif ev["t"] == "music":
            print(f"  MUSIC action={ev['action']}" +
                  (f" key={ev['key']}" if "key" in ev else ""))
        elif ev["t"] == "einlage":
            print(f"  EINLAGE n={ev['n']}")
        elif ev["t"] == "bridge":
            print(f"  BRIDGE")


# ---------------------------------------------------------------- GEN PHASE (PODCAST)
def phase_gen_podcast(spec):
    events = parse_podcast(spec)
    speech = [e for e in events if e["t"] == "speech"]
    print(f"== gen: {len(speech)} speech segments ==")
    model = spec.get("model", "eleven_v3")
    speakers = spec.get("speakers", {})

    out_dir = os.path.join(ROOT, "out", spec["slug"])
    sfx_dir  = os.path.join(out_dir, "sfx")
    mus_dir  = os.path.join(out_dir, "music")
    for d in (sfx_dir, mus_dir):
        os.makedirs(d, exist_ok=True)

    print("== voices ==")
    for ev in speech:
        stem = ev["stem"]
        os.makedirs(os.path.dirname(stem), exist_ok=True)
        sp_cfg = speakers[ev["role"]]
        kw = dict(
            model=model,
            stability=sp_cfg.get("stability", 0.5),
            similarity=sp_cfg.get("similarity", 0.8),
            speaker_boost=sp_cfg.get("speaker_boost", True),
            skip_existing=True,
        )
        if "style" in sp_cfg:
            kw["style"] = sp_cfg["style"]
        if "speed" in sp_cfg:
            kw["speed"] = sp_cfg["speed"]
        if el._exists(stem):
            print(f"  skip: {os.path.basename(stem)}")
        else:
            el.tts(ev["voice_id"], ev["text"], stem, **kw)
            print(f"  ok  : {os.path.basename(stem)} ({len(ev['text'])}c)")

    print("== sfx ==")
    for name, s_spec in spec.get("sfx", {}).items():
        out = os.path.join(sfx_dir, name + ".mp3")
        dur = s_spec.get("dur")
        if el._exists(out):
            print(f"  skip: sfx:{name}")
        else:
            el.sfx(s_spec["prompt"], out, duration=dur, skip_existing=True)
            print(f"  ok  : sfx:{name}")

    print("== music ==")
    for name, m_spec in spec.get("music", {}).items():
        out = os.path.join(mus_dir, name + ".mp3")
        if el._exists(out):
            print(f"  skip: music:{name}")
        else:
            el.music(m_spec["prompt"], out, m_spec["ms"], skip_existing=True)
            print(f"  ok  : music:{name}")

    print("GEN DONE")


# ---------------------------------------------------------------- MIX HELPERS
def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(" ".join(str(x) for x in cmd[:8]) + "\n" + r.stderr[-1500:] + "\n")
        raise SystemExit(f"command failed ({r.returncode})")
    return r

def dur_of(path):
    r = subprocess.run(
        [FFPROBE, "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True)
    return float(r.stdout.strip())

def norm(inp, outp, extra=""):
    filt = "aformat=sample_rates=44100:channel_layouts=stereo"
    if extra:
        filt = extra + "," + filt
    run([FF, "-y", "-i", inp, "-af", filt, "-c:a", "flac", outp])

def silence(secs, outp):
    run([FF, "-y", "-f", "lavfi", "-t", f"{secs:.3f}",
         "-i", "anullsrc=r=44100:cl=stereo", "-c:a", "flac", outp])

def loop_bed(src, length, vol, outp):
    fade_out = max(0.0, length - 3.0)
    run([FF, "-y", "-stream_loop", "-1", "-i", src,
         "-t", f"{length:.3f}",
         "-af", (f"volume={vol},"
                 f"afade=t=in:st=0:d=2.0,"
                 f"afade=t=out:st={fade_out:.3f}:d=3.0,"
                 "aformat=sample_rates=44100:channel_layouts=stereo"),
         "-c:a", "flac", outp])

def underscore(src, vol, outp):
    """Render a named music bed as a low-volume, faded underscore (no loop).

    Used for keyed bed_on cues (e.g. a mysterious pad under a climax) so a short
    named bed plays quietly under the speech at that point rather than looping.
    """
    d = dur_of(src)
    fo = max(0.0, d - 3.0)
    run([FF, "-y", "-i", src,
         "-af", (f"volume={vol},"
                 f"afade=t=in:st=0:d=1.5,"
                 f"afade=t=out:st={fo:.3f}:d=3.0,"
                 "aformat=sample_rates=44100:channel_layouts=stereo"),
         "-c:a", "flac", outp])


# ---------------------------------------------------------------- MIX PHASE (PODCAST)
def phase_mix_podcast(spec):
    events = parse_podcast(spec)
    out_dir = os.path.join(ROOT, "out", spec["slug"])
    sfx_dir  = os.path.join(out_dir, "sfx")
    mus_dir  = os.path.join(out_dir, "music")
    work_dir = os.path.join(out_dir, "work")
    os.makedirs(work_dir, exist_ok=True)

    gaps = spec.get("gaps", {})
    GAP_BASE   = gaps.get("base",    0.55)
    GAP_SWITCH = gaps.get("switch",  0.90)
    GAP_SFX    = gaps.get("sfx_tail", 0.35)
    speech_tempo = spec.get("speech_tempo")
    loudnorm_params = spec.get("output", {}).get("loudnorm", "I=-16:TP=-1.5:LRA=11")
    einlagen = spec.get("einlagen", {})
    intro_audio  = spec.get("intro_audio")
    bridge_audio = spec.get("bridge_audio")

    # Build speech bus
    pieces = []; t = 0.0; prev_role = None
    bed_on = False; bed_start = None; bed_spans = []
    overlays = []   # (kind, key, t_seconds)

    def add_sil(sec):
        nonlocal t
        if sec <= 0: return
        p = os.path.join(work_dir, f"sil_{len(pieces)}.flac")
        silence(sec, p); pieces.append(p); t += sec

    def insert_audio_file(rel_path, label):
        """Normalize a ROOT-relative audio file into the speech bus. Returns True on success."""
        nonlocal t
        full = os.path.join(ROOT, rel_path)
        if not os.path.exists(full):
            print(f"  warn: {label} file not found: {full}, skipping")
            return False
        w = os.path.join(work_dir, f"{label}_{len(pieces)}.flac")
        norm(full, w)
        pieces.append(w)
        t += dur_of(w)
        return True

    # Optional intro audio — first piece on the speech bus, followed by GAP_SWITCH
    if intro_audio:
        if insert_audio_file(intro_audio, "intro"):
            add_sil(GAP_SWITCH)
            prev_role = None   # reset so first speech line gets no gap

    for ev in events:
        k = ev["t"]

        if k == "bridge":
            if bridge_audio:
                add_sil(GAP_SWITCH)
                if insert_audio_file(bridge_audio, "bridge"):
                    add_sil(GAP_SFX)
                prev_role = None   # treat next speech after bridge as a fresh start
            continue

        if k == "music":
            action = ev["action"]
            if action == "intro":
                key = ev.get("key", "title_motif")
                overlays.append(("motif", key, t))
                bed_start = t; bed_on = True
            elif action == "stinger":
                key = ev.get("key", "transition")
                overlays.append(("stinger", key, t))
            elif action == "bed_on":
                key = ev.get("key")
                if key:
                    # named bed → low-volume faded underscore at this point
                    overlays.append(("underscore", key, t))
                else:
                    if not bed_on:
                        bed_start = t; bed_on = True
            elif action == "outro":
                if bed_on:
                    bed_spans.append((bed_start, t)); bed_on = False
                key = ev.get("key", "title_motif")
                overlays.append(("motif", key, t))
            continue

        if k == "sfx":
            sfx_p = os.path.join(sfx_dir, ev["key"] + ".mp3")
            if os.path.exists(sfx_p):
                w = os.path.join(work_dir, f"sfx_{len(pieces)}.flac")
                norm(sfx_p, w); pieces.append(w); t += dur_of(w)
                add_sil(GAP_SFX)
            continue

        if k == "einlage":
            n = ev["n"]
            einlage_path = einlagen.get(str(n)) or einlagen.get(n)
            if einlage_path:
                full_path = os.path.join(ROOT, einlage_path)
                w = os.path.join(work_dir, f"einlage_{n}.flac")
                run([FF, "-y", "-i", full_path,
                     "-af", "aformat=sample_rates=44100:channel_layouts=stereo",
                     "-c:a", "flac", w])
                pieces.append(w); t += dur_of(w)
            continue

        if k == "speech":
            gap = GAP_BASE
            if prev_role is not None and ev["role"] != prev_role:
                gap = GAP_SWITCH
            if prev_role is None and not pieces:
                gap = 0.0
            add_sil(gap)
            stem = ev["stem"]
            w = os.path.join(work_dir, "n_" + os.path.basename(stem) + ".flac")
            norm(stem, w)
            pieces.append(w); t += dur_of(w); prev_role = ev["role"]

    if bed_on:
        bed_spans.append((bed_start, t))
    add_sil(1.2)

    # Concat speech bus
    if not pieces:
        sys.exit("mix: no pieces to concat")

    # Optional: apply speech tempo to a temp bus first if needed
    # We'll build the bus from pieces and then apply atempo if set
    bus_raw = os.path.join(work_dir, "speech_bus_raw.flac")
    n = len(pieces)
    inputs = []
    for p in pieces: inputs += ["-i", p]
    fc = "".join(f"[{i}:a]" for i in range(n)) + f"concat=n={n}:v=0:a=1[o]"
    run([FF, "-y", *inputs, "-filter_complex", fc, "-map", "[o]", "-c:a", "flac", bus_raw])

    if speech_tempo and speech_tempo != 1.0:
        bus = os.path.join(work_dir, "speech_bus.flac")
        run([FF, "-y", "-i", bus_raw,
             "-af", f"atempo={speech_tempo},aformat=sample_rates=44100:channel_layouts=stereo",
             "-c:a", "flac", bus])
        total = dur_of(bus)
    else:
        bus = bus_raw
        total = t

    print(f"   speech bus: {total:.1f}s")

    layers = ["-i", bus]
    delay_ms_list = []

    # Ambient bed segments
    bed_key = "bed"  # default bed music key
    for i, (s_t, e_t) in enumerate(bed_spans):
        length = e_t - s_t
        src = os.path.join(mus_dir, bed_key + ".mp3")
        if not os.path.exists(src):
            print(f"  warn: bed music not found: {src}, skipping bed segment")
            continue
        seg = os.path.join(work_dir, f"bed_seg_{i}.flac")
        loop_bed(src, length, 0.10, seg)
        layers += ["-i", seg]; delay_ms_list.append(int(s_t * 1000))

    # Motif / stinger overlays
    for kind, key, ts in overlays:
        src = os.path.join(mus_dir, key + ".mp3")
        if not os.path.exists(src):
            print(f"  warn: overlay music not found: {src}, skipping")
            continue
        w = os.path.join(work_dir, f"ov_{kind}_{len(delay_ms_list)}.flac")
        if kind == "underscore":
            underscore(src, 0.12, w)
        else:
            norm(src, w)
        layers += ["-i", w]; delay_ms_list.append(int(ts * 1000))

    out_final_name = spec.get("output", {}).get("final", "output.mp3")
    out_path = os.path.join(out_dir, out_final_name)

    if not delay_ms_list:
        run([FF, "-y", "-i", bus,
             "-af", f"loudnorm={loudnorm_params}",
             "-codec:a", "libmp3lame", "-q:a", "2", out_path])
    else:
        n_extra = len(delay_ms_list)
        n_total = 1 + n_extra
        filter_parts = []
        for i, d in enumerate(delay_ms_list):
            idx2 = i + 1
            filter_parts.append(f"[{idx2}:a]adelay={d}|{d}[l{idx2}]")
        mixed = "[0:a]" + "".join(f"[l{i+1}]" for i in range(n_extra))
        fc2 = (";".join(filter_parts)
               + f";{mixed}amix=inputs={n_total}:normalize=0:duration=first[mix]"
               + f";[mix]loudnorm={loudnorm_params}[out]")
        run([FF, "-y", *layers,
             "-filter_complex", fc2, "-map", "[out]",
             "-codec:a", "libmp3lame", "-q:a", "2", out_path])

    print(f"MIX DONE → {out_path}")


# ---------------------------------------------------------------- HOERSPIEL PATH
def run_hoerspiel(spec, cmd):
    hs = spec.get("hoerspiel")
    if not hs:
        sys.exit("spec missing 'hoerspiel' section for kind: hoerspiel")

    model = spec.get("model")
    narr_out_id = hs.get("narr_out_id")

    # Build voices dict from top-level speakers (ROLE -> voice_id)
    # or fall back to legacy hs["voices"] for backward compat
    if "voices" in hs:
        voices = hs["voices"]
    else:
        speakers = spec.get("speakers", {})
        voices = {role: cfg["voice_id"] for role, cfg in speakers.items()}

    # slug: top-level spec["slug"] (SPEC §4.1) or legacy hs["slug"] for backward compat
    slug = spec.get("slug") or hs.get("slug")
    if not slug:
        sys.exit("spec missing 'slug'")

    sc = hoerspiel.Scene(
        slug=slug,
        title=hs.get("title", spec.get("title", "")),
        scene_index=hs.get("scene_index", 1),
        voices=voices,
        reverb_roles=hs.get("reverb_roles", []),
        drama=hs["drama"],
        narr_heraus=hs["narr_heraus"],
        sfx=hs.get("sfx", spec.get("sfx", {})),
        music=hs.get("music", spec.get("music", {})),
        display=hs.get("display", {}),
        bed=hs.get("bed_sfx", hs.get("bed", "atmo_base")),
        analysis=hs.get("analysis_list", hs.get("analysis")),
        name=hs.get("name"),
        source_md=hs.get("source_md"),
        narr_out_id=narr_out_id,
    )

    if cmd in ("gen", "all"):
        hoerspiel.phase_gen(sc, model=model)
    if cmd in ("mix", "all"):
        hoerspiel.phase_mix(sc)
    if cmd in ("book", "all"):
        hoerspiel.phase_book(sc)


# ---------------------------------------------------------------- MAIN
def main():
    if len(sys.argv) < 3:
        sys.exit("usage: produce.py <spec.yaml> gen|mix|all|book|parse")
    spec_path = sys.argv[1]
    cmd = sys.argv[2]

    if not os.path.exists(spec_path):
        # Try relative to ROOT
        spec_path_abs = os.path.join(ROOT, spec_path)
        if os.path.exists(spec_path_abs):
            spec_path = spec_path_abs
        else:
            sys.exit(f"spec not found: {sys.argv[1]}")

    spec = load_spec(spec_path)
    kind = spec.get("kind", "podcast")

    if kind == "podcast":
        if cmd == "parse":
            phase_parse(spec)
        elif cmd == "gen":
            phase_gen_podcast(spec)
        elif cmd == "mix":
            phase_mix_podcast(spec)
        elif cmd == "all":
            phase_gen_podcast(spec)
            phase_mix_podcast(spec)
        else:
            sys.exit(f"unknown command for kind=podcast: {cmd} (use gen|mix|all|parse)")

    elif kind == "hoerspiel":
        if cmd == "parse":
            hs = spec.get("hoerspiel", {})
            drama = hs.get("drama", [])
            speech = [e for e in drama if "id" in e]
            cues   = [e for e in drama if "cue" in e]
            total_chars = sum(len((e.get("tag", "") + " " + e["text"]).strip()) for e in speech)
            print(f"== parse: {len(speech)} speech items, {len(cues)} cue items, "
                  f"{total_chars} chars (incl. tags) ==")
            for e in drama:
                if "id" in e:
                    tag = e.get("tag", "")
                    preview = (tag + " " + e["text"]).strip()[:60]
                    print(f"  {e['id']:20s} [{e['who']:10s}] gap={e['gap']:.2f}  {preview}")
                else:
                    print(f"  CUE: {e['cue']} gain={e['gain']}")
        else:
            run_hoerspiel(spec, cmd)

    else:
        sys.exit(f"unknown kind: {kind!r} (expected 'podcast' or 'hoerspiel')")


if __name__ == "__main__":
    main()
