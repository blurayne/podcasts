#!/usr/bin/env python3
"""Produce Scene 1 ("Das Thing und das umstrittene Feld") as a Hörspiel.

Two phases:
  gen  -> generate every voice / SFX / music stem via the ElevenLabs API
          (idempotent: skips any stem file that already exists & is non-empty,
           so credits are only ever spent once per stem)
  mix  -> assemble the stems into out/scene1/scene1.mp3 with ffmpeg

Run:  python3 scripts/s01e01_scene1.py gen
      python3 scripts/s01e01_scene1.py mix
      python3 scripts/s01e01_scene1.py all
"""
import os, sys, json, re, subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import el  # the ElevenLabs API CLI/library

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT  = os.path.join(ROOT, "out", "die-frau-vor-dem-recht", "S01-01", "scene1")
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

FF      = _pick([os.environ.get("FFMPEG_BIN"), "ffmpeg", "/usr/bin/ffmpeg"])
FFPROBE = _pick([os.environ.get("FFPROBE_BIN"), "ffprobe", "/usr/bin/ffprobe"])
MODEL   = "eleven_v3"

# ---------------------------------------------------------------- cast
VOICES = {
    "SPRECHER": "wcGcDDfRHvH6LR9p07u4",  # Apollo – Documentary & TV
    "SEGIMER":  "fehqjfT0R2fGKeUX2YeE",  # Gerry – Composed & Strong (rhine franconian)
    "PRIESTER": "ZgTblco1F8U3zN77c5Rj",  # Andreas – Pleasant German
    "FOLKWIN":  "FTNCalFNG5bRnkkaP5Ug",  # Otto
    "WALUBURG": "BIvP0GN1cAtSRTxNHnWS",  # Ellen – Serious, Direct
    "SWANHILD": "uvysWDLbKpA4XvpD3GI6",  # Leonie
}
REVERB_ROLES = {"WALUBURG"}  # she "speaks from a distance"

