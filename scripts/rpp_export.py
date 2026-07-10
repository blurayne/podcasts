#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml", "markdown-it-py"]
# ///
"""
rpp_export.py — turn a produce.py podcast spec into an editable REAPER project.

The generic engine (scripts/produce.py) renders a deterministic single-file mix
with ffmpeg: a sequential *speech bus* (voice + silence + sfx + einlagen laid
end to end) with *music overlays* (beds, motifs, stingers, underscores) mixed on
top at absolute time offsets. This tool walks the SAME timeline arithmetic but,
instead of concatenating, emits a multi-lane REAPER project (.RPP) that
references the already-generated stems in out/<slug>/ at their exact offsets:

    VOICE        every speech stem at its cumulative offset
    SFX          every one-shot sfx at its offset
    EINLAGE      intro / bridge / Hörspiel-Einlagen inserts
    MUSIC · BED  looped ambient bed spans (track vol 0.10, matching produce.py)
    MUSIC · CUES motifs / stingers (vol 1.0) and underscores (item vol 0.12)

So you get BOTH: the reproducible ffmpeg mix (`produce.py <spec> mix`) AND a
hand-editable session (`rpp_export.py <spec>`) built from one source of truth.

Durations come from ffprobe on the real stems (produce.dur_of). Run AFTER `gen`
so the stems exist. `--fake-durations` fills nominal lengths for a structural
dry-run without ffmpeg/stems (the offsets are then only illustrative).

REAPER render:  reaper -renderproject <out.rpp>   (Linux: wrap in xvfb-run)
Set the render format once in File > Render, or keep ffmpeg for the final mix.
The recommended per-voice ReaPlugs chain is written to MIX-NOTES.md alongside
the project (not embedded — valid FX state must be captured from a real REAPER).
"""
import os, sys, argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import produce  # noqa: E402  (reuse the exact spec/parse/slug/dur logic)

ROOT = produce.ROOT


def _q(s):
    """Quote a REAPER string field (paths with spaces etc.)."""
    s = str(s)
    if '"' not in s:
        return f'"{s}"'
    if "'" not in s:
        return f"'{s}'"
    return "`" + s.replace("`", "'") + "`"


def _src_type(path):
    ext = os.path.splitext(path)[1].lower()
    return {".wav": "WAVE", ".flac": "FLAC", ".mp3": "MP3",
            ".ogg": "VORBIS", ".aiff": "WAVE", ".aif": "WAVE"}.get(ext, "MP3")


class Placement:
    __slots__ = ("lane", "path", "pos", "length", "name", "vol", "loop")
    def __init__(self, lane, path, pos, length, name, vol=1.0, loop=0):
        self.lane, self.path, self.pos, self.length = lane, path, pos, length
        self.name, self.vol, self.loop = name, vol, loop


