# Dependencies

## Compile the delivered paper

Only main.tex and a standard pdfLaTeX installation are needed. Three official CVM style files, four lossless RGB image streams and the bibliography are embedded. No external image, BibTeX, shell escape, Python or network access is required. Compile three times for references and page backreferences.

Standard packages: fontenc, times, graphicx, amsmath, amssymb, booktabs, array, balance, xcolor, tikz and hyperref. The official styles remain unchanged. Compiler validation is recorded in verification.json.

## Optional author editing

- Reassemble main.tex: Python 3 + Pillow; run python build.py. This uses the current delivered PNG files.
- Independent verification: Python 3 + Pillow + pypdf and pdfLaTeX; run python verify.py.
- Statistical plots: use their supplied SVG/PDF sources or matplotlib builders. Their data are retained.
- Current architecture: raster PNG, 1448x1086, edited with the built-in imagegen tool. There is no vector source for this version. The prompts are supplied in figure_revision. The old architecture builder and vector files are archived separately and must not be used to regenerate the current architecture.
- Package reviewed outputs: python package_approved_release.py. It requires completed visual QA in verification.json and verifies archive extraction and source assembly.

Neural-model execution is not needed to rebuild the manuscript. Source paths in evidence records are provenance, not paper-compilation dependencies.