# ---------------------------------------------------------------- drama script
# gap = seconds of silence before this line.  tag = leading v3 audio tag.
DRAMA = [
  {"id":"00_narr_in","who":"SPRECHER","gap":0.0,
   "text":"Um das Jahr 90 nach Christus, östlich des Rheins. Ein Stamm versammelt sich zum Thing — der Versammlung der freien, waffenfähigen Männer. Frauen haben hier kein Rederecht. Und doch stehen an diesem Tag zwei Frauen im Zentrum: eine Seherin, deren Wort als göttlich gilt — und eine Frau, die aus dem Nachbarstamm hierher verheiratet wurde. Hören wir hinein."},
  {"cue":"spear_shield_3","gain":0.9},
  {"id":"01_priester","who":"PRIESTER","gap":0.8,
   "text":"[shouting] Schweigt! [calm] Das Thing ist eröffnet. Wer das Wort führt, führt es geordnet — oder er schweigt. So wollen es die Götter."},
  {"id":"02_segimer","who":"SEGIMER","gap":0.6,
   "text":"Ihr kennt den Grund. Das Feld am Erlenbach — dreimal in drei Sommern haben ihre Leute die Ernte eingeholt. Unser Korn. Unser Boden."},
  {"id":"03_folkwin","who":"FOLKWIN","gap":0.35,"tag":"[shouting]",
   "text":"Dann ziehen wir hinüber und holen es uns zurück! Mit dem Speer, nicht mit Worten!"},
  {"cue":"grollen","gain":0.7},
  {"id":"04_segimer","who":"SEGIMER","gap":0.7,
   "text":"Und dann? Fehde. Tote auf beiden Seiten. Ihre Sippe gegen unsere, Sommer um Sommer. Folkwin, du zählst die Klingen. Zähl auch die Gräber."},
  {"id":"05_priester","who":"PRIESTER","gap":0.5,
   "text":"Der Stamm am Fluss ist uns durch Eid und Heirat verbunden. Wer bricht, bricht auch den Frieden der Götter."},
  {"id":"06_segimer","who":"SEGIMER","gap":0.5,
   "text":"Darum frage ich, bevor ein Speer fliegt: Was sagt die, die weiter sieht als wir? Man rufe die Seherin."},
  {"cue":"hush_gust","gain":0.8},
  {"id":"07_waluburg","who":"WALUBURG","gap":0.9,"tag":"[calm]",
   "text":"Ich stehe nicht in eurem Ring, Männer — das Recht des Rings ist nicht mein Recht. Aber ich lese das Los, und ich lese den Fluss. Ich sehe Rauch über dem Erlenbach, wenn ihr die Speere nehmt. Ich sehe eure Höfe leer."},
  {"id":"08_folkwin","who":"FOLKWIN","gap":0.6,"tag":"[whispers]",
   "text":"…und wenn wir warten?"},
  {"id":"09_waluburg","who":"WALUBURG","gap":0.4,"tag":"[calm]",
   "text":"Dann lebt, wer jetzt lebt. Die Götter geben kein Recht auf Blut vor dem neuen Mond."},
  {"cue":"raunen","gain":0.6},
  {"id":"10_segimer","who":"SEGIMER","gap":0.7,
   "text":"Ihr hört sie. — Aber es ist noch eine hier, die beide Ufer kennt. Swanhild, du kamst von ihnen zu uns. Tritt heran. Nicht um zu richten — um zu sagen, was du weißt."},
  {"cue":"steps_surprise","gain":0.6},
  {"id":"11_swanhild","who":"SWANHILD","gap":0.7,"tag":"[calm]",
   "text":"Ich bin Herd und Hand in Segimers Haus. Aber meine Mutter wohnt am Erlenbach. — Ihr nennt es Diebstahl. Sie nennen es ihr altes Recht: Ihr Großvater habe das Feld gerodet, ehe euer Zaun stand."},
  {"id":"12_folkwin","who":"FOLKWIN","gap":0.3,"tag":"[angry]",
   "text":"Also lügen sie!"},
  {"id":"13_swanhild","who":"SWANHILD","gap":0.4,
   "text":"Nein. Sie erinnern anders. Und darum: Schickt keine Speere. Schickt mich. Ich bin die Brücke — solange die Brücke hält. Mein Sohn trägt euer Blut und ihres. Wollt ihr, dass er einen Onkel erschlägt?"},
  {"id":"14_segimer","who":"SEGIMER","gap":0.8,
   "text":"… Ein Bote statt einer Klinge. Geiseln zum Pfand, bis das Feld geteilt ist. Wer ist dafür?"},
  {"cue":"spears_vote","gain":0.85},
  {"id":"15_priester","who":"PRIESTER","gap":1.2,
   "text":"[shouting] Die Waffen sprechen! [calm] Der Stamm hat entschieden: erst das Wort, dann — wenn es sein muss — der Speer."},
]

NARR_HERAUS = "Ein Speerklirren als Ja. Eine Frau als lebende Friedensbrücke. Aber wie viel davon ist historisch — und wie viel ist Wunsch?"

# ---------------------------------------------------------------- sfx / music
SFX = {
  "atmo_base":      {"prompt":"Ancient Germanic tribal assembly on an open windswept field: steady wind, distant cowbells, low murmur of a large crowd of men, occasional birdsong, no music", "auto":True},
  "spear_shield_3": {"prompt":"A spear shaft striking a wooden shield three times, three sharp hard wooden knocks", "dur":3},
  "grollen":        {"prompt":"A crowd of warriors growling in approval, a few spear shafts clashing", "dur":3},
  "hush_gust":      {"prompt":"A murmuring crowd growing reverently silent, slow footsteps on earth, a gust of wind", "dur":4},
  "raunen":         {"prompt":"An impressed crowd of people murmuring quietly in awe", "dur":3},
  "steps_surprise": {"prompt":"A few footsteps approaching on earth, a crowd murmuring in surprise", "dur":3},
  "spears_vote":    {"prompt":"Many spear shafts rhythmically beating against wooden shields, growing louder, a tribal war assembly voting yes in unison", "dur":6},
}
MUSIC = {
  "intro":  {"prompt":"Dark solemn ancient Germanic ritual atmosphere: low sustained drone, a distant war horn, slow frame drum, ominous and sacred, cinematic, no vocals", "ms":26000},
  "bed":    {"prompt":"Very soft neutral documentary underscore: sustained low strings, contemplative, minimal, unobtrusive, slow, no melody, no vocals", "ms":45000},
  "outro":  {"prompt":"Reflective solemn outro: soft strings and a low slow drum, contemplative, gradually fading, cinematic, no vocals", "ms":22000},
}

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

def tts(role, text, out_path, label):
    if el._exists(out_path):
        print(f"  skip (exists): {label}")
    else:
        el.tts(VOICES[role], text, out_path, model=MODEL)
        print(f"  ok: {label}")

