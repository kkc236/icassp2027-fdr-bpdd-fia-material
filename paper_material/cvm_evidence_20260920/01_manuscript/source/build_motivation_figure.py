"""Rebuild the two-panel motivation figure from packaged validation GT.

Run from any directory with Python 3 (standard library only):
    python path/to/source/build_motivation_figure.py
Use --check to verify that both generated outputs are current without writing.
All source/output paths are relative to this packaged project, not the cwd.
"""

import argparse
import bisect
import gzip
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path("qualitative/gt_reconstructed/instances_val.json.gz")
GZIP_SHA256 = "7959b5a87cfed051303d9234ca192a2ecd61be2e5691187533cfcc90af614abd"
JSON_SHA256 = "92d2866fe6e6ff4c3101b82c01b7718eb78b3759399042c4501d893798fc8bfa"
EXPECTED_COUNTS = [6856, 14011, 12414, 4580, 898]
BIN_EDGES = [0, 8, 16, 32, 64, None]
BIN_LABELS = ["[0,8)", "[8,16)", "[16,32)", "[32,64)", "[64,infinity)"]


def profile():
    compressed = (ROOT / SOURCE).read_bytes()
    payload = gzip.decompress(compressed)
    source_hash = hashlib.sha256(compressed).hexdigest()
    json_hash = hashlib.sha256(payload).hexdigest()
    if (source_hash, json_hash) != (GZIP_SHA256, JSON_SHA256):
        raise ValueError("Packaged validation GT differs from the frozen source.")
    data = json.loads(payload)
    images = {image["id"]: image for image in data["images"]}
    annotations = data["annotations"]
    if len(images) != 548 or len(images) != len(data["images"]):
        raise ValueError("Expected 548 unique validation image records.")
    if len(annotations) != 38759:
        raise ValueError("Expected 38,759 packaged validation boxes.")
    counts = [0] * 5
    for annotation in annotations:
        image = images[annotation["image_id"]]
        width, height = annotation["bbox"][2:]
        values = [width, height, image["width"], image["height"]]
        if not all(math.isfinite(value) and value > 0 for value in values):
            raise ValueError("All image/box extents must be positive and finite.")
        # Reproduce the detector's independent horizontal and vertical stretch.
        width_input = width * 640 / image["width"]
        height_input = height * 640 / image["height"]
        size = math.sqrt(width_input * height_input)
        # bisect_right assigns boundary values to the next half-open bin.
        counts[bisect.bisect_right(BIN_EDGES[1:-1], size)] += 1
    if counts != EXPECTED_COUNTS:
        raise ValueError("Computed bin counts differ from the frozen profile.")
    total = sum(counts)
    bins = [
        {
            "lower_inclusive_px": BIN_EDGES[index],
            "upper_exclusive_px": BIN_EDGES[index + 1],
            "label": BIN_LABELS[index],
            "count": count,
            "fraction": count / total,
            "percentage": 100 * count / total,
            "display_percentage": f"{100 * count / total:.1f}",
        }
        for index, count in enumerate(counts)
    ]
    displacement = [step / 20 for step in range(81)]
    curves = [
        {
            "box_width_px": width,
            "samples": [
                {"displacement_px": delta, "iou": (width - delta) / (width + delta)}
                for delta in displacement
            ],
            "iou_at_one_px": (width - 1) / (width + 1),
        }
        for width in [8, 16, 32]
    ]
    return {
        "schema_version": 1,
        "source": {
            "relative_path": SOURCE.as_posix(),
            "gzip_sha256": source_hash,
            "uncompressed_json_sha256": json_hash,
            "image_count": len(images),
            "annotation_count": len(annotations),
            "population": "All boxes in the packaged reconstructed validation GT; no additional filtering.",
        },
        "input_scale_profile": {
            "input_width_px": 640,
            "input_height_px": 640,
            "resize": "Independent-axis stretch; not aspect-ratio-preserving letterbox.",
            "equivalent_side_formula": "sqrt((bbox_width * 640 / image_width) * (bbox_height * 640 / image_height))",
            "interval_convention": "Half-open bins [lower, upper); null upper bound means infinity.",
            "bins": bins,
            "below_32_px_count": sum(counts[:3]),
            "below_32_px_fraction": sum(counts[:3]) / total,
            "below_32_px_percentage": 100 * sum(counts[:3]) / total,
            "display_below_32_px_percentage": f"{100 * sum(counts[:3]) / total:.1f}",
            "metric_boundary": "These input-scale bins differ from AP_s, which uses COCO area ranges in original-image coordinates.",
        },
        "analytic_iou": {
            "assumptions": "Two equal-size axis-aligned boxes, equal vertical position, horizontal displacement d in [0,4], widths w in {8,16,32} pixels; d < w.",
            "formula": "IoU = (w - d) / (w + d)",
            "interpretation": "Analytic geometry illustration, not measured model localization error or a model result.",
            "curves": curves,
        },
        "figure": {
            "relative_path": "figures/motivation.tikz",
            "label": "fig:motivation",
            "drawing_width_cm": 16.8,
            "drawing_height_cm": 5.0,
            "caption_outside_drawing": True,
            "dependencies": "Existing TikZ and xcolor only; no pgfplots.",
        },
    }


