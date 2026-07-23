"""Matplotlib-first plotting on calibrated PNG imagery."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Mapping

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from PIL import Image

from .artists.base import Layer
from .artists.shapes import CircleCloud, EllipseCloud, PolygonCloud, RectangleCloud
from .coordinates import CoordinateSystem
from .metadata import load_png_image, read_png_metadata


class ImagePlot:
    """A calibrated PNG background plus ordinary Matplotlib axes.

    Data passed to plotting methods is expressed in the selected world
    coordinate system. The background image is affinely transformed into that
    same space, so normal Matplotlib artists remain available without wrappers.
    """

    def __init__(
        self,
        image_path: str | Path,
        coordinate_system: str | CoordinateSystem | None = None,
        *,
        ax: Axes | None = None,
        figsize: tuple[float, float] | None = None,
        dpi: float | None = None,
        image_alpha: float = 1.0,
        interpolation: str = "nearest",
    ) -> None:
        self.image_path = Path(image_path)
        self.image = load_png_image(self.image_path)

        if isinstance(coordinate_system, CoordinateSystem):
            self.metadata = read_png_metadata(self.image_path, required=False)
            self.coordinate_systems = (
                self._load_coordinate_systems() if self.metadata is not None else {}
            )
            self.coordinate_systems = dict(self.coordinate_systems)
            self.coordinate_systems[coordinate_system.name] = coordinate_system
            self.coordinate_system = coordinate_system
        else:
            self.metadata = read_png_metadata(self.image_path, required=True)
            self.coordinate_systems = self._load_coordinate_systems()
            self.coordinate_system = self._select_coordinate_system(coordinate_system)

        if ax is None:
            self.figure, self.ax = plt.subplots(figsize=figsize, dpi=dpi)
        else:
            self.ax = ax
            self.figure = ax.figure

        self._draw_background(image_alpha=image_alpha, interpolation=interpolation)

    def _load_coordinate_systems(self) -> Mapping[str, CoordinateSystem]:
        result: dict[str, CoordinateSystem] = {}
        for raw in self.metadata["coordinate_systems"]:
            system = CoordinateSystem.from_metadata(raw)
            if system.name in result:
                raise ValueError(f"Duplicate coordinate-system name: {system.name!r}")
            result[system.name] = system
        return result

    def _select_coordinate_system(self, name: str | None) -> CoordinateSystem:
        if name is None:
            if len(self.coordinate_systems) != 1:
                available = ", ".join(self.coordinate_systems)
                raise ValueError(
                    "The PNG contains multiple coordinate systems. Select one with "
                    f"coordinate_system=. Available systems: {available}"
                )
            return next(iter(self.coordinate_systems.values()))
        try:
            return self.coordinate_systems[name]
        except KeyError as exc:
            available = ", ".join(self.coordinate_systems)
            raise KeyError(f"Unknown coordinate system {name!r}. Available: {available}") from exc

    def _draw_background(self, *, image_alpha: float, interpolation: str) -> None:
        width, height = self.image.size
        transform = self.coordinate_system.matplotlib_transform + self.ax.transData

        # Pixel-center coordinates are 0..width-1 and 0..height-1. The extent
        # uses half-pixel outer edges and preserves the PNG's downward pixel Y.
        self.background_artist = self.ax.imshow(
            np.asarray(self.image),
            extent=(-0.5, width - 0.5, height - 0.5, -0.5),
            origin="upper",
            transform=transform,
            alpha=image_alpha,
            interpolation=interpolation,
            zorder=0,
        )

        corners = np.array(
            [[-0.5, -0.5], [width - 0.5, -0.5], [width - 0.5, height - 0.5], [-0.5, height - 0.5]]
        )
        world_corners = self.coordinate_system.pixel_to_world(corners)
        x_min, y_min = world_corners.min(axis=0)
        x_max, y_max = world_corners.max(axis=0)
        self.ax.set_xlim(x_min, x_max)
        self.ax.set_ylim(y_min, y_max)
        self.ax.set_aspect("equal", adjustable="box")
        self.ax.set_xlabel("World X")
        self.ax.set_ylabel("World Y")

    def scatter(self, points=None, *, x=None, y=None, **kwargs):
        x_values, y_values = self._normalize_xy(points, x=x, y=y)
        kwargs.setdefault("zorder", 3)
        return self.ax.scatter(x_values, y_values, **kwargs)

    def plot(self, points=None, *, x=None, y=None, **kwargs):
        x_values, y_values = self._normalize_xy(points, x=x, y=y)
        kwargs.setdefault("zorder", 2)
        return self.ax.plot(x_values, y_values, **kwargs)

    def text(self, x: float, y: float, text: str, **kwargs):
        kwargs.setdefault("zorder", 4)
        return self.ax.text(x, y, text, **kwargs)

    def add(self, layer: Layer):
        return layer.draw(self.ax)

    def circles(self, centers, radii, **kwargs):
        kwargs.setdefault("zorder", 2)
        return self.add(CircleCloud(centers, radii, kwargs))

    def ellipses(self, centers, widths, heights, angles=0.0, **kwargs):
        kwargs.setdefault("zorder", 2)
        return self.add(EllipseCloud(centers, widths, heights, angles, kwargs))

    def rectangles(self, centers, widths, heights, angles=0.0, **kwargs):
        kwargs.setdefault("zorder", 2)
        return self.add(RectangleCloud(centers, widths, heights, angles, kwargs))

    def polygons(self, polygons, **kwargs):
        kwargs.setdefault("zorder", 2)
        return self.add(PolygonCloud(polygons, kwargs))

    def legend(self, *args, **kwargs):
        return self.ax.legend(*args, **kwargs)

    def save(self, path: str | Path, *, dpi: float = 200, **kwargs) -> None:
        kwargs.setdefault("bbox_inches", "tight")
        self.figure.savefig(path, dpi=dpi, **kwargs)

    def show(self, *args, **kwargs) -> None:
        plt.show(*args, **kwargs)

    def pixel_to_world(self, points):
        return self.coordinate_system.pixel_to_world(points)

    def world_to_pixel(self, points):
        return self.coordinate_system.world_to_pixel(points)

    @staticmethod
    def _normalize_xy(points=None, *, x=None, y=None) -> tuple[np.ndarray, np.ndarray]:
        if points is not None:
            if x is not None or y is not None:
                raise ValueError("Pass either points or x/y, not both.")
            # Basic pandas support without requiring pandas as a dependency.
            if hasattr(points, "to_numpy"):
                array = np.asarray(points.to_numpy(), dtype=float)
            else:
                array = np.asarray(points, dtype=float)
            if array.ndim != 2 or array.shape[1] != 2:
                raise ValueError("points must have shape (N, 2).")
            return array[:, 0], array[:, 1]

        if x is None or y is None:
            raise ValueError("Provide points or both x= and y=.")
        x_values = np.asarray(x, dtype=float)
        y_values = np.asarray(y, dtype=float)
        if x_values.shape != y_values.shape:
            raise ValueError("x and y must have matching shapes.")
        return x_values, y_values
