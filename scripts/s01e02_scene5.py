#!/usr/bin/env python3
"""Szene 5 — "Die Verheiratung der Tochter — 2026" (Deutschland, Gegenwart)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hoerspiel as H

VOICES = {
    "SPRECHER":   "dCnu06FiOZma2KVNUoPZ",  # Erzählstimme / Doku-Rahmen
    "VATER":      "g1jpii0iyvtRs8fqXsd1",  # Ende 40, Familienoberhaupt
    "MUTTER":     "7eVMgwCnXydb3CikjV7a",  # Mitte 40, ambivalent
    "AMIRA":      "BIvP0GN1cAtSRTxNHnWS",  # 17, Gymnasiastin
    "ABU_KHALED": "nZpMT2RjIpaat0IaA7Sd",  # 60er, Vermittler
}
DISPLAY = {"SPRECHER":"ERZÄHLER", "VATER":"VATER", "MUTTER":"MUTTER",
           "AMIRA":"AMIRA", "ABU_KHALED":"ABU KHALED"}

DRAMA = [
  {"cue":"atmo_room","gain":0.7},
  {"id":"00_narr_in","who":"SPRECHER","gap":0.0,
   "text":"Eine Wohnung in einer deutschen Großstadt, ein Donnerstagabend. Die Familie hat Besuch. Es geht — wie vor zwölfhundert Jahren am Herdfeuer des fränkischen Hofes — um die Zukunft einer Tochter. Nur dass diese Tochter in drei Monaten Abitur schreibt."},
  {"id":"01_abu_khaled","who":"ABU_KHALED","gap":0.6,"tag":"[calm]",
   "text":"Bruder, ich bin nicht gekommen, um zu richten. Ich bin gekommen, damit zwei Familien Freunde bleiben. Dein Cousin sagt, es gab ein Wort zwischen euch. Ein Wort ist ein Wort."},
  {"id":"02_vater","who":"VATER","gap":0.5,
   "text":"Es gab ein Wort, Abu Khaled. Vor zwei Jahren schon. Sein Sohn ist ein guter Junge, er hat Arbeit, das Haus im Dorf ist fertig. Ich habe nichts versprochen, was ich nicht halten kann. Nur sie — sie macht mir Schande vor ihm."},
  {"id":"03_amira","who":"AMIRA","gap":0.4,
   "text":"Ich mache niemandem Schande. Ich habe niemandem etwas versprochen. Ich war fünfzehn, als ihr das „Wort“ gegeben habt. Mich hat keiner gefragt."},
  {"id":"04_abu_khaled","who":"ABU_KHALED","gap":0.5,"tag":"[calm]",
   "text":"Kind, niemand verheiratet dich morgen. Aber eine Verlobung ist kein Gefängnis, sie ist ein Schutz. Dein Vater trägt Verantwortung für dich. Wenn das Wort platzt, verliert er das Gesicht — und du verlierst mit."},
  {"id":"05_amira","who":"AMIRA","gap":0.4,"tag":"[calm]",
   "text":"Nach welchem Recht? Nach dem Gesetz hier bin ich mit achtzehn frei. Meine Lehrerin sagt — und die Beratungsstelle sagt es auch: Niemand darf mich verloben, verheiraten, niemand darf mir drohen. Das ist Paragraf 237. Ich habe die Nummer der Beratungsstelle im Handy, Baba. Ich will das nicht benutzen müssen. Ich will, dass wir reden."},
  {"id":"06_mutter","who":"MUTTER","gap":0.5,"tag":"[whispers]",
   "text":"Hör ihr zu. Sie ist die Erste von uns, die das Abitur macht. Meine Mutter wurde mit sechzehn gegeben, ich mit neunzehn. Vielleicht — vielleicht ist das Wort, das wir halten müssen, das an unsere Tochter."},
  {"id":"07_abu_khaled","who":"ABU_KHALED","gap":0.7,"tag":"[calm]",
   "text":"Bruder — ich sage dir, was ich deinem Cousin sagen werde: Eine Braut, die Nein sagt, ist kein Gewinn, sie ist eine offene Rechnung. Auch der Prophet hat den Konsens der Frau verlangt. Lass mich einen Weg finden, bei dem keiner das Gesicht verliert: kein Bruch — ein Aufschub. Nach dem Studium sieht man weiter. Und du, Kind: Ehre deinen Vater. Er trägt schwerer an alledem, als du siehst."},
  {"id":"08_narr_out","who":"SPRECHER","gap":0.6,
   "text":"Kein Urteil, kein Vertrag — ein Aufschub, der wie Frieden aussieht und ein Waffenstillstand ist. Die karolingische Tochter hatte in dieser Szene keinen Text. Amira hat einen: eine Schule, ein Gesetz, eine Telefonnummer. Das ist der ganze Unterschied von zwölfhundert Jahren — und er ist gewaltig. Aber der Tisch, an dem über sie verhandelt wird, steht noch."},
]

NARR_HERAUS = "Wie realistisch ist diese Szene? Eine kurze Einordnung."

ANALYSIS = [
  "Die Konstellation — transnationale Verlobungsabsprache, hinzugezogener Vermittler, ambivalente Mutter, bildungsorientierte Tochter und ein versöhnlicher „Aufschub“ — ist aus der Beratungspraxis vielfach dokumentiert: BMFSFJ-Studie von 2011, Fallberichte von Papatya und Terre des Femmes. Die Häufigkeit sollte man nicht überzeichnen; die Konstellation korreliert mit patrilinearen Ehr- und Clanstrukturen bestimmter Herkunftsmilieus, nicht mit Religiosität als solcher.",
  "Die Strukturparallele zur Karolingerszene trägt: der Vater als faktischer wali, der Konsens normativ vorgesehen und faktisch unter Druck. Der entscheidende Unterschied ist institutionell — 2026 hat die Tochter Exit-Optionen und damit Verhandlungsmacht: Paragraf 237 des Strafgesetzbuchs, Schulsozialarbeit, Jugendamt, anonyme Zufluchtseinrichtungen. Nicht die Gesinnung am Tisch hat sich zuerst geändert, sondern die Opportunitätsstruktur um den Tisch herum.",
]

SFX = {
  "atmo_base": {"prompt":"an intimate living room in the evening, faint clink of tea glasses, a muffled street behind the window", "auto":True},
  "atmo_room": {"prompt":"an intimate living room in the evening, faint clink of tea glasses, a muffled street behind the window", "dur":4},
}
MUSIC = {
  "intro":  {"prompt":"Warm restrained contemporary underscore, subtle oud and piano, intimate and quietly modern, not sentimental, no vocals", "ms":20000},
  "bed":    {"prompt":"Very soft neutral documentary underscore: sustained low strings, contemplative, minimal, unobtrusive, no melody, no vocals", "ms":45000},
  "outro":  {"prompt":"Reflective, quietly hopeful outro: warm restrained oud and piano, gently fading, no vocals", "ms":20000},
}

SCENE = H.Scene(slug="die-frau-vor-dem-recht/S01-02/scene5", name="scene5",
                title="Die Frau vor dem Recht — Der Parallelbogen — Szene 5 — Die Verheiratung der Tochter, 2026",
                scene_index=None, voices=VOICES, reverb_roles=set(), drama=DRAMA,
                narr_heraus=NARR_HERAUS, sfx=SFX, music=MUSIC, display=DISPLAY,
                analysis=ANALYSIS)

if __name__ == "__main__":
    H.main(SCENE, sys.argv[1] if len(sys.argv) > 1 else "all")
