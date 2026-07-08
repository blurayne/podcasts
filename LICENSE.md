# Licenses

Copyright © 2026 blurayne

This repository mixes **software** (the production pipeline) and **creative
works** (scripts, transcripts, studies, produced audio). One license cannot
sensibly cover both: the GNU GPL is a *software* license — its core mechanism
("you must ship the corresponding source code") maps poorly onto prose and
audio, and the FSF itself recommends against using the GPL for non-software
works. So the repository is licensed per component, using GPLv3 for everything
that is software and the closest copyleft equivalent — **CC BY-SA 4.0** — for
everything that isn't. CC BY-SA 4.0 is the license Creative Commons and the
FSF declared **one-way compatible with GPLv3**, so the two halves of the repo
can even be combined into a GPLv3 whole if anyone ever needs to.

## Overview

| Component | Paths | License |
|---|---|---|
| Production pipeline & tooling | `scripts/`, `.github/`, `.claude/`, `mise.toml`, `.gitattributes` | [GPL-3.0-or-later](LICENSES/GPL-3.0.txt) |
| Website | `index.html` | [GPL-3.0-or-later](LICENSES/GPL-3.0.txt) |
| Episode sources (transcripts, plans, YAML specs) | `series/` | [CC BY-SA 4.0](LICENSES/CC-BY-SA-4.0.txt) |
| Study volumes („Bände", LaTeX sources + PDFs) | `series/**/studie/` | [CC BY-SA 4.0](LICENSES/CC-BY-SA-4.0.txt) |
| Produced audio published by the site | `audio/` | [CC BY-SA 4.0](LICENSES/CC-BY-SA-4.0.txt) — see [AI-generated audio](#ai-generated-audio-elevenlabs) below |
| Documentation | `README.md`, `SPEC.md`, `LAYOUT-STUDIES.md`, `AGENTS.md`, `VOICES.md`, `GDRIVE.md`, `NEXT.md`, `docs/` | [CC BY-SA 4.0](LICENSES/CC-BY-SA-4.0.txt) |

Full license texts live in [`LICENSES/`](LICENSES/):

- [`LICENSES/GPL-3.0.txt`](LICENSES/GPL-3.0.txt) — GNU General Public License v3.0 (or, at your option, any later version)
- [`LICENSES/CC-BY-SA-4.0.txt`](LICENSES/CC-BY-SA-4.0.txt) — Creative Commons Attribution-ShareAlike 4.0 International

Attribution for CC BY-SA material: **"blurayne — <https://github.com/blurayne/podcasts>"**.

## AI-generated audio (ElevenLabs)

All voices, sound effects and music in the produced episodes are generated
with [ElevenLabs](https://elevenlabs.io) (TTS, SFX and Music APIs) under a
**paid subscription (Creator plan)**. Under the ElevenLabs Terms of Service,
output generated during a paid subscription comes with a **commercial-use
license**; ownership of the output, to the extent permitted by law, is
assigned to the subscriber. On that basis the produced audio in `audio/` is
released under CC BY-SA 4.0 to the full extent of the rights we hold.

Caveats that CC BY-SA cannot waive, because they come from elsewhere:

- **ElevenLabs prohibited uses** still bind everyone: the audio may not be
  used to train or seed voice-cloning / speech-synthesis models, to
  impersonate real persons, or for fraud or deception.
- **Voice Library voices** (the cast is studio-quality `professional`
  voices from the ElevenLabs Voice Library) are licensed through ElevenLabs'
  revenue-share program; the license covers the *generated audio*, not the
  voice itself — nobody may extract or re-synthesize the voices.
- In some jurisdictions purely AI-generated works enjoy **limited or no
  copyright protection**; where that is the case, the CC license simply has
  nothing to attach to and the material is effectively free there anyway.

## Third-party material

- **Fonts** — the study PDFs embed subsets of
  [Space Grotesk](https://github.com/floriankarsten/space-grotesk) and
  [IBM Plex Mono](https://github.com/IBM/plex), both under the
  [SIL Open Font License 1.1](https://openfontlicense.org), which expressly
  permits embedding in documents. The font files themselves are **not**
  distributed in this repository (they are fetched into a local, untracked
  `fonts/` folder at build time; see `LAYOUT-STUDIES.md`).
- **Deliberately excluded from the repository** (git-ignored, never
  distributed): downloaded voice-actor demo reels (`sprachproben/`), the
  reference transcript of the original „Woozle Goozle" show
  (`series/science-for-kids/woozle-orig.txt`), and the intro jingle
  (`series/science-for-kids/wusl-gusl-intro.mp3`). These are
  copyright-sensitive reference materials and are **not** covered by any
  license in this file.
- **Trademarks** — „Woozle Goozle" is a third-party trademark; the kids' show
  in this repository was renamed **Wusl Gusl** for that reason. Nothing in
  this file grants trademark rights of any kind.

## Publishing the produced episodes (e.g. YouTube)

The *Homo ante legem / Die Frau vor dem Recht* series is original writing
voiced entirely with ElevenLabs-generated speech, SFX and music produced
under a paid plan — there is no third-party recorded music or audio in it.
Publishing it on YouTube (including monetized) is permitted, provided:

1. the ElevenLabs subscription was active (paid tier) when the audio was
   generated — true for this project (Creator plan);
2. the ElevenLabs prohibited-use policy is respected (no impersonation,
   deception, etc. — a documentary podcast is fine);
3. YouTube's disclosure rules for **altered or synthetic content** are
   followed: tick the "altered/synthetic content" disclosure when uploading,
   since the voices are realistic AI speech.

Crediting „Audio generated with ElevenLabs" in the video description is not
required on paid plans but is good practice.
