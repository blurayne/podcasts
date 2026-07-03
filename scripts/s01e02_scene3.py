#!/usr/bin/env python3
"""Islam Szene 3 — "Vor dem Kadi" (Aintab / Osmanisches Reich, 1541)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hoerspiel as H

VOICES = {
    "SPRECHER":  "dCnu06FiOZma2KVNUoPZ",  # Erzählstimme — documentary narrator
    "FATMA":     "BIvP0GN1cAtSRTxNHnWS",  # Fatma — the widow / plaintiff
    "KADI":      "ZgTblco1F8U3zN77c5Rj",  # the judge
    "MEHMED":    "FTNCalFNG5bRnkkaP5Ug",  # brother of the deceased husband
    "SCHREIBER": "wloRHjPaKZv3ucH7TQOT",  # the scribe
}
DISPLAY = {"SPRECHER":"ERZÄHLER", "FATMA":"FATMA", "KADI":"KADI",
           "MEHMED":"MEHMED", "SCHREIBER":"SCHREIBER"}

DRAMA = [
  {"id":"00_narr_in","who":"SPRECHER","gap":0.0,
   "text":"Aintab, Anatolien, im Jahr 1541. Das Sultansreich Süleymans führt über jede Gerichtsstube Buch. In diesen Registern — den Sicil — steht, was Normtexte nicht verraten: wer wirklich klagt. Und da steht, erstaunlich oft: eine Frau."},
  {"id":"01_kadi","who":"KADI","gap":0.6,
   "text":"Es erscheint Fatma, Tochter des Hüseyin, aus dem Viertel der Gerber, Witwe des Sattlers Ali. — Du sprichst selbst, Frau, oder durch einen Bevollmächtigten?"},
  {"id":"02_fatma","who":"FATMA","gap":0.4,
   "text":"Selbst, Efendi."},
  {"id":"03_schreiber","who":"SCHREIBER","gap":0.4,"tag":"[whispers]",
   "text":"… erschien in eigener Person …"},
  {"id":"04_fatma","who":"FATMA","gap":0.5,
   "text":"Mein Mann ist vor vier Monaten gestorben, Gott sei ihm gnädig. Sein Bruder Mehmed hat die Werkstatt genommen, das Haus, die zwei Weingärten. Ich fordere dreierlei: meinen aufgeschobenen Brautpreis — vierzig Silberstücke, so steht es im Ehevertrag —, denn der Mahr ist eine Schuld auf dem Nachlass. Dann meinen Erbanteil: der achte Teil, wie das Gesetz Gottes der Witwe zuweist. Und den kleinen Weingarten am Osttor fordere ich ganz — denn der ist gar kein Nachlass. Der ist mein Eigentum. Mein Vater hat ihn mir zur Hochzeit übertragen."},
  {"id":"05_mehmed","who":"MEHMED","gap":0.3,"tag":"[angry]",
   "text":"Efendi, sie hat im Haus meines Bruders gelebt, von seinem Brot —"},
  {"id":"06_kadi","who":"KADI","gap":0.3,"tag":"[calm]",
   "text":"Das Brot deines Bruders macht ihr Gut nicht zu deinem. — Frau: Beweise."},
  {"id":"07_fatma","who":"FATMA","gap":0.4,
   "text":"Für den Mahr: der Ehevertrag, hier, mit den Namen der Zeugen. Für den Weingarten: Er ist vor diesem Gericht eingetragen, im Register deines Vorgängers, im Jahr, als die große Dürre war. Und zwei Zeugen aus dem Viertel, die die Übertragung gesehen haben, warten draußen."},
  {"id":"08_kadi","who":"KADI","gap":0.5,
   "text":"Man hole den Band. … Eingetragen: Weingarten am Osttor, Übertragung an Fatma bint Hüseyin. — Mehmed: Bestreitest du die Eintragung dieses Gerichts?"},
  {"id":"09_mehmed","who":"MEHMED","gap":0.4,"tag":"[angry]",
   "text":"… Nein, Efendi."},
  {"id":"10_kadi","who":"KADI","gap":0.5,
   "text":"Dann ergeht, was ergehen muss. Schreiber: Der Weingarten am Osttor gehört der Klägerin und ist ihr unverzüglich zu überlassen. Aus dem Nachlass des Ali sind ihr auszukehren: vierzig Silberstücke aufgeschobener Mahr — vorab, als Schuld vor aller Teilung — sodann ihr Achtel nach dem Erbrecht."},
  {"id":"11_kadi","who":"KADI","gap":0.4,"tag":"[calm]",
   "text":"Und damit Friede in der Familie des Sattlers einkehre, wird dies alles versiegelt und verlesen. Wer es umstößt, stößt das Register des Sultans um."},
  {"cue":"seal_stamp","gain":0.85},
  {"id":"12_narr_out","who":"SPRECHER","gap":0.7,
   "text":"Kein Einzelfall, keine Legende — ein Durchschnittstag. Die Historikerin, die die Register von Aintab ausgewertet hat, fand Frauen als klagende Partei in Eigentums-, Erb- und Ehesachen; auch gegen die eigenen Verwandten. Und sie fand etwas, das noch mehr verblüfft: Frauen gingen an dieses Gericht, obwohl das Erbrecht ihnen nur den halben Anteil gab — weil ein halber Anteil, den ein Sultansregister schützt, mehr wert ist als ein ganzer, den niemand aufschreibt."},
]

NARR_HERAUS = "Wie realistisch ist diese Szene? Eine kurze Einordnung."

ANALYSIS = [
  "Setting und Verfahren sind aktengestützt: Leslie Peirce wertete die Gerichtsregister von Aintab des Jahrgangs 1540/41 monographisch aus. Frauen erschienen dort routinemäßig in eigener Person als Klägerinnen — um Mahr, Erbteil und Sondereigentum, auch gegen Schwäger — und gewannen häufig. Genau diese drei Anspruchsarten sind die typischen Klagefälle der Register. [belegt]",
  "Der Kern-Mechanismus ist die gütergetrennte Ehe des islamischen Rechts als Klagegrundlage: Weil ihr Vermögen nie in die Verwaltung des Mannes überging — anders als im BGB von 1900 —, hatte die Frau stets Eigenes einzuklagen. Grenze des Bildes: Die Register zeigen die, die kamen, nicht die durch Familiendruck Ferngehaltenen. Handlungsmacht ja, Verschiebung der Position nein — das Achtel bleibt ein Achtel. [plausibel]",
]

SFX = {
  "atmo_base":  {"prompt":"an Ottoman-era stone courtroom, muffled town outside, rustling paper, quiet footsteps on carpet", "auto":True},
  "seal_stamp": {"prompt":"a hard wax seal stamp pressed firmly onto paper twice, sharp and heavy on a wooden desk in a quiet stone room", "dur":2},
}
MUSIC = {
  "intro":  {"prompt":"Sober near-eastern court theme: restrained oud and soft frame drum, dignified and measured, quiet, no vocals", "ms":22000},
  "bed":    {"prompt":"Very soft neutral documentary underscore: sustained low strings, contemplative, minimal, unobtrusive, no melody, no vocals", "ms":45000},
  "outro":  {"prompt":"Reflective near-eastern outro: gentle oud and low strings, contemplative, slowly fading, no vocals", "ms":20000},
}

SCENE = H.Scene(slug="die-frau-vor-dem-recht/S01-02/scene3", name="scene3",
                title="Die Frau vor dem Recht — Der Parallelbogen — Szene 3 — Vor dem Kadi",
                scene_index=None, voices=VOICES, reverb_roles=set(), drama=DRAMA,
                narr_heraus=NARR_HERAUS, sfx=SFX, music=MUSIC, display=DISPLAY,
                analysis=ANALYSIS)

if __name__ == "__main__":
    H.main(SCENE, sys.argv[1] if len(sys.argv) > 1 else "all")
