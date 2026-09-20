#!/bin/sh
set -eu
cd -- "$(dirname -- "$0")"
for pass in 1 2 3; do
  pdflatex -interaction=nonstopmode -halt-on-error -file-line-error -no-shell-escape main.tex
done
cp main.pdf MANUSCRIPT_CVM.pdf
