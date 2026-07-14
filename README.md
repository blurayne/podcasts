# Audio Production Pipeline

AI-driven production pipeline for German podcast and radio-play (Hörspiel) series. A single YAML-driven engine turns human-readable Markdown scripts into fully mixed episodes using ElevenLabs (TTS, SFX, music) and ffmpeg, and the companion study PDFs are typeset with XeTeX/tectonic.

Most episodes were researched and written by **Fable** (a Claude model); it occasionally reverted to the **Opus** model where the work touched sensitive areas — for example the physics research on atoms, or the World War II context in Episode 3 of Homo ante legem.

🌐 **Live site:** <https://blurayne.github.io/podcasts/>

☕ **Support:** if you enjoy these productions, you can [buy me a coffee](https://buymeacoffee.com/blackrain).

## How it works

Every episode is produced by one generic engine, `scripts/produce.py`, driven by a per-episode **YAML spec** (production config: voices, model, SFX/music prompts, cue rules, gaps, output) plus a **Markdown transcript** (the dialogue). The full schema, engine CLI, and credit-safe rules are the authoritative contract in [`SPEC.md`](SPEC.md); the reusable operator guide is the skill at `.claude/skills/produce-podcast-episode/`.

```bash
scripts/produce.py <spec.yaml> parse   # print the parsed event list (no API calls, free)
scripts/produce.py <spec.yaml> gen     # generate TTS + SFX + music stems (spends credits, idempotent)
scripts/produce.py <spec.yaml> mix     # ffmpeg assembly → final MP3 (free, re-runnable)
scripts/produce.py <spec.yaml> all     # gen + mix (+ book for Hörspiele)
```

Scripts run via a uv shebang (`#!/usr/bin/env -S uv run --script`) with PEP 723 inline dependencies — no virtualenv setup needed.

## Series

### Homo ante legem — Der Mensch vor dem Recht (S01)

> **Homo ante legem**
> *Der Mensch vor dem Recht*
> Leitformel: **Status sequitur functionem** — Rechtsstellung folgt Funktionsstellung.

Historical documentary podcast + Hörspiel series on the legal status of persons — women *and* men — across cultures and centuries, each episode paired with a peer-reviewed-style study PDF (the „Bände", Observatory layout). *(Formerly „Die Frau vor dem Recht"; renamed as the series broadened from the woman to the person before the law.)*

> **Kurzbefund**

> Die Reihe lässt sich **keinem Lager** zuordnen — sie ist eine **bewusste Triangulation**: ein *links-materialistischer Erklärungsapparat*, ein *klassisch-liberaler normativer Fluchtpunkt* und eine *ungewöhnlich faire, aber entwaffnende Aufnahme rechter/biologischer Argumente*. Der Schwerpunkt liegt auf einem **materialistisch fundierten Links-Liberalismus mit heterodox-zentristischer Streitkultur**, der sich programmatisch vom „woke"-Register absetzt, ohne dessen strukturanalytischen Gehalt aufzugeben. Am nächsten steht das einem **heterodoxen Zentrum** im Sinne von Nancy Fraser, Martha Nussbaum und Richard Reeves — nicht der Identitätslinken, nicht der Männerrechts-/traditionalistischen Rechten.
> 
> In Folge 8 erfindet die Reihe schließlich eine eigene „Disziplin" — die **Funktionskritik** —, als „zweites Auge" *komplementär* zum intersektionalen Feminismus, das dessen „Leerstelle" beim Mann kritisiert, aber ausdrücklich „kein Anti-Feminismus" sein will.
> 
> In Folge 12 (*Der Gegenanwalt*) begibt sich die Funktionskritik selbst auf die Anklagebank — sie stellt sich der gleichen Kritik, die sie an anderen übt.



| # | Folder slug | Topic | Spielzeit | Anhören |
|---|---|---|---|---|
| S01-01 | `germanen-europa` | Germanen bis Europa (3 Hörspiele + podcast) — produced | 25:20 | [▶ Drive](https://drive.google.com/file/d/1rYvdheXtUlleIMsMta8CpAT0NwFDKE5b/view) |
| S01-02 | `islam-der-parallelbogen` | Der Parallelbogen / Islam (5 Hörspiele + podcast) — produced | 33:42 | [▶ Drive](https://drive.google.com/file/d/1DK7IcAhanl94FHPUS0fu-nH5Hyb4qG4J/view) |
| S01-03 | `judentum-gesetz-ohne-land` | Judentum — Gesetz ohne Land | 36:16 | [▶ Drive](https://drive.google.com/file/d/1_5xDFSyINZBLzH3zmct2iDujp-yh7yLA/view) |
| S01-04 | `matriarchat-gegentest` | Matriarchat-Gegentest | 32:27 | [▶ Drive](https://drive.google.com/file/d/1_tDH7gjKYU4T6AGbfe2HuRbR6W_kNXCp/view) |
| S01-05 | `koda-woher-die-funktion` | Koda — Woher die Funktion | 11:18 | [▶ Drive](https://drive.google.com/file/d/1j6WdHgbkrjuEvASiQ0hdN0x9LrRv20Xh/view) |
| S01-06 | `der-mann-unter-dem-patriarchat` | Der Mann unter dem Patriarchat | 23:53 | [▶ Drive](https://drive.google.com/file/d/1ZmlXKOFlvuBdipUBp-DUtEXD1bz8WJCt/view) |
| S01-07 | `der-markt-der-begehrten` | Der Markt der Begehrten (Band VII) | 41:11 | [▶ Drive](https://drive.google.com/file/d/1RV4Q97f1Qs4ne03Pb6Rpy1h33f9B9YnO/view) |
| S01-08 | `die-funktionskritik` | Die Funktionskritik (Band VIII) — produced | 19:56 | [▶ Drive](https://drive.google.com/file/d/1sfBrmA9ck_Y2r4DyloBZbtb0M-6Jp5ah/view) |
| S01-09 | `die-wanderung-der-funktion` | Die Wanderung der Funktion (Doppelfolge, Band IX) | 25:32 | [▶ Drive](https://drive.google.com/file/d/1swFqQ_5ON3zkryfpyGGnD9l7tusHFEtg/view) |
| S01-10 | `die-entkopplung` | Die Entkopplung (Finale, Band X) — produced | 32:18 | [▶ Drive](https://drive.google.com/file/d/12xt_dVdxCGbG80GAGlrKIB4kQxSf0rP7/view) |

Podcast continuity: STIMME 1 = Mila Winter, STIMME 2 = Wolf Spencer.

### Science for Kids

Kids' science podcast. Ep. 1 *„Kleiner geht's nicht"* — a journey from cells to quarks (produced). *Wusl Gusl — Schrumpfomat 3002* — a manic character-driven version of the same physics (inspired by "Woozle Goozle"; v3 spec in `series/science-for-kids/wusl-gusl.yaml`). The Wusl Gusl audio is produced; its [Drive link](https://drive.google.com/file/d/1BQpkJJqdM1kaLwVEAlpzdLfNnHRWT3d5/view) still needs to be shared publicly by the author before it plays.

## Study PDFs

Each Band is a LaTeX study compiled with the shared "Observatory" layout (fonts, colours, confidence chips, box types). Toolchain and template are documented in [`LAYOUT-STUDIES.md`](LAYOUT-STUDIES.md); compile with `tectonic` (or system `xelatex`).

## Repository layout

```
series/<show>/<episode>/   — sources: transcript .md, *.yaml specs, studie/ (LaTeX + PDF)
out/<show>/<slug>/         — generated stems + final mixes (git-ignored; reproducible from specs)
audio/                     — MP3s published by the GitHub Pages site
scripts/                   — produce.py (engine), el.py (ElevenLabs CLI/lib), hoerspiel.py (Hörspiel lib)
docs/                      — API-CLI, research, templates
index.html + .github/workflows/pages.yml — the GitHub Pages site (pandoc build)
SPEC.md, LAYOUT-STUDIES.md, AGENTS.md      — engine spec, study-build spec, standing conventions
```

Per-episode output: `podcast.mp3` (feature), and for Hörspiele `sceneN.mp3` (full play), `sceneN_play.mp3` (drama-only stem embedded in the podcast), `sceneN_audiobook.mp3` (clean read).

## Setup

```bash
mise install                       # uv, ffmpeg, jq, curl, tectonic (studies)
set -a; source ./.env; set +a      # load ELEVENLABS_API_KEY (never commit .env)
python3 scripts/el.py balance      # check the shared credit pool
```

ffmpeg: the mise-managed binary may be broken; the engine auto-picks a working `ffmpeg`/`ffprobe` (`$FFMPEG_BIN` → PATH → `/usr/bin/ffmpeg`).

## Conventions

Standing project conventions (voice policy, caching/credit discipline, uv shebangs, etc.) live in [`AGENTS.md`](AGENTS.md) (`CLAUDE.md` is a symlink to it). Key rules: cast only studio-quality voices, always pass `skip_existing` so re-runs never re-spend credits, and confirm the estimated cost (credits + USD) before any `gen`.

## License

Code (pipeline, site) is **GPL-3.0-or-later**; creative works (transcripts, studies, produced audio) are **CC BY-SA 4.0**. The full outline — including the ElevenLabs commercial-use terms the audio is produced under and what that means for publishing (e.g. on YouTube) — is in [`LICENSE.md`](LICENSE.md).
