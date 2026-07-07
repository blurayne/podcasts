#!/usr/bin/env python3
"""Scene 3 — "Die Frau, die zur Waffe greift" (Island, spätes 10. Jh.)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hoerspiel as H

VOICES = {
    "SPRECHER": "wcGcDDfRHvH6LR9p07u4",  # Apollo – Documentary & TV (continuous narrator)
    "THORGERD": "BIvP0GN1cAtSRTxNHnWS",  # Ellen — the húsfreyja
    "DIEB":     "L5Oo1OjjHdbIvJDQFgmN",  # Bartholomeus Bösewicht — the thief
    "GRIM":     "ZgTblco1F8U3zN77c5Rj",  # Andreas — the old servant
}
DISPLAY = {"SPRECHER":"ERZÄHLER", "THORGERD":"THORGERD", "DIEB":"ERSTER DIEB", "GRIM":"GRIM"}

DRAMA = [
  {"id":"00_narr_in","who":"SPRECHER","gap":0.0,
   "text":"Island, um 980. Ein Hof, abgelegen. Der Hausherr ist auf See. Zurück bleibt die Hausherrin — die húsfreyja — mit den Schlüsseln zu allem, was der Hof besitzt. In dieser Nacht kommen Diebe."},
  {"cue":"night_break_in","gain":0.9},
  {"id":"01_thorgerd","who":"THORGERD","gap":0.6,"tag":"[whispers]",
   "text":"Grim! Wach auf. Am Vorratshaus. Hörst du?"},
  {"id":"02_grim","who":"GRIM","gap":0.4,"tag":"[whispers]",
   "text":"…Füchse, Herrin. Oder der Wind."},
  {"id":"03_thorgerd","who":"THORGERD","gap":0.4,"tag":"[whispers]",
   "text":"Füchse tragen kein Eisen. Gib mir den Sax vom Balken."},
  {"cue":"door_frost_steps","gain":0.7},
  {"id":"04_thorgerd","who":"THORGERD","gap":0.7,"tag":"[shouting]",
   "text":"Wer bricht bei Nacht mein Vorratshaus? Nennt euch — oder geht, und ihr behaltet euer Leben!"},
  {"id":"05_dieb","who":"DIEB","gap":0.4,"tag":"[sarcastic]",
   "text":"Eine Frau allein. Der Hausherr ist auf See, weiß das ganze Tal. Geh rein, Weib, dann geschieht dir nichts."},
  {"id":"06_thorgerd","who":"THORGERD","gap":0.4,
   "text":"Der Hof ist mein, solange er fort ist. Und der Riegel, den du brichst, ist mein Recht."},
  {"cue":"scuffle","gain":0.8},
  {"id":"07_dieb","who":"DIEB","gap":0.2,"tag":"[shouting]",
   "text":"Her mit den Schlüsseln —!"},
  {"id":"08_thorgerd","who":"THORGERD","gap":0.15,"tag":"[shouting]",
   "text":"— Lass — los!"},
  {"cue":"thud_fall","gain":0.85},
  {"id":"09_grim","who":"GRIM","gap":1.1,
   "text":"Herrin… er rührt sich nicht. Ihr habt ihn… unter der Rippe. Er ist tot."},
  {"id":"10_thorgerd","who":"THORGERD","gap":0.6,
   "text":"Er hat mich gepackt. Bei Nacht. Am eigenen Vorratshaus. — Grim, hol Licht. Weck die Mägde. Ich will, dass jeder sieht, wie er liegt, und wo. Am aufgebrochenen Riegel. Mit dem Diebsgut in der Hand."},
  {"id":"11_grim","who":"GRIM","gap":0.4,
   "text":"Sie werden fragen, Herrin. Seine Sippe wird fragen."},
  {"id":"12_thorgerd","who":"THORGERD","gap":0.4,
   "text":"Dann sollen sie fragen. Ich habe nichts im Dunkeln getan. Ein Dieb, bei Nacht, handhaft — der fällt ungesühnt. Das ist das Gesetz. Aber sagen muss es ein Mann für mich, vor dem Thing. Hol mir morgen den Goden."},
  {"cue":"wind_steps_away","gain":0.7},
]

NARR_HERAUS = "Eine Frau tötet einen Einbrecher — und beruft sich aufs Gesetz. Zu Recht? Und durfte sie das überhaupt, als Frau? Sehen wir genauer hin."

SFX = {
  "atmo_base":        {"prompt":"A cold remote Icelandic farmstead at night: low wind around a turf longhouse, faint embers, bleak and quiet", "auto":True},
  "night_break_in":   {"prompt":"Night wind, a dog barking fiercely, wood splintering quietly as a door bolt is broken", "dur":4},
  "door_frost_steps": {"prompt":"A heavy wooden door opening to cold night air, footsteps crunching on frost", "dur":3},
  "scuffle":          {"prompt":"Fast footsteps on frozen ground, a brief violent struggle, cloth tearing", "dur":3},
  "thud_fall":        {"prompt":"A dull heavy blow, a sharp gasp, a body falling onto frozen ground, then sudden silence, a dog stops barking", "dur":4},
  "wind_steps_away":  {"prompt":"Cold night wind, footsteps walking away into the distance", "dur":4},
}
MUSIC = {
  "intro":  {"prompt":"Bleak Nordic winter tension: low drone, cold sparse strings, a distant hint of dread, cinematic, no vocals", "ms":24000},
  "bed":    {"prompt":"Very soft neutral documentary underscore: sustained low strings, contemplative, minimal, unobtrusive, no melody, no vocals", "ms":45000},
  "outro":  {"prompt":"Somber Nordic outro: low strings and a slow drum, resolute and cold, slowly fading, no vocals", "ms":22000},
}

SCENE = H.Scene(slug="die-frau-vor-dem-recht/S01-01/scene3", name="scene3", source_md="series/die-frau-vor-dem-recht/S01-01/hoerspiele.md", title="Die Frau vor dem Recht — Szene 3 — Die Frau, die zur Waffe greift",
                scene_index=3, voices=VOICES, reverb_roles=set(), drama=DRAMA,
                narr_heraus=NARR_HERAUS, sfx=SFX, music=MUSIC, display=DISPLAY)

if __name__ == "__main__":
    H.main(SCENE, sys.argv[1] if len(sys.argv) > 1 else "all")
