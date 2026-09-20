# Rebuilding the bubble figures

Run `python source/build_bubble_figures.py` from this package (Python 3.10+, matplotlib). The script resolves paths relative to itself and uses no network or model runtime.

- `bubble_plot_data.json`: complete plotting data and source provenance; both CSVs are regenerated from it.
- `bubble_comparison_data.csv`: eight points, six reported by two external papers and two archived native runs.
- `bubble_internal_data.csv`: five archived native-validation configurations, an alternative figure rather than an external comparison.
- `bubble_captions.tex`: suggested caption text, not inserted into the manuscript automatically.
- Output: `assets/bubble_comparison.{png,pdf,svg}` and `assets/bubble_internal.{png,pdf,svg}`.
- `qa/bubble_figures/build_manifest.json`: source hash, point coordinates/areas, label bounds, export hashes.

The y axis is AP over IoU 0.50:0.95, never AP50. Circular marker areas and area-legend circles use the same linear multiplier `s = 3.5 * GFLOPs`. PDF embeds TrueType fonts; SVG retains text; PNG uses 360 dpi. The external graph does not imply matched training or evaluation protocols. The original BDNet table prints three YOLO variants with an uppercase `-I`; short graph labels therefore omit that suffix, while JSON/CSV retain it verbatim.
