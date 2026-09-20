"""Rebuild the two AP50:95 bubble figures from the frozen plotting data.

Usage: python source/build_bubble_figures.py
Requires Python 3.10+ and matplotlib. No model execution or network access.
The CSV files are convenient extracts; bubble_plot_data.json is authoritative.
All circles use s = AREA_SCALE * GFLOPs, with no offset or nonlinear scaling.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import sys
local_deps=Path(__file__).resolve().parents[1]/'qa/drawing_dependencies'
if local_deps.exists():sys.path.insert(0,str(local_deps))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import MultipleLocator, FormatStrFormatter

ROOT = Path(__file__).resolve().parents[1]
DATA = Path(__file__).with_name("bubble_plot_data.json")
ASSETS = ROOT / "assets"
QA = ROOT / "qa" / "bubble_figures"
AREA_SCALE = 3.5  # points squared per GFLOP, identical for points and area legends
COLORS = {"bdnet": "#6E8CA7", "fgh": "#73938B", "host": "#90969B", "internal": "#7691A1", "full": "#B64335"}
TEXT = "#242A30"
MUTED = "#5A626B"

matplotlib.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.labelsize": 11,
    "xtick.labelsize": 9.5,
    "ytick.labelsize": 9.5,
    "axes.edgecolor": "#59636D",
    "axes.linewidth": 0.7,
    "text.color": TEXT,
    "axes.labelcolor": TEXT,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "svg.fonttype": "none",
    "svg.hashsalt": "cvm-bubbles-20260917",
    "savefig.facecolor": "white",
})


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canvas(xlim, ylim, xstep, ystep=2):
    fig = plt.figure(figsize=(7.2, 4.75), facecolor="white")
    ax = fig.add_axes([0.105, 0.205, 0.86, 0.725])
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_xlabel("Parameters (M)", labelpad=8)
    ax.set_ylabel("VisDrone AP (%)", labelpad=8)
    ax.xaxis.set_major_locator(MultipleLocator(xstep))
    ax.yaxis.set_major_locator(MultipleLocator(ystep))
    ax.grid(True, color="#E5E9EC", linewidth=0.6)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(length=3.5, width=0.7)
    return fig, ax


def draw_bubble(ax, row, color, full=False):
    return ax.scatter(
        [row["parameters_m"]], [row["ap50_95_percent"]],
        s=[AREA_SCALE * row["gflops_per_image"]], marker="o",
        facecolor=color, edgecolor=color if full else "white",
        linewidth=1.15 if full else 0.7, alpha=0.90 if full else 0.80,
        zorder=5 if full else 3, clip_on=True,
    )


def label(ax, row, text, offset, align="left", full=False, leader=False):
    arrow = {"arrowstyle": "-", "color": "#9AA3AB", "lw": 0.65,
             "shrinkA": 3, "shrinkB": 11} if leader else None
    return ax.annotate(
        text, (row["parameters_m"], row["ap50_95_percent"]),
        xytext=offset, textcoords="offset points", ha=align, va="center",
        fontsize=10.5 if full else 10, fontweight="bold" if full else "normal",
        color=COLORS["full"] if full else TEXT, arrowprops=arrow,
        annotation_clip=False, zorder=7,
    )


def size_legend(ax, values, location, ncol=3):
    handles = [ax.scatter([], [], s=AREA_SCALE * v, marker="o", facecolor="none",
                          edgecolor="#7D868E", linewidth=0.8) for v in values]
    leg = ax.legend(handles, [str(v) for v in values], title="GFLOPs / image",
                    bbox_to_anchor=location, loc="center", ncol=ncol,
                    frameon=False, labelspacing=1.5, columnspacing=1.2,
                    handletextpad=0.9, borderpad=0.4, fontsize=9,
                    title_fontsize=9.5, scatterpoints=1)
    ax.add_artist(leg)


def export(fig, stem, rows, labels):
    ASSETS.mkdir(parents=True, exist_ok=True)
    QA.mkdir(parents=True, exist_ok=True)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    label_boxes = {name: list(obj.get_window_extent(renderer).bounds)
                   for name, obj in labels.items()}
    for ext in ("png", "pdf", "svg"):
        options = {"dpi": 360} if ext == "png" else {}
        metadata = ({"CreationDate": None, "ModDate": None} if ext == "pdf"
                    else {"Date": None} if ext == "svg" else None)
        fig.savefig(ASSETS / f"{stem}.{ext}", metadata=metadata, **options)
    fig.savefig(QA / f"{stem}_preview.png", dpi=180)
    points = [{"id": r["id"], "parameters_m": r["parameters_m"],
               "ap50_95_percent": r["ap50_95_percent"], "gflops_per_image": r["gflops_per_image"],
               "scatter_s_points_squared": AREA_SCALE * r["gflops_per_image"]}
              for r in rows]
    plt.close(fig)
    return {"points": points, "label_boxes_at_100_dpi": label_boxes,
            "outputs": {ext: {"path": str(ASSETS / f"{stem}.{ext}"),
                              "sha256": sha(ASSETS / f"{stem}.{ext}")}
                        for ext in ("png", "pdf", "svg")}}


def comparison(data):
    rows = data["external_context"]["points"]
    byid = {r["id"]: r for r in rows}
    fig, ax = canvas((0, 50), (20.5, 34.0), 10)
    for r in sorted(rows, key=lambda p: p["gflops_per_image"], reverse=True):
        color = COLORS["full" if r["id"] == "ours_full" else "host" if r["id"] == "ours_host" else r["source_id"]]
        draw_bubble(ax, r, color, full=r["id"] == "ours_full")
    config = {
        "bdnet": ("BDNet", (14, 0), "left", False),
        "fghdet": ("FGHDet", (0, 26), "center", False),
        "yolo11_bd": ("YOLO11", (-16, -5), "right", False),
        "yolo12_bd": ("YOLO12", (-13, 21), "right", True),
        "yolo26_bd": ("YOLO26", (-3, -27), "center", True),
        "yolov7_fgh": ("YOLOv7", (15, -9), "left", False),
        "ours_host": ("RT-DETR-L (our host)", (-16, 14), "right", False),
        "ours_full": ("Ours (Full)", (17, 13), "left", False),
    }
    labels = {key: label(ax, byid[key], text, offset, align, key == "ours_full", leader)
              for key, (text, offset, align, leader) in config.items()}
    size_legend(ax, [50, 125, 250], (0.215, 0.30))
    sources = [Line2D([], [], linestyle="none", marker="o", markersize=7,
                      markerfacecolor=COLORS[key], markeredgecolor="white", label=title)
               for key, title in (("bdnet", "Reported by BDNet"), ("fgh", "Reported by FGHDet"))]
    fig.legend(handles=sources, loc="center", bbox_to_anchor=(0.54, 0.086),
               ncol=2, frameon=False, fontsize=9, handletextpad=0.45, columnspacing=2.4)
    fig.text(0.535, 0.025,
             "640 × 640; AP = AP50:95. Reported protocols differ.",
             ha="center", va="bottom", color=MUTED, fontsize=8.7)
    return export(fig, "bubble_comparison", rows, labels)


def internal(data):
    rows = data["internal_native_validation"]["points"]
    byid = {r["id"]: r for r in rows}
    fig, ax = canvas((32.1, 36.2), (20.5, 32.1), 1)
    ax.xaxis.set_major_formatter(FormatStrFormatter("%.0f"))
    for r in sorted(rows, key=lambda p: p["gflops_per_image"], reverse=True):
        color = COLORS["full" if r["id"] == "full" else "host" if r["id"] == "host" else "internal"]
        draw_bubble(ax, r, color, full=r["id"] == "full")
    config = {
        "host": ("RT-DETR-L (host)", (14, -5), "left", False),
        "g": ("GCDL", (-23, 19), "right", True),
        "gf": ("GCDL + F", (1, 37), "center", True),
        "gb": ("GCDL + B", (-4, -26), "center", True),
        "full": ("Ours (Full)", (16, 15), "left", False),
    }
    labels = {key: label(ax, byid[key], text, offset, align, key == "full", leader)
              for key, (text, offset, align, leader) in config.items()}
    size_legend(ax, [100, 120, 140], (0.28, 0.40))
    fig.text(0.535, 0.083, "Five configurations under the native validation protocol",
             ha="center", va="center", color=MUTED, fontsize=9)
    fig.text(0.535, 0.025,
             "640 × 640; AP = AP50:95. Validation-selected checkpoints after 100 epochs.",
             ha="center", va="bottom", color=MUTED, fontsize=8.7)
    return export(fig, "bubble_internal", rows, labels)


def write_csv(data):
    fields = ["id", "display_label", "parameters_m", "ap50_95_percent", "ap50_percent",
              "gflops_per_image", "source_id", "source_label_verbatim", "origin",
              "accuracy_split", "input_hw", "epochs", "pretraining", "notes"]
    for group, name in (("external_context", "bubble_comparison_data.csv"),
                        ("internal_native_validation", "bubble_internal_data.csv")):
        with (DATA.parent / name).open("w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            for row in data[group]["points"]:
                writer.writerow({**row, "input_hw": "x".join(map(str, row["input_hw"]))})


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    write_csv(data)
    result = {"input_json_sha256": sha(DATA), "matplotlib_version": matplotlib.__version__,
              "axis_metric": "AP50:95", "bubble_scaling": "s = 3.5 * GFLOPs, identical circular markers",
              "external": comparison(data), "internal": internal(data)}
    (QA / "build_manifest.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("Created bubble_comparison and bubble_internal in PNG, PDF and SVG.")


if __name__ == "__main__":
    main()
