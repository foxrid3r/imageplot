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
    return array


@dataclass(frozen=True)
class CoordinateSystem:
    """A full 2D affine relationship between PNG pixels and world coordinates."""

    name: str
    pixel_to_world_matrix: np.ndarray
    world_to_pixel_matrix: np.ndarray

    @classmethod
    def from_metadata(cls, system: dict[str, Any]) -> "CoordinateSystem":
        pixel_points: list[list[float]] = []
        world_points: list[list[float]] = []

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
                    f"Coordinate system {system.get('name', '<unnamed>')!r} "
                    f"has an incomplete {point_name!r}."
                )
            px, py, wx, wy = map(float, values)
            pixel_points.append([px, py])
            world_points.append([wx, wy])

        source = np.column_stack([np.asarray(pixel_points), np.ones(3)])
        target = np.asarray(world_points)
        if abs(np.linalg.det(source)) < 1e-12:
            raise CoordinateSystemError("The three pixel reference points are collinear.")

        # Solve source @ coefficients = target. The homogeneous matrix uses
        # column vectors: [world_x, world_y, 1]^T = M @ [pixel_x, pixel_y, 1]^T.
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
            name=str(system.get("name", "Unnamed")),
            pixel_to_world_matrix=matrix,
            world_to_pixel_matrix=np.linalg.inv(matrix),
        )

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
        # Matplotlib Affine2D.from_values expects a, b, c, d, e, f where
        # x' = a*x + c*y + e and y' = b*x + d*y + f.
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
