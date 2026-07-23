"""Plot several point sets and a path over a calibrated PNG."""
from pathlib import Path

import pandas as pd

from imageplot import ImagePlot

ROOT = Path(__file__).resolve().parents[1]
block_path = ROOT / "examples" / "block-with-holes.png"
block_rotated_path = ROOT / "examples" / "block-with-holes-rotated.png"
coord_sys_name = "Datum1"

image_path = block_path
excel_path = ROOT / "examples" / "block_points.xlsx"

# Load the Excel file
df = pd.read_excel(excel_path, engine="openpyxl")

x_col = "X (mm)"
y_col = "Y (mm)"

# Remove rows where either coordinate is missing.
df = df.dropna(subset=[x_col, y_col])

# Convert the columns to numeric arrays.
x_data = pd.to_numeric(df[x_col], errors="raise").to_numpy()
y_data = pd.to_numeric(df[y_col], errors="raise").to_numpy()

plot = ImagePlot(image_path, coordinate_system=coord_sys_name)

plot.ax.scatter(
    x_data,
    y_data,
    s=24,
    alpha=0.8,
    label="Points",
)

plot.legend()
plot.show()
