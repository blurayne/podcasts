# Build-Pipeline & Layout-System „Observatory"
### Dokumentation für die Reihe „Die Frau vor dem Recht" (Bände VII–X)

Diese Datei hält fest, **wie** die PDF-Studien der Reihe kompiliert wurden und **welches Layout** dabei durchgehend zum Einsatz kam — als Referenz für künftige Bände oder falls die Pipeline auf einem anderen Rechner reproduziert werden soll.

---

## 1. Toolchain

| Komponente | Version/Quelle |
|---|---|
| Engine | **XeTeX** 3.141592653-2.6-0.999995 (TeX Live 2023, Debian) |
| Aufruf | `xelatex` (nicht `pdflatex` — zwingend wegen `fontspec` + eingebetteter OTF-Fonts) |
| Durchläufe | **2×** pro Dokument (erster Durchlauf schreibt `.toc`/Referenzen, zweiter löst sie auf) |
| Fehlerprüfung | `grep -cE '^! ' logfile.log` — jede Zahl >0 heißt: Kompilierung hat harte Fehler |

**Kompilier-Befehl (Standard für jeden Band):**
```bash
xelatex -interaction=nonstopmode band10.tex > pass1.log 2>&1
xelatex -interaction=nonstopmode band10.tex > pass2.log 2>&1
grep -E '^! ' pass2.log   # muss leer sein
pdfinfo band10.pdf | grep Pages
```

---

## 2. Font-Beschaffung

Zwei Font-Familien, **lokal in einen `fonts/`-Unterordner neben die `.tex`-Datei** kopiert (nicht systemweit installiert — macht das Projekt portabel):

| Familie | Schnitte | Quelle | Stolperstein |
|---|---|---|---|
| **Space Grotesk** | Light, Regular, Medium, Bold | `github.com/floriankarsten/space-grotesk`, Pfad `master/fonts/otf/` | — |
| **IBM Plex Mono** | Regular, Medium, Text, Bold | `raw.githubusercontent.com/IBM/plex/`**`v6.4.0`**`/IBM-Plex-Mono/fonts/complete/otf/` | Der `master`-Pfad liefert eine **HTML-404-Seite statt der Schrift** — zwingend den Tag `v6.4.0` (oder eine andere feste Release-Version) verwenden, sonst landet eine kaputte HTML-Datei als „Font" im Ordner. |

Geladen wird ausschließlich über `fontspec` mit explizitem `Path=./fonts/`:

```latex
\usepackage{fontspec}
\setmainfont{SpaceGrotesk-Regular.otf}[
  Path=./fonts/,
  BoldFont=SpaceGrotesk-Bold.otf,
  FontFace={lt}{n}{SpaceGrotesk-Light.otf},
  FontFace={mb}{n}{SpaceGrotesk-Medium.otf}]
\newfontfamily\grotesklight{SpaceGrotesk-Light.otf}[Path=./fonts/]
\newfontfamily\groteskmed{SpaceGrotesk-Medium.otf}[Path=./fonts/]
\setmonofont{IBMPlexMono-Regular.otf}[
  Path=./fonts/,
  BoldFont=IBMPlexMono-Bold.otf,
  FontFace={md}{n}{IBMPlexMono-Medium.otf}]
```

`\grotesklight` / `\groteskmed` sind die Handles, über die im Fließtext gezielt der leichte bzw. mediumfette Schnitt angesprochen wird (v. a. auf der Titelseite).

---

## 3. Bekannte Preambel-Fallstricke (und ihre Fixes)

Diese Probleme sind in früheren Bänden aufgetreten und wurden fest in die Vorlage eingebaut:

- **`csquotes` + deutsche Anführungszeichen:** `\usepackage[autostyle=false,german=quotes]{csquotes}` — ohne `autostyle=false` kollidiert das Paket mit der manuellen `\enquote{}`-Verwendung im Text.
- **`\blacksquare` für die Konfidenz-Legende:** benötigt `\usepackage{amssymb}` — ohne das Paket bricht die Titelseite (Legendensymbole) mit „Undefined control sequence" ab.
- **Kein `fontawesome5`:** Paket ist in dieser Umgebung nicht verfügbar — alle Icons/Symbole laufen stattdessen über einfache Unicode-/`amssymb`-Zeichen.
- **`datenbox`-Titel mit Kommas:** Der optionale Titel-Parameter der `datenbox` muss als `title={#1}` (in geschweiften Klammern) übergeben werden — sonst interpretiert `tcolorbox` ein Komma im Titeltext als Ende des optionalen Arguments und bricht das Parsing.
- **`&` in Box-Titeln:** muss als `\&` escaped werden, sonst interpretiert LaTeX es als Tabellen-Spaltentrenner.
- **Heredoc-Encoding:** Beim Anhängen von Textblöcken per `bash`-Heredoc (`cat >> datei.tex << 'EOF'`) sind vereinzelt einzelne Umlaut-Bytes korrumpiert (`0xa4` statt `ä`). Fix: Datei binär einlesen, kaputte Bytes gezielt ersetzen, UTF-8 zurückschreiben — und **danach immer** `python3 -c "open(datei).read()"` zur Kontrolle laufen lassen.
- **Gedankenstriche:** `---`/`--` im Quelltext verlassen sich auf die automatische TeX-Ligatur-Konvertierung zu Em-/En-Dash. Sicherer (und für dieses Projekt inzwischen Standard): die echten Unicode-Zeichen **—** (Em-Dash) und **–** (En-Dash) direkt im Quelltext verwenden — funktioniert unabhängig von Font-Ligatur-Einstellungen.

