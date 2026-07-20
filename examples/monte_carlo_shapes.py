"""Visualize a Monte Carlo population of rotated rectangular parts."""
from pathlib import Path
import numpy as np

from imageplot import ImagePlot

ROOT = Path(__file__).resolve().parents[1]
image_path = ROOT / "examples" / "demo_fixture.png"
output_path = ROOT / "output" / "monte_carlo_shapes.png"

rng = np.random.default_rng(42)
count = 750
centers = rng.normal(loc=(145, 82), scale=(8, 5), size=(count, 2))
angles = rng.normal(loc=0.0, scale=2.0, size=count)

plot = ImagePlot(image_path, coordinate_system="Fixture", figsize=(11, 7), image_alpha=0.9)
plot.rectangles(
    centers,
    widths=48,
    heights=24,
    angles=angles,
    facecolor="none",
    edgecolor="tab:blue",
    linewidth=0.35,
    alpha=0.08,
)
plot.scatter(centers, s=3, alpha=0.15, label="Simulated centers")
plot.ax.set_title("Monte Carlo placement population")
plot.legend()
plot.save(output_path)
print(output_path)
