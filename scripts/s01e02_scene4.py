#!/usr/bin/env python3
"""Szene 4 — „Der Schleier, dreimal" (Teheran, Triptychon: 1936 / 1979 / 2022)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hoerspiel as H

VOICES = {
    "SPRECHER":     "dCnu06FiOZma2KVNUoPZ",  # Erzählstimme (Doku-Rahmen)
    "MARJAM_YOUNG": "rAmra0SCIYOxYmRNDSm3",  # Marjam 1936, ~20
    "MARJAM_OLD":   "FOfJ2PMgU6HOGbNYnzto",  # Marjam als Großmutter (gealtert)
    "GENDARM":      "fehqjfT0R2fGKeUX2YeE",  # amtlich-schneidend
    "SIMIN":        "BIvP0GN1cAtSRTxNHnWS",  # 1979, Tochter, Lehrerin
    "NILUFAR":      "uvysWDLbKpA4XvpD3GI6",  # 2022, Enkelin, Studentin
    "ZEITANSAGE":   "2OcnG4mH3jIMtWz3vKus",  # trockene Zeitstempel
}
DISPLAY = {
    "SPRECHER":     "ERZÄHLER",
    "MARJAM_YOUNG": "MARJAM",
    "MARJAM_OLD":   "MARJAM",
    "GENDARM":      "GENDARM",
    "SIMIN":        "SIMIN",
    "NILUFAR":      "NILUFAR",
    "ZEITANSAGE":   "ZEITANSAGE",
}

DRAMA = [
  {"id":"00_narr_in","who":"SPRECHER","gap":0.0,
   "text":"Drei Szenen, eine Straße, eine Familie. Was sich ändert, ist nur die Richtung des Zwangs."},

  # ---- Bild 1: 1936 ----
  {"id":"01_zeit","who":"ZEITANSAGE","gap":0.7,"tag":"[calm]",
   "text":"Teheran. Neunzehnhundertsechsunddreißig."},
  {"cue":"atmo_1936","gain":0.9},
  {"id":"02_gendarm","who":"GENDARM","gap":0.7,"tag":"[shouting] Halt. [calm]",
   "text":"Du. Der Tschador. Du kennst den Erlass des Schahs: Keine Verhüllung auf öffentlicher Straße. Wir sind ein modernes Land."},
  {"id":"03_marjam","who":"MARJAM_YOUNG","gap":0.4,"tag":"[whispers]",
   "text":"Herr — ich trage ihn, seit ich denken kann. Meine Mutter, ihre Mutter — lass mich nach Hause, ich —"},
  {"cue":"cloth_tear","gain":0.85},
  {"id":"04_gendarm","who":"GENDARM","gap":0.6,"tag":"[calm]",
   "text":"Nach Hause gehst du ohne. So. Sag deinem Mann: Der Schah macht euch frei. Ob ihr wollt oder nicht."},
  {"id":"05_marjam","who":"MARJAM_YOUNG","gap":0.5,"tag":"[whispers]",
   "text":"Frei. — Ihr nehmt mir das Tuch, wie andere mir eines aufzwingen würden. Gefragt hat mich keiner von euch."},

  # ---- Bild 2: 1979 ----
  {"id":"06_zeit","who":"ZEITANSAGE","gap":0.8,"tag":"[calm]",
   "text":"Teheran. Neunzehnhundertneunundsiebzig. Der achte März."},
  {"cue":"atmo_1979","gain":0.9},
  {"id":"07_simin","who":"SIMIN","gap":0.7,
   "text":"Mutter, wenn du das sehen könntest — zehntausende! Lehrerinnen, Krankenschwestern, Studentinnen! Wir haben den Schah gestürzt — wir, auch wir! — und jetzt sagt der Ajatollah, ins Amt gehen wir künftig nur bedeckt. [angry] Ich habe die Revolution nicht gemacht, um rückwärtszugehen."},
  {"id":"08_marjam","who":"MARJAM_OLD","gap":0.5,"tag":"[calm]",
   "text":"Ich habe es ihnen gesagt, Kind, damals wie heute: Es war nie das Tuch. Vierunddreißig haben sie es mir vom Kopf gerissen, im Namen des Fortschritts. Jetzt nageln sie es deiner Tochter fest, im Namen Gottes. Es ist derselbe Griff. Nur die Hand wechselt."},

  # ---- Bild 3: 2022 ----
  {"id":"09_zeit","who":"ZEITANSAGE","gap":0.8,"tag":"[calm]",
   "text":"Teheran. Zweitausendzweiundzwanzig. September."},
  {"cue":"atmo_2022","gain":0.9},
  {"id":"10_nilufar","who":"NILUFAR","gap":0.7,"tag":"[whispers]",
   "text":"Großmutter — geh nicht ans Fenster, aber hör zu. Sie haben ein Mädchen sterben lassen, Dschina hieß sie, Mahsa stand im Pass. Aufgegriffen wegen ein paar Haarsträhnen. Und jetzt — hörst du das? Das ganze Viertel ruft es. Frau. Leben. Freiheit. — Ich habe dein altes Kopftuch dabei, das aus Maschhad. Ich trage es heute Nacht um den Hals. Nicht auf dem Kopf, nicht in der Tasche: um den Hals. Sollen sie raten, was es bedeutet."},
  {"id":"11_simin","who":"SIMIN","gap":0.5,"tag":"[calm]",
   "text":"Sag ihr, was die Urgroßmutter gesagt hat."},
  {"id":"12_nilufar","who":"NILUFAR","gap":0.5,"tag":"[whispers]",
   "text":"Ich weiß es auswendig, Oma. — Es war nie das Tuch. Es war immer die Frage, wessen Hand. Heute Nacht ist es meine."},

  # ---- Rahmen ----
  {"id":"13_narr_out","who":"SPRECHER","gap":0.8,
   "text":"Neunzehnsechsunddreißig: Entschleierung mit Polizeigewalt. Neunzehnneunundsiebzig: Verschleierung mit Revolutionsgewalt. Zweitausendzweiundzwanzig: Hunderttausende, angeführt von den Enkelinnen beider Zwänge. Dreimal derselbe Körper als Plakatfläche staatlicher Programme — und am Ende ein Satz, der die ganze Studie zusammenfasst: Es geht nie um das Tuch. Es geht darum, wessen Hand."},
]

NARR_HERAUS = "Wie realistisch ist diese Szene? Eine kurze Einordnung."

ANALYSIS = [
  "Neunzehnhundertsechsunddreißig: der Kaschf-e-hidschab-Erlass Reza Schahs verbot die Verschleierung im öffentlichen Raum; Polizisten rissen Frauen nachweislich die Tschadors herunter. Neunzehnhundertneunundsiebzig: die Frauendemonstrationen gegen Khomeinis Hidschab-Pflicht sind breit dokumentiert. Zweitausendzweiundzwanzig: der Tod Mahsa Aminis im Polizeigewahrsam und die \"Frau, Leben, Freiheit\"-Proteste sind Zeitgeschichte. Alles belegt.",
  "Die Drei-Generationen-Familie ist fiktiv, aber demographisch stimmig — plausibel. Ihr Kernbefund: Der Zwang wechselte die Richtung, nicht die Grammatik. Der weibliche Körper blieb der Austragungsort staatlicher Programme, säkular wie theokratisch. Mahsa Aminis Tod wird hier berichtet, nicht dargestellt.",
]

SFX = {
  "atmo_base":  {"prompt":"A very low, subtle neutral city-night ambience: distant muffled traffic, faint room tone, quiet, unobtrusive urban night bed", "auto":True},
  "atmo_1936":  {"prompt":"A 1930s Middle Eastern street: horse hooves on cobblestone, an early sputtering motorcar passing, market vendors calling, footsteps of two women", "dur":6},
  "atmo_1979":  {"prompt":"A large 1979 street demonstration: a dense crowd of women chanting rhythmically in unison, tense and energetic, protest atmosphere", "dur":6},
  "atmo_2022":  {"prompt":"A city night in 2022: distant crowds chanting rhythmically, growing closer, with a faint mobile-phone video recording crackle and hiss", "dur":6},
  "cloth_tear": {"prompt":"A single sharp piece of heavy cloth being torn and ripped away quickly", "dur":2},
}

MUSIC = {
  "intro":  {"prompt":"Bleak Persian mood, solo tar and setar, sparse, sorrowful and tense, cinematic, no vocals", "ms":20000},
  "bed":    {"prompt":"Very soft neutral documentary underscore: sustained low strings, contemplative, minimal, unobtrusive, no melody, no vocals", "ms":45000},
  "outro":  {"prompt":"Solemn Persian outro, tar and setar with slow percussion, hopeful and defiant, resolute, slowly fading, no vocals", "ms":22000},
}

SCENE = H.Scene(slug="die-frau-vor-dem-recht/S01-02/scene4", name="scene4",
                title="Die Frau vor dem Recht — Der Parallelbogen — Szene 4 — Der Schleier, dreimal",
                scene_index=None, voices=VOICES, reverb_roles=set(), drama=DRAMA,
                narr_heraus=NARR_HERAUS, sfx=SFX, music=MUSIC, display=DISPLAY,
                analysis=ANALYSIS)

if __name__ == "__main__":
    H.main(SCENE, sys.argv[1] if len(sys.argv) > 1 else "all")