def build_placements(spec, fake=None):
    """Mirror produce.phase_mix_podcast's timeline walk, emitting Placements
    on named lanes with absolute POSITIONs instead of concatenating pieces."""
    events = produce.parse_podcast(spec)
    slug = spec["slug"]
    sfx_dir = os.path.join(ROOT, "out", slug, "sfx")
    mus_dir = os.path.join(ROOT, "out", slug, "music")

    gaps = spec.get("gaps", {})
    GAP_BASE   = gaps.get("base", 0.55)
    GAP_SWITCH = gaps.get("switch", 0.90)
    GAP_SFX    = gaps.get("sfx_tail", 0.35)
    einlagen   = spec.get("einlagen", {})
    intro_audio  = spec.get("intro_audio")
    bridge_audio = spec.get("bridge_audio")
    music_gain = float(spec.get("music_gain", 1.0))

    # nominal lengths for --fake-durations dry-runs
    sfx_dur = {k: v.get("dur", 2) for k, v in (spec.get("sfx") or {}).items()}
    mus_ms  = {k: v.get("ms", 8000) for k, v in (spec.get("music") or {}).items()}

    def dur(path, kind=None, key=None):
        if fake is not None:
            if kind == "sfx":    return float(sfx_dur.get(key, 2))
            if kind == "music":  return mus_ms.get(key, 8000) / 1000.0
            if kind == "speech": return float(fake)
            return float(fake) * 2  # intro/bridge/einlage
        return produce.dur_of(path)

    out, t, prev_role = [], 0.0, None
    bed_on = False; bed_start = None; bed_spans = []; overlays = []
    placed_any = [False]  # mirror produce's "not pieces" first-line gap rule

    def sil(sec):
        nonlocal t
        if sec > 0:
            t += sec

    def insert(path, lane, name, kind=None):
        nonlocal t
        if fake is None and not os.path.exists(path):
            print(f"  warn: {lane} file not found, skipping: {path}")
            return False
        d = dur(path, kind=kind)
        out.append(Placement(lane, path, t, d, name))
        t += d
        placed_any[0] = True
        return True

    if intro_audio:
        p = os.path.join(ROOT, intro_audio)
        if insert(p, "EINLAGE", "intro", kind="insert"):
            sil(GAP_SWITCH)
            prev_role = None

    for ev in events:
        k = ev["t"]

        if k == "bridge":
            if bridge_audio:
                sil(GAP_SWITCH)
                if insert(os.path.join(ROOT, bridge_audio), "EINLAGE", "bridge",
                          kind="insert"):
                    sil(GAP_SFX)
                prev_role = None
            continue

        if k == "music":
            action = ev["action"]
            if action == "intro":
                overlays.append(("motif", ev.get("key", "title_motif"), t))
                bed_start = t; bed_on = True
            elif action == "stinger":
                overlays.append(("stinger", ev.get("key", "transition"), t))
            elif action == "bed_on":
                key = ev.get("key")
                if key:
                    overlays.append(("underscore", key, t))
                elif not bed_on:
                    bed_start = t; bed_on = True
            elif action == "outro":
                if bed_on:
                    bed_spans.append((bed_start, t)); bed_on = False
                overlays.append(("motif", ev.get("key", "title_motif"), t))
            continue

        if k == "sfx":
            p = os.path.join(sfx_dir, ev["key"] + ".mp3")
            if fake is not None or os.path.exists(p):
                d = dur(p, kind="sfx", key=ev["key"])
                out.append(Placement("SFX", p, t, d, ev["key"]))
                t += d; placed_any[0] = True
                sil(GAP_SFX)
            continue

        if k == "einlage":
            n = ev["n"]
            rel = einlagen.get(str(n)) or einlagen.get(n)
            if rel:
                insert(os.path.join(ROOT, rel), "EINLAGE",
                       f"einlage_{n}", kind="insert")
            continue

        if k == "speech":
            gap = GAP_BASE
            if prev_role is not None and ev["role"] != prev_role:
                gap = GAP_SWITCH
            if prev_role is None and not placed_any[0]:
                gap = 0.0
            sil(gap)
            insert(ev["stem"], "VOICE", os.path.basename(ev["stem"]),
                   kind="speech")
            prev_role = ev["role"]

    if bed_on:
        bed_spans.append((bed_start, t))

    # Ambient bed spans → looped item, track carries the 0.10 gain
    for i, (s_t, e_t) in enumerate(bed_spans):
        src = os.path.join(mus_dir, "bed.mp3")
        if fake is None and not os.path.exists(src):
            print(f"  warn: bed music not found, skipping span: {src}")
            continue
        out.append(Placement("MUSIC · BED", src, s_t, e_t - s_t,
                             f"bed_{i}", loop=1))

    # Motif / stinger / underscore overlays. Each music kind goes to its own
    # lane so the per-kind gain lives on the track (no fragile item-vol fields):
    # underscores quiet (0.12), motifs/stingers full (1.0), all × music_gain.
    for kind, key, ts in overlays:
        src = os.path.join(mus_dir, key + ".mp3")
        if fake is None and not os.path.exists(src):
            print(f"  warn: overlay music not found, skipping: {src}")
            continue
        d = dur(src, kind="music", key=key)
        lane = "MUSIC · UNDERSCORE" if kind == "underscore" else "MUSIC · CUES"
        out.append(Placement(lane, src, ts, d, f"{kind}:{key}"))

    return out


# Per-lane track volume (linear). Music lanes are scaled by music_gain in emit,
# mirroring produce.py: bed 0.10, underscore 0.12, motif/stinger 1.0.
LANE_BASEVOL = {
    "VOICE":             1.0,
    "SFX":               1.0,   # engine concatenates sfx at full level
    "EINLAGE":           1.0,
    "MUSIC · BED":        0.10,
    "MUSIC · UNDERSCORE": 0.12,
    "MUSIC · CUES":       1.0,
}
MUSIC_LANES = {"MUSIC · BED", "MUSIC · UNDERSCORE", "MUSIC · CUES"}
LANE_ORDER = ["VOICE", "SFX", "EINLAGE",
              "MUSIC · BED", "MUSIC · UNDERSCORE", "MUSIC · CUES"]


