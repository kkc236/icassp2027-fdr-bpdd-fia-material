"""Pure drawing/format QA. All data are SYNTHETIC; never paper evidence."""
from pathlib import Path
from types import SimpleNamespace
import hashlib
import importlib.util
import json
import subprocess
import tempfile

import pypdfium2 as pdfium
from pypdf import PdfReader
from PIL import Image, ImageDraw

import prepare_qualitative as prep

ROOT = Path(__file__).resolve().parent
embed_path = next(path for path in (ROOT / "embed_raster.py", ROOT.parent / "source/qualitative/embed_raster.py") if path.exists())
spec = importlib.util.spec_from_file_location("standalone_raster", embed_path)
embed_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(embed_module)
embedded_raster_tex = embed_module.embedded_raster_tex
QA = ROOT / "synthetic_qa_NOT_PAPER_EVIDENCE"
QA.mkdir(exist_ok=True)


def dump(path, data):
    path.write_text(json.dumps(data), encoding="utf-8")


def must_fail(fn, expected):
    try:
        fn()
    except (ValueError, KeyError) as exc:
        assert expected in str(exc), (expected, str(exc))
    else:
        raise AssertionError(f"Expected failure: {expected}")


images_dir = QA / "synthetic_images"
raw_dir = QA / "synthetic_raw"
images_dir.mkdir(exist_ok=True)
raw_dir.mkdir(exist_ok=True)
image = Image.new("RGB", (200, 100), "#eeeeee")
ImageDraw.Draw(image).text((4, 40), "SYNTHETIC QA ONLY", fill="black")
image.save(images_dir / "SYNTHETIC.png")
gt = {"images": [{"id": 0, "file_name": "SYNTHETIC.png", "width": 200, "height": 100}],
      "categories": [{"id": i, "name": name, "supercategory": "object"} for i, name in enumerate(prep.CLASSES)],
      "annotations": [{"id": i, "image_id": 0, "category_id": 0, "bbox": b, "iscrowd": 0}
                      for i, b in enumerate(([10, 10, 30, 30], [100, 10, 30, 30], [170, 50, 20, 20]))]}
gt_path = QA / "SYNTHETIC_instances.json"
dump(gt_path, gt)
manifest_path = QA / "SYNTHETIC_image_manifest.json"
dump(manifest_path, [{"file_name": "SYNTHETIC.png", "sha256": prep.sha(images_dir / "SYNTHETIC.png")}])
def det(box, score, category=0):
    return {"bbox_xyxy": box, "score": score, "category_id": category}
row = {"image_id": "SYNTHETIC", "width": 200, "height": 100, "detections": [
    det([10, 10, 40, 40], .9), det([10, 10, 40, 40], .8), # Duplicate must be FP.
    det([100, 10, 130, 40], .7, 1), # Wrong class must be FP + missed GT.
    det([170, 50, 190, 70], .25, 0.0), # Inclusive threshold and normalized integer category.
    det([100, 10, 130, 40], .249), # Below threshold must disappear.
]}
for name in ("dfine_final_val.jsonl", "joint_final_val.jsonl"):
    dump(raw_dir / name, row)
args = SimpleNamespace(gt=gt_path, raw_dir=raw_dir, images=images_dir, image_manifest=manifest_path,
                       output=QA / "rendered_synthetic", selection=QA / "SYNTHETIC_selection.json")
# The QA fixture declares its own test hashes in memory. Production EXPECTED remains unchanged on disk.
prep.EXPECTED = {"instances_val.json": prep.sha(gt_path), **{n: prep.sha(raw_dir / n) for n in ("dfine_final_val.jsonl", "joint_final_val.jsonl")}}
data = prep.load_data(args)
matched = prep.match(data[1]["SYNTHETIC"], data[2]["SYNTHETIC"]["detections"])
assert (matched["tp"], matched["fp"], matched["fn"]) == (2, 2, 1)
visible = prep.crop_diagnostics(data[1]["SYNTHETIC"], matched, [90, 0, 150, 60])
assert visible["visible_missed_gt_indices"] == [1]
assert visible["visible_unmatched_predictions"] == 1
assert visible["visible_matched_predictions"] == 0
dump(args.selection, {"examples": []})
must_fail(lambda: prep.render(args, data), "at least one")
dump(args.selection, {"examples": [{"image_id": "SYNTHETIC", "crop_xyxy": [0.5, 0, 200, 100]}]})
must_fail(lambda: prep.render(args, data), "integer pixel")
dump(args.selection, {"examples": [{"image_id": "SYNTHETIC", "crop_xyxy": [5, 0, 199, 85], "label": "SYNTHETIC QA - NOT RESEARCH EVIDENCE"}]})
prep.render(args, data)
render_manifest = json.loads((args.output / "render_manifest.json").read_text())
assert render_manifest["examples"][0]["displayed_dfine"]["matching_scope"].startswith("whole image")
image.putpixel((0, 0), (1, 2, 3))
image.save(images_dir / "SYNTHETIC.png")
must_fail(lambda: prep.load_data(args), "content hash mismatch")

