# Image Data Overlay Tool

A Matplotlib-first Python library for plotting engineering data over PNG images using full 2D affine coordinate systems.

Coordinate systems can be loaded from the PNG Coordinate System Metadata Editor or created programmatically.

## Install

```powershell
python -m pip install -e .
```

## Use embedded PNG metadata

```python
from imageplot import ImagePlot

plot = ImagePlot("fixture.png", coordinate_system="Fixture")
plot.scatter([(10, 15), (12, 18), (14, 17)], label="Measured")
plot.legend()
plot.show()
```

## Create a coordinate system programmatically

```python
from imageplot import CoordinateSystem, ImagePlot

fixture = CoordinateSystem.from_points(
    name="Fixture",
    origin_pixel=(1250, 820),
    origin_world=(0.0, 0.0),
    x_point_pixel=(1750, 850),
    x_point_world=(100.0, 0.0),
    y_point_pixel=(1220, 320),
    y_point_world=(0.0, 100.0),
)

# The PNG does not need embedded metadata for this workflow.
plot = ImagePlot("fixture.png", coordinate_system=fixture)
plot.scatter([(10, 15), (12, 18)])
plot.show()
```

## Embed a programmatically created coordinate system

```python
from imageplot import CoordinateSystem, add_coordinate_system

fixture = CoordinateSystem.from_points(
    name="Fixture",
    origin_pixel=(1250, 820),
    origin_world=(0.0, 0.0),
    x_point_pixel=(1750, 850),
    x_point_world=(100.0, 0.0),
    y_point_pixel=(1220, 320),
    y_point_world=(0.0, 100.0),
)

add_coordinate_system("fixture.png", fixture)
```

The resulting `coordinate_systems_json` iTXt metadata is compatible with the existing PNG Coordinate System Metadata Editor.

Use `replace=False` to reject a duplicate name instead of replacing it:

```python
add_coordinate_system("fixture.png", fixture, replace=False)
```

## Load coordinate systems directly

```python
from imageplot import load_coordinate_systems

for system in load_coordinate_systems("fixture.png"):
    print(system.name, system.handedness)
```

## Coordinate conversions

```python
pixels = plot.world_to_pixel(world_points)
world = plot.pixel_to_world(pixel_points)
```
