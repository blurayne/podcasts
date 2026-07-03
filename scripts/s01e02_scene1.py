#!/usr/bin/env python3
"""Islam Szene 1 — „Die Kauffrau von Mekka" (Mekka, um 595 n. Chr.)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hoerspiel as H

VOICES = {
    "SPRECHER":   "dCnu06FiOZma2KVNUoPZ",  # narrator / ERZÄHLSTIMME
    "KHADIDSCHA": "7eVMgwCnXydb3CikjV7a",  # Khadidscha bint Khuwailid
    "NAFISA":     "uvysWDLbKpA4XvpD3GI6",  # Nafisa — Vertraute und Botin
    "MAISARA":    "FTNCalFNG5bRnkkaP5Ug",  # Maisara — Diener
}
DISPLAY = {
    "SPRECHER":"ERZÄHLER", "KHADIDSCHA":"KHADIDSCHA",
    "NAFISA":"NAFISA", "MAISARA":"MAISARA",
}

DRAMA = [
  {"cue":"atmo_base","gain":0.8},
  {"id":"00_narr_in","who":"SPRECHER","gap":0.0,
   "text":"Mekka, gut dreißig Jahre bevor es eine neue Weltreligion geben wird. Eine Handelsstadt ohne König, regiert von Sippen und Verträgen. In einem Kontor unweit des Heiligtums sitzt eine Frau über ihren Listen, die zweimal verwitwet ist, die nicht wieder verheiratet wurde — und die es sich leisten kann, dass das so bleibt."},
  {"id":"01_maisara","who":"MAISARA","gap":0.6,
   "text":"Herrin — die Ballen aus Busra sind verkauft, alle. Der Gewinn liegt über dem, was dein Vetter im letzten Jahr gemacht hat. Fast das Doppelte."},
  {"id":"02_khadidscha","who":"KHADIDSCHA","gap":0.4,"tag":"[calm]",
   "text":"Fast das Doppelte. Und die Karawane? Verluste, Streit, Zoll?"},
  {"id":"03_maisara","who":"MAISARA","gap":0.4,
   "text":"Nichts davon. Der Mann, den du angestellt hast — der Sohn Abdallahs, aus dem Haus Haschim — er handelt … er handelt, als gehöre die Ware ihm, und rechnet ab, als gehöre sie dir. Die Leute in Busra nannten ihn al-Amin. Den Zuverlässigen."},
  {"id":"04_khadidscha","who":"KHADIDSCHA","gap":0.5,
   "text":"Den Zuverlässigen. Nafisa."},
  {"id":"05_nafisa","who":"NAFISA","gap":0.4,
   "text":"Ich kenne dieses Gesicht. Das ist nicht das Gesicht einer Frau, die über Warenballen nachdenkt."},
  {"id":"06_khadidscha","who":"KHADIDSCHA","gap":0.4,
   "text":"Es ist das Gesicht einer Frau, die rechnet. Ich habe zwei Männer überlebt und mehr Vermögen gemehrt als die meisten Männer dieser Stadt. Jeder dritte Haushalt am Basar hat mich für seine Söhne gefragt — und ich habe jeden dritten Haushalt abgewiesen, denn sie fragten nicht nach mir, sie fragten nach meinen Karawanen. Dieser eine fragt nach gar nichts. Das gefällt mir."},
  {"id":"07_nafisa","who":"NAFISA","gap":0.4,
   "text":"Und was soll ich tun?"},
  {"id":"08_khadidscha","who":"KHADIDSCHA","gap":0.4,
   "text":"Was du am besten kannst: Geh zu ihm und stelle Fragen, die wie Plaudern klingen. Warum er nicht heiratet. Ob es am Brautgeld liegt. Und wenn er antwortet, wie ich glaube, dass er antwortet — dann frag ihn, was er zu einer Frau sagen würde, die Vermögen hat, Ansehen hat und ihn nicht nach seinem Besitz fragt."},
  {"id":"09_nafisa","who":"NAFISA","gap":0.4,"tag":"[laughs]",
   "text":"Du lässt ihn werben, indem du wirbst."},
  {"id":"10_khadidscha","who":"KHADIDSCHA","gap":0.4,
   "text":"Ich lasse ihn frei antworten. Das ist mehr, als diese Stadt ihren Töchtern gewährt. Meinen Oheim brauche ich am Ende für den Vertrag — einen Mann, der spricht, was ich beschlossen habe. So läuft es hier: Beschlossen wird im Kontor, gesprochen wird im Männerkreis. Geh, Nafisa."},
  {"cue":"footsteps_recede","gain":0.7},
  {"id":"11_narr_out","who":"SPRECHER","gap":0.6,
   "text":"Sie werden heiraten. Fünfundzwanzig Jahre lang, bis zu ihrem Tod, wird sie seine einzige Frau sein — in einer Stadt, in der Männern von Stand keine Zahl gesetzt ist. Und als er Jahre später zitternd von einer Erscheinung im Berg zurückkehrt, wird der erste Mensch, der ihm glaubt, diese Kauffrau sein. Der erste Muslim der Geschichte — nach allem, was die Überlieferung sagt — war eine Geschäftsfrau, die ihren Angestellten geheiratet hat."},
]

NARR_HERAUS = "Wie realistisch ist diese Szene? Eine kurze Einordnung."

ANALYSIS = [
  "Der Kern ist mehrfach belegt und im Milieu plausibel: Khadidscha war eine vermögende Fernhandelskauffrau, stellte Muhammad für ihre Syrien-Karawane an, war mit dem Ergebnis zufrieden und ließ die Eheanbahnung selbst ausgehen — über ihre Vertraute Nafisa. Auch der Beiname al-Amin, ihre zwei früheren Ehen und die Monogamie bis zu ihrem Tod stehen so in den ältesten Sira-Quellen: Ibn Ishaq, Ibn Sa'd.",
  "Vorbehalt: Diese Quellen sind erst 150 bis 200 Jahre später verschriftet, gesichert ist das Bild, nicht jedes Detail; ihr Alter — 40 oder 28 — bleibt umstritten. Dass eine selbstständige Kauffrau mit eigener Partnerwahl möglich war, gilt der Forschung als plausibel. Khadidscha ist das arabische Gegenstück zur húsfreyja: Beweis des Möglichen, nicht des Garantierten — der Vertrag wird im Kontor beschlossen, im Männerkreis gesprochen.",
]

SFX = {
  "atmo_base":        {"prompt":"A Middle-Eastern bazaar in Mecca at middle distance: camels grunting, merchants calling out, distant hammer strokes on metal; nearer, the soft clicking of counting stones and cloth being unrolled", "auto":True},
  "footsteps_recede": {"prompt":"footsteps on stone walking away and receding into the distance, the bazaar swelling briefly then settling", "dur":3},
}
MUSIC = {
  "intro":  {"prompt":"Evocative Middle-Eastern intro: solo oud plucking a modal desert melody, warm ney flute breath, distant frame drum, ancient and dignified, no vocals", "ms":22000},
  "bed":    {"prompt":"very soft neutral documentary underscore, minimal, no vocals", "ms":45000},
  "outro":  {"prompt":"Reflective oud outro: sparse gentle oud with soft ney, bittersweet and contemplative, slowly fading, no vocals", "ms":20000},
}

SCENE = H.Scene(slug="die-frau-vor-dem-recht/S01-02/scene1", name="scene1",
                title="Die Frau vor dem Recht — Der Parallelbogen — Szene 1 — Die Kauffrau von Mekka",
                scene_index=None, voices=VOICES, reverb_roles=set(), drama=DRAMA,
                narr_heraus=NARR_HERAUS, sfx=SFX, music=MUSIC, display=DISPLAY,
                analysis=ANALYSIS)

if __name__ == "__main__":
    H.main(SCENE, sys.argv[1] if len(sys.argv) > 1 else "all")