def gen_sfx(name, spec):
    out = os.path.join(SFXD, name + ".mp3")
    if el._exists(out):
        print(f"  skip (exists): sfx:{name}")
    else:
        el.sfx(spec["prompt"], out, duration=None if spec.get("auto") else spec["dur"])
        print(f"  ok: sfx:{name}")

def gen_music(name, spec):
    out = os.path.join(MUSD, name + ".mp3")
    if el._exists(out):
        print(f"  skip (exists): music:{name}")
    else:
        el.music(spec["prompt"], out, spec["ms"])
        print(f"  ok: music:{name}")

# ---------------------------------------------------------------- analysis text
def analysis_paragraphs():
    text = open(os.path.join(ROOT,"series","die-frau-vor-dem-recht","S01-01","hoerspiele.md"), encoding="utf-8").read()
    body = re.split(r"\n# SZENE \d", text)[1]           # scene 1 body
    ana  = body.split("## Historische Einordnung")[1].split("\n# ")[0]
    paras=[]
    for raw in ana.split("\n"):
        p = raw.strip()
        if not p or p.startswith("#") or p.startswith("---") or p.startswith("##"):
            continue
        p = re.sub(r"\*\*([^*]*)\*\*", r"\1", p)
        p = re.sub(r"\*([^*]*)\*", r"\1", p)
        p = p.replace("„",'"').replace("“",'"').replace("”",'"')
        p = re.sub(r"\s+"," ",p).strip()
        if len(p) > 3:
            paras.append(p)
    return paras

# ---------------------------------------------------------------- GEN phase
def phase_gen():
    print("== voices ==")
    tts("SPRECHER", DRAMA[0]["text"], os.path.join(VOX,"00_narr_in.mp3"), "narr_in")
    for el in DRAMA:
        if "cue" in el: continue
        if el["id"]=="00_narr_in": continue
        text = (el.get("tag","")+" "+el["text"]).strip()
        tts(el["who"], text, os.path.join(VOX, el["id"]+".mp3"), el["id"]+"/"+el["who"])
    tts("SPRECHER", NARR_HERAUS, os.path.join(VOX,"16_narr_out.mp3"), "narr_out")
    for i,p in enumerate(analysis_paragraphs()):
        tts("SPRECHER", p, os.path.join(VOX, f"ana_{i:02d}.mp3"), f"analysis[{i}] ({len(p)}c)")
    print("== sfx ==")
    for name,spec in SFX.items(): gen_sfx(name,spec)
    print("== music ==")
    for name,spec in MUSIC.items(): gen_music(name,spec)
    print("GEN DONE")

# ---------------------------------------------------------------- MIX phase
def norm(inp, outp, extra=""):
    """decode any input to a clean 44.1k stereo wav (optionally with a filter)."""
    filt = "aformat=sample_rates=44100:channel_layouts=stereo"
    if extra: filt = extra + "," + filt
    run([FF,"-y","-i",inp,"-af",filt, outp])

def silence(secs, outp):
    run([FF,"-y","-f","lavfi","-t",f"{secs:.3f}","-i","anullsrc=r=44100:cl=stereo", outp])

def build_voice_bus(items, out_wav):
    """items: ordered list of dicts {role,text_file,gap,reverb} -> concat wav.
       returns (total_len, [(item_id, start_time)...])."""
    pieces=[]; t=0.0; starts=[]
    for it in items:
        g=it["gap"]
        if g>0:
            sp=os.path.join(WORK,f"sil_{len(pieces)}.wav"); silence(g,sp); pieces.append(sp); t+=g
        stem=it["file"]
        w=os.path.join(WORK,"n_"+os.path.basename(stem)+".wav")
        norm(stem, w, "aecho=0.85:0.9:70:0.32,highpass=f=90" if it.get("reverb") else "")
        pieces.append(w); starts.append((it["id"], t)); t+=dur(w)
    # concat all pieces
    inputs=[];
    for p in pieces: inputs += ["-i",p]
    n=len(pieces)
    fc="".join(f"[{i}:a]" for i in range(n))+f"concat=n={n}:v=0:a=1[o]"
    run([FF,"-y",*inputs,"-filter_complex",fc,"-map","[o]",out_wav])
    return dur(out_wav), dict(starts)

