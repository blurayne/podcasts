# Restructure Plan — file/folder reorganisation (REVIEW BEFORE EXECUTION)

Goal: a **sense-making, episode-oriented** layout. Nothing here is executed yet —
this is for your OK. Estimated credit cost: **0** (all moves + free ffmpeg re-mixes;
no re-generation of any TTS/SFX/music stem).

## Problems with the current layout

- Episode content is split inconsistently: Ep 1 sources sit at repo **root**
  (`play.md`, the podcast transcript, the analysis HTML) **plus** `part1-germanucus/`
  (study .tex/.pdf, note the typo *germanucus*); Ep 2 sources sit tidily in `part2-islam/`.
- Naming is mixed: `scene2.py` vs `islam_szene3.py` vs `produce_scene1.py`;
  output `scene1_thing.mp3` vs `scene2.mp3` vs `islam-szene1.mp3`.
- Docs are scattered at root (`PLAN.md`, `PODCAST-PLAN.md`, `API-CLI.md`,
  `INTFEM-ANALYSIS.md`, `WOKE.md`, the studio-request), one plan hides in `part2-islam/`.
- Stray artefacts: `out/podcast/…-v2.mp3` (leftover), `scripts/__pycache__/`.

## Entscheidungen (fixiert)

1. **Verschachtelte** Output-Ordner (braucht die ~5-Zeilen-Engine-Änderung: `Scene` bekommt
   `slug` = Unter­pfad unter `out/` **und** `name` = Datei-Basisname).
