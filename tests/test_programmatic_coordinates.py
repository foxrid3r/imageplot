import numpy as np
from PIL import Image

from imageplot import (
    CoordinateSystem,
    ImagePlot,
    add_coordinate_system,
    load_coordinate_systems,
)


def make_system():
    return CoordinateSystem.from_points(
        name="Fixture",
        origin_pixel=(10, 20),
        origin_world=(0, 0),
        x_point_pixel=(110, 20),
        x_point_world=(50, 0),
        y_point_pixel=(10, 120),
        y_point_world=(0, -25),
    )


def test_from_points_round_trip():
    system = make_system()
    pixels = np.array([[10, 20], [110, 20], [10, 120], [60, 70]])
    world = system.pixel_to_world(pixels)
    assert np.allclose(system.world_to_pixel(world), pixels)
    assert system.to_metadata()["name"] == "Fixture"


def test_write_and_load_metadata(tmp_path):
    path = tmp_path / "image.png"
    Image.new("RGB", (200, 150), "white").save(path)
    add_coordinate_system(path, make_system())
    systems = load_coordinate_systems(path)
    assert len(systems) == 1
    assert systems[0].name == "Fixture"
    assert np.allclose(systems[0].pixel_to_world([[110, 20]]), [[50, 0]])


def test_imageplot_accepts_programmatic_system_without_metadata(tmp_path):
    path = tmp_path / "plain.png"
    Image.new("RGB", (200, 150), "white").save(path)
    plot = ImagePlot(path, coordinate_system=make_system())
    assert plot.coordinate_system.name == "Fixture"
    assert np.allclose(plot.pixel_to_world([[10, 20]]), [[0, 0]])