---

## 4. Seitenlayout

```latex
\usepackage[a4paper,margin=2.3cm,top=2.5cm,bottom=2.5cm]{geometry}
```

A4, schmale Ränder (2,3 cm seitlich, 2,5 cm oben/unten) — bewusst enger als der LaTeX-Standard, damit die zweispaltig wirkenden Datenboxen und Tabellen genug Breite haben.

**Kopf-/Fußzeile** (`fancyhdr`): dünne helle Trennlinie (`obsline`, 0,4 pt), links der Reihentitel, rechts der Bandtitel, beide in `\scshape`, gedämpfter Farbe (`obsmuted`); Fußzeile zentriert nur die Seitenzahl.

**Absatzformat:** kein Einzug (`\parindent=0pt`), stattdessen vertikaler Abstand zwischen Absätzen (`\parskip=0.55em`) — Blocksatz-Fließtext-Konvention statt klassischer Buchsatz-Einzüge.

---

## 5. Die Observatory-Farbpalette

Ein dunkles Titelblatt, ein helles Innenlayout — zwei Modi derselben Palette:

```latex
\definecolor{obsbg}{HTML}{0F172A}       % tiefes Schiefergrau — Titelseiten-Hintergrund
\definecolor{obscard}{HTML}{1E293B}     % helleres Schiefergrau — Merksatz-Boxen
\definecolor{obsink}{HTML}{1A2333}      % Beinahe-Schwarz — Fließtextfarbe im Innenteil
\definecolor{obsmuted}{HTML}{64748B}    % gedämpftes Grau — Kopfzeile, Nebentext
\definecolor{obsline}{HTML}{CBD5E1}     % helle Linie — Trennregeln auf dunklem Grund
\definecolor{obsaccent}{HTML}{38BDF8}   % Himmelblau — Akzent, § -Nummern, Links
\definecolor{obsviolet}{HTML}{818CF8}   % Indigo — zweiter Akzent, Subsections
\definecolor{obspaper}{HTML}{F8FAFC}    % Off-White — Textfarbe auf dunklem Grund
```

**Vier Konfidenz-Farben**, quer durch die ganze Reihe identisch verwendet:

```latex
\definecolor{cbelegt}{HTML}{059669}     % Smaragdgrün
\definecolor{cplausibel}{HTML}{0284C7}  % Blau
\definecolor{cumstritten}{HTML}{D97706} % Bernstein
\definecolor{cspekulativ}{HTML}{9333EA} % Violett
```

---

## 6. Die Konfidenz-Chips

Kernidee der ganzen Reihe: **jede belastbare Aussage trägt sichtbar ihren Evidenzgrad**. Umgesetzt als kleine farbige Inline-Badges via `tcolorbox`:

```latex
\newtcbox{\chip}[1][obsmuted]{on line,boxsep=0pt,left=5pt,right=5pt,top=1.5pt,bottom=1.5pt,
  colframe=#1,colback=#1,coltext=white,boxrule=0pt,arc=2pt,fontupper=\ttfamily\scriptsize\bfseries}
\newcommand{\belegt}{\chip[cbelegt]{belegt}}
\newcommand{\plausibel}{\chip[cplausibel]{plausibel}}
\newcommand{\umstritten}{\chip[cumstritten]{umstritten}}
\newcommand{\spekulativ}{\chip[cspekulativ]{spekulativ}}
```

Im Fließtext einfach als `\belegt`, `\plausibel` etc. hinter die jeweilige Aussage gesetzt — erscheint als kleines, abgerundetes, farbiges Label direkt im Text.

Legende dazu (auf jeder Titelseite):

- 🟩 **belegt** · quellennah/empirisch gesichert
- 🟦 **plausibel** · begründete Deutung
- 🟧 **umstritten** · aktive Forschungskontroverse
- 🟪 **spekulativ** · Hypothese jenseits der Evidenz

---

## 7. Die drei Kasten-Typen

Drei wiederkehrende `tcolorbox`-Umgebungen strukturieren jede Studie:

### `merksatz` — die Kernthese zum Mitnehmen
Dunkler Kasten (Kartenfarbe `obscard`), heller Text, mediumfette Grotesk in „large". Wird für die jeweils wichtigste, zitierfähige Aussage eines Abschnitts benutzt — bewusst visuell vom Fließtext abgesetzt wie ein Pull-Quote.