2. **Pläne immer getrennt** (kein Merge von `PLAN.md` + `PODCAST-PLAN.md`).
3. Struktur **`series/<name>/S01-01`** = Season 01, Folge 01. Serie = `die-frau-vor-dem-recht`;
   S01-01 = Folge 1 (Germanen/Europa), S01-02 = Folge 2 („Der Parallelbogen").

## Target tree

```
audiobook/
├── AGENTS.md   CLAUDE.md→AGENTS.md   mise.toml   .env   .claude/     (unchanged, root)
├── docs/
│   ├── API-CLI.md   INTFEM-ANALYSIS.md   WOKE.md   RESTRUCTURE-PLAN.md
│   ├── studio-api-access-request.md
│   └── templates/studio-api-access-request.template.md
├── scripts/
│   ├── el.py   hoerspiel.py                       (shared — Namen bleiben; Engine: slug+name)
│   ├── s01e01_scene1.py  s01e01_scene2.py  s01e01_scene3.py  s01e01_podcast.py
│   └── s01e02_scene1.py … s01e02_scene5.py         s01e02_podcast.py
├── series/die-frau-vor-dem-recht/
│   ├── S01-01/                                     (Folge 1 — Germanen/Europa)
│   │   ├── PLAN.md   PODCAST-PLAN.md
│   │   ├── hoerspiele.md          (was play.md — Szenen 1–3 in einer Datei)
│   │   ├── podcast.md             (was …_die-frau-vor-dem-recht.md)
│   │   └── studie/  studie.tex  studie.pdf  analyse.html
│   └── S01-02/                                     (Folge 2 — „Der Parallelbogen")
│       ├── PLAN.md                (was part2-islam/EPISODE2-PLAN.md; enthält Podcast+Szenen)
│       ├── podcast.md             (was …_der-parallelbogen.md)
│       ├── szene-1-khadidscha-mekka.md … szene-5-deutschland-2026.md
│       └── studie/  vergleichsstudie.tex  vergleichsstudie.pdf
└── out/die-frau-vor-dem-recht/
    ├── S01-01/  scene1/  scene2/  scene3/  podcast/     (Dateien: scene1.mp3, scene1_play.mp3,
    └── S01-02/  scene1/ … scene5/  podcast/              scene1_audiobook.mp3, .txt; podcast/podcast.mp3)
```

*Anpassung der Rename-Maps unten:* die „To"-Spalten verwenden nun
`series/die-frau-vor-dem-recht/S01-0X/…`, die Slugs werden `die-frau-vor-dem-recht/S01-0X/sceneN`
(Basisname `sceneN`), die Skripte `s01e0X_*.py`. Sonst unverändert.
*Hinweis Ausnahme #2:* Folge 2 hat bislang **nur einen** kombinierten Plan (EPISODE2-PLAN.md);
er wird zu `S01-02/PLAN.md` — ich **splitte ihn nicht** (getrennt-Regel = nicht mergen, nicht
zwangsweise aufteilen). Sag Bescheid, falls du für S01-02 doch eine eigene `PODCAST-PLAN.md` willst.

## Rename map — SOURCES & STUDIES

| From | To |
|---|---|
| `play.md` | `series/ep1-die-frau-vor-dem-recht/hoerspiele.md` |
| `2026-07-02_podcast-transkript_die-frau-vor-dem-recht.md` | `series/ep1-…/podcast.md` |
| `2026-07-01_…_analyse_v4.html` | `series/ep1-…/studie/analyse.html` |
| `part1-germanucus/…_studie.tex` / `…_studie_latex.pdf` | `series/ep1-…/studie/studie.tex` / `studie.pdf` |
| `part2-islam/…_der-parallelbogen.md` | `series/ep2-der-parallelbogen/podcast.md` |
| `part2-islam/…_hoerspiel-islam_szene-N_*.md` | `series/ep2-…/szene-N-*.md` |
| `part2-islam/…_vergleichsstudie.tex` / `…_latex.pdf` | `series/ep2-…/studie/vergleichsstudie.tex` / `.pdf` |
| `part2-islam/EPISODE2-PLAN.md` | `series/ep2-…/PLAN.md` |

(then remove the now-empty `part1-germanucus/`, `part2-islam/`)

## Rename map — DOCS

| From | To |
|---|---|
| `PLAN.md` | `series/ep1-…/PLAN.md` |
| `PODCAST-PLAN.md` | `series/ep1-…/PODCAST-PLAN.md` |
| `API-CLI.md` | `docs/API-CLI.md` |
| `INTFEM-ANALYSIS.md` | `docs/INTFEM-ANALYSIS.md` |
| `WOKE.md` | `docs/WOKE.md` |
| `elevenlabs-studio-access-request.md` | `docs/studio-api-access-request.md` |
| `templates/elevenlabs-studio-access-request.md` | `docs/templates/studio-api-access-request.template.md` |
| `AGENTS.md`, `CLAUDE.md` | **stay at root** (symlink preserved) |

## Rename map — SCRIPTS  (＋ required edits)

| From | To | Edits needed |
|---|---|---|
| `produce_scene1.py` | `ep1_scene1.py` | `play.md`→ep1 hoerspiele path; `OUT` `scene1`→`ep1-scene1`; final `scene1_thing.mp3`→`ep1-scene1.mp3` |
| `scene2.py` | `ep1_scene2.py` | `slug` `scene2`→`ep1-scene2`; pass ep1 source path (see hoerspiel) |
| `scene3.py` | `ep1_scene3.py` | `slug` `scene3`→`ep1-scene3` |
| `produce_podcast.py` | `ep1_podcast.py` | `SRC`→`series/ep1-…/podcast.md`; `OUT` `podcast`→`ep1-podcast` |
| `islam_szene1.py … 5` | `ep2_scene1.py … 5` | `SOURCE`→`series/ep2-…/szene-N-*.md`; `slug` `islam-szeneN`→`ep2-sceneN` |
| `produce_podcast2.py` | `ep2_podcast.py` | `SRC`→`series/ep2-…/podcast.md`; `OUT` `podcast-ep2`→`ep2-podcast`; `play_path()` `out/islam-szeneN`→`out/ep2-sceneN` |
| `hoerspiel.py` | *(name kept)* | line 77 `open(ROOT/"play.md")`: make `analysis_paragraphs()` take a source path; `Scene` gains `source_md=`; ep1 scene2/3 pass `series/ep1-…/hoerspiele.md`. (Keeps the engine episode-agnostic.) |
| `el.py` | *(unchanged)* | none |

No script imports another scene script, so renaming entry-point scripts is safe;
the only cross-file **data** dependency is `ep2_podcast.py` → `out/ep2-sceneN/..._play.mp3`.

## Rename map — OUTPUTS (work preserved, no re-gen)

Method per unit: **move the dir**, then run `python3 scripts/<script> mix book`
(ffmpeg-only, free) to re-emit the final files under the new slug; delete old-named finals.
Stems (`voices/ sfx/ music/`) don't embed the slug, so the dir-move keeps them and
`skip_existing` prevents any re-generation.

| From | To |
|---|---|
| `out/scene1/` (`scene1_thing.mp3`) | `out/ep1-scene1/` (`ep1-scene1.mp3`) |
| `out/scene2/`, `out/scene3/` | `out/ep1-scene2/`, `out/ep1-scene3/` |
| `out/podcast/` | `out/ep1-podcast/` (keep `podcast_die-frau-vor-dem-recht.mp3`) |
| `out/islam-szene1…5/` | `out/ep2-scene1…5/` (`islam-szeneN*.mp3`→`ep2-sceneN*.mp3`) |
| `out/podcast-ep2/` | `out/ep2-podcast/` |

## Doc cross-references to update

`AGENTS.md` (Production layout section), `series/ep1-…/PLAN.md`,
`series/ep1-…/PODCAST-PLAN.md`, `series/ep2-…/PLAN.md`, `docs/API-CLI.md` — repoint the
script/source/output paths listed above. (These are text-only edits; I'll grep-verify
zero stale paths after.)

## Housekeeping

- delete `out/podcast/podcast_die-frau-vor-dem-recht-v2.mp3` (stray earlier render)
- delete `scripts/__pycache__/`
- fold away the `part1-germanucus` typo (its files move into `series/ep1-…/studie/`)

## Risks & rollback

- **Not a git repo** → no undo net. Before executing I'll write a `restore-map.sh`
  (reverse `mv`s) and/or tar `scripts/ *.md series/ part*/` so the move is reversible.
- `mise.toml`/`.env` untouched → no `mise trust` re-run needed.
- `CLAUDE.md → AGENTS.md` symlink stays valid (both remain at root).
- After the move I verify with: `parse` on both podcast scripts + one `mix` per scene
  (free) + a grep for any surviving old path string.

## Execution order (once you OK)

1. Backup / write reverse-map.
2. `mkdir` target dirs; move sources, studies, docs, plans.
3. Rename + edit scripts (paths, slugs) and the small `hoerspiel.py` `source_md` change.
4. Move output dirs; free `mix book` re-emit; delete old-named finals + stray `-v2`.
5. Update doc cross-references; grep-verify no stale paths.
6. Smoke test: `ep1_podcast.py parse`, `ep2_podcast.py parse`, one scene `mix`.

---
**Open choices for you:** (a) keep flat output dirs `out/ep1-scene1/` (proposed, minimal
code) vs. nested `out/ep1/scene1/` (needs a ~5-line engine change to split dir from
basename); (b) keep `PLAN.md`+`PODCAST-PLAN.md` separate per episode, or merge into one
`PLAN.md` per episode; (c) rename dir label `series/` vs `episodes/` vs `content/`.
