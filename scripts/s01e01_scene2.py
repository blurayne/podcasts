#!/usr/bin/env python3
"""Scene 2 — "Die Verheiratung der Tochter" (fränkisch-karolingisch, frühes 9. Jh.)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hoerspiel as H

VOICES = {
    "SPRECHER": "wcGcDDfRHvH6LR9p07u4",  # Apollo – Documentary & TV (continuous narrator)
    "HAIMO":    "FTNCalFNG5bRnkkaP5Ug",  # Otto — the father / Muntwalt
    "ADELHEID": "uvysWDLbKpA4XvpD3GI6",  # Leonie — the mother
}
DISPLAY = {"SPRECHER":"ERZÄHLER", "HAIMO":"HAIMO", "ADELHEID":"ADELHEID"}

DRAMA = [
  {"id":"00_narr_in","who":"SPRECHER","gap":0.0,
   "text":"Frankenreich, um 820. Ein freier Grundbesitzer und seine Frau sitzen abends beim Feuer. Es geht um ihre Tochter — und um eine Entscheidung, die rechtlich allein dem Vater zusteht. Rechtlich. Hören wir, wie es wirklich zugeht."},
  {"cue":"spindle_stop","gain":0.7},
  {"id":"01_haimo","who":"HAIMO","gap":0.8,
   "text":"Wicho hat Boten geschickt. Sein Vater bietet für Bertrada zwei Hufen am Wald und Vieh dazu. Das Wittum wäre gesichert. Es ist ein gutes Haus, Adelheid. Ein Bündnis, das uns nach Süden deckt."},
  {"id":"02_adelheid","who":"ADELHEID","gap":0.4,
   "text":"Zwei Hufen. Du sprichst von Land, Haimo. Ich frage nach dem Mann. Wie alt ist Wicho?"},
  {"id":"03_haimo","who":"HAIMO","gap":0.4,
   "text":"Über zwanzig. Kräftig, heißt es."},
  {"id":"04_adelheid","who":"ADELHEID","gap":0.4,
   "text":"Und Bertrada ist dreizehn. Die Munt liegt bei dir, ich weiß. Du gibst sie fort, du schließt den Vertrag, dein Wort gilt vor der Sippe. Aber ein Wort von mir zählt auch — wenn schon nicht vor Gericht, dann hier, an diesem Feuer."},
  {"id":"05_haimo","who":"HAIMO","gap":0.5,"tag":"[calm]",
   "text":"Das tut es. Sprich."},
  {"id":"06_adelheid","who":"ADELHEID","gap":0.4,
   "text":"Ich habe sie erzogen, nicht du. Sie spinnt und webt feiner als die Mägde im Frauenhaus. Sie kennt die Kräuter — welche das Fieber senken, welche die Blutung stillen. Sie führt bald selbst die Schlüssel eines Hofes. Das ist etwas wert, Haimo. Gib sie keinem, der es nicht achtet."},
  {"id":"07_haimo","who":"HAIMO","gap":0.4,
   "text":"Ich verkaufe kein Kalb. Ich sichere ihr ein Haus."},
  {"id":"08_adelheid","who":"ADELHEID","gap":0.4,
   "text":"Dann sichere auch, dass sie gehört wird. Erinnerst du dich an die Königstochter aus Thüringen — die dem König geraubt und zur Ehe gezwungen wurde und dann floh, um Nonne zu werden? Ein „Ja“ der Braut ist im Recht nicht nötig. Aber ein „Nein“ mit den Füßen — das haben schon Königinnen getan."},
  {"id":"09_haimo","who":"HAIMO","gap":0.7,"tag":"[calm]",
   "text":"Du meinst, ich soll sie fragen."},
  {"id":"10_adelheid","who":"ADELHEID","gap":0.4,
   "text":"Ich meine, du sollst sie kennen, bevor du sie gibst. Lass Wicho im Sommer kommen. Lass sie ihn sehen. Und lass mich lehren, was ihr nützt — nicht nur Spindel und Topf. Sie soll die Psalmen lesen können. Es gibt Frauen, die schreiben, Haimo. Für ihre Söhne. Ganze Bücher."},
  {"id":"11_haimo","who":"HAIMO","gap":0.5,
   "text":"Lesen. Für eine Bäuerin."},
  {"id":"12_adelheid","who":"ADELHEID","gap":0.4,
   "text":"Für die Herrin eines Hofes. Wer rechnen und lesen kann, wird nicht betrogen, wenn der Mann im Feld liegt oder im Krieg."},
  {"id":"13_haimo","who":"HAIMO","gap":0.6,"tag":"[sighs]",
   "text":"Der Vertrag wird geschlossen — das ist meine Sache und die seines Vaters. Aber der Sommer gehört dir. Lehre sie. Und ich sehe sie mir an, den Wicho, bevor ich die Hand gebe."},
  {"id":"14_adelheid","who":"ADELHEID","gap":0.5,"tag":"[whispers]",
   "text":"Mehr will ich nicht."},
  {"cue":"spindle_resume","gain":0.6},
]

NARR_HERAUS = "Der Vater entscheidet — und hört doch auf die Mutter. War das die Regel? Oder Wunschdenken?"

SFX = {
  "atmo_base":      {"prompt":"A quiet night indoors beside a crackling hearth fire, a wooden hand spindle softly whirring, faint dogs outside in the distance, a lone night bird", "auto":True},
  "spindle_stop":   {"prompt":"a wooden hand spindle slowing and coming to a stop", "dur":2},
  "spindle_resume": {"prompt":"a wooden hand spindle starting to whirr again softly", "dur":2},
}
MUSIC = {
  "intro":  {"prompt":"Warm melancholic hearth theme: soft plucked harp and strings, intimate, a little wistful, gentle medieval folk color, no vocals", "ms":24000},
  "bed":    {"prompt":"Very soft neutral documentary underscore: sustained low strings, contemplative, minimal, unobtrusive, no melody, no vocals", "ms":45000},
  "outro":  {"prompt":"Gentle reflective outro: soft warm strings, bittersweet, slowly fading, no vocals", "ms":22000},
}

SCENE = H.Scene(slug="die-frau-vor-dem-recht/S01-01/scene2", name="scene2", source_md="series/die-frau-vor-dem-recht/S01-01/hoerspiele.md", title="Die Frau vor dem Recht — Szene 2 — Die Verheiratung der Tochter",
                scene_index=2, voices=VOICES, reverb_roles=set(), drama=DRAMA,
                narr_heraus=NARR_HERAUS, sfx=SFX, music=MUSIC, display=DISPLAY)

if __name__ == "__main__":
    H.main(SCENE, sys.argv[1] if len(sys.argv) > 1 else "all")