def emit_rpp(spec, placements, project_title, render_dir=None, render_stem=None):
    music_gain = float(spec.get("music_gain", 1.0))
    by_lane = {}
    for p in placements:
        by_lane.setdefault(p.lane, []).append(p)
    lanes = [l for l in LANE_ORDER if l in by_lane] + \
            [l for l in by_lane if l not in LANE_ORDER]

    L = []
    A = L.append
    A('<REAPER_PROJECT 0.1 "7.0" 0')
    A("  RIPPLE 0")
    A("  TEMPO 120 4 4")
    A("  SAMPLERATE 44100 0 0")
    A("  LOOP 0")
    safe_title = "".join(c if c.isalnum() or c in "-_." else "_" for c in project_title)
    # RENDER_FILE = output directory; RENDER_PATTERN = bare filename stem (no ext).
    # REAPER appends RENDER_PATTERN + codec extension to RENDER_FILE.
    A(f"  RENDER_PATTERN {_q(render_stem or safe_title)}")
    if render_dir:
        A(f"  RENDER_FILE {_q(render_dir + '/')}")
        A("  RENDER_1X 0")
        A("  RENDER_RANGE 1 0 0 18 1000")   # 1 = entire project
        A("  RENDER_RESAMPLE 3 0 1")
        A("  RENDER_ADDTOPROJ 0")
        A("  RENDER_DITHER 0")
    for lane in lanes:
        vol = LANE_BASEVOL.get(lane, 1.0)
        if lane in MUSIC_LANES:
            vol *= music_gain
        A("  <TRACK")
        A(f"    NAME {_q(lane)}")
        A(f"    VOLPAN {vol:.6f} 0 -1 -1 1")
        A("    MUTESOLO 0 0 0")
        for p in sorted(by_lane[lane], key=lambda x: x.pos):
            A("    <ITEM")
            A(f"      POSITION {p.pos:.6f}")
            A(f"      LENGTH {p.length:.6f}")
            A(f"      LOOP {p.loop}")
            A("      SOFFS 0")
            A(f"      FADEIN 1 0.005 0 1 0 0 0")
            A(f"      FADEOUT 1 0.005 0 1 0 0 0")
            A(f"      NAME {_q(p.name)}")
            A(f"      <SOURCE {_src_type(p.path)}")
            A(f"        FILE {_q(p.path)}")
            A("      >")
            A("    >")
        A("  >")
    A(">")
    return "\n".join(L) + "\n"


MIX_NOTES = """\
# {title} — REAPER-Session (aus produce.py-Spec generiert)

Lanes (oben → unten): **VOICE · SFX · EINLAGE · MUSIC · BED · MUSIC · UNDERSCORE
· MUSIC · CUES**. Positionen und Offsets sind identisch zur ffmpeg-Mixphase
(`produce.py <spec> mix`). Die Musik-Lanes tragen ihren Gain auf der Spur —
BED 0.10, UNDERSCORE 0.12, CUES 1.0 (jeweils × `music_gain`) — wie im Engine-Mix.

## Empfohlene ReaPlugs-Kette auf der VOICE-Lane (von Hand einfügen)

Diese Kette wird **nicht** eingebettet (gültiger FX-State muss aus einem echten
REAPER stammen; blind erzeugte FX-Blöcke können das Projekt beschädigen). In
REAPER auf der VOICE-Spur → FX → hinzufügen, in dieser Reihenfolge:

1. **ReaEQ** — Hochpass ~80 Hz (Rumpeln weg), leichte Präsenz +2 dB @ 3–5 kHz.
2. **ReaFIR** (Mode: *Subtract*) — Grundrauschen entfernen: „Automatically build
   noise profile" über eine Sprechpause, dann fixieren.
3. **ReaComp** — Ratio ~3:1, Threshold so, dass ~4–6 dB Gain-Reduction; Attack
   ~10 ms, Release ~120 ms.
4. **ReaXcomp** *(optional)* — leiser De-Esser-Band um 6–8 kHz.
5. **ReaLimit** — Ceiling −1.5 dBTP als Sicherheitsnetz.

Loudness zum Schluss auf **−16 LUFS (Stereo)** normalisieren — im Render-Dialog
(Normalize → LUFS-I) oder weiterhin über die ffmpeg-`loudnorm`-Stufe der Engine.

## Rendern

    reaper -renderproject "{rpp}"      # Linux headless: xvfb-run -a reaper -renderproject …

Ausgabeformat einmalig unter *File → Render* setzen (z. B. MP3 −q:a 2 oder WAV),
oder den finalen Mix weiter mit `produce.py <spec> mix` erzeugen — die Session
hier ist zum Feinschliff von Hand gedacht, nicht als Ersatz der Engine.
"""


