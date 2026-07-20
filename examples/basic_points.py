"""Plot several point sets and a path over a calibrated PNG."""
from pathlib import Path
import numpy as np

from imageplot import ImagePlot

ROOT = Path(__file__).resolve().parents[1]
image_path = ROOT / "examples" / "demo_fixture.png"
output_path = ROOT / "output" / "basic_points.png"

rng = np.random.default_rng(7)
measured = rng.normal(loc=(145, 82), scale=(16, 9), size=(80, 2))
rejected = np.array([[105, 45], [195, 117], [208, 61]])
path = np.array([[35, 40], [90, 65], [145, 82], [220, 125]])

plot = ImagePlot(image_path, coordinate_system="Fixture", figsize=(11, 7))
plot.scatter(measured, s=22, alpha=0.75, label="Measured")
plot.scatter(rejected, s=70, marker="x", linewidths=2, label="Rejected")
plot.plot(path, linewidth=2, marker="o", label="Programmed path")
plot.ax.set_title("Fixture measurement overlay")
plot.legend()
plot.save(output_path)
print(output_path)
