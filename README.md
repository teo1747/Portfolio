# Portfolio — Junior Deogracias Mambo Motsou

Bilingual (English / French) portfolio site and the LaTeX sources of my CVs.

**Live site:** https://teo1747.github.io/Portfolio/ (French: `/fr/`)

## What's here

```
content/          all site text, one TOML file per section (bilingual)
  profile.toml      name, hero, about, facts, education, CV list
  experience.toml   jobs; items link to project cards (#p-<id>)
  projects.toml     project cards: problem, contribution, environment, outcome
  skills.toml       skills table
  ui.toml           interface strings (buttons, labels, categories)
assets/           style.css, site.js, fonts, favicon, cv/ (downloadable PDFs)
build.py          static site generator (Python 3.11+, standard library only)
diagrams.py       technical diagrams drawn as inline SVG
404.html          not-found page
cv/               LaTeX sources of the four CVs (see cv/README.md)
.github/workflows/pages.yml   builds and publishes the site on every push to main
```

## Edit the site

1. Change text in `content/*.toml`. Each field is either one string (same in both languages) or
   `{ en = "...", fr = "..." }`. Long text uses `field.en = """ ... """` and `field.fr = """ ... """`.
   Inline markup: `**bold**`, `` `code` ``, `[link text](https://...)`.
2. Preview locally:
   ```sh
   python3 build.py --serve     # http://localhost:8000  (French at /fr/)
   ```
3. Commit and push to `main`. The workflow rebuilds and deploys in about a minute.

**Add a project:** copy a `[[project]]` block in `content/projects.toml`, give it a unique `id`, a
`category` (`professional`, `academic` or `personal`), `domains` from `ui.toml [domains]`, and `env` rows
using the keys in `ui.toml [env]`. Order in the file is the order on the page.

**Project images:** each project can have one visual.
- `image = "therm.jpg"` uses a file in `assets/img/projects/` (keep it under about 1,280 px wide). Clicking it opens it full size.
  Add `image_fit = "contain"` for screenshots that must not be cropped.
- `image = "diagram:tcu"` draws one of the technical diagrams in `diagrams.py` (inline SVG, follows light and dark mode).
  To add a diagram, write a function there and register it in `DIAGRAMS`.
- `image_alt` describes the picture for screen readers; `image_caption` is shown under it.
- `featured = true` puts the project first, as a wide card.

**Portrait:** replace `assets/img/portrait.jpg` (4:5, about 640 × 800 px).

## Update the CVs

```sh
cd cv && ./build.sh     # needs XeLaTeX + latexmk; copies the PDFs into assets/cv/
```

Or edit on Overleaf (instructions in `cv/README.md`), download the PDFs, and put them in `assets/cv/`
with the same file names. Then commit and push.

## First-time GitHub Pages setup

In the repository: **Settings → Pages → Build and deployment → Source: GitHub Actions**.
After that, every push to `main` publishes the site.

## Design notes

- Fonts: Archivo and JetBrains Mono, self-hosted (SIL Open Font License, see `assets/fonts/`).
  No external requests, no cookies, no analytics.
- Light and dark themes follow the visitor's system setting. Motion is limited to the hero waveform
  drawing in once, and is disabled when the visitor prefers reduced motion.
- The page works without JavaScript; the script only adds the project filters.

## Licence

Code (`build.py`, `assets/site.js`, `assets/style.css`, CV class files): MIT.
Text, CV content and personal information: © Junior Deogracias Mambo Motsou, all rights reserved.
