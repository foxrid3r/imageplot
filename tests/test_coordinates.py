import numpy as np
from imageplot.coordinates import CoordinateSystem


def test_round_trip_affine():
    raw = {
        "name": "Test",
        "origin": {"pixel_x": 10, "pixel_y": 20, "world_x": 0, "world_y": 0},
        "x_point": {"pixel_x": 110, "pixel_y": 25, "world_x": 50, "world_y": 0},
        "y_point": {"pixel_x": 15, "pixel_y": 220, "world_x": 0, "world_y": 100},
    }
    system = CoordinateSystem.from_metadata(raw)
    pixels = np.array([[10, 20], [62.5, 122.5], [110, 25]], dtype=float)
    world = system.pixel_to_world(pixels)
    restored = system.world_to_pixel(world)
    np.testing.assert_allclose(restored, pixels, atol=1e-10)
