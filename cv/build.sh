#!/bin/sh
# Build the four CVs with XeLaTeX and collect them in ./pdf
set -e
cd "$(dirname "$0")"
mkdir -p build pdf
for v in hwsw-en hwsw-fr sw-en sw-fr fpga-en fpga-fr; do
  latexmk -outdir=build "cv-$v.tex"
done
cp build/cv-hwsw-en.pdf pdf/CV_MamboMotsou_Embedded-SW-HW-Engineer_EN.pdf
cp build/cv-hwsw-fr.pdf pdf/CV_MamboMotsou_Ingenieur-Logiciel-Materiel-Embarque_FR.pdf
cp build/cv-sw-en.pdf   pdf/CV_MamboMotsou_Embedded-Software-Engineer_EN.pdf
cp build/cv-sw-fr.pdf   pdf/CV_MamboMotsou_Ingenieur-Logiciel-Embarque_FR.pdf
cp build/cv-fpga-en.pdf pdf/CV_MamboMotsou_FPGA-SoC-Engineer_EN.pdf
cp build/cv-fpga-fr.pdf pdf/CV_MamboMotsou_Ingenieur-FPGA-SoC_FR.pdf
# keep the website's downloadable copies in sync
if [ -d ../assets/cv ]; then cp pdf/*.pdf ../assets/cv/ && echo "Copied to ../assets/cv (website)"; fi
echo "PDFs written to $(pwd)/pdf"
