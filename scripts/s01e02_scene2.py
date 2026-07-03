#!/usr/bin/env python3
"""Islam Szene 2 — „Die Lehrerin der Männer" (Mekka, um 1055 n. Chr.)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hoerspiel as H

VOICES = {
    "SPRECHER":         "dCnu06FiOZma2KVNUoPZ",  # Erzählstimme (Doku-Rahmen)
    "KARIMA":           "FOfJ2PMgU6HOGbNYnzto",  # Karima al-Marwaziyya
    "AL_CHATIB":        "fehqjfT0R2fGKeUX2YeE",  # al-Chatib al-Baghdadi
    "JUNGER_GELEHRTER": "f2yUVfK5jdm78zlpcZ8C",  # ungeduldiger junger Gelehrter
}
DISPLAY = {
    "SPRECHER":         "ERZÄHLER",
    "KARIMA":           "KARIMA",
    "AL_CHATIB":        "AL-CHATIB",
    "JUNGER_GELEHRTER": "EIN JUNGER GELEHRTER",
}

DRAMA = [
  {"cue":"atmo_base","gain":0.8},
  {"id":"00_narr_in","who":"SPRECHER","gap":0.0,
   "text":"Mekka, elftes Jahrhundert. Männer reisen tausende Kilometer aus Bagdad und Damaskus hierher — nicht nur zur Pilgerfahrt. Sie kommen, um bei einer Frau zu lernen. Wer die verlässlichste Fassung der wichtigsten Hadith-Sammlung des Islam hören will, des Sahih al-Buchari, der muss dorthin, wo sie gelesen wird: bei Karima, der Tochter Ahmads, aus Merw."},
  {"id":"01_junger","who":"JUNGER_GELEHRTER","gap":0.6,"tag":"[whispers]",
   "text":"Meister, wir sitzen den fünften Tag. In Bagdad wartet dein Lehrstuhl. Kann man die restlichen Kapitel nicht … zügiger hören?"},
  {"id":"02_chatib","who":"AL_CHATIB","gap":0.5,
   "text":"Ich habe für dieses Buch auf zehn Reisen mein Leben riskiert. Ich werde es nicht auf den letzten Seiten verderben, weil ein junger Mann Heimweh hat."},
  {"id":"03_karima","who":"KARIMA","gap":0.5,"tag":"[calm]",
   "text":"Der junge Mann möge lauter ungeduldig sein. Dann hört man wenigstens, wo er liest, statt zu lesen. — Fahre fort, Abu Bakr. Kapitel über das Fasten, die dritte Überlieferung."},
  {"id":"04_chatib","who":"AL_CHATIB","gap":0.5,
   "text":"… erzählte uns Abdallah ibn Maslama, von Malik, von Nafi, von Abdallah ibn Umar, Gott habe an beiden Wohlgefallen …"},
  {"id":"05_karima","who":"KARIMA","gap":0.4,"tag":"[calm]",
   "text":"Halt. Lies die Kette noch einmal."},
  {"id":"06_chatib","who":"AL_CHATIB","gap":0.4,
   "text":"Von Malik, von Nafi, von Abdallah ibn —"},
  {"id":"07_karima","who":"KARIMA","gap":0.5,"tag":"[calm]",
   "text":"In deiner Abschrift steht Abdallah ibn Maslama. In meiner Vorlage — und ich habe sie vor sechzig Jahren gegen das Exemplar meines Lehrers al-Kuschmihani kollationiert, Buchstabe für Buchstabe — steht an dieser Stelle ein anderer Anfang der Kette. Dein Kopist hat zwei Überlieferungen verschränkt. Streich es an. Wer bei mir hört, nimmt meine Lesart mit oder gar keine."},
  {"id":"08_chatib","who":"AL_CHATIB","gap":0.5,
   "text":"Deshalb bin ich hier, Herrin. In Bagdad sagen sie: Wer al-Buchari von Karima hat, dessen Text streitet niemand an."},
  {"id":"09_karima","who":"KARIMA","gap":0.4,"tag":"[calm]",
   "text":"In Bagdad sagen sie viel. Sie sagen auch, es sei wunderlich, dass Männer bei einer alten Frau sitzen. Dabei ist es das Gewöhnlichste der Welt: Der Prophet hat gesagt, nehmt die Hälfte eurer Religion von Aischa. Eine Kette ist eine Kette. Sie fragt nicht, was zwischen den Beinen dessen ist, der sie trägt — sie fragt, ob er wahrhaftig ist und ob er genau ist. Ich bin genau."},
  {"id":"10_narr_out","who":"SPRECHER","gap":0.7,
   "text":"Als die Lesung vollendet ist, stellt sie die Bescheinigung aus — die Idschaza, die Lehrerlaubnis: Der berühmteste Gelehrte Bagdads darf dieses Buch fortan überliefern, weil eine Frau ihm bezeugt, dass er es richtig gehört hat. Er wird als al-Chatib al-Baghdadi in die Wissenschaftsgeschichte eingehen. In seiner Überliefererkette, gesprochen in Moscheen bis heute, steht ihr Name."},
]

NARR_HERAUS = "Wie realistisch ist diese Szene? Eine kurze Einordnung."

ANALYSIS = [
  "Person und Konstellation sind historisch belegt: Karima al-Marwaziyya war die angesehenste Überliefererin des Sahih al-Buchari ihrer Zeit, und prominente Gelehrte reisten eigens zu ihr, darunter tatsächlich al-Chatib al-Baghdadi. Die biographischen Lexika, etwa adh-Dhahabi, verzeichnen sie. Auch ihre Arbeitsweise — Kollation gegen die Vorlage des Lehrers, Bestehen auf der eigenen Lesart — entspricht der Überlieferung. Belegt.",
  "Weibliche Überlieferungs-Autorität war im klassischen Islam normal: Mohammad Akram Nadwi zählt über achttausend muhaddithat, weibliche Hadith-Gelehrte, mit Lehrautorität ausdrücklich auch über Männer. Das männliche Monopol lag eine Ebene höher — beim Rechtsgutachten und beim Richteramt. Der genaue Wortlaut und die konkrete Kollations-Korrektur sind dramatische Lizenz, doch der Fehlertyp verschränkter Ketten ist fachlich realistisch. Belegt.",
]

SFX = {
  "atmo_base": {"prompt":"quiet mosque courtyard, distant pilgrims, doves, dry rustle of large paper pages, a reed pen scratching", "auto":True},
  "paper":     {"prompt":"the dry rustle and turning of large heavy manuscript paper pages", "dur":2},
}
MUSIC = {
  "intro":  {"prompt":"Middle-Eastern ney flute solo, scholarly and contemplative, quiet and reverent, sparse, no vocals", "ms":22000},
  "bed":    {"prompt":"Very soft neutral documentary underscore: sustained low strings, contemplative, minimal, unobtrusive, no melody, no vocals", "ms":45000},
  "outro":  {"prompt":"Reflective Middle-Eastern ney flute, gentle and meditative, slowly fading, no vocals", "ms":20000},
}

SCENE = H.Scene(slug="die-frau-vor-dem-recht/S01-02/scene2", name="scene2",
                title="Die Frau vor dem Recht — Der Parallelbogen — Szene 2 — Die Lehrerin der Männer",
                scene_index=None, voices=VOICES, reverb_roles=set(), drama=DRAMA,
                narr_heraus=NARR_HERAUS, sfx=SFX, music=MUSIC, display=DISPLAY,
                analysis=ANALYSIS)

if __name__ == "__main__":
    H.main(SCENE, sys.argv[1] if len(sys.argv) > 1 else "all")
