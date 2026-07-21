"""Read and write coordinate-system metadata embedded in PNG images."""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Iterable

from PIL import Image, PngImagePlugin

from .coordinates import CoordinateSystem

METADATA_KEY = "coordinate_systems_json"
SUPPORTED_SCHEMA = "png-coordinate-systems"
METADATA_VERSION = 1


class MetadataError(ValueError):
    """Raised when PNG coordinate metadata is missing or invalid."""


def load_png_image(path: str | Path) -> Image.Image:
    """Load a PNG as an independent RGBA image without requiring metadata."""
    image_path = Path(path)
    with Image.open(image_path) as opened:
        if opened.format != "PNG":
            raise MetadataError(f"{image_path.name!r} is not a PNG image.")
        return opened.convert("RGBA")


def read_png_metadata(path: str | Path, *, required: bool = True) -> dict[str, Any] | None:
    """Read and validate embedded coordinate-system JSON metadata."""
    image_path = Path(path)
    with Image.open(image_path) as opened:
        if opened.format != "PNG":
            raise MetadataError(f"{image_path.name!r} is not a PNG image.")
        raw = opened.info.get(METADATA_KEY)

    if raw is None:
        if required:
            raise MetadataError(
                f"{image_path.name!r} does not contain the {METADATA_KEY!r} "
                "PNG metadata chunk."
            )
        return None

    try:
        payload = json.loads(raw) if isinstance(raw, str) else raw
    except json.JSONDecodeError as exc:
        raise MetadataError(f"Invalid coordinate-system JSON: {exc}") from exc

    if not isinstance(payload, dict):
        raise MetadataError("Coordinate-system metadata must be a JSON object.")
    if payload.get("schema") != SUPPORTED_SCHEMA:
        raise MetadataError(
            f"Unsupported metadata schema {payload.get('schema')!r}; "
            f"expected {SUPPORTED_SCHEMA!r}."
        )
    systems = payload.get("coordinate_systems")
    if not isinstance(systems, list) or not systems:
        raise MetadataError("The PNG contains no coordinate systems.")
    return payload


def load_png_metadata(path: str | Path) -> tuple[Image.Image, dict[str, Any]]:
    """Load a PNG and parse its embedded coordinate-system JSON metadata."""
    return load_png_image(path), read_png_metadata(path, required=True)  # type: ignore[return-value]


def load_coordinate_systems(path: str | Path) -> list[CoordinateSystem]:
    """Load all embedded coordinate systems from a PNG."""
    payload = read_png_metadata(path, required=True)
    assert payload is not None
    return [CoordinateSystem.from_metadata(item) for item in payload["coordinate_systems"]]


def write_coordinate_systems(
    path: str | Path,
    coordinate_systems: Iterable[CoordinateSystem],
) -> None:
    """Replace the PNG's embedded coordinate-system list atomically."""
    image_path = Path(path)
    systems = list(coordinate_systems)
    if not systems:
        raise MetadataError("At least one coordinate system is required.")

    payload = {
        "schema": SUPPORTED_SCHEMA,
        "version": METADATA_VERSION,
        "coordinate_systems": [system.to_metadata() for system in systems],
    }

    with Image.open(image_path) as opened:
        if opened.format != "PNG":
            raise MetadataError(f"{image_path.name!r} is not a PNG image.")
        opened.load()
        image = opened.copy()
        original_info = dict(opened.info)

    png_info = PngImagePlugin.PngInfo()
    for key, value in original_info.items():
        if key == METADATA_KEY:
            continue
        if isinstance(value, str):
            png_info.add_itxt(key, value)

    png_info.add_itxt(
        METADATA_KEY,
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
    )

    save_options: dict[str, Any] = {"format": "PNG", "pnginfo": png_info}
    for key in ("icc_profile", "dpi", "exif"):
        if original_info.get(key) is not None:
            save_options[key] = original_info[key]

    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            suffix=".png",
            prefix=f".{image_path.stem}-",
            dir=image_path.parent,
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
        image.save(temporary_path, **save_options)
        os.replace(temporary_path, image_path)
    except Exception:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        raise
    finally:
        image.close()


def add_coordinate_system(
    path: str | Path,
    coordinate_system: CoordinateSystem,
    *,
    replace: bool = True,
) -> None:
    """Add or replace one named coordinate system in a PNG."""
    payload = read_png_metadata(path, required=False)
    systems = [] if payload is None else [
        CoordinateSystem.from_metadata(item)
        for item in payload["coordinate_systems"]
    ]

    match = next(
        (
            index
            for index, existing in enumerate(systems)
            if existing.name.casefold() == coordinate_system.name.casefold()
        ),
        None,
    )
    if match is None:
        systems.append(coordinate_system)
    elif replace:
        systems[match] = coordinate_system
    else:
        raise MetadataError(
            f"A coordinate system named {coordinate_system.name!r} already exists."
        )

    write_coordinate_systems(path, systems)
