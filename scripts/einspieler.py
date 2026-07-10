#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml"]
# ///
"""einspieler.py — produce short musical "Einspieler" (documentary inserts).

Usage:
    einspieler.py <spec.yaml> parse|gen|build|all

Each Einspieler is a bookend sound + the ERZÄHLER voice over a background-music
bed (music_vol) + the bookend sound again. The transcript is markdown with one
section per Einspieler headed `## 1`, `## 2`, … `## 13`; all prose lines under a
header (until the next `##`) form that segment's narrator text — there is no
`**ERZÄHLER:**` label. Music is assigned per segment via the spec's `assign`
list (letter → `music_tracks`).

Reuses produce.py for the ffmpeg binary resolution, the `run(...)` runner,
`dur_of(...)`, `ROOT`, `load_spec(...)` and the text-slug helper, so stem naming
and command execution stay identical to the main engine.
"""
import os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import produce  # noqa: E402  (reuse ROOT, load_spec, _slug, run, dur_of, FF)
import el        # noqa: E402  (reuse the tts() generator)

ROOT = produce.ROOT


# ---------------------------------------------------------------- SPEC LOADING
def load_spec(path):
    """Load the YAML spec (no schema validation — einspieler keys differ from
    produce.py's KNOWN_TOPLEVEL, so we read the file directly)."""
    import yaml
    spec = yaml.safe_load(open(path, encoding="utf-8"))
    for req in ("slug", "kind", "transcript", "speaker", "bookend", "music_tracks", "assign"):
        if req not in spec:
            sys.exit(f"spec missing required key: {req}")
    if spec.get("kind") != "einspieler":
        sys.exit(f"expected kind: einspieler, got {spec.get('kind')!r}")
    return spec


# ---------------------------------------------------------------- TRANSCRIPT PARSE
def parse_segments(spec):
    """Parse the transcript into an ordered list of (n:int, text:str).

    Sections are headed `## N`; the segment text is every prose line under that
    header (joined with spaces) until the next `##` header. Blank lines and any
    other `#`-level headings are ignored.
    """
    transcript_path = os.path.join(ROOT, spec["transcript"])
    if not os.path.exists(transcript_path):
        sys.exit(f"transcript not found: {transcript_path}")
    lines = open(transcript_path, encoding="utf-8").read().splitlines()

    SEC_RE = re.compile(r"^##\s+(\d+)\s*$")
    segments = []
    cur_n = None
    buf = []

    def flush():
        if cur_n is not None:
            text = " ".join(buf).strip()
            if text:
                segments.append((cur_n, text))

    for raw in lines:
        s = raw.strip()
        m = SEC_RE.match(s)
        if m:
            flush()
            cur_n = int(m.group(1))
            buf = []
            continue
        if s.startswith("#"):
            # any other heading level ends the current segment's prose
            continue
        if not s:
            continue
        if cur_n is not None:
            buf.append(s)
    flush()

    segments.sort(key=lambda x: x[0])
    return segments


# ---------------------------------------------------------------- PATH HELPERS
def voice_stem_path(spec, n, text):
    """Voice-stem path — textslug via produce._slug so changed text re-gens only
    that stem (mirrors produce.phase_gen_podcast's `{idx}_{key}_{slug}.mp3`)."""
    slug_n = produce._slug(text)
    return os.path.join(ROOT, "out", spec["slug"], "voices",
                        f"{n:02d}_erzaehler_{slug_n}.mp3")


def output_path(spec, n):
    """Final mixed Einspieler — 2-digit zero-padded (einspieler_01.mp3 …)."""
    return os.path.join(ROOT, "out", spec["slug"], f"einspieler_{n:02d}.mp3")


def music_track_for(spec, n):
    """Resolve segment n (1-based) to its ROOT-relative music track path via
    assign[n-1] → music_tracks[letter]."""
    assign = spec["assign"]
    letter = assign[n - 1]                     # per Einspieler 1..N
    return spec["music_tracks"][letter], letter


# ---------------------------------------------------------------- PARSE PHASE (CLI)
def phase_parse(spec):
    segments = parse_segments(spec)
    print(f"== parse: {len(segments)} Einspieler ==")
    for n, text in segments:
        rel, letter = music_track_for(spec, n)
        stem = voice_stem_path(spec, n, text)
        out = output_path(spec, n)
        print(f"  {n:02d}  {len(text):4d}c  track={letter}  \"{text[:50]}\"")
        print(f"      voice → {os.path.relpath(stem, ROOT)}")
        print(f"      out   → {os.path.relpath(out, ROOT)}")


# ---------------------------------------------------------------- GEN PHASE (spends credits)
def phase_gen(spec):
    """TTS each segment's narrator text to its voice stem (skip if it exists).

    Mirrors produce.phase_gen_podcast's el.tts(...) call — same model + voice
    settings, skip_existing=True so re-runs never re-spend credits.
    """
    segments = parse_segments(spec)
    print(f"== gen: {len(segments)} voice stems ==")
    model = spec.get("model", "eleven_v3")
    sp = spec["speaker"]

    for n, text in segments:
        stem = voice_stem_path(spec, n, text)
        os.makedirs(os.path.dirname(stem), exist_ok=True)
        if el._exists(stem):
            print(f"  skip: {os.path.basename(stem)}")
            continue
        el.tts(
            sp["voice_id"], text, stem,
            model=model,
            stability=sp.get("stability", 0.5),
            similarity=sp.get("similarity", 0.75),
            speaker_boost=sp.get("speaker_boost", True),
            skip_existing=True,
        )
        print(f"  ok  : {os.path.basename(stem)} ({len(text)}c)")
    print("GEN DONE")