# A standalone two-image TeX compile tests XObject resource isolation and strip order.
test_image = Image.new("RGB", (256, 192), "white")
d = ImageDraw.Draw(test_image)
for box, color in [((0, 0, 127, 95), "red"), ((128, 0, 255, 95), "green"),
                   ((0, 96, 127, 191), "blue"), ((128, 96, 255, 191), "yellow")]:
    d.rectangle(box, fill=color)
definition, provenance = embedded_raster_tex(test_image, "SyntheticFirst")
assert provenance["strip_count"] >= 2
alpha = Image.new("RGBA", (64, 32), (0, 0, 255, 128))
definition_two, provenance_two = embedded_raster_tex(alpha, "SyntheticSecond")
tex = (r"\documentclass{article}" "\n"
       r"\usepackage[paperwidth=400bp,paperheight=350bp,margin=20bp]{geometry}" "\n"
       r"\usepackage{graphicx}" "\n" + definition + definition_two + "\n" +
       r"\begin{document}\pagestyle{empty}\noindent\ShowSyntheticFirst{256bp}\par\noindent\ShowSyntheticSecond{64bp}\end{document}")
tex_path = QA / "SYNTHETIC_inline_raster.tex"
tex_path.write_text(tex, encoding="ascii")
import os
import shutil
pdflatex = os.environ.get("PDFLATEX") or shutil.which("pdflatex") or "C:/Users/16946/AppData/Local/Programs/MiKTeX/miktex/bin/x64/pdflatex.exe"
result = subprocess.run([str(pdflatex), "-no-shell-escape", "-interaction=nonstopmode", "-halt-on-error", tex_path.name], cwd=QA, capture_output=True, text=True)
assert result.returncode == 0, result.stdout[-4000:]
pdf = pdfium.PdfDocument(str(tex_path.with_suffix(".pdf")))
assert len(pdf) == 1
page = pdf[0]
page_image = page.render(scale=1).to_pil().convert("RGB")
page_image.save(QA / "SYNTHETIC_inline_raster_render.png")
reader = PdfReader(tex_path.with_suffix(".pdf"))
assert len(reader.pages[0].images) == provenance["strip_count"] + provenance_two["strip_count"]
alpha_object = next(item.image for item in reader.pages[0].images if item.image.size == (64, 32))
assert alpha_object.convert("RGB").getpixel((10, 10)) == (127, 127, 255)
red_pixels = [(x, y) for y in range(page_image.height) for x in range(page_image.width) if page_image.getpixel((x, y)) == (255, 0, 0)]
first_left = min(x for x, y in red_pixels)
first_top = min(y for x, y in red_pixels)
for x, y, expected in [(25, 25, (255, 0, 0)), (200, 25, (0, 128, 0)),
                       (25, 150, (0, 0, 255)), (200, 150, (255, 255, 0))]:
    got = page_image.getpixel((round(first_left + x), round(first_top + y)))
    assert got == expected, (x, y, got, expected)
_, jpeg_info = embedded_raster_tex(test_image, "SyntheticJpeg", encoding="jpeg", jpeg_quality=70)
assert jpeg_info["rgb_sha256"] != jpeg_info["input_rgb_sha256"]
assert jpeg_info["lossless"] is False
dump(QA / "SYNTHETIC_QA_REPORT.json", {
    "notice": "SYNTHETIC DRAWING/FORMAT QA ONLY. No model inference, no genuine prediction examples.",
    "checks": ["duplicate detection one-to-one matching", "class mismatch", "inclusive score boundary", "float category normalization",
               "crop-visible unmatched objects", "empty selection refusal", "fractional crop refusal", "image tamper refusal",
               "render manifest scope", "standalone no-shell-escape compile", "multiple raster resource isolation",
               "exact RGB quadrant positions across strips", "RGBA compositing on white", "JPEG source versus decoded pixel hash"],
    "raster": provenance, "alpha_raster": provenance_two, "jpeg": jpeg_info,
    "status": "passed"})
print("SYNTHETIC QA passed; no genuine prediction validation was performed.")
