# Wusl Gusl — Episodenstruktur: das Drei-Stimmen-Modell

Eine Referenz für das Bauprinzip dieser Folge, das auf dem Originalformat der Wusel-Gudel-Sendung basiert.

## Produktion (gemessen, eleven_v3)

Vollständiger Render dieser Folge (138 Segmente / 18.479 Zeichen / ~26 min Audio): **~4,8 min** end-to-end (gen + mix), Kosten **~10.200 Credits (~$2,24)** → **~0,55 Credits/Zeichen**, Durchsatz **~64 Zeichen/Sek** (~5× Echtzeit; Mix +30–60 s). Faustregel für künftige Folgen: Kosten ≈ Zeichen × 0,55 Cr; Renderzeit ≈ Zeichen ÷ 64 s + ~1 min.

## Die drei Stimmen

**WUSL** (das lila Fellknäuel) ist der komödiantische Motor: manisch, stolz, laut, übermütig. Seine Gadgets piepen, explodieren und tun das Falsche. Witze, Soundgags, Ausrufe, Selbstüberschätzung — alles landet bei WUSL. Inline-Kues (`[stolz]`, `[quietscht]`, `[KRAWUMMS-Imitation]`) gehören zu seinen Zeilen.

**MODERATOR** (Benis Rolle, per `replace:`-Regel umbenannt) ist der geduldige Kumpel und Stichwortgeber. Er stellt die Fragen, die das nächste Einspieler motivieren, reagiert auf Wusls Eskapaden und führt zwischen den Einspieler-Blöcken durch. Leichte Ironie, freundliche Korrekturen, gelegentliches Lachen — aber keine Sachvorträge.

**ERZÄHLER** ist eine ruhige, warme, dokumentarische Stimme. Er liefert die inhaltlich dichten Erklärblöcke (die sogenannten Einspieler): sachlich, präzise, kind-friendly formuliert, aber ohne Witze, ohne Gadget-Gags, ohne Ausrufe und ohne Soundkues. Diese Trennung ist das Herzstück des Formats: Die Komödie trägt die Neugier, der Erzähler trägt das Wissen.

## Die Grundregel: Einspieler sind gagfrei

Die ERZÄHLER-Blöcke sind vollständig frei von Witzen, Scherzeinschüben, Soundkues (`[lacht]`, `[quietscht]` etc.) und Gerätehumor. Sie sind kurze, fokussierte Sachpassagen, die ein einzelnes Konzept erklären — so wie ein ruhiger Dokumentarfilm-Kommentar, der genau dann einsetzt, wenn der Witz verpufft ist und der Hörer bereit ist, etwas Echtes zu lernen. Alle Komik gehört in die umrahmenden WUSL- und MODERATOR-Zeilen.

## Rhythmus und Pacing

Das Format wechselt brisk zwischen zwei Phasen ab: erstens ein kurzes komisches Framing, das eine Frage aufwirft oder einen Gag aufbaut, und zweitens ein kompakter Einspieler, der die Frage beantwortet. Danach folgt eine schnelle Reaktion oder ein neuer Gag — und weiter zum nächsten Thema. Kein Block sollte so lange laufen, dass das Alternieren zum Stillstand kommt. Ein Einspieler hat typischerweise drei bis sechs Sätze (ca. 200–400 Zeichen), manchmal mehr für komplexere Themen wie die zwei Regelbücher oder die Gravitations-Problematik. Das WUSL/MODERATOR-Framing davor und danach ist oft nur zwei bis vier Zeilen lang.

## Wie Abschnitte aufgebaut sind

Jeder `## N · TITEL`-Abschnitt beginnt mit einem kurzen WUSL/MODERATOR-Austausch, der entweder eine Frage stellt, einen Gag aufbaut oder das Gadget des Abschnitts einführt. Dann setzt ERZÄHLER ein und liefert den Einspieler. Danach folgt eine Reaktion — Wusls Überraschung, sein nächster Einfall, oder ein kleiner Rückfragen-Gag — bevor der Übergang zum nächsten Abschnitt eingeleitet wird. Nicht jeder Abschnitt braucht einen Einspieler (Intro, Überblick, Outro sind reine Banter-Segmente), aber alle Wissensvermittlung liegt beim ERZÄHLER.

## Abschnittsgrenzen und Audio-Struktur

Die `## N · TITEL`-Überschriften triggern im Produktions-System (`produce.py`) das Bridge-Audio (ein kurzes Übergangs-Motiv), das zwischen Abschnitten eingeblendet wird. Das erzeugt eine klare, hörerfreundliche Gliederung ohne harte Schnitte. `<!-- start -->` und `<!-- end -->` begrenzen den parse-Bereich; alles außerhalb (diese Howto-Notiz, das Cue-Sheet) wird vom Engine ignoriert.

## Inline-Kues

Soundkues im v3-Format (`\`[lacht]\``, `\`[stolz]\``, `\`[quietscht]\`` etc.) gehören ausschließlich in WUSL- und MODERATOR-Zeilen. ERZÄHLER-Zeilen sind kue-frei. Standalone-Kue-Zeilen (z.B. `\`[Fanfare. Dann ein wildes Durcheinander...]\``) triggern SFX oder Musik-Events gemäß den `cue_rules` im YAML.

## Voices im YAML

WUSL: `xOrwxaQJaTlyIgWk33GY`, niedriges stability/similarity für maximale Lebendigkeit. MODERATOR: `rDBaN5ZF8ukjsiAjsmmU` (im Transcript als MODERATOR, via `replace:` zu Beni umbenannt). ERZÄHLER: `FTNCalFNG5bRnkkaP5Ug`, stability 0.5, similarity 0.75 — ausgewogen ruhig für dokumentarischen Ton. Alle drei nutzen `eleven_v3` und `speaker_boost: true`.
