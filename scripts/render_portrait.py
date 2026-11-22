#!/usr/bin/env python3
"""Turn the supplied illustration into the reference layout's ASCII portrait."""
from html import escape
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps

ROOT = Path(__file__).resolve().parent.parent
COLS, ROWS = 180, 96
RAMP = " .`:-=+*cs#%@"


def render():
    image = Image.open(ROOT / "assets/profile.png").convert("L")
    image = ImageOps.autocontrast(image, cutoff=1)
    image = ImageEnhance.Contrast(image).enhance(1.05)
    image = image.resize((COLS, ROWS), Image.Resampling.LANCZOS)
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 840 850" '
        'role="img" aria-label="ASCII portrait of Aruneshwaran K">',
        '<title>Aruneshwaran K — portrait from the supplied illustration</title>',
        '<g font-family="monospace" font-size="7.2" fill="#111111">',
    ]
    for y in range(ROWS):
        chars = []
        for x in range(COLS):
            luminance = (image.getpixel((x, y)) / 255) ** 1.18
            index = round((1 - luminance) * (len(RAMP) - 1))
            chars.append(" " if luminance >= 0.80 else RAMP[index])
        parts.append(
            f'<text xml:space="preserve" x="20" y="{43.2 + y * 800 / ROWS:.1f}" '
            f'textLength="800" lengthAdjust="spacing">{escape("".join(chars))}</text>'
        )
    parts.append("</g></svg>")
    (ROOT / "assets/portrait-ascii.svg").write_text("".join(parts))
    print("wrote assets/portrait-ascii.svg")


if __name__ == "__main__":
    render()
