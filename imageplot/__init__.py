"""Plot engineering data over PNG images with affine coordinates."""

from .artists.base import Layer
from .artists.shapes import CircleCloud, EllipseCloud, PolygonCloud, RectangleCloud
from .coordinates import CoordinateSystem, CoordinateSystemError
from .figure import ImagePlot
from .metadata import (
    MetadataError,
    add_coordinate_system,
    load_coordinate_systems,
    read_png_metadata,
    write_coordinate_systems,
)

__all__ = [
    "CircleCloud",
    "CoordinateSystem",
    "CoordinateSystemError",
    "EllipseCloud",
    "ImagePlot",
    "Layer",
    "MetadataError",
    "PolygonCloud",
    "RectangleCloud",
    "add_coordinate_system",
    "load_coordinate_systems",
    "read_png_metadata",
    "write_coordinate_systems",
]
