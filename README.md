# Image Data Overlay Tool

A Matplotlib-first Python library for plotting engineering data over PNG images created with the PNG Coordinate System Metadata Editor.

The library reads the embedded `coordinate_systems_json` iTXt chunk, constructs the full pixel-to-world affine transform, and places the image in world-coordinate space. Your points and shapes can then be plotted with ordinary Matplotlib calls.

## Install

From this directory:

```powershell
python -m pip install -e .
```

## Basic use

```python
from imageplot import ImagePlot

plot = ImagePlot("fixture.png", coordinate_system="Fixture")
plot.scatter([(10, 15), (12, 18), (14, 17)], label="Measured")
plot.plot([(0, 0), (25, 10)], label="Path")
plot.legend()
plot.show()
```

The underlying objects remain normal Matplotlib objects:

```python
plot.ax.grid(True)
plot.ax.set_title("Inspection results")
plot.figure.tight_layout()
```

## Shape clouds

```python
plot.circles(centers, radii=2.5, alpha=0.08)
plot.ellipses(centers, widths, heights, angles)
plot.rectangles(centers, widths, heights, angles)
plot.polygons(list_of_vertex_arrays, alpha=0.1)
```

These methods use Matplotlib patch collections and are suitable for large Monte Carlo populations.

## Coordinate conversions

```python
pixels = plot.world_to_pixel(world_points)
world = plot.pixel_to_world(pixel_points)

matrix = plot.coordinate_system.pixel_to_world_matrix
print(plot.coordinate_system.handedness)
```

## Included examples

Run these from the project directory:

```powershell
python examples/create_demo_png.py
python examples/basic_points.py
python examples/monte_carlo_shapes.py
```

Generated images are written to `output/`.
