"""Create the default Mouse Mover icon."""

from __future__ import annotations

import os

from PIL import Image, ImageDraw

APP_ICON_FILE = "icon.ico"


def make_icon_image() -> Image.Image:
    size = 256
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((24, 16, 232, 240), fill=(37, 99, 235), outline=(30, 64, 175), width=12)
    draw.line((128, 40, 128, 136), fill=(255, 255, 255), width=12)
    draw.ellipse((104, 144, 152, 192), fill=(255, 255, 255))
    return img


def main() -> int:
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), APP_ICON_FILE)
    if not os.path.exists(icon_path):
        make_icon_image().save(
            icon_path,
            format="ICO",
            sizes=((16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)),
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
