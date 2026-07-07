#!/usr/bin/env -S uv run --script
"""Reusable Hörspiel production engine.

A scene is described by a `Scene` object (cast, drama timeline, SFX, music,
which analysis section of play.md to narrate). The engine turns it into:

  gen  -> generate every voice / SFX / music stem via the ElevenLabs API (el.py)
  mix  -> full radio-play master  out/<slug>/<slug>.mp3
  book -> clean audiobook read    out/<slug>/<slug>_audiobook.mp3  + import .txt

Drama timeline elements (ordered):
  {"id":.., "who":ROLE, "gap":secs, "text":.., "tag":"[calm]"}  # spoken line
  {"cue":SFX_NAME, "gain":0.8}                                   # one-shot SFX

Convention: SFX key `atmo_base` is the looped bed; MUSIC keys `intro`,`bed`,`outro`.
"""
import os, sys, subprocess, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import el  # ElevenLabs API CLI/library

MODEL = "eleven_v3"
NARRATOR_ROLE = "SPRECHER"

def _pick(cands):
    for c in [c for c in cands if c]:
        try:
            subprocess.run([c, "-version"], capture_output=True, check=True); return c
        except Exception:
            pass
    raise SystemExit("no working ffmpeg/ffprobe found")

FF      = _pick([os.environ.get("FFMPEG_BIN"), "ffmpeg", "/usr/bin/ffmpeg"])
FFPROBE = _pick([os.environ.get("FFPROBE_BIN"), "ffprobe", "/usr/bin/ffprobe"])


class Scene:
    def __init__(self, *, slug, title, scene_index, voices, reverb_roles,
                 drama, narr_heraus, sfx, music, display, bed="atmo_base",
                 analysis=None, name=None, source_md=None, narr_out_id=None):
        # slug        = output subdir under out/ (may be nested, e.g. "series/S01-01/scene1")
        # name        = file basename (defaults to the last path component of slug)
        # analysis    = explicit tl;dr paragraphs; if None, parsed from source_md by index.
        # source_md   = ROOT-relative markdown to parse the full Einordnung from (Ep. 1).
        # narr_out_id = basename override for the narr-out stem (default: "narr_out")
        self.slug = slug; self.name = name or os.path.basename(slug)
        self.source_md = source_md; self.narr_out_id = narr_out_id
        self.title = title; self.scene_index = scene_index
        self.voices = voices; self.reverb_roles = set(reverb_roles)
        self.drama = drama; self.narr_heraus = narr_heraus
        self.sfx = sfx; self.music = music; self.display = display; self.bed = bed
        self.analysis = analysis
        self.OUT  = os.path.join(ROOT, "out", slug)
        self.VOX  = os.path.join(self.OUT, "voices")
        self.SFXD = os.path.join(self.OUT, "sfx")
        self.MUSD = os.path.join(self.OUT, "music")
        self.WORK = os.path.join(self.OUT, "work")
        for d in (self.VOX, self.SFXD, self.MUSD, self.WORK):
            os.makedirs(d, exist_ok=True)


# ---------------------------------------------------------------- helpers
def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(" ".join(cmd[:6]) + " ...\n" + r.stderr[-1500:] + "\n")
        raise SystemExit(f"command failed ({r.returncode})")
    return r

