"""Reusable shape-cloud layers for Monte Carlo and tolerance visualization."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Sequence

import numpy as np
from matplotlib.axes import Axes
from matplotlib.collections import PatchCollection
from matplotlib.patches import Circle, Ellipse, Polygon, Rectangle

from .base import Layer


@dataclass
class CircleCloud(Layer):
    centers: Iterable[Iterable[float]]
    radii: float | Sequence[float]
    kwargs: dict[str, Any] = field(default_factory=dict)

    def draw(self, ax: Axes):
        centers = np.asarray(self.centers, dtype=float)
        if centers.ndim != 2 or centers.shape[1] != 2:
            raise ValueError("centers must have shape (N, 2)")
        radii = np.broadcast_to(np.asarray(self.radii, dtype=float), len(centers))
        patches = [Circle(tuple(center), float(radius)) for center, radius in zip(centers, radii)]
        collection = PatchCollection(patches, **self.kwargs)
        ax.add_collection(collection)
        return collection


@dataclass
class EllipseCloud(Layer):
    centers: Iterable[Iterable[float]]
    widths: float | Sequence[float]
    heights: float | Sequence[float]
    angles: float | Sequence[float] = 0.0
    kwargs: dict[str, Any] = field(default_factory=dict)

    def draw(self, ax: Axes):
        centers = np.asarray(self.centers, dtype=float)
        count = len(centers)
        widths = np.broadcast_to(np.asarray(self.widths, dtype=float), count)
        heights = np.broadcast_to(np.asarray(self.heights, dtype=float), count)
        angles = np.broadcast_to(np.asarray(self.angles, dtype=float), count)
        patches = [
            Ellipse(tuple(c), float(w), float(h), angle=float(a))
            for c, w, h, a in zip(centers, widths, heights, angles)
        ]
        collection = PatchCollection(patches, **self.kwargs)
        ax.add_collection(collection)
        return collection


@dataclass
class RectangleCloud(Layer):
    centers: Iterable[Iterable[float]]
    widths: float | Sequence[float]
    heights: float | Sequence[float]
    angles: float | Sequence[float] = 0.0
    kwargs: dict[str, Any] = field(default_factory=dict)

    def draw(self, ax: Axes):
        centers = np.asarray(self.centers, dtype=float)
        count = len(centers)
        widths = np.broadcast_to(np.asarray(self.widths, dtype=float), count)
        heights = np.broadcast_to(np.asarray(self.heights, dtype=float), count)
        angles = np.broadcast_to(np.asarray(self.angles, dtype=float), count)
        patches = []
        for center, width, height, angle in zip(centers, widths, heights, angles):
            lower_left = (center[0] - width / 2.0, center[1] - height / 2.0)
            patches.append(
                Rectangle(lower_left, float(width), float(height), angle=float(angle), rotation_point="center")
            )
        collection = PatchCollection(patches, **self.kwargs)
        ax.add_collection(collection)
        return collection


@dataclass
class PolygonCloud(Layer):
    polygons: Iterable[Iterable[Iterable[float]]]
    kwargs: dict[str, Any] = field(default_factory=dict)

    def draw(self, ax: Axes):
        patches = [Polygon(np.asarray(vertices, dtype=float), closed=True) for vertices in self.polygons]
        collection = PatchCollection(patches, **self.kwargs)
        ax.add_collection(collection)
        return collection
