"""Affine mappings between source-image pixels and engineering coordinates."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

import numpy as np
from matplotlib.transforms import Affine2D

POINT_NAMES = ("origin", "x_point", "y_point")


class CoordinateSystemError(ValueError):
    """Raised when a coordinate system cannot define a valid affine map."""


def _as_points(values: Iterable[Iterable[float]] | np.ndarray) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    if array.ndim == 1:
        if array.size != 2:
            raise ValueError("A single point must contain exactly two values.")
        array = array.reshape(1, 2)
    if array.ndim != 2 or array.shape[1] != 2:
        raise ValueError("Points must have shape (N, 2).")
    if not np.all(np.isfinite(array)):
        raise ValueError("Points must contain finite numeric values.")
    return array


def _point_metadata(
    pixel: Iterable[float] | np.ndarray,
    world: Iterable[float] | np.ndarray,
    *,
    point_name: str,
) -> dict[str, float]:
    pixel_array = np.asarray(pixel, dtype=float)
    world_array = np.asarray(world, dtype=float)

    if pixel_array.shape != (2,):
        raise CoordinateSystemError(
            f"{point_name!r} pixel coordinates must contain exactly two values."
        )
    if world_array.shape != (2,):
        raise CoordinateSystemError(
            f"{point_name!r} world coordinates must contain exactly two values."
        )
    if not np.all(np.isfinite(np.concatenate([pixel_array, world_array]))):
        raise CoordinateSystemError(
            f"{point_name!r} coordinates must contain finite numeric values."
        )

    return {
        "pixel_x": float(pixel_array[0]),
        "pixel_y": float(pixel_array[1]),
        "world_x": float(world_array[0]),
        "world_y": float(world_array[1]),
    }


@dataclass(frozen=True)
class CoordinateSystem:
    """A full 2D affine relationship between PNG pixels and world coordinates."""

    name: str
    pixel_to_world_matrix: np.ndarray
    world_to_pixel_matrix: np.ndarray
    reference_points: dict[str, dict[str, float]] | None = None

    @classmethod
    def from_points(
        cls,
        *,
        name: str,
        origin_pixel: Iterable[float],
        origin_world: Iterable[float],
        x_point_pixel: Iterable[float],
        x_point_world: Iterable[float],
        y_point_pixel: Iterable[float],
        y_point_world: Iterable[float],
    ) -> "CoordinateSystem":
        """Create a coordinate system from three corresponding point pairs."""
        metadata = {
            "name": str(name),
            "origin": _point_metadata(
                origin_pixel, origin_world, point_name="origin"
            ),
            "x_point": _point_metadata(
                x_point_pixel, x_point_world, point_name="x_point"
            ),
            "y_point": _point_metadata(
                y_point_pixel, y_point_world, point_name="y_point"
            ),
        }
        return cls.from_metadata(metadata)

    @classmethod
    def from_metadata(cls, system: dict[str, Any]) -> "CoordinateSystem":
        pixel_points: list[list[float]] = []
        world_points: list[list[float]] = []
        reference_points: dict[str, dict[str, float]] = {}
        name = str(system.get("name", "Unnamed"))

        for point_name in POINT_NAMES:
            point = system.get(point_name)
            if not isinstance(point, dict):
                raise CoordinateSystemError(f"Missing point {point_name!r}.")
            values = [
                point.get("pixel_x"),
                point.get("pixel_y"),
                point.get("world_x"),
                point.get("world_y"),
            ]
            if any(value is None for value in values):
                raise CoordinateSystemError(
                    f"Coordinate system {name!r} has an incomplete {point_name!r}."
                )
            try:
                px, py, wx, wy = map(float, values)
            except (TypeError, ValueError) as exc:
                raise CoordinateSystemError(
                    f"Coordinate system {name!r} has non-numeric values in "
                    f"{point_name!r}."
                ) from exc
            if not np.all(np.isfinite([px, py, wx, wy])):
                raise CoordinateSystemError(
                    f"Coordinate system {name!r} has non-finite values in "
                    f"{point_name!r}."
                )

            pixel_points.append([px, py])
            world_points.append([wx, wy])
            reference_points[point_name] = {
                "pixel_x": px,
                "pixel_y": py,
                "world_x": wx,
                "world_y": wy,
            }

        source = np.column_stack([np.asarray(pixel_points), np.ones(3)])
        target = np.asarray(world_points)
        if abs(np.linalg.det(source)) < 1e-12:
            raise CoordinateSystemError("The three pixel reference points are collinear.")

        world_source = np.column_stack([target, np.ones(3)])
        if abs(np.linalg.det(world_source)) < 1e-12:
            raise CoordinateSystemError("The three world reference points are collinear.")

        coefficients = np.linalg.solve(source, target)
        matrix = np.array(
            [
                [coefficients[0, 0], coefficients[1, 0], coefficients[2, 0]],
                [coefficients[0, 1], coefficients[1, 1], coefficients[2, 1]],
                [0.0, 0.0, 1.0],
            ],
            dtype=float,
        )
        if abs(np.linalg.det(matrix)) < 1e-15:
            raise CoordinateSystemError("The pixel-to-world transform is singular.")

        return cls(
            name=name,
            pixel_to_world_matrix=matrix,
            world_to_pixel_matrix=np.linalg.inv(matrix),
            reference_points=reference_points,
        )

    def to_metadata(self) -> dict[str, Any]:
        """Return metadata compatible with the PNG Coordinate System Editor."""
        if self.reference_points is None:
            raise CoordinateSystemError(
                "This coordinate system was created from matrices and has no "
                "reference-point metadata to serialize."
            )
        return {
            "name": self.name,
            **{
                point_name: dict(self.reference_points[point_name])
                for point_name in POINT_NAMES
            },
        }

    def pixel_to_world(self, points: Iterable[Iterable[float]] | np.ndarray) -> np.ndarray:
        return self._transform(points, self.pixel_to_world_matrix)

    def world_to_pixel(self, points: Iterable[Iterable[float]] | np.ndarray) -> np.ndarray:
        return self._transform(points, self.world_to_pixel_matrix)

    @staticmethod
    def _transform(
        points: Iterable[Iterable[float]] | np.ndarray,
        matrix: np.ndarray,
    ) -> np.ndarray:
        array = _as_points(points)
        homogeneous = np.column_stack([array, np.ones(len(array))])
        return (matrix @ homogeneous.T).T[:, :2]

    @property
    def matplotlib_transform(self) -> Affine2D:
        """Return a Matplotlib pixel-to-world affine transform."""
        m = self.pixel_to_world_matrix
        return Affine2D.from_values(
            m[0, 0], m[1, 0], m[0, 1], m[1, 1], m[0, 2], m[1, 2]
        )

    @property
    def origin(self) -> np.ndarray:
        return self.pixel_to_world([[0.0, 0.0]])[0]

    @property
    def linear_matrix(self) -> np.ndarray:
        return self.pixel_to_world_matrix[:2, :2].copy()

    @property
    def determinant(self) -> float:
        return float(np.linalg.det(self.linear_matrix))

    @property
    def handedness(self) -> str:
        return "right-handed" if self.determinant > 0 else "left-handed"
