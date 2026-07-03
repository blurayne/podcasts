# Die Frau vor dem Recht — Podcast Studio

> Doku-Feature-Podcast und Hörspiel-Produktion · 1.900 Jahre Rechtsgeschichte der Frau

**[→ Zur Website (GitHub Pages)](https://blurayne.github.io/podcasts/)**

---

## Staffel 1 · Die Frau vor dem Recht (S01)

### Folge 01 — Von der Seherin im Turm (Germanen & Europa)

Zweistimmiges Doku-Feature (35–40 min): Von Veleda, der Seherin der Brukterer (70 n. Chr.),
über fränkisches Mündelrecht und mittelhochdeutsches Stadtrecht bis zur rechtlichen
Gleichstellung in der BRD 1977.

| Dokument | Beschreibung |
|---|---|
| [Podcast-Skript](series/die-frau-vor-dem-recht/S01-01/podcast.md) | Vollständiges Doku-Feature-Skript |
| [Hörspiel-Szenen 1–3](series/die-frau-vor-dem-recht/S01-01/hoerspiele.md) | Drei dramatisierte Einlagen: Thing (90 n. Chr.), Verheiratung (Franken 9. Jh.), Island (~980) |
| [Wissenschaftliche Studie](series/die-frau-vor-dem-recht/S01-01/studie/studie.pdf) | Begleitstudie: Rechtsstellung der Frau, Germanen bis Frühmittelalter |
| [Analyse (HTML)](series/die-frau-vor-dem-recht/S01-01/studie/analyse.html) | HTML-Analysedokument zur Studie |

### Folge 02 — Der Parallelbogen (Von Mekka nach Neukölln)

Zweistimmiges Doku-Feature (55–60 min): Die Rechtsstellung der Frau im Islam, gespiegelt an
1.900 Jahren Europa — von Khadidscha in Mekka bis zur Mahsa-Amini-Generation und deutschem
Recht 2026. Fünf Hörspiel-Einlagen eingebettet.

| Dokument | Beschreibung |
|---|---|
| [Podcast-Skript](series/die-frau-vor-dem-recht/S01-02/podcast.md) | Vollständiges Doku-Feature-Skript |
| [Szene 1 — Die Kauffrau von Mekka](series/die-frau-vor-dem-recht/S01-02/szene-1-khadidscha-mekka.md) | Khadidscha bint Khuwailid, Mekka ~595 |
| [Szene 2 — Die Lehrerin der Männer](series/die-frau-vor-dem-recht/S01-02/szene-2-karima-mekka.md) | Karima al-Marwaziyya, Mekka ~1055 |
| [Szene 3 — Vor dem Kadi](series/die-frau-vor-dem-recht/S01-02/szene-3-aintab-kadi.md) | Osmanisches Recht, Aintab 1541 |
| [Szene 4 — Der Schleier, dreimal](series/die-frau-vor-dem-recht/S01-02/szene-4-teheran-schleier.md) | Teheran 1936 · 1979 · 2022 |
| [Szene 5 — Die Verheiratung der Tochter, 2026](series/die-frau-vor-dem-recht/S01-02/szene-5-deutschland-2026.md) | Deutschland, Gegenwart |
| [Vergleichsstudie](series/die-frau-vor-dem-recht/S01-02/studie/vergleichsstudie.pdf) | Akademische Begleitstudie Islam & Europa |

---

## Kleiner geht's nicht · Quarks for Kids

| Dokument | Beschreibung |
|---|---|
| [Folge 1 — Die Reise ins Allerkleinste](series/quarks-for-kids/podcast-kleiner-gehts-nicht.md) | Kinderpodcast: Atome, Quarks, Planck-Länge (10–12 min) |
| [HTML-Version](series/quarks-for-kids/reise-ins-allerkleinste.html) | Gerenderte HTML-Fassung |

---

## Analyse & Forschung

| Dokument | Beschreibung |
|---|---|
| [Hatten es Frauen bei den Germanen leichter?](NEXT.md) | Essay: formale Rechtslage, Sichtbarkeit, ökonomische Grundlogik — Germanen vs. Islam |
| [Intersektional-feministische Lektüre](docs/INTFEM-ANALYSIS.md) | Vier feministische Lesarten zu Folge 1 & 2, Patriarchat- und Feminismus-Definition |
| [Woke, Struktur und Identität](docs/NO-WOKE.md) | Analytische Abhandlung: Referenten von „woke", Steelman beider Seiten |

---

## Technik

Produziert mit [ElevenLabs](https://elevenlabs.io) TTS/SFX/Music · Python (`scripts/`) ·
ffmpeg für Assembly · Modell: `eleven_v3` · Nur studio-quality Stimmen (Professional-Kategorie).

Toolchain: `mise.toml` (Python 3.12, ffmpeg, jq, curl).
Orchestrierung: `scripts/hoerspiel.py` (Engine) + episodenspezifische Skripte.
