"""Inline an RGB raster in an ASCII-only pdfLaTeX source, without shell escape.

The image is a PDF image XObject; a form XObject supplies local resources.
JPEG input may be preserved byte-for-byte, or a Pillow image encoded losslessly.
Only graphicx and pdfTeX primitives are required in the generated document.
"""
from __future__ import annotations

from io import BytesIO
import hashlib
import re
import zlib
from PIL import Image


def embedded_raster_tex(image: Image.Image | bytes, name: str, *, encoding: str = "flate", jpeg_quality: int = 95) -> tuple[str, dict]:
    """Return ``(ASCII TeX definition, provenance)``.

    In the preamble, include ``\\usepackage{graphicx}`` and this definition.
    In the body use ``\\ShowNAME{\\linewidth}``, replacing NAME by ``name``.
    ``encoding='jpeg'`` preserves supplied RGB JPEG bytes verbatim; otherwise
    it converts the Pillow image to RGB and encodes it at the specified quality.
    ``encoding='flate'`` preserves every decoded RGB pixel losslessly.

    The name must contain only ASCII letters. Transparent inputs are composited
    on white. TeX's object-stream compression is disabled locally because this
    image dictionary already declares its decoding filters.
    """
    if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z]+", name):
        raise ValueError("name must contain only ASCII letters")
    input_bytes = image if isinstance(image, bytes) else None
    original = Image.open(BytesIO(image)) if input_bytes is not None else image
    original.load()
    if original.mode in ("RGBA", "LA") or "transparency" in original.info:
        rgba = original.convert("RGBA")
        im = Image.new("RGB", rgba.size, "white")
        im.paste(rgba, mask=rgba.getchannel("A"))
    else:
        im = original.convert("RGB")
    width, height = im.size
    if min(width, height) < 1 or max(width, height) > 16000:
        raise ValueError("Image dimensions must each be in [1, 16000] pixels for TeX box dimensions")
    if encoding == "flate":
        # Keep each TeX argument small even for incompressible photographs.
        # Each strip contains at most ~64 KiB of uncompressed RGB pixels.
        strip_height = max(1, 65536 // (width * 3))
        parts = []
        for top in range(0, height, strip_height):
            bottom = min(top + strip_height, height)
            payload = zlib.compress(im.crop((0, top, width, bottom)).tobytes(), level=9)
            parts.append((top, bottom - top, payload))
        filter_name = "FlateDecode"
    elif encoding == "jpeg":
        if not isinstance(jpeg_quality, int) or isinstance(jpeg_quality, bool) or not 1 <= jpeg_quality <= 100:
            raise ValueError("jpeg_quality must be an integer in [1, 100]")
        if input_bytes is not None and original.format == "JPEG" and original.mode == "RGB":
            payload = input_bytes
        else:
            buf = BytesIO()
            im.save(buf, format="JPEG", quality=jpeg_quality, subsampling=0)
            payload = buf.getvalue()
        if len(payload) > 700000:
            raise ValueError("Large JPEG exceeds conservative TeX token budget; use encoding='flate'")
        parts = [(0, height, payload)]
        filter_name = "DCTDecode"
    else:
        raise ValueError("encoding must be 'flate' or 'jpeg'")
    definitions = []
    resources = []
    instructions = []
    for index, (top, part_height, payload) in enumerate(parts):
        encoded = payload.hex().upper()
        hexlines = "\n".join(encoded[i:i+120] for i in range(0, len(encoded), 120))
        definitions.append(rf"""\immediate\pdfobj stream attr{{/Type /XObject /Subtype /Image
/Width {width} /Height {part_height} /ColorSpace /DeviceRGB /BitsPerComponent 8
/Interpolate false /Filter [/ASCIIHexDecode /{filter_name}]}}{{
{hexlines}>
}}
\expandafter\edef\csname InlineImageObject{index}\endcsname{{\the\pdflastobj}}
""")
        resources.append(rf"/InlineRaster{index} \csname InlineImageObject{index}\endcsname\space 0 R")
        instructions.append(rf"q {width} 0 0 {part_height} 0 {height-top-part_height} cm /InlineRaster{index} Do Q")
    tex = rf"""% Embedded raster {name}: {width} x {height} RGB pixels; {filter_name}.
\begingroup
\pdfcompresslevel=0
{''.join(definitions)}%
\setbox0=\hbox to {width}bp{{\vrule width0pt height{height}bp depth0pt
\pdfliteral{{{' '.join(instructions)}}}\hss}}
\immediate\pdfxform resources{{/XObject << {' '.join(resources)} >>}} 0
\expandafter\xdef\csname InlineForm{name}\endcsname{{\the\pdflastxform}}
\endgroup
\expandafter\newcommand\csname Show{name}\endcsname[1]{{%
  \resizebox{{#1}}{{!}}{{\pdfrefxform\csname InlineForm{name}\endcsname}}}}
"""
    tex.encode("ascii")
    decoded = Image.open(BytesIO(parts[0][2])).convert("RGB") if encoding == "jpeg" else im
    return tex, {
        "name": name,
        "width": width,
        "height": height,
        "encoding": encoding,
        "rgb_sha256": hashlib.sha256(decoded.tobytes()).hexdigest(),
        "input_rgb_sha256": hashlib.sha256(im.tobytes()).hexdigest(),
        "payload_sha256": [hashlib.sha256(part[2]).hexdigest() for part in parts],
        "payload_bytes": sum(len(part[2]) for part in parts),
        "strip_count": len(parts),
        "tex_bytes": len(tex.encode("ascii")),
        "lossless": encoding == "flate",
    }


if __name__ == "__main__":
    import json
    from pathlib import Path
    from PIL import ImageDraw
    root = Path(__file__).resolve().parent
    sample = Image.new("RGB", (400, 200), "white")
    draw = ImageDraw.Draw(sample)
    for bounds, color in [((0,0,199,99),"red"), ((200,0,399,99),"green"), ((0,100,199,199),"blue"), ((200,100,399,199),"yellow")]:
        draw.rectangle(bounds, fill=color)
    draw.rectangle((10,10,30,30), fill="white")
    draw.rectangle((370,170,390,190), fill="black")
    tex, info = embedded_raster_tex(sample, "Demo")
    doc = r"\documentclass{article}" + "\n" + r"\usepackage[paperwidth=500bp,paperheight=400bp,margin=50bp]{geometry}" + "\n" + r"\usepackage{graphicx}" + "\n" + tex + "\n" + r"\begin{document}\pagestyle{empty}\noindent\ShowDemo{400bp}\end{document}" + "\n"
    (root / "proof.tex").write_text(doc, encoding="ascii")
    sample.save(root / "sample.png")
    (root / "provenance.json").write_text(json.dumps(info, indent=2), encoding="utf-8")
