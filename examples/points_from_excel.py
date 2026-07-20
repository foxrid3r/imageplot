"""Plot several point sets and a path over a calibrated PNG."""
from pathlib import Path
import numpy as np
import pandas as pd

from imageplot import ImagePlot

ROOT = Path(__file__).resolve().parents[1]
image_path = ROOT / "examples" / "pallet.png"
output_path = ROOT / "output" / "pallet_points.png"
excel_path = ROOT / "examples" / "pallet_points.xlsx"

plot = ImagePlot(image_path, coordinate_system="PalletFrame")

df = pd.read_excel(excel_path)

for col in df.columns:
    if col.endswith("X (mm)"):
        y_col = col.replace("X (mm)", "Y (mm)")

        if y_col in df.columns:
            plot.scatter(
                df[[col, y_col]].to_numpy(),
                label=col[:-7],      # Remove " X (mm)"
                s=12,
                alpha=0.5
            )

plot.legend()
plot.show()
