"""Plot several point sets and a path over a calibrated PNG."""
from pathlib import Path

import pandas as pd

from imageplot import ImagePlot

ROOT = Path(__file__).resolve().parents[1]
image_path = ROOT / "examples" / "pallet.png"
output_path = ROOT / "output" / "pallet_points.png"
excel_path = ROOT / "examples" / "pallet_points.xlsx"

plot = ImagePlot(image_path, coordinate_system="PalletFrame")

df = pd.read_excel(excel_path, engine="openpyxl")

for x_col in df.columns:
    if not x_col.endswith("X (mm)"):
        continue

    y_col = x_col.replace("X (mm)", "Y (mm)")
    if y_col not in df.columns:
        continue

    x_values = df[x_col].tolist()
    y_values = df[y_col].tolist()
    points = list(zip(x_values, y_values))
    label = x_col.removesuffix(" X (mm)") or "points"
    plot.scatter(points, label=label, s=12, alpha=0.5)

plot.legend()
plot.show()