def main():
    ap = argparse.ArgumentParser(description="Export a produce.py podcast spec to a REAPER .RPP project.")
    ap.add_argument("spec", help="path to the episode YAML spec")
    ap.add_argument("-o", "--out", help="output .rpp path (default: out/<slug>/<title>.rpp)")
    ap.add_argument("--fake-durations", type=float, metavar="SECS", default=None,
                    help="structural dry-run: nominal item lengths, no ffmpeg/stems needed")
    ap.add_argument("--gap-scale", type=float, metavar="FACTOR", default=None,
                    help="multiply all gap values (base/switch/sfx_tail) by FACTOR "
                         "(e.g. 0.5 for snappier kids pacing). Overrides the spec's gaps section.")
    ap.add_argument("--render", action="store_true",
                    help="embed render settings in the RPP and immediately invoke "
                         "`reaper -renderproject` to produce the final MP3.")
    args = ap.parse_args()

    spec = produce.load_spec(args.spec)
    if spec.get("kind", "podcast") != "podcast":
        sys.exit("rpp_export currently supports kind: podcast only")

    if args.gap_scale is not None:
        base = spec.get("gaps", {})
        spec["gaps"] = {
            "base":     (base.get("base",     0.55)) * args.gap_scale,
            "switch":   (base.get("switch",   0.90)) * args.gap_scale,
            "sfx_tail": (base.get("sfx_tail", 0.35)) * args.gap_scale,
        }

    title = spec.get("title") or spec["slug"].replace("/", "_")
    placements = build_placements(spec, fake=args.fake_durations)
    if not placements:
        sys.exit("no placements produced (did you run `produce.py <spec> gen` first?)")

    out_dir = os.path.join(ROOT, "out", spec["slug"])
    os.makedirs(out_dir, exist_ok=True)
    safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in title)
    rpp_path = args.out or os.path.join(out_dir, safe + ".rpp")

    render_mp3 = None
    if args.render:
        final = spec.get("output", {}).get("final", "out.mp3")
        final_base = os.path.basename(final)
        safe_base = "".join(c if c.isalnum() or c in "-_." else "_" for c in final_base)
        # REAPER treats RENDER_FILE as a directory and appends RENDER_PATTERN+ext —
        # so point it at the output dir; the pattern becomes the bare stem name.
        render_mp3 = os.path.join(ROOT, "out", spec["slug"])

    render_stem = None
    if args.render:
        render_stem = os.path.splitext(safe_base)[0]

    with open(rpp_path, "w", encoding="utf-8") as f:
        f.write(emit_rpp(spec, placements, title, render_dir=render_mp3, render_stem=render_stem))

    notes_path = os.path.join(os.path.dirname(rpp_path), "MIX-NOTES.md")
    with open(notes_path, "w", encoding="utf-8") as f:
        f.write(MIX_NOTES.format(title=title, rpp=rpp_path))

    lanes = {}
    for p in placements:
        lanes[p.lane] = lanes.get(p.lane, 0) + 1
    total = max((p.pos + p.length for p in placements), default=0.0)
    print(f"RPP → {rpp_path}")
    print(f"   {len(placements)} items across {len(lanes)} lanes, ~{total:.1f}s")
    for lane in LANE_ORDER:
        if lane in lanes:
            print(f"     {lane:14s} {lanes[lane]:3d} items")
    print(f"   notes → {notes_path}")
    if args.fake_durations is not None:
        print("   (fake durations — offsets illustrative; re-run after `gen` for real timing)")

    if args.render:
        import subprocess
        print(f"\nRendering via REAPER → {render_mp3}")
        result = subprocess.run(["reaper", "-renderproject", rpp_path],
                                capture_output=True, text=True)
        if result.returncode == 0:
            print("REAPER render complete.")
        else:
            print(f"REAPER exited {result.returncode}")
            if result.stderr:
                print(result.stderr[:500])


if __name__ == "__main__":
    main()