def dur(path):
    r = subprocess.run([FFPROBE,"-v","error","-show_entries","format=duration",
                        "-of","default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    return float(r.stdout.strip())

def scene_analysis(sc):
    """Explicit tl;dr paragraphs if provided, else full Einordnung from source_md."""
    return sc.analysis if sc.analysis is not None else analysis_paragraphs(sc.scene_index, sc.source_md)

def analysis_paragraphs(scene_index, source_md=None):
    src = os.path.join(ROOT, source_md) if source_md else os.path.join(ROOT, "series", "die-frau-vor-dem-recht", "S01-01", "hoerspiele.md")
    text = open(src, encoding="utf-8").read()
    body = re.split(r"\n# SZENE \d", text)[scene_index]
    ana  = body.split("## Historische Einordnung")[1].split("\n# ")[0]
    out = []
    for raw in ana.split("\n"):
        p = raw.strip()
        if not p or p.startswith("#") or p.startswith("---"):
            continue
        p = re.sub(r"\*\*([^*]*)\*\*", r"\1", p)
        p = re.sub(r"\*([^*]*)\*", r"\1", p)
        p = p.replace("„",'"').replace("“",'"').replace("”",'"')
        p = re.sub(r"\s+"," ",p).strip()
        if len(p) > 3:
            out.append(p)
    return out


# ---------------------------------------------------------------- GEN
def phase_gen(sc, model=None):
    _model = model if model is not None else MODEL
    print("== voices ==")
    for el_ in sc.drama:
        if "id" not in el_:
            continue
        out = os.path.join(sc.VOX, el_["id"] + ".mp3")
        if el._exists(out):
            print(f"  skip: {el_['id']}"); continue
        text = (el_.get("tag","") + " " + el_["text"]).strip()
        el.tts(sc.voices[el_["who"]], text, out, model=_model)
        print(f"  ok: {el_['id']}/{el_['who']}")
    narr_out_basename = sc.narr_out_id if sc.narr_out_id is not None else "narr_out"
    out = os.path.join(sc.VOX, narr_out_basename + ".mp3")
    if not el._exists(out):
        el.tts(sc.voices[NARRATOR_ROLE], sc.narr_heraus, out, model=_model); print(f"  ok: {narr_out_basename}")
    for i, p in enumerate(scene_analysis(sc)):
        out = os.path.join(sc.VOX, f"ana_{i:02d}.mp3")
        if el._exists(out):
            print(f"  skip: ana_{i:02d}"); continue
        el.tts(sc.voices[NARRATOR_ROLE], p, out, model=_model); print(f"  ok: ana_{i:02d} ({len(p)}c)")
    print("== sfx ==")
    for name, spec in sc.sfx.items():
        out = os.path.join(sc.SFXD, name + ".mp3")
        if el._exists(out): print(f"  skip: sfx:{name}"); continue
        el.sfx(spec["prompt"], out, duration=None if spec.get("auto") else spec["dur"]); print(f"  ok: sfx:{name}")
    print("== music ==")
    for name, spec in sc.music.items():
        out = os.path.join(sc.MUSD, name + ".mp3")
        if el._exists(out): print(f"  skip: music:{name}"); continue
        el.music(spec["prompt"], out, spec["ms"]); print(f"  ok: music:{name}")
    print("GEN DONE")


# ---------------------------------------------------------------- MIX
def norm(inp, outp, extra=""):
    filt = "aformat=sample_rates=44100:channel_layouts=stereo"
    if extra: filt = extra + "," + filt
    run([FF,"-y","-i",inp,"-af",filt, outp])

def silence(secs, outp):
    run([FF,"-y","-f","lavfi","-t",f"{secs:.3f}","-i","anullsrc=r=44100:cl=stereo", outp])

def build_voice_bus(sc, items, out_wav):
    pieces=[]; t=0.0; starts=[]
    for it in items:
        g=it["gap"]
        if g>0:
            sp=os.path.join(sc.WORK,f"sil_{len(pieces)}.wav"); silence(g,sp); pieces.append(sp); t+=g
        w=os.path.join(sc.WORK,"n_"+os.path.basename(it["file"])+".wav")
        norm(it["file"], w, "aecho=0.85:0.9:70:0.32,highpass=f=90" if it.get("reverb") else "")
        pieces.append(w); starts.append((it["id"], t)); t+=dur(w)
    inputs=[]
    for p in pieces: inputs += ["-i",p]
    n=len(pieces)
    fc="".join(f"[{i}:a]" for i in range(n))+f"concat=n={n}:v=0:a=1[o]"
    run([FF,"-y",*inputs,"-filter_complex",fc,"-map","[o]",out_wav])
    return dur(out_wav), dict(starts)

def duck_bed(sc, bed, sidechain, out_wav, target_len, vol):
    looped=os.path.join(sc.WORK,"bed_loop.wav")
    run([FF,"-y","-stream_loop","-1","-i",bed,"-t",f"{target_len:.3f}",
         "-af",f"volume={vol},aformat=sample_rates=44100:channel_layouts=stereo",looped])
    run([FF,"-y","-i",looped,"-i",sidechain,"-filter_complex",
         "[0:a][1:a]sidechaincompress=threshold=0.03:ratio=8:attack=5:release=350[o]",
         "-map","[o]", out_wav])

def render_drama(sc):
    items=[]
    for el_ in sc.drama:
        if "cue" in el_: continue
        items.append({"id":el_["id"], "file":os.path.join(sc.VOX,el_["id"]+".mp3"),
                      "gap":el_["gap"], "reverb": el_["who"] in sc.reverb_roles})
    bus=os.path.join(sc.WORK,"drama_voice.wav")
    blen, starts = build_voice_bus(sc, items, bus)
    cue_at=[]
    for i,e in enumerate(sc.drama):
        if "cue" in e:
            nxt=next((sc.drama[j]["id"] for j in range(i+1,len(sc.drama)) if "id" in sc.drama[j]), None)
            at = starts.get(nxt, blen) if nxt else blen
            cue_at.append((e["cue"], e["gain"], max(0.0, at-0.15)))
    atmo=os.path.join(sc.WORK,"drama_atmo.wav")
    duck_bed(sc, os.path.join(sc.SFXD,sc.bed+".mp3"), bus, atmo, blen+2.0, 0.32)
    inputs=["-i",bus,"-i",atmo]; fc=[]; labels=["[0:a]","[1:a]"]
    for k,(cid,gain,at) in enumerate(cue_at, start=2):
        inputs += ["-i", os.path.join(sc.SFXD,cid+".mp3")]
        ms=int(at*1000)
        fc.append(f"[{k}:a]aformat=sample_rates=44100:channel_layouts=stereo,volume={gain},adelay={ms}|{ms}[c{k}]")
        labels.append(f"[c{k}]")
    fc.append("".join(labels)+f"amix=inputs={len(labels)}:normalize=0:dropout_transition=0[o]")
    out=os.path.join(sc.WORK,"seg_drama.wav")
    run([FF,"-y",*inputs,"-filter_complex",";".join(fc),"-map","[o]","-t",f"{blen+1.5:.3f}", out])
    return out

def render_analysis(sc):
    narr_out_basename = sc.narr_out_id if sc.narr_out_id is not None else "narr_out"
    items=[{"id":"heraus","file":os.path.join(sc.VOX, narr_out_basename + ".mp3"),"gap":0.0,"reverb":False}]
    i=0
    while os.path.exists(os.path.join(sc.VOX,f"ana_{i:02d}.mp3")):
        items.append({"id":f"ana_{i:02d}","file":os.path.join(sc.VOX,f"ana_{i:02d}.mp3"),
                      "gap":0.6,"reverb":False}); i+=1
    bus=os.path.join(sc.WORK,"ana_voice.wav")
    blen,_=build_voice_bus(sc, items, bus)
    bed=os.path.join(sc.WORK,"ana_bed.wav")
    duck_bed(sc, os.path.join(sc.MUSD,"bed.mp3"), bus, bed, blen+2.0, 0.108)  # music -10%
    out=os.path.join(sc.WORK,"seg_analysis.wav")
    run([FF,"-y","-i",bus,"-i",bed,"-filter_complex",
         "[0:a][1:a]amix=inputs=2:normalize=0:dropout_transition=0[o]","-map","[o]",
         "-t",f"{blen+1.5:.3f}",out])
    return out

def faded(sc, src, outp, fin, fout):
    d=dur(src)
    run([FF,"-y","-i",src,"-af",
         f"volume=0.9,afade=t=in:st=0:d={fin},afade=t=out:st={max(0,d-fout):.3f}:d={fout},"  # music -10%
         f"aformat=sample_rates=44100:channel_layouts=stereo", outp])

def phase_mix(sc):
    print("== render drama ==");    seg_drama    = render_drama(sc)
    # export the play (voices + atmo + SFX, no intro/outro music, no analysis) so the
    # podcast feature can splice it in at its >>> HÖRSPIEL-EINLAGE marker.
    play = os.path.join(sc.OUT, sc.name + "_play.mp3")
    run([FF,"-y","-i",seg_drama,"-af","loudnorm=I=-16:TP=-1.5:LRA=11",
         "-codec:a","libmp3lame","-q:a","2", play])
    print("PLAY:", play, f"({dur(play):.1f}s)")
    print("== render analysis =="); seg_analysis = render_analysis(sc)
    print("== music fades ==")
    intro=os.path.join(sc.WORK,"seg_intro.wav"); faded(sc, os.path.join(sc.MUSD,"intro.mp3"),intro,1.5,2.5)
    outro=os.path.join(sc.WORK,"seg_outro.wav"); faded(sc, os.path.join(sc.MUSD,"outro.mp3"),outro,2.0,3.5)
    g1=os.path.join(sc.WORK,"g1.wav"); silence(0.4,g1)
    g2=os.path.join(sc.WORK,"g2.wav"); silence(0.6,g2)
    g3=os.path.join(sc.WORK,"g3.wav"); silence(0.4,g3)
    order=[intro,g1,seg_drama,g2,seg_analysis,g3,outro]
    inputs=[]
    for p in order: inputs+=["-i",p]
    n=len(order)
    fc="".join(f"[{i}:a]" for i in range(n))+f"concat=n={n}:v=0:a=1[c];[c]loudnorm=I=-16:TP=-1.5:LRA=11[o]"
    final=os.path.join(sc.OUT, sc.name+".mp3")
    run([FF,"-y",*inputs,"-filter_complex",fc,"-map","[o]","-codec:a","libmp3lame","-q:a","2",final])
    print("FINAL:", final, f"({dur(final):.1f}s)")


# ---------------------------------------------------------------- BOOK
def write_import_doc(sc):
    L=[sc.title, "", "Kapitel 1 — Das Hörspiel", ""]
    for el_ in sc.drama:
        if "id" not in el_: continue
        L += [f'{sc.display.get(el_["who"], el_["who"])}: {el_["text"]}', ""]
    L += [f'ERZÄHLER: {sc.narr_heraus}', "", "Kapitel 2 — Historische Einordnung", ""]
    for p in scene_analysis(sc):
        L += [p, ""]
    path=os.path.join(sc.OUT, sc.name+"_audiobook.txt")
    open(path,"w",encoding="utf-8").write("\n".join(L))
    print("IMPORT DOC:", path, f"({sum(len(x) for x in L)} chars)")

def render_audiobook(sc):
    drama=[{"id":el_["id"],"file":os.path.join(sc.VOX,el_["id"]+".mp3"),
            "gap":min(el_["gap"],0.7),"reverb":False} for el_ in sc.drama if "id" in el_]
    dbus=os.path.join(sc.WORK,"ab_drama.wav"); build_voice_bus(sc, drama, dbus)
    narr_out_basename = sc.narr_out_id if sc.narr_out_id is not None else "narr_out"
    ana=[{"id":"heraus","file":os.path.join(sc.VOX, narr_out_basename + ".mp3"),"gap":0.0,"reverb":False}]
    i=0
    while os.path.exists(os.path.join(sc.VOX,f"ana_{i:02d}.mp3")):
        ana.append({"id":f"ana_{i:02d}","file":os.path.join(sc.VOX,f"ana_{i:02d}.mp3"),
                    "gap":0.55,"reverb":False}); i+=1
    abus=os.path.join(sc.WORK,"ab_ana.wav"); build_voice_bus(sc, ana, abus)
    gap=os.path.join(sc.WORK,"ab_gap.wav"); silence(1.3,gap)
    out=os.path.join(sc.OUT, sc.name+"_audiobook.mp3")
    run([FF,"-y","-i",dbus,"-i",gap,"-i",abus,"-filter_complex",
         "[0:a][1:a][2:a]concat=n=3:v=0:a=1[c];[c]loudnorm=I=-19:TP=-3:LRA=11[o]",
         "-map","[o]","-codec:a","libmp3lame","-q:a","2", out])
    print("AUDIOBOOK:", out, f"({dur(out):.1f}s)")

def phase_book(sc):
    print("== import doc =="); write_import_doc(sc)
    print("== render audiobook =="); render_audiobook(sc)


def main(sc, cmd="all"):
    if cmd in ("gen","all"):  phase_gen(sc)
    if cmd in ("mix","all"):  phase_mix(sc)
    if cmd in ("book","all"): phase_book(sc)