# ---------------------------------------------------------------- MIX HELPERS
def _norm(inp, outp):
    """Normalize any audio file to 44100Hz stereo FLAC (produce.norm without
    the extra-filter arg)."""
    produce.run([produce.FF, "-y", "-i", inp,
                 "-af", "aformat=sample_rates=44100:channel_layouts=stereo",
                 "-c:a", "flac", outp])


def _silence(secs, outp):
    """Emit `secs` of 44100Hz stereo silence as FLAC (mirrors produce.silence)."""
    produce.run([produce.FF, "-y", "-f", "lavfi", "-t", f"{secs:.3f}",
                 "-i", "anullsrc=r=44100:cl=stereo", "-c:a", "flac", outp])


def _concat(pieces, outp):
    """Concatenate FLAC pieces into one FLAC via the concat filter."""
    inputs = []
    for p in pieces:
        inputs += ["-i", p]
    n = len(pieces)
    fc = "".join(f"[{i}:a]" for i in range(n)) + f"concat=n={n}:v=0:a=1[o]"
    produce.run([produce.FF, "-y", *inputs, "-filter_complex", fc,
                 "-map", "[o]", "-c:a", "flac", outp])


# ---------------------------------------------------------------- BUILD PHASE (free ffmpeg)
def phase_build(spec):
    """For each segment: bookend + voice(over music bed) + bookend → final MP3."""
    produce._ensure_ffmpeg()
    segments = parse_segments(spec)
    print(f"== build: {len(segments)} Einspieler ==")

    out_dir  = os.path.join(ROOT, "out", spec["slug"])
    work_dir = os.path.join(out_dir, "work")
    os.makedirs(work_dir, exist_ok=True)

    gaps = spec.get("gaps", {})
    gap_bookend  = gaps.get("bookend", 0.20)
    fade_in      = gaps.get("music_fade_in", 2.0)
    fade_out     = gaps.get("music_fade_out", 2.5)
    music_vol    = float(spec.get("music_vol", 0.40))
    loudnorm     = spec.get("output", {}).get("loudnorm", "I=-16:TP=-1.5:LRA=11")

    bookend_src = os.path.join(ROOT, spec["bookend"])
    if not os.path.exists(bookend_src):
        sys.exit(f"bookend file not found: {bookend_src}")

    # Normalize the bookend once — it is reused at head and tail of every segment.
    bookend_n = os.path.join(work_dir, "bookend.flac")
    _norm(bookend_src, bookend_n)

    for n, text in segments:
        stem = voice_stem_path(spec, n, text)
        if not el._exists(stem):
            print(f"  warn: voice stem missing for {n:02d}, skipping: "
                  f"{os.path.relpath(stem, ROOT)}")
            continue

        # 1. normalize the voice stem to 44100Hz stereo FLAC
        voice_n = os.path.join(work_dir, f"voice_{n:02d}.flac")
        _norm(stem, voice_n)

        # 2. foreground = bookend + gap + voice + gap + bookend
        gap_p = os.path.join(work_dir, f"gap_{n:02d}.flac")
        _silence(gap_bookend, gap_p)
        fg = os.path.join(work_dir, f"foreground_{n:02d}.flac")
        _concat([bookend_n, gap_p, voice_n, gap_p, bookend_n], fg)

        # 3. music bed looped to the foreground length, at music_vol with fades
        F = produce.dur_of(fg)
        fo_start = max(0.0, F - fade_out)
        track_rel, _letter = music_track_for(spec, n)
        track_src = os.path.join(ROOT, track_rel)
        if not os.path.exists(track_src):
            print(f"  warn: music track missing for {n:02d}, skipping: {track_src}")
            continue
        bed = os.path.join(work_dir, f"bed_{n:02d}.flac")
        produce.run([produce.FF, "-y", "-stream_loop", "-1", "-i", track_src,
                     "-t", f"{F:.3f}",
                     "-af", (f"volume={music_vol},"
                             f"afade=t=in:st=0:d={fade_in},"
                             f"afade=t=out:st={fo_start:.3f}:d={fade_out},"
                             "aformat=sample_rates=44100:channel_layouts=stereo"),
                     "-c:a", "flac", bed])

        # 4. mix foreground over the bed, loudness-normalize, encode to MP3
        out_path = output_path(spec, n)
        produce.run([produce.FF, "-y", "-i", fg, "-i", bed,
                     "-filter_complex",
                     ("[0:a][1:a]amix=inputs=2:normalize=0:duration=first[m];"
                      f"[m]loudnorm={loudnorm}[out]"),
                     "-map", "[out]",
                     "-codec:a", "libmp3lame", "-q:a", "2", out_path])
        print(f"  ok  : {os.path.basename(out_path)} ({F:.1f}s)")
    print("BUILD DONE")


# ---------------------------------------------------------------- MAIN
def main():
    if len(sys.argv) < 3:
        sys.exit("usage: einspieler.py <spec.yaml> parse|gen|build|all")
    spec_path = sys.argv[1]
    cmd = sys.argv[2]

    if not os.path.exists(spec_path):
        spec_path_abs = os.path.join(ROOT, spec_path)
        if os.path.exists(spec_path_abs):
            spec_path = spec_path_abs
        else:
            sys.exit(f"spec not found: {sys.argv[1]}")

    spec = load_spec(spec_path)

    if cmd == "parse":
        phase_parse(spec)
    elif cmd == "gen":
        phase_gen(spec)
    elif cmd == "build":
        phase_build(spec)
    elif cmd == "all":
        phase_gen(spec)
        phase_build(spec)
    else:
        sys.exit(f"unknown command: {cmd} (use parse|gen|build|all)")


if __name__ == "__main__":
    main()
