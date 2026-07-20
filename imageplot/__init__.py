"""Plot engineering data over PNG images with embedded affine coordinates."""
from .artists.base import Layer
from .artists.shapes import CircleCloud, EllipseCloud, PolygonCloud, RectangleCloud
from .coordinates import CoordinateSystem, CoordinateSystemError
from .figure import ImagePlot
from .metadata import MetadataError

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
]
