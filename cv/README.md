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
cvstyle.sty        layout: two columns, colours, sidebar and entry macros, variant switch
en/blocks.tex      every CV block in English (written once)
fr/blocks.tex      the same blocks in French
cv-*-*.tex         the six main files: pick blocks and their order
latexmkrc          tells latexmk / Overleaf to use XeLaTeX
build.sh           builds all six PDFs into ./pdf (and copies them to ../assets/cv)
```

Page layout: a tinted sidebar on the left (name, headline, focus chips, contact, languages, skills,
certification) and a main column (summary, experience, projects, education) with dates in a narrow
left column. Typeface: Latin Modern Roman (the fontspec default, with optical sizes); icons from
`fontawesome5`. Both ship with TeX Live and Overleaf, so no font files are bundled.

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
- **Sidebar macros** (in `cvstyle.sty`; the sidebar comes first, `\mainpart` switches to the main column):
  - `\BlkHeader{Headline}{\focus{..}\focus{..}}` — name, headline, focus chips and contact (in `blocks.tex`)
  - `\cvlang{Language}{level 0–5, halves allowed}{detail}` — a language with its dot rating
  - `\cvskill{Group}{\chip{..}\chip[(detail)]{..}}` — a skill group; the optional detail prints in regular weight
  - `\cvcert{text}` — a certification line
- **Main-column macros:**
  - `\cvsection{\faBuilding}{Title}` — a section heading with an icon (`\faCode`, `\faGraduationCap`, ...)
  - `\cventry{Role}{Organisation}{Location}{Dates}` — a job
  - `\cvsub{Title}` — a project inside a job
  - `\cvproject{Title}{Context}{Dates}{github.com/owner/repo or empty}`
  - `\cvenv{Environment:}{\chip{..}\chip{..}}` — the technical environment as a row of chips
  - `\cvedu{Degree}{School}{Place}{Dates}`, `\cvgroup{Label}`, `\cvsummary{text}`
- Keep each CV at two pages: after editing, check the page count (`pdfinfo pdf/<file>.pdf`).

## ATS notes

Real selectable text, no text in images. The two-column layout means some applicant-tracking systems
read the sidebar and the main column interleaved; for a portal that parses CVs badly, paste the text
into its form fields. I²C is written with the Unicode superscript so it extracts as one word.
Check with `pdftotext pdf/<file>.pdf -`.