### `datenbox` — harte Zahlen/Befunde mit Titel
Heller Kasten, dünne linke Akzentlinie in Himmelblau, optionaler Titel in Mono-Schrift oberhalb des Texts (z. B. „BEFUND · HUNT, EASTWICK & FINKEL 2015"). Für konkrete Studienbefunde, die als Zitatblock hervorgehoben werden sollen.

### `gegen` — die Gegendarstellung
Heller Kasten, linke Akzentlinie in Bernstein (derselbe Ton wie „umstritten"), mit einem `tcolorbox`-Overlay-Label „GEGENDARSTELLUNG" oben links, das über den Rahmen hinausragt. Trägt in jeder Studie den stärksten Einwand gegen die gerade vorgetragene These — das methodische Herzstück der ganzen Reihe (Gegendarstellungspflicht).

```latex
\newtcolorbox{gegen}{
  enhanced,breakable,
  colback=obspaper,colframe=cumstritten,
  boxrule=0pt,leftrule=3pt,arc=1pt,
  left=12pt,right=12pt,top=8pt,bottom=8pt,
  overlay unbroken and first={
    \node[anchor=north west,font=\ttfamily\scriptsize\bfseries\color{cumstritten}]
    at ([xshift=12pt,yshift=-4pt]frame.north west){GEGENDARSTELLUNG};},
  before upper={\vspace{1.1em}}}
```

---

## 8. Überschriften

```latex
\titleformat{\section}
  {\groteskmed\Large\color{obsink}}
  {\color{obsaccent}\S\,\thesection}{0.7em}{}
  [\vspace{-0.6em}{\color{obsline}\rule{\textwidth}{0.4pt}}]
\titleformat{\subsection}
  {\groteskmed\large\color{obsink}}
  {\color{obsviolet}\thesubsection}{0.6em}{}
```

Abschnitte werden **nicht** als „1. Kapitel …" nummeriert, sondern als „**§ 1** …" mit dem Paragraphenzeichen in Akzentblau, gefolgt von einer dünnen Trennlinie unter der ganzen Zeile. Subsections bekommen dieselbe Optik in Violett, ohne Trennlinie. Größere Studien (Doppelstudien wie Band IX) gliedern zusätzlich in `\part*{Teil …}` — unnummerierte Teile, die nur im Inhaltsverzeichnis auftauchen (`\addcontentsline{toc}{part}{…}`).

---

## 9. Die Titelseite

Vollflächig dunkel (`obsbg`), über `\newgeometry{margin=0pt}` + `colorbox` + `minipage[t][\paperheight][t]` als eigene „Seite in der Seite" gebaut, danach `\restoregeometry` für den Rest des Dokuments. Feststehender Aufbau, Zeile für Zeile:

1. **Kicker-Zeile** in Mono/Akzentblau: `OBSERVATORY · [Fachgebiet] · [Band] · [Untertitel-Kategorie]`, darunter eine dünne graue Trennlinie
2. **Reihentitel** klein, hell, Light-Schnitt: „Die Frau vor dem Recht"
3. **Bandtitel** riesig (40 pt), Medium-Schnitt: der eigentliche Titel
4. **Untertitel** kursiv, Light, in gedämpftem Hellgrau
5. Trennlinie, dann ein **Abstract-Absatz** (4–6 Zeilen Fließtext, was der Band leistet)
6. Die **Konfidenzmarker-Legende** (s. o.) in kleiner Mono-Schrift
7. `\vfill`, dann **Datum + Leitformel** ganz unten: „6. Juli 2026 · Leitformel: Rechtsstellung folgt Funktionsstellung"

Nach der Titelseite folgt automatisch `\tableofcontents` (unnummeriert, `\thispagestyle{empty}`), dann `\clearpage` und der Einsprung in den eigentlichen Studientext per `\input{…_body.tex}` — jeder Band hat seinen Fließtext in einer eigenen `_body.tex`-Datei, während die Wrapper-Datei (`band10.tex` etc.) nur Präambel + Titelseite + den `\input`-Befehl enthält. Das hält die Vorlage wiederverwendbar: ein neuer Band = Präambel kopieren, Titelseite austauschen, neue `_body.tex` schreiben.

---

## 10. Dateistruktur pro Band

```
bandX/
├── band10.tex        ← Wrapper: Präambel, Farben, Boxen, Titelseite, \input
├── x_body.tex         ← der eigentliche Studientext (§§, Boxen, Kapitel)
├── band10.pdf         ← kompiliertes Ergebnis
└── fonts/
    ├── SpaceGrotesk-{Light,Regular,Medium,Bold}.otf
    └── IBMPlexMono-{Regular,Medium,Text,Bold}.otf
```

Diese Trennung Wrapper/Body ist der Grund, warum sich alle vier Bände (VII–X) so schnell aus dem jeweils vorherigen ableiten ließen: Titelseite und Präambel werden per Skript kopiert und nur die Textbausteine (Titel, Kicker, Abstract) ausgetauscht, der `_body.tex`-Inhalt wird komplett neu geschrieben.
