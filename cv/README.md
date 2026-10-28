# CV sources — Junior Deogracias Mambo Motsou

Six CVs built from one set of content blocks:

| File | Role | Language |
|---|---|---|
| `cv-hwsw-en.tex` | Embedded Software & Hardware Engineer | English |
| `cv-hwsw-fr.tex` | Ingénieur logiciel et matériel embarqué | Français |
| `cv-sw-en.tex` | Embedded Software Engineer | English |
| `cv-sw-fr.tex` | Ingénieur logiciel embarqué | Français |
| `cv-fpga-en.tex` | FPGA & SoC Engineer | English |
| `cv-fpga-fr.tex` | Ingénieur FPGA & SoC | Français |

## Layout

```
cvstyle.sty        layout: fonts, colours, section/entry macros, variant switch
en/blocks.tex      every CV block in English (written once)
fr/blocks.tex      the same blocks in French
cv-*-*.tex         the six main files: pick blocks and their order
fonts/             Archivo static instances (SIL Open Font License, see fonts/OFL.txt)
latexmkrc          tells latexmk / Overleaf to use XeLaTeX
build.sh           builds all six PDFs into ./pdf (and copies them to ../assets/cv)
```

## Compile

**Overleaf:** upload the whole folder (zip it, then *New Project → Upload Project*).
`latexmkrc` selects XeLaTeX automatically; if not, set *Menu → Compiler → XeLaTeX*.
Choose which CV to build with *Menu → Main document*.

**Locally** (TeX Live with XeLaTeX and latexmk):

```sh
./build.sh                 # all six → pdf/
latexmk cv-sw-en.tex       # just one
```

## Editing

- **Change a fact once, in both languages:** edit the block in `en/blocks.tex` and the block with the
  same name in `fr/blocks.tex`. Every CV that uses it updates.
- **Change which projects a CV shows, or their order:** edit the list between `\begin{document}` and
  `\end{document}` in that `cv-*.tex` file.
- **Text that only some variants should show:** `\HW{...}` appears in the Software & Hardware and the
  FPGA/SoC CVs, `\SW{...}` only in the Software CV, `\FP{...}` only in the FPGA/SoC CV, `\NF{...}` in
  every CV except FPGA/SoC. Whole bullets work too: `\HW{\item ...}`.
- **Dates, phone, availability:** `\forviadates`, `\phone`, `\availability`, `\iucplace`, `\iucdates`
  are defined near the top of each `blocks.tex`.
- **Entry macros** (in `cvstyle.sty`):
  - `\cventry{Role}{Organisation}{Location}{Dates}` — a job
  - `\cvsub{Title}` — a project inside a job
  - `\cvproject{Title}{Context}{Dates}{github.com/owner/repo or empty}`
  - `\cvenv{Environment:}{tools...}` — the technical-environment line
  - `\cvskill{Label}{content}` — a skills row
- Keep each CV at two pages: after editing, check the page count (`pdfinfo pdf/<file>.pdf`).

## ATS notes

Single column, real selectable text, no icons or text in images. The font's contextual alternates are
switched off (`RawFeature={-calt}`) so that copied text keeps `C++`, `x86-64`, `J-Link` intact, and I²C
is written with the Unicode superscript so it extracts as one word. Check with `pdftotext pdf/<file>.pdf -`.