def render_tikz(data):
    stats = data["input_scale_profile"]
    lines = [
        r"% Generated by source/build_motivation_figure.py; do not edit by hand.",
        r"\begin{figure*}[t]",
        r"\centering",
        r"\begin{tikzpicture}[x=1cm,y=1cm,font=\sffamily\footnotesize]",
        r"\definecolor{motink}{HTML}{22364A}",
        r"\definecolor{motblue}{HTML}{236B9C}",
        r"\definecolor{motorange}{HTML}{A76115}",
        r"\path[use as bounding box] (0,0) rectangle (16.8,5.0);",
        r"\node[anchor=west,font=\sffamily\bfseries\small,text=motink] at (.04,4.76) {(a) Object scales at the detector input};",
        r"\node[anchor=west,font=\sffamily\scriptsize,text=motink!85] at (.04,4.34) {548 validation images; 38,759 ground-truth boxes};",
        r"\node[anchor=west,font=\sffamily\bfseries\small,text=motink] at (8.70,4.76) {(b) IoU sensitivity to a horizontal shift};",
        r"\draw[motink!18,line width=.45pt] (8.40,.18) -- (8.40,4.85);",
    ]
    # Panel (a): five equal-width bins, with a zero-based percentage axis.
    x_start, x_end, y_start, y_end = 0.90, 8.00, 1.04, 3.88
    y_scale = (y_end - y_start) / 40
    for tick in [0, 10, 20, 30, 40]:
        y = y_start + tick * y_scale
        lines += [
            f"\\draw[motink!12,line width=.4pt] ({x_start:.2f},{y:.3f}) -- ({x_end:.2f},{y:.3f});",
            f"\\node[anchor=east,font=\\sffamily\\scriptsize,text=motink!80] at (.78,{y:.3f}) {{{tick}}};",
        ]
    lines += [
        r"\node[rotate=90,font=\sffamily\scriptsize,text=motink] at (.17,2.46) {Ground-truth boxes (\%)};",
        r"\draw[motink!55,line width=.5pt] (.90,1.04) -- (8.00,1.04);",
    ]
    bin_tex = [r"$[0,8)$", r"$[8,16)$", r"$[16,32)$", r"$[32,64)$", r"$[64,\infty)$"]
    for index, row in enumerate(stats["bins"]):
        x = 1.64 + index * 1.38
        top = y_start + row["percentage"] * y_scale
        color = ["motblue!60", "motblue!80", "motblue", "motink!40", "motink!27"][index]
        lines += [
            f"\\fill[{color}] ({x - .43:.3f},{y_start:.3f}) rectangle ({x + .43:.3f},{top:.4f});",
            f"\\node[anchor=south,font=\\sffamily\\bfseries\\scriptsize,text=motink] at ({x:.3f},{top + .06:.4f}) {{{row['display_percentage']}\\%}};",
            f"\\node[anchor=north,font=\\sffamily\\scriptsize,text=motink] at ({x:.3f},.92) {{{bin_tex[index]}}};",
        ]
    lines += [
        f"\\node[align=center,font=\\sffamily\\bfseries\\scriptsize,text=motblue] at (6.65,3.48) {{{stats['display_below_32_px_percentage']}\\% have\\\\$s<32$ pixels}};",
        r"\node[font=\sffamily\scriptsize,text=motink] at (4.45,.28) {Equivalent side $s=\sqrt{w_{\rm in}h_{\rm in}}$ (pixels)};",
    ]
    # Panel (b): native line segments sample the analytic equation every .05 px.
    x_start, x_end, y_start, y_end = 9.43, 16.50, 1.04, 3.88

    def xy(delta, iou):
        return x_start + delta * (x_end - x_start) / 4, y_start + iou * (y_end - y_start)

    for tick in [0, .25, .5, .75, 1]:
        y = xy(0, tick)[1]
        label = "0" if tick == 0 else f"{tick:.2f}"
        lines += [
            f"\\draw[motink!12,line width=.4pt] ({x_start:.3f},{y:.3f}) -- ({x_end:.3f},{y:.3f});",
            f"\\node[anchor=east,font=\\sffamily\\scriptsize,text=motink!80] at (9.31,{y:.3f}) {{{label}}};",
        ]
    lines += [
        r"\node[rotate=90,font=\sffamily\scriptsize,text=motink] at (8.59,2.46) {IoU};",
        r"\draw[motink!55,line width=.5pt] (9.43,1.04) -- (16.50,1.04);",
        r"\node[font=\sffamily\scriptsize,text=motink] at (12.97,.28) {Horizontal displacement $d$ (pixels)};",
    ]
    for tick in range(5):
        x, _ = xy(tick, 0)
        lines += [
            f"\\draw[motink!55,line width=.45pt] ({x:.3f},1.04) -- ({x:.3f},.96);",
            f"\\node[anchor=north,font=\\sffamily\\scriptsize,text=motink] at ({x:.3f},.92) {{{tick}}};",
        ]
    one_px = xy(1, 0)[0]
    lines.append(f"\\draw[motink!40,densely dotted,line width=.6pt] ({one_px:.4f},1.04) -- ({one_px:.4f},3.88);")
    curve_styles = [("motorange", ""), ("motblue", ",dashed"), ("motink", "")]
    for index, curve in enumerate(data["analytic_iou"]["curves"]):
        color, dash = curve_styles[index]
        coords = [xy(point["displacement_px"], point["iou"]) for point in curve["samples"]]
        path = " -- ".join(f"({x:.4f},{y:.4f})" for x, y in coords)
        lines.append(f"\\draw[{color},line width=1.05pt{dash}] {path};")
        legend_x = 9.00 + index * 2.52
        lines += [
            f"\\draw[{color},line width=1.05pt{dash}] ({legend_x:.3f},4.30) -- ({legend_x + .47:.3f},4.30);",
            f"\\node[anchor=west,font=\\sffamily\\scriptsize,text=motink] at ({legend_x + .55:.3f},4.30) {{$w={curve['box_width_px']}$ px}};",
        ]
        if curve["box_width_px"] in [8, 32]:
            x, y = xy(1, curve["iou_at_one_px"])
            lines.append(f"\\fill[{color}] ({x:.4f},{y:.4f}) circle[radius=.045];")
            if curve["box_width_px"] == 8:
                lines.append(f"\\node[anchor=north east,font=\\sffamily\\bfseries\\scriptsize,text={color},fill=white,inner sep=1pt] at ({x - .10:.4f},{y - .04:.4f}) {{0.778}};")
            else:
                lines.append(f"\\node[anchor=south west,font=\\sffamily\\bfseries\\scriptsize,text={color},fill=white,inner sep=1pt] at ({x + .10:.4f},{y + .04:.4f}) {{0.939}};")
    lines += [
        r"\end{tikzpicture}",
        r"\caption{Task scale and analytic localization sensitivity. (a) All converted-label VisDrone validation ground truth (548 images, 38,759 boxes), after the independent-axis resizing to $640\times640$ used by the common evaluator. The equivalent side is $s=\sqrt{w_{\rm in}h_{\rm in}}$; all five bins and their rounded proportions are shown. These input-scale bins differ from the original-image COCO area ranges used for $\mathrm{AP}_{s}$. (b) For equal-size axis-aligned boxes with unchanged vertical position, a horizontal shift gives $\mathrm{IoU}=(w-d)/(w+d)$ for $0\leq d<w$. A one-pixel shift yields 0.778 for $w=8$ and 0.939 for $w=32$. This is an analytic geometry illustration, not a measurement of model localization errors.}",
        r"\label{fig:motivation}",
        r"\end{figure*}",
    ]
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify generated files without writing")
    args = parser.parse_args()
    data = profile()
    outputs = {
        ROOT / "inputs/motivation_profile.json": json.dumps(data, indent=2, ensure_ascii=True, allow_nan=False) + "\n",
        ROOT / "figures/motivation.tikz": render_tikz(data),
    }
    for path, text in outputs.items():
        encoded = text.encode("ascii")
        if args.check:
            if not path.is_file() or path.read_bytes() != encoded:
                raise ValueError(f"Generated output is missing or stale: {path.relative_to(ROOT)}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(encoded)
    print(json.dumps({
        "mode": "check" if args.check else "write",
        "images": data["source"]["image_count"],
        "boxes": data["source"]["annotation_count"],
        "bin_counts": [row["count"] for row in data["input_scale_profile"]["bins"]],
        "below_32_px_percent": data["input_scale_profile"]["display_below_32_px_percentage"],
        "drawing_cm": [16.8, 5.0],
        "outputs": [path.relative_to(ROOT).as_posix() for path in outputs],
    }))


if __name__ == "__main__":
    main()