def duck_bed(bed, sidechain, out_wav, target_len, vol):
    """loop 'bed' to target_len, lower volume, duck under 'sidechain'."""
    looped=os.path.join(WORK,"bed_loop.wav")
    run([FF,"-y","-stream_loop","-1","-i",bed,"-t",f"{target_len:.3f}",
         "-af",f"volume={vol},aformat=sample_rates=44100:channel_layouts=stereo",looped])
    run([FF,"-y","-i",looped,"-i",sidechain,"-filter_complex",
         "[0:a][1:a]sidechaincompress=threshold=0.03:ratio=8:attack=5:release=350[o]",
         "-map","[o]", out_wav])

def render_drama():
    # voice items in order (narration + dialogue), collecting cue placements
    items=[]; cues=[]
    for el in DRAMA:
        if "cue" in el:
            cues.append(el); continue
        items.append({"id":el["id"], "file":os.path.join(VOX,el["id"]+".mp3"),
                      "gap":el["gap"], "reverb": el["who"] in REVERB_ROLES})
    bus=os.path.join(WORK,"drama_voice.wav")
    blen, starts = build_voice_bus(items, bus)
    # map each cue to the start time of the NEXT line after it in DRAMA
    order=[e for e in DRAMA]; cue_at=[]
    for i,e in enumerate(order):
        if "cue" in e:
            nxt=next((order[j]["id"] for j in range(i+1,len(order)) if "id" in order[j]), None)
            at = starts.get(nxt, blen) if nxt else blen
            # opening cue (before first line) fire at 0
            cue_at.append((e["cue"], e["gain"], max(0.0, at-0.15)))
    # atmo bed ducked by the whole voice bus
    atmo=os.path.join(WORK,"drama_atmo.wav")
    duck_bed(os.path.join(SFXD,"atmo_base.mp3"), bus, atmo, blen+2.0, 0.32)
    # assemble: voice + atmo + oneshots (each delayed), amix normalize=0
    inputs=["-i",bus,"-i",atmo]; fc=[]; labels=["[0:a]","[1:a]"]
    for k,(cid,gain,at) in enumerate(cue_at, start=2):
        inputs += ["-i", os.path.join(SFXD,cid+".mp3")]
        ms=int(at*1000)
        fc.append(f"[{k}:a]aformat=sample_rates=44100:channel_layouts=stereo,volume={gain},adelay={ms}|{ms}[c{k}]")
        labels.append(f"[c{k}]")
    fc.append("".join(labels)+f"amix=inputs={len(labels)}:normalize=0:dropout_transition=0[o]")
    out=os.path.join(WORK,"seg_drama.wav")
    run([FF,"-y",*inputs,"-filter_complex",";".join(fc),"-map","[o]",
         "-t",f"{blen+1.5:.3f}", out])
    return out

def render_analysis():
    items=[{"id":"heraus","file":os.path.join(VOX,"16_narr_out.mp3"),"gap":0.0,"reverb":False}]
    i=0
    while os.path.exists(os.path.join(VOX,f"ana_{i:02d}.mp3")):
        items.append({"id":f"ana_{i:02d}","file":os.path.join(VOX,f"ana_{i:02d}.mp3"),
                      "gap":0.6,"reverb":False}); i+=1
    bus=os.path.join(WORK,"ana_voice.wav")
    blen,_=build_voice_bus(items, bus)
    bed=os.path.join(WORK,"ana_bed.wav")
    duck_bed(os.path.join(MUSD,"bed.mp3"), bus, bed, blen+2.0, 0.108)  # music -10%
    out=os.path.join(WORK,"seg_analysis.wav")
    run([FF,"-y","-i",bus,"-i",bed,"-filter_complex",
         "[0:a][1:a]amix=inputs=2:normalize=0:dropout_transition=0[o]","-map","[o]",
         "-t",f"{blen+1.5:.3f}",out])
    return out

def faded(src, outp, fin, fout):
    d=dur(src)
    run([FF,"-y","-i",src,"-af",
         f"volume=0.9,afade=t=in:st=0:d={fin},afade=t=out:st={max(0,d-fout):.3f}:d={fout},"  # music -10%
         f"aformat=sample_rates=44100:channel_layouts=stereo", outp])

