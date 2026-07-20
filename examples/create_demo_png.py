"""Create a self-contained calibrated demo PNG for the example scripts."""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, PngImagePlugin

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"
OUTPUT.mkdir(exist_ok=True)
path = ROOT / "examples" / "demo_fixture.png"

image = Image.new("RGB", (900, 600), "#e6e8eb")
draw = ImageDraw.Draw(image)
draw.rectangle((80, 70, 820, 530), fill="#c9cdd2", outline="#32363a", width=5)
draw.rectangle((210, 155, 690, 445), fill="#aeb4ba", outline="#42474c", width=4)
for x, y in [(160, 135), (740, 135), (160, 465), (740, 465)]:
    draw.ellipse((x - 34, y - 34, x + 34, y + 34), fill="#555b61", outline="#202326", width=4)

# A deliberately rotated and mildly skewed coordinate system.
payload = {
    "schema": "png-coordinate-systems",
    "version": 1,
    "image": {
        "width": image.width,
        "height": image.height,
        "pixel_origin": "top-left",
        "pixel_x_direction": "right",
        "pixel_y_direction": "down",
    },
    "coordinate_systems": [
        {
            "name": "Fixture",
            "origin": {"pixel_x": 160, "pixel_y": 465, "world_x": 0.0, "world_y": 0.0},
            "x_point": {"pixel_x": 740, "pixel_y": 430, "world_x": 290.0, "world_y": 0.0},
            "y_point": {"pixel_x": 185, "pixel_y": 135, "world_x": 0.0, "world_y": 165.0},
        }
    ],
}
metadata = PngImagePlugin.PngInfo()
metadata.add_itxt("coordinate_systems_json", json.dumps(payload))
image.save(path, pnginfo=metadata)
print(path)