def phase_mix():
    print("== render drama ==");    seg_drama    = render_drama()
    print("== render analysis =="); seg_analysis = render_analysis()
    print("== music fades ==")
    intro=os.path.join(WORK,"seg_intro.wav"); faded(os.path.join(MUSD,"intro.mp3"),intro,1.5,2.5)
    outro=os.path.join(WORK,"seg_outro.wav"); faded(os.path.join(MUSD,"outro.mp3"),outro,2.0,3.5)
    # final concat with small gaps
    g1=os.path.join(WORK,"g1.wav"); silence(0.4,g1)
    g2=os.path.join(WORK,"g2.wav"); silence(0.6,g2)
    g3=os.path.join(WORK,"g3.wav"); silence(0.4,g3)
    order=[intro,g1,seg_drama,g2,seg_analysis,g3,outro]
    inputs=[];
    for p in order: inputs+=["-i",p]
    n=len(order)
    fc="".join(f"[{i}:a]" for i in range(n))+f"concat=n={n}:v=0:a=1[c];[c]loudnorm=I=-16:TP=-1.5:LRA=11[o]"
    final=os.path.join(OUT,"scene1.mp3")
    run([FF,"-y",*inputs,"-filter_complex",fc,"-map","[o]","-codec:a","libmp3lame","-q:a","2",final])
    print("FINAL:", final, f"({dur(final):.1f}s)")

# ---------------------------------------------------------------- audiobook
DISPLAY = {"SPRECHER":"ERZÄHLER", "SEGIMER":"SEGIMER", "PRIESTER":"DER PRIESTER",
           "FOLKWIN":"FOLKWIN", "WALUBURG":"WALUBURG", "SWANHILD":"SWANHILD"}

def write_import_doc():
    """Clean, chapterised text of Scene 1 for manual import into ElevenLabs Studio."""
    L = ["Die Frau vor dem Recht",
         "Szene 1 — Das Thing und das umstrittene Feld", "",
         "Kapitel 1 — Das Hörspiel", ""]
    for el in DRAMA:
        if "id" not in el:
            continue
        L += [f'{DISPLAY.get(el["who"], el["who"])}: {el["text"]}', ""]
    L += [f"ERZÄHLER: {NARR_HERAUS}", "", "Kapitel 2 — Historische Einordnung", ""]
    for p in analysis_paragraphs():
        L += [p, ""]
    path = os.path.join(OUT, "scene1_audiobook.txt")
    open(path, "w", encoding="utf-8").write("\n".join(L))
    print("IMPORT DOC:", path, f"({sum(len(x) for x in L)} chars)")

def render_audiobook():
    """Clean voice-only read (no atmo/SFX/music) assembled from existing stems."""
    drama = [{"id":el["id"], "file":os.path.join(VOX, el["id"]+".mp3"),
              "gap":min(el["gap"], 0.7), "reverb":False}
             for el in DRAMA if "id" in el]
    dbus = os.path.join(WORK, "ab_drama.wav"); build_voice_bus(drama, dbus)
    ana = [{"id":"heraus", "file":os.path.join(VOX,"16_narr_out.mp3"), "gap":0.0, "reverb":False}]
    i = 0
    while os.path.exists(os.path.join(VOX, f"ana_{i:02d}.mp3")):
        ana.append({"id":f"ana_{i:02d}", "file":os.path.join(VOX,f"ana_{i:02d}.mp3"),
                    "gap":0.55, "reverb":False}); i += 1
    abus = os.path.join(WORK, "ab_ana.wav"); build_voice_bus(ana, abus)
    gap = os.path.join(WORK, "ab_gap.wav"); silence(1.3, gap)
    out = os.path.join(OUT, "scene1_audiobook.mp3")
    run([FF,"-y","-i",dbus,"-i",gap,"-i",abus,"-filter_complex",
         "[0:a][1:a][2:a]concat=n=3:v=0:a=1[c];[c]loudnorm=I=-19:TP=-3:LRA=11[o]",
         "-map","[o]","-codec:a","libmp3lame","-q:a","2", out])
    print("AUDIOBOOK:", out, f"({dur(out):.1f}s)")

def phase_book():
    print("== import doc =="); write_import_doc()
    print("== render audiobook =="); render_audiobook()

# ---------------------------------------------------------------- main
if __name__=="__main__":
    cmd = sys.argv[1] if len(sys.argv)>1 else "all"
    if cmd in ("gen","all"):  phase_gen()
    if cmd in ("mix","all"):  phase_mix()
    if cmd in ("book","all"): phase_book()
